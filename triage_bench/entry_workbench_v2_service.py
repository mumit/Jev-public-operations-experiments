"""Versioned learning examples; never accept or score participant exports."""
import json
from .entry_walkthrough_service import EntryWalkthrough
from . import entry_walkthrough as old

class EntryWorkbenchV2:
    def __init__(self):self.original=EntryWalkthrough()
    def examples(self):
        p=self.original.pack()
        if not p['available']:return p
        examples=[]
        for item in p['practice']:
            example={k:v for k,v in item.items() if k!='reference'}
            examples.append({**example,'condition':'practice'})
        examples.extend(p['tasks'])
        return {'available':True,'schema':'entry-learning-v2-1','mode':'software_demo','examples':examples,'source_protocol_sha256':p['protocol_sha256'],'interface_sha256':old.sha(json.dumps({n:old.sha((old.ROOT/n).read_bytes()) for n in ('triage_bench/entry_workbench_v2_service.py','triage_bench/web/entry-workbench-v2.html','triage_bench/web/entry-workbench-v2.js','triage_bench/web/entry-workbench-v2.css')},sort_keys=True).encode()),'provider_calls':0,'server_writes':0,'scored_participants':0}
    def references(self):
        self.original.verified();p=old.load(old.PACK)
        return {'references':p['references']+[{'id':t['id'],**t['reference']} for t in p['practice']],'origin':'Scripted assistant-authored learning references; no independent review.'}
