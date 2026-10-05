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
    def test_hidden_reference_fields_do_not_mutate_source(self):
        from triage_bench.public_claim_language_service import PublicClaimLanguageStudy
        packet={'id':'one','dataset':'Sample','observation':observation()};reference={'id':'one','answer':'supported'}
        outcome={'id':'one','round':1,'reference':'supported','correct':True,'false_displayed_support':False,'false_displayed_contradiction':False,'unknown_to_decisive':False,'correct_displayed_support':True}
        result={'datasets':{'Sample':{'forms':{'plain':{'outcomes':[outcome]}}}}}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);(path/'responses.jsonl').write_text(json.dumps({'card_id':'one'})+'\n')
            with patch.object(PublicClaimLanguageStudy,'verified',return_value=result),patch('triage_bench.public_claim_language_service.OUTPUT',path),patch('triage_bench.public_claim_language_service.load',side_effect=lambda p:[packet] if p.name=='inputs.json' else [reference]):
                study=PublicClaimLanguageStudy(path);hidden=study.card('one');self.assertIsNone(hidden['reference'])
                for key in ('reference','correct','false_displayed_support','false_displayed_contradiction','unknown_to_decisive','correct_displayed_support'):self.assertNotIn(key,hidden['outcomes']['plain'][0])
                self.assertEqual(study.card('one',True)['reference'],reference);self.assertIn('reference',outcome)
    def test_overview_preserves_counts_and_separate_choices(self):
        from triage_bench.public_claim_language_service import PublicClaimLanguageStudy
        packet={'id':'one','dataset':'Sample','selection':'measured_zero','observation':observation(),'statements':{'statement_a':'Claim.'},'form_fields':{'canonical':'statement_a'}}
        result={'datasets':{'Sample':{'propositions':1,'service_cards':1,'pairs':[],'stable_fixes':[],'stable_losses':[],'forms':{'plain':{'outcomes':[],'stable_correct_ids':[]}}}}}
        with patch.object(PublicClaimLanguageStudy,'verified',return_value=result),patch('triage_bench.public_claim_language_service.load',return_value=[packet]):
            panel=PublicClaimLanguageStudy('.').overview()['datasets']['Sample'];self.assertEqual(panel['propositions'],1);self.assertEqual(panel['service_cards'],1);self.assertEqual(panel['proposition_choices'][0]['id'],'one')
    def test_reader_return_preserves_selected_wording(self):
        from types import SimpleNamespace
        from triage_bench.study_page import return_path,render_study
        from triage_bench.paths import ROOT
        value='/claim-language?dataset=Train+Ticket&card=fixture&form=rephrased&round=2#input'
        self.assertEqual(return_path(value),value)
        page=render_study(SimpleNamespace(root=ROOT),{'doc':'public-claim-language','return':value}).decode()
        self.assertIn('card=fixture&amp;form=rephrased',page);self.assertIn('round=2#input',page)
if __name__=='__main__':unittest.main()
