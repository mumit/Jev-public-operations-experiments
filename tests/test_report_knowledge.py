import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench import report_knowledge_data as data,report_knowledge_trial as trial
from triage_bench.report_knowledge_features import request,ARMS
from triage_bench.literal_claim_features import request as original
from triage_bench.report_knowledge_scoring import score,TARGET,COMPANIONS
from tests.test_incident_scope import response as frozen_response

def response(i,arm,n,choice,probability=.9):
 row=frozen_response(i,arm,n,choice)
 row['answers']['verdict']['probabilities']={c:probability if c==choice else (1-probability)/2 for c in data.CHOICES}
 return row

class KnowledgeTests(unittest.TestCase):
 def fixture(self):
  old=data.load(data.old.PACK);cs=data.load(data.ANNOTATIONS)['claims'];packets=list(old['claims']);refs=list(old['references'])
  for c in cs:
   packets.append({'id':c['id'],'source_id':c['source_id'],'topic':c['topic']});refs.append({'id':c['id'],'choice':c['choice']})
  baseline={p['id']:{a:{'valid':True,'choice':None,'displayed':False} for a in ARMS} for p in packets}
  rows=[response(r['id'],a,n,'not_established' if a=='literal' and r['id']==TARGET else r['choice']) for n in (1,2,3) for r in refs for a in ARMS]
  return packets,refs,baseline,rows
 def test_control_bytes_and_state_are_unchanged_without_answer_hints(self):
  p={'report':'Full source with unknown facts.','scoped_report':'Full source with unknown facts.','claim':'An exact claim.','selected_incident':'Title','scope':'SECRET','choice':'SECRET','rationale':'SECRET'}
  a=request(p,'literal');b=request(p,'knowledge');self.assertEqual(a,original(p,'literal'));self.assertEqual(a['state'],b['state']);self.assertNotIn('SECRET',b['state'])
  self.assertEqual(set(a),set(b));self.assertEqual(set(a['questions']),set(b['questions']));self.assertEqual(set(a['questions']['verdict']['criteria']),set(b['questions']['verdict']['criteria']))
  self.assertEqual(set(json.loads(a['state'])),{'claim','report_excerpt','selected_incident'});self.assertNotEqual(a['questions'],b['questions'])
 def test_preparation_preserves_every_old_reference_and_source(self):
  old=data.load(data.old.PACK)
  with tempfile.TemporaryDirectory() as temp:
   cache=Path(temp);(cache/'cf-power-2024.json').write_text(json.dumps({'blocks':[{'text':'Fixture block '+str(i)} for i in range(49)]}))
   with patch.object(data,'committed'),patch.object(data.old,'packets',return_value=(old['claims'],old['references'])),patch.object(data.old.audit,'CACHE',cache):r=data.prepare()
  self.assertEqual(r['claims'][:27],old['claims']);self.assertEqual(r['references'][:27],old['references']);self.assertEqual(len(r['claims']),30);self.assertEqual(r['independent_reference_reviews'],0)
 def test_companion_classes_must_remain_distinct(self):
  old=data.load(data.old.PACK);annotations=data.load(data.ANNOTATIONS);annotations['claims'][0]['choice']='supported';real=data.load
  with patch.object(data,'committed'),patch.object(data.old,'packets',return_value=(old['claims'],old['references'])),patch.object(data,'load',side_effect=lambda p:annotations if p==data.ANNOTATIONS else ({'blocks':[{'text':'fixture'}]*49} if p.name=='cf-power-2024.json' else real(p))):
   with self.assertRaises(ValueError):data.prepare()
 def test_correct_interpretation_and_no_losses_can_pass(self):
  p,r,b,rows=self.fixture();s=score(p,r,rows,True,b);self.assertTrue(s['candidate_passes']);self.assertEqual(len(s['outcomes']),180);self.assertEqual(len(s['gates']),12)
  self.assertTrue(all(x['choice_gains']==[TARGET] and not x['choice_losses'] and not x['losses'] for x in s['paired']))
 def test_withholding_the_wrong_target_is_not_a_corrected_interpretation(self):
  p,r,b,rows=self.fixture()
  for i,x in enumerate(rows):
   if x['claim_id']==TARGET and x['arm']=='knowledge':rows[i]=response(TARGET,'knowledge',x['round'],'not_established',.6)
  s=score(p,r,rows,True,b);self.assertFalse(s['candidate_passes'])
  self.assertTrue(all(not g['criteria']['original_failure_correctly_chosen_and_displayed'] for g in s['gates'] if g['source_id']=='all'))
 def test_ordinary_choice_loss_blocks_even_when_not_displayed(self):
  p,r,b,rows=self.fixture();chosen=next(i for i,x in enumerate(rows) if x['arm']=='knowledge' and x['claim_id']=='cf-dns27-2024-c1')
  rows[chosen]=response('cf-dns27-2024-c1','knowledge',1,'not_established',.6);s=score(p,r,rows,True,b)
  self.assertFalse(s['candidate_passes']);self.assertIn('cf-dns27-2024-c1',s['paired'][0]['choice_losses'])
 def test_missing_rows_and_duplicate_joins_are_visible(self):
  p,r,b,rows=self.fixture();s=score(p,r,[],False,b);self.assertEqual(len(s['outcomes']),180);self.assertFalse(s['candidate_passes']);self.assertTrue(all(x['withheld'] for x in s['outcomes']))
  with self.assertRaises(ValueError):score(p,r,rows+[rows[0]],True,b)
 def test_global_failure_stops_once_with_no_resume(self):
  profile={'model':'jev-1.13.0','endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-only'}
  job={'id':'fixture','claim_id':'fixture','arm':'literal','round':1,'request_sha256':'fixture','body':{'model':profile['model'],'state':'{}','questions':{}}}
  with tempfile.TemporaryDirectory() as temp:
   protocol=Path(temp)/'protocol.json';protocol.write_text('{}');folder=Path(temp)/'once'
   with patch.object(trial,'PROTOCOL',protocol),patch.object(trial,'LOCAL',folder),patch.object(trial,'check',return_value={'profile':profile}),patch.object(trial,'jobs',return_value=[job]*180),patch('urllib.request.build_opener') as opener:
    opener.return_value.open.side_effect=HTTPError(profile['endpoint'],400,'bad',{},None);s=trial.run(profile)
    self.assertEqual(opener.return_value.open.call_count,1);self.assertEqual(s['unattempted_calls'],179)
    self.assertNotIn('fixture-only',(folder/'responses.jsonl').read_text())
    with self.assertRaises(FileExistsError):trial.run(profile)
