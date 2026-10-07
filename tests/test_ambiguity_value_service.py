import json,unittest
from unittest.mock import patch
from triage_bench.ambiguity_value_service import AmbiguityValueStudy
from triage_bench import ambiguity_value_trial as t

class ValueServiceTests(unittest.TestCase):
 def setUp(self):
  self.service=AmbiguityValueStudy();ps,refs=t.data.reconstruct();out=t.score_rows(ps,refs,[],False);self.data=(out|{'actual_calls':0,'valid_answers':0,'input_tokens':0,'summed_latency_ms':0},ps,refs,[],[{'card_id':p['id'],'round':n,'body':{'state':p['text']},'request_sha256':'fixture'} for p in ps for n in (1,2,3)])
 def test_hidden_reference_and_exact_three_rounds(self):
  with patch.object(self.service,'verified',return_value=self.data):
   a=self.service.card(self.data[1][0]['id']);self.assertIsNone(a['reference']);self.assertEqual(len(a['rounds']),3);self.assertTrue(all(r['outcomes'] is None for r in a['rounds']));self.assertTrue(all(r['row'] is None for r in a['rounds']))
   b=self.service.card(self.data[1][0]['id'],True);self.assertIsNotNone(b['reference']);self.assertTrue(all(r['outcomes'] is not None for r in b['rounds']))
 def test_bad_card_fails_and_overview_denominators_remain(self):
  with patch.object(self.service,'verified',return_value=self.data):
   with self.assertRaises(ValueError):self.service.card('invented')
   a=self.service.overview();self.assertEqual(a['totals']['jev']['opportunities'],144);self.assertEqual(a['totals']['jev']['correct_display'],0);self.assertFalse(a['candidate_passes']);self.assertEqual(a['provider_calls_on_page'],0)
 def test_real_evidence_drift_is_detected(self):
  # One verified cache entry cannot mask a changed checkpoint signature.
  p=t.result_path();raw=p.read_text();self.service.cache=(('stale',),None,None,None,None,None)
  with patch.object(t,'verify',side_effect=ValueError('Changed assessment')):
   with self.assertRaises(ValueError):self.service.verified()
  self.assertEqual(p.read_text(),raw)
if __name__=='__main__':unittest.main()
