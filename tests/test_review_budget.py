import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench import review_budget_data as data,review_budget_trial as trial
from triage_bench.review_budget_scoring import score
from triage_bench.report_knowledge_features import ARMS,request
from tests.test_report_knowledge import response

class ReviewBudgetTests(unittest.TestCase):
 def fixture(self):
  ann=data.load(data.ANNOTATIONS);packets=[{'id':c['id'],'source_id':c['source_id'],'topic':c['topic'],'assertion_scope':c['assertion_scope']} for c in ann['claims']];refs=[{'id':c['id'],'choice':c['choice']} for c in ann['claims']]
  baseline={p['id']:{a:{'valid':True,'choice':None,'displayed':False} for a in ARMS} for p in packets}
  rows=[response(r['id'],a,n,r['choice']) for n in (1,2,3) for r in refs for a in ARMS]
  return packets,refs,baseline,rows
 def withhold(self,rows,ids,arm='knowledge',n=1):
  for i,r in enumerate(rows):
   if r['claim_id'] in ids and r['round']==n and r['arm']==arm:rows[i]=response(r['claim_id'],arm,n,r['answers']['verdict']['choice'],.6)
 def test_integer_budget_accepts_two_reviews_but_rejects_three(self):
  p,r,b,rows=self.fixture();self.withhold(rows,[p[0]['id'],p[1]['id']]);s=score(p,r,rows,True,b);self.assertTrue(s['candidate_passes'])
  self.withhold(rows,[p[2]['id']]);s=score(p,r,rows,True,b);self.assertFalse(s['candidate_passes'])
  gate=next(g for g in s['gates'] if g['source_id']=='all' and g['round']==1)
  self.assertFalse(gate['criteria']['ninety_percent_correct_display_floor']);self.assertFalse(gate['criteria']['ten_percent_review_ceiling'])
 def test_wrong_display_fails_despite_coverage_floor(self):
  p,r,b,rows=self.fixture();i=next(i for i,x in enumerate(rows) if x['arm']=='knowledge');rows[i]=response(rows[i]['claim_id'],'knowledge',1,'not_established')
  s=score(p,r,rows,True,b);self.assertFalse(s['candidate_passes']);g=next(g for g in s['gates'] if g['source_id']=='all' and g['round']==1)
  self.assertTrue(g['criteria']['ninety_percent_correct_display_floor']);self.assertFalse(g['criteria']['no_wrong_displays'])
 def test_display_losses_are_reported_without_old_no_loss_gate(self):
  p,r,b,rows=self.fixture();self.withhold(rows,[p[0]['id']]);s=score(p,r,rows,True,b)
  self.assertTrue(s['candidate_passes']);self.assertEqual(s['paired'][0]['losses'],[p[0]['id']]);self.assertEqual(len(s['gates']),12)
 def test_classes_and_scope_have_balanced_denominators(self):
  p,r,b,rows=self.fixture();s=score(p,r,rows,True,b)
  for scope,count in [('all',27),('incident_fact',18),('report_knowledge',9)]:
   panel=next(x for x in s['panels'] if x['arm']=='knowledge' and x['round']==1 and x['source_id']=='all' and x['reference_class']=='all' and x['assertion_scope']==scope)
   self.assertEqual(panel['claims'],count)
  self.assertEqual(len(s['outcomes']),162)
 def test_missing_or_invalid_control_fails_complete_evidence(self):
  p,r,b,rows=self.fixture();s=score(p,r,[],False,b);self.assertFalse(s['candidate_passes']);self.assertEqual(len(s['outcomes']),162)
  rows=rows[1:];s=score(p,r,rows,True,b);self.assertFalse(s['candidate_passes'])
  with self.assertRaises(ValueError):score(p,r,rows+[rows[0]],True,b)
 def test_new_source_preparation_and_input_allowlist(self):
  with patch.object(data,'committed'),patch.object(data.audit,'committed'):pack=data.prepare()
  self.assertEqual(len(pack['claims']),27);self.assertEqual(len(pack['references']),27);self.assertEqual(pack['independent_reference_reviews'],0)
  packet=dict(pack['claims'][0]);packet.update(report='Full source',scoped_report='Full source',choice='SECRET',rationale='SECRET')
  a=request(packet,'literal');b=request(packet,'knowledge');self.assertEqual(a['state'],b['state']);self.assertNotIn('assertion_scope',json.loads(b['state']));self.assertNotIn('SECRET',b['state'])
 def test_once_only_global_failure_preserves_162_denominator(self):
  profile={'model':'jev-1.13.0','endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-only'}
  job={'id':'fixture','claim_id':'fixture','arm':'literal','round':1,'request_sha256':'fixture','body':{'model':profile['model'],'state':'{}','questions':{}}}
  with tempfile.TemporaryDirectory() as temp:
   protocol=Path(temp)/'protocol.json';protocol.write_text('{}');folder=Path(temp)/'once'
   with patch.object(trial,'PROTOCOL',protocol),patch.object(trial,'LOCAL',folder),patch.object(trial,'check',return_value={'profile':profile}),patch.object(trial,'jobs',return_value=[job]*162),patch('urllib.request.build_opener') as opener:
    opener.return_value.open.side_effect=HTTPError(profile['endpoint'],400,'bad',{},None);s=trial.run(profile)
    self.assertEqual(opener.return_value.open.call_count,1);self.assertEqual(s['unattempted_calls'],161);self.assertNotIn('fixture-only',(folder/'responses.jsonl').read_text())
    with self.assertRaises(FileExistsError):trial.run(profile)
