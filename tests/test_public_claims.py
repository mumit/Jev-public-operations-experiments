import copy,json,unittest
from triage_bench.public_claim_reference import evaluate
from triage_bench.public_claim_features import ledger,request,FIELDS,ARMS
from triage_bench.public_claim_data import claims
from triage_bench.public_claim_trial import assess,answers
from triage_bench.profile import MODEL

def observation():
    return {'service':'sample-service','metrics':{'socket':{'signed_change':-3.,'before_missing_fraction':.2,'after_missing_fraction':.2,'before_median':6.,'after_median':3.}},'trace':None,'metric_change_definition':'Scaled signed change.','window_seconds':{'before':60,'after':60},'condition':'Observed service.'}

class ClaimTests(unittest.TestCase):
    def test_missing_is_not_contradiction(self):
        o=observation();p={'kind':'metric_material','channel':'socket','asserted':True}
        self.assertEqual(evaluate(o,p)['answer'],'supported')
        self.assertEqual(evaluate(o,{**p,'asserted':False})['answer'],'contradicted')
        for value in (.200001,None):
            o['metrics']['socket']['after_missing_fraction']=value
            self.assertEqual(evaluate(o,p)['answer'],'unanswerable')
            self.assertEqual(evaluate(o,{**p,'asserted':False})['answer'],'unanswerable')
    def test_duration_boundary_and_inadequate_samples(self):
        o=observation();o['trace']={'before':{'spans':5,'duration_median_us':100},'after':{'spans':5,'duration_median_us':75}}
        p={'kind':'duration_material','measure':'duration_median_us','asserted':True}
        self.assertEqual(evaluate(o,p)['answer'],'supported')
        o['trace']['after']['spans']=4;self.assertEqual(evaluate(o,p)['answer'],'unanswerable')
        o['trace']['after']['spans']=5;o['trace']['before']['duration_median_us']=0
        self.assertEqual(evaluate(o,p)['answer'],'unanswerable')
    def test_absence_count_vs_health_cause(self):
        o=observation()
        self.assertEqual(evaluate(o,{'kind':'span_adequacy','asserted':False})['answer'],'unanswerable')
        o['trace']={'before':{'spans':0},'after':{'spans':0}}
        self.assertEqual(evaluate(o,{'kind':'span_adequacy','asserted':False})['answer'],'supported')
        for kind in ('causality','health'):
            for positive in (True,False):self.assertEqual(evaluate(o,{'kind':kind,'asserted':positive})['answer'],'unanswerable')
    def test_ledger_preserves_values_and_eligibility(self):
        o=observation();before=copy.deepcopy(o);l=ledger(o)
        self.assertEqual(l['metric_facts'][0]['absolute_scaled_change'],3)
        self.assertTrue(l['metric_facts'][0]['eligible_for_change_policy'])
        self.assertIsNone(l['trace_observations']);self.assertFalse(any(r['eligible_for_change_policy'] for r in l['duration_facts']))
        self.assertEqual(o,before)
    def test_balanced_shuffled_claims_and_no_reference_metadata(self):
        source={'id':'fixture','observation':observation()};statements,refs=claims(source)
        self.assertEqual(sorted(r['answer'] for r in refs.values()),['contradicted','supported','unanswerable'])
        self.assertEqual((statements,refs),claims(source))
        for arm in ARMS:
            body=request(source['observation'],statements,arm);self.assertEqual(set(body['questions']),set(FIELDS))
            state=json.loads(body['state']);self.assertNotIn('answers',state);self.assertNotIn('proposition',state);self.assertNotIn('id',state)
            for field in FIELDS:self.assertTrue(body['questions'][field]['instructions'].endswith(statements[field]))
    def test_failed_denominators_and_false_support(self):
        refs=[{'id':'fixture','answers':{f:{'answer':v} for f,v in zip(FIELDS,('supported','contradicted','unanswerable'))}}]
        packets=[{'id':'fixture','dataset':'Sample','case_id':'one'}]
        result=assess([],packets,refs)['Sample'];self.assertFalse(result['research_gate'])
        self.assertEqual(result['arms']['ledger']['per_round'][0]['failed_or_missing'],3)
        rows=[{'card_id':'fixture','arm':a,'round':n,'status':'ok','answers':{f:{'choice':'supported','probabilities':{'supported':.9,'contradicted':.05,'unanswerable':.05}} for f in FIELDS}} for a in ARMS for n in (1,2,3)]
        result=assess(rows,packets,refs)['Sample'];self.assertEqual(result['arms']['ledger']['per_round'][0]['false_displayed_support'],2);self.assertFalse(result['research_gate'])
    def test_normalization_rejects_invented_fields(self):
        body=request(observation(),{f:'Claim.' for f in FIELDS},'observations')
        raw={'model':MODEL,'answers':{f:{'choice':'supported','probabilities':{'supported':1.,'contradicted':0.,'unanswerable':0.}} for f in FIELDS}}
        self.assertEqual(answers(raw,body)['statement_a']['choice'],'supported')
        raw['answers']['statement_a']['probabilities']['supported']=.5
        with self.assertRaises(ValueError):answers(raw,body)
        raw['answers']['extra']={}
        with self.assertRaises(ValueError):answers(raw,body)
if __name__=='__main__':unittest.main()
