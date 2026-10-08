import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench.literal_claim_features import request,ARMS
from triage_bench.incident_scope_features import request as scope_request
from triage_bench import literal_claim_data as data
from triage_bench import literal_claim_trial as trial
from triage_bench.literal_claim_scoring import score
from triage_bench.hosted import encoded
from tests.test_incident_scope import response

class LiteralClaimTests(unittest.TestCase):
    def fixture(self):
        packets=[{'id':'gh-april-2023-c'+str(i),'topic':('service_impact','cause_certainty','recovery_scope')[(i-1)//2]} for i in range(1,7)]
        refs=[{'id':p['id'],'choice':'supported' if p['id'].endswith(('1','4','6')) else 'contradicted'} for p in packets]
        baseline={p['id']:{a:{'choice':None,'valid':True,'displayed':False} for a in ARMS} for p in packets}
        return packets,refs,baseline

    def test_state_and_legacy_request_stay_exact(self):
        packet={'report':'Original full source','scoped_report':'Original selected section','claim':'Unchanged claim','selected_incident':'Explicit header'}
        old=scope_request(packet,'selected_section');legacy=request(packet,'legacy');literal=request(packet,'literal')
        self.assertEqual(encoded(old),encoded(legacy));self.assertEqual(legacy['state'],literal['state'])
        self.assertEqual(legacy['model'],literal['model']);self.assertEqual(set(literal['questions']['verdict']['criteria']),{'supported','contradicted','not_established'})
        self.assertIn('exact proposition',literal['questions']['verdict']['criteria']['not_established'])
        self.assertNotEqual(legacy['questions'],literal['questions'])

    def test_new_reference_version_changes_one_choice_only(self):
        result=data.prepare();_,old=data.scope.packets(local=False);before={r['id']:r for r in old}
        changed=[r['id'] for r in result['references'] if r['choice']!=before[r['id']]['choice']]
        self.assertEqual(changed,['gh-april-2023-c3'])
        for r in result['references']:
            self.assertEqual(r['evidence_spans'],before[r['id']]['evidence_spans'])
            if r['id']!='gh-april-2023-c3':self.assertEqual(r,before[r['id']])
        self.assertEqual(result['reference_classes'],['supported','contradicted'])
        self.assertEqual(result['human_entries'],0)

    def test_absent_replies_keep_all_36_opportunities(self):
        p,r,b=self.fixture();s=score(p,r,[],False,b)
        self.assertEqual(len(s['outcomes']),36);self.assertFalse(s['candidate_passes'])
        self.assertTrue(all(o['withheld'] for o in s['outcomes']))

    def test_one_wrong_display_or_correct_loss_fails(self):
        p,r,b=self.fixture();rows=[response(x['id'],a,n,x['choice']) for n in (1,2,3) for x in r for a in ARMS]
        self.assertTrue(score(p,r,rows,True,b)['candidate_passes'])
        changed=[response(o['claim_id'],o['arm'],o['round'],'not_established') if o['arm']=='literal' and o['claim_id'].endswith('3') and o['round']==2 else o for o in rows]
        self.assertFalse(score(p,r,changed,True,b)['candidate_passes'])
        with self.assertRaises(ValueError):score(p,r,rows+[rows[0]],True,b)

    def test_completed_protocol_cannot_retry_http_failure(self):
        profile={'model':'jev-1.13.0','endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-only'}
        job={'id':'fixture','claim_id':'fixture','arm':'legacy','round':1,'request_sha256':'fixture','body':{'model':profile['model'],'state':'{}','questions':{}}}
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'once';protocol=Path(temp)/'protocol.json';protocol.write_text('{}')
            with patch.object(trial,'PROTOCOL',protocol),patch.object(trial,'LOCAL',folder),patch.object(trial,'check',return_value={'profile':profile}),patch.object(trial,'jobs',return_value=[job]*36),patch('urllib.request.build_opener') as opener:
                opener.return_value.open.side_effect=HTTPError(profile['endpoint'],400,'bad',{},None)
                result=trial.run(profile)
                self.assertEqual(opener.return_value.open.call_count,1);self.assertEqual(result['unattempted_calls'],35)
                self.assertNotIn('fixture-only',(folder/'responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):trial.run(profile)
