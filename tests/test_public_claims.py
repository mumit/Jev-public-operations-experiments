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
    def test_reference_reveal_does_not_mutate_results(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from triage_bench.public_claim_service import PublicClaimStudy
        packet={'id':'card','dataset':'Sample','observation':observation()}
        ref={'id':'card','answers':{}}
        outcome={'id':'card','field':'statement_a','round':1,'reference':'supported','correct':True,'false_displayed_support':False,'correct_displayed_support':True}
        result={'datasets':{'Sample':{'arms':{'ledger':{'outcomes':[outcome]}}}}}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);(path/'responses.jsonl').write_text(json.dumps({'card_id':'card'})+'\n')
            with patch.object(PublicClaimStudy,'verified',return_value=result),patch('triage_bench.public_claim_service.OUTPUT',path),patch('triage_bench.public_claim_service.load',side_effect=lambda p:[packet] if p.name=='inputs.json' else [ref]):
                study=PublicClaimStudy(path);hidden=study.card('card')
                self.assertIsNone(hidden['reference'])
                for key in ('reference','correct','false_displayed_support','correct_displayed_support'):self.assertNotIn(key,hidden['outcomes']['ledger'][0])
                self.assertEqual(study.card('card',True)['reference'],ref)
                self.assertIn('reference',outcome)
    def test_overview_keeps_numeric_counts(self):
        from unittest.mock import patch
        from triage_bench.public_claim_service import PublicClaimStudy
        packet={'id':'card','dataset':'Sample','case_id':'source','observation':observation()}
        result={'datasets':{'Sample':{'cards':1,'claims':3,'pairs':[],'stable_fixes':[],'stable_losses':[],'arms':{'ledger':{'outcomes':[],'stable_correct_claims':[]}}}}}
        with patch.object(PublicClaimStudy,'verified',return_value=result),patch('triage_bench.public_claim_service.load',return_value=[packet]):
            panel=PublicClaimStudy('.').overview()['datasets']['Sample']
            self.assertEqual(panel['cards'],1);self.assertEqual(panel['claims'],3);self.assertEqual(panel['card_choices'][0]['id'],'card')
    def test_article_return_preserves_claim(self):
        from triage_bench.study_page import return_path,render_study
        from triage_bench.paths import ROOT
        from types import SimpleNamespace
        value='/claim-assessment?dataset=Train+Ticket&card=fixture&arm=ledger&round=2&field=statement_c#input'
        self.assertEqual(return_path(value),value)
        page=render_study(SimpleNamespace(root=ROOT),{'doc':'public-claims','return':value}).decode()
        self.assertIn('card=fixture&amp;arm=ledger',page);self.assertIn('field=statement_c#input',page)
    def test_once_only_model_error_redacts_echo(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch,MagicMock
        from triage_bench import public_claim_trial as trial
        from triage_bench.app import profiles
        profile=profiles()['jev'];profile['api_key']='private-fixture-key'
        body=request(observation(),{f:'Claim.' for f in FIELDS},'ledger')
        planned=[{'id':'one','card_id':'card','arm':'ledger','round':1,'request_sha256':'fixture','body':body}]
        plan={k:profile[k] for k in ('model','endpoint','context_tokens')}
        raw={'model':'wrong','echo':profile['api_key']};response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps(raw).encode();opener=MagicMock();opener.open.return_value=response
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'hosted';protocol=Path(temp)/'protocol.json';protocol.write_text('{}')
            with patch.object(trial,'check',return_value=(plan,planned)),patch.object(trial,'OUTPUT',path),patch.object(trial,'PROTOCOL',protocol),patch('urllib.request.build_opener',return_value=opener):
                result=trial.run(profile);self.assertEqual(result['stopped_reason'],'checkpoint_mismatch');self.assertEqual(result['failed'],1)
                self.assertNotIn(profile['api_key'],(path/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):trial.run(profile)
                self.assertEqual(opener.open.call_count,1)
if __name__=='__main__':unittest.main()
