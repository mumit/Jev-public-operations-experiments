"""Read-only complete workflow, actual bindings and fresh provider calls."""
import copy,json
from . import full_workflow_trial as t

class FullWorkflowStudy:
    def __init__(self,root):self.root=root;self._signature=None;self._result=None
    def verified(self):
        paths=[t.PLAN,t.RESULT,*(t.protocol_path(p) for p in ('initial','verdict')),*t.DATA.rglob('*'),*t.BASE.rglob('*'),*(self.root/n for n in t.SOURCES)]
        signature=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if signature!=self._signature:
            t.committed(t.RESULT);result=t.score()
            if result!=t.load(t.RESULT):raise ValueError('Complete workflow assessment changed.')
            self._signature,self._result=signature,result
        return self._result
    def overview(self):
        try:r=copy.deepcopy(self.verified())
        except (OSError,ValueError,KeyError):return {'available':False,'error':'Restore all twenty-six evidence assets.'}
        r.pop('outcomes');return {'available':True,'cards':[{k:p[k] for k in ('id','dataset','wording')} for p in t.load(t.DATA/'inputs.json')],**r}
    def card(self,identifier,reveal=False):
        r=self.verified()
        try:p=next(p for p in t.load(t.DATA/'inputs.json') if p['id']==identifier)
        except StopIteration as error:raise ValueError('Unknown note.') from error
        return {**p,'bindings':[b for b in t.load(t.protocol_path('verdict'))['bindings'] if b['card_id']==identifier],
            'jobs':[j for phase in ('initial','verdict') for j in t.load(t.output(phase)/'requests.json') if j['card_id']==identifier],
            'responses':[j for phase in ('initial','verdict') for j in map(json.loads,(t.output(phase)/'responses.jsonl').read_text().splitlines()) if j['card_id']==identifier],
            'reference':next(x for x in t.load(t.DATA/'references.json') if x['id']==identifier) if reveal else None,
            'outcomes':[o for o in r['outcomes'] if o['note_id']==identifier] if reveal else None}
