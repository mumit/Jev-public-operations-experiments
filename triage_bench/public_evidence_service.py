"""Read-only numerical evidence assessment, with explicit reference reveal."""
import copy,json
from pathlib import Path
from .public_rca_stages import load,committed
from .public_evidence_data import DATA
from .public_evidence_trial import RESULT,OUTPUT,score


class PublicEvidenceStudy:
    def __init__(self,root):self.root=Path(root)
    def verified(self):
        committed(RESULT);assessment=score()
        if assessment!=load(RESULT):raise ValueError('Evidence assessment changed.')
        return assessment
    def overview(self):
        try:assessment=self.verified()
        except (OSError,ValueError,KeyError):return {'available':False,'notes':['Verified evidence-assessment results are unavailable.']}
        result=copy.deepcopy(assessment);packets=load(DATA/'inputs.json')
        for name,panel in result['datasets'].items():
            panel['card_choices']=[{'id':p['id'],'service':p['observation']['service'],'case_id':p['case_id'],'selection':p['selection']} for p in packets if p['dataset']==name]
            panel['card_ids']=list(dict.fromkeys(r['id'] for r in panel.pop('pairs')))
            panel['stable_fix_count']=len(panel.pop('stable_fixes'));panel['stable_loss_count']=len(panel.pop('stable_losses'))
            for arm in panel['arms'].values():arm.pop('outcomes')
        return {'available':True,**result}
    def card(self,identifier,reveal=False):
        assessment=self.verified();packet=next(p for p in load(DATA/'inputs.json') if p['id']==identifier)
        source=assessment['datasets'][packet['dataset']];outcomes={}
        for arm,result in source['arms'].items():
            outcomes[arm]=[copy.deepcopy(r) for r in result['outcomes'] if r['id']==identifier]
            if not reveal:
                for row in outcomes[arm]:
                    for field in ('field_correct','all_correct','reference_composition','composition_correct','false_displayed_support','correct_displayed_support'):row.pop(field)
        rows=[json.loads(line) for line in (OUTPUT/'responses.jsonl').read_text().splitlines()]
        ref=next(r for r in load(DATA/'references.json') if r['id']==identifier) if reveal else None
        return {**packet,'outcomes':outcomes,'responses':[r for r in rows if r['card_id']==identifier],'reference':ref}
