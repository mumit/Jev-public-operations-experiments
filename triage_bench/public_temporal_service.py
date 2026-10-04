"""Inspect complete, recomputed development evidence; GET never calls a provider."""
import copy,json
from pathlib import Path
from .public_rca_stages import load,committed
from .public_rca_models import FEATURES
from .public_temporal_trial import DATA,PROTOCOL,OUTPUT,score,ARMS


class PublicTemporalStudy:
    def __init__(self,root):
        self.root=Path(root);self.assessment=self.root/'checkpoints/public-temporal-development-results-2026-10-04.json'

    def verified(self):
        committed(PROTOCOL);committed(self.assessment)
        if load(OUTPUT/'summary.json')['status']!='completed':raise ValueError('Complete development evidence required.')
        result=score()
        if result!=load(self.assessment) or result['failed_or_missing']:raise ValueError('Unverified development assessment.')
        return result

    def overview(self):
        result={'available':False,'notes':[],'cases':[],'metrics':{},'controls':{}}
        try:assessment=self.verified()
        except (OSError,ValueError,KeyError):
            result['notes']=['Verified temporal development evidence is unavailable locally. The original public-study-v1 bundle does not include this later run. No results have been fabricated.'];return result
        result.update(available=True,cases=[{'id':c['id'],'fault':c['fault']} for c in assessment['cases']],metrics=assessment['metrics'],controls=assessment['controls'],paired=assessment['paired'],
            condition='18 development cases, six correlated groups, 68 observed services per case. Three repeated rounds are not independent held-out cases.',next_gate=assessment['next_gate'])
        return result

    def case(self,identifier,arm='named',reveal=False):
        if arm not in ARMS:raise ValueError('Unknown development arm.')
        assessment=self.verified();source=next((c for c in assessment['cases'] if c['id']==identifier),None)
        if source is None:raise ValueError('Unknown development case.')
        case=copy.deepcopy(source)
        if not reveal:
            case.pop('target');case.pop('group')
            for data in case['arms'].values():
                for r in data['rounds']:
                    for key in ('top1_correct','target_in_shortlist','wrong_leads'):r.pop(key)
        packet=next(p for p in load(DATA/'development.inputs.json') if p['id']==identifier)
        rows=[json.loads(line) for line in (OUTPUT/'responses.jsonl').read_text().splitlines()]
        return {'case':case,'arm':arm,'request':packet['requests'][arm],
            'named_state':json.loads(packet['requests']['named']['state']),
            'added_windows':json.loads(packet['requests']['temporal']['state'])['latency_time_windows'],
            'responses':[r for r in rows if r['case_id']==identifier and r['arm']==arm],
            'controls':load(OUTPUT/'controls.json')[identifier],'ml_features':FEATURES,
            'reference':{'target':source['target'],'fault':source['fault']} if reveal else None}
