import copy,unittest
from unittest.mock import patch
from triage_bench.explicit_native_features import observations
from triage_bench import explicit_native_data as d,explicit_native_trial as t,explicit_claim_data as original
from triage_bench.public_rca_data import state_from_metrics

class ExplicitNativeTests(unittest.TestCase):
    def setUp(self):self.time=[1700000000+i for i in range(10)];self.columns={'time':self.time,'PassthroughCluster_load':[1.]*5+[2.]*5,'emailservice_latency':[100.]*5+[125.]*5,'emailservice_cpu':[10.]*5+[9.]*5}
    def test_native_names_preserved_with_no_workload_or_percentile_alias(self):
        services,windows,counts=observations(self.columns,self.time[5]);self.assertIn('load',services['PassthroughCluster']);self.assertIn('latency',services['emailservice']);self.assertNotIn('workload',services['PassthroughCluster']);self.assertNotIn('latency-50',services['emailservice']);self.assertEqual(counts,{'before':5,'after':5});self.assertEqual(windows,{'before':5,'after':5})
    def test_common_channel_formula_matches_frozen_adapter(self):
        for values in ([1.,2.,3.,4.,5.,3.,4.,5.,6.,7.],[None,2.,3.,None,5.,None,None,5.,6.,7.],[0.]*5+[0.]*5):
            cols={'time':self.time,'emailservice_cpu':values};old=state_from_metrics(cols,self.time[5]);new,_,_=observations(cols,self.time[5]);self.assertEqual(new['emailservice']['cpu'],dict(zip(old['columns'],old['services']['emailservice']['cpu'])))
    def test_unknown_metadata_and_invalid_timeline_rejected(self):
        for change in ({'emailservice_rootcause':[1]*10},{'cause':['emailservice']*10},{'emailservice_latency-50':[1]*10},{'emailservice_cpu':[1]*9}):
            with self.assertRaises(ValueError):observations({**self.columns,**change},self.time[5])
        bad=copy.deepcopy(self.columns);bad['time'][1]=bad['time'][0]
        with self.assertRaises(ValueError):observations(bad,self.time[5])
    def test_missingness_keeps_unknown_not_zero(self):
        cols={'time':self.time,'emailservice_load':[None]*10};services,_,_=observations(cols,self.time[5]);m=services['emailservice']['load'];self.assertIsNone(m['signed_change']);self.assertIsNone(m['before_median']);self.assertEqual(m['before_missing_fraction'],1.)
    def test_groups_disjoint_from_failed_and_sealed_original(self):
        rows=d.allocation();previous=d.failed.allocation()+original.allocation();self.assertEqual(len(rows),15);self.assertFalse({r['source_case'] for r in rows}&{r['source_case'] for r in previous});self.assertEqual(len({r['group'] for r in rows}),3)
    def test_candidate_functions_unchanged_in_new_confirmation(self):
        p=original.boundaries()[0];p={k:v for k,v in p.items() if k!='fixture_answer'}
        with patch.object(t,'check_plan',return_value={'maximum_calls':6}),patch.object(d,'validate'),patch.object(t,'load',return_value=[p]):jobs=t.requests()
        for j in jobs:self.assertEqual(j['body'],t.prior.request(p['observation'],p['claim'],j['arm']))

if __name__=='__main__':unittest.main()
