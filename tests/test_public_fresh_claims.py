import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from tests.test_public_claims import observation
from triage_bench.public_fresh_claim_features import compose, strongest_channel, FIELDS, ARMS
from triage_bench.public_fresh_claim_trial import assess


class FreshClaimTests(unittest.TestCase):
    def fixture(self):
        a = observation()
        a['service'] = 'alpha'
        b = copy.deepcopy(a)
        b['service'] = 'beta'
        b['metrics']['socket']['signed_change'] = 0
        source = {'id': 'fixture', 'trace_context': {'services': {}},
            'trace_changes': {'window_seconds': {'before': 60, 'after': 60}},
            'requests': {'metrics': {'state': json.dumps({'services': {'alpha': a['metrics'], 'beta': b['metrics']}})}}}
        return compose(source, 'Sample')

    def test_exact_text_service_and_full_note_are_preserved(self):
        p, ref = self.fixture()
        bound = p['requests']['bound']
        state = json.loads(bound['state'])
        self.assertEqual(len(state['services']), 2)
        for f in FIELDS:
            scoped = p['claim_requests'][f]['scoped']
            ss = json.loads(scoped['state'])
            self.assertEqual(scoped['questions'], {f: bound['questions'][f]})
            self.assertEqual(ss['report'], state['report'])
            self.assertEqual(len(ss['services']), 1)
            self.assertEqual(ss['services'][0]['service'], p['claim_sources'][f]['service'])
            span = p['supplied_bindings'][f]
            self.assertEqual(state['report'][span['start']:span['end']], p['statements'][f])
            self.assertTrue(bound['questions'][f]['instructions'].endswith(p['statements'][f]))
        self.assertNotIn('proposition', bound['state'])
        self.assertNotIn('reference', bound['state'])
        self.assertEqual(ref['answers'][FIELDS[2]]['answer'], 'unanswerable')
        self.assertEqual(ref['answers'][FIELDS[5]]['answer'], 'unanswerable')

    def test_selection_does_not_choose_ineligible_or_nonfinite_metric(self):
        o = observation()
        o['metrics']['mem'] = {**o['metrics']['socket'], 'signed_change': 100, 'after_missing_fraction': .21}
        o['metrics']['cpu'] = {**o['metrics']['socket'], 'signed_change': float('nan')}
        self.assertEqual(strongest_channel(o), 'socket')
        o['metrics']['socket']['after_missing_fraction'] = None
        self.assertEqual(strongest_channel(o), 'cpu')  # deterministic fallback, not eligible evidence

    def test_absence_keeps_duration_and_counts_unknown(self):
        p, ref = self.fixture()
        self.assertEqual(ref['answers'][FIELDS[1]]['answer'], 'unanswerable')
        self.assertEqual(ref['answers'][FIELDS[4]]['answer'], 'unanswerable')
        state = json.loads(p['requests']['bound']['state'])
        self.assertTrue(all(s['recorded_span_counts']['before'] is None for s in state['services']))

    def test_grouped_allocation_opens_only_nine_reserves(self):
        from triage_bench.public_fresh_claim_data import allocation
        rows = allocation()
        self.assertEqual(len(rows), 9)
        self.assertEqual(len({r['group'] for r in rows}), 3)
        self.assertEqual(sum(r['dataset'] == 'Train Ticket' for r in rows), 3)
        self.assertTrue(all(r['split'] == 'confirmation' for r in rows))
        self.assertFalse(any(r['source_case'].startswith('re3ss_') for r in rows))

    def panel(self):
        p, ref = self.fixture()
        ref = {'id': p['id'], 'answers': {f: {'answer': ('supported', 'contradicted', 'unanswerable')[i % 3]} for i, f in enumerate(FIELDS)}}
        rows = []
        for arm in ARMS:
            for n in (1, 2, 3):
                for f in ((None,) if arm == 'bound' else FIELDS):
                    fields = FIELDS if f is None else (f,)
                    rows.append({'card_id': p['id'], 'arm': arm, 'round': n, 'field': f, 'status': 'ok',
                        'answers': {k: {'choice': ref['answers'][k]['answer'], 'probabilities': {ref['answers'][k]['answer']: 1}} for k in fields}})
        return p, ref, rows

    def test_failed_request_retains_denominators_and_no_spurious_fix(self):
        p, ref, rows = self.panel()
        rows = [r for r in rows if not (r['arm'] == 'bound' and r['round'] == 1)]
        result = assess(rows, [p], [ref])['Sample']
        self.assertFalse(result['research_gate'])
        self.assertEqual(result['arms']['bound']['per_round'][0]['claims'], 6)
        self.assertEqual(result['arms']['bound']['per_round'][0]['failed_or_missing'], 6)
        self.assertFalse(any(pair['fix'] for pair in result['pairs']))

    def test_displayed_wrong_contradiction_fails_its_candidate(self):
        p, ref, rows = self.panel()
        row = next(r for r in rows if r['arm'] == 'scoped' and r['round'] == 1 and r['field'] == FIELDS[0])
        row['answers'][FIELDS[0]] = {'choice': 'contradicted', 'probabilities': {'contradicted': .99}}
        result = assess(rows, [p], [ref])['Sample']
        self.assertTrue(result['arms']['bound']['research_gate'])
        self.assertFalse(result['arms']['scoped']['research_gate'])
        self.assertEqual(result['arms']['scoped']['per_round'][0]['wrong_displayed'], 1)
        self.assertEqual(result['arms']['scoped']['per_round'][0]['all_six_correct'], 0)

    def test_absent_class_is_not_a_passing_confirmation(self):
        p, ref, rows = self.panel()
        ref['answers'] = {f: {'answer': 'supported'} for f in FIELDS}
        for row in rows:
            row['answers'] = {f: {'choice': 'supported', 'probabilities': {'supported': 1}} for f in row['answers']}
        result = assess(rows, [p], [ref])['Sample']
        self.assertFalse(result['research_gate'])
        self.assertEqual(result['arms']['bound']['gate_status'], 'insufficient_class_coverage')

    def test_model_mismatch_stops_once_without_credential_leak(self):
        from triage_bench import public_fresh_claim_trial as trial
        from triage_bench.app import profiles
        p, _ = self.fixture()
        profile = profiles()['jev']
        profile['api_key'] = 'private-fresh-fixture'
        plan = {k: profile[k] for k in ('model', 'endpoint', 'context_tokens')}
        req = {'id': 'one', 'card_id': p['id'], 'arm': 'bound', 'round': 1, 'field': None, 'body': p['requests']['bound']}
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({'model': 'wrong', 'echo': profile['api_key']}).encode()
        opener = MagicMock()
        opener.open.return_value = response
        with tempfile.TemporaryDirectory() as t:
            path = Path(t)
            protocol = path / 'protocol.json'
            protocol.write_text('{}')
            with patch.object(trial, 'check', return_value=(plan, [req])), patch.object(trial, 'PROTOCOL', protocol), patch.object(trial, 'OUTPUT', path / 'hosted'), patch('urllib.request.build_opener', return_value=opener):
                result = trial.run(profile)
                self.assertEqual(result['stopped_reason'], 'checkpoint_mismatch')
                self.assertEqual(result['unattempted'], 188)
                self.assertNotIn(profile['api_key'], (path / 'hosted/responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):
                    trial.run(profile)
                self.assertEqual(opener.open.call_count, 1)
