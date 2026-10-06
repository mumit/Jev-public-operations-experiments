import copy
import unittest
from unittest.mock import patch
from triage_bench import direct_subject_trial as t
from triage_bench import separate_subject_trial as old
from tests import test_subject_check as old_tests

class DirectSubjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packets,cls.records=t.check_reviews()
    answer=staticmethod(old_tests.SubjectCheckTests.answer)
    def fixture(self):
        refs={p['id']:{sid:{'verdict':'supported','service':d['values']['service'],'subject_form':'pronoun'} for sid,d in r['export']['reviews'].items() if d['decision']=='confirm'} for p,r in zip(self.packets,self.records)}
        rows=[]
        for p,r in zip(self.packets,self.records):
            for arm in t.CALL_ARMS:
                for n in (1,2,3):
                    answers={}
                    for sid,ref in refs[p['id']].items():
                        if arm=='direct_subject':
                            service=ref['service'];options=p['services']+['unresolved'];answers[sid+'_subject']={'choice':service,'probabilities':{s:1.0 if s==service else 0.0 for s in options}}
                        elif arm.endswith('checked'):answers[sid+'_subject']=self.answer('conflict' if arm.startswith('wrong') else 'matched')
                        else:answers[sid+'_verdict']=self.answer('contradicted' if arm=='wrong_baseline' else 'supported')
                    rows.append({'id':p['id']+'::'+arm+'::'+str(n),'card_id':p['id'],'arm':arm,'round':n,'status':'ok','latency_ms':1,'usage':{'input_tokens':10},'answers':answers})
        return refs,rows

    def test_exact_controls_and_no_mutation(self):
        for p,r in zip(self.packets,self.records):
            snap=copy.deepcopy((p,r))
            for arm in t.CALL_ARMS[1:]:self.assertEqual(t.body(p,r,arm),old.body(p,r,arm))
            t.body(p,r,'direct_subject');self.assertEqual((p,r),snap)

    def test_direct_uses_complete_observed_inventory_without_binding_or_measurements(self):
        for p,r in zip(self.packets,self.records):
            b=t.body(p,r,'direct_subject');state=t.json.loads(b['state'])
            self.assertEqual(state,{'note':p['note'],'observed_services':p['services']});self.assertEqual(len(b['questions']),6)
            for sid,q in b['questions'].items():
                self.assertEqual(list(q['criteria']),p['services']+['unresolved']);self.assertNotIn('Proposed service:',q['instructions'])
                c=next(c for c in p['candidates'] if c['id']==sid.split('_')[0]);self.assertTrue(q['instructions'].endswith(c['text']))
            changed=copy.deepcopy(r)
            for d in changed['export']['reviews'].values():
                if d['decision']=='confirm':d['values']['service']='untrusted-alternate'
            self.assertEqual(t.body(p,changed,'direct_subject'),b)

    def test_one_direct_reply_composes_both_proposals_without_rebinding(self):
        _,rows=self.fixture();index={(r['card_id'],r['arm'],r['round']):r for r in rows};p=self.packets[0];r=self.records[0];snap=copy.deepcopy(index)
        clean=t.composed_row(index,p['id'],'clean_direct',1,r);wrong=t.composed_row(index,p['id'],'wrong_direct',1,r)
        self.assertEqual(clean['source_call_ids'][0],wrong['source_call_ids'][0]);self.assertNotEqual(clean['source_call_ids'][1],wrong['source_call_ids'][1])
        self.assertTrue(t.decision(clean,'s03',True)['displayed']);self.assertFalse(t.decision(wrong,'s03',True)['displayed'])
        self.assertEqual(t.decision(wrong,'s03',True)['subject'],'conflict');self.assertEqual(wrong['answers']['s03_verdict']['choice'],'contradicted');self.assertEqual(index,snap)

    def test_unresolved_and_low_probability_never_display(self):
        _,rows=self.fixture();index={(r['card_id'],r['arm'],r['round']):r for r in rows};p=self.packets[0];r=self.records[0]
        for choice,prob in (('unresolved',1.0),(r['export']['reviews']['s03']['values']['service'],.69)):
            index[(p['id'],'direct_subject',1)]['answers']['s03_subject']={'choice':choice,'probabilities':{choice:prob}}
            d=t.decision(t.composed_row(index,p['id'],'clean_direct',1,r),'s03',True);self.assertFalse(d['displayed'])

    def test_quarantine_either_call_preserves_valid_siblings_and_missing_call_denominator(self):
        for arm in ('direct_subject','clean_baseline'):
            refs,rows=self.fixture();p=self.packets[0];record=self.records[0];index={(r['card_id'],r['arm'],r['round']):r for r in rows}
            source=index[(p['id'],arm,1)];source['quarantined_sentences']=['s03'];source['status']='ok_with_review'
            combined=t.composed_row(index,p['id'],'clean_direct',1,record)
            self.assertFalse(t.decision(combined,'s03',True)['displayed']);self.assertTrue(t.decision(combined,'s04',True)['displayed'])
            rows=[r for r in rows if r is not source];result=t.assess(self.packets,refs,rows);m=result['panels']['Train Ticket']['all']['arms']['clean_direct'][0]['strata']['all']
            self.assertEqual(m['denominator'],54);self.assertEqual(m['correct_safe_displayed'],48);self.assertFalse(m['complete']);self.assertFalse(result['candidate_passes'])

    def test_unique_accuracy_and_costs_count_shared_replies_once(self):
        refs,rows=self.fixture();result=t.assess(self.packets,refs,rows)
        self.assertTrue(result['candidate_passes']);self.assertEqual(sum(c['calls'] for c in result['costs'].values()),405)
        self.assertEqual(result['workflow_costs']['clean_direct']['calls'],162)
        self.assertEqual(sum(p['denominator'] for p in result['unique_direct_subject'] if p['wording']=='all'),486)
        self.assertTrue(all(p['gains']==p['losses']==0 for p in result['paired_clean_displays']))

    def test_wrong_extracted_service_is_unsafe_even_with_correct_verdict(self):
        refs,rows=self.fixture()
        for row in rows:
            if row['arm']=='direct_subject':
                record=next(r for r in self.records if r['note_id']==row['card_id']);wrong=t.decisions(record,'wrong_direct')
                for sid,d in wrong.items():
                    if d['decision']=='confirm':row['answers'][sid+'_subject']={'choice':d['values']['service'],'probabilities':{d['values']['service']:1.0}}
            if row['arm']=='wrong_baseline':row['answers']={k:self.answer('supported') for k in row['answers']}
        result=t.assess(self.packets,refs,rows);m=result['panels']['Train Ticket']['all']['arms']['wrong_direct'][0]['strata']['all']
        self.assertEqual(m['unsafe_displayed'],54);self.assertEqual(m['wrong_verdict_displayed'],0);self.assertFalse(result['candidate_passes'])

    def test_budget_and_all_verdicts_are_fixed_before_subject_answers(self):
        with patch.object(t,'check_plan',return_value={}):jobs=t.requests()
        self.assertEqual(len(jobs),405);self.assertEqual(sum(len(j['body']['questions']) for j in jobs),2430)
        self.assertEqual({j['phase'] for j in jobs[:243]},{'text'});self.assertEqual({j['phase'] for j in jobs[243:]},{'verdict'})
        self.assertEqual(sum(j['arm']=='direct_subject' for j in jobs),81)

    def test_global_failure_stops_and_rerun_is_rejected(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import Mock
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'test-placeholder-key'}
        plan={k:v for k,v in profile.items() if k!='api_key'}
        jobs=[{'id':'first','card_id':'n','arm':'direct_subject','phase':'text','round':1,'body':{'model':t.MODEL,'state':'{}','questions':{}},'request_sha256':'a'},
              {'id':'later','card_id':'n','arm':'clean_baseline','phase':'verdict','round':1,'body':{'model':t.MODEL,'state':'{}','questions':{}},'request_sha256':'b'}]
        opener=Mock();opener.open.side_effect=OSError('test transport failure')
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'run';protocol=Path(folder)/'protocol';protocol.write_text('{}')
            with patch.object(t,'OUT',out),patch.object(t,'PROTOCOL',protocol),patch.object(t,'check',return_value=(plan,jobs)),patch('triage_bench.direct_subject_trial.urllib.request.build_opener',return_value=opener):
                result=t.run(profile);self.assertEqual(result['attempted_calls'],1);self.assertEqual(opener.open.call_count,1)
                self.assertNotIn(profile['api_key'],(out/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):t.run(profile)
