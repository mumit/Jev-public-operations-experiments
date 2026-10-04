import unittest
from triage_bench.public_temporal_audit import latency_windows

class TemporalAuditTests(unittest.TestCase):
    def test_baseline_is_fixed_before_boundary_and_bins_use_elapsed_time(self):
        columns={'time':[1700000000+x for x in (0,10,20,30,90,330,751)],'a_latency-50':[1,3,10,12,20,30,40]}
        result=latency_windows(columns,1700000020)['a_latency-50']
        self.assertEqual(result['before_median'],2)
        self.assertEqual([w['rows'] for w in result['windows']],[2,1,1])
        columns['a_latency-50'][-2]=1000
        self.assertEqual(result['baseline_scale'],latency_windows(columns,1700000020)['a_latency-50']['baseline_scale'])

    def test_missing_and_empty_bins_stay_unknown(self):
        columns={'time':[1700000000,1700000001,1700000002],'a_latency-90':[None,None,None]}
        result=latency_windows(columns,1700000001)['a_latency-90']
        self.assertIsNone(result['before_median']);self.assertIsNone(result['baseline_scale'])
        self.assertEqual(result['windows'][0]['missing_fraction'],1)
        self.assertIsNone(result['windows'][1]['missing_fraction'])
        self.assertTrue(all(w['median'] is None and w['signed_change'] is None for w in result['windows']))

    def test_raw_resource_columns_are_not_mislabeled_latency(self):
        columns={'time':[1700000000,1700000001],'a_cpu':[1,2]}
        self.assertEqual(latency_windows(columns,1700000001),{})
        with self.assertRaises(ValueError):latency_windows({'time':[1700000000000,1700000001000]},1700000001000)
        with self.assertRaises(ValueError):latency_windows({'time':[1700000000,1700000001],'a_latency-50':[1]},1700000001)
