"""Read-only public study inspection; no calls and guarded later splits."""
import json
from pathlib import Path
from triage_bench.public_rca_trial import check,body
from triage_bench.public_rca_stages import gate,verify_hosted,verify_local,score
from triage_bench.public_rca_models import infer


class PublicRCAStudy:
    def __init__(self,root):
        self.root=Path(root)
        self.data=self.root/'runs/public-data/metric-study-2026-10-03-v2'
        self.protocol=self.root/'checkpoints/public-rca-protocol-2026-10-03.json'
        self.candidate=self.root/'checkpoints/public-rca-candidate-2026-10-03.json'
        self.boundary=self.root/'checkpoints/public-rca-boundary-2026-10-03.json'
        self.local=self.root/'runs/public-rca/local-2026-10-03-v1'
        self.cache={}

    def overview(self):
        protocol=json.loads(self.protocol.read_text())
        overview={'counts':protocol['counts'],'condition':protocol['condition'],
                  'available_splits':[],'cases':{},'results':{},'notes':[],
                  'methods':{'change':'Change ranking','resource':'Resource ranking','ml':'Trained ML','jev':'Jev'},
                  'boundary':None,'boundary_results':{},'data_available':False}
        if not (self.data/'manifest.json').exists():
            overview['notes'].append('Local public-data files are unavailable. Restore or prepare the frozen pack; missing results remain unavailable.')
            return overview
        try:check(protocol,self.data)
        except (OSError,ValueError,KeyError):
            overview['notes'].append('Source or data verification failed. Inspection is unavailable rather than showing changed evidence.')
            return overview
        overview['data_available']=True
        for split in ('train','development','calibration','evaluation'):
            try:
                if split in ('calibration','evaluation'):
                    gate(self.data,self.protocol,split,self.candidate,self.boundary)
                hosted=self.root/f'runs/public-rca/{split}-2026-10-03-v1'
                if split=='evaluation':verify_hosted(hosted,self.protocol,split)
                overview['available_splits'].append(split)
                packets=json.loads((self.data/f'{split}.inputs.json').read_text())
                overview['cases'][split]=[r['id'] for r in packets]
                if (hosted/'summary.json').exists():
                    result=score(self.data,self.protocol,self.local,hosted,split)
                    overview['results'][split]={k:v for k,v in result.items() if k not in {'outcomes','comparisons'}}
            except (OSError,ValueError,KeyError):
                if split in ('train','development'):
                    overview['notes'].append('Local/hosted evidence could not verify. Model results are unavailable.')
        if self.boundary.exists() and 'calibration' in overview['results']:
            try:gate(self.data,self.protocol,'evaluation',self.candidate,self.boundary)
            except (OSError,KeyError,ValueError):
                overview['notes'].append('Display boundary verification failed.');return overview
            overview['boundary']=json.loads(self.boundary.read_text())['selected']
            if overview['boundary']:
                threshold=overview['boundary']['threshold']
                for split,result in overview['results'].items():
                    overview['boundary_results'][split]=next(row for row in result['curves'] if row['threshold']==threshold)
        return overview

    def case(self,split,identifier,reveal=False):
        overview=self.overview()
        if split not in overview['available_splits']:raise ValueError('This split is sealed or unavailable.')
        packets=json.loads((self.data/f'{split}.inputs.json').read_text());packet=next((r for r in packets if r['id']==identifier),None)
        if not packet:raise ValueError('Unknown public case.')
        result={'id':identifier,'split':split,'state':packet['state'],'request':body(packet['state']),
                'local':None,'jev':None,'reference':None,'features':None}
        try:
            model=verify_local(self.local,self.data);result['local']=infer(packet['state'],model)
            result['features']=model['features'];result['ml_intercept']=model['intercept']
        except (OSError,ValueError,KeyError):pass
        hosted=self.root/f'runs/public-rca/{split}-2026-10-03-v1'
        if (hosted/'summary.json').exists():
            rows=verify_hosted(hosted,self.protocol,split,require_complete=False)
            result['jev']=next((r for r in rows if r['id']==identifier),None)
        if reveal:
            refs=json.loads((self.data/f'{split}.references.json').read_text())
            result['reference']=next(r for r in refs if r['id']==identifier)
        return result
