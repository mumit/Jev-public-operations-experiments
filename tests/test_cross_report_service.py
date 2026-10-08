import unittest
from triage_bench.cross_report_service import CrossReportStudy
from triage_bench.study_page import render_study,return_path

class CrossServiceTests(unittest.TestCase):
 def test_repeated_error_is_withheld_and_reference_starts_hidden(self):
  s=CrossReportStudy();o=s.overview();self.assertEqual(len(o['claims']),27);self.assertTrue(o['results']['candidate_passes'])
  self.assertEqual(o['results']['actual_calls'],162);self.assertEqual(len(o['results']['gates']),12)
  for n in (1,2,3):
   hidden=s.claim('cf-power-2024-c5',n);shown=s.claim('cf-power-2024-c5',n,reveal=True)
   self.assertIsNone(hidden['reference']);self.assertNotIn('wrong_display',hidden['outcomes']['legacy'])
   self.assertEqual(shown['reference']['choice'],'contradicted');self.assertTrue(shown['outcomes']['legacy']['wrong_display'])
   self.assertTrue(shown['outcomes']['literal']['withheld']);self.assertFalse(shown['outcomes']['literal']['correct_choice'])
   self.assertEqual(hidden['rows'],shown['rows'])
 def test_whole_report_selection_has_no_public_full_source(self):
  s=CrossReportStudy();a=s.claim('cf-dns27-2024-c7',input_arm='legacy');b=s.claim('cf-dns27-2024-c7',input_arm='literal')
  self.assertNotIn('scoped_report',a['claim']);self.assertEqual(a['claim']['retained_blocks'],list(range(75)))
  if a['exact_input_available']:
   self.assertEqual(a['request']['state'],b['request']['state']);self.assertNotEqual(a['request']['questions'],b['request']['questions'])
  with self.assertRaises(ValueError):s.claim('cf-dns27-2024-c7',n=4)
 def test_class_denominators_and_error_opportunity_are_preserved(self):
  r=CrossReportStudy().overview()['results']
  p=[p for p in r['panels'] if p['arm']=='literal' and p['source_id']=='all' and p['reference_class']!='all']
  self.assertEqual(sum(x['claims'] for x in p),81);self.assertEqual(sum(x['correct_display'] for x in p),78)
  self.assertTrue(all(x['comparative_error_opportunity'] for x in r['paired']))
  self.assertTrue(all(not x['gains'] and not x['losses'] for x in r['paired']))
 def test_reader_return_preserves_whole_report_context(self):
  path='/cross-reports?claim=cf-power-2024-c5&round=2&input=literal'
  self.assertEqual(return_path(path),path)
  html=render_study(CrossReportStudy(),{'doc':'cross-reports','return':path}).decode()
  self.assertIn('Whole-report transfer',html);self.assertIn('round=2&amp;input=literal',html)
