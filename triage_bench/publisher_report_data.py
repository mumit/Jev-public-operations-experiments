"""Resolve immutable claim metadata against retained publisher snapshots."""
import json
from pathlib import Path
from .paths import ROOT
from . import report_source_audit as audit
from .report_evidence_service import DESIGN
from .public_rca_stages import committed
from .publisher_report_features import CHOICES

CLAIMS=ROOT/'checkpoints/publisher-report-claims-2026-10-07.json'
REFERENCES=ROOT/'checkpoints/publisher-report-references-2026-10-07.json'

def load(path):return json.loads(Path(path).read_text())

def metadata():
    d=load(ROOT/DESIGN);c=load(CLAIMS);r=load(REFERENCES)
    if c['schema']!='publisher-report-claims-1' or r['schema']!='publisher-report-references-1' or r['human_reviews'] or r['independent_reference_reviews']:
        raise ValueError('Claim schema or review attribution changed.')
    catalog={s['id']:s for s in audit.load_catalog()['sources']};cs=c['claims'];rs=r['references']
    if len(cs)!=48 or len({c['id'] for c in cs})!=48 or {c['id'] for c in cs}!={r['id'] for r in rs} or len(rs)!=48:
        raise ValueError('Claim/reference slots changed.')
    if {c['source_id'] for c in cs}!=set(d['primary_sources']):raise ValueError('Primary source allocation changed.')
    for source in d['primary_sources']:
        for topic in d['topics']:
            if sum(c['source_id']==source and c['topic']==topic for c in cs)!=2:raise ValueError('Topic denominator changed.')
    for c in cs:
        if set(c)!={'id','source_id','topic','claim'} or not isinstance(c['claim'],str) or not c['claim'].strip():raise ValueError('Input allowlist changed.')
        c['allocation']=catalog[c['source_id']]['allocation'];c['incident_group']=catalog[c['source_id']]['incident_group']
    for r in rs:
        if r['choice'] not in CHOICES or r['review_status']!='assistant_resolved' or not r['evidence_spans']:raise ValueError('Reference unresolved or malformed.')
    return d,cs,rs

def packets(phase):
    if phase not in {'development','evaluation'}:raise ValueError('Unknown report phase.')
    audit.verify(local=True);d,claims,refs=metadata();reference={r['id']:r for r in refs};packets=[]
    for c in claims:
        if c['allocation']!=phase:continue
        a=load(audit.CACHE/(c['source_id']+'.json'));p=audit.input_prefix(a['blocks']);r=reference[c['id']]
        if r['excerpt_sha256']!=p['sha256']:raise ValueError('Annotated excerpt changed.')
        for span in r['evidence_spans']:
            b=span['block']
            if type(b)!=int or not 0<=b<p['included_blocks']:raise ValueError('Evidence outside supplied excerpt.')
            text=a['blocks'][b]['text'];start,end=span['start'],span['end']
            if type(start)!=int or type(end)!=int or not 0<=start<end<=len(text) or audit.digest(text[start:end].encode())!=span['sha256']:
                raise ValueError('Exact evidence span changed.')
        packets.append({**c,'report':p['text'],'excerpt_sha256':p['sha256']})
    if len(packets)!=24:raise ValueError('Whole-phase denominator changed.')
    return packets,[r for r in refs if r['id'] in {c['id'] for c in packets}]

def committed_inputs():
    for path in (ROOT/DESIGN,audit.CATALOG,audit.AUDIT,CLAIMS,REFERENCES):committed(path)
