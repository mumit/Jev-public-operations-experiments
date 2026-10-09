"""Controlled three-class claims against complete fixed publisher reports."""
import json
from .paths import ROOT
from . import review_budget_audit as audit
from .report_source_audit import digest
from .public_rca_stages import committed

PLAN=audit.PLAN
ANNOTATIONS=ROOT/'checkpoints/publisher-review-budget-annotations-2026-10-08.json'
PACK=ROOT/'checkpoints/publisher-review-budget-pack-2026-10-08.json'
TOPICS=('impact','cause','recovery')
CHOICES=('supported','contradicted','not_established')

def load(path):return json.loads(path.read_text())

def prepare():
    for path in (PLAN,ANNOTATIONS,audit.AUDIT):committed(path)
    sources=audit.verify();plan=load(PLAN);annotations=load(ANNOTATIONS);packets=[];refs=[]
    if not sources['preparation_eligible'] or [s['id'] for s in sources['sources']]!=[s['id'] for s in plan['sources']]:raise ValueError('Source allocation or eligibility changed.')
    for source in sources['sources']:
        if source['status']!='available':raise ValueError('Unavailable allocated source.')
        article=load(audit.CACHE/(source['id']+'.json'));blocks=article['blocks'];full=audit.text(article)
        if digest(full.encode())!=source['text_sha256']:raise ValueError('Source text changed.')
        claims=[c for c in annotations['claims'] if c['source_id']==source['id']]
        if len(claims)!=9:raise ValueError('Every report needs nine claims.')
        if sum(c.get('assertion_scope')=='report_knowledge' for c in claims)<3:raise ValueError('Need at least three reporting assertions per report.')
        if any(c.get('assertion_scope') not in ('incident_fact','report_knowledge') for c in claims):raise ValueError('Missing scope stratum.')
        for topic in TOPICS:
            group=[c for c in claims if c['topic']==topic]
            if len(group)!=3 or sorted(c['choice'] for c in group)!=sorted(CHOICES):raise ValueError('Each topic needs all three reference classes.')
            for c in group:
                indices=c['evidence_blocks']
                if not indices or any(type(i)!=int or not 0<=i<len(blocks) for i in indices) or len(set(indices))!=len(indices):raise ValueError('Invalid evidence blocks.')
                if not c['claim'].strip() or not c['rationale'].strip():raise ValueError('Missing claim or reference rationale.')
                packets.append({'id':c['id'],'source_id':source['id'],'source_url':source['url'],'topic':topic,
                    'claim':c['claim'],'assertion_scope':c['assertion_scope'],'selected_incident':article['title'],'source_display_name':article['title'],
                    'retained_blocks':list(range(len(blocks))),'scoped_report_sha256':digest(full.encode()),'excerpt_bytes':len(full.encode())})
                refs.append({'id':c['id'],'choice':c['choice'],'rationale':c['rationale'],'evidence_spans':[
                    {'block':i,'sha256':digest(blocks[i]['text'].encode())} for i in indices]})
    if len(packets)!=27 or len({p['id'] for p in packets})!=27 or len(annotations['claims'])!=27:raise ValueError('Claim allocation changed.')
    return {'schema':'publisher-review-budget-pack-1','plan_sha256':digest(PLAN.read_bytes()),
        'audit_sha256':digest(audit.AUDIT.read_bytes()),'annotations_sha256':digest(ANNOTATIONS.read_bytes()),
        'producer_sha256':digest((ROOT/'triage_bench/review_budget_data.py').read_bytes()),'claims':packets,'references':refs,
        'human_entries':0,'human_reviews':0,'independent_reference_reviews':0,'source_cautions':annotations['source_cautions'],
        'preparation':'Same-assistant controlled claims after source inspection, before new model outcomes; complete extracted report retained.'}

def packets(local=True):
    for path in (PLAN,ANNOTATIONS,PACK):committed(path)
    pack=load(PACK);audit.verify(local=local)
    for path,key in ((PLAN,'plan_sha256'),(ANNOTATIONS,'annotations_sha256'),(audit.AUDIT,'audit_sha256'),
        (ROOT/'triage_bench/review_budget_data.py','producer_sha256')):
        if digest(path.read_bytes())!=pack[key]:raise ValueError('Frozen claim preparation changed.')
    if local and prepare()!=pack:raise ValueError('References or full source input changed.')
    result=[]
    for original in pack['claims']:
        p=dict(original)
        if local:
            article=load(audit.CACHE/(p['source_id']+'.json'))
            if p['retained_blocks']!=list(range(len(article['blocks']))):raise ValueError('Whole-report retention changed.')
            p['scoped_report']=audit.text(article);p['report']=p['scoped_report']
            if digest(p['scoped_report'].encode())!=p['scoped_report_sha256']:raise ValueError('Full source text changed.')
        result.append(p)
    return result,pack['references']
