import unittest
from unittest.mock import patch
from triage_bench import public_trace_data as data, public_trace_trial as trial


class TraceProtocolTests(unittest.TestCase):
    def test_group_allocation_keeps_audited_cases_in_development(self):
        from triage_bench.public_rca_stages import load
        plan = load(data.PLAN)
        audit = load(data.ROOT / 'checkpoints/public-traces-audit-plan-2026-10-04.json')
        by_source = {r['source_case']: r for r in plan['assignments']}
        self.assertTrue(all(by_source[c]['split'] == 'development' for c in audit['cases']))
        groups = {}
        for r in plan['assignments']:
            groups.setdefault(r['group'], set()).add(r['split'])
        self.assertTrue(all(len(s) == 1 for s in groups.values()))
        self.assertEqual(sum(r['split'] == 'reserve' for r in plan['assignments']), 25)

    def test_evaluation_guard_precedes_destination_and_download(self):
        with patch.object(data, 'check_plan', return_value={}), \
             patch.object(trial, 'check_candidate', side_effect=ValueError('sealed')), \
             patch.object(data, 'folder') as destination, patch.object(data, 'fetch') as download:
            with self.assertRaisesRegex(ValueError, 'sealed'):
                data.prepare('evaluation')
            destination.assert_not_called()
            download.assert_not_called()

    def score(self, *, regression=False, missing=False):
        refs = [{'id': n, 'group': n, 'target': 'cause', 'fault': 'f'} for n in ('tt', 'ob')]
        rows = []
        for ref in refs:
            for number in (1, 2, 3):
                for arm in data.ARMS:
                    if missing and ref['id'] == 'ob' and number == 3 and arm == 'traces':
                        continue
                    choice = 'cause' if arm == 'traces' else 'other'
                    if regression and ref['id'] == 'tt' and number == 2:
                        choice = 'cause' if arm == 'metrics' else 'other'
                    rows.append({'case_id': ref['id'], 'arm': arm, 'round': number,
                                 'status': 'ok', 'choice': choice,
                                 'probabilities': {choice: .8, 'insufficient_evidence': .2}})
        controls = {ref['id']: {a: {'choice': 'cause'} for a in ('ml', 'change', 'resource', 'trace_duration')} for ref in refs}
        plan = {'assignments': [{'id': 'tt', 'dataset': 'Train Ticket'}, {'id': 'ob', 'dataset': 'Online Boutique'}],
                'stage_calls': {'development': 12}}
        with patch.object(trial, 'verified_rows', return_value=(rows, {'failed': 0, 'unattempted': int(missing)})), \
             patch.object(trial, 'check_plan', return_value=plan), \
             patch.object(trial, 'load', side_effect=[refs, controls]), \
             patch.object(trial, 'sha', return_value='fixture'), \
             patch('pathlib.Path.read_bytes', return_value=b'fixture'):
            return trial.score('development')

    def test_gate_requires_repeated_fix_and_preserves_missing_denominator(self):
        good = self.score()
        self.assertTrue(good['promotion_gate'])
        self.assertEqual(good['datasets']['Train Ticket']['stable_fixes'], ['tt'])
        self.assertFalse(self.score(regression=True)['promotion_gate'])
        incomplete = self.score(missing=True)
        self.assertFalse(incomplete['promotion_gate'])
        last = incomplete['datasets']['Online Boutique']['arms']['traces']['selective']['per_round'][2]
        self.assertEqual((last['cases'], last['failed_or_missing']), (1, 1))
