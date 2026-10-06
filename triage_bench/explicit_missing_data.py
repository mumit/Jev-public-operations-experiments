"""Prepare a new pack from preserved sources, without reopening protected data."""
import json
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load
from .public_rca_data import dump
from . import explicit_native_v2_data as previous, explicit_claim_data as original
from .explicit_preparation_audit import verify as verify_failures, AUDIT
from .explicit_missing_features import observations

PLAN=ROOT/'checkpoints/explicit-missing-plan-2026-10-06.json'
BASE=ROOT/'runs/explicit-missing'
DATA=BASE/'confirmation-data-2026-10-06-v1'

def reconstruct(plan):
    import pyarrow.parquet as pq
    index={r['case']:r for r in pq.read_table(original.INDEX).to_pylist()}; rows=[];coverage=[]
    for a in plan['assignments']:
        directory=previous.DATA/'raw'/a['id'];boundary=int((directory/'inject_time.txt').read_text());r=index[a['source_case']]
        if boundary!=r['inject_time'] or r['has_traces']:raise ValueError('Pinned incident condition changed.')
        services,windows,counts=observations(pq.read_table(directory/'metrics.parquet').to_pydict(),boundary)
        if counts!={'before':r['normal_timesteps'],'after':r['faulty_timesteps']}:raise ValueError('Actual window counts differ from index.')
        missing=not counts['before'] or not counts['after']
        coverage.append({'recording':a['id'],'window_rows':counts,'window_seconds':windows,'missing_window':missing})
        names=sorted(services,key=lambda s:sha(('explicit-services/'+r['case']+'/'+s).encode()))[:2]
        if len(names)!=2:raise ValueError('Two observed services required.')
        for i,s in enumerate(names):
            o={'service':s,'metrics':services[s],'trace':None,'window_seconds':windows}
            rows.extend(original.entries(o,a['id']+'-'+str(i),a['dataset'],a['id'],'missing_window' if missing else 'complete_windows'))
    return rows,coverage

def prepare(check_plan):
    p=check_plan();verify_failures()
    if DATA.exists():raise ValueError('Never overwrite the new missing-window pack.')
    rows,coverage=reconstruct(p)
    if len(rows)!=360 or sum(r['missing_window'] for r in coverage)!=1:raise ValueError('Frozen complete/missing allocation changed.')
    refs=original.references(rows)
    if any(r['answer']!='unanswerable' for r,p in zip(refs,rows) if p['category']=='missing_window'):raise ValueError('Missing window must leave both polarities unknown.')
    DATA.mkdir(parents=True);dump(DATA/'inputs.json',rows);dump(DATA/'references.json',refs);dump(DATA/'coverage.json',coverage)
    m={'schema':'explicit-missing-data-1','claims':360,'recordings':15,'previously_opened_recordings':15,'new_recordings':0,'downloads':0,'missing_window_recordings':1,'plan_sha256':sha(PLAN.read_bytes()),'source_audit_sha256':sha(AUDIT.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json','coverage.json')}}
    dump(DATA/'manifest.json',m);validate(check_plan);return m

def validate(check_plan):
    p=check_plan();verify_failures();m=load(DATA/'manifest.json')
    expected={'schema':'explicit-missing-data-1','claims':360,'recordings':15,'previously_opened_recordings':15,'new_recordings':0,'downloads':0,'missing_window_recordings':1,'plan_sha256':sha(PLAN.read_bytes()),'source_audit_sha256':sha(AUDIT.read_bytes())}
    if any(m.get(k)!=v for k,v in expected.items()) or set(m['files'])!={'inputs.json','references.json','coverage.json'}:raise ValueError('Missing-window pack identity changed.')
    for n,digest in m['files'].items():
        if sha((DATA/n).read_bytes())!=digest:raise ValueError('Missing-window pack bytes changed.')
    rows,coverage=reconstruct(p)
    if rows!=load(DATA/'inputs.json') or coverage!=load(DATA/'coverage.json') or original.references(rows)!=load(DATA/'references.json') or len(rows)!=360:raise ValueError('Missing-window reconstruction changed.')
    if sum(r['missing_window'] for r in coverage)!=1:raise ValueError('Missing recording was excluded or replaced.')
    return m
