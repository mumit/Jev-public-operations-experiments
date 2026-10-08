"""A new literal reference version; preserve every historical reference byte."""
from .paths import ROOT
from . import incident_scope_data as scope
from . import publisher_report_data as old
from .report_source_audit import digest
from .public_rca_stages import committed

PLAN=ROOT/'checkpoints/publisher-literal-claim-plan-2026-10-07.json'
PACK=ROOT/'checkpoints/publisher-literal-claim-references-2026-10-07.json'

def prepare():
    committed(PLAN);packets,refs=scope.packets(local=False);new=[]
    for r in refs:
        r=dict(r)
        if r['id']=='gh-april-2023-c3':
            r['choice']='contradicted';r['rationale']='The claim says this report confirms the contributing factors; the report explicitly says their investigation remains ongoing.'
        new.append(r)
    return {'schema':'publisher-literal-claim-references-1','plan_sha256':digest(PLAN.read_bytes()),
        'original_references_sha256':digest(old.REFERENCES.read_bytes()),'selections_sha256':digest(scope.PACK.read_bytes()),
        'references':new,'changed_reference_ids':['gh-april-2023-c3'],'human_entries':0,'human_reviews':0,
        'independent_reference_reviews':0,'reference_classes':['supported','contradicted']}

def packets(local=True):
    for p in (PLAN,PACK):committed(p)
    pack=old.load(PACK)
    if prepare()!=pack:raise ValueError('Literal reference version changed.')
    packets,_=scope.packets(local=local)
    return packets,pack['references']
