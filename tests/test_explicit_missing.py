import unittest
from unittest.mock import patch
from triage_bench import explicit_missing_features as f, explicit_missing_trial as t, explicit_missing_data as d
from triage_bench.explicit_native_v2_features import observations as old
from triage_bench.explicit_claim_features import evaluate
from triage_bench.explicit_format_features import calculated, facts
from triage_bench.explicit_claim_data import entries, references, boundaries

class MissingWindowTests(unittest.TestCase):
    def columns(self):
        return {'time':[1700000000+i for i in range(10)],'emailservice_cpu':[1.]*5+[2.]*5}
    def test_complete_windows_preserve_every_existing_aggregate(self):
        c=self.columns();self.assertEqual(f.observations(c,c['time'][5]),old(c,c['time'][5]))
    def test_absent_after_is_unknown_not_zero_or_full_missing_measurement(self):
        services,windows,counts=f.observations(self.columns(),1700000100)
        v=services['emailservice']['cpu'];self.assertEqual(counts,{'before':10,'after':0})
        self.assertIsNone(windows['after']);self.assertIsNone(v['after_median']);self.assertIsNone(v['after_missing_fraction']);self.assertIsNone(v['signed_change'])
        self.assertIsNotNone(v['before_median'])
        o={'service':'emailservice','metrics':services['emailservice'],'trace':None,'window_seconds':windows}
        rows=entries(o,'fixture','Online Boutique','recording','missing_window')
        self.assertEqual(len(rows),12)
        self.assertTrue(all(r['answer']=='unanswerable' for r in references(rows)))
        self.assertTrue(all(evaluate(o,r['claim'])['answer']=='unanswerable' for r in rows))
        for r in rows[:4]:self.assertFalse(calculated(facts(o,r['claim']),r['claim']['kind'])['observations_eligible'])
    def test_absent_before_and_bad_timeline_are_distinct(self):
        _,windows,counts=f.observations(self.columns(),1699999999)
        self.assertIsNone(windows['before']);self.assertEqual(counts['before'],0)
        for boundary in (True,0,1700000000.5):
            with self.assertRaises(ValueError):f.observations(self.columns(),boundary)
        c=self.columns();c['time'][1]=c['time'][0]
        with self.assertRaises(ValueError):f.observations(c,1700000005)
    def test_answer_metadata_remains_rejected(self):
        c=self.columns();c['emailservice_cause']=c.pop('emailservice_cpu')
        with self.assertRaises(ValueError):f.observations(c,1700000100)
    def test_exact_jobs_preserve_both_unchanged_request_functions(self):
        p=boundaries()[0];p={k:v for k,v in p.items() if k!='fixture_answer'}
        with patch.object(t,'check_plan',return_value={'maximum_calls':6}),patch.object(d,'validate'),patch.object(t,'load',return_value=[p]):jobs=t.requests()
        self.assertEqual(len(jobs),6)
        for j in jobs:self.assertEqual(j['body'],t.request(p['observation'],p['claim'],j['arm']))
    def test_missing_calls_fail_every_separate_scope(self):
        p=boundaries()[0];p={k:v for k,v in p.items() if k!='fixture_answer'};p['category']='complete_windows'
        def load(path):return [p] if path.name=='inputs.json' else [{'id':p['id'],'answer':'supported'}]
        with patch.object(t,'verified_rows',return_value=([],{'attempted_calls':0,'status':'incomplete_or_failed'})),patch.object(t,'load',side_effect=load),patch.object(t,'sha',return_value='fixture'),patch('pathlib.Path.read_bytes',return_value=b'fixture'):
            r=t.score()
        self.assertFalse(r['candidate_passes']);self.assertEqual({v['scope'] for v in r['panels']},{'overall','complete_windows','complete_metrics'})
        self.assertTrue(all(v['claims']==1 and not v['passes'] for v in r['panels']))

if __name__=='__main__':unittest.main()
