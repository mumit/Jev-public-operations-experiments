"""Inspect saved presentation arms; evaluating or browsing cannot call Jev."""
from pathlib import Path

from .public_rca_stages import load,verify_hosted,verify_local
from .public_rca_models import infer
from .public_format_data import ARMS,transform
from .public_format_trial import body,check,ROOT
from .public_format_stages import gate,score


class PublicFormatStudy:
    def __init__(self,root):
        self.root=Path(root)
        self.data=self.root/'runs/public-data/input-format-2026-10-03-v1'
        self.protocol=self.root/'checkpoints/public-format-protocol-2026-10-03.json'
        self.candidate=self.root/'checkpoints/public-format-candidate-2026-10-03.json'
        self.boundary=self.root/'checkpoints/public-format-boundary-2026-10-03.json'

    def overview(self):
        protocol=load(self.protocol)
        result={'counts':protocol['counts'],'condition':'Known injection boundary; paired input presentation only. Online Boutique development, Sock Shop calibration and evaluation. No incident detector.',
            'available_splits':[],'cases':{},'results':{},'notes':[],'boundary':{},'boundary_results':[],
            'data_available':False,'arms':list(ARMS),
            'methods':{'change':'Change ranking','resource':'Resource ranking','ml':'ML · frozen transfer',
                       'compact':'Jev · compact','named':'Jev · named','explained':'Jev · explained'}}
        if not (self.data/'manifest.json').exists():
            result['notes'].append('The new public input pack is unavailable locally. No predictions have been fabricated.');return result
        try:check(protocol,self.data)
        except (OSError,KeyError,ValueError):
            result['notes'].append('Data, source or fitted-control verification failed. Inspection is unavailable.');return result
        result['data_available']=True
        for split in ('development','calibration','evaluation'):
            hosted=self.root/f'runs/public-format/{split}-2026-10-03-v1'
            try:
                if split!='development':gate(self.data,self.protocol,split,self.candidate,self.boundary)
                if split=='evaluation':verify_hosted(hosted,self.protocol,split)
                result['cases'][split]=[r['id'] for r in load(self.data/f'{split}.inputs.json')]
                result['available_splits'].append(split)
                if (hosted/'summary.json').exists():
                    assessment=score(self.data,self.protocol,hosted,split)
                    result['results'][split]={k:v for k,v in assessment.items() if k!='outcomes'}
            except (OSError,KeyError,ValueError):pass
        if self.boundary.exists() and 'calibration' in result['results']:
            try:gate(self.data,self.protocol,'evaluation',self.candidate,self.boundary)
            except (OSError,KeyError,ValueError):
                result['notes'].append('The display boundary failed verification; no threshold is shown.')
                return result
            result['boundary']=load(self.boundary)['selected']
            for split,assessment in result['results'].items():
                for arm,selected in result['boundary'].items():
                    row=next(r for r in assessment['curves'][arm] if r['threshold']==selected['threshold']) if selected else {'threshold':None,'suggestions':0,'wrong':0,'review':protocol['counts'][split]}
                    result['boundary_results'].append({'split':split,'arm':arm,**row})
        return result

    def case(self,split,identifier,arm='compact',reveal=False):
        overview=self.overview()
        if split not in overview['available_splits']:raise ValueError('This split is sealed or unavailable.')
        if arm not in ARMS:raise ValueError('Unknown input arm.')
        packet=next((r for r in load(self.data/f'{split}.inputs.json') if r['id']==identifier),None)
        if packet is None:raise ValueError('Unknown public case.')
        protocol=load(self.protocol)
        model=verify_local(ROOT/protocol['local'],ROOT/protocol['historical_data'])
        result={'id':identifier,'split':split,'arm':arm,'state':packet['state'],'presentation':transform(packet['state'],arm),
            'request':body(packet['state'],arm),'base_request':body(packet['state'],'compact'),
            'local':infer(packet['state'],model),'features':model['features'],'ml_intercept':model['intercept'],
            'jev':None,'jev_all':{},'reference':None,'boundary':overview['boundary'].get(arm)}
        hosted=self.root/f'runs/public-format/{split}-2026-10-03-v1'
        if (hosted/'summary.json').exists():
            rows=verify_hosted(hosted,self.protocol,split,require_complete=False)
            result['jev_all']={a:next((r for r in rows if r['id']==identifier+'::'+a),None) for a in ARMS}
            result['jev']=result['jev_all'][arm]
        if reveal:result['reference']=next(r for r in load(self.data/f'{split}.references.json') if r['id']==identifier)
        return result
