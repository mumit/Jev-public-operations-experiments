import copy
import json
import unittest
from triage_bench import separate_subject_trial as t
from triage_bench import subject_check_trial as old
from tests import test_subject_check as old_tests

class SeparateSubjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packets,cls.records=t.check_reviews()

    def test_controls_are_exact_and_sources_remain_unchanged(self):
        for p,r in zip(self.packets,self.records):
            snapshot=copy.deepcopy((p,r))
            for prefix in ('clean','wrong'):
                self.assertEqual(t.body(p,r,prefix+'_baseline'),old.body(p,r,prefix+'_baseline'))
                self.assertEqual(t.body(p,r,prefix+'_joint'),old.body(p,r,prefix+'_checked'))
            self.assertEqual((p,r),snapshot)

    def test_text_call_contains_only_note_and_same_subject_questions(self):
        for p,r in zip(self.packets,self.records):
            for prefix in ('clean','wrong'):
                b=t.body(p,r,prefix+'_checked');joint=t.body(p,r,prefix+'_joint')
                self.assertEqual(json.loads(b['state']),{'note':p['note']})
                self.assertEqual(len(b['questions']),6)
                self.assertEqual(b['questions'],{k:v for k,v in joint['questions'].items() if k.endswith('_subject')})
                self.assertEqual(b['model'],joint['model'])

    def test_proposal_change_preserves_literal_note_and_question_options(self):
        for p,r in zip(self.packets,self.records):
            clean=t.body(p,r,'clean_checked');wrong=t.body(p,r,'wrong_checked')
            self.assertEqual(clean['state'],wrong['state'])
            text={c['id']:c['text'] for c in p['candidates']}
            for field,q in clean['questions'].items():
                sid=field.split('_')[0];a=r['export']['reviews'][sid]['values']['service'];b=t.decisions(r,'wrong_checked')[sid]['values']['service']
                self.assertEqual(q['instructions'].replace('Proposed service: '+a+'.','Proposed service: '+b+'.'),wrong['questions'][field]['instructions'])
                self.assertTrue(q['instructions'].endswith(text[sid]));self.assertEqual(q['criteria'],wrong['questions'][field]['criteria'])

    answer=staticmethod(old_tests.SubjectCheckTests.answer)
    def fixture(self):
        refs={p['id']:{sid:{'verdict':'supported','service':d['values']['service'],'subject_form':'pronoun'} for sid,d in r['export']['reviews'].items() if d['decision']=='confirm'} for p,r in zip(self.packets,self.records)}
        rows=[]
        for p in self.packets:
            for arm in t.ARMS:
                for n in (1,2,3):
                    answers={}
                    for sid in refs[p['id']]:
                        if not arm.endswith('checked'):answers[sid+'_verdict']=self.answer('contradicted' if arm=='wrong_baseline' else 'supported')
                        if not arm.endswith('baseline'):answers[sid+'_subject']=self.answer('conflict' if arm.startswith('wrong') else 'matched')
                    rows.append({'id':p['id']+'::'+arm+'::'+str(n),'card_id':p['id'],'arm':arm,'round':n,'status':'ok','latency_ms':1,'usage':{'input_tokens':10},'answers':answers})
        return refs,rows

    def test_two_call_composition_uses_actual_baseline_without_rebinding(self):
        _,rows=self.fixture();index={(r['card_id'],r['arm'],r['round']):r for r in rows};snap=copy.deepcopy(index)
        row=t.composed_row(index,self.packets[0]['id'],'wrong_checked',1)
        self.assertEqual(row['answers']['s03_verdict']['choice'],'contradicted')
        self.assertEqual(row['answers']['s03_subject']['choice'],'conflict')
        self.assertFalse(t.decision(row,'s03',True)['displayed']);self.assertEqual(index,snap)
        self.assertEqual(len(row['source_call_ids']),2)

    def test_invalid_field_in_either_call_blocks_sentence_only(self):
        _,rows=self.fixture();index={(r['card_id'],r['arm'],r['round']):r for r in rows};note=self.packets[0]['id']
        for arm in ('clean_checked','clean_baseline'):
            source=index[(note,arm,1)];source['quarantined_sentences']=['s03'];source['status']='ok_with_review'
            row=t.composed_row(index,note,'clean_checked',1)
            self.assertFalse(t.decision(row,'s03',True)['displayed']);self.assertTrue(t.decision(row,'s04',True)['displayed'])
            self.assertEqual(row['answers']['s03_verdict']['choice'],'supported')
            source.pop('quarantined_sentences');source['status']='ok'

    def test_missing_either_call_never_displays_or_shrinks_denominator(self):
        for arm in ('clean_checked','clean_baseline'):
            refs,rows=self.fixture();rows=[r for r in rows if not(r['card_id']==self.packets[0]['id'] and r['arm']==arm and r['round']==1)]
            result=t.assess(self.packets,refs,rows);m=result['panels']['Train Ticket']['all']['arms']['clean_checked'][0]['strata']['all']
            self.assertEqual(m['denominator'],54);self.assertEqual(m['correct_safe_displayed'],48);self.assertFalse(m['complete']);self.assertFalse(result['candidate_passes'])

    def test_candidate_needs_clean_coverage_and_rejects_coincidental_safe_label(self):
        refs,rows=self.fixture();self.assertTrue(t.assess(self.packets,refs,rows)['candidate_passes'])
        for row in rows:
            if row['arm']=='clean_checked':
                row['answers']={k:self.answer('unresolved') for k in row['answers']}
        self.assertFalse(t.assess(self.packets,refs,rows)['candidate_passes'])
        refs,rows=self.fixture()
        for row in rows:
            if row['arm']=='wrong_checked':row['answers']={k:self.answer('matched') for k in row['answers']}
            if row['arm']=='wrong_baseline':row['answers']={k:self.answer('supported') for k in row['answers']}
        result=t.assess(self.packets,refs,rows);m=result['panels']['Train Ticket']['all']['arms']['wrong_checked'][0]['strata']['all']
        self.assertEqual(m['wrong_verdict_displayed'],0);self.assertEqual(m['unsafe_displayed'],54);self.assertFalse(result['candidate_passes'])

    def test_workflow_cost_adds_two_real_calls_without_claiming_extra_inference(self):
        refs,rows=self.fixture();r=t.assess(self.packets,refs,rows)
        self.assertEqual(sum(c['calls'] for c in r['costs'].values()),486)
        self.assertEqual(r['workflow_costs']['clean_checked']['calls'],162)
        self.assertEqual(r['workflow_costs']['clean_joint']['calls'],81)
        self.assertEqual(r['workflow_costs']['clean_checked']['input_tokens'],1620)
