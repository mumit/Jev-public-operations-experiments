import copy,json,unittest
from unittest.mock import patch
from triage_bench import explicit_claim_data as d,explicit_claim_features as old,explicit_format_features as f,explicit_format_trial as t

class ExplicitFormatTests(unittest.TestCase):
    def test_typed_controls_exact_and_preprocessing_disclosed(self):
        for p in d.boundaries():
            self.assertEqual(f.request(p['observation'],p['claim'],'typed'),old.request(p['observation'],p['claim']))
            a=f.request(p['observation'],p['claim'],'focused');b=f.request(p['observation'],p['claim'],'calculated')
            sa=json.loads(a['state']);sb=json.loads(b['state']);computed=sb.pop('calculated_observations');self.assertEqual(sa,sb)
            self.assertFalse({'answer','truth','verdict','asserted','reference'}&set(computed))
            self.assertIn('deterministic preprocessing',b['questions']['claim_verdict']['instructions'])
    def test_computed_facts_are_assertion_independent(self):
        for p in d.boundaries():
            c={**p['claim'],'asserted':not p['claim']['asserted']}
            one=json.loads(f.request(p['observation'],p['claim'],'calculated')['state']);two=json.loads(f.request(p['observation'],c,'calculated')['state'])
            self.assertEqual(one,two)
    def test_direct_negative_comparisons_and_known_zero(self):
        p=d.boundaries()[0];c={**p['claim'],'asserted':False}
        self.assertIn('less than 3.0',f.statement(c));self.assertNotIn('false:',f.statement(c))
        p=next(p for p in d.boundaries() if p['id']=='ECB-spans_zero-0');b=f.request(p['observation'],p['claim'],'calculated')
        self.assertEqual(json.loads(b['state'])['calculated_observations']['minimum_recorded_spans'],0)
        self.assertIn('known count, not missing',b['questions']['claim_verdict']['instructions'])
    def test_invalid_numeric_inputs_do_not_create_computed_numbers(self):
        p=d.boundaries()[0]
        for v in (True,None,'3',float('inf')):
            o=copy.deepcopy(p['observation']);o['metrics']['cpu']['signed_change']=v
            facts=old.facts(o,p['claim']);computed=f.calculated(facts,'metric_material')
            self.assertFalse(computed['observations_eligible']);self.assertIsNone(computed['absolute_scaled_change'])
    def test_planned_calls_have_one_question_and_rotated_arms(self):
        with patch.object(t,'check_plan'):
            jobs=t.requests()
        self.assertEqual(len(jobs),2250);self.assertEqual(len({j['id'] for j in jobs}),2250)
        for arm in f.ARMS:self.assertEqual(sum(j['arm']==arm for j in jobs),750)
        self.assertTrue(all(len(j['body']['questions'])==1 for j in jobs))
        self.assertEqual([j['arm'] for j in jobs[:6]],['typed','focused','calculated','focused','calculated','typed'])
    def test_global_failure_stops_without_retry_or_overwrite(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import Mock
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-key'}
        plan={k:v for k,v in profile.items() if k!='api_key'};jobs=[{'id':str(i),'card_id':'n','arm':'typed','phase':'development','round':1,'body':{'model':t.MODEL,'state':'{}','questions':{}},'request_sha256':str(i)} for i in range(2)]
        opener=Mock();opener.open.side_effect=OSError('fixture failure')
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/'out';protocol=Path(folder)/'protocol';protocol.write_text('{}')
            with patch.object(t,'output',return_value=dest),patch.object(t,'protocol_path',return_value=protocol),patch.object(t,'check',return_value=(plan,jobs)),patch('triage_bench.explicit_format_trial.urllib.request.build_opener',return_value=opener):
                result=t.run('development',profile);self.assertEqual(result['attempted_calls'],1);self.assertEqual(opener.open.call_count,1)
                self.assertNotIn('fixture-key',(dest/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):t.run('development',profile)

if __name__=='__main__':unittest.main()
