import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench import cross_report_data as data,cross_report_trial as trial
from triage_bench.literal_claim_features import request
from triage_bench.report_source_audit import digest

class CrossReportTests(unittest.TestCase):
 def fixture(self):
  inventory=data.load(data.audit.AUDIT)
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);cache=Path(temp.name)
  for source in inventory['sources']:
   article={'title':source['title'],'blocks':[{'text':'Whole fixture block '+str(i)} for i in range(source['blocks'])]}
   source['text_sha256']=digest(data.audit.text(article).encode())
   (cache/(source['id']+'.json')).write_text(json.dumps(article))
  return inventory,cache
 def test_preparation_retains_every_block_and_fixed_report_allocation(self):
  inv,cache=self.fixture()
  with patch.object(data,'committed'),patch.object(data.audit,'verify',return_value=inv),patch.object(data.audit,'CACHE',cache):pack=data.prepare()
  self.assertEqual(len(pack['claims']),27)
  for source in inv['sources']:
   claims=[p for p in pack['claims'] if p['source_id']==source['id']]
   self.assertEqual(len(claims),9)
   for p in claims:self.assertEqual(p['retained_blocks'],list(range(source['blocks'])))
  self.assertEqual(pack['independent_reference_reviews'],0)
 def test_invalid_reference_class_cannot_prepare(self):
  inv,cache=self.fixture();annotations=data.load(data.ANNOTATIONS);annotations['claims'][0]['choice']='contradicted';real_load=data.load
  with patch.object(data,'committed'),patch.object(data.audit,'verify',return_value=inv),patch.object(data.audit,'CACHE',cache),patch.object(data,'load',side_effect=lambda p:annotations if p==data.ANNOTATIONS else real_load(p)):
   with self.assertRaises(ValueError):data.prepare()
 def test_evidence_must_be_an_actual_retained_block(self):
  inv,cache=self.fixture();annotations=data.load(data.ANNOTATIONS);annotations['claims'][0]['evidence_blocks']=[999];real_load=data.load
  with patch.object(data,'committed'),patch.object(data.audit,'verify',return_value=inv),patch.object(data.audit,'CACHE',cache),patch.object(data,'load',side_effect=lambda p:annotations if p==data.ANNOTATIONS else real_load(p)):
   with self.assertRaises(ValueError):data.prepare()
 def test_paired_state_has_full_code_and_no_reference_or_id(self):
  p={'report':'Paragraph\n\nroute add PREFIX\n\nLast paragraph','scoped_report':'Paragraph\n\nroute add PREFIX\n\nLast paragraph','selected_incident':'Whole title','claim':'Claim','choice':'SECRET','id':'SECRET','rationale':'SECRET'}
  a,b=request(p,'legacy'),request(p,'literal');self.assertEqual(a['state'],b['state']);state=json.loads(a['state'])
  self.assertEqual(state['report_excerpt'],p['report']);self.assertNotIn('SECRET',a['state'])
  self.assertEqual(set(state),{'report_excerpt','selected_incident','claim'})
 def test_provider_failure_is_once_only_and_no_resume(self):
  profile={'model':'jev-1.13.0','endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768,'api_key':'fixture-only'}
  job={'id':'fixture','claim_id':'fixture','arm':'legacy','round':1,'request_sha256':'fixture','body':{'model':profile['model'],'state':'{}','questions':{}}}
  with tempfile.TemporaryDirectory() as temp:
   protocol=Path(temp)/'protocol.json';protocol.write_text('{}');folder=Path(temp)/'once'
   with patch.object(trial,'PROTOCOL',protocol),patch.object(trial,'LOCAL',folder),patch.object(trial,'check',return_value={'profile':profile}),patch.object(trial,'jobs',return_value=[job]*162),patch('urllib.request.build_opener') as opener:
    opener.return_value.open.side_effect=HTTPError(profile['endpoint'],400,'bad',{},None)
    r=trial.run(profile);self.assertEqual(opener.return_value.open.call_count,1);self.assertEqual(r['unattempted_calls'],161)
    with self.assertRaises(FileExistsError):trial.run(profile)
