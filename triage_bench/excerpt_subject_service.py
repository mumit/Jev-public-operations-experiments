"""Read-only inspection of separate calls and unchanged proposal composition."""
import copy
import json
from .public_rca_stages import load, committed
from .excerpt_subject_trial import PLAN, PROTOCOL, SUBJECT_PROTOCOL, VERDICT_PROTOCOL, RESULT, OUT, SOURCES, DATA, ARMS, decisions, composed_row, decision, score, excerpt_context
from .assistant_review_trial import REVIEWS, check_reviews
from .claim_review import SPEC

class ExcerptSubjectStudy:
    def __init__(self,root):self.root=root;self._signature=None;self._result=None
    def verified(self):
        paths=[PLAN,PROTOCOL,SUBJECT_PROTOCOL,VERDICT_PROTOCOL,RESULT,REVIEWS,*DATA.rglob('*'),*OUT.rglob('*'),*(self.root/n for n in SOURCES),SPEC,*(self.root/n for n in load(SPEC)['sha256'])]
        signature=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if signature!=self._signature:
            committed(RESULT);value=score()
            if value!=load(RESULT):raise ValueError('Excerpt-subject results changed.')
            self._signature,self._result=signature,value
        return self._result
    def overview(self):
        try:result=copy.deepcopy(self.verified())
        except (OSError,ValueError,KeyError):return {'available':False,'error':'Restore all twenty-four public evidence assets.'}
        result.pop('outcomes');packets,_=check_reviews()
        return {'available':True,'notes':[{'id':p['id'],'dataset':p['dataset'],'wording':p['wording']} for p in packets],**result}
    def card(self,identifier,reveal=False):
        self.verified();packets,records=check_reviews()
        try:p=next(p for p in packets if p['id']==identifier);r=next(r for r in records if r['note_id']==identifier)
        except StopIteration as error:raise ValueError('Unknown note.') from error
        rows=[row for row in map(json.loads,(OUT/'responses.jsonl').read_text().splitlines()) if row['card_id']==identifier]
        index={(row['card_id'],row['arm'],row['round'],row['sentence']):row for row in rows}
        composition=[]
        for arm in ARMS:
            for n in (1,2,3):
                sentences={}
                for sid,d in r['export']['reviews'].items():
                    if d['decision']!='confirm':continue
                    combined=composed_row(index,identifier,arm,n,r,sid)
                    sentences[sid]={**decision(combined,sid,not arm.endswith('baseline')),
                        'source_call_ids':combined.get('source_call_ids',[combined.get('id')])}
                composition.append({'arm':arm,'round':n,'sentences':sentences})
        return {'id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'note':p['note'],'sentences':p['candidates'],
            'contexts':{sid:excerpt_context(p,sid) for sid,d in r['export']['reviews'].items() if d['decision']=='confirm'},'clean_decisions':r['export']['reviews'],'decisions':{a:decisions(r,a) for a in ARMS},
            'jobs':[j for j in load(OUT/'requests.json') if j['card_id']==identifier],'responses':rows,'composition':composition,
            'reference':load(PROTOCOL)['references'][identifier] if reveal else None}
