"""Assistant-supplied selection fixtures on the already inspected monthly report."""
from .paths import ROOT
from . import publisher_report_data as old
from .publisher_scope_preview import sections
from .incident_scope_features import select
from .report_source_audit import digest
from .public_rca_stages import committed

PLAN=ROOT/'checkpoints/publisher-incident-scope-plan-2026-10-07.json'
PACK=ROOT/'checkpoints/publisher-incident-selections-2026-10-07.json'
SOURCE='gh-april-2023'

def prepare():
    committed(PLAN);plan=old.load(PLAN);old.committed_inputs()
    packets,refs=old.packets('evaluation');packets=[p for p in packets if p['source_id']==SOURCE]
    blocks,inventory=sections(SOURCE);fixtures=[]
    for p in packets:
        label=plan['selection_contract']['mapping'][p['id']]
        found=[s for s in inventory if s['label'].startswith(label+' ')]
        if len(found)!=1:raise ValueError('Prepared explicit selection is not unique.')
        chosen,indices,text=select(blocks,inventory,found[0]['id'])
        fixtures.append({'id':p['id'],'selection_id':chosen['id'],'selected_incident':chosen['label'],
            'selection_author':'assistant_fixture','retained_blocks':indices,'full_excerpt_sha256':p['excerpt_sha256'],
            'scoped_excerpt_sha256':digest(text.encode()),'full_bytes':len(p['report'].encode()),'scoped_bytes':len(text.encode())})
    return {'schema':'publisher-incident-selections-1','source_id':SOURCE,'inventory':inventory,'fixtures':fixtures,
        'human_entries':0,'human_reviews':0,'independent_reference_reviews':0,'plan_sha256':digest(PLAN.read_bytes())}

def packets(local=True):
    for p in (PLAN,PACK):committed(p)
    pack=old.load(PACK);plan=old.load(PLAN)
    if pack['plan_sha256']!=digest(PLAN.read_bytes()) or pack['source_id']!=SOURCE or pack['human_entries']:
        raise ValueError('Selection contract changed.')
    _,cs,refs=old.metadata();cs=[c for c in cs if c['source_id']==SOURCE]
    rs=[r for r in refs if r['id'] in {c['id'] for c in cs}]
    if len(cs)!=6 or {f['id'] for f in pack['fixtures']}!={c['id'] for c in cs} or len(pack['fixtures'])!=6:
        raise ValueError('Six selection slots required.')
    fixtures={f['id']:f for f in pack['fixtures']}
    if not local:return [{**c,**fixtures[c['id']]} for c in cs],rs
    if prepare()!=pack:raise ValueError('Frozen selection or source blocks changed.')
    full,_=old.packets('evaluation');by_id={p['id']:p for p in full};blocks,inventory=sections(SOURCE);result=[]
    for c in cs:
        f=fixtures[c['id']];chosen,indices,text=select(blocks,inventory,f['selection_id'])
        # Validation only: references never select blocks or enter requests.
        if any(s['block'] not in indices for r in rs if r['id']==c['id'] for s in r['evidence_spans']):
            raise ValueError('Selected section omits frozen reference evidence.')
        result.append({**by_id[c['id']],**f,'scoped_report':text})
    return result,rs
