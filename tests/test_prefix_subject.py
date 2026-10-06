import copy
import unittest
from unittest.mock import patch
from triage_bench import prefix_subject_trial as t
from triage_bench import direct_subject_trial as old
from tests import test_direct_subject as old_tests

class PrefixSubjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packets,cls.records=t.check_reviews()
    answer=staticmethod(old_tests.DirectSubjectTests.answer)
    def fixture(self):
        refs,previous=old_tests.DirectSubjectTests.fixture(self);rows=[]
        for r in previous:
            if r['arm'].endswith('baseline'):
                rows.append({**r,'sentence':None})
            elif r['arm']=='direct_subject':
                for field,a in r['answers'].items():
                    sid=field.split('_')[0]
                    for arm in ('full_subject','prefix_subject'):
                        rows.append({**r,'id':r['id']+'::'+arm+'::'+sid,'arm':arm,'sentence':sid,'answers':{field:copy.deepcopy(a)}})
        return refs,rows

    def test_paired_requests_differ_only_in_literal_note_suffix(self):
        for p,r in zip(self.packets,self.records):
            snapshot=copy.deepcopy((p,r));prior=old.body(p,r,'direct_subject')
            for field,q in prior['questions'].items():
                sid=field.split('_')[0];full=t.body(p,r,'full_subject',sid);prefix=t.body(p,r,'prefix_subject',sid)
                self.assertEqual(full['questions'],{field:q});self.assertEqual(prefix['questions'],full['questions'])
                self.assertEqual(full['model'],prefix['model']);a=t.json.loads(full['state']);b=t.json.loads(prefix['state'])
                self.assertEqual(a['observed_services'],p['services']);self.assertEqual(b['observed_services'],a['observed_services'])
                self.assertEqual(a['note'],p['note']);self.assertTrue(a['note'].startswith(b['note']))
                i=next(i for i,c in enumerate(p['candidates']) if c['id']==sid)
                self.assertEqual(b['note'],'\n'.join(c['text'] for c in p['candidates'][:i+1]));self.assertNotIn('Proposed service:',q['instructions'])
            self.assertEqual((p,r),snapshot)

    def test_literal_prefix_preserves_line_endings_and_rejects_bad_boundaries(self):
        p=copy.deepcopy(self.packets[0]);p['note']=p['note'].replace('\n','\r\n')
        self.assertEqual(t.note_prefix(p,'s03'),'\r\n'.join(c['text'] for c in p['candidates'][:3]))
        p['candidates'][0]['text']='altered header'
        with self.assertRaises(ValueError):t.note_prefix(p,'s03')
        with self.assertRaises(ValueError):t.note_prefix(self.packets[0],'missing')

    def test_verdict_batches_are_exact_and_subject_calls_ignore_reviewed_names(self):
        for p,r in zip(self.packets,self.records):
            for arm in ('clean_baseline','wrong_baseline'):self.assertEqual(t.body(p,r,arm),old.body(p,r,arm))
            changed=copy.deepcopy(r)
            for d in changed['export']['reviews'].values():
                if d['decision']=='confirm':d['values']['service']='untrusted-substitute'
            sid=next(c['id'] for c in p['candidates'] if r['export']['reviews'][c['id']]['decision']=='confirm')
            self.assertEqual(t.body(p,changed,'prefix_subject',sid),t.body(p,r,'prefix_subject',sid))
            with self.assertRaises(ValueError):t.body(p,r,'prefix_subject','s01')

    def test_one_claim_reply_serves_both_proposals_without_rebinding(self):
        _,rows=self.fixture();index={(r['card_id'],r['arm'],r['round'],r['sentence']):r for r in rows};p=self.packets[0];r=self.records[0];snapshot=copy.deepcopy(index)
        clean=t.composed_row(index,p['id'],'clean_prefix',1,r,'s03');wrong=t.composed_row(index,p['id'],'wrong_prefix',1,r,'s03')
        self.assertEqual(clean['source_call_ids'][0],wrong['source_call_ids'][0]);self.assertNotEqual(clean['source_call_ids'][1],wrong['source_call_ids'][1])
        self.assertTrue(t.decision(clean,'s03',True)['displayed']);self.assertFalse(t.decision(wrong,'s03',True)['displayed'])
        self.assertEqual(wrong['answers']['s03_verdict']['choice'],'contradicted');self.assertEqual(index,snapshot)

    def test_quarantines_from_either_call_block_only_their_sentence(self):
        for arm,sid in (('prefix_subject','s03'),('clean_baseline',None)):
            _,rows=self.fixture();index={(r['card_id'],r['arm'],r['round'],r['sentence']):r for r in rows};p=self.packets[0];r=self.records[0]
            source=index[(p['id'],arm,1,sid)];source['status']='ok_with_review';source['quarantined_sentences']=['s03']
            self.assertFalse(t.decision(t.composed_row(index,p['id'],'clean_prefix',1,r,'s03'),'s03',True)['displayed'])
            self.assertTrue(t.decision(t.composed_row(index,p['id'],'clean_prefix',1,r,'s04'),'s04',True)['displayed'])

    def test_missing_one_subject_preserves_full_denominator_and_other_claims(self):
        refs,rows=self.fixture();rows=[r for r in rows if not(r['card_id']==self.packets[0]['id'] and r['arm']=='prefix_subject' and r['round']==1 and r['sentence']=='s03')]
        result=t.assess(self.packets,refs,rows);m=result['panels']['Train Ticket']['all']['arms']['clean_prefix'][0]['strata']['all']
        self.assertEqual(m['denominator'],54);self.assertEqual(m['correct_safe_displayed'],53);self.assertFalse(m['complete']);self.assertFalse(result['candidate_passes'])

    def test_unique_accuracy_costs_and_paired_losses_use_actual_claim_calls(self):
        refs,rows=self.fixture();result=t.assess(self.packets,refs,rows)
        self.assertTrue(result['candidate_passes']);self.assertEqual(sum(c['calls'] for c in result['costs'].values()),1134)
        self.assertEqual(result['workflow_costs']['clean_prefix']['calls'],567)
        self.assertEqual(sum(p['denominator'] for p in result['unique_subject'] if p['wording']=='all' and p['approach']=='prefix'),486)
        self.assertTrue(all(p['gains']==p['losses']==0 for p in result['paired_clean_displays']))
        p=self.packets[0];row=next(r for r in rows if r['card_id']==p['id'] and r['arm']=='prefix_subject' and r['round']==1 and r['sentence']=='s03')
        service=row['answers']['s03_subject']['choice'];row['answers']['s03_subject']['probabilities'][service]=.69
        result=t.assess(self.packets,refs,rows);paired=next(p for p in result['paired_clean_displays'] if p['dataset']=='Train Ticket' and p['wording']=='all' and p['round']==1)
        self.assertEqual(paired['losses'],1);self.assertFalse(result['candidate_passes'])

    def test_wrong_service_display_is_unsafe_even_when_verdict_coincides(self):
        refs,rows=self.fixture()
        for row in rows:
            if row['arm']=='prefix_subject':
                r=next(r for r in self.records if r['note_id']==row['card_id']);sid=row['sentence'];service=t.decisions(r,'wrong_prefix')[sid]['values']['service']
                row['answers'][sid+'_subject']={'choice':service,'probabilities':{service:1.0}}
            if row['arm']=='wrong_baseline':row['answers']={k:self.answer('supported') for k in row['answers']}
        result=t.assess(self.packets,refs,rows);m=result['panels']['Train Ticket']['all']['arms']['wrong_prefix'][0]['strata']['all']
        self.assertEqual(m['unsafe_displayed'],54);self.assertEqual(m['wrong_verdict_displayed'],0);self.assertFalse(result['candidate_passes'])

    def test_budget_is_once_per_sentence_pair_and_verdicts_are_unconditional(self):
        with patch.object(t,'check_plan',return_value={}):jobs=t.requests()
        self.assertEqual(len(jobs),1134);self.assertEqual(sum(len(j['body']['questions']) for j in jobs),1944)
        self.assertEqual({j['phase'] for j in jobs[:972]},{'text'});self.assertEqual({j['phase'] for j in jobs[972:]},{'verdict'})
        self.assertTrue(all(len(j['body']['questions'])==1 and j['sentence'] for j in jobs[:972]))
        self.assertEqual(len({(j['card_id'],j['arm'],j['round'],j['sentence']) for j in jobs}),1134)
        self.assertTrue(all(j['sentence'] is None and len(j['body']['questions'])==6 for j in jobs[972:]))

    def test_global_failure_stops_before_verdicts_and_rejects_rerun(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import Mock
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'test-placeholder-key'}
        plan={k:v for k,v in profile.items() if k!='api_key'}
        jobs=[{'id':'first','card_id':'n','arm':'prefix_subject','phase':'text','sentence':'s03','round':1,'body':{'model':t.MODEL,'state':'{}','questions':{}},'request_sha256':'a'},
              {'id':'later','card_id':'n','arm':'clean_baseline','phase':'verdict','sentence':None,'round':1,'body':{'model':t.MODEL,'state':'{}','questions':{}},'request_sha256':'b'}]
        opener=Mock();opener.open.side_effect=OSError('test transport failure')
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'run';protocol=Path(folder)/'protocol';protocol.write_text('{}')
            with patch.object(t,'OUT',out),patch.object(t,'PROTOCOL',protocol),patch.object(t,'check',return_value=(plan,jobs)),patch('triage_bench.prefix_subject_trial.urllib.request.build_opener',return_value=opener):
                result=t.run(profile);self.assertEqual(result['attempted_calls'],1);self.assertEqual(opener.open.call_count,1)
                self.assertNotIn(profile['api_key'],(out/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):t.run(profile)
