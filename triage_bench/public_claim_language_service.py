"""Read-only wording study with separate reference reveal."""
import copy,json
from pathlib import Path
from .public_rca_stages import load,committed
from .public_claim_language_data import DATA
from .public_claim_language_trial import RESULT,OUTPUT,score

class PublicClaimLanguageStudy:
    def __init__(self,root):self.root=Path(root)
    def verified(self):
        committed(RESULT);assessment=score()
        if assessment!=load(RESULT):raise ValueError('Language assessment changed.')
        return assessment
    def overview(self):
        try:assessment=self.verified()
        except (OSError,ValueError,KeyError):return {'available':False,'notes':['Verified wording diagnostic is unavailable.']}
        result=copy.deepcopy(assessment);packets=load(DATA/'inputs.json')
        for name,panel in result['datasets'].items():
            panel['proposition_choices']=[{'id':p['id'],'service':p['observation']['service'],'selection':p['selection'],'canonical':p['statements'][p['form_fields']['canonical']]} for p in packets if p['dataset']==name]
            panel.pop('pairs');panel['stable_fix_count']=len(panel.pop('stable_fixes'));panel['stable_loss_count']=len(panel.pop('stable_losses'))
            for form in panel['forms'].values():form.pop('outcomes');form['stable_correct_count']=len(form.pop('stable_correct_ids'))
        return {'available':True,**result}
    def card(self,identifier,reveal=False):
        assessment=self.verified();packet=next(p for p in load(DATA/'inputs.json') if p['id']==identifier);outcomes={}
        for form,result in assessment['datasets'][packet['dataset']]['forms'].items():
            outcomes[form]=[copy.deepcopy(r) for r in result['outcomes'] if r['id']==identifier]
            if not reveal:
                for r in outcomes[form]:
                    for f in ('reference','correct','false_displayed_support','false_displayed_contradiction','unknown_to_decisive','correct_displayed_support'):r.pop(f)
        rows=[json.loads(l) for l in (OUTPUT/'responses.jsonl').read_text().splitlines()]
        ref=next(r for r in load(DATA/'references.json') if r['id']==identifier) if reveal else None
        return {**packet,'outcomes':outcomes,'responses':[r for r in rows if r['card_id']==identifier],'reference':ref}
