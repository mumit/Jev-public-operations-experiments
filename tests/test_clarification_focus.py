import copy,json,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from triage_bench import clarification_features as original,clarification_data as data,clarification_focus_features as f,clarification_focus_trial as t

class FocusTests(unittest.TestCase):
    def test_only_instruction_strings_change_in_both_exact_inputs(self):
        for p in data.reconstruct()[0]:
            before=original.request(p);control=f.request(p,'control');focused=f.request(p,'focused')
            self.assertEqual(before,control);self.assertEqual(before['state'],focused['state'])
            for key in before['questions']:
                a=copy.deepcopy(before['questions'][key]);b=copy.deepcopy(focused['questions'][key]);a.pop('instructions');b.pop('instructions');self.assertEqual(a,b)
            self.assertLess(len(json.dumps(focused)),len(json.dumps(control)))
        with self.assertRaises(ValueError):f.request(p,'other')
    def test_all_statements_and_rounds_have_fresh_paired_controls(self):
        packets=data.reconstruct()[0]
        with patch.object(t,'check_plan',return_value={'maximum_calls':456}),patch.object(data,'validate'),patch.object(t,'load',return_value=packets):jobs=t.requests()
        self.assertEqual(len(jobs),456);self.assertEqual(len({j['id'] for j in jobs}),456)
        for i in range(0,456,2):
            a,b=jobs[i:i+2];self.assertEqual((a['card_id'],a['round']),(b['card_id'],b['round']));self.assertEqual({a['arm'],b['arm']},{'control','focused'})
        self.assertEqual({jobs[i]['arm'] for i in range(0,456,2)},{'control','focused'})
    def test_missing_calls_stay_in_full_arm_and_stratum_denominators(self):
        packets,refs=data.reconstruct()
        with patch.object(t,'verified_rows',return_value=([],{'attempted_calls':0,'status':'incomplete_or_failed'})),patch.object(t,'load',side_effect=[packets,refs]),patch.object(t,'sha',return_value='fixture'),patch.object(Path,'read_bytes',return_value=b''):
            r=t.score()
        self.assertFalse(r['candidate_passes']);self.assertEqual(len(r['outcomes']),684)
        for method in ('control','focused','parser'):
            p=[p for p in r['panels'] if p['method']==method and p['scope']=='overall'];self.assertEqual(sum(v['claims'] for v in p),228)
        self.assertEqual(sum(p['withheld'] for p in r['panels'] if p['method']=='focused' and p['scope']=='overall'),228)
    def test_once_only_runner_stops_on_global_access_failure(self):
        import urllib.error
        jobs=[{'id':'fixture','card_id':'fixture','arm':'control','phase':'development','round':1,'request_sha256':'fixture','body':{'model':t.MODEL}}, {'id':'next','body':{'model':t.MODEL}}]
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-key'}
        with tempfile.TemporaryDirectory() as tmp,patch.object(t,'check',return_value=(profile,jobs)),patch.object(t,'output',return_value=Path(tmp)/'run'),patch.object(t,'protocol_path',return_value=Path(tmp)/'p.json'),patch('urllib.request.OpenerDirector.open',side_effect=urllib.error.HTTPError('fixture',403,'Forbidden',{},None)) as transport:
            (Path(tmp)/'p.json').write_text('{}');r=t.run('development',profile);self.assertEqual(r['attempted_calls'],1);self.assertEqual(r['unattempted_jobs'],1);self.assertEqual(transport.call_count,1)
            with self.assertRaises(FileExistsError):t.run('development',profile)
