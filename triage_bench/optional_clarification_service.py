"""Read-only recorded suggestions; local entry prototypes are not human studies."""
import copy,json
from . import optional_clarification_trial as original,optional_question_trial as policy
from .optional_clarification_features import decision,parser_decision
from .optional_question_policy import decision as policy_decision

class OptionalClarificationStudy:
    def __init__(self,root):self.root=root;self._cache={}
    def trial(self,phase):
        if phase not in ('format','policy'):raise ValueError('Unknown optional study stage.')
        return original if phase=='format' else policy
    def verified(self,phase='policy'):
        t=self.trial(phase)
        paths=[t.PLAN,t.protocol_path(),t.result_path(),*(self.root/n for n in t.SOURCES),*(self.root/n for n in t.load(t.PLAN)['evidence_sha256']),*t.data.DATA.rglob('*'),*t.output().rglob('*'),*original.original.output().rglob('*'),*original.previous.output().rglob('*'),*original.output().rglob('*')]
        signature=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if phase not in self._cache or self._cache[phase][0]!=signature:self._cache[phase]=(signature,t.verify())
        return self._cache[phase][1]
    def overview(self,phase='policy'):
        t=self.trial(phase)
        try:result=copy.deepcopy(self.verified(phase))
        except (OSError,ValueError,KeyError):return {'available':False,'error':'Restore the committed optional-question study to inspect it.'}
        result.pop('outcomes');result['cards']=[{k:p[k] for k in ('id','dataset','family','variant','text')} for p in t.load(t.data.DATA/'inputs.json')]
        return {'available':True,'phase':phase,'candidate':'direct' if phase=='format' else 'first_question',**result}
    def card(self,identifier,reveal=False,phase='policy'):
        t=self.trial(phase);result=self.verified(phase)
        try:packet=next(p for p in t.load(t.data.DATA/'inputs.json') if p['id']==identifier)
        except StopIteration as e:raise ValueError('Unknown optional-question statement.') from e
        rows=[r for r in map(json.loads,(t.output()/'responses.jsonl').read_text().splitlines()) if r['card_id']==identifier]
        return {**packet,'phase':phase,'responses':rows,'decisions':{arm:{str(n):(decision if phase=='format' else policy_decision)(next((r for r in rows if r['arm']==(arm if phase=='format' else 'shared') and r['round']==n),None),arm) for n in (1,2,3)} for arm in (('direct','checklist') if phase=='format' else ('first_question','all_fields'))},'parser':parser_decision(packet),'jobs':[j for j in t.load(t.output()/'requests.json') if j['card_id']==identifier],
          'reference':next(r for r in t.load(t.data.DATA/'references.json') if r['id']==identifier) if reveal else None,
          'outcomes':[o for o in result['outcomes'] if o['id']==identifier] if reveal else None,
          'provider_calls':0,'server_writes':0,'human_review_recorded':False,'entry_autofill':False}
