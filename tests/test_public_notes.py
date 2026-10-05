import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from tests import test_public_fresh_claims as fresh_tests
from triage_bench.public_note_features import compose, candidates, extraction, parser, annotated, verdict_request, DIMENSIONS, accept
from triage_bench.public_note_trial import assess


class NoteTests(unittest.TestCase):
    def fixture(self):
        old, reference = fresh_tests.FreshClaimTests().fixture()
        return compose(old, reference, old['observations'])

    def answers(self, reference):
        return {a['id'] + '_' + d: {'choice': a[d], 'probabilities': {a[d]: .99}} for a in reference['annotations'] for d in DIMENSIONS}

    def test_generic_boundaries_match_spans_without_splitting_decimal_or_compound(self):
        p, r = self.fixture()
        self.assertEqual(len(p['candidates']), 12)
        self.assertEqual(sum(a['actionable'] for a in r['annotations']), 6)
        self.assertEqual(sum(a['role'] == 'assertion' for a in r['annotations']), 7)
        for a in r['annotations']:
            self.assertEqual(p['note'][a['start']:a['end']], a['text'])
        self.assertEqual(len(candidates('Value is 3.0. Check it? Alpha caused it and beta is healthy.')), 3)

    def test_extraction_has_context_but_no_telemetry_or_gold(self):
        p, r = self.fixture(); body = p['extraction_request']; state = json.loads(body['state'])
        self.assertEqual(len(body['questions']), 72)
        self.assertEqual(state['note'], p['note'])
        self.assertEqual(state['observed_service_inventory'], ['alpha', 'beta'])
        self.assertNotIn('observations', state)
        self.assertNotIn('annotations', state)
        self.assertNotIn('supported', json.dumps(body))
        self.assertTrue(all('candidates[' in q['instructions'] for q in body['questions'].values()))

    def test_relevant_probability_gate_ignores_irrelevant_dimensions(self):
        p, r = self.fixture(); answers = self.answers(r)
        a = next(a for a in r['annotations'] if a['kind'] == 'health' and a['actionable'])
        answers[a['id'] + '_channel']['probabilities'] = {'none_or_unclear': .01}
        self.assertTrue(extraction(p, answers)[a['id']]['accepted'])
        answers[a['id'] + '_service']['probabilities'][a['service']] = .69
        self.assertEqual(extraction(p, answers)[a['id']]['review_reason'], 'low_extraction_probability')

    def test_ambiguous_compound_and_missing_dimensions_are_not_accepted(self):
        p, r = self.fixture(); result = extraction(p, self.answers(r))
        self.assertEqual(sum(v['accepted'] for v in result.values()), 6)
        ambiguous = next(a for a in r['annotations'] if a['category'] == 'ambiguous')
        self.assertEqual(result[ambiguous['id']]['review_reason'], 'unresolved_service')
        self.assertFalse(any(v['accepted'] for v in extraction(p, {}).values()))
        metric = next(a for a in r['annotations'] if a['kind'] == 'metric_material')
        values = {d: metric[d] for d in DIMENSIONS}; values['channel'] = 'none_or_unclear'
        self.assertEqual(accept(p, values)['review_reason'], 'unresolved_channel')

    def test_parser_accepts_only_explicit_literal_claims(self):
        p, r = self.fixture(); values = parser(p)
        self.assertEqual(sum(v['accepted'] for v in values.values()), 2)
        self.assertTrue(all(v['minimum_required_probability'] is None for v in values.values()))
        self.assertFalse(any(values[a['id']]['accepted'] for a in r['annotations'] if not a['actionable']))

    def test_predicted_binding_drives_actual_verdict_facts_without_gold_repair(self):
        p, r = self.fixture(); bound = annotated(p, r)
        self.assertIsNone(verdict_request(p, {k: {**v, 'accepted': False} for k, v in bound.items()}))
        a = next(a for a in r['annotations'] if a['actionable'])
        predicted = {k: {**v, 'accepted': k == a['id']} for k, v in bound.items()}
        wrong_service = 'beta' if a['service'] == 'alpha' else 'alpha'
        predicted[a['id']]['service'] = wrong_service
        body = verdict_request(p, predicted); state = json.loads(body['state'])
        self.assertEqual([s['service'] for s in state['services']], [wrong_service])
        self.assertTrue(body['questions'][a['id'] + '_verdict']['instructions'].endswith(a['text']))
        self.assertEqual(state['note'], p['note'])
        self.assertNotIn('proposition', body['state'])

    def panel(self):
        p, r = self.fixture(); bindings = annotated(p, r)
        assigned, verdicts, erows = [], [], []
        for n in (1, 2, 3):
            erows.append({'card_id': p['id'], 'round': n, 'status': 'ok'})
            for arm in ('jev', 'parser', 'annotated'):
                assigned.append({'card_id': p['id'], 'arm': arm, 'round': n, 'bindings': copy.deepcopy(bindings)})
                verdicts.append({'card_id': p['id'], 'arm': arm, 'round': n, 'status': 'ok', 'answers': {
                    a['id'] + '_verdict': {'choice': a['verdict'], 'probabilities': {a['verdict']: .99}}
                    for a in r['annotations'] if a['actionable']}})
        return p, r, assigned, verdicts, erows

    def test_coincidental_right_verdict_on_wrong_service_is_unsafe_and_fails(self):
        p, r, assigned, verdicts, erows = self.panel()
        target = next(a for a in r['annotations'] if a['actionable'])
        wrong = next(v for v in assigned if v['arm'] == 'jev' and v['round'] == 1)
        wrong['bindings'][target['id']]['service'] = 'beta' if target['service'] == 'alpha' else 'alpha'
        result = assess([p], [r], assigned, verdicts, erows)['Sample']['arms']['jev']
        row = result['per_round'][0]
        self.assertEqual(row['unsafe_displayed'], 1)
        self.assertEqual(row['end_to_end_correct'], 5)
        self.assertEqual(row['conditional_verdict_total'], 5)
        self.assertFalse(result['research_gate'])

    def test_missing_verdict_keeps_gold_claims_and_failed_call(self):
        p, r, assigned, verdicts, erows = self.panel()
        verdicts = [v for v in verdicts if not (v['arm'] == 'jev' and v['round'] == 1)]
        row = assess([p], [r], assigned, verdicts, erows)['Sample']['arms']['jev']['per_round'][0]
        self.assertEqual(row['routable_claims'], 6)
        self.assertEqual(row['atomic_assertions_in_notes'], 9)
        self.assertEqual(row['end_to_end_correct'], 0)
        self.assertFalse(row['complete_calls'])

    def test_review_only_claim_wrongly_accepted_is_not_hidden_from_display_score(self):
        p, r, assigned, verdicts, erows = self.panel()
        target = next(a for a in r['annotations'] if a['category'] == 'ambiguous')
        wrong = next(v for v in assigned if v['arm'] == 'jev' and v['round'] == 1)
        wrong['bindings'][target['id']].update(accepted=True, service='alpha')
        reply = next(v for v in verdicts if v['arm'] == 'jev' and v['round'] == 1)
        reply['answers'][target['id'] + '_verdict'] = {'choice': 'unanswerable', 'probabilities': {'unanswerable': .99}}
        row = assess([p], [r], assigned, verdicts, erows)['Sample']['arms']['jev']['per_round'][0]
        self.assertEqual(row['accepted_review_or_nonclaims'], 1)
        self.assertEqual(row['unsafe_displayed'], 1)

    def test_model_mismatch_stops_once_and_redacts(self):
        from triage_bench import public_note_trial as trial
        from triage_bench.app import profiles
        p, _ = self.fixture(); profile = profiles()['jev']; profile['api_key'] = 'private-note-fixture'
        frozen = {k: profile[k] for k in ('model', 'endpoint', 'context_tokens')}
        req = {'id': 'one', 'card_id': p['id'], 'arm': 'jev', 'round': 1, 'phase': 'extraction', 'body': p['extraction_request']}
        response = MagicMock(); response.__enter__.return_value.read.return_value = json.dumps({'model': 'wrong', 'echo': profile['api_key']}).encode()
        opener = MagicMock(); opener.open.return_value = response
        with tempfile.TemporaryDirectory() as t:
            path = Path(t); protocol = path / 'protocol.json'; protocol.write_text('{}')
            with patch.object(trial, 'check', return_value=(frozen, [req])), patch.object(trial, 'protocol_path', return_value=protocol), patch.object(trial, 'output', return_value=path / 'hosted'), patch('urllib.request.build_opener', return_value=opener):
                result = trial.run('extraction', profile)
                self.assertEqual(result['stopped_reason'], 'checkpoint_mismatch')
                self.assertNotIn(profile['api_key'], (path / 'hosted/responses.jsonl').read_text())
                with self.assertRaises(FileExistsError): trial.run('extraction', profile)
                self.assertEqual(opener.open.call_count, 1)

    def test_zero_claims_is_application_skip_without_provider_response(self):
        from triage_bench import public_note_trial as trial
        from triage_bench.app import profiles
        profile = profiles()['jev']; profile['api_key'] = 'private-note-fixture'
        frozen = {k: profile[k] for k in ('model', 'endpoint', 'context_tokens')}
        req = {'id': 'one', 'card_id': 'p', 'arm': 'jev', 'round': 1, 'phase': 'verdict', 'body': None}
        opener = MagicMock()
        with tempfile.TemporaryDirectory() as t:
            path = Path(t); protocol = path / 'protocol.json'; protocol.write_text('{}')
            with patch.object(trial, 'check', return_value=(frozen, [req])), patch.object(trial, 'protocol_path', return_value=protocol), patch.object(trial, 'output', return_value=path / 'hosted'), patch('urllib.request.build_opener', return_value=opener):
                result = trial.run('verdict', profile)
                row = json.loads((path / 'hosted/responses.jsonl').read_text())
                self.assertEqual(result['attempted_calls'], 0)
                self.assertEqual(result['status'], 'completed')
                self.assertNotIn('raw_response', row)
                self.assertFalse(opener.open.called)


