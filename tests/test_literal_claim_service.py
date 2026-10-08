import unittest
from triage_bench.literal_claim_service import LiteralClaimStudy
from triage_bench.study_page import render_study,return_path

class LiteralServiceTests(unittest.TestCase):
    def test_new_reference_and_old_reference_stay_separate(self):
        s=LiteralClaimStudy();h=s.claim('gh-april-2023-c3');r=s.claim('gh-april-2023-c3',reveal=True)
        self.assertIsNone(h['reference']);self.assertIsNone(h['historical_reference'])
        self.assertEqual(r['reference']['choice'],'contradicted')
        self.assertEqual(r['historical_reference']['choice'],'not_established')
        self.assertTrue(r['outcomes']['literal']['correct_display'])
        self.assertEqual(h['rows'],r['rows'])

    def test_complete_fresh_comparison_and_policy_reclassification(self):
        r=LiteralClaimStudy().overview()['results']
        self.assertEqual(r['actual_calls'],36);self.assertFalse(r['candidate_passes'])
        self.assertEqual(r['historical_reply_reclassification']['new_calls'],0)
        panels=[p for p in r['panels'] if p['arm']=='literal' and p['topic']=='all']
        self.assertEqual(sum(p['correct_display'] for p in panels),12)
        self.assertEqual(sum(p['wrong_display'] for p in panels),0)

    def test_saved_states_stay_identical_when_local_inputs_exist(self):
        s=LiteralClaimStudy();a=s.claim('gh-april-2023-c3',input_arm='legacy');b=s.claim('gh-april-2023-c3',input_arm='literal')
        if a['exact_input_available']:
            self.assertEqual(a['request']['state'],b['request']['state'])
            self.assertNotEqual(a['request']['questions'],b['request']['questions'])
        with self.assertRaises(ValueError):s.claim('gh-april-2023-c3',input_arm='full')

    def test_formatted_article_preserves_selection(self):
        path='/literal-claims?claim=gh-april-2023-c1&round=2&input=literal'
        self.assertEqual(return_path(path),path)
        html=render_study(LiteralClaimStudy(),{'doc':'literal-claims','return':path}).decode()
        self.assertIn('Literal claim definitions reduce',html)
        self.assertIn('round=2&amp;input=literal',html)
