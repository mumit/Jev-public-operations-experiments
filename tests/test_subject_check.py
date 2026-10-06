import copy
import unittest
from triage_bench import subject_check_trial as t
from triage_bench.assistant_review_trial import check_reviews
from triage_bench.binding_corruption_trial import body as prior_body

class SubjectCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packets,cls.records=check_reviews()

    def test_exact_baselines_and_identical_evidence(self):
        for p,r in zip(self.packets,self.records):
            snapshot=copy.deepcopy(r)
            self.assertEqual(t.body(p,r,'clean_baseline'),prior_body(p,r,'clean_bound'))
            self.assertEqual(t.body(p,r,'wrong_baseline'),prior_body(p,r,'service_bound'))
            self.assertEqual(len({t.body(p,r,a)['state'] for a in t.ARMS}),1)
            self.assertEqual(snapshot,r)

    def test_checked_questions_keep_literal_text_and_flag_uncertain_proposal(self):
        for p,r in zip(self.packets,self.records):
            text={c['id']:c['text'] for c in p['candidates']}
            for arm in ('clean_checked','wrong_checked'):
                b=t.body(p,r,arm);self.assertEqual(len(b['questions']),12)
                for field,q in b['questions'].items():
                    self.assertTrue(q['instructions'].endswith(text[field.split('_')[0]]))
                    self.assertIn('may be incorrect',q['instructions'])
                    self.assertNotIn('assistant-reviewed',q['instructions'])
                    if field.endswith('_subject'):self.assertEqual(set(q['criteria']),{'matched','conflict','unresolved'})
                    else:self.assertEqual(set(q['criteria']),{'supported','contradicted','unanswerable'})

    def test_clean_vs_corrupt_checked_only_changes_proposed_service(self):
        for p,r in zip(self.packets,self.records):
            clean=t.body(p,r,'clean_checked');wrong=t.body(p,r,'wrong_checked')
            decisions=t.decisions(r,'wrong_checked')
            for field,q in clean['questions'].items():
                sid=field.split('_')[0];original=r['export']['reviews'][sid]['values']['service'];changed=decisions[sid]['values']['service']
                instructions=q['instructions'].replace('Proposed service: '+original+'.','Proposed service: '+changed+'.').replace('The proposed service binding is '+original+';','The proposed service binding is '+changed+';')
                self.assertEqual(instructions,wrong['questions'][field]['instructions'])
                self.assertEqual(q['criteria'],wrong['questions'][field]['criteria'])

    @staticmethod
    def answer(choice,probability=1):
        choices=('matched','conflict','unresolved') if choice in ('matched','conflict','unresolved') else ('supported','contradicted','unanswerable')
        return {'choice':choice,'probabilities':{k:probability if k==choice else (1-probability)/2 for k in choices}}

    def test_display_requires_both_probabilities_and_matching_subject(self):
        row={'status':'ok','answers':{'s03_verdict':self.answer('supported'),'s03_subject':self.answer('matched',.69)}}
        self.assertFalse(t.decision(row,'s03',True)['displayed'])
        row['answers']['s03_subject']=self.answer('matched',.70)
        self.assertTrue(t.decision(row,'s03',True)['displayed'])
        row['answers']['s03_subject']=self.answer('conflict',1)
        self.assertFalse(t.decision(row,'s03',True)['displayed'])
        row['answers']['s03_subject']=self.answer('unresolved',1)
        self.assertFalse(t.decision(row,'s03',True)['displayed'])
        self.assertTrue(t.decision(row,'s03',False)['displayed'])

    def test_invalid_sibling_quarantines_both_decisions(self):
        row={'status':'ok_with_review','quarantined_sentences':['s03'],'answers':{'s03_verdict':self.answer('supported'),'s03_subject':self.answer('matched'),'s04_verdict':self.answer('supported'),'s04_subject':self.answer('matched')}}
        self.assertFalse(t.decision(row,'s03',True)['displayed']);self.assertEqual(t.decision(row,'s03',True)['verdict'],'unavailable')
        self.assertTrue(t.decision(row,'s04',True)['displayed']);self.assertEqual(row['answers']['s03_verdict']['choice'],'supported')

    def fixture(self):
        refs={p['id']:{sid:{'verdict':'supported','service':d['values']['service'],'subject_form':'pronoun'} for sid,d in r['export']['reviews'].items() if d['decision']=='confirm'} for p,r in zip(self.packets,self.records)}
        rows=[]
        for p in self.packets:
            for arm in t.ARMS:
                for n in (1,2,3):
                    answers={sid+'_verdict':self.answer('contradicted' if arm=='wrong_baseline' else 'supported') for sid in refs[p['id']]}
                    if arm.endswith('checked'):answers.update({sid+'_subject':self.answer('conflict' if arm.startswith('wrong') else 'matched') for sid in refs[p['id']]})
                    rows.append({'card_id':p['id'],'arm':arm,'round':n,'status':'ok','latency_ms':1,'answers':answers})
        return refs,rows

    def test_success_requires_detection_and_clean_coverage(self):
        refs,rows=self.fixture();r=t.assess(self.packets,refs,rows);self.assertTrue(r['candidate_passes'])
        for row in rows:
            if row['arm']=='clean_checked':
                for field in row['answers']:
                    if field.endswith('_subject'):row['answers'][field]=self.answer('conflict')
        r=t.assess(self.packets,refs,rows);self.assertFalse(r['candidate_passes'])
        self.assertEqual(r['panels']['Train Ticket']['all']['arms']['clean_checked'][0]['strata']['all']['safe_display_losses'],54)

    def test_wrong_binding_is_unsafe_even_with_correct_verdict(self):
        refs,rows=self.fixture()
        for row in rows:
            if row['arm']=='wrong_checked':
                for field in row['answers']:
                    if field.endswith('_subject'):row['answers'][field]=self.answer('matched')
        r=t.assess(self.packets,refs,rows);self.assertFalse(r['candidate_passes'])
        m=r['panels']['Train Ticket']['all']['arms']['wrong_checked'][0]['strata']['all']
        self.assertEqual(m['correct'],54);self.assertEqual(m['wrong_verdict_displayed'],0);self.assertEqual(m['unsafe_displayed'],54)

    def test_missing_call_keeps_subject_and_verdict_denominators(self):
        refs,rows=self.fixture();rows=[r for r in rows if not(r['card_id']==self.packets[0]['id'] and r['arm']=='clean_checked' and r['round']==1)]
        r=t.assess(self.packets,refs,rows);m=r['panels']['Train Ticket']['all']['arms']['clean_checked'][0]['strata']['all']
        self.assertEqual(m['denominator'],54);self.assertEqual(m['correct'],48);self.assertEqual(m['subject_correct'],48);self.assertFalse(m['complete']);self.assertFalse(r['candidate_passes'])

    def test_inspector_hides_references_and_composes_only_actual_answers(self):
        from unittest.mock import patch
        from triage_bench.subject_check_service import SubjectCheckStudy
        from triage_bench.paths import ROOT
        study=SubjectCheckStudy(ROOT);saved=t.load(t.RESULT);snapshot=copy.deepcopy(saved)
        with patch.object(study,'verified',return_value=saved):
            hidden=study.card(self.packets[0]['id']);shown=study.card(self.packets[0]['id'],True)
            self.assertIsNone(hidden['reference']);self.assertTrue(shown['reference'])
            self.assertNotIn('outcomes',study.overview());self.assertEqual(saved,snapshot)
            for row in hidden['composition']:
                for value in row['sentences'].values():self.assertNotIn('reference',value);self.assertNotIn('safe',value)

    def test_report_keeps_selected_case_return(self):
        from types import SimpleNamespace
        from triage_bench.paths import ROOT
        from triage_bench.study_page import render_study
        target='/subject-check?dataset=Online+Boutique&wording=boundary&arm=wrong_checked&round=1&sentence=s07'
        html=render_study(SimpleNamespace(root=ROOT),{'doc':'subject-check','return':target}).decode()
        self.assertIn('Check the subject before displaying a verdict',html);self.assertIn('wrong_checked',html)
