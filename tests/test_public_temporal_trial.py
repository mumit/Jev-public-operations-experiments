import unittest
from triage_bench.public_temporal_trial import shortlist

class ShortlistTests(unittest.TestCase):
    def test_shortlist_keeps_selected_tied_winner_and_excludes_zero_candidates(self):
        row={'status':'ok','choice':'z','probabilities':{'a':.4,'z':.4,'b':.1,'c':.1,'zero':0,'insufficient_evidence':0}}
        self.assertEqual(shortlist(row),['z','a','b'])
        self.assertEqual(row['choice'],'z')
        row['probabilities']={'z':1,'zero':0,'insufficient_evidence':0}
        self.assertEqual(shortlist(row),['z'])

    def test_insufficient_evidence_failed_and_missing_responses_withhold_leads(self):
        self.assertEqual(shortlist(None),[])
        self.assertEqual(shortlist({'status':'error'}),[])
        self.assertEqual(shortlist({'status':'ok','choice':'insufficient_evidence','probabilities':{'a':.3,'b':.3,'insufficient_evidence':.4}}),[])
