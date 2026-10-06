import copy
import unittest
from unittest.mock import patch
from triage_bench import subject_robustness_trial as t

class SubjectRobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cards=t.load(t.CARDS);cls.refs=t.load(t.REFERENCES)
    def fixture(self):
        rows=[]
        for c in self.cards:
            for n in (1,2,3):
                for arm in t.ARMS:
                    choice=self.refs[c['id']]['visible_subjects'][arm]
                    rows.append({'id':c['id']+arm+str(n),'card_id':c['id'],'arm':arm,'round':n,'sentence':c['sentence'],'answers':{c['sentence']+'_subject':{'choice':choice,'probabilities':{choice:1}}},'status':'ok','quarantined_sentences':[],'usage':{'input_tokens':10},'latency_ms':2})
        return rows
    def test_wire_contains_no_references_or_family_and_only_context_differs(self):
        for c in self.cards:
            wire=[t.body(c,a) for a in t.ARMS];prototype=copy.deepcopy(wire[0]);prototype.pop('state')
            for a,b in zip(t.ARMS,wire):
                state=t.json.loads(b.pop('state'));self.assertEqual(set(state),{'note','observed_services'})
                self.assertEqual(state['note'],t.context(c,a));self.assertEqual(state['observed_services'],c['services'])
                self.assertEqual(b,prototype);self.assertNotIn('source_subject',state);self.assertNotIn('family',state)
                text=next(x['text'] for x in c['candidates'] if x['id']==c['sentence'])
                self.assertTrue(b['questions'][c['sentence']+'_subject']['instructions'].endswith(text))
    def test_fifteen_families_keep_expected_information_losses_explicit(self):
        self.assertEqual(len(self.cards),135);self.assertEqual(len({c['family'] for c in self.cards}),15)
        for c in self.cards:
            ref=self.refs[c['id']]
            if c['family']=='later_clarification':
                self.assertNotEqual(ref['visible_subjects']['full'],'unresolved');self.assertEqual(ref['visible_subjects']['prefix'],'unresolved')
            if c['family'] in ('quoted_interruption','request_interruption','question_interruption'):
                self.assertNotEqual(ref['visible_subjects']['prefix'],'unresolved');self.assertEqual(ref['visible_subjects']['excerpt'],'unresolved')
            if c['family'] in ('ambiguous_pair','missing_anchor','quoted_target','compound_target','outside_inventory'):self.assertEqual(ref['source_subject'],'unresolved')
    def test_exact_budget_and_rotation_no_numeric_verdict_phase(self):
        with patch.object(t,'check_plan',return_value={}):jobs=t.requests()
        self.assertEqual(len(jobs),1215);self.assertEqual(len({j['id'] for j in jobs}),1215)
        self.assertTrue(all(len(j['body']['questions'])==1 and j['phase']=='text' for j in jobs))
        self.assertEqual({a:sum(j['arm']==a for j in jobs) for a in t.ARMS},{a:405 for a in t.ARMS})
    def test_perfect_visible_answers_can_still_lose_source_coverage(self):
        result=t.assess(self.cards,self.refs,self.fixture())
        self.assertTrue(all(o['visible_correct'] for o in result['outcomes']));self.assertFalse(result['candidate_passes'])
        self.assertTrue(any(p['source_display_losses']>0 for p in result['paired']))
        self.assertFalse(any(o['unsupported_eligible'] for o in result['outcomes']))
    def test_lucky_hidden_subject_is_not_a_safe_eligible_resolution(self):
        rows=self.fixture();c=next(c for c in self.cards if c['family']=='later_clarification');original=self.refs[c['id']]['source_subject']
        r=next(r for r in rows if r['card_id']==c['id'] and r['arm']=='excerpt' and r['round']==1)
        r['answers'][c['sentence']+'_subject']={'choice':original,'probabilities':{original:1}}
        out=next(o for o in t.assess(self.cards,self.refs,rows)['outcomes'] if o['card_id']==c['id'] and o['arm']=='excerpt' and o['round']==1)
        self.assertTrue(out['source_correct']);self.assertTrue(out['unsupported_eligible']);self.assertFalse(out['safe_source_eligible'])
    def test_missing_and_quarantined_calls_preserve_denominators(self):
        rows=self.fixture();rows.pop();rows[0]['quarantined_sentences']=[rows[0]['sentence']]
        result=t.assess(self.cards,self.refs,rows)
        self.assertEqual(len(result['outcomes']),1215);self.assertEqual(sum(o['quarantined'] for o in result['outcomes']),1)
        self.assertTrue(any(not o['complete'] for o in result['outcomes']));self.assertFalse(result['candidate_passes'])

class RobustnessConsumerTests(unittest.TestCase):
    def test_inspector_preserves_actual_context_and_hides_judgments(self):
        from triage_bench.subject_robustness_service import SubjectRobustnessStudy
        from triage_bench.paths import ROOT
        study=SubjectRobustnessStudy(ROOT);identifier='RSC-9780eea6c8b1'
        with patch.object(study,'verified',return_value=t.load(t.RESULT)):
            hidden=study.card(identifier);shown=study.card(identifier,True)
            self.assertIsNone(hidden['reference']);self.assertIsNone(hidden['outcomes'])
            self.assertEqual(shown['reference']['visible_subjects']['excerpt'],'unresolved')
            self.assertEqual(hidden['contexts']['excerpt'],'Is shippingservice healthy?\nThe service in my current assessment has enough recorded spans.')
            self.assertNotIn('outcomes',study.overview())
    def test_reader_keeps_context_and_challenge(self):
        from types import SimpleNamespace
        from triage_bench.study_page import render_study
        from triage_bench.paths import ROOT
        html=render_study(SimpleNamespace(root=ROOT),{'doc':'subject-robustness','return':'/subject-robustness?arm=excerpt&card=RSC-9780eea6c8b1#inspect'}).decode()
        self.assertIn('Check what context selection removes',html);self.assertIn('RSC-9780eea6c8b1',html);self.assertIn('#inspect',html)
