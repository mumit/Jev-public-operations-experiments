"""Read-only inspection of the separate same-assistant diagnostic."""
import copy
import json
from .public_rca_stages import load, committed
from .assistant_review_trial import PLAN, PROTOCOL, REVIEWS, RESULT, OUT, SOURCES, DATA, score
from .claim_review import SPEC


class AssistantReviewStudy:
    def __init__(self, root):
        self.root=root;self._signature=None;self._result=None

    def verified(self):
        paths=[PLAN,PROTOCOL,REVIEWS,RESULT,*DATA.rglob('*'),*OUT.rglob('*'),
            *(self.root/n for n in SOURCES),SPEC,*(self.root/n for n in load(SPEC)['sha256'])]
        signature=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if signature!=self._signature:
            committed(RESULT);result=score()
            if result!=load(RESULT):raise ValueError('Assistant-review results changed.')
            self._signature,self._result=signature,result
        return self._result

    def overview(self):
        try:result=copy.deepcopy(self.verified())
        except (OSError,ValueError,KeyError):return {'available':False,'error':'Restore all eighteen public evidence assets.'}
        for group in result['panels'].values():
            for p in group.values():
                for rounds in p['arms'].values():
                    for r in rounds:r.pop('outcomes')
        return {'available':True,**result}

    def card(self, identifier, reveal=False):
        result=self.verified();record=copy.deepcopy(next(r for r in load(REVIEWS)['records'] if r['note_id']==identifier))
        responses=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines() if json.loads(line)['card_id']==identifier]
        jobs=[j for j in load(OUT/'requests.json') if j['card_id']==identifier]
        outcomes={arm:[] for arm in ('bound_text','explicit_meaning')}
        for arm,rr in result['panels']['all'][record['dataset']]['arms'].items():
            for r in rr:
                for o in r['outcomes']:
                    if o['note_id']!=identifier:continue
                    value={'round':r['round'],**copy.deepcopy(o)}
                    if not reveal:
                        for k in ('reference','correct','wrong_displayed'):value.pop(k)
                    outcomes[arm].append(value)
        return {**record,'responses':responses,'jobs':jobs,'outcomes':outcomes,'reference':
            next(r for r in load(DATA/'references.json') if r['id']==identifier) if reveal else None}
