"""Read-only inspection of the completed, committed disagreement experiment."""
import copy,json
from pathlib import Path
from .public_rca_stages import load,committed
from .public_rca_models import FEATURES
from .public_agreement_trial import RESULTS,score,verified_rows,output
from .public_agreement_data import folder

class PublicAgreementStudy:
    def __init__(self,root):self.root=Path(root)
    def verified(self):
        committed(RESULTS);verified_rows('evaluation',complete=True);a=score()
        if a!=load(RESULTS) or a['failed_or_missing']:raise ValueError('Agreement assessment failed recomputation.')
        return a
    def overview(self):
        try:a=self.verified()
        except (OSError,ValueError,KeyError):return {'available':False,'notes':['Disagreement results are unavailable until complete recorded evidence matches the committed assessment.']}
        datasets={}
        for name,panel in a['datasets'].items():
            cases={r['id']:[] for r in panel['routing']['outcomes']}
            for r in panel['routing']['outcomes']:cases[r['id']].append(r['action'])
            datasets[name]={**{k:v for k,v in panel.items() if k!='routing'},'cases':[{'id':i,'actions':actions} for i,actions in cases.items()],
                'rounds':panel['routing']['per_round'],'stable_display_cases':panel['routing']['stable_display_cases'],'research_gate':panel['routing']['research_gate'],'gate_definition':panel['routing']['gate_definition']}
        return {'available':True,'datasets':datasets,'policy':a['policy'],'condition':'New RE1 recordings of familiar applications and fault types. Supplied incident boundaries and published injected-service references. Repeats are not independent incidents. Agreement does not establish correctness.'}
    def case(self,dataset,identifier,reveal=False):
        a=self.verified()
        if dataset not in a['datasets']:raise ValueError('Unknown application.')
        outcomes=[copy.deepcopy(r) for r in a['datasets'][dataset]['routing']['outcomes'] if r['id']==identifier]
        if not outcomes:raise ValueError('Unknown disagreement case.')
        ref={'target':outcomes[0]['target'],'fault':outcomes[0]['fault']} if reveal else None
        if not reveal:
            for row in outcomes:
                for key in ('group','target','fault','base_correct','retained_correct','base_wrong','retained_wrong','raw_correct','ml_correct'):row.pop(key)
        packet=next(r for r in load(folder()/'inputs.json') if r['id']==identifier)
        responses=[json.loads(line) for line in (output()/'responses.jsonl').read_text().splitlines()]
        return {'id':identifier,'dataset':dataset,'outcomes':outcomes,'reference':ref,'policy':a['policy'],'request':packet['request'],'state':json.loads(packet['request']['state']),
            'responses':[r for r in responses if r['case_id']==identifier],'controls':load(output()/'controls.json')[identifier],'ml_features':FEATURES}
