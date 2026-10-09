import unittest
from triage_bench.review_budget_service import ReviewBudgetStudy
from triage_bench.study_page import render_study,return_path

class ReviewBudgetServiceTests(unittest.TestCase):
 def test_every_round_meets_review_budget(self):
  o=ReviewBudgetStudy().overview();r=o['results'];self.assertEqual(len(o['claims']),27);self.assertEqual(r['actual_calls'],162);self.assertTrue(r['candidate_passes'])
  self.assertTrue(all(g['passes'] for g in r['gates']));panels=[p for p in r['panels'] if p['arm']=='knowledge' and p['source_id']=='all' and p['reference_class']=='all' and p['assertion_scope']=='all']
  self.assertEqual([(p['correct_display'],p['wrong_display'],p['withheld']) for p in panels],[(25,0,2)]*3)
 def test_no_error_opportunity_and_four_losses_remain_visible(self):
  r=ReviewBudgetStudy().overview()['results'];self.assertTrue(all(not p['choice_gains'] and not p['choice_losses'] and not p['gains'] and not p['control_wrong_displays'] for p in r['paired']))
  self.assertEqual(sum(len(p['losses']) for p in r['paired']),4)
  ps=[p for p in r['panels'] if p['arm']=='knowledge' and p['source_id']=='all' and p['reference_class']=='not_established' and p['assertion_scope']=='all'];self.assertEqual(sum(p['correct_display'] for p in ps),21)
 def test_unknown_claim_withheld_and_reference_hidden(self):
  s=ReviewBudgetStudy();a=s.claim('cf-nov18-2025-c9',1);b=s.claim('cf-nov18-2025-c9',1,True,'knowledge')
  self.assertIsNone(a['reference']);self.assertNotIn('correct_choice',a['outcomes']['knowledge']);self.assertTrue(b['outcomes']['knowledge']['correct_choice']);self.assertTrue(b['outcomes']['knowledge']['withheld']);self.assertTrue(b['outcomes']['literal']['correct_display'])
  if b['exact_input_available']:
   c=s.claim('cf-nov18-2025-c9',1,True,'literal');self.assertEqual(b['request']['state'],c['request']['state'])
 def test_reader_return_preserves_report_claim_and_round(self):
  p='/review-budget?claim=cf-nov18-2025-c9&round=2&input=knowledge';self.assertEqual(return_path(p),p)
  h=render_study(ReviewBudgetStudy(),{'doc':'review-budget','return':p}).decode();self.assertIn('The accepted review budget passes',h);self.assertIn('round=2&amp;input=knowledge',h)
