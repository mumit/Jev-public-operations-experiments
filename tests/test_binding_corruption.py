import copy
import unittest
from triage_bench import binding_corruption_trial as t
from triage_bench.assistant_review_trial import check_reviews, body

class BindingCorruptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.packets,cls.records=check_reviews()

    def test_clean_controls_are_exact_and_every_state_identical(self):
        for p,r in zip(self.packets,self.records):
            original=copy.deepcopy(r)
            self.assertEqual(t.body(p,r,'clean_bound'),body(p,r,'bound_text'))
            self.assertEqual(t.body(p,r,'clean_meaning'),body(p,r,'explicit_meaning'))
            states=[t.body(p,r,a)['state'] for a in t.ARMS]
            self.assertEqual(len(set(states)),1)
            self.assertEqual(r,original)

    def test_bijective_subject_swap_and_only_polarity_changes(self):
        for r in self.records:
            changed=t.altered(r,'service_bound')['export']['reviews']
            flipped=t.altered(r,'polarity_meaning')['export']['reviews']
            for sid,v in r['export']['reviews'].items():
                if v['decision']=='withhold':
                    self.assertEqual(changed[sid],v);self.assertEqual(flipped[sid],v);continue
                self.assertNotEqual(changed[sid]['values']['service'],v['values']['service'])
                self.assertEqual({k:x for k,x in changed[sid]['values'].items() if k!='service'},{k:x for k,x in v['values'].items() if k!='service'})
                self.assertNotEqual(flipped[sid]['values']['polarity'],v['values']['polarity'])
                self.assertEqual({k:x for k,x in flipped[sid]['values'].items() if k!='polarity'},{k:x for k,x in v['values'].items() if k!='polarity'})

    def test_literal_sentences_preserved_in_actual_questions(self):
        for p,r in zip(self.packets,self.records):
            text={c['id']:c['text'] for c in p['candidates']}
            for arm in t.ARMS:
                q=t.body(p,r,arm)['questions']
                self.assertEqual(len(q),6)
                for sid,item in q.items():self.assertTrue(item['instructions'].endswith(text[sid.removesuffix('_verdict')]))

    def test_missing_and_wrong_replies_keep_full_denominators(self):
        p=self.packets[0];sid='s03'
        refs={p['id']:{a:{sid:{'original':'supported','altered':'contradicted','divergent':True,'subject_form':'direct_name'}} for a in t.ARMS}}
        row={'card_id':p['id'],'arm':'service_bound','round':1,'status':'ok','latency_ms':1,'answers':{sid+'_verdict':{'choice':'contradicted','probabilities':{'supported':.01,'contradicted':.98,'unanswerable':.01}}}}
        result=t.assess([p],refs,[row]);m=result['panels'][p['dataset']]['all']['service_bound'][0]['strata']
        self.assertEqual(m['divergent']['denominator'],1);self.assertEqual(m['divergent']['wrong_displayed'],1)
        self.assertEqual(m['divergent']['matches_altered'],1);self.assertEqual(m['invariant']['denominator'],0)
        absent=result['panels'][p['dataset']]['all']['clean_bound'][0]['strata']['all']
        self.assertFalse(absent['complete']);self.assertEqual(absent['denominator'],1);self.assertEqual(absent['correct'],0);self.assertEqual(absent['withheld'],1)

    def test_confident_correct_invariant_does_not_prove_binding(self):
        p=self.packets[0];sid='s03';refs={p['id']:{a:{sid:{'original':'unanswerable','altered':'unanswerable','divergent':False,'subject_form':'pronoun'}} for a in t.ARMS}}
        row={'card_id':p['id'],'arm':'service_meaning','round':1,'status':'ok','latency_ms':1,'answers':{sid+'_verdict':{'choice':'unanswerable','probabilities':{'supported':.01,'contradicted':.01,'unanswerable':.98}}}}
        m=t.assess([p],refs,[row])['panels'][p['dataset']]['all']['service_meaning'][0]['strata']
        self.assertEqual(m['all']['correct'],1);self.assertEqual(m['divergent']['denominator'],0);self.assertEqual(m['invariant']['denominator'],1)