class CompactNoteTests(unittest.TestCase):
    def test_compact_questions_preserve_note_inventory_spans_and_option_keys(self):
        from triage_bench.public_note_v2_features import extraction_request
        p, r = NoteTests().fixture()
        original = p['extraction_request']; compact = extraction_request(p)
        a, b = json.loads(original['state']), json.loads(compact['state'])
        definitions = b.pop('extraction_definitions')
        self.assertEqual(a, b)
        self.assertEqual(set(definitions), set(DIMENSIONS))
        for field, question in compact['questions'].items():
            dimension = field.split('_', 1)[1]
            self.assertEqual(set(question['criteria']), set(original['questions'][field]['criteria']))
            self.assertIn('extraction_definitions.' + dimension, question['instructions'])
            self.assertIn('Resolve pronouns only from a unique antecedent', definitions['service'])
        self.assertIn('Two or more independently checkable assertions', definitions['role'])
        self.assertIn('other thresholds', definitions['kind'])
        self.assertIn('zero or negative', definitions['polarity'])

    def test_compact_composition_and_verdict_helpers_are_original_frozen_functions(self):
        from triage_bench import public_note_features as original, public_note_v2_features as compact
        for name in ('extraction', 'parser', 'annotated', 'semantics', 'verdict_request'):
            self.assertIs(getattr(compact, name), getattr(original, name))


