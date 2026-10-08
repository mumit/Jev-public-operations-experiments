import unittest
from triage_bench.incident_scope_service import IncidentScopeStudy
from triage_bench.study_page import render_study,return_path

class ScopeServiceTests(unittest.TestCase):
    def test_public_overview_keeps_complete_counts(self):
        s=IncidentScopeStudy();overview=s.overview()
        self.assertEqual(overview['results']['actual_calls'],54)
        self.assertFalse(overview['results']['candidate_passes'])
        self.assertEqual(len(overview['claims']),6)
        self.assertEqual(overview['results']['human_entries'],0)

    def test_reveal_preserves_original_answer_and_hides_again(self):
        s=IncidentScopeStudy();hidden=s.claim('gh-april-2023-c3');revealed=s.claim('gh-april-2023-c3',reveal=True)
        self.assertIsNone(hidden['reference']);self.assertNotIn('wrong_display',hidden['outcomes']['selected_section'])
        self.assertEqual(revealed['reference']['choice'],'not_established')
        self.assertTrue(revealed['outcomes']['selected_section']['wrong_display'])
        self.assertEqual(hidden['rows'],revealed['rows'])
        self.assertIsNone(s.claim('gh-april-2023-c3')['reference'])

    def test_local_input_is_explicit_and_matches_frozen_request(self):
        s=IncidentScopeStudy();hidden=s.claim('gh-april-2023-c3');self.assertIsNone(hidden['request'])
        selected=s.claim('gh-april-2023-c3',input_arm='selected_section')
        if selected['exact_input_available']:
            import json
            state=json.loads(selected['request']['state'])
            self.assertEqual(state['claim'],selected['claim']['claim'])
            self.assertEqual(state['selected_incident'],selected['claim']['selected_incident'])
            self.assertEqual(set(state),{'claim','selected_incident','report_excerpt'})

    def test_invalid_selections_do_not_load_a_fallback(self):
        s=IncidentScopeStudy()
        for n in (0,4):
            with self.assertRaises(ValueError):s.claim('gh-april-2023-c3',n)
        with self.assertRaises(ValueError):s.claim('gh-april-2023-c3',input_arm='automatic')
        with self.assertRaises(StopIteration):s.claim('missing')

    def test_formatted_report_preserves_claim_and_round(self):
        path='/incident-scope?claim=gh-april-2023-c3&round=2&input=selected_section'
        self.assertEqual(return_path(path),path)
        html=render_study(IncidentScopeStudy(),{'doc':'incident-scope','return':path}).decode()
        self.assertIn('Explicit incident selection does not improve',html)
        self.assertIn('round=2&amp;input=selected_section',html)
