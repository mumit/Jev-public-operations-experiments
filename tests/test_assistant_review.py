import copy
import unittest
from unittest.mock import patch
from tests import test_public_note_language as note_tests
from triage_bench import assistant_review_trial as trial
from triage_bench.public_note_features import annotated, verdict_request, DIMENSIONS
from triage_bench.claim_review import SCHEMA, fingerprint


class AssistantReviewTests(unittest.TestCase):
    def fixture(self):
        p,ref=note_tests.NoteLanguageTests().fixture()
        bound=annotated(p,ref)
        decisions={identifier:{'decision':'confirm','values':{d:b[d] for d in DIMENSIONS}} if b['accepted'] else {'decision':'withhold','reason':'unresolved'} for identifier,b in bound.items()}
        return p,ref,{'export':{'reviews':decisions}}

    def test_control_is_exact_frozen_bound_request_and_input_is_immutable(self):
        p,ref,r=self.fixture();before=copy.deepcopy((p,r));expected=verdict_request(p,annotated(p,ref))
        self.assertEqual(trial.body(p,r,'bound_text'),expected)
        self.assertEqual((p,r),before)

    def test_explicit_input_identifies_assistant_and_passes_meaning_without_answers(self):
        p,_,r=self.fixture();a=trial.body(p,r,'bound_text');b=trial.body(p,r,'explicit_meaning')
        self.assertEqual(a['state'],b['state']);self.assertEqual(set(a['questions']),set(b['questions']))
        for q in b['questions'].values():
            self.assertIn('assistant-reviewed',q['instructions']);self.assertIn('"kind":',q['instructions']);self.assertNotIn('analyst-confirmed',q['instructions']);self.assertNotIn('reference',q['instructions'])
        with self.assertRaises(ValueError):trial.body(p,r,'invented')

    def panels(self):
        packets,refs,rows=[],{},[]
        for dataset in ('Train Ticket','Online Boutique'):
            for wording in ('plain','negated','boundary'):
                p,ref,_=self.fixture();p.update(id=dataset+'-'+wording,dataset=dataset,wording=wording);refs[p['id']]=ref;packets.append(p)
                for arm in trial.ARMS:
                    for n in (1,2,3):
                        rows.append({'card_id':p['id'],'arm':arm,'round':n,'status':'ok','latency_ms':100,'usage':{'input_tokens':100},
                            'answers':{a['id']+'_verdict':{'choice':a['verdict'],'probabilities':{a['verdict']:.9}} for a in ref['annotations'] if a['actionable']}})
        return packets,refs,rows

    def test_no_output_repairs_and_complete_rounds_can_pass(self):
        packets,refs,rows=self.panels();before=copy.deepcopy(rows);result=trial.assess(packets,refs,rows)
        self.assertTrue(result['candidate_passes']);self.assertEqual(rows,before)
        self.assertEqual(result['panels']['all']['Train Ticket']['arms']['explicit_meaning'][0]['correct'],18)

    def test_missing_failed_or_wrong_answers_keep_full_denominators(self):
        for mode in ('missing','failed','wrong'):
            packets,refs,rows=self.panels();row=next(r for r in rows if r['arm']=='explicit_meaning')
            if mode=='missing':rows.remove(row)
            elif mode=='failed':row.update(status='error',answers={})
            else:
                key=next(iter(row['answers']));row['answers'][key]={'choice':'invented','probabilities':{'invented':.99}}
            result=trial.assess(packets,refs,rows);self.assertFalse(result['candidate_passes'])
            panel=result['panels']['plain']['Train Ticket']['arms']['explicit_meaning'][0];self.assertEqual(panel['denominator'],6);self.assertLess(panel['correct'],6)

    def test_correct_verdict_lost_to_display_fails_even_when_accuracy_stays_perfect(self):
        packets,refs,rows=self.panels();row=next(r for r in rows if r['arm']=='explicit_meaning');key=next(iter(row['answers']));choice=row['answers'][key]['choice'];row['answers'][key]['probabilities'][choice]=.69
        result=trial.assess(packets,refs,rows);self.assertFalse(result['candidate_passes'])
        panel=result['panels']['plain']['Train Ticket']['arms']['explicit_meaning'][0];self.assertEqual(panel['correct'],6);self.assertEqual(panel['correct_displayed'],5)

    def test_review_provenance_cannot_be_relabelled_human(self):
        with patch.object(trial,'committed'),patch.object(trial,'load',return_value={'schema':'assistant-review-decisions-1','human_review':True,'independent_review':False,'blinded':False}):
            with self.assertRaises(ValueError):trial.check_reviews()
