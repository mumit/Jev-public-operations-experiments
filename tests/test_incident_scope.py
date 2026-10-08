import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench.incident_scope_features import select,request,ARMS
from triage_bench.incident_scope_scoring import score
from triage_bench import incident_scope_data as data
from triage_bench import incident_scope_trial as trial
from triage_bench.publisher_report_features import request as original
from triage_bench.hosted import encoded

def response(i,arm,n,choice):
    probabilities={x:0.05 for x in ('supported','contradicted','not_established')};probabilities[choice]=0.9
    return {'claim_id':i,'arm':arm,'round':n,'status':'ok','answers':{'verdict':{'choice':choice,'probabilities':probabilities}}}

class IncidentScopeTests(unittest.TestCase):
    def test_selection_has_no_default_or_inference(self):
        blocks=[{'text':'Introduction'},{'text':'March 29 incident'},{'text':'Earlier recovery, then degradation.'},{'text':'March 31 incident'},{'text':'Different users.'}]
        inventory=[{'id':'one','start':1,'end':3,'label':'March 29'},{'id':'two','start':3,'end':5,'label':'March 31'}]
        for value in (None,'',[],['one','two'],'March 29','unknown'):
            with self.assertRaises(ValueError):select(blocks,inventory,value)
        section,indices,text=select(blocks,inventory,'one')
        self.assertEqual(indices,[0,1,2]);self.assertEqual(text,'Introduction\n\nMarch 29 incident\n\nEarlier recovery, then degradation.')
        self.assertNotIn('Different users',text)

    def test_only_state_changes_with_selection(self):
        packet={'report':'Entire original report','scoped_report':'Introduction and whole section','claim':'Unchanged claim','selected_incident':'March 29'}
        self.assertEqual(encoded(request(packet,'full')),encoded(original(packet)))
        bound=request(packet,'selected_full');scoped=request(packet,'selected_section')
        self.assertEqual(bound['questions'],scoped['questions']);self.assertEqual(bound['questions'],original(packet)['questions'])
        self.assertEqual(json.loads(bound['state']),{'claim':'Unchanged claim','report_excerpt':'Entire original report','selected_incident':'March 29'})
        self.assertEqual(json.loads(scoped['state'])['report_excerpt'],'Introduction and whole section')
        self.assertNotIn('reference',scoped['state'])
        with self.assertRaises(ValueError):request({**packet,'selected_incident':''},'selected_section')

    def fixture(self):
        packets=[{'id':'gh-april-2023-c'+str(n),'topic':('service_impact','cause_certainty','recovery_scope')[(n-1)//2]} for n in range(1,7)]
        refs=[{'id':p['id'],'choice':'supported' if p['id'].endswith('1') else 'contradicted'} for p in packets]
        baseline={p['id']:{a:{'valid':True,'choice':None,'displayed':False,'reason':'no_literal_match'} for a in ARMS} for p in packets}
        return packets,refs,baseline

    def test_missing_answers_keep_every_denominator(self):
        packets,refs,baseline=self.fixture();r=score(packets,refs,[],False,baseline)
        self.assertEqual(len(r['outcomes']),54);self.assertTrue(all(o['withheld'] for o in r['outcomes']))
        self.assertFalse(r['candidate_passes'])
        self.assertTrue(all(p['claims']==6 for p in r['panels'] if p['topic']=='all'))

    def test_comparator_cannot_replace_failed_candidate(self):
        packets,refs,baseline=self.fixture();rows=[]
        for n in (1,2,3):
            for r in refs:
                for arm in ARMS:
                    choice='not_established' if arm=='selected_section' else r['choice']
                    rows.append(response(r['id'],arm,n,choice))
        r=score(packets,refs,rows,True,baseline)
        self.assertFalse(r['candidate_passes']);self.assertEqual(r['candidate'],'selected_section')
        with self.assertRaises(ValueError):score(packets,refs,rows+[rows[0]],True,baseline)

    def test_wrong_display_and_correct_loss_fail_independently(self):
        packets,refs,baseline=self.fixture();rows=[response(r['id'],a,n,r['choice']) for n in (1,2,3) for r in refs for a in ARMS]
        self.assertTrue(score(packets,refs,rows,True,baseline)['candidate_passes'])
        changed=[response(r['claim_id'],r['arm'],r['round'],'not_established') if r['arm']=='selected_section' and r['claim_id'].endswith('6') and r['round']==2 else r for r in rows]
        result=score(packets,refs,changed,True,baseline)
        self.assertFalse(result['gates'][1]['criteria']['no_correct_display_losses'])
        self.assertFalse(result['gates'][1]['criteria']['no_wrong_display'])
        self.assertFalse(result['candidate_passes'])

    def test_recorded_source_selection_preserves_all_evidence(self):
        if not data.old.audit.CACHE.exists():return
        prepared=data.prepare()
        self.assertEqual(len(prepared['fixtures']),6);self.assertEqual(len(prepared['inventory']),7)
        first=prepared['fixtures'][0]
        self.assertEqual(first['retained_blocks'],[0,10,11,12,13]);self.assertEqual(first['scoped_bytes'],1125)
        self.assertEqual(prepared['human_entries'],0)

    def test_global_http_error_stops_without_retry(self):
        profile={'model':'jev-1.13.0','endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-only'}
        job={'id':'fixture','claim_id':'fixture','arm':'full','round':1,'request_sha256':'fixture','body':{'model':profile['model'],'state':'{}','questions':{}}}
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'once'
            protocol=Path(temp)/'protocol.json';protocol.write_text('{}')
            with patch.object(trial,'PROTOCOL',protocol),patch.object(trial,'LOCAL',folder),patch.object(trial,'check',return_value={'profile':profile}),patch.object(trial,'jobs',return_value=[job]*54),patch('urllib.request.build_opener') as opener:
                opener.return_value.open.side_effect=HTTPError(profile['endpoint'],400,'bad',{},None)
                result=trial.run(profile)
                self.assertEqual(opener.return_value.open.call_count,1)
                self.assertEqual(result['unattempted_calls'],53)
                self.assertNotIn('fixture-only',(folder/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):trial.run(profile)
