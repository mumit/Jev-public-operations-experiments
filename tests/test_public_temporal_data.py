import copy,json,unittest
from triage_bench.public_temporal_data import partition,temporal_body,COUNTS
from triage_bench.public_rca_data import state_from_metrics,FAULTS
from triage_bench.public_format_trial import body

class FreshTemporalDataTests(unittest.TestCase):
    def test_all_correlated_repetitions_stay_in_one_split(self):
        rows=[{'dataset':'RE2-TT','case':f'{s}_{f}_{r}','root_cause_service':s,'fault':f,'repetition':r} for s in ['a','b','c','d','e'] for f in FAULTS for r in (1,2,3)]
        plan=partition(rows);self.assertEqual(len(plan),90)
        for split,n in COUNTS.items():
            selected=[p for p in plan if p['split']==split];self.assertEqual(len(selected),n)
            self.assertEqual({p['group'].split('/')[1] for p in selected},set(FAULTS))
        groups={}
        for p in plan:groups.setdefault(p['group'],set()).add(p['split'])
        self.assertTrue(all(len(s)==1 for s in groups.values()))
        rows[0]['repetition']=2
        with self.assertRaises(ValueError):partition(rows)

    def test_temporal_addition_keeps_named_measurements_question_and_candidates(self):
        columns={'time':[1700000000,1700000001,1700000002],'a_cpu':[1,2,3],'a_latency-50':[1,2,3],'b_latency-90':[2,3,4]}
        state=state_from_metrics(columns,1700000001);saved=copy.deepcopy(state)
        named=body(state,'named');temporal=temporal_body(state,columns,1700000001)
        left=json.loads(named['state']);right=json.loads(temporal['state']);extra=right.pop('latency_time_windows')
        self.assertEqual(left,right);self.assertEqual(state,saved);self.assertEqual(named['questions'],temporal['questions'])
        self.assertEqual(set(extra['series']),{'a_latency-50','b_latency-90'})
        self.assertIsNone(extra['series']['a_latency-50'][1][0])
        self.assertEqual(extra['series']['a_latency-50'][1][3],0)
