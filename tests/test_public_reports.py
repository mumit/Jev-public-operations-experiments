import copy,json,unittest,tempfile
from pathlib import Path
from unittest.mock import patch,MagicMock
from triage_bench.public_report_features import request,text,FIELDS
from triage_bench.public_report_trial import assess
from triage_bench.public_report_data import compose
from tests.test_public_claims import observation

class ReportTests(unittest.TestCase):
    def fixture(self):
        a=observation();a['service']='alpha';b=copy.deepcopy(a);b['service']='beta';b['metrics']['socket']['signed_change']=0
        statements={f:text(a if i%2==0 else b,{'kind':'metric_direction','channel':'socket','asserted':True}) for i,f in enumerate(FIELDS)}
        return a,b,statements
    def test_paired_states_differ_only_by_report(self):
        a,b,s=self.fixture();atomic=request([a,b],s,'atomic');report=request([a,b],s,'report');state=json.loads(report['state']);note=state.pop('report')
        self.assertEqual(state,json.loads(atomic['state']));self.assertEqual(note.count('\n'),6)
        for i,f in enumerate(FIELDS,1):
            self.assertIn(f'{i}. {s[f]}',note);self.assertIn(s[f],atomic['questions'][f]['instructions']);self.assertIn(f'sentence {i}',report['questions'][f]['instructions'])
            self.assertEqual(atomic['questions'][f]['criteria'],report['questions'][f]['criteria'])
        self.assertNotIn('reference',state);self.assertNotIn('source_card',state)
    def test_distinct_service_guard_and_source_preservation(self):
        a,b,s=self.fixture();before=copy.deepcopy([a,b]);request([a,b],s,'report');self.assertEqual([a,b],before)
        with self.assertRaises(ValueError):request([a,a],s,'report')
        with self.assertRaises(ValueError):request([a,b],s,'other')
    def test_names_replace_this_service_without_causal_proof(self):
        a,b,s=self.fixture()
        for kind in ('health','causality'):
            sentence=text(a,{'kind':kind,'asserted':True});self.assertIn('alpha',sentence);self.assertNotIn('this service',sentence.lower())
    def test_selection_uses_catalogue_not_reference_balance(self):
        a,b,s=self.fixture();sources=[{'id':n,'case_id':'same','dataset':'Sample','observation':o} for n,o in [('a',a),('b',b)]]
        refs={n:{'answers':{f:{'proposition':{'kind':'health','asserted':True}} for f in ('statement_a','statement_b','statement_c')}} for n in ('a','b')}
        first=compose(sources,refs);self.assertEqual(first,compose(list(reversed(sources)),refs));self.assertEqual(len(first[0][0]['statements']),6)
        self.assertEqual({v['service'] for v in first[1][0]['answers'].values()},{'alpha','beta'})
    def panel(self):
        p={'id':'p','dataset':'Sample','claim_sources':{f:{'service':'alpha' if i<3 else 'beta'} for i,f in enumerate(FIELDS)}}
        ref={'id':'p','answers':{f:{'answer':('supported','contradicted','unanswerable')[i%3]} for i,f in enumerate(FIELDS)}}
        rows=[{'card_id':'p','arm':arm,'round':n,'status':'ok','answers':{f:{'choice':ref['answers'][f]['answer'],'probabilities':{ref['answers'][f]['answer']:1}} for f in FIELDS}} for arm in ('atomic','report') for n in (1,2,3)]
        return p,ref,rows
    def test_one_wrong_claim_fails_whole_report(self):
        p,ref,rows=self.panel();self.assertTrue(assess(rows,[p],[ref])['Sample']['research_gate'])
        rows[3]['answers'][FIELDS[0]]={'choice':'contradicted','probabilities':{'contradicted':1}}
        r=assess(rows,[p],[ref])['Sample'];self.assertFalse(r['research_gate']);v=r['arms']['report']['per_round'][0]
        self.assertEqual(v['correct'],5);self.assertEqual(v['all_six_correct'],0);self.assertEqual(v['wrong_displayed'],1)
    def test_missing_keeps_all_denominators_and_no_false_pair_fix(self):
        p,ref,rows=self.panel();r=assess(rows[3:],[p],[ref])['Sample'];self.assertFalse(r['research_gate']);self.assertEqual(r['arms']['atomic']['per_round'][0]['failed_or_missing'],6);self.assertFalse(any(o['fix'] for o in r['pairs']))
    def test_whole_display_requires_every_claim(self):
        p,ref,rows=self.panel();rows[3]['answers'][FIELDS[0]]['probabilities']['supported']=.69
        v=assess(rows,[p],[ref])['Sample']['arms']['report']['per_round'][0];self.assertEqual(v['all_six_correct'],1);self.assertEqual(v['complete_display'],0);self.assertEqual(v['correct_displayed_support'],1)
    def test_once_only_model_stop_redacts(self):
        from triage_bench import public_report_trial as trial
        from triage_bench.app import profiles
        a,b,s=self.fixture();body=request([a,b],s,'report');profile=profiles()['jev'];profile['api_key']='private-report-fixture';plan={k:profile[k] for k in ('model','endpoint','context_tokens')};planned=[{'id':'one','card_id':'p','arm':'report','round':1,'request_sha256':'fixture','body':body}]
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps({'model':'wrong','echo':profile['api_key']}).encode();opener=MagicMock();opener.open.return_value=response
        with tempfile.TemporaryDirectory() as t:
            path=Path(t);protocol=path/'p.json';protocol.write_text('{}');out=path/'hosted'
            with patch.object(trial,'check',return_value=(plan,planned)),patch.object(trial,'OUTPUT',out),patch.object(trial,'PROTOCOL',protocol),patch('urllib.request.build_opener',return_value=opener):
                result=trial.run(profile);self.assertEqual(result['stopped_reason'],'checkpoint_mismatch');self.assertNotIn(profile['api_key'],(out/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):trial.run(profile)
                self.assertEqual(opener.open.call_count,1)
if __name__=='__main__':unittest.main()

class ReportReaderTests(unittest.TestCase):
    def test_reference_reveal_is_separate(self):
        from triage_bench.public_report_service import PublicReportStudy
        packet={'id':'p','dataset':'Sample'};reference={'id':'p','answers':{}};outcome={'id':'p','field':'statement_a','reference':'supported','correct':True,'unknown_to_decisive':False}
        result={'datasets':{'Sample':{'arms':{'report':{'outcomes':[outcome]}}}}}
        with tempfile.TemporaryDirectory() as t:
            path=Path(t);(path/'responses.jsonl').write_text('{"card_id":"p"}\n')
            with patch.object(PublicReportStudy,'verified',return_value=result),patch('triage_bench.public_report_service.OUTPUT',path),patch('triage_bench.public_report_service.load',side_effect=lambda p:[packet] if p.name=='inputs.json' else [reference]):
                study=PublicReportStudy(path);hidden=study.card('p');self.assertIsNone(hidden['reference']);self.assertNotIn('correct',hidden['outcomes']['report'][0]);self.assertNotIn('reference',hidden['outcomes']['report'][0]);self.assertEqual(study.card('p',True)['reference'],reference);self.assertIn('correct',outcome)
    def test_article_preserves_report_claim_arm_and_round(self):
        from types import SimpleNamespace
        from triage_bench.study_page import return_path,render_study
        from triage_bench.paths import ROOT
        value='/report-reading?dataset=Train+Ticket&card=fixture&field=statement_f&arm=report&round=2#inspect'
        self.assertEqual(return_path(value),value);page=render_study(SimpleNamespace(root=ROOT),{'doc':'public-reports','return':value}).decode();self.assertIn('field=statement_f&amp;arm=report',page);self.assertIn('round=2#inspect',page)
