import copy
import json
import unittest
from unittest.mock import patch
from triage_bench.public_trace_task_features import changes, relative, requests, COLUMNS
from triage_bench.public_trace_task_data import partition
from triage_bench import public_trace_task_data as data, public_trace_task_trial as trial
from triage_bench.public_selective_policy import evaluate


class TraceTaskTests(unittest.TestCase):
    def context(self):
        before = {'duration_median_us': 10., 'duration_p90_us': 20., 'uncovered_duration_median_us': 5.,
                  'uncovered_duration_p90_us': None, 'spans': 10, 'distinct_traces': 3,
                  'status_code_counts': {}, 'status_missing_fraction': 1.}
        after = {**before, 'duration_median_us': 15., 'uncovered_duration_median_us': 4., 'spans': 5}
        return {'services': {'a': {'before': before, 'after': after}}, 'candidates_without_spans': ['b']}

    def test_changes_correct_unequal_windows_and_preserve_unknowns(self):
        context = self.context()
        delta = changes(context, 20, 10)
        values = dict(zip(COLUMNS, delta['services']['a']))
        self.assertEqual(values['median_duration_relative_change'], .5)
        self.assertEqual(values['median_uncovered_relative_change'], -.2)
        self.assertEqual(values['recorded_span_rate_relative_change'], 0)
        self.assertIsNone(values['p90_uncovered_relative_change'])
        self.assertNotIn('b', delta['services'])
        self.assertTrue(values['duration_sample_supported'])
        context['services']['a']['after']['spans'] = 4
        self.assertFalse(changes(context, 20, 10)['services']['a'][-1])
        self.assertIsNone(relative(0, 5))
        with self.assertRaises(ValueError):
            changes(context, 0, 10)

    def test_each_arm_changes_only_its_declared_factor(self):
        state = {'condition': 'fixture', 'columns': ['before_median', 'after_median', 'signed_change', 'before_missing_fraction', 'after_missing_fraction'],
                 'signed_change_definition': 'fixture', 'window_rows': {'before': 2, 'after': 2},
                 'services': {'a': {'cpu': [1, 2, 1, 0, 0]}, 'b': {}}}
        context = self.context()
        frozen = copy.deepcopy((state, context))
        actual = requests(state, context, changes(context, 20, 10))
        self.assertEqual((state, context), frozen)
        traces = json.loads(actual['traces']['state'])
        metrics = json.loads(actual['metrics']['state'])
        traces.pop('trace_context')
        self.assertEqual(traces, metrics)
        self.assertEqual(actual['trace_task']['state'], actual['traces']['state'])
        delta = json.loads(actual['trace_deltas']['state'])
        delta.pop('trace_changes')
        self.assertEqual(delta, json.loads(actual['trace_task']['state']))
        self.assertEqual(actual['trace_task']['questions'], actual['trace_deltas']['questions'])
        for a in actual.values():
            self.assertEqual(set(a['questions']['cause']['criteria']), {'a', 'b', 'insufficient_evidence'})
        self.assertEqual(actual['metrics']['questions'], actual['traces']['questions'])
        self.assertEqual(actual['trace_task']['questions']['cause']['criteria']['a'], actual['traces']['questions']['cause']['criteria']['a'])

    def test_fresh_groups_preserve_evaluation_and_exclude_inspected_cases(self):
        previous = json.loads(data.PREVIOUS.read_text())['assignments']
        result = partition(previous)
        self.assertEqual({r['source_case'] for r in result if r['split'] == 'evaluation'},
                         {r['source_case'] for r in previous if r['split'] == 'evaluation'})
        fresh = {r['source_case'] for r in result if r['split'] == 'development'}
        old = {r['source_case'] for r in previous if r['split'] == 'development'}
        self.assertFalse(fresh & old)
        self.assertEqual(len(fresh), 16)
        self.assertEqual(sum(r['split'] == 'reserve' for r in result), 9)

    def test_evaluation_guard_precedes_local_files_and_network(self):
        with patch.object(data, 'check_plan', return_value={}), \
             patch.object(trial, 'check_candidate', side_effect=ValueError('sealed')), \
             patch.object(data, 'folder') as folder, patch.object(data, 'fetch') as fetch:
            with self.assertRaisesRegex(ValueError, 'sealed'):
                data.prepare('evaluation')
            folder.assert_not_called()
            fetch.assert_not_called()

    def test_primary_gate_rejects_lost_coverage_and_missing_rounds(self):
        refs = [{'id': 'case', 'target': 'cause', 'group': 'g', 'fault': 'f'}]
        rows = [{'case_id': 'case', 'round': n, 'status': 'ok', 'choice': 'cause', 'probabilities': {'cause': .8, 'other': .2}} for n in (1, 2, 3)]
        good = {'selective': evaluate(rows, refs, trial.POLICY), 'unfiltered': evaluate(rows, refs, {'threshold': 0., 'margin': 0., 'maximum_leads': 1})}
        none = {'selective': evaluate([], refs, trial.POLICY), 'unfiltered': evaluate([], refs, trial.POLICY)}
        results = {'metrics': none, 'traces': none, trial.PRIMARY: good}
        comparisons = {c+'__trace_deltas': {'stable_fixes': ['case'], 'stable_regressions': []} for c in ('metrics', 'traces')}
        self.assertTrue(trial.gate(results, comparisons))
        weak = copy.deepcopy(good)
        weak['selective'] = evaluate([{**r, 'probabilities': {'cause': .6, 'other': .4}} for r in rows], refs, trial.POLICY)
        results[trial.PRIMARY] = weak
        self.assertFalse(trial.gate(results, comparisons))
        self.assertEqual(evaluate(rows[:2], refs, trial.POLICY)['per_round'][2]['failed_or_missing'], 1)

    def test_failed_or_missing_predictions_are_not_paired_fixes(self):
        refs = [{'id': 'case', 'target': 'cause', 'group': 'g', 'fault': 'f'}]
        rows = [{'case_id': 'case', 'arm': 'trace_deltas', 'round': 1, 'status': 'error', 'choice': 'cause'}]
        result = trial.paired(rows, refs, 'traces', 'trace_deltas')
        self.assertEqual(result['stable_fixes'], [])
        self.assertFalse(any(r['fix'] for r in result['pairs']))
