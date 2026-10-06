import copy
import unittest
from unittest.mock import patch
from triage_bench import excerpt_subject_trial as t
from triage_bench import prefix_subject_trial as prior
from tests import test_prefix_subject as prior_tests


class ExcerptSubjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packets,cls.records=t.check_reviews()
    answer=staticmethod(prior_tests.PrefixSubjectTests.answer)
    def fixture(self):
        refs,rows=prior_tests.PrefixSubjectTests.fixture(self)
        for row in rows:
            row['arm']={'full_subject':'prefix_subject','prefix_subject':'excerpt_subject'}.get(row['arm'],row['arm'])
        return refs,rows
    def packet(self,lines,services):
        return {'note':'\r\n'.join(lines),'services':services,'candidates':[{'id':'s'+str(i+1),'text':x} for i,x in enumerate(lines)]}

    def test_latest_complete_name_preserves_exact_source_slice(self):
        p=self.packet(['frontend has a fault.','Inspect frontend-external.','frontend-external has rising errors.','This service has enough spans.'],['frontend','frontend-external'])
        c=t.excerpt_context(p,'s4')
        self.assertEqual(c['note'],'frontend-external has rising errors.\r\nThis service has enough spans.')
        self.assertEqual(c['mentioned_services'],['frontend-external']);self.assertEqual(c['start_sentence'],'s3')
        self.assertEqual(p['note'][c['start_offset']:c['end_offset']],c['note'])

    def test_multi_name_and_no_name_fall_back_without_skipping_latest_sentence(self):
        for lines,reason in [(['redis is abnormal.','redis and frontend are under review.','This service is healthy.'],'multiple_names_full_prefix'),(['An incident is under review.','This service is healthy.'],'no_name_full_prefix')]:
            p=self.packet(lines,['redis','frontend']);c=t.excerpt_context(p,'s'+str(len(lines)))
            self.assertEqual(c['note'],p['note']);self.assertEqual(c['selection'],reason);self.assertEqual(c['start_offset'],0)

    def test_exact_case_boundaries_and_repeated_sentence_offsets(self):
        p=self.packet(['redis is abnormal.','redis is abnormal.','This service is healthy.'],['redis'])
        c=t.excerpt_context(p,'s3');self.assertEqual(c['start_sentence'],'s2');self.assertGreater(c['start_offset'],0)
        p=self.packet(['REDIS is abnormal.','xredis and redis-x appear here.','This service is healthy.'],['redis'])
        self.assertEqual(t.excerpt_context(p,'s3')['selection'],'no_name_full_prefix')
        with self.assertRaises(ValueError):t.excerpt_context(p,'missing')
        p['candidates'][0]['text']='Changed'
        with self.assertRaises(ValueError):t.excerpt_context(p,'s3')

    def test_paired_body_changes_only_note_and_never_uses_reviewed_subject(self):
        for p,r in zip(self.packets,self.records):
            original=copy.deepcopy((p,r))
            for c in p['candidates']:
                if r['export']['reviews'][c['id']]['decision']!='confirm':continue
                sid=c['id'];a=t.body(p,r,'prefix_subject',sid);b=t.body(p,r,'excerpt_subject',sid)
                self.assertEqual(a,prior.body(p,r,'prefix_subject',sid));aa=t.json.loads(a['state']);bb=t.json.loads(b['state'])
                self.assertEqual(bb['note'],t.excerpt_context(p,sid)['note']);self.assertEqual(aa['observed_services'],bb['observed_services'])
                aa.pop('note');bb.pop('note');self.assertEqual(aa,bb)
                a.pop('state');b.pop('state');self.assertEqual(a,b)
                changed=copy.deepcopy(r);changed['export']['reviews'][sid]['values']['service']='wrong-reference'
                self.assertEqual(t.body(p,r,'excerpt_subject',sid),t.body(p,changed,'excerpt_subject',sid))
            self.assertEqual((p,r),original)
            for a in ('clean_baseline','wrong_baseline'):self.assertEqual(t.body(p,r,a),prior.body(p,r,a))

    def test_budget_is_fixed_and_verdicts_unconditional(self):
        with patch.object(t,'check_plan',return_value={}):jobs=t.requests()
        self.assertEqual(len(jobs),1134);self.assertEqual(sum(len(j['body']['questions']) for j in jobs),1944)
        self.assertTrue(all(j['phase']=='text' and len(j['body']['questions'])==1 for j in jobs[:972]))
        self.assertTrue(all(j['phase']=='verdict' and len(j['body']['questions'])==6 for j in jobs[972:]))
        self.assertEqual(len({j['id'] for j in jobs}),1134)

    def test_shared_subject_gates_and_paired_regressions_are_not_repaired(self):
        refs,rows=self.fixture();result=t.assess(self.packets,refs,rows)
        self.assertTrue(result['candidate_passes']);self.assertEqual(result['workflow_costs']['clean_excerpt']['calls'],567)
        self.assertEqual(sum(v['calls'] for v in result['costs'].values()),1134)
        row=next(r for r in rows if r['arm']=='excerpt_subject');sid=row['sentence'];row['answers'][sid+'_subject']['probabilities'][row['answers'][sid+'_subject']['choice']]=.69
        result=t.assess(self.packets,refs,rows);self.assertFalse(result['candidate_passes'])
        self.assertEqual(sum(p['losses'] for p in result['paired_clean_displays'] if p['wording']=='all'),1)
        rows.remove(row);result=t.assess(self.packets,refs,rows)
        self.assertEqual(sum(p['denominator'] for p in result['unique_subject'] if p['wording']=='all' and p['approach']=='excerpt'),486)

    def test_wrong_subject_is_unsafe_even_with_coincident_verdict(self):
        refs,rows=self.fixture();p=self.packets[0];r=self.records[0];sid='s03'
        row=next(x for x in rows if x['card_id']==p['id'] and x['arm']=='excerpt_subject' and x['round']==1 and x['sentence']==sid)
        service=t.decisions(r,'wrong_excerpt')[sid]['values']['service'];row['answers'][sid+'_subject']={'choice':service,'probabilities':{service:1}}
        result=t.assess(self.packets,refs,rows)
        o=next(o for o in result['outcomes'] if o['note_id']==p['id'] and o['arm']=='wrong_excerpt' and o['round']==1 and o['sentence']==sid)
        self.assertTrue(o['displayed']);self.assertTrue(o['unsafe_displayed']);self.assertFalse(result['candidate_passes'])

    def test_quarantine_remains_local_and_sources_remain_actual(self):
        _,rows=self.fixture();p=self.packets[0];r=self.records[0];index={(x['card_id'],x['arm'],x['round'],x['sentence']):x for x in rows}
        index[(p['id'],'excerpt_subject',1,'s03')]['quarantined_sentences']=['s03']
        a=t.composed_row(index,p['id'],'clean_excerpt',1,r,'s03');b=t.composed_row(index,p['id'],'wrong_excerpt',1,r,'s03')
        self.assertEqual(a['source_call_ids'][0],b['source_call_ids'][0]);self.assertFalse(t.decision(a,'s03',True)['displayed'])
        self.assertTrue(t.decision(t.composed_row(index,p['id'],'clean_excerpt',1,r,'s04'),'s04',True)['displayed'])

    def test_inspector_context_is_source_derived_and_references_are_hidden(self):
        from triage_bench.paths import ROOT
        from triage_bench.excerpt_subject_service import ExcerptSubjectStudy
        study=ExcerptSubjectStudy(ROOT);saved=t.load(t.RESULT)
        with patch.object(study,'verified',return_value=saved):
            hidden=study.card(self.packets[0]['id']);shown=study.card(self.packets[0]['id'],True)
            self.assertIsNone(hidden['reference']);self.assertTrue(shown['reference'])
            self.assertEqual(hidden['contexts']['s03'],t.excerpt_context(self.packets[0],'s03'))
            self.assertNotIn('outcomes',study.overview())
    def test_report_preserves_selected_workflow_and_sentence(self):
        from types import SimpleNamespace
        from triage_bench.paths import ROOT
        from triage_bench.study_page import render_study
        html=render_study(SimpleNamespace(root=ROOT),{'doc':'excerpt-subject','return':'/excerpt-subject?arm=clean_excerpt&round=2&sentence=s07'}).decode()
        self.assertIn('latest explicit service context',html);self.assertIn('clean_excerpt',html);self.assertIn('sentence=s07',html)
