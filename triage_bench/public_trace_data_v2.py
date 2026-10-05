"""Grouped RE3 paired metric/trace packs, with evaluation locked behind development."""
import hashlib,json,shutil
from pathlib import Path
from .paths import ROOT
from .public_data import REVISION,REPOSITORY,sha,fetch
from .public_rca_data import state_from_metrics,dump
from .public_format_trial import body
from .public_rca_stages import load,committed
from .public_trace_features import summarize,augment
from .public_trace_wire import compact
from .hosted import encoded

PLAN=ROOT/'checkpoints/public-traces-v2-plan-2026-10-04.json'
BASE=ROOT/'runs/public-traces'
INDEX=ROOT/'runs/public-data/preflight-2026-10-03-v1/cases.parquet'
COUNTS={'development':13,'evaluation':22}
ARMS=('metrics','traces')
GROUPS={'RE3-TT':{'development':{'ts-auth-service/f1','ts-route-service/f2'},'evaluation':{'ts-auth-service/f2','ts-route-service/f1','ts-route-service/f4'}},'RE3-OB':{'development':{'adservice/f3','emailservice/f2'},'evaluation':{'adservice/f4','cartservice/f1','currencyservice/f1','emailservice/f3'}}}

def partition(index):
    assignments=[]
    for suite,name,counts in [('RE3-TT','Train Ticket',(7,10,13)),('RE3-OB','Online Boutique',(6,12,12))]:
        rows=sorted((r for r in index if r['dataset']==suite),key=lambda r:r['case']);groups={}
        if len(rows)!=30 or not all(r['has_traces'] for r in rows):raise ValueError('Unexpected RE3 panel.')
        for r in rows:
            group=r['root_cause_service']+'/'+r['fault'];split='development' if group in GROUPS[suite]['development'] else 'evaluation' if group in GROUPS[suite]['evaluation'] else 'reserve'
            assignments.append({'id':'TRC-'+sha(r['case'].encode())[:12],'suite':suite,'dataset':name,'group':suite+'/'+group,'split':split,'source_case':r['case']});groups.setdefault(group,set()).add(split)
        if any(len(s)!=1 for s in groups.values()):raise ValueError('Group leakage.')
        if tuple(sum(a['dataset']==name and a['split']==s for a in assignments) for s in ('development','evaluation','reserve'))!=counts:raise ValueError('RE3 allocation drift.')
    if len({a['id'] for a in assignments})!=60:raise ValueError('Duplicate case identity.')
    return assignments

def folder(split):
    if split not in COUNTS:raise ValueError('Unknown trace split.')
    return BASE/(split+'-data-2026-10-04-v2')

def check_plan():
    p=load(PLAN);committed(PLAN)
    if p['schema']!='public-traces-plan-1' or p['counts']!=COUNTS or p['maximum_calls']!=210 or p['revision']!=REVISION or sha(INDEX.read_bytes())!=p['index_sha256']:raise ValueError('Trace plan drift.')
    for mapping in ('source_sha256','evidence_sha256'):
        for name,digest in p[mapping].items():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or sha((ROOT/path).read_bytes())!=digest:raise ValueError('Trace source or evidence drift.')
    return p

