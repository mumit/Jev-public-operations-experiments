"""Audit a predeclared RE3 trace/metric sample. No inference or reserve access."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.public_data import REVISION,REPOSITORY,sha,fetch
from triage_bench.public_rca_data import dump
from triage_bench.public_rca_stages import load,committed

PLAN=ROOT/'checkpoints/public-traces-audit-plan-2026-10-04.json'
RESULT=ROOT/'checkpoints/public-traces-audit-results-2026-10-04.json'
INDEX=ROOT/'runs/public-data/preflight-2026-10-03-v1/cases.parquet'
FOLDER=ROOT/'runs/public-traces/audit-data-2026-10-04-v1'
SOURCES=('scripts/audit_public_traces.py','triage_bench/public_data.py','triage_bench/public_rca_data.py','triage_bench/public_rca_stages.py','uv.lock')

def plan():
    import pyarrow.parquet as pq
    if PLAN.exists():raise ValueError('Trace audit plan exists.')
    rows=pq.read_table(INDEX).to_pylist();cases=[r['case'] for r in rows if (r['dataset'],r['root_cause_service'],r['fault']) in {('RE3-TT','ts-auth-service','f1'),('RE3-OB','adservice','f3')}]
    if len(cases)!=7 or any(not r['has_traces'] for r in rows if r['case'] in cases):raise ValueError('Unexpected trace audit group.')
    p={'schema':'public-traces-audit-plan-1','revision':REVISION,'index_sha256':sha(INDEX.read_bytes()),'cases':sorted(cases),'maximum_calls':0,
       'decision':'User authorized richer causal evidence for Jev on 2026-10-04.',
       'purpose':'Audit source trace schema, units, parent links and candidate-name alignment before constructing a separately frozen paired experiment. These seven cases and their whole service/fault groups become development. Leave all other RE3 telemetry and all RE1 reserves unopened.',
       'maximum_file_bytes':50_000_000,'files':['inject_time.txt','metrics.parquet','traces.parquet'],
       'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES}}
    dump(PLAN,p);return {'schema_cases':7,'maximum_calls':0}

def check():
    p=load(PLAN);committed(PLAN)
    if p['revision']!=REVISION or p['maximum_calls']!=0 or sha(INDEX.read_bytes())!=p['index_sha256']:raise ValueError('Trace audit plan drift.')
    for n,h in p['source_sha256'].items():
        if sha((ROOT/n).read_bytes())!=h:raise ValueError('Trace audit source drift.')
    return p

def profile(case,directory,row):
    import pyarrow.parquet as pq
    t=pq.read_table(directory/'traces.parquet');m=pq.read_table(directory/'metrics.parquet');data=t.to_pylist();boundary=int((directory/'inject_time.txt').read_text())
    if boundary!=row['inject_time'] or t.num_rows!=row['n_traces'] or m.num_rows!=row['n_timesteps']:raise ValueError('Trace audit source-index drift.')
    keys=Counter((r.get('traceID'),r.get('spanID')) for r in data);lookup=set(keys);times=[r.get('startTime') for r in data];ms=[r.get('startTimeMillis') for r in data]
    names=Counter(str(r.get('serviceName')) for r in data);status=Counter(str(r.get('statusCode')) for r in data)
    return {'id':'TRC-'+sha(case.encode())[:12],'source_case':case,'dataset':row['dataset'],'trace_schema':{f.name:str(f.type) for f in t.schema},'trace_rows':t.num_rows,'metric_rows':m.num_rows,
       'metric_service_names':sorted({n.rsplit('_',1)[0] for n in m.schema.names if n!='time'}),'metric_names':sorted({n.rsplit('_',1)[1] for n in m.schema.names if n!='time'}),
       'trace_service_counts':dict(sorted(names.items())),'status_code_counts':dict(sorted(status.items())),'start_time_range':[min(times),max(times)],'start_millis_range':[min(ms),max(ms)],
       'microsecond_millis_consistent':all(isinstance(a,int) and isinstance(b,int) and a//1000==b for a,b in zip(times,ms)),
       'trace_before':sum(a<boundary*1_000_000 for a in times),'trace_after':sum(a>=boundary*1_000_000 for a in times),
       'duration_range':[min(r.get('duration') for r in data),max(r.get('duration') for r in data)],
       'duplicate_span_keys':sum(n-1 for n in keys.values()),'missing_trace_or_span_ids':sum(not r.get('traceID') or not r.get('spanID') for r in data),
       'root_rows':sum(not r.get('parentSpanID') for r in data),'linked_parent_rows':sum(bool(r.get('parentSpanID')) and (r.get('traceID'),r.get('parentSpanID')) in lookup for r in data),
       'unresolved_parent_rows':sum(bool(r.get('parentSpanID')) and (r.get('traceID'),r.get('parentSpanID')) not in lookup for r in data),
       'source_metric_window':[row['time_start'],boundary,row['time_end']]}

def audit():
    import pyarrow.parquet as pq
    p=check()
    if FOLDER.exists() or RESULT.exists():raise ValueError('Trace audit already started; no overwrite.')
    FOLDER.mkdir(parents=True);files=[];profiles=[];indexed={r['case']:r for r in pq.read_table(INDEX).to_pylist()}
    for case in p['cases']:
        identifier='TRC-'+sha(case.encode())[:12];directory=FOLDER/'raw'/identifier;directory.mkdir(parents=True)
        tree=json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{case}'));entries={r['path']:r for r in tree if r['type']=='file'}
        for name in p['files']:
            e=entries[case+'/'+name]
            if not 0<e['size']<=p['maximum_file_bytes']:raise ValueError('Trace audit file cap exceeded.')
            raw=fetch(f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{case}/{name}',e['size'])
            expected=e['lfs']['oid'] if 'lfs' in e else e['oid'];actual=sha(raw) if 'lfs' in e else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
            if len(raw)!=e['size'] or actual!=expected:raise ValueError('Publisher hash mismatch.')
            (directory/name).write_bytes(raw);files.append({'path':str((directory/name).relative_to(FOLDER)),'bytes':len(raw),'sha256':sha(raw),'publisher_hash':expected})
        profiles.append(profile(case,directory,indexed[case]));print(f'Trace audit {len(profiles)}/7',flush=True)
    r={'schema':'public-traces-audit-1','plan_sha256':sha(PLAN.read_bytes()),'profiles':profiles,'files':files,'new_hosted_calls':0}
    dump(FOLDER/'manifest.json',r);dump(RESULT,r);return {'cases':7,'bytes':sum(r['bytes'] for r in files),'new_hosted_calls':0}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','audit'));a=p.parse_args();print(json.dumps(plan() if a.action=='plan' else audit()))
