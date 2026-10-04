import unittest
from triage_bench.public_agreement_policy import route,assess
from triage_bench.public_agreement_data import partition

class RoutingTests(unittest.TestCase):
    def row(self,choice='a',p=.8):return {'case_id':'one','round':1,'status':'ok','choice':choice,'probabilities':{choice:p,'b' if choice=='a' else 'a':1-p,'insufficient_evidence':0.}}
    def test_reference_free_routing_and_no_fallback(self):
        r=route(self.row(),'b');self.assertEqual(r['action'],'review_required');self.assertEqual(r['leads'],[]);self.assertEqual(r['base_leads'],['a']);self.assertEqual(r['ml_choice'],'b')
        self.assertEqual(route(self.row(),'a')['leads'],['a'])
    def test_boundary_missing_and_insufficient_evidence(self):
        self.assertEqual(route(self.row(p=.69),'b')['action'],'withheld')
        self.assertEqual(route(None,'a')['reason'],'failed_or_missing')
        self.assertEqual(route({'status':'ok','choice':'insufficient_evidence','probabilities':{'a':.3,'insufficient_evidence':.7}},'a')['action'],'withheld')
        self.assertEqual(route(self.row(),'absent')['reason'],'ml_unavailable')
    def test_both_wrong_agreement_and_correct_loss_are_visible(self):
        refs=[{'id':'one','group':'g','fault':'loss','target':'b'},{'id':'two','group':'h','fault':'cpu','target':'a'}]
        rows=[self.row(),{**self.row(),'case_id':'two'}];controls={'one':{'ml':{'choice':'a'}},'two':{'ml':{'choice':'b'}}}
        r=assess(rows,refs,controls,rounds=1)['per_round'][0]
        self.assertEqual(r['agreements_both_wrong'],1);self.assertEqual(r['correct_routed_to_review'],1);self.assertEqual(r['wrong_routed_to_review'],0)
    def test_grouped_balanced_split_excludes_audit(self):
        rows=[{'case':f'{d}_{s}_{f}_{n}','dataset':d,'root_cause_service':s,'fault':f,'repetition':n} for d in ('RE1-TT','RE1-SS') for s in 'abcde' for f in ('cpu','delay','disk','loss','mem') for n in range(1,6)]
        audit=[r['case'] for r in rows if r['root_cause_service']=='a' and r['fault']=='cpu']
        result=partition(rows,audit)
        self.assertEqual(sum(r['split']=='evaluation' for r in result),100);self.assertEqual(sum(r['split']=='reserve' for r in result),140)
        self.assertFalse(any(r['source_case'] in audit for r in result if r['split']=='evaluation'))