def verify_audit():
    import pyarrow.parquet as pq
    from scripts.audit_public_traces import check,PLAN as AP,RESULT as AR,FOLDER as AF,profile
    p=check();committed(AR);r=load(AR)
    if r!=load(AF/'manifest.json') or r['plan_sha256']!=sha(AP.read_bytes()) or r['new_hosted_calls']!=0:raise ValueError('Trace audit drift.')
    expected={(('TRC-'+sha(case.encode())[:12]),n) for case in p['cases'] for n in p['files']}
    if len(r['files'])!=21 or {(f['path'].split('/')[1],f['path'].split('/')[2]) for f in r['files']}!=expected:raise ValueError('Audit file identities changed.')
    for f in r['files']:
        raw=(AF/f['path']).read_bytes();actual=sha(raw) if len(f['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if len(raw)!=f['bytes'] or sha(raw)!=f['sha256'] or actual!=f['publisher_hash']:raise ValueError('Trace audit publisher evidence drift.')
    rows={r['case']:r for r in pq.read_table(INDEX).to_pylist()}
    if r['profiles']!=[profile(c,AF/'raw'/('TRC-'+sha(c.encode())[:12]),rows[c]) for c in p['cases']]:raise ValueError('Trace audit reconstruction failed.')
    return r

def reconstruct(directory,row):
    import pyarrow.parquet as pq
    boundary=int((directory/'inject_time.txt').read_text())
    if boundary!=row['inject_time']:raise ValueError('Source boundary drift.')
    state=state_from_metrics(pq.read_table(directory/'metrics.parquet').to_pydict(),boundary)
    if state['window_rows']!={'before':row['normal_timesteps'],'after':row['faulty_timesteps']}:raise ValueError('Metric windows drift.')
    if row['root_cause_service'] not in state['services']:raise ValueError('Published cause outside observed candidates; do not repair it from labels.')
    raw=(directory/'traces.parquet').read_bytes()
    if pq.read_metadata(directory/'traces.parquet').num_rows!=row['n_traces']:raise ValueError('Trace row count drift.')
    context=summarize(raw,boundary,row['time_start'],row['time_end'],state['services'])
    return state,context,{arm:body(state if arm=='metrics' else augment(state,compact(context)),'named') for arm in ARMS}

def prepare(split):
    import pyarrow.parquet as pq
    p=check_plan()
    if split=='evaluation':
        from .public_trace_trial_v2 import check_candidate
        check_candidate()
    destination=folder(split)
    if destination.exists():raise ValueError('Trace pack already started; no overwrite.')
    index=pq.read_table(INDEX).to_pylist()
    if p['assignments']!=partition(index):raise ValueError('Trace allocation drift.')
    rows={r['case']:r for r in index};selected=[a for a in p['assignments'] if a['split']==split]
    audit=load(ROOT/'checkpoints/public-traces-audit-results-2026-10-04.json');old={(f['path'].split('/')[1],f['path'].split('/')[2]):{**f,'copy_path':'runs/public-traces/audit-data-2026-10-04-v1/'+f['path']} for f in audit['files']}
    prior=load(ROOT/'checkpoints/public-traces-sizing-2026-10-04.json')['manifest']
    for f in prior['downloads']:old[(f['id'],f['name'])]={**f,'copy_path':"runs/public-traces/development-data-2026-10-04-v1/raw/"+f['id']+'/'+f['name']}
    destination.mkdir(parents=True);packets=[];refs=[];sizes=[];files=[]
    for a in selected:
        directory=destination/'raw'/a['id'];directory.mkdir(parents=True);row=rows[a['source_case']]
        entries=None
        for name in ('inject_time.txt','metrics.parquet','traces.parquet'):
            if (a['id'],name) in old:
                f=old[(a['id'],name)];source=ROOT/f['copy_path'];raw=source.read_bytes();expected=f['publisher_hash']
                if sha(raw)!=f['sha256'] or len(raw)!=f['bytes']:raise ValueError('Audited source drift.')
            else:
                if entries is None:entries={r['path']:r for r in json.loads(fetch(f"https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{a['source_case']}")) if r['type']=='file'}
                e=entries[a['source_case']+'/'+name]
                if not 0<e['size']<=50_000_000:raise ValueError('Trace source cap exceeded.')
                raw=fetch(f"https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{a['source_case']}/{name}",e['size']);expected=e['lfs']['oid'] if 'lfs' in e else e['oid']
                actual=sha(raw) if 'lfs' in e else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
                if len(raw)!=e['size'] or expected!=actual:raise ValueError('Trace publisher checksum mismatch.')
            (directory/name).write_bytes(raw);files.append({'id':a['id'],'name':name,'bytes':len(raw),'sha256':sha(raw),'publisher_hash':expected})
        state,context,requests=reconstruct(directory,row);packets.append({'id':a['id'],'state':state,'trace_context':context,'requests':requests});refs.append({'id':a['id'],'group':a['group'],'target':row['root_cause_service'],'fault':row['fault']})
        sizes.append({'id':a['id'],'candidates':len(state['services']),'trace_services':len(context['services']),'edges':len(context['dependencies']),'request_bytes':{arm:len(encoded(requests[arm])) for arm in ARMS}})
        print(f'Prepared traces {split} {len(packets)}/{len(selected)}',flush=True)
    for n,v in [('inputs.json',packets),('references.json',refs),('sizing.json',sizes)]:dump(destination/n,v)
    m={'schema':'public-traces-pack-1','split':split,'cases':len(packets),'revision':REVISION,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((destination/n).read_bytes()) for n in ('inputs.json','references.json','sizing.json')},'downloads':files,
       'largest_request_bytes':max(v for s in sizes for v in s['request_bytes'].values()),'fits_empirical_wire_cap':all(v<=p['maximum_request_bytes'] for s in sizes for v in s['request_bytes'].values())}
    dump(destination/'manifest.json',m);validate(split);return m

def validate(split):
    import pyarrow.parquet as pq
    p=check_plan();directory=folder(split);m=load(directory/'manifest.json')
    if (m['schema'],m['split'],m['cases'],m['revision'],m['plan_sha256'])!=('public-traces-pack-1',split,COUNTS[split],REVISION,sha(PLAN.read_bytes())):raise ValueError('Trace pack identity drift.')
    if set(m['files'])!={'inputs.json','references.json','sizing.json'}:raise ValueError('Unexpected trace pack files.')
    for n,h in m['files'].items():
        if sha((directory/n).read_bytes())!=h:raise ValueError('Trace pack bytes changed.')
    index=pq.read_table(INDEX).to_pylist()
    if p['assignments']!=partition(index):raise ValueError('Case allocation changed.')
    expected={a['id']:a for a in p['assignments'] if a['split']==split};packets=load(directory/'inputs.json');refs=load(directory/'references.json');sizes=load(directory/'sizing.json')
    if [r['id'] for r in packets]!=list(expected) or [r['id'] for r in refs]!=list(expected) or {d.name for d in (directory/'raw').iterdir()}!=set(expected):raise ValueError('Trace case identities changed.')
    if len(m['downloads'])!=COUNTS[split]*3 or {(d['id'],d['name']) for d in m['downloads']}!={(i,n) for i in expected for n in ('inject_time.txt','metrics.parquet','traces.parquet')}:raise ValueError('Download identity drift.')
    for d in m['downloads']:
        raw=(directory/'raw'/d['id']/d['name']).read_bytes();actual=sha(raw) if len(d['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if sha(raw)!=d['sha256'] or len(raw)!=d['bytes'] or actual!=d['publisher_hash']:raise ValueError('Source publisher bytes changed.')
    computed=[];indexed={r['case']:r for r in index}
    for packet,ref in zip(packets,refs):
        a=expected[packet['id']];row=indexed[a['source_case']];state,context,requests=reconstruct(directory/'raw'/a['id'],row)
        if packet!={'id':a['id'],'state':state,'trace_context':context,'requests':requests} or ref!={'id':a['id'],'group':a['group'],'target':row['root_cause_service'],'fault':row['fault']}:raise ValueError('Trace request/reference reconstruction failed.')
        augmented=json.loads(requests['traces']['state']);augmented.pop('trace_context')
        if augmented!=json.loads(requests['metrics']['state']) or requests['metrics']['questions']!=requests['traces']['questions']:raise ValueError('Trace addition changed metric evidence/questions.')
        if any(term in json.dumps(requests) for term in ('re3tt_','re3ob_','source_case','root_cause_service','methodName','operationName','parentSpanID','traceID','spanID',a['id'])):raise ValueError('Answer metadata or source identity entered requests.')
        computed.append({'id':a['id'],'candidates':len(state['services']),'trace_services':len(context['services']),'edges':len(context['dependencies']),'request_bytes':{arm:len(encoded(requests[arm])) for arm in ARMS}})
    if sizes!=computed or m['largest_request_bytes']!=max(v for s in sizes for v in s['request_bytes'].values()) or m['fits_empirical_wire_cap']!=all(v<=p['maximum_request_bytes'] for s in sizes for v in s['request_bytes'].values()):raise ValueError('Trace sizing drift.')
    return m
