import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from triage_bench import optional_clarification_features as f,optional_clarification_data as d,optional_clarification_trial as t,clarification_data as old_data
from triage_bench.clarification_focus_features import request as old_request
from triage_bench.clarification_features import FIELDS

class OptionalTests(unittest.TestCase):
    def row(self,choice,score=.95):return {'status':'ok','quarantined_sentences':[],'answers':{'suggestion':{'choice':choice,'probabilities':{choice:score}}}}
    def test_both_requests_keep_identical_allowlisted_state_and_unchanged_control(self):
        p=d.reconstruct()[0][0]
        self.assertEqual(f.request(p,'checklist'),old_request(p,'focused'))
        direct=f.request(p,'direct');self.assertEqual(direct['state'],f.request(p,'checklist')['state']);self.assertEqual(set(direct['questions']),{'suggestion'})
        self.assertEqual(direct,f.request({**p,'reference':'no_question','needed':['service'],'measurements':{'cpu':0},'family':'other'},'direct'))
        self.assertEqual(set(json.loads(direct['state'])),{'analyst_statement','observed_services','channel_aliases','available_comparison'})
    def test_new_text_and_references_freeze_all_scopes_and_priority(self):
        packets,refs=d.reconstruct();old=old_data.reconstruct()[0]
        self.assertEqual(len(packets),92);self.assertEqual(len({p['family'] for p in packets}),23);self.assertFalse({p['text'] for p in packets}&{p['text'] for p in old})
        for dataset in ('Train Ticket','Online Boutique'):
            rs=[ref for ref,p in zip(refs,packets) if p['dataset']==dataset]
            self.assertEqual({s:sum(r['scope']==s for r in rs) for s in ('complete_wording','needs_question','outside_task')},{'complete_wording':12,'needs_question':28,'outside_task':6})
        i=next(i for i,p in enumerate(packets) if p['family']=='subject_and_channel_missing');self.assertEqual(refs[i]['choice'],'service');self.assertEqual(refs[i]['needed'],['service','channel'])
    def test_no_suggestion_never_clears_fills_or_binds_a_claim(self):
        for c in f.CHOICES:
            r=f.decision(self.row(c),'direct');self.assertNotEqual(r['action'],'ready');self.assertNotIn('entry',r);self.assertNotIn('binding',r)
        r=f.decision(self.row('no_question'),'direct');self.assertEqual(r['action'],'no_suggestion');self.assertIn('Complete every required field',r['question'])
        labels={'scope':'metric_check',**{k:'clear' for k in FIELDS if k!='scope'}}
        row={'status':'ok','quarantined_sentences':[],'answers':{'claim_'+k:{'choice':v,'probabilities':{v:.95}} for k,v in labels.items()}}
        self.assertEqual(f.decision(row,'checklist')['action'],'no_suggestion');self.assertEqual(f.decision(row,'checklist')['labels'],labels)
    def test_silent_and_withheld_misses_remain_in_ambiguity_counts(self):
        ref={'choice':'service','needed':['service','channel']}
        r=f.assessment(f.decision(self.row('no_question'),'direct'),ref);self.assertTrue(r['silent_miss']);self.assertTrue(r['missed_clarification']);self.assertFalse(r['correct_display'])
        r=f.assessment(f.decision(self.row('service',.69),'direct'),ref);self.assertTrue(r['workflow_correct']);self.assertTrue(r['missed_clarification']);self.assertTrue(r['withheld_ambiguity']);self.assertFalse(r['silent_miss'])
        r=f.assessment(f.decision(self.row('service',.7),'direct'),ref);self.assertTrue(r['canonical_question']);self.assertFalse(r['missed_clarification'])
    def test_necessary_out_of_order_differs_from_unnecessary_and_wrong_scope(self):
        ref={'choice':'service','needed':['service','channel']}
        r=f.assessment(f.decision(self.row('channel'),'direct'),ref);self.assertTrue(r['necessary_question']);self.assertTrue(r['wrong_order_question']);self.assertFalse(r['unnecessary_question']);self.assertFalse(r['workflow_correct'])
        r=f.assessment(f.decision(self.row('window'),'direct'),ref);self.assertTrue(r['unnecessary_question']);self.assertTrue(r['missed_clarification'])
        r=f.assessment(f.decision(self.row('outside_scope'),'direct'),ref);self.assertTrue(r['wrong_scope'])
    def test_invalid_single_or_checklist_answer_quarantines_without_repair(self):
        row=self.row('service');row['quarantined_sentences']=['suggestion'];original=copy.deepcopy(row)
        self.assertFalse(f.decision(row,'direct')['valid']);self.assertFalse(f.decision(row,'direct')['displayed']);self.assertEqual(row,original)
        self.assertFalse(f.decision(None,'direct')['valid']);self.assertFalse(f.decision(self.row('invented'),'direct')['valid'])
    def test_pair_order_and_total_questions_match_frozen_budget(self):
        packets=d.reconstruct()[0]
        with patch.object(t,'check_plan',return_value={'maximum_calls':552,'maximum_answers':1932}),patch.object(d,'validate'),patch.object(t,'load',return_value=packets):jobs=t.requests()
        self.assertEqual(len(jobs),552);self.assertEqual(len({j['id'] for j in jobs}),552);self.assertEqual(sum(len(j['body']['questions']) for j in jobs),1932)
        for i in range(0,552,2):
            a,b=jobs[i:i+2];self.assertEqual((a['card_id'],a['round']),(b['card_id'],b['round']));self.assertEqual({a['arm'],b['arm']},{'direct','checklist'})
    def test_missing_calls_keep_every_arm_round_stratum_and_ambiguity(self):
        packets,refs=d.reconstruct()
        with patch.object(t,'verified_rows',return_value=([],{'attempted_calls':0,'status':'incomplete_or_failed'})),patch.object(t,'load',side_effect=[packets,refs]),patch.object(t,'sha',return_value='fixture'),patch.object(Path,'read_bytes',return_value=b''):
            r=t.score()
        self.assertFalse(r['candidate_passes']);self.assertEqual(len(r['outcomes']),828)
        ps=[p for p in r['panels'] if p['method']=='direct' and p['scope']=='overall'];self.assertEqual(sum(p['claims'] for p in ps),276);self.assertEqual(sum(p['missed_clarification'] for p in ps),168)
    def test_global_failure_stops_once_and_destination_cannot_rerun(self):
        import urllib.error
        jobs=[{'id':'fixture','card_id':'fixture','arm':'direct','phase':'development','round':1,'request_sha256':'fixture','body':{'model':t.MODEL}},{'id':'next','body':{'model':t.MODEL}}]
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-key'}
        with tempfile.TemporaryDirectory() as tmp,patch.object(t,'check',return_value=(profile,jobs)),patch.object(t,'output',return_value=Path(tmp)/'run'),patch.object(t,'protocol_path',return_value=Path(tmp)/'p.json'),patch('urllib.request.OpenerDirector.open',side_effect=urllib.error.HTTPError('fixture',403,'Forbidden',{},None)) as transport:
            (Path(tmp)/'p.json').write_text('{}');r=t.run('development',profile);self.assertEqual(r['attempted_calls'],1);self.assertEqual(r['unattempted_jobs'],1);self.assertEqual(transport.call_count,1)
            with self.assertRaises(FileExistsError):t.run('development',profile)

if __name__=='__main__':unittest.main()
