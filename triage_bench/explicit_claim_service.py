"""Read-only claim entry preview and verified experiment inspection."""
import copy,json
from . import explicit_claim_trial as t,explicit_format_trial as formats
from .explicit_claim_features import validate,canonical,evaluate,request
from .explicit_format_features import request as format_request,statement

class ExplicitClaimStudy:
    def __init__(self,root):self.root=root;self._cache={}
    def data_phase(self,phase):
        if phase not in ('development','confirmation','format'):raise ValueError('Unknown claim phase.')
        return 'development' if phase=='format' else phase
    def verified(self,phase):
        source=self.data_phase(phase);trial=formats if phase=='format' else t
        result_path=formats.result_path() if phase=='format' else t.result_path(phase)
        paths=[trial.PLAN,result_path,trial.protocol_path(source),t.PLAN,*(self.root/n for n in trial.SOURCES),*(self.root/n for n in t.load(trial.PLAN)['evidence_sha256']),*t.data.folder(source).rglob('*'),*trial.output(source).rglob('*')]
        sig=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if phase not in self._cache or self._cache[phase][0]!=sig:self._cache[phase]=(sig,formats.verify() if phase=='format' else t.verify(phase))
        return self._cache[phase][1]
    def overview(self,phase='development'):
        try:r=copy.deepcopy(self.verified(phase))
        except (OSError,ValueError,KeyError):return {'available':False,'error':'This phase needs its recorded evidence and committed assessment.'}
        r.pop('outcomes');source=self.data_phase(phase)
        if phase=='format':
            selected=[p for p in r['panels'] if p['arm']=='calculated']
            r.update(phase='format',passes=r['candidate_passes'],opportunities=750,correct_answers=sum(p['correct'] for p in selected),correct_displays=sum(p['correct_display'] for p in selected),wrong_displays=sum(p['wrong_display'] for p in selected),rule_correct=750)
        cards=[{'id':p['id'],'dataset':p['dataset'],'category':p['category'],'kind':p['claim']['kind'],'service':p['claim']['service'],'asserted':p['claim']['asserted'],'recording':p['recording']} for p in t.load(t.data.folder(source)/'inputs.json')]
        phases=['development']+(['format'] if formats.result_path().exists() else [])+(['confirmation'] if t.result_path('confirmation').exists() else [])
        return {'available':True,'cards':cards,'phases':phases,**r}
    def packet(self,phase,identifier):
        source=self.data_phase(phase);t.data.validate_pack(source,t.check_plan)
        try:return next(p for p in t.load(t.data.folder(source)/'inputs.json') if p['id']==identifier)
        except StopIteration as e:raise ValueError('Unknown explicit claim.') from e
    def card(self,phase,identifier,reveal=False):
        result=self.verified(phase);p=self.packet(phase,identifier);source=self.data_phase(phase);trial=formats if phase=='format' else t
        return {**p,'canonical':canonical(p['claim']),
          'jobs':[j for j in t.load(trial.output(source)/'requests.json') if j['card_id']==identifier],
          'responses':[r for r in map(json.loads,(trial.output(source)/'responses.jsonl').read_text().splitlines()) if r['card_id']==identifier],
          'reference':next(r for r in t.load(t.data.folder(source)/'references.json') if r['id']==identifier) if reveal else None,
          'outcomes':[o for o in result['outcomes'] if o['id']==identifier] if reveal else None,
          'exact_result':evaluate(p['observation'],p['claim']) if reveal else None}
    def preview(self,phase,identifier,text,arm='typed'):
        if not isinstance(text,str) or len(text)>1024:raise ValueError('Claim entry too large.')
        if arm not in ('typed','focused','calculated') or (phase!='format' and arm!='typed'):raise ValueError('Unknown preview representation.')
        claim=json.loads(text);p=self.packet(phase,identifier);validate(p['observation'],claim)
        return {'schema':'explicit-claim-preview-1','phase':phase,'arm':arm,'source_card':identifier,'source_observation_sha256':t.sha(t.encoded(p['observation'])),
          'claim':claim,'canonical':canonical(claim) if arm=='typed' else statement(claim),'exact_result':evaluate(p['observation'],claim),'prospective_jev_request':format_request(p['observation'],claim,arm),
          'provider_calls':0,'server_writes':0,'human_review_recorded':False,'status':'local_draft',
          'note':'This preview evaluates fields directly. It is not a Jev response, independent review or completed analyst entry study.'}
