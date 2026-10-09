import unittest
from triage_bench.report_knowledge_service import ReportKnowledgeStudy
from triage_bench.study_page import render_study,return_path

class KnowledgeServiceTests(unittest.TestCase):
 def test_failed_gate_and_complete_denominators(self):
  o=ReportKnowledgeStudy().overview();r=o['results']
  self.assertEqual(len(o['claims']),30);self.assertEqual(r['actual_calls'],180)
  self.assertFalse(r['candidate_passes']);self.assertEqual(sum(g['passes'] for g in r['gates']),4)
  self.assertTrue(all(not p['choice_losses'] for p in r['paired']))
  self.assertEqual(sum(len(p['losses']) for p in r['paired']),5)
 def test_target_corrected_and_reference_hidden(self):
  s=ReportKnowledgeStudy()
  for n in (1,2,3):
   a=s.claim('cf-power-2024-c5',n);b=s.claim('cf-power-2024-c5',n,True)
   self.assertIsNone(a['reference']);self.assertNotIn('correct_choice',a['outcomes']['knowledge'])
   self.assertTrue(b['outcomes']['knowledge']['correct_display'])
   self.assertFalse(b['outcomes']['literal']['correct_choice']);self.assertEqual(a['rows'],b['rows'])
 def test_paired_inputs_and_choice_display_loss(self):
  s=ReportKnowledgeStudy();a=s.claim('cf-power-2024-c10',1,True,'literal');b=s.claim('cf-power-2024-c10',1,True,'knowledge')
  self.assertTrue(b['outcomes']['knowledge']['correct_choice']);self.assertTrue(b['outcomes']['knowledge']['withheld'])
  if a['exact_input_available']:
   self.assertEqual(a['request']['state'],b['request']['state']);self.assertNotEqual(a['request']['questions'],b['request']['questions'])
  with self.assertRaises(ValueError):s.claim('cf-power-2024-c5',input_arm='legacy')
 def test_report_preserves_return_context(self):
  p='/report-knowledge?claim=cf-power-2024-c10&round=2&input=knowledge'
  self.assertEqual(return_path(p),p)
  h=render_study(ReportKnowledgeStudy(),{'doc':'report-knowledge','return':p}).decode()
  self.assertIn('Correct interpretation',h);self.assertIn('round=2&amp;input=knowledge',h)
