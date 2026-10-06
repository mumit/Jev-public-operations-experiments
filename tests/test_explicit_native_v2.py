import unittest
from triage_bench.explicit_native_v2_features import observations,CHANNELS
from triage_bench import explicit_native_v2_data as d
from triage_bench.public_data import METRICS

class NativeV2Tests(unittest.TestCase):
    def test_allowlist_union_and_native_names_not_aliases(self):
        self.assertEqual(set(CHANNELS),set(METRICS)|{'load','latency'})
        times=[1700000000+i for i in range(10)];cols={'time':times,**{'emailservice_'+m:[1.]*5+[2.]*5 for m in CHANNELS}}
        services,_,_=observations(cols,times[5]);self.assertEqual(set(services['emailservice']),set(CHANNELS))
        for metric in CHANNELS:self.assertEqual(services['emailservice'][metric]['signed_change'],100.)
    def test_unknown_answer_metadata_still_rejected(self):
        times=[1700000000+i for i in range(10)]
        with self.assertRaises(ValueError):observations({'time':times,'emailservice_cause':[1.]*10},times[5])
    def test_fresh_allocation_excludes_both_failed_panels_and_original_panel(self):
        rows=d.allocation();seen=d.original.allocation()+d.failed.allocation()+d.failed.failed.allocation()
        self.assertEqual(len(rows),15);self.assertFalse({r['source_case'] for r in rows}&{r['source_case'] for r in seen})

if __name__=='__main__':unittest.main()
