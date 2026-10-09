"""Keep all inspected transfer claims and references, adding three scope companions."""
import json
from .paths import ROOT
from . import cross_report_data as old
from .report_source_audit import digest
from .public_rca_stages import committed

PLAN=ROOT/'checkpoints/publisher-knowledge-development-plan-2026-10-08.json'
ANNOTATIONS=ROOT/'checkpoints/publisher-knowledge-development-companions-2026-10-08.json'
PACK=ROOT/'checkpoints/publisher-knowledge-development-pack-2026-10-08.json'
TOPICS=old.TOPICS
CHOICES=old.CHOICES

def load(path):return json.loads(path.read_text())

def prepare():
 for p in (PLAN,ANNOTATIONS):committed(p)
 packets,refs=old.packets();packets=[{k:v for k,v in p.items() if k not in ('report','scoped_report')} for p in packets];refs=[dict(r) for r in refs]
 source=next(p for p in packets if p['id']=='cf-power-2024-c5');article=load(old.audit.CACHE/(source['source_id']+'.json'));cs=load(ANNOTATIONS)['claims']
 if len(cs)!=3 or sorted(c['choice'] for c in cs)!=sorted(CHOICES):raise ValueError('Companion classes changed.')
 for c in cs:
  if c['source_id']!=source['source_id'] or c['topic']!='cause' or not c['evidence_blocks'] or any(type(i)!=int or not 0<=i<len(article['blocks']) for i in c['evidence_blocks']):raise ValueError('Companion source scope changed.')
  packets.append({**source,**{k:c[k] for k in ('id','source_id','topic','claim')}})
  refs.append({'id':c['id'],'choice':c['choice'],'rationale':c['rationale'],'evidence_spans':[{'block':i,'sha256':digest(article['blocks'][i]['text'].encode())} for i in c['evidence_blocks']]})
 if len(packets)!=30 or len({p['id'] for p in packets})!=30:raise ValueError('Development allocation changed.')
 return {'schema':'publisher-knowledge-development-pack-1','plan_sha256':digest(PLAN.read_bytes()),'annotations_sha256':digest(ANNOTATIONS.read_bytes()),'old_pack_sha256':digest(old.PACK.read_bytes()),'producer_sha256':digest((ROOT/'triage_bench/report_knowledge_data.py').read_bytes()),'claims':packets,'references':refs,'target':'cf-power-2024-c5','companions':[c['id'] for c in cs],'human_entries':0,'human_reviews':0,'independent_reference_reviews':0,'preparation':'Inspected development; all 27 historical references byte-preserved plus three prospectively authored companion references.'}

def packets(local=True):
 for p in (PLAN,ANNOTATIONS,PACK):committed(p)
 pack=load(PACK);old.packets(local=False)
 for p,k in ((PLAN,'plan_sha256'),(ANNOTATIONS,'annotations_sha256'),(old.PACK,'old_pack_sha256'),(ROOT/'triage_bench/report_knowledge_data.py','producer_sha256')):
  if digest(p.read_bytes())!=pack[k]:raise ValueError('Frozen knowledge development dependency changed.')
 if local and prepare()!=pack:raise ValueError('Development sources or references changed.')
 result=[]
 for original in pack['claims']:
  p=dict(original)
  if local:
   article=load(old.audit.CACHE/(p['source_id']+'.json'));full=old.audit.text(article)
   if p['retained_blocks']!=list(range(len(article['blocks']))) or digest(full.encode())!=p['scoped_report_sha256']:raise ValueError('Full source input changed.')
   p['report']=p['scoped_report']=full
  result.append(p)
 return result,pack['references']
