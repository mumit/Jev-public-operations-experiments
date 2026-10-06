import copy,json,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from triage_bench import clarification_features as f,clarification_data as d,clarification_trial as t

class ClarificationTests(unittest.TestCase):
    def clear(self):return {'scope':'metric_check',**{k:'clear' for k in f.PRIORITY}}
    def row(self,labels,score=.95):
        return {'status':'ok','quarantined_sentences':[],'answers':{'claim_'+k:{'choice':v,'probabilities':{v:score}} for k,v in labels.items()}}
    def test_reference_counts_and_multi_issue_priority_are_hand_declared(self):
        packets,refs=d.reconstruct();self.assertEqual(len(packets),76);self.assertEqual(len({p['family'] for p in packets}),19)
        self.assertTrue(all(len([p for p in packets if p['family']==fam])==4 for fam in {p['family'] for p in packets}))
        i=next(i for i,p in enumerate(packets) if p['family']=='several_missing')
        self.assertEqual(refs[i]['decision']['needed'],['service','kind','polarity','window']);self.assertEqual(refs[i]['decision']['next_field'],'service')
    def test_request_allowlist_excludes_reference_and_measurements(self):
        p=d.reconstruct()[0][0];one=f.request(p);two=f.request({**p,'reference':'outside_scope','measurements':{'cpu':42},'family':'changed'})
        self.assertEqual(one,two);self.assertEqual(set(json.loads(one['state'])),{'analyst_statement','observed_services','channel_aliases','available_comparison'})
        self.assertEqual(len(one['questions']),6);self.assertNotIn(p['id'],json.dumps(one))
    def test_all_missing_fields_remain_visible_while_code_asks_one(self):
        labels={**self.clear(),'channel':'clarify','window':'clarify'};r=f.compose(labels)
        self.assertEqual(r['needed'],['channel','window']);self.assertEqual(r['next_field'],'channel');self.assertEqual(r['question'],f.QUESTION['channel'])
    def test_scope_and_invalid_field_combinations_go_to_review_without_repair(self):
        outside={'scope':'outside_scope',**{k:'not_applicable' for k in f.PRIORITY}}
        self.assertEqual(f.compose(outside)['action'],'outside_scope')
        self.assertEqual(f.compose({**outside,'service':'clear'})['action'],'review');self.assertEqual(f.compose({**self.clear(),'window':'not_applicable'})['action'],'review')
    def test_low_score_and_quarantine_preserve_raw_classification(self):
        row=self.row(self.clear(),.69);original=copy.deepcopy(row);r=f.decision(row)
        self.assertFalse(r['displayed']);self.assertEqual(r['action'],'review');self.assertEqual(r['classified_decision']['action'],'ready');self.assertEqual(row,original)
        row['quarantined_sentences']=['claim'];self.assertIsNone(f.decision(row)['labels'])
        row=self.row(self.clear(),.7);self.assertTrue(f.decision(row)['displayed'])
    def test_scoring_distinguishes_premature_ready_unnecessary_questions_and_withholding(self):
        ref={'labels':{**self.clear(),'service':'clarify'},'decision':f.compose({**self.clear(),'service':'clarify'})}
        r=t.assessment(f.decision(self.row(self.clear())),ref);self.assertTrue(r['premature_ready']);self.assertFalse(r['workflow_correct'])
        bad={**self.clear(),'window':'clarify'};r=t.assessment(f.decision(self.row(bad)),ref);self.assertTrue(r['unnecessary_question']);self.assertEqual(r['missing_needed_fields'],1)
        ref={'labels':self.clear(),'decision':f.compose(self.clear())};r=t.assessment(f.decision(self.row(self.clear(),.69)),ref)
        self.assertTrue(r['workflow_correct']);self.assertFalse(r['correct_display']);self.assertTrue(r['withheld'])
    def test_parser_uses_text_inventory_and_no_reference_metadata(self):
        p=d.reconstruct()[0][0];self.assertEqual(f.parser(p),f.parser({**p,'family':'other','reference':self.clear()}))
        p={**p,'text':'The backend caused the incident.'};self.assertEqual(f.compose(f.parser(p))['action'],'outside_scope')
    def test_once_only_runner_stops_on_global_failure_and_keeps_budget(self):
        job={'id':'fixture','card_id':'fixture','phase':'development','round':1,'request_sha256':'fixture','body':{'model':t.MODEL,'questions':{'claim_scope':{'criteria':{'metric_check':'ok'}}}}}
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-key'}
        import urllib.error
        with tempfile.TemporaryDirectory() as tmp,patch.object(t,'check',return_value=({'model':t.MODEL,'endpoint':profile['endpoint'],'context_tokens':32768},[job,{**job,'id':'next'}])),patch.object(t,'output',return_value=Path(tmp)/'run'),patch.object(t,'protocol_path',return_value=Path(tmp)/'p.json'),patch('urllib.request.OpenerDirector.open',side_effect=urllib.error.HTTPError('fixture',403,'Forbidden',{},None)) as transport:
            (Path(tmp)/'p.json').write_text('{}');r=t.run('development',profile)
            self.assertEqual(r['attempted_calls'],1);self.assertEqual(r['unattempted_jobs'],1);self.assertEqual(transport.call_count,1)
            with self.assertRaises(FileExistsError):t.run('development',profile)

if __name__=='__main__':unittest.main()
