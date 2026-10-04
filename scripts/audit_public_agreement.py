"""Inspect a fixed RE1 schema sample before choosing transfer inputs; no inference."""
import argparse,hashlib,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.public_data import REVISION,REPOSITORY,sha,fetch
from triage_bench.public_rca_stages import load,committed
from triage_bench.public_rca_data import dump

PLAN=ROOT/'checkpoints/public-agreement-audit-plan-2026-10-04.json'
RESULT=ROOT/'checkpoints/public-agreement-audit-results-2026-10-04.json'
INDEX=ROOT/'runs/public-data/preflight-2026-10-03-v1/cases.parquet'
FOLDER=ROOT/'runs/public-agreement/audit-data-2026-10-04-v1'
SOURCES=('scripts/audit_public_agreement.py','triage_bench/public_data.py','triage_bench/public_rca_stages.py','triage_bench/public_rca_data.py','uv.lock')

def plan():
    import pyarrow.parquet as pq
    if PLAN.exists():raise ValueError('Audit plan exists.')
    rows=pq.read_table(INDEX).to_pylist()
    cases=[r['case'] for r in rows if r['dataset'] in {'RE1-TT','RE1-SS'} and r['fault']=='cpu' and r['root_cause_service'] in {'ts-auth-service','carts'}]
    if len(cases)!=10:raise ValueError('Unexpected schema sample.')
    p={'schema':'public-agreement-audit-plan-1','revision':REVISION,'index_sha256':sha(INDEX.read_bytes()),'cases':sorted(cases),'maximum_calls':0,
       'purpose':'Check RE1 metric names, timestamp schema and evidence compatibility before a separately frozen disagreement experiment. These ten cases and both full service/fault groups become inspected development; exclude them from evaluation and reserves.',
       'user_decision':'Test Jev/ML disagreement as an analyst-review trigger. Do not substitute the ML answer or retune the 0.70 boundary.',
       'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES}}
    dump(PLAN,p);return {'schema_cases':10,'maximum_calls':0}

def check():
    p=load(PLAN);committed(PLAN)
    if p['revision']!=REVISION or p['maximum_calls']!=0 or sha(INDEX.read_bytes())!=p['index_sha256']:raise ValueError('Audit plan drift.')
    for n,h in p['source_sha256'].items():
        if sha((ROOT/n).read_bytes())!=h:raise ValueError('Audit source drift.')
    return p

def audit():
    import pyarrow.parquet as pq
    p=check()
    if FOLDER.exists() or RESULT.exists():raise ValueError('Audit already started; no overwrite.')
    FOLDER.mkdir(parents=True);files=[];profiles=[]
    rows={r['case']:r for r in pq.read_table(INDEX).to_pylist()}
    for case in p['cases']:
        identifier='AGR-'+sha(case.encode())[:12];directory=FOLDER/'raw'/identifier;directory.mkdir(parents=True)
        tree=json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{case}'))
        entries={r['path']:r for r in tree if r['type']=='file'}
        for name in ('metrics.parquet','inject_time.txt'):
            e=entries[case+'/'+name]
            if not 0<e['size']<=5_000_000:raise ValueError('File cap exceeded.')
            data=fetch(f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{case}/{name}',e['size'])
            expected=e['lfs']['oid'] if 'lfs' in e else e['oid'];actual=sha(data) if 'lfs' in e else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            if len(data)!=e['size'] or expected!=actual:raise ValueError('Publisher hash mismatch.')
            (directory/name).write_bytes(data);files.append({'path':str((directory/name).relative_to(FOLDER)),'bytes':len(data),'sha256':sha(data),'publisher_hash':expected})
        t=pq.read_table(directory/'metrics.parquet');boundary=int((directory/'inject_time.txt').read_text());times=t.column('time').to_pylist()
        if boundary!=rows[case]['inject_time']:raise ValueError('Boundary drift.')
        profiles.append({'id':identifier,'source_case':case,'dataset':rows[case]['dataset'],'columns':t.schema.names,'rows':t.num_rows,'metric_suffixes':sorted({n.rsplit('_',1)[1] for n in t.schema.names if n!='time'}),'time_type':str(t.schema.field('time').type),'unique_sorted_times':times==sorted(set(times)),'before':sum(x<boundary for x in times),'after':sum(x>=boundary for x in times)})
        print(f'Checked schema {len(profiles)}/10',flush=True)
    m={'schema':'public-agreement-audit-1','plan_sha256':sha(PLAN.read_bytes()),'profiles':profiles,'files':files,'new_hosted_calls':0}
    dump(FOLDER/'manifest.json',m);dump(RESULT,m);return {'cases':len(profiles),'metric_suffixes':sorted({s for r in profiles for s in r['metric_suffixes']}),'new_hosted_calls':0}

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('action',choices=('plan','audit'));args=a.parse_args();print(json.dumps(plan() if args.action=='plan' else audit()))
