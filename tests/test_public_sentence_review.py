import copy
import unittest
from tests import test_public_notes as note_tests
from triage_bench.profile import MODEL
from triage_bench.public_note_v2_features import extraction_request
from triage_bench.public_sentence_features import validate_reply, extract, GlobalReplyError, whole_note_counterfactual
from triage_bench.public_sentence_trial import assess, counterfactual


class SentenceReviewTests(unittest.TestCase):
    def fixture(self):
        p, r = note_tests.NoteTests().fixture(); p['extraction_request'] = extraction_request(p)
        body = p['extraction_request']; gold = {a['id']: a for a in r['annotations']}
        raw = {'model': MODEL, 'usage': {'input_tokens': 100}, 'answers': {}}
        for field, question in body['questions'].items():
            sid, dimension = field.split('_', 1); choice = gold[sid][dimension]
            raw['answers'][field] = {'type': 'choice', 'choice': choice,
                'probabilities': {k: float(k == choice) for k in question['criteria']}}
        return p, r, body, raw

    def test_invalid_unused_dimension_quarantines_only_its_sentence(self):
        p, r, body, raw = self.fixture()
        a = next(a for a in r['annotations'] if a['actionable'] and a['kind'] == 'health')
        field = a['id'] + '_channel'; answer = raw['answers'][field]
        other = next(k for k in answer['probabilities'] if k != answer['choice'])
        answer['probabilities'] = {k: .49 if k == answer['choice'] else .51 if k == other else 0 for k in answer['probabilities']}
        row = validate_reply(raw, body, 32768); result = extract(p, row)
        self.assertEqual(row['quarantined_sentences'], [a['id']])
        self.assertEqual(len(row['answers']), 71)
        self.assertEqual(sum(v['accepted'] for v in result.values()), 5)
        self.assertFalse(result[a['id']]['accepted'])
        self.assertIsNone(result[a['id']]['minimum_required_probability'])
        self.assertNotIn(field, row['answers'])
        self.assertEqual(raw['answers'][field]['choice'], answer['choice'])
        self.assertEqual(sum(v['accepted'] for v in whole_note_counterfactual(p, {'raw_response': raw}).values()), 0)
        row.update(card_id=p['id'], round=1, raw_response=raw)
        panel = counterfactual([p], [r], [row])[0]
        self.assertEqual(panel['recovered_correct_bindings'], 5)
        self.assertEqual(panel['lost_correct_bindings'], 0)

    def test_missing_field_does_not_invent_a_choice_or_probability(self):
        p, r, body, raw = self.fixture(); field = next(iter(raw['answers']))
        del raw['answers'][field]
        row = validate_reply(raw, body, 32768)
        self.assertNotIn(field, row['answers'])
        self.assertEqual(len(row['quarantined_sentences']), 1)
        self.assertIsNone(extract(p, row)[field.split('_')[0]]['minimum_required_probability'])

    def test_unexpected_fields_wrong_model_and_bad_usage_are_global(self):
        p, r, body, raw = self.fixture()
        for mutation in ('extra', 'model', 'usage', 'overflow', 'shape'):
            value = copy.deepcopy(raw)
            if mutation == 'extra': value['answers']['surprise'] = {}
            elif mutation == 'model': value['model'] = 'wrong'
            elif mutation == 'usage': value['usage']['input_tokens'] = True
            elif mutation == 'overflow': value['usage']['input_tokens'] = 32769
            else: value['answers'] = []
            with self.assertRaises(GlobalReplyError): validate_reply(value, body, 32768)

    def test_verdict_inconsistency_preserves_sibling_verdict(self):
        body = {'questions': {f: {'criteria': {'supported': '', 'contradicted': '', 'unanswerable': ''}} for f in ('s02_verdict', 's03_verdict')}}
        good = {'type': 'choice', 'choice': 'supported', 'probabilities': {'supported': 1, 'contradicted': 0, 'unanswerable': 0}}
        bad = {'type': 'choice', 'choice': 'supported', 'probabilities': {'supported': .49, 'contradicted': .51, 'unanswerable': 0}}
        raw = {'model': MODEL, 'usage': {'input_tokens': 3}, 'answers': {'s02_verdict': good, 's03_verdict': bad}}
        row = validate_reply(raw, body, 32768)
        self.assertEqual(set(row['answers']), {'s02_verdict'})
        self.assertEqual(row['quarantined_sentences'], ['s03'])

    def test_partial_completed_reply_retains_missing_verdict_denominator(self):
        p, r, assigned, verdicts, erows = note_tests.NoteTests().panel()
        row = next(v for v in verdicts if v['arm'] == 'jev' and v['round'] == 1)
        del row['answers'][next(iter(row['answers']))]; row['status'] = 'ok_with_review'
        result = assess([p], [r], assigned, verdicts, erows)['Sample']['arms']['jev']['per_round'][0]
        self.assertTrue(result['complete_calls'])
        self.assertEqual(result['routable_claims'], 6)
        self.assertEqual(result['end_to_end_correct'], 5)
        self.assertEqual(result['all_six_correct'], 0)
        verdicts.remove(row)
        self.assertFalse(assess([p], [r], assigned, verdicts, erows)['Sample']['arms']['jev']['per_round'][0]['complete_calls'])

    def test_correct_verdict_for_wrong_binding_remains_unsafe(self):
        p, r, assigned, verdicts, erows = note_tests.NoteTests().panel()
        bound = next(b for b in assigned if b['arm'] == 'jev' and b['round'] == 1)
        a = next(a for a in r['annotations'] if a['actionable'])
        bound['bindings'][a['id']]['service'] = 'beta' if a['service'] == 'alpha' else 'alpha'
        row = assess([p], [r], assigned, verdicts, erows)['Sample']['arms']['jev']['per_round'][0]
        self.assertEqual(row['unsafe_displayed'], 1)
        self.assertEqual(row['end_to_end_correct'], 5)

    def test_reader_hides_reference_results_without_mutating_saved_assessment(self):
        from unittest.mock import patch
        from triage_bench.public_sentence_service import PublicSentenceStudy
        p, r, assigned, verdicts, erows = note_tests.NoteTests().panel()
        study = PublicSentenceStudy('.')
        result = {'bindings': assigned, 'datasets': assess([p], [r], assigned, verdicts, erows)}
        before = copy.deepcopy(result)
        def loaded(path):
            if path.name == 'inputs.json': return [p]
            if path.name == 'references.json': return [r]
            return []
        with patch.object(study, 'verified', return_value=result), patch('triage_bench.public_sentence_service.load', side_effect=loaded), patch('pathlib.Path.read_text', return_value=''):
            hidden = study.card(p['id'])
            self.assertIsNone(hidden['reference'])
            self.assertNotIn('end_to_end_correct', hidden['outcomes']['jev'][0])
            self.assertEqual(study.card(p['id'], True)['reference'], r)
            self.assertEqual(result, before)

    def test_formatted_report_retains_sentence_selection(self):
        from triage_bench.study_page import render_study
        from triage_bench.paths import ROOT
        from types import SimpleNamespace
        query = {'doc': 'public-sentence-review', 'return': '/sentence-review?card=sample&sentence=s03&dimension=kind&round=2#input'}
        page = render_study(SimpleNamespace(root=ROOT), query).decode()
        self.assertIn('/sentence-review?card=sample&amp;sentence=s03&amp;dimension=kind&amp;round=2#input', page)

    def test_global_error_stops_once_and_redacts_credentials(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch, MagicMock
        from triage_bench import public_sentence_trial as trial
        from triage_bench.app import profiles
        p, _, body, raw = self.fixture()
        profile = profiles()['jev']; profile['api_key'] = 'sentence-private-fixture'
        frozen = {k: profile[k] for k in ('model', 'endpoint', 'context_tokens')}
        raw['answers']['unexpected'] = {}; raw['echo'] = profile['api_key']
        req = {'id': 'one', 'card_id': p['id'], 'arm': 'jev', 'round': 1, 'phase': 'extraction', 'body': body}
        response = MagicMock(); response.__enter__.return_value.read.return_value = json.dumps(raw).encode()
        opener = MagicMock(); opener.open.return_value = response
        with tempfile.TemporaryDirectory() as t:
            directory = Path(t); protocol = directory / 'protocol'; protocol.write_text('{}')
            with patch.object(trial, 'check', return_value=(frozen, [req, {**req, 'id': 'two'}])), patch.object(trial, 'protocol_path', return_value=protocol), patch.object(trial, 'output', return_value=directory / 'hosted'), patch('urllib.request.build_opener', return_value=opener):
                result = trial.run('extraction', profile)
                self.assertEqual(result['stopped_reason'], 'answer_envelope_mismatch')
                self.assertEqual(result['unattempted_jobs'], 1)
                self.assertNotIn(profile['api_key'], (directory / 'hosted/responses.jsonl').read_text())
                with self.assertRaises(FileExistsError): trial.run('extraction', profile)
                self.assertEqual(opener.open.call_count, 1)

    def test_zero_accepted_claims_skips_without_fabricated_provider_evidence(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch, MagicMock
        from triage_bench import public_sentence_trial as trial
        from triage_bench.app import profiles
        profile = profiles()['jev']; profile['api_key'] = 'sentence-private-fixture'
        frozen = {k: profile[k] for k in ('model', 'endpoint', 'context_tokens')}
        req = {'id': 'skip', 'card_id': 'note', 'arm': 'jev', 'round': 1, 'phase': 'verdict', 'body': None}
        with tempfile.TemporaryDirectory() as t:
            directory = Path(t); protocol = directory / 'protocol'; protocol.write_text('{}')
            opener = MagicMock()
            with patch.object(trial, 'check', return_value=(frozen, [req])), patch.object(trial, 'protocol_path', return_value=protocol), patch.object(trial, 'output', return_value=directory / 'hosted'), patch('urllib.request.build_opener', return_value=opener):
                result = trial.run('verdict', profile)
                self.assertEqual(result['attempted_calls'], 0)
                self.assertFalse(opener.open.called)
                row = json.loads((directory / 'hosted/responses.jsonl').read_text())
                self.assertFalse(any(k in row for k in ('answers', 'usage', 'raw_response')))
