"""Read-only claim entry preview and verified experiment inspection."""
import copy,json
from . import explicit_claim_trial as t
from .explicit_claim_features import KINDS,DURATIONS,validate,canonical,evaluate,request

class ExplicitClaimStudy:
    def __init__(self,root):self.root=root;self._cache={}
    def verified(self,phase):
        paths=[t.PLAN,t.result_path(phase),t.protocol_path(phase),*(self.root/n for n in t.SOURCES),*(self.root/n for n in t.load(t.PLAN)['evidence_sha256']),*t.data.folder(phase).rglob('*'),*t.output(phase).rglob('*')]
        sig=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if phase not in self._cache or self._cache[phase][0]!=sig:self._cache[phase]=(sig,t.verify(phase))
        return self._cache[phase][1]
    def overview(self,phase='development'):
        try:r=copy.deepcopy(self.verified(phase))
        except (OSError,ValueError,KeyError):return {'available':False,'error':'This phase needs its recorded evidence and committed assessment.'}
        r.pop('outcomes')
        cards=[{'id':p['id'],'dataset':p['dataset'],'category':p['category'],'kind':p['claim']['kind'],'service':p['claim']['service'],'asserted':p['claim']['asserted'],'recording':p['recording']} for p in t.load(t.data.folder(phase)/'inputs.json')]
        return {'available':True,'cards':cards,'phases':[p for p in ('development','confirmation') if t.result_path(p).exists()],**r}
    def packet(self,phase,identifier):
        t.data.validate_pack(phase,t.check_plan)
        try:return next(p for p in t.load(t.data.folder(phase)/'inputs.json') if p['id']==identifier)
        except StopIteration as e:raise ValueError('Unknown explicit claim.') from e
    def card(self,phase,identifier,reveal=False):
        result=self.verified(phase);p=self.packet(phase,identifier)
        return {**p,'canonical':canonical(p['claim']),
          'jobs':[j for j in t.load(t.output(phase)/'requests.json') if j['card_id']==identifier],
          'responses':[r for r in map(json.loads,(t.output(phase)/'responses.jsonl').read_text().splitlines()) if r['card_id']==identifier],
          'reference':next(r for r in t.load(t.data.folder(phase)/'references.json') if r['id']==identifier) if reveal else None,
          'outcomes':[o for o in result['outcomes'] if o['id']==identifier] if reveal else None,
          'exact_result':evaluate(p['observation'],p['claim']) if reveal else None}
    def preview(self,phase,identifier,text):
        if not isinstance(text,str) or len(text)>1024:raise ValueError('Claim entry too large.')
        claim=json.loads(text);p=self.packet(phase,identifier);validate(p['observation'],claim)
        return {'schema':'explicit-claim-preview-1','phase':phase,'source_card':identifier,'source_observation_sha256':t.sha(t.encoded(p['observation'])),
          'claim':claim,'canonical':canonical(claim),'exact_result':evaluate(p['observation'],claim),'prospective_jev_request':request(p['observation'],claim),
          'provider_calls':0,'server_writes':0,'human_review_recorded':False,'status':'local_draft',
          'note':'This preview evaluates fields directly. It is not a Jev response, independent review or completed analyst entry study.'}
