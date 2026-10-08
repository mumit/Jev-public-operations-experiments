import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench import selective_report_data as data
from triage_bench import selective_report_trial as trial
from triage_bench.selective_report_scoring import score
from triage_bench.literal_claim_features import request,ARMS
from tests.test_incident_scope import response

class SelectiveReportTests(unittest.TestCase):
    def fixture(self):
        packets=[{'id':s+'-'+str(i),'source_id':s,'topic':data.TOPICS[i//3]} for s in ('jan','feb','mar') for i in range(9)]
        refs=[{'id':p['id'],'choice':data.CHOICES[int(p['id'].rsplit('-',1)[1])%3]} for p in packets]
        baseline={p['id']:{a:{'valid':True,'choice':None,'displayed':False} for a in ARMS} for p in packets}
        return packets,refs,baseline

    def test_preparation_preserves_all_sources_and_uses_count_mapping(self):
        inventory=data.load(data.audit.AUDIT)
        with tempfile.TemporaryDirectory() as temp:
            cache=Path(temp)
            for source in inventory['sources']:
                (cache/(source['id']+'.json')).write_text(json.dumps({'blocks':[{'text':'Fixture block '+str(i)} for i in range(source['blocks'])]}))
            with patch.object(data,'committed'),patch.object(data.audit,'verify',return_value=inventory),patch.object(data.audit,'CACHE',cache):
                pack=data.prepare()
        self.assertEqual(len(pack['claims']),27)
        for source,expected in (('gh-january-2024',3),('gh-february-2024',1),('gh-march-2024',2)):
            claims=[p for p in pack['claims'] if p['source_id']==source]
            self.assertEqual(len({p['selected_section_id'] for p in claims}),expected)
            self.assertEqual(len(claims),9)
        self.assertEqual(pack['independent_reference_reviews'],0)
        jan=next(p for p in pack['claims'] if p['id']=='gh-january-2024-c1')
        self.assertEqual(jan['retained_blocks'],[0,1,2,3])

    def test_allowlist_and_questions_reuse_exact_frozen_producer(self):
        p={'report':'Whole source','scoped_report':'Whole selected section','claim':'Claim text','selected_incident':'Explicit header','choice':'SECRET','rationale':'SECRET','id':'SECRET'}
        a,b=request(p,'legacy'),request(p,'literal')
        self.assertEqual(a['state'],b['state']);self.assertNotIn('SECRET',a['state'])
        self.assertEqual(set(json.loads(a['state'])),{'report_excerpt','claim','selected_incident'})

    def test_all_denominators_survive_missing_rows(self):
        p,r,b=self.fixture();result=score(p,r,[],False,b)
        self.assertEqual(len(result['outcomes']),162);self.assertEqual(len(result['gates']),12)
        self.assertFalse(result['candidate_passes']);self.assertTrue(all(o['withheld'] for o in result['outcomes']))

    def test_class_coverage_and_paired_losses_are_required(self):
        p,r,b=self.fixture();rows=[response(x['id'],a,n,x['choice']) for n in (1,2,3) for x in r for a in ARMS]
        self.assertTrue(score(p,r,rows,True,b)['candidate_passes'])
        # Withhold all unknowns in one source/round: six correct displays still fail class coverage.
        changed=[{**x,'status':'ok','answers':{'verdict':{'choice':'supported','probabilities':{'supported':.5,'contradicted':.25,'not_established':.25}}}} if x['arm']=='literal' and x['round']==2 and x['claim_id'].startswith('feb-') and x['claim_id'].endswith(('2','5','8')) else x for x in rows]
        result=score(p,r,changed,True,b)
        gate=next(g for g in result['gates'] if g['source_id']=='feb' and g['round']==2)
        self.assertTrue(gate['criteria']['at_least_six_correct_displays'])
        self.assertFalse(gate['criteria']['all_three_classes_correctly_displayed']);self.assertFalse(gate['criteria']['no_correct_display_losses'])
        with self.assertRaises(ValueError):score(p,r,rows+[rows[0]],True,b)

    def test_wrong_display_in_any_report_prevents_aggregate_pass(self):
        p,r,b=self.fixture();rows=[response(x['id'],a,n,x['choice']) for n in (1,2,3) for x in r for a in ARMS]
        rows[1]=response(rows[1]['claim_id'],'literal',1,'contradicted')
        self.assertFalse(score(p,r,rows,True,b)['candidate_passes'])

    def test_provider_failure_stops_once_and_cannot_resume(self):
        profile={'model':'jev-1.13.0','endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-only'}
        job={'id':'fixture','claim_id':'fixture','arm':'legacy','round':1,'request_sha256':'fixture','body':{'model':profile['model'],'state':'{}','questions':{}}}
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'once';protocol=Path(temp)/'protocol.json';protocol.write_text('{}')
            with patch.object(trial,'PROTOCOL',protocol),patch.object(trial,'LOCAL',folder),patch.object(trial,'check',return_value={'profile':profile}),patch.object(trial,'jobs',return_value=[job]*162),patch('urllib.request.build_opener') as opener:
                opener.return_value.open.side_effect=HTTPError(profile['endpoint'],400,'bad',{},None)
                result=trial.run(profile);self.assertEqual(opener.return_value.open.call_count,1)
                self.assertEqual(result['unattempted_calls'],161)
                self.assertNotIn('fixture-only',(folder/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):trial.run(profile)
