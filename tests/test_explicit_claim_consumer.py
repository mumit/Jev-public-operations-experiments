import json,unittest
from unittest.mock import patch
from types import SimpleNamespace
from triage_bench.paths import ROOT
from triage_bench.explicit_claim_service import ExplicitClaimStudy
from triage_bench import explicit_claim_trial as t

class ExplicitConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.study=ExplicitClaimStudy(ROOT);cls.identifier='ECB-duration_below-1'
    def test_recorded_wrong_answer_preserved_and_reference_hidden(self):
        with patch.object(self.study,'verified',return_value=t.load(t.result_path('development'))):
            hidden=self.study.card('development',self.identifier);shown=self.study.card('development',self.identifier,True)
        self.assertIsNone(hidden['reference']);self.assertIsNone(hidden['outcomes']);self.assertIsNone(hidden['exact_result'])
        self.assertEqual(hidden['responses'][0]['answers']['claim_verdict']['choice'],'supported');self.assertEqual(shown['reference']['answer'],'contradicted');self.assertEqual(shown['exact_result']['answer'],'contradicted')
    def test_preview_negates_assertion_without_calling_provider_or_writing(self):
        claim={'service':'example-service','kind':'duration_material','measure':'duration_median_us','asserted':False}
        with patch('urllib.request.OpenerDirector.open',side_effect=AssertionError('No provider calls')):
            p=self.study.preview('development',self.identifier,json.dumps(claim))
        self.assertEqual(p['exact_result']['answer'],'supported');self.assertEqual(p['provider_calls'],0);self.assertEqual(p['server_writes'],0);self.assertFalse(p['human_review_recorded']);self.assertEqual(p['status'],'local_draft')
        self.assertNotIn('reference',p);self.assertNotIn('raw_response',p)
    def test_format_preview_discloses_calculated_facts_and_has_no_provider_answer(self):
        claim={'service':'example-service','kind':'duration_material','measure':'duration_median_us','asserted':True}
        p=self.study.preview('format',self.identifier,json.dumps(claim),'calculated')
        state=json.loads(p['prospective_jev_request']['state']);self.assertIn('calculated_observations',state);self.assertNotIn('raw_response',p);self.assertEqual(p['exact_result']['answer'],'contradicted')
    def test_preview_rejects_unknown_id_service_extra_fields_and_large_payload(self):
        claim={'service':'example-service','kind':'health','asserted':True}
        for identifier,c in [('bad',claim),(self.identifier,{**claim,'service':'other'}),(self.identifier,{**claim,'reference':'supported'})]:
            with self.assertRaises(ValueError):self.study.preview('development',identifier,json.dumps(c))
        with self.assertRaises(ValueError):self.study.preview('development',self.identifier,'x'*1025)
        with self.assertRaises(ValueError):self.study.preview('development',self.identifier,json.dumps(claim),'calculated')
        with self.assertRaises(ValueError):self.study.preview('bad',self.identifier,json.dumps(claim))
    def test_reader_retains_claim_and_representation(self):
        from triage_bench.study_page import render_study
        html=render_study(SimpleNamespace(root=ROOT),{'doc':'explicit-claims','return':'/explicit-claims?phase=format&card=ECB-duration_below-1&arm=calculated#inspect'}).decode()
        self.assertIn('Explicit claims: Jev versus an exact policy evaluator',html);self.assertIn('arm=calculated',html);self.assertIn('ECB-duration_below-1',html)
    def test_missing_window_preview_preserves_unknown_for_both_assertions(self):
        from triage_bench.explicit_missing_data import DATA
        p=next(r for r in t.load(DATA/'inputs.json') if r['category']=='missing_window' and r['claim']['kind']=='metric_material')
        with patch('urllib.request.OpenerDirector.open',side_effect=AssertionError('No provider calls')):
            for asserted in (True,False):
                r=self.study.preview('fresh',p['id'],json.dumps({**p['claim'],'asserted':asserted}),'calculated')
                self.assertEqual(r['exact_result']['answer'],'unanswerable')
                state=json.loads(r['prospective_jev_request']['state']);self.assertIsNone(state['window_seconds']['after']);self.assertIsNone(state['selected_observations']['after_missing_fraction'])
                self.assertFalse(state['calculated_observations']['observations_eligible'])
        with self.assertRaises(ValueError):self.study.preview('fresh',p['id'],json.dumps(p['claim']),'typed')
    def test_confirmation_summary_counts_each_opportunity_once(self):
        panels=[{'arm':'calculated','scope':scope,'claims':360,'correct':360,'correct_display':360,'wrong_display':0,'rule_correct':360} for scope in ('overall','complete_windows','missing_window')]
        with patch.object(self.study,'verified',return_value={'candidate_passes':True,'outcomes':[],'panels':panels}):r=self.study.overview('fresh')
        self.assertTrue(r['available']);self.assertEqual(r['opportunities'],360);self.assertEqual(r['correct_answers'],360)

if __name__=='__main__':unittest.main()
