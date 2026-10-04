"""Read-only inspector for complete selective-policy stages; answers require reveal."""
import copy,json
from pathlib import Path
from .public_rca_stages import load,committed
from .public_rca_models import FEATURES
from .public_selective_data import folder
from .public_selective_trial import BOUNDARY,RESULTS,score,verified_rows,output
from .public_confirmation_trial import RESULTS as CONFIRMATION_RESULTS,score as confirmation_score,verified_rows as confirmation_rows,output as confirmation_output
from .public_confirmation_data import folder as confirmation_folder

CONFIRMATIONS={'train-ticket-reserve':'Train Ticket','sock-shop-reserve':'Sock Shop'}

class PublicSelectiveStudy:
    def __init__(self,root):self.root=Path(root)

    def verified(self,split):
        if split in CONFIRMATIONS:
            committed(CONFIRMATION_RESULTS);confirmation_rows('confirmation',complete=True);a=confirmation_score()
            if a!=load(CONFIRMATION_RESULTS) or a['failed_or_missing']:raise ValueError('Confirmation assessment failed recomputation.')
            return a['datasets'][CONFIRMATIONS[split]]
        if split not in ('calibration','evaluation'):raise ValueError('Unknown selective split.')
        path=BOUNDARY if split=='calibration' else RESULTS;committed(path);verified_rows(split,complete=True)
        recorded=load(path);assessment=recorded['assessment'] if split=='calibration' else recorded
        if score(split)!=assessment or assessment['failed_or_missing']:raise ValueError('Selective assessment failed recomputation.')
        return assessment

    def overview(self):
        stages={};notes=[]
        for split in ('calibration','evaluation',*CONFIRMATIONS):
            try:a=self.verified(split)
            except (OSError,ValueError,KeyError):notes.append(split.capitalize()+' results are unavailable until complete recorded evidence matches its committed assessment.');continue
            cases={r['id']:r for r in a['selective']['outcomes']}
            stages[split]={'cases':[{'id':r['id'],'fault':r['fault']} for r in cases.values()],
                'selected_policy':a['selective']['policy'],'selected':a['selective']['per_round'],'stable_display_cases':a['selective']['stable_display_cases'],
                'comparators':{k:v['per_round'] for k,v in a['comparators'].items()},'original_shortlist':a['original_shortlist'],'controls':a['controls'],
                'groups':a['groups'],'curves':a['curves']}
        return {'available':bool(stages),'stages':stages,'notes':notes,'condition':'Known incident boundary, controlled application faults, one published injected service per case. Repeats are not independent cases.'}

    def case(self,split,identifier,reveal=False):
        a=self.verified(split);outcomes=[copy.deepcopy(r) for r in a['selective']['outcomes'] if r['id']==identifier]
        if not outcomes:raise ValueError('Unknown selective case.')
        reference={'target':outcomes[0]['target'],'fault':outcomes[0]['fault']} if reveal else None
        if not reveal:
            for row in outcomes:
                for key in ('target','group','correct_first','cause_included','wrong_leads','raw_correct_first'):row.pop(key)
        data=confirmation_folder('confirmation') if split in CONFIRMATIONS else folder(split)
        run=confirmation_output() if split in CONFIRMATIONS else output(split)
        packet=next(r for r in load(data/'inputs.json') if r['id']==identifier)
        responses=[json.loads(line) for line in (run/'responses.jsonl').read_text().splitlines()]
        return {'id':identifier,'split':split,'outcomes':outcomes,'policy':a['selective']['policy'],'reference':reference,
            'request':packet['request'],'state':json.loads(packet['request']['state']),
            'responses':[r for r in responses if r['case_id']==identifier],
            'controls':load(run/'controls.json')[identifier],'ml_features':FEATURES}
