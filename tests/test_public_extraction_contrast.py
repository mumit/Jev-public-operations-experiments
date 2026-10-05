import copy
import json
import unittest
from tests import test_public_notes as note_tests
from triage_bench.public_note_v2_features import extraction_request as baseline_request
from triage_bench.public_contrast_features import ARMS, ROLE, MEANING, extraction_request, validate_changes
from triage_bench.public_contrast_trial import assess
from triage_bench.hosted import encoded


class ExtractionContrastTests(unittest.TestCase):
    def fixture(self):
        p, r = note_tests.NoteTests().fixture()
        p['extraction_request'] = baseline_request(p)
        return p, r

    def test_baseline_body_is_identical_and_input_is_not_mutated(self):
        p, _ = self.fixture(); before = copy.deepcopy(p)
        self.assertEqual(encoded(extraction_request(p, 'baseline')), encoded(p['extraction_request']))
        for arm in ARMS: extraction_request(p, arm)
        validate_changes(p)
        self.assertEqual(p, before)
        with self.assertRaises(ValueError): extraction_request(p, 'unknown')

    def test_factorial_changes_only_the_declared_shared_definitions(self):
        p, _ = self.fixture(); before = json.loads(p['extraction_request']['state'])
        for arm, changed in [('baseline', set()), ('role', {'role'}), ('meaning', {'kind'}), ('combined', {'role', 'kind'})]:
            body = extraction_request(p, arm); after = json.loads(body['state'])
            self.assertEqual({d for d in before['extraction_definitions'] if before['extraction_definitions'][d] != after['extraction_definitions'][d]}, changed)
            self.assertEqual(body['questions'], p['extraction_request']['questions'])
            for key in ('note', 'candidates', 'observed_service_inventory', 'metric_channel_inventory'):
                self.assertEqual(after[key], before[key])
            self.assertNotIn('observations', after)
            self.assertNotIn('annotations', after)

    def test_definitions_use_generic_examples_without_case_service_or_verdict_answers(self):
        p, r = self.fixture(); text = ROLE + MEANING
        for s in p['services']: self.assertNotIn(s, text)
        for value in ('supported', 'contradicted', 'unanswerable', p['id']): self.assertNotIn(value, text)
        self.assertIn('not telemetry truth', MEANING)
        self.assertIn('not separate independently checkable assertions', ROLE)
        self.assertIn('it does not assert service health', MEANING)

    def panel(self):
        p, r, old_assigned, old_verdicts, old_extract = note_tests.NoteTests().panel()
        assigned, verdicts, extracted = [], [], []
        for n in (1, 2, 3):
            for arm in ARMS:
                source = next(a for a in old_assigned if a['arm'] == 'jev' and a['round'] == n)
                assigned.append({**copy.deepcopy(source), 'arm': arm})
                vr = next(v for v in old_verdicts if v['arm'] == 'jev' and v['round'] == n)
                verdicts.append({**copy.deepcopy(vr), 'arm': arm})
                extracted.append({'card_id': p['id'], 'round': n, 'arm': arm, 'status': 'ok'})
        return p, r, assigned, verdicts, extracted

    def test_each_arm_uses_its_own_extraction_status(self):
        p, r, assigned, verdicts, extracted = self.panel()
        extracted = [e for e in extracted if not (e['arm'] == 'meaning' and e['round'] == 1)]
        panel = assess([p], [r], assigned, verdicts, extracted)['Sample']
        self.assertFalse(panel['arms']['meaning']['per_round'][0]['complete_calls'])
        self.assertTrue(panel['arms']['baseline']['per_round'][0]['complete_calls'])
        self.assertTrue(panel['arms']['combined']['per_round'][0]['complete_calls'])

    def test_pairs_keep_fix_and_loss_when_totals_tie(self):
        p, r, assigned, verdicts, extracted = self.panel()
        targets = [a for a in r['annotations'] if a['actionable']][:2]
        for arm, target in [('baseline', targets[0]), ('combined', targets[1])]:
            binding = next(a for a in assigned if a['arm'] == arm and a['round'] == 1)['bindings'][target['id']]
            binding['accepted'] = False
        panel = assess([p], [r], assigned, verdicts, extracted)['Sample']
        comparison = next(c for c in panel['comparisons'] if c['control'] == 'baseline' and c['candidate'] == 'combined')
        self.assertEqual(comparison['per_round'][0]['end_to_end_gain'], 1)
        self.assertEqual(comparison['per_round'][0]['end_to_end_loss'], 1)

    def test_better_single_change_cannot_replace_failed_combined_candidate(self):
        p, r, assigned, verdicts, extracted = self.panel()
        target = next(a for a in r['annotations'] if a['actionable'])
        next(a for a in assigned if a['arm'] == 'combined' and a['round'] == 1)['bindings'][target['id']]['accepted'] = False
        panel = assess([p], [r], assigned, verdicts, extracted)['Sample']
        self.assertTrue(panel['arms']['role']['research_gate'])
        self.assertFalse(panel['research_gate'])
        self.assertEqual(panel['arms']['role']['gate_status'], 'diagnostic_not_candidate')
        self.assertFalse(panel['candidate_gate']['baseline_comparison_pass'])

    def test_wrong_binding_cannot_be_hidden_by_correct_verdict(self):
        p, r, assigned, verdicts, extracted = self.panel()
        target = next(a for a in r['annotations'] if a['actionable'])
        next(a for a in assigned if a['arm'] == 'combined' and a['round'] == 1)['bindings'][target['id']]['service'] = 'beta' if target['service'] == 'alpha' else 'alpha'
        row = assess([p], [r], assigned, verdicts, extracted)['Sample']['arms']['combined']['per_round'][0]
        self.assertEqual(row['accepted_wrong_bindings'], 1)
        self.assertEqual(row['unsafe_displayed'], 1)
        self.assertEqual(row['end_to_end_correct'], 5)

    def test_missing_verdict_retains_all_claim_denominators(self):
        p, r, assigned, verdicts, extracted = self.panel()
        verdicts = [v for v in verdicts if not (v['arm'] == 'combined' and v['round'] == 1)]
        row = assess([p], [r], assigned, verdicts, extracted)['Sample']['arms']['combined']['per_round'][0]
        self.assertEqual(row['routable_claims'], 6)
        self.assertFalse(row['complete_calls'])
        self.assertEqual(row['end_to_end_correct'], 0)

    def test_once_only_global_error_stops_and_redacts(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch, MagicMock
        from triage_bench import public_contrast_trial as trial
        from triage_bench.app import profiles
        from triage_bench.profile import MODEL
        p, _ = self.fixture(); profile = profiles()['jev']; profile['api_key'] = 'contrast-private-fixture'
        frozen = {k: profile[k] for k in ('model', 'endpoint', 'context_tokens')}
        request = {'id': 'one', 'card_id': p['id'], 'arm': 'combined', 'round': 1, 'phase': 'extraction', 'body': extraction_request(p, 'combined')}
        response = MagicMock(); response.__enter__.return_value.read.return_value = json.dumps({'model': MODEL, 'usage': {'input_tokens': True}, 'answers': {}, 'echo': profile['api_key']}).encode()
        opener = MagicMock(); opener.open.return_value = response
        with tempfile.TemporaryDirectory() as t:
            directory = Path(t); protocol = directory / 'protocol'; protocol.write_text('{}')
            with patch.object(trial, 'check', return_value=(frozen, [request, {**request, 'id': 'two'}])), patch.object(trial, 'protocol_path', return_value=protocol), patch.object(trial, 'output', return_value=directory / 'new' / 'hosted'), patch('urllib.request.build_opener', return_value=opener):
                result = trial.run('extraction', profile)
                self.assertEqual(result['stopped_reason'], 'untrustworthy_usage')
                self.assertEqual(result['unattempted_jobs'], 1)
                self.assertNotIn(profile['api_key'], (directory / 'new/hosted/responses.jsonl').read_text())
                with self.assertRaises(FileExistsError): trial.run('extraction', profile)
                self.assertEqual(opener.open.call_count, 1)

    def test_reader_keeps_references_hidden_and_does_not_mutate_saved_outcomes(self):
        from unittest.mock import patch
        from triage_bench.public_contrast_service import PublicContrastStudy
        p, r, assigned, verdicts, extracted = self.panel()
        result = {'bindings': assigned, 'datasets': assess([p], [r], assigned, verdicts, extracted)}
        before = copy.deepcopy(result); study = PublicContrastStudy('.')
        def loaded(path):
            if path.name == 'inputs.json': return [p]
            if path.name == 'references.json': return [r]
            return []
        with patch.object(study, 'verified', return_value=result), patch('triage_bench.public_contrast_service.load', side_effect=loaded), patch('pathlib.Path.read_text', return_value=''):
            hidden = study.card(p['id'])
            self.assertIsNone(hidden['reference'])
            self.assertNotIn('end_to_end_correct', hidden['outcomes']['combined'][0])
            self.assertEqual(study.card(p['id'], True)['reference'], r)
            self.assertEqual(result, before)

    def test_formatted_report_retains_contrast_and_sentence_selection(self):
        from triage_bench.study_page import render_study
        from triage_bench.paths import ROOT
        from types import SimpleNamespace
        query = {'doc': 'public-extraction-contrast', 'return': '/extraction-contrast?card=sample&arm=combined&sentence=s03&dimension=kind&round=2#input'}
        page = render_study(SimpleNamespace(root=ROOT), query).decode()
        self.assertIn('/extraction-contrast?card=sample&amp;arm=combined&amp;sentence=s03&amp;dimension=kind&amp;round=2#input', page)
