"""Read-only inspection of frozen corruption requests and responses."""
import copy
import json
from .public_rca_stages import load, committed
from .binding_corruption_trial import PLAN, PROTOCOL, RESULT, OUT, SOURCES, DATA, score, altered, ARMS
from .assistant_review_trial import REVIEWS, check_reviews
from .claim_review import SPEC

class BindingCorruptionStudy:
    def __init__(self,root):self.root=root;self._signature=None;self._result=None
    def verified(self):
        paths=[PLAN,PROTOCOL,RESULT,REVIEWS,*DATA.rglob('*'),*OUT.rglob('*'),*(self.root/n for n in SOURCES),SPEC,*(self.root/n for n in load(SPEC)['sha256'])]
        signature=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if signature!=self._signature:
            committed(RESULT);value=score()
            if value!=load(RESULT):raise ValueError('Corruption results changed.')
            self._signature,self._result=signature,value
        return self._result
    def overview(self):
        try:result=copy.deepcopy(self.verified())
        except (OSError,ValueError,KeyError):return {'available':False,'error':'Restore all nineteen public evidence assets.'}
        result.pop('outcomes');packets,_=check_reviews()
        return {'available':True,'notes':[{'id':p['id'],'dataset':p['dataset'],'wording':p['wording']} for p in packets],**result}
    def card(self,identifier,reveal=False):
        result=self.verified();packets,records=check_reviews()
        try:p=next(p for p in packets if p['id']==identifier);r=next(r for r in records if r['note_id']==identifier)
        except StopIteration as error:raise ValueError('Unknown note.') from error
        refs=load(PROTOCOL)['diagnostic_references'][identifier] if reveal else None
        return {'id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'note':p['note'],'sentences':p['candidates'],
            'clean_decisions':r['export']['reviews'],'decisions':{a:altered(r,a)['export']['reviews'] for a in ARMS},
            'jobs':[j for j in load(OUT/'requests.json') if j['card_id']==identifier],
            'responses':[r for r in map(json.loads,(OUT/'responses.jsonl').read_text().splitlines()) if r['card_id']==identifier],
            'reference':refs}
