import unittest
from triage_bench.public_trace_features import uncovered,summarize_rows,augment,trace_ranking

class TraceTests(unittest.TestCase):
    def row(self,span,service,t,duration,parent=None,code=None):return {'traceID':'000123','spanID':span,'parentSpanID':parent,'serviceName':service,'startTime':t,'startTimeMillis':t//1000,'duration':duration,'statusCode':code,'operationName':'secret_fault_label'}
    def test_child_union_clipping(self):
        self.assertEqual(uncovered(100,100,[(80,40),(110,70),(160,80)]),0)
        self.assertEqual(uncovered(100,100,[(110,30),(120,30)]),60)
    def test_dependencies_time_boundaries_coverage_and_metadata_exclusion(self):
        rows=[self.row('root','a',1000000,1000),self.row('child','b',1000100,500,'root',12),self.row('late','b',2000000,100,'absent'),self.row('outside','a',4000000,100)]
        r=summarize_rows(rows,2,1,2,['a','b','c'])
        self.assertEqual(r['dependencies'],[['a','b',1,0]]);self.assertEqual(r['coverage']['after']['unresolved_parent_spans'],1)
        self.assertEqual(r['services']['a']['before']['uncovered_duration_median_us'],500)
        self.assertEqual(r['services']['b']['before']['status_code_counts'],{'12':1});self.assertEqual(r['services']['b']['after']['status_missing_fraction'],1)
        self.assertEqual(r['candidates_without_spans'],['c']);self.assertEqual(r['outside_interval_spans'],1)
        self.assertNotIn('secret_fault_label',str(r));self.assertNotIn('000123',str(r));self.assertIsNone(r['services']['a']['after']['duration_median_us'])
    def test_duplicate_cycles_and_bad_units_stop(self):
        a=self.row('a','a',1000000,10,'b');b=self.row('b','b',1000000,10,'a')
        for rows in ([a,a],[a,b],[{**a,'parentSpanID':None,'startTimeMillis':1}]):
            with self.assertRaises(ValueError):summarize_rows(rows,2,1,2,['a','b'])
    def test_augmentation_preserves_control_and_unknown_mapping(self):
        state={'services':{'a':{'cpu':[1,2,3,0,0]}}};context=summarize_rows([self.row('s','unmapped',1000000,10)],2,1,2,['a'])
        enriched=augment(state,context);self.assertEqual({k:v for k,v in enriched.items() if k!='trace_context'},state)
        self.assertNotIn('trace_context',state);self.assertEqual(context['unmapped_trace_services'],{'unmapped':1})
        self.assertEqual(trace_ranking(context,['a'])['choice'],'insufficient_evidence')