class NoteReaderTests(unittest.TestCase):
    def test_reader_preserves_selected_note_method_dimension_and_section(self):
        from types import SimpleNamespace
        from triage_bench.paths import ROOT
        from triage_bench.study_page import render_study, return_path
        value = '/note-extraction?dataset=Online+Boutique&card=sample&arm=parser&sentence=s06&round=2&dimension=service#input'
        self.assertEqual(return_path(value), value)
        page = render_study(SimpleNamespace(root=ROOT), {'doc':'public-note-extraction','return':value}).decode()
        self.assertIn('arm=parser&amp;sentence=s06', page)
        self.assertIn('dimension=service#input', page)

    def test_missing_evidence_does_not_become_empty_success(self):
        from triage_bench.public_note_service import PublicNoteStudy
        with patch.object(PublicNoteStudy, 'verified', side_effect=FileNotFoundError):
            self.assertFalse(PublicNoteStudy(Path('.')).overview()['available'])

    def test_reveal_hides_gold_and_does_not_mutate_cached_results(self):
        from triage_bench import public_note_service as service
        packet = {'id':'p','dataset':'Sample'}
        o = {'id':'p','sentence':'s01','gold_role':'assertion','reference':'supported','end_to_end_correct':True,'unsafe_displayed':False}
        result = {'datasets':{'Sample':{'arms':{'jev':{'outcomes':[o]}}}},'bindings':[]}
        with tempfile.TemporaryDirectory() as t:
            path=Path(t);(path/'responses.jsonl').write_text('{"card_id":"p"}\n')
            def fixture(p):
                return [packet] if p.name=='inputs.json' else [{'id':'p','annotations':[]}] if p.name=='references.json' else {'bindings':[]} if 'protocol' in p.name else []
            with patch.object(service.PublicNoteStudy,'verified',return_value=result),patch.object(service,'load',side_effect=fixture),patch.object(service,'output',return_value=path):
                study=service.PublicNoteStudy(path);hidden=study.card('p')
                self.assertIsNone(hidden['reference'])
                self.assertNotIn('end_to_end_correct',hidden['outcomes']['jev'][0])
                self.assertNotIn('reference',hidden['outcomes']['jev'][0])
                self.assertIn('reference',o)
                self.assertIsNotNone(study.card('p',True)['reference'])


