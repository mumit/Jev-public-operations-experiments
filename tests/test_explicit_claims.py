import copy,json,unittest
from unittest.mock import patch
from triage_bench import explicit_claim_features as f,explicit_claim_data as d,explicit_claim_trial as t

class ExplicitContractTests(unittest.TestCase):
    def setUp(self):
        self.p=d.boundaries()[0];self.o=copy.deepcopy(self.p['observation']);self.c=copy.deepcopy(self.p['claim'])
    def test_hand_specified_boundary_oracle(self):
        fixtures=d.boundaries()
        self.assertEqual(len(fixtures),34)
        for p in fixtures:
            with self.subTest(p=p['id']):self.assertEqual(f.evaluate(p['observation'],p['claim'])['answer'],p['fixture_answer'])
        self.assertEqual([p['fixture_answer'] for p in fixtures],[r['answer'] for r in d.references(fixtures)])
    def test_fields_reject_extra_wrong_service_boolean_and_channel(self):
        for changes in ({'service':'other'},{'asserted':'false'},{'asserted':1},{'channel':'invented'},{'draft':'overwrite'},{'measure':'duration_median_us'}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):f.request(self.o,{**self.c,**changes})
    def test_missing_invalid_numeric_values_are_unknown_not_false(self):
        for v in (None,True,float('inf'),float('nan'),'3'):
            self.o['metrics']['cpu']['signed_change']=v
            for asserted in (True,False):self.assertEqual(f.evaluate(self.o,{**self.c,'asserted':asserted})['answer'],'unanswerable')
        for v in (-1,.200001,None,True):
            self.o['metrics']['cpu'].update(signed_change=3.,before_missing_fraction=v)
            self.assertEqual(f.evaluate(self.o,self.c)['answer'],'unanswerable')
    def test_duration_and_counts_do_not_trust_invalid_counts(self):
        c={'service':self.o['service'],'kind':'span_adequacy','asserted':True}
        for v in (-1,5.5,True,None,'5',float('inf')):
            self.o['trace']['after']['spans']=v
            self.assertEqual(f.evaluate(self.o,c)['answer'],'unanswerable')
            self.assertEqual(f.evaluate(self.o,{**c,'kind':'duration_material','measure':'duration_median_us'})['answer'],'unanswerable')
    def test_wire_is_selected_raw_facts_not_reference_or_full_observation(self):
        body=f.request(self.o,self.c);state=json.loads(body['state'])
        self.assertEqual(set(state),{'service','window_seconds','claim','selected_observations','policy'})
        self.assertEqual(set(state['selected_observations']),{'signed_change','before_missing_fraction','after_missing_fraction'})
        self.assertNotIn('trace',body['state']);self.assertNotIn('truth',body['state']);self.assertNotIn('answer',body['state'])
        self.assertEqual(set(body['questions']),{'claim_verdict'})
    def test_both_polarities_of_health_and_cause_stay_unknown(self):
        for k in ('health','causality'):
            for asserted in (True,False):self.assertEqual(f.evaluate(self.o,{'service':self.o['service'],'kind':k,'asserted':asserted})['answer'],'unanswerable')
    def test_missing_reply_denominator_and_confident_wrong_display(self):
        p={k:v for k,v in self.p.items() if k!='fixture_answer'};ref={'id':p['id'],'answer':'supported'}
        row={'card_id':p['id'],'round':1,'answers':{'claim_verdict':{'choice':'contradicted','probabilities':{'contradicted':.9,'supported':.1,'unanswerable':0}}},'latency_ms':1}
        def fake_load(path):return [p] if path.name=='inputs.json' else [ref]
        with patch.object(t,'verified_rows',return_value=([row],{'attempted_calls':1,'status':'incomplete_or_failed'})),patch.object(t,'load',side_effect=fake_load),patch.object(t,'sha',return_value='fixture'),patch('pathlib.Path.read_bytes',return_value=b'fixture'):
            r=t.score('development')
        self.assertEqual(r['opportunities'],3);self.assertEqual(r['valid_answers'],1);self.assertEqual(r['wrong_displays'],1);self.assertFalse(r['passes'])
    def test_stable_assessment_preserves_outcomes_but_excludes_timing(self):
        self.assertEqual(t.stable({'outcomes':[1],'exact_evaluator_timing':{'total_nanoseconds':1}}),{'outcomes':[1]})
    def test_confirmation_requires_committed_passing_development(self):
        with patch.object(t,'committed'),patch.object(t,'score',return_value={'passes':False}),patch.object(d,'prepare') as prepare:
            with self.assertRaises(ValueError):t.prepare('confirmation')
            prepare.assert_not_called()

if __name__=='__main__':unittest.main()
