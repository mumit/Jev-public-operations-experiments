"""Read-only whole-report transfer comparison with hidden references."""
from pathlib import Path
from .paths import ROOT
from . import report_knowledge_trial as trial
from . import report_knowledge_data as data
from .report_knowledge_features import ARMS
from .hosted import encoded
from .report_source_audit import digest

class ReportKnowledgeStudy:
    def __init__(self,root=ROOT):self.root=Path(root)
    def overview(self):
        if self.root.resolve()!=ROOT.resolve():raise ValueError('Evidence belongs to this checkout.')
        result=trial.verify(local=False);packets,_=data.packets(local=False)
        return {'claims':packets,'arms':list(ARMS),'results':{k:v for k,v in result.items() if k!='outcomes'},
            'exact_input_available':(trial.LOCAL/'requests.json').exists(),'source_cautions':{}}
    def claim(self,identifier,n=1,reveal=False,input_arm=None):
        if n not in (1,2,3) or input_arm is not None and input_arm not in ARMS:raise ValueError('Unknown selection.')
        result=trial.verify(local=False);packets,refs=data.packets(local=False)
        packet=next(p for p in packets if p['id']==identifier);rows,_=trial.rows(local=False)
        outcomes={o['arm']:{'prediction':o['prediction'],'literal_rule':o['literal_rule'],
            **({k:o[k] for k in ('correct_display','wrong_display','correct_choice','withheld')} if reveal else {})}
            for o in result['outcomes'] if o['id']==identifier and o['round']==n}
        request=None;path=trial.LOCAL/'requests.json'
        if input_arm and path.exists():
            job=next(j for j in data.load(path) if j['claim_id']==identifier and j['round']==n and j['arm']==input_arm)
            frozen=next(j for j in trial.check(local=False)['requests'] if j['id']==job['id'])
            if digest(encoded(job['body']))!=frozen['request_sha256']:raise ValueError('Exact local request changed.')
            request=job['body']
        return {'claim':packet,'round':n,'outcomes':outcomes,'rows':{a:next((r for r in rows if r['claim_id']==identifier and r['round']==n and r['arm']==a),None) for a in ARMS},
            'reference':next(r for r in refs if r['id']==identifier) if reveal else None,'request':request,
            'exact_input_available':path.exists(),'human_entries':0,'new_inference_calls':0}
