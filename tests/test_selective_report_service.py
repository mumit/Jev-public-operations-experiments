import unittest
from triage_bench.selective_report_service import SelectiveReportStudy
from triage_bench.study_page import render_study,return_path

class SelectiveServiceTests(unittest.TestCase):
    def test_hidden_reference_and_complete_new_report_counts(self):
        s=SelectiveReportStudy();o=s.overview();self.assertEqual(len(o['claims']),27)
        self.assertTrue(o['results']['candidate_passes']);self.assertEqual(o['results']['actual_calls'],162)
        self.assertEqual(len(o['results']['gates']),12)
        hidden=s.claim('gh-march-2024-c3');shown=s.claim('gh-march-2024-c3',reveal=True)
        self.assertIsNone(hidden['reference']);self.assertEqual(shown['reference']['choice'],'not_established')
        self.assertTrue(shown['outcomes']['literal']['correct_display']);self.assertFalse(shown['outcomes']['legacy']['correct_display'])
        self.assertNotIn('correct_display',hidden['outcomes']['literal']);self.assertEqual(hidden['rows'],shown['rows'])

    def test_all_classes_and_reports_retained(self):
        result=SelectiveReportStudy().overview()['results']
        panels=[p for p in result['panels'] if p['arm']=='literal' and p['source_id']=='all' and p['reference_class']!='all']
        self.assertEqual(sum(p['claims'] for p in panels),81)
        self.assertTrue(all(p['correct_display']==p['claims']==9 for p in panels))
        self.assertTrue(all(not p['comparative_error_opportunity'] for p in result['paired']))

    def test_exact_state_and_no_public_full_text(self):
        s=SelectiveReportStudy();a=s.claim('gh-february-2024-c8',input_arm='legacy');b=s.claim('gh-february-2024-c8',input_arm='literal')
        self.assertNotIn('scoped_report',a['claim'])
        if a['exact_input_available']:
            self.assertEqual(a['request']['state'],b['request']['state']);self.assertNotEqual(a['request']['questions'],b['request']['questions'])
        with self.assertRaises(ValueError):s.claim('gh-february-2024-c8',n=4)

    def test_formatted_report_preserves_selection(self):
        path='/selective-reports?claim=gh-march-2024-c3&round=2&input=literal'
        self.assertEqual(return_path(path),path)
        html=render_study(SelectiveReportStudy(),{'doc':'selective-reports','return':path}).decode()
        self.assertIn('New reports confirm three-class reading',html);self.assertIn('round=2&amp;input=literal',html)
