"""Read-only inspection of committed, recomputed replay evidence."""
import copy
from pathlib import Path
from .public_rca_stages import load,committed
from .public_repeat_results import score,verified_rows
from .public_repeat_trial import ARMS,DATA


class PublicRepeatStudy:
    def __init__(self,root):
        self.root=Path(root)
        self.protocol=self.root/'checkpoints/public-repeat-protocol-2026-10-03.json'
        self.assessment=self.root/'checkpoints/public-repeat-results-2026-10-03.json'
        self.folder=self.root/'runs/public-repeat/diagnostic-2026-10-03-v1'

    def verified(self):
        committed(self.protocol);committed(self.assessment)
        protocol,rows=verified_rows(self.protocol,self.folder,complete=True)
        result=score(self.protocol,self.folder)
        if result!=load(self.assessment):raise ValueError('Replay assessment differs from actual evidence.')
        return protocol,rows,result

    def overview(self):
        result={'available':False,'notes':[],'cases':[],'metrics':{},'research_gate':None}
        try:protocol,rows,assessment=self.verified()
        except (OSError,ValueError,KeyError):
            result['notes']=['Verified replay evidence is unavailable locally. Restore its separate evidence bundle when published. No predictions have been fabricated.']
            return result
        result.update(available=True,distinct_cases=assessment['distinct_cases'],distinct_groups=assessment['distinct_groups'],
            rounds=protocol['rounds'],planned=protocol['maximum_calls'],thresholds=protocol['thresholds'],
            metrics=assessment['metrics'],research_gate=assessment['research_gate'],comparisons=assessment['comparisons'])
        for case in assessment['cases']:
            result['cases'].append({k:case[k] for k in ('id','split','role','fault')})
        return result

    def case(self,identifier,arm='named',reveal=False):
        if arm not in ARMS:raise ValueError('Unknown replay arm.')
        protocol,rows,assessment=self.verified()
        source=next((c for c in assessment['cases'] if c['id']==identifier),None)
        if source is None:raise ValueError('Unknown replay case.')
        case=copy.deepcopy(source)
        if not reveal:
            case.pop('target');case.pop('group')
            for data in case['arms'].values():
                data['original'].pop('correct');data.pop('wrong_displayed')
                for repeat in data['repeats']:repeat.pop('correct')
        requests=load(self.folder/'requests.json')
        request=next(r for r in requests if r['case_id']==identifier and r['arm']==arm)
        historical=self.root/f"runs/public-format/{case['split']}-2026-10-03-v1/responses.jsonl"
        import json
        original=next(json.loads(line) for line in historical.read_text().splitlines() if json.loads(line)['id']==identifier+'::'+arm)
        selected=[r for r in rows if r['case_id']==identifier and r['arm']==arm]
        return {'case':case,'arm':arm,'threshold':protocol['thresholds'][arm],
            'request':request['body'],'request_sha256':request['request_sha256'],
            'original_response':original,'responses':selected,'reference':{'target':source['target'],'fault':source['fault']} if reveal else None}
