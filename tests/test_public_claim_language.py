import json,unittest,copy,tempfile
from pathlib import Path
from unittest.mock import patch,MagicMock
from triage_bench.public_claim_language_features import request,variants,FIELDS,FORMS
from triage_bench.public_claim_language_data import catalogue
from triage_bench.public_claim_language_trial import assess
from triage_bench.public_claim_features import request as old_request
from triage_bench.public_claim_reference import evaluate
from tests.test_public_claims import observation

class LanguageTests(unittest.TestCase):
    def test_ledger_and_instructions_unchanged(self):
        o=observation();texts=dict(zip(FIELDS,('Alpha.','Beta.','Gamma.')))
        self.assertEqual(request(o,texts),old_request(o,texts,'ledger'))
        state=json.loads(request(o,texts)['state'])
        for key in ('form_fields','proposition','selection','answer','source_card'):self.assertNotIn(key,state)
    def test_wordings_cover_both_polarities_without_health_negation(self):
        props=[{'kind':k,'asserted':v,**({'channel':'socket'} if k.startswith('metric') else {'measure':'duration_median_us'} if k.startswith('duration') else {})} for k in ('metric_material','metric_direction','duration_material','span_adequacy','health','causality') for v in (True,False)]
        for p in props:
            texts=variants(p);self.assertEqual(set(texts),set(FORMS));self.assertEqual(len(set(texts.values())),3)
            self.assertNotIn('supported',json.dumps(texts))
            if p['kind']=='health':self.assertNotIn('not unhealthy',json.dumps(texts))
        self.assertIn('not below',variants({'kind':'metric_material','channel':'socket','asserted':True})['rephrased'])
        self.assertIn('not at least',variants({'kind':'metric_material','channel':'socket','asserted':False})['rephrased'])
    def test_count_null_and_zero_retain_frozen_policy(self):
        o=observation();p={'kind':'span_adequacy','asserted':False}
        self.assertEqual(evaluate(o,p)['answer'],'unanswerable')
        o['trace']={'before':{'spans':0},'after':{'spans':0}}
        self.assertEqual(evaluate(o,p)['answer'],'supported')
        o['trace']['before']['spans']=5;o['trace']['after']['spans']=5
        self.assertEqual(evaluate(o,p)['answer'],'contradicted')
    def test_zero_catalogue_excludes_ineligible_zero(self):
        o=observation();o['metrics']['socket']['signed_change']=0
        source={'id':'fixture','observation':o};ref={'answers':{f:{'proposition':{'kind':'health','asserted':True}} for f in FIELDS}}
        self.assertEqual(len(catalogue(source,ref)),5)
        o['metrics']['socket']['after_missing_fraction']=.21
        self.assertEqual(len(catalogue(source,ref)),4)
        self.assertEqual(o['metrics']['socket']['signed_change'],0)
    def test_failed_denominators_remain_per_form(self):
        packet={'id':'fixture','dataset':'Sample','source_card':'source','case_id':'case','selection':'recorded_counts','form_fields':dict(zip(FORMS,FIELDS))}
        ref={'id':'fixture','answer':'unanswerable'};r=assess([], [packet],[ref])['Sample']
        self.assertFalse(r['research_gate'])
        for f in FORMS:self.assertEqual(r['forms'][f]['per_round'][0]['failed_or_missing'],1)
        self.assertFalse(any(p['fix'] or p['loss'] for p in r['pairs']))
    def test_wrong_contradictions_fail_even_without_false_support(self):
        packets=[{'id':v,'dataset':'Sample','source_card':'source','case_id':'case','selection':'original_claim','form_fields':dict(zip(FORMS,FIELDS))} for v in ('supported','contradicted','unanswerable')]
        refs=[{'id':p['id'],'answer':p['id']} for p in packets]
        rows=[{'card_id':p['id'],'round':n,'status':'ok','answers':{f:{'choice':p['id'],'probabilities':{p['id']:1.}} for f in FIELDS}} for p in packets for n in (1,2,3)]
        self.assertTrue(assess(rows,packets,refs)['Sample']['research_gate'])
        row=next(r for r in rows if r['card_id']=='supported' and r['round']==1)
        row['answers']['statement_c']={'choice':'contradicted','probabilities':{'contradicted':.9,'supported':.1}}
        r=assess(rows,packets,refs)['Sample'];self.assertFalse(r['form_gates']['rephrased'])
        self.assertEqual(r['forms']['rephrased']['per_round'][0]['false_displayed_contradiction'],1)
        self.assertEqual(r['forms']['rephrased']['per_round'][0]['false_displayed_support'],0)
    def test_once_only_wrong_model_stops_and_redacts(self):
        from triage_bench import public_claim_language_trial as trial
        from triage_bench.app import profiles
        profile=profiles()['jev'];profile['api_key']='private-language-fixture'
        body=request(observation(),{f:'Claim.' for f in FIELDS});planned=[{'id':'one','card_id':'card','arm':'ledger','round':1,'request_sha256':'fixture','body':body}]
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
