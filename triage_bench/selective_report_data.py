"""Count-based section fixtures and three-class references on fixed new reports."""
import json
from .paths import ROOT
from . import selective_report_audit as audit
from .incident_scope_features import select
from .report_source_audit import digest
from .public_rca_stages import committed

PLAN=ROOT/'checkpoints/publisher-selective-confirmation-plan-v2-2026-10-07.json'
ANNOTATIONS=ROOT/'checkpoints/publisher-selective-annotations-2026-10-07.json'
PACK=ROOT/'checkpoints/publisher-selective-pack-2026-10-07.json'
TOPICS=('impact','cause','recovery')
CHOICES=('supported','contradicted','not_established')

def load(path):return json.loads(path.read_text())

def prepare():
    for path in (PLAN,ANNOTATIONS):committed(path)
    sources=audit.verify();plan=load(PLAN);annotations=load(ANNOTATIONS);packets=[];refs=[]
    if [s['id'] for s in sources['sources']]!=[s['id'] for s in plan['sources']]:raise ValueError('Source allocation changed.')
    for source in sources['sources']:
        if source['status']!='available' or not source['sections']:raise ValueError('Unavailable source or selected section.')
        blocks=load(audit.CACHE/(source['id']+'.json'))['blocks'];sections=source['sections']
        claims=[c for c in annotations['claims'] if c['source_id']==source['id']]
        if len(claims)!=9:raise ValueError('Every report needs nine claims.')
        for t,topic in enumerate(TOPICS):
            group=[c for c in claims if c['topic']==topic]
            if len(group)!=3 or sorted(c['choice'] for c in group)!=sorted(CHOICES):raise ValueError('Each topic needs all three reference classes.')
            chosen,indices,text=select(blocks,sections,sections[min(t,len(sections)-1)]['id'])
            for c in group:
                if not c['evidence_blocks'] or not set(c['evidence_blocks'])<=set(range(chosen['start'],chosen['end'])):raise ValueError('Evidence is outside selected section.')
                packets.append({'id':c['id'],'source_id':source['id'],'source_url':source['url'],'topic':topic,
                    'claim':c['claim'],'selected_incident':chosen['label'],'selected_section_id':chosen['id'],
                    'retained_blocks':indices,'scoped_report_sha256':digest(text.encode()),'excerpt_bytes':len(text.encode())})
                refs.append({'id':c['id'],'choice':c['choice'],'rationale':c['rationale'],'evidence_spans':[
                    {'block':i,'sha256':digest(blocks[i]['text'].encode())} for i in c['evidence_blocks']]})
    if len(packets)!=27 or len({p['id'] for p in packets})!=27 or len(annotations['claims'])!=27:raise ValueError('Claim allocation changed.')
    return {'schema':'publisher-selective-pack-1','plan_sha256':digest(PLAN.read_bytes()),
        'audit_sha256':digest(audit.AUDIT.read_bytes()),'annotations_sha256':digest(ANNOTATIONS.read_bytes()),
        'producer_sha256':digest((ROOT/'triage_bench/selective_report_data.py').read_bytes()),'claims':packets,'references':refs,
        'human_entries':0,'human_reviews':0,'independent_reference_reviews':0,'source_cautions':annotations['source_cautions'],
        'preparation':'Same-assistant controlled claims after a preserved layout-audit failure; before new model outcomes.'}

def packets(local=True):
    for path in (PLAN,ANNOTATIONS,PACK):committed(path)
    pack=load(PACK);audit.verify(local=local)
    for path,key in ((PLAN,'plan_sha256'),(ANNOTATIONS,'annotations_sha256'),(audit.AUDIT,'audit_sha256'),
        (ROOT/'triage_bench/selective_report_data.py','producer_sha256')):
        if digest(path.read_bytes())!=pack[key]:raise ValueError('Frozen claim preparation changed.')
    if local and prepare()!=pack:raise ValueError('References or source sections changed.')
    result=[]
    for original in pack['claims']:
        p=dict(original)
        if local:
            blocks=load(audit.CACHE/(p['source_id']+'.json'))['blocks']
            p['scoped_report']='\n\n'.join(blocks[i]['text'] for i in p['retained_blocks']);p['report']=p['scoped_report']
            if digest(p['scoped_report'].encode())!=p['scoped_report_sha256']:raise ValueError('Selected source text changed.')
        result.append(p)
    return result,pack['references']
