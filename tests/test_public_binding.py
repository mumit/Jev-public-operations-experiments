import copy,json,unittest,tempfile
from pathlib import Path
from unittest.mock import patch,MagicMock
from triage_bench.public_report_features import request as previous,FIELDS
from triage_bench.public_binding_features import request,ARMS
from triage_bench.public_binding_trial import assess
from tests.test_public_claims import observation

class BindingTests(unittest.TestCase):
    def packet(self):
        a=observation();a['service']='alpha';b=copy.deepcopy(a);b['service']='beta';b['metrics']['socket']['signed_change']=0
        claims={f:f'For service {"alpha" if i%2==0 else "beta"}: The eligible signed change for socket is greater than zero.' for i,f in enumerate(FIELDS)}
        return {'id':'p','dataset':'Sample','observations':[a,b],'statements':claims,'claim_sources':{f:{'service':'alpha' if i%2==0 else 'beta'} for i,f in enumerate(FIELDS)},'requests':{'report':previous([a,b],claims,'report')}}
    def test_lookup_exact_historical_body(self):
        p=self.packet();self.assertEqual(request(p,'lookup'),p['requests']['report'])
    def test_binding_changes_only_instruction_suffix(self):
        p=self.packet();old=request(p,'lookup');new=request(p,'bound');self.assertEqual(old['state'],new['state']);self.assertEqual(old['model'],new['model'])
        for i,f in enumerate(FIELDS,1):
            a=old['questions'][f];b=new['questions'][f];self.assertEqual(a['criteria'],b['criteria']);self.assertEqual(a['instructions'].split('Assess only sentence ')[0],b['instructions'].split('Claim ID ')[0]);self.assertIn('C'+str(i),b['instructions']);self.assertIn(p['statements'][f],b['instructions'])
    def test_single_removes_only_other_questions(self):
        p=self.packet();b=request(p,'bound');s=request(p,'single',FIELDS[2]);self.assertEqual(s['state'],b['state']);self.assertEqual(s['questions'],{FIELDS[2]:b['questions'][FIELDS[2]]})
    def test_scoping_removes_only_other_service_facts(self):
        p=self.packet();s=request(p,'single',FIELDS[1]);f=request(p,'scoped',FIELDS[1]);a=json.loads(s['state']);b=json.loads(f['state']);self.assertEqual(a['report'],b['report']);self.assertEqual(s['questions'],f['questions']);self.assertEqual(b['services'],[a['services'][1]]);self.assertEqual(b['services'][0]['service'],'beta');self.assertIn('alpha',b['report'])
    def test_invalid_selection_and_missing_binding_reject(self):
        p=self.packet();before=copy.deepcopy(p)
        for arm,f in [('scoped',None),('bound',FIELDS[0]),('single','absent'),('other',None)]:
            with self.assertRaises(ValueError):request(p,arm,f)
        request(p,'scoped',FIELDS[0]);self.assertEqual(p,before)
        p['claim_sources'][FIELDS[0]]['service']='absent'
        with self.assertRaises(ValueError):request(p,'scoped',FIELDS[0])
    def panel(self):
        p=self.packet();refs={'id':'p','answers':{f:{'answer':('supported','contradicted','unanswerable')[i%3]} for i,f in enumerate(FIELDS)}};rows=[]
        for arm in ARMS:
            for n in (1,2,3):
                for field in ((None,) if arm in ('lookup','bound') else FIELDS):
                    fields=FIELDS if field is None else (field,)
                    rows.append({'card_id':'p','arm':arm,'field':field,'round':n,'status':'ok','answers':{f:{'choice':refs['answers'][f]['answer'],'probabilities':{refs['answers'][f]['answer']:1.}} for f in fields}})
        return p,refs,rows
    def test_scoring_keeps_grouping_and_all_six_denominators(self):
        p,ref,rows=self.panel();r=assess(rows,[p],[ref])['Sample'];self.assertTrue(r['research_gate'])
        for arm in ARMS:
            v=r['arms'][arm]['per_round'][0];self.assertEqual(v['claims'],6);self.assertEqual(v['all_six_correct'],1);self.assertEqual(v['complete_correct_display'],1)
        self.assertTrue(r['steps']['lookup__bound']['no_error_opportunity']);self.assertEqual(r['steps']['lookup__bound']['stable_fixes'],[])
    def test_wrong_scoped_answer_fails_only_scoping_step(self):
        p,ref,rows=self.panel();row=next(r for r in rows if r['arm']=='scoped' and r['round']==1 and r['field']==FIELDS[0]);row['answers'][FIELDS[0]]={'choice':'contradicted','probabilities':{'contradicted':1}}
        r=assess(rows,[p],[ref])['Sample'];self.assertFalse(r['step_gates']['scoped']);self.assertTrue(r['step_gates']['single']);self.assertEqual(r['arms']['scoped']['per_round'][0]['all_six_correct'],0);self.assertEqual(r['arms']['scoped']['per_round'][0]['wrong_displayed'],1)
    def test_missing_single_request_cannot_be_an_improvement(self):
        p,ref,rows=self.panel();rows=[r for r in rows if not(r['arm']=='single' and r['round']==1 and r['field']==FIELDS[0])];r=assess(rows,[p],[ref])['Sample'];self.assertFalse(r['step_gates']['scoped']);self.assertEqual(r['arms']['single']['per_round'][0]['failed_or_missing'],1);self.assertFalse(any(o['fix'] for o in r['pairs']))
    def test_actual_question_count_controls_provider_validation(self):
        from triage_bench.public_binding_trial import answers
        from triage_bench.profile import MODEL
        p=self.packet();body=request(p,'single',FIELDS[0]);raw={'model':MODEL,'answers':{FIELDS[0]:{'choice':'supported','probabilities':{'supported':1,'contradicted':0,'unanswerable':0}}}}
        # Reuse the actual provider structure from the established normalizer contract.
        with patch('triage_bench.public_binding_trial.normalize',return_value=('supported',{'supported':1},None)):
            self.assertEqual(set(answers(raw,body)),{FIELDS[0]});raw['answers'][FIELDS[1]]=raw['answers'][FIELDS[0]]
            with self.assertRaises(ValueError):answers(raw,body)
    def test_once_only_model_stop_redacts(self):
        from triage_bench import public_binding_trial as trial
        from triage_bench.app import profiles
        body=request(self.packet(),'single',FIELDS[0]);profile=profiles()['jev'];profile['api_key']='private-binding-fixture';plan={k:profile[k] for k in ('model','endpoint','context_tokens')};planned=[{'id':'one','card_id':'p','arm':'single','field':FIELDS[0],'round':1,'request_sha256':'fixture','body':body}]
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps({'model':'wrong','echo':profile['api_key']}).encode();opener=MagicMock();opener.open.return_value=response
        with tempfile.TemporaryDirectory() as t:
            path=Path(t);protocol=path/'p.json';protocol.write_text('{}');out=path/'hosted'
            with patch.object(trial,'check',return_value=(plan,planned)),patch.object(trial,'OUTPUT',out),patch.object(trial,'PROTOCOL',protocol),patch('urllib.request.build_opener',return_value=opener):
                result=trial.run(profile);self.assertEqual(result['stopped_reason'],'checkpoint_mismatch');self.assertNotIn(profile['api_key'],(out/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):trial.run(profile)
                self.assertEqual(opener.open.call_count,1)

class BindingReaderTests(unittest.TestCase):
    def test_hidden_historical_reference_does_not_mutate(self):
        from triage_bench.public_binding_service import PublicBindingStudy
        packet={'id':'p','dataset':'Sample'};reference={'id':'p','answers':{}};outcome={'id':'p','field':'statement_a','reference':'supported','correct':True,'unknown_to_decisive':False}
        result={'datasets':{'Sample':{'arms':{'lookup':{'outcomes':[outcome]}}}}};historical={'datasets':{'Sample':{'arms':{'report':{'outcomes':[outcome]}}}}}
        with tempfile.TemporaryDirectory() as t:
            path=Path(t);(path/'responses.jsonl').write_text('{"card_id":"p","arm":"report","field":null}\n')
            def fixture(p):
                if p.name=='inputs.json':return [packet]
                if p.name=='references.json':return [reference]
                return historical
            with patch.object(PublicBindingStudy,'verified',return_value=result),patch('triage_bench.public_binding_service.OUTPUT',path),patch('triage_bench.public_binding_service.HISTORICAL_OUTPUT',path),patch('triage_bench.public_binding_service.load',side_effect=fixture):
                study=PublicBindingStudy(path);hidden=study.card('p');self.assertIsNone(hidden['reference']);self.assertNotIn('correct',hidden['outcomes']['lookup'][0]);self.assertNotIn('reference',hidden['historical_outcomes'][0]);self.assertEqual(study.card('p',True)['reference'],reference);self.assertIn('correct',outcome)
    def test_article_preserves_binding_context(self):
        from types import SimpleNamespace
        from triage_bench.study_page import return_path,render_study
        from triage_bench.paths import ROOT
        value='/claim-binding?dataset=Train+Ticket&card=fixture&field=statement_c&arm=scoped&round=2#input'
        self.assertEqual(return_path(value),value);page=render_study(SimpleNamespace(root=ROOT),{'doc':'public-binding','return':value}).decode();self.assertIn('field=statement_c&amp;arm=scoped',page);self.assertIn('round=2#input',page)
