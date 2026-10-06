import copy
import unittest
from unittest.mock import patch
from triage_bench import full_workflow_trial as t

class FullWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packets,cls.records=t.check_reviews();cls.refs={r['id']:r for r in t.load(t.DATA/'references.json')}
    def fixture(self):
        assigned=[];initial=[];verdict=[]
        for n in (1,2,3):
            for p in self.packets:
                for arm in t.ARMS:
                    b=t.annotated(p,self.refs[p['id']]);assigned.append({'card_id':p['id'],'arm':arm,'round':n,'bindings':b})
                    answers={a['id']+'_verdict':{'choice':a['verdict'],'probabilities':{a['verdict']:1}} for a in self.refs[p['id']]['annotations'] if a['actionable']}
                    row={'card_id':p['id'],'arm':arm,'round':n,'status':'ok','answers':answers,'quarantined_sentences':[],'latency_ms':1,'usage':{'input_tokens':1}}
                    (initial if arm=='structured' else verdict).append(row)
                initial.append({'card_id':p['id'],'arm':'automatic','round':n,'status':'ok','answers':{},'quarantined_sentences':[],'latency_ms':1,'usage':{'input_tokens':1}})
        return assigned,initial,verdict
    def test_initial_inputs_keep_all_candidates_and_use_exact_frozen_controls(self):
        with patch.object(t,'check_plan',return_value={}):jobs=t.requests('initial')
        self.assertEqual(len(jobs),162);self.assertEqual(sum(len(j['body']['questions']) for j in jobs),6318)
        index={p['id']:(p,r) for p,r in zip(self.packets,self.records)}
        for j in jobs:
            p,r=index[j['card_id']]
            expected=t.extraction_request(p,'meaning') if j['arm']=='automatic' else t.structured_body(p,r,'clean_baseline')
            self.assertEqual(j['body'],expected)
            if j['arm']=='automatic':self.assertEqual(len(j['body']['questions']),72)
    def test_automatic_and_structured_phase_rows_do_not_overwrite_each_other(self):
        b,i,v=self.fixture();out=t.assess(self.packets,self.refs,b,i,v)
        self.assertTrue(out['candidate_passes']);i=[r for r in i if not(r['arm']=='automatic' and r['round']==1 and r['card_id']==self.packets[0]['id'])]
        out=t.assess(self.packets,self.refs,b,i,v);self.assertFalse(out['candidate_passes'])
        self.assertFalse(out['panels'][self.packets[0]['dataset']]['all']['arms']['automatic'][0]['complete'])
        self.assertTrue(out['panels'][self.packets[0]['dataset']]['all']['arms']['structured'][0]['complete'])
    def test_wrong_binding_fails_even_with_correct_numerical_verdict(self):
        b,i,v=self.fixture();item=next(x for x in b if x['arm']=='automatic');sid=next(k for k,d in item['bindings'].items() if d['accepted'])
        item['bindings'][sid]['service']=next(s for s in self.packets[0]['services'] if s!=item['bindings'][sid]['service'])
        out=t.assess(self.packets,self.refs,b,i,v);o=next(o for o in out['outcomes'] if o['note_id']==item['card_id'] and o['arm']=='automatic' and o['round']==item['round'] and o['sentence']==sid)
        self.assertTrue(o['verdict_correct']);self.assertTrue(o['unsafe_displayed']);self.assertFalse(o['end_correct']);self.assertFalse(out['candidate_passes'])
    def test_numerical_quarantine_withholds_only_that_sentence(self):
        b,i,v=self.fixture();row=v[0];sid=next(iter(row['answers'])).split('_')[0];row['quarantined_sentences']=[sid]
        out=t.assess(self.packets,self.refs,b,i,v)
        affected=[o for o in out['outcomes'] if o['note_id']==row['card_id'] and o['arm']==row['arm'] and o['round']==row['round']]
        self.assertEqual(sum(o['quarantined'] for o in affected),1);self.assertFalse(next(o for o in affected if o['sentence']==sid)['displayed'])
        self.assertEqual(len(out['outcomes']),2916)
    def test_dependent_requests_preserve_actual_bindings_and_explicit_skips(self):
        p=self.packets[0];b=t.parser(p);before=copy.deepcopy(b)
        t.verdict_request(p,b);self.assertEqual(b,before)
        for d in b.values():d['accepted']=False
        self.assertIsNone(t.verdict_request(p,b))
    def test_global_transport_failure_stops_and_rerun_is_rejected(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import Mock
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-key'}
        plan={k:v for k,v in profile.items() if k!='api_key'}
        jobs=[{'id':str(i),'card_id':'n','arm':'automatic','phase':'initial','round':1,'body':{'model':t.MODEL,'state':'{}','questions':{}},'request_sha256':str(i)} for i in range(2)]
        opener=Mock();opener.open.side_effect=OSError('fixture failure')
        with tempfile.TemporaryDirectory() as f:
            dest=Path(f)/'out';protocol=Path(f)/'protocol';protocol.write_text('{}')
            with patch.object(t,'output',return_value=dest),patch.object(t,'protocol_path',return_value=protocol),patch.object(t,'check',return_value=(plan,jobs)),patch('triage_bench.full_workflow_trial.urllib.request.build_opener',return_value=opener):
                r=t.run('initial',profile);self.assertEqual(r['attempted_calls'],1);self.assertEqual(opener.open.call_count,1)
                self.assertNotIn(profile['api_key'],(dest/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):t.run('initial',profile)

class FullWorkflowConsumerTests(unittest.TestCase):
    def test_actual_bindings_are_not_repaired_and_references_are_hidden(self):
        from triage_bench.full_workflow_service import FullWorkflowStudy
        from triage_bench.paths import ROOT
        study=FullWorkflowStudy(ROOT)
        with patch.object(study,'verified',return_value=t.load(t.RESULT)):
            hidden=study.card('NWL-fe6c9911a37a');shown=study.card('NWL-fe6c9911a37a',True)
            b=next(b['bindings']['s03'] for b in hidden['bindings'] if b['arm']=='automatic' and b['round']==1)
            self.assertEqual(b['polarity'],'negative');self.assertTrue(b['accepted'])
            self.assertEqual(next(a['polarity'] for a in shown['reference']['annotations'] if a['id']=='s03'),'positive')
            self.assertIsNone(hidden['reference']);self.assertIsNone(hidden['outcomes'])
            self.assertEqual(len(hidden['candidates']),12);self.assertNotIn('outcomes',study.overview())
    def test_reader_keeps_workflow_and_sentence(self):
        from types import SimpleNamespace
        from triage_bench.study_page import render_study
        from triage_bench.paths import ROOT
        html=render_study(SimpleNamespace(root=ROOT),{'doc':'full-workflow','return':'/full-workflow?arm=parser&sentence=s10#inspect'}).decode()
        self.assertIn('Compare the complete note workflow',html);self.assertIn('arm=parser',html);self.assertIn('sentence=s10',html)
