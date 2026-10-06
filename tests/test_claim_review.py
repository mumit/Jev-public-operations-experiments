import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tests import test_public_note_language as note_tests
from triage_bench import claim_review as review
from triage_bench.claim_review_service import ClaimReviewStudy
from triage_bench.public_note_features import DIMENSIONS
from triage_bench.study_page import return_path


class ClaimReviewTests(unittest.TestCase):
    def setUp(self):
        self.p, _ = note_tests.NoteLanguageTests().fixture()
        self.original = {c['id']: dict(zip(DIMENSIONS, ['non_assertion','none','unmapped','none_or_unclear','none_or_unclear','unclear']), accepted=False, minimum_required_probability=.1, review_reason='not_single_assertion') for c in self.p['candidates']}
        self.export = {'schema': review.SCHEMA, 'workflow_sha256': 'digest', 'note_id': self.p['id'], 'proposal': copy.deepcopy(self.original),
            'reviews': {c['id']: {'decision':'withhold','reason':'unresolved'} for c in self.p['candidates']}}
        for name, value in [('fingerprint','digest'),('packet',self.p),('proposal',self.original)]:
            patcher=patch.object(review,name,return_value=value); patcher.start(); self.addCleanup(patcher.stop)

    def confirm(self, identifier=None):
        identifier=identifier or self.p['candidates'][1]['id']
        v={'role':'assertion','service':self.p['services'][0],'kind':'metric_direction','channel':self.p['channels'][0],
            'measure':'none_or_unclear','polarity':'positive'}
        self.export['reviews'][identifier]={'decision':'confirm','values':v}
        return identifier

    def test_partial_review_cannot_prepare_complete_request(self):
        self.export['reviews'].pop(self.p['candidates'][0]['id'])
        with self.assertRaises(ValueError):review.validate(self.export)
        result=review.validate(self.export,require_complete=False)
        self.assertFalse(result['complete']); self.assertIsNone(result['request'])

    def test_explicit_confirmation_does_not_fabricate_probability_or_mutate_proposals(self):
        identifier=self.confirm(); before=copy.deepcopy((self.p,self.original,self.export))
        result=review.validate(self.export)
        self.assertEqual(result['confirmed'],[identifier]);self.assertEqual(result['provider_calls'],0)
        self.assertEqual(len(result['corrections']),1)
        self.assertEqual((self.p,self.original,self.export),before)
        self.assertNotIn('probability',json.dumps(result['request']))

    def test_request_uses_confirmed_subject_meaning_exact_span_and_only_selected_ledger(self):
        identifier=self.confirm(); result=review.validate(self.export); request=result['request']
        state=json.loads(request['state']); self.assertEqual(state['note'],self.p['note'])
        self.assertEqual([s['service'] for s in state['services']],[self.p['services'][0]])
        text=request['questions'][identifier+'_verdict']['instructions']
        self.assertIn(self.p['candidates'][1]['text'],text);self.assertIn('"kind":"metric_direction"',text)
        self.export['reviews'][identifier]['values']['polarity']='negative'
        self.assertNotEqual(review.validate(self.export)['request_sha256'],result['request_sha256'])

    def test_withheld_only_review_produces_no_model_body(self):
        result=review.validate(self.export);self.assertIsNone(result['request']);self.assertIsNone(result['request_sha256'])

    def test_unknown_service_compound_unmapped_and_nonstring_are_rejected(self):
        identifier=self.confirm()
        for dim,value in [('service','invented'),('role','multiple_assertions'),('kind','unmapped'),('polarity',True),('channel',12)]:
            bad=copy.deepcopy(self.export);bad['reviews'][identifier]['values'][dim]=value
            with self.assertRaises(ValueError):review.validate(bad)

    def test_provenance_proposal_and_irrelevant_dimensions_are_checked(self):
        identifier=self.confirm()
        for mutate in [lambda e:e.update(workflow_sha256='wrong'),lambda e:e['proposal'][identifier].update(service='invented'),
                       lambda e:e['reviews'][identifier]['values'].update(measure='duration')]:
            bad=copy.deepcopy(self.export);mutate(bad)
            with self.assertRaises(ValueError):review.validate(bad)

    def test_duplicate_json_keys_and_nonfinite_numbers_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'review.json'
            for text in ['{"reviews":{},"reviews":{}}','{"value":NaN}']:
                path.write_text(text)
                with self.assertRaises(ValueError):review.read_export(path)

    def test_service_excludes_annotations_verdicts_and_recording_metadata(self):
        evidence=unittest.mock.Mock(); service=ClaimReviewStudy(evidence)
        with patch('triage_bench.claim_review_service.packet',return_value=self.p),patch('triage_bench.claim_review_service.proposal',return_value=self.original),patch('triage_bench.claim_review_service.fingerprint',return_value='digest'):
            result=service.card(self.p['id'])
        for key in ('reference','outcomes','source_report_id','parent_note_id','responses','extraction_request'):
            self.assertNotIn(key,result)
        self.assertEqual(result['proposal'],self.original);evidence.verified.assert_called_once()
        self.assertEqual(return_path('/claim-review?card=example'),'/claim-review?card=example')

    def test_browser_numeric_roundtrip_preserves_proposals_without_boolean_coercion(self):
        identifier=self.p['candidates'][0]['id']
        self.original[identifier]['minimum_required_probability']=1.0
        self.export['proposal'][identifier]['minimum_required_probability']=1
        self.assertTrue(review.validate(self.export)['complete'])
        self.export['proposal'][identifier]['accepted']=0
        with self.assertRaises(ValueError):review.validate(self.export)