class RejectedNoteTests(unittest.TestCase):
    def test_inconsistent_unused_field_quarantines_whole_frozen_response(self):
        from triage_bench import public_note_v2_trial as trial
        from triage_bench.app import profiles
        from triage_bench.profile import MODEL
        p,r=NoteTests().fixture();profile=profiles()['jev'];profile['api_key']='private-quarantine-fixture'
        body=p['extraction_request'];gold=NoteTests().answers(r)
        raw={'model':MODEL,'answers':{},'usage':{'input_tokens':123}}
        for field,q in body['questions'].items():
            choice=gold[field]['choice']
            raw['answers'][field]={'type':'choice','choice':choice,'probabilities':{k:float(k==choice) for k in q['criteria']},'confidence':1.}
        raw['answers']['s01_service'].update(choice='none',probabilities={'none':.49,'alpha':.50,'beta':.01,'ambiguous':0})
        req={'id':'one','card_id':p['id'],'arm':'jev','round':1,'phase':'extraction','body':body}
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps(raw).encode()
        opener=MagicMock();opener.open.return_value=response
        with tempfile.TemporaryDirectory() as t:
            path=Path(t);protocol=path/'protocol.json';protocol.write_text('{}')
            frozen={k:profile[k] for k in ('model','endpoint','context_tokens')}
            with patch.object(trial,'check',return_value=(frozen,[req])),patch.object(trial,'protocol_path',return_value=protocol),patch.object(trial,'output',return_value=path/'hosted'),patch('urllib.request.build_opener',return_value=opener):
                summary=trial.run('extraction',profile)
                saved=json.loads((path/'hosted/responses.jsonl').read_text())
                self.assertEqual(summary['failed'],1)
                self.assertEqual(summary['status'],'incomplete_or_failed')
                self.assertNotIn('answers',saved)
                self.assertEqual(len(saved['raw_response']['answers']),72)
                self.assertEqual(opener.open.call_count,1)

    def test_complete_extraction_is_required_before_any_dependent_binding(self):
        from triage_bench import public_note_v2_trial as trial
        with patch.object(trial,'verified_rows',side_effect=ValueError('Complete note evidence required.')) as reader:
            with self.assertRaises(ValueError):trial.bindings()
            reader.assert_called_once_with('extraction',complete=True)
