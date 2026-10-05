"""Read-only binding study; individual provider responses stay separate."""
import copy,json
from pathlib import Path
from .public_rca_stages import load,committed
from .public_binding_data import DATA
from .public_binding_trial import RESULT,OUTPUT,score
from .public_report_trial import RESULT as HISTORICAL_RESULT,OUTPUT as HISTORICAL_OUTPUT
class PublicBindingStudy:
    def __init__(self,root):self.root=Path(root)
    def verified(self):
        committed(RESULT);assessment=score()
        if assessment!=load(RESULT):raise ValueError('Binding assessment drift.')
        return assessment
    def overview(self):
        try:result=copy.deepcopy(self.verified())
        except (OSError,ValueError,KeyError):return {'available':False,'notes':['Verified binding diagnostic is unavailable.']}
        packets=load(DATA/'inputs.json')
        for name,panel in result['datasets'].items():
            panel['report_choices']=[{'id':p['id'],'services':[o['service'] for o in p['observations']]} for p in packets if p['dataset']==name]
            pairs=panel.pop('pairs')
            for edge,v in panel['steps'].items():
                v['stable_fix_count']=len(v.pop('stable_fixes'));v['stable_loss_count']=len(v.pop('stable_losses'))
                v['round_changes']=[{'round':n,'fixes':sum(o['fix'] for o in pairs if o['edge']==edge and o['round']==n),'losses':sum(o['loss'] for o in pairs if o['edge']==edge and o['round']==n)} for n in (1,2,3)]
            for arm in panel['arms'].values():arm.pop('outcomes')
        return {'available':True,**result}
    def card(self,identifier,reveal=False):
        result=self.verified();packet=next(p for p in load(DATA/'inputs.json') if p['id']==identifier);outcomes={}
        for arm,v in result['datasets'][packet['dataset']]['arms'].items():outcomes[arm]=[copy.deepcopy(o) for o in v['outcomes'] if o['id']==identifier]
        historical=copy.deepcopy([o for o in load(HISTORICAL_RESULT)['datasets'][packet['dataset']]['arms']['report']['outcomes'] if o['id']==identifier])
        if not reveal:
            for o in historical+[o for group in outcomes.values() for o in group]:
                for k in ('reference','correct','unknown_to_decisive'):o.pop(k)
        rows=[json.loads(l) for l in (OUTPUT/'responses.jsonl').read_text().splitlines()]
        oldrows=[json.loads(l) for l in (HISTORICAL_OUTPUT/'responses.jsonl').read_text().splitlines()]
        return {**packet,'outcomes':outcomes,'responses':[r for r in rows if r['card_id']==identifier],'historical_outcomes':historical,
                'historical_responses':[r for r in oldrows if r['card_id']==identifier and r['arm']=='report'],
                'reference':next(r for r in load(DATA/'references.json') if r['id']==identifier) if reveal else None}
