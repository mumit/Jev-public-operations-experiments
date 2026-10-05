"""Read-only paired report inspection with explicit reference reveal."""
import copy,json
from pathlib import Path
from .public_rca_stages import load,committed
from .public_report_data import DATA
from .public_report_trial import RESULT,OUTPUT,score
class PublicReportStudy:
    def __init__(self,root):self.root=Path(root)
    def verified(self):
        committed(RESULT);assessment=score()
        if assessment!=load(RESULT):raise ValueError('Report assessment drift.')
        return assessment
    def overview(self):
        try:result=copy.deepcopy(self.verified())
        except (OSError,ValueError,KeyError):return {'available':False,'notes':['Verified report diagnostic is unavailable.']}
        packets=load(DATA/'inputs.json')
        for name,panel in result['datasets'].items():
            panel['report_choices']=[{'id':p['id'],'services':[o['service'] for o in p['observations']]} for p in packets if p['dataset']==name]
            panel.pop('pairs');panel['stable_fix_count']=len(panel.pop('stable_fixes'));panel['stable_loss_count']=len(panel.pop('stable_losses'))
            for arm in panel['arms'].values():arm.pop('outcomes')
        return {'available':True,**result}
    def card(self,identifier,reveal=False):
        result=self.verified();packet=next(p for p in load(DATA/'inputs.json') if p['id']==identifier);outcomes={}
        for arm,v in result['datasets'][packet['dataset']]['arms'].items():
            outcomes[arm]=[copy.deepcopy(o) for o in v['outcomes'] if o['id']==identifier]
            if not reveal:
                for o in outcomes[arm]:
                    for k in ('reference','correct','unknown_to_decisive'):o.pop(k)
        rows=[json.loads(l) for l in (OUTPUT/'responses.jsonl').read_text().splitlines()]
        return {**packet,'outcomes':outcomes,'responses':[r for r in rows if r['card_id']==identifier],
                'reference':next(r for r in load(DATA/'references.json') if r['id']==identifier) if reveal else None}
