"""Read-only context challenges with separately revealed references."""
import copy,json
from . import subject_robustness_trial as t

class SubjectRobustnessStudy:
    def __init__(self,root):self.root=root;self._signature=None;self._result=None
    def verified(self):
        paths=[t.PLAN,t.PROTOCOL,t.RESULT,t.CARDS,t.REFERENCES,*t.OUT.rglob('*'),*(self.root/n for n in t.SOURCES)]
        signature=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if signature!=self._signature:
            t.committed(t.RESULT);result=t.score()
            if result!=t.load(t.RESULT):raise ValueError('Robustness assessment changed.')
            self._signature,self._result=signature,result
        return self._result
    def overview(self):
        try:r=copy.deepcopy(self.verified())
        except (OSError,ValueError,KeyError):return {'available':False,'error':'Restore all twenty-five evidence assets.'}
        r.pop('outcomes');return {'available':True,'cards':[{k:p[k] for k in ('id','dataset','family')} for p in t.load(t.CARDS)],**r}
    def card(self,identifier,reveal=False):
        r=self.verified()
        try:p=next(p for p in t.load(t.CARDS) if p['id']==identifier)
        except StopIteration as error:raise ValueError('Unknown challenge.') from error
        return {**p,'contexts':{a:t.context(p,a) for a in t.ARMS},'selection':t.excerpt_context(p,p['sentence']),
            'jobs':[j for j in t.load(t.OUT/'requests.json') if j['card_id']==identifier],
            'responses':[j for j in map(json.loads,(t.OUT/'responses.jsonl').read_text().splitlines()) if j['card_id']==identifier],
            'reference':t.load(t.REFERENCES)[identifier] if reveal else None,
            'outcomes':[o for o in r['outcomes'] if o['card_id']==identifier] if reveal else None}
