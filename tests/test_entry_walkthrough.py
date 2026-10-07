import copy,json,unittest
from unittest.mock import patch
from triage_bench import entry_walkthrough as t

class EntryWalkthroughTests(unittest.TestCase):
    def setUp(self):self.pack=t.reconstruct();self.identity={'protocol_sha256':'fixture'}
    def export(self,count=8,mode='participant'):
        rs=[]
        for task,ref in zip(self.pack['tasks'][:count],self.pack['references']):
            rs.append({'id':task['id'],'condition':task['condition'],'fields':copy.deepcopy(ref['fields']),'disposition':'submit','questions':[{'field':k,'at_ms':10} for k in ref['needed']],'elapsed_ms':1000,'foreground_ms':800,'interruptions':0,'usefulness':None,'comment':''})
        return {'schema':'entry-walkthrough-export-1','protocol_sha256':'fixture','pack_sha256':'pack','mode':mode,'session_id':'fixture','records':rs,'provider_calls':0,'server_writes':0,'automatic_field_entries':0}
    def assess(self,e,allow=False):
        with patch.object(t,'verify',return_value=self.identity),patch.object(t,'load',return_value=self.pack),patch.object(t,'sha',return_value='pack'),patch.object(t.Path if hasattr(t,'Path') else type(t.PACK),'read_bytes',return_value=b'fixture'):
            return t.validate_export(e,allow)
    def test_task_selection_is_balanced_and_not_model_filled(self):
        self.assertEqual([p['condition'] for p in self.pack['tasks']],['entry','assisted','assisted','entry','assisted','entry','entry','assisted'])
        for condition in ('entry','assisted'):
            ps=[p for p in self.pack['tasks'] if p['condition']==condition];self.assertEqual(len(ps),4);self.assertEqual(len({p['family'] for p in ps}),4);self.assertEqual(sum(p['dataset']=='Train Ticket' for p in ps),2)
        self.assertTrue(all(p['suggestion'] is None for p in self.pack['tasks'] if p['condition']=='entry'));self.assertEqual(self.pack['provider_calls'],0);self.assertEqual(len(self.pack['practice']),2)
    def test_complete_grounded_entries_and_partial_denominators(self):
        r=self.assess(self.export());self.assertEqual(sum(p['grounded_correct'] for p in r['panels']),8);self.assertTrue(r['complete']);self.assertEqual(r['self_declared_participants'],1)
        r=self.assess(self.export(3));self.assertEqual(r['assigned_tasks'],8);self.assertEqual(r['unrecorded_tasks'],5);self.assertFalse(r['complete'])
    def test_matching_guess_does_not_count_as_grounded(self):
        e=self.export();e['records'][1]['questions']=[];r=self.assess(e);self.assertTrue(r['outcomes'][1]['guessed_match']);self.assertFalse(r['outcomes'][1]['grounded_correct']);self.assertEqual(r['outcomes'][1]['unclarified_fields'],['service'])
    def test_incomplete_withholding_and_unneeded_questions_remain_scored(self):
        e=self.export();e['records'][0]['fields']={k:None for k in t.FIELDS};e['records'][0]['disposition']='withhold';e['records'][0]['questions']=[{'field':'service','at_ms':10}];r=self.assess(e);self.assertTrue(r['outcomes'][0]['withheld']);self.assertEqual(r['outcomes'][0]['unnecessary_questions'],1);self.assertEqual(len(r['outcomes'][0]['missing_fields']),5)
    def test_wrong_valid_fields_differ_from_invalid_catalog(self):
        e=self.export();e['records'][0]['fields']['polarity']='deny';self.assertTrue(self.assess(e)['outcomes'][0]['wrong_entry']);e['records'][0]['fields']['channel']='invented'
        with self.assertRaises(ValueError):self.assess(e)
    def test_preview_does_not_become_human_evidence(self):
        e=self.export(mode='assistant_preview')
        with self.assertRaises(ValueError):self.assess(e)
        self.assertEqual(self.assess(e,True)['self_declared_participants'],0)
    def test_protocol_order_and_automatic_entry_claims_rejected(self):
        for change in ('protocol','order','auto','practice'):
            e=self.export()
            if change=='protocol':e['protocol_sha256']='other'
            elif change=='order':e['records'].reverse()
            elif change=='auto':e['automatic_field_entries']=1
            else:e['records'][0]['id']='PRACTICE-1'
            with self.assertRaises(ValueError):self.assess(e)
    def test_clock_errors_and_bool_timing_rejected(self):
        for value in (True,-1,float('nan'),float('inf')):
            e=self.export();e['records'][0]['foreground_ms']=value
            with self.assertRaises(ValueError):self.assess(e)
        e=self.export();e['records'][0]['questions']=[{'field':'service','at_ms':20000}]
        with self.assertRaises(ValueError):self.assess(e)
if __name__=='__main__':unittest.main()
