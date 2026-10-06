import copy
import json
import unittest
from tests import test_public_notes as note_tests
from triage_bench.public_note_language_features import compose, FORMS, ARMS, extraction_request, validate_changes
from triage_bench.public_note_features import DIMENSIONS, semantics, annotated, verdict_request
from triage_bench.public_contrast_features import MEANING
from triage_bench.public_note_language_trial import assess


class NoteLanguageTests(unittest.TestCase):
    def fixture(self, form='plain'):
        p, r = note_tests.NoteTests().fixture()
        return compose(p, r, form)

    def test_all_forms_preserve_meanings_facts_verdicts_and_input(self):
        old, ref = note_tests.NoteTests().fixture(); before = copy.deepcopy((old, ref))
        original = {a['category']: a for a in ref['annotations']}
        for form in FORMS:
            p, r = compose(old, ref, form)
            self.assertNotEqual(p['note'], old['note'])
            self.assertEqual(p['observations'], old['observations'])
            for a in r['annotations']:
                gold = original[a['category']]
                for k in ('category', 'role', 'actionable', *DIMENSIONS, 'proposition', 'verdict', 'facts'):
                    self.assertEqual(a.get(k), gold.get(k))
                self.assertEqual(p['note'][a['start']:a['end']], a['text'])
        self.assertEqual((old, ref), before)

    def test_generic_boundaries_preserve_decimal_compound_and_denominators(self):
        for form in FORMS:
            p, r = self.fixture(form)
            self.assertEqual(len(p['candidates']), 12)
            self.assertEqual(sum(a['actionable'] for a in r['annotations']), 6)
            self.assertEqual(sum(a['role'] == 'assertion' for a in r['annotations']), 7)
            self.assertEqual(sum(a['role'] == 'multiple_assertions' for a in r['annotations']), 1)
            self.assertEqual(sum(a['role'] == 'non_assertion' for a in r['annotations']), 4)
            self.assertEqual(sum(v['accepted'] for v in annotated(p, r).values()), 6)

    def test_local_antecedent_blocks_remain_intact(self):
        for form in FORMS:
            _, r = self.fixture(form); order = [a['category'] for a in r['annotations']]
            for block in [('a_metric','a_duration','a_cause'), ('b_check','b_metric','b_count','b_health')]:
                start = order.index(block[0]); self.assertEqual(tuple(order[start:start+len(block)]), block)

    def test_fixed_family_only_changes_no_other_definitions_questions_or_inputs(self):
        p, _ = self.fixture(); before = copy.deepcopy(p); validate_changes(p)
        a, b = [extraction_request(p, arm) for arm in ARMS]
        sa, sb = json.loads(a['state']), json.loads(b['state'])
        self.assertEqual(a['questions'], b['questions'])
        self.assertEqual(sb['extraction_definitions']['kind'], MEANING)
        self.assertEqual({k for k in sa['extraction_definitions'] if sa['extraction_definitions'][k] != sb['extraction_definitions'][k]}, {'kind'})
        self.assertEqual(p, before)
        with self.assertRaises(ValueError): extraction_request(p, 'combined')

    def test_requests_cannot_include_annotations_or_source_identity(self):
        for form in FORMS:
            p, _ = self.fixture(form)
            for arm in ARMS:
                b = extraction_request(p, arm); s = json.loads(b['state'])
                self.assertEqual(set(s), {'note','candidates','observed_service_inventory','metric_channel_inventory','extraction_definitions'})
                self.assertEqual(len(b['questions']), 72)
                for forbidden in ('observations', 'annotations','reference', 'parent_note_id', p['id'],p['parent_note_id'],p['source_report_id']):
                    self.assertNotIn(forbidden, json.dumps(b))

    def test_verdicts_use_actual_bindings_and_keep_raw_new_text(self):
        p,r = self.fixture('boundary'); b = annotated(p,r); v = verdict_request(p,b)
        self.assertEqual(len(v['questions']),6)
        for a in r['annotations']:
            if a['actionable']:
                self.assertIn(a['text'],v['questions'][a['id']+'_verdict']['instructions'])
        target=next(a for a in r['annotations'] if a['actionable']); b[target['id']]['accepted']=False
        self.assertNotIn(target['id']+'_verdict', verdict_request(p,b)['questions'])

    def panel(self):
        p,r=self.fixture(); assigned=[]; verdicts=[]; extraction=[]
        for n in (1,2,3):
            for arm in ARMS:
                assigned.append({'card_id':p['id'],'round':n,'arm':arm,'bindings':annotated(p,r)})
                verdicts.append({'card_id':p['id'],'round':n,'arm':arm,'status':'ok','answers':{a['id']+'_verdict':{'choice':a['verdict'],'probabilities':{a['verdict']:.99}} for a in r['annotations'] if a['actionable']}})
                extraction.append({'card_id':p['id'],'round':n,'arm':arm,'status':'ok'})
        return p,r,assigned,verdicts,extraction

    def test_failed_family_candidate_keeps_full_denominator(self):
        p,r,a,v,e=self.panel(); target=next(x for x in r['annotations'] if x['actionable'])
        next(x for x in a if x['arm']=='meaning' and x['round']==1)['bindings'][target['id']]['accepted']=False
        panel=assess([p],[r],a,v,e)[p['dataset']]
        self.assertFalse(panel['research_gate']); self.assertEqual(panel['candidate_gate']['candidate'],'meaning')
        row=panel['arms']['meaning']['per_round'][0]
        self.assertEqual((row['routable_claims'],row['end_to_end_correct']),(6,5))
        self.assertEqual(panel['comparisons'][0]['per_round'][0]['binding_loss'],1)

    def test_wrong_binding_with_right_verdict_remains_unsafe(self):
        p,r,a,v,e=self.panel(); target=next(x for x in r['annotations'] if x['actionable'])
        bound=next(x for x in a if x['arm']=='meaning' and x['round']==1)['bindings'][target['id']]
        bound['service']='beta' if bound['service']=='alpha' else 'alpha'
        row=assess([p],[r],a,v,e)[p['dataset']]['arms']['meaning']['per_round'][0]
        self.assertEqual((row['accepted_wrong_bindings'],row['unsafe_displayed'],row['end_to_end_correct']),(1,1,5))
