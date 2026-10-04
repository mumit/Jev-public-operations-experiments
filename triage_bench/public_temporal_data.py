"""Fresh grouped Train Ticket development; later telemetry remains undownloaded."""
import copy
import hashlib
import json
from pathlib import Path
from .paths import ROOT
from .public_data import REVISION,REPOSITORY,sha,fetch
from .public_rca_data import FAULTS,state_from_metrics,dump
from .public_format_trial import body
from .public_repeat_trial import check
from .public_rca_stages import load,committed
from .public_temporal_audit import latency_windows
from .hosted import encoded

COUNTS={'development':18,'calibration':18,'evaluation':36,'reserve':18}
MAX_FILE_BYTES=5_000_000


def partition(index):
    rows=sorted([r for r in index if r['dataset']=='RE2-TT'],key=lambda r:r['case'])
    services=sorted({r['root_cause_service'] for r in rows})
    if len(rows)!=90 or len(services)!=5:raise ValueError('Unexpected Train Ticket index.')
    plan=[];groups={}
    for row in rows:
        service,fault=row['root_cause_service'],row['fault'];offset=(services.index(service)-FAULTS.index(fault))%5
        split='development' if offset==0 else 'calibration' if offset==1 else 'evaluation' if offset in (2,3) else 'reserve'
        group=service+'/'+fault
        plan.append({'id':'TMP-'+sha(row['case'].encode())[:12],'split':split,'group':group,'source_case':row['case']})
        groups.setdefault(group,[]).append(row['repetition'])
    if len(groups)!=30 or any(sorted(rs)!=[1,2,3] for rs in groups.values()) or len({r['id'] for r in plan})!=90:raise ValueError('Unexpected repetitions or identifiers.')
    for split,count in COUNTS.items():
        chosen=[r for r in plan if r['split']==split]
        if len(chosen)!=count or {r['group'].split('/')[1] for r in chosen}!=set(FAULTS):raise ValueError('Missing count or fault coverage.')
    return plan


def freeze_preparation(index_file,output):
    import pyarrow.parquet as pq
    output=Path(output)
    if output.exists():raise ValueError('Preparation plan already exists.')
    historical=load(ROOT/'checkpoints/public-repeat-protocol-2026-10-03.json');check(historical)
    index_file=Path(index_file)
    if sha(index_file.read_bytes())!=load(ROOT/'runs/public-data/input-format-2026-10-03-v1/manifest.json')['index_sha256']:raise ValueError('Different pinned index.')
    result={'schema':'public-temporal-preparation-1','revision':REVISION,'index_sha256':sha(index_file.read_bytes()),'counts':COUNTS,
        'assignments':partition(pq.read_table(index_file).to_pylist()),'download_split':'development','maximum_cases':18,
        'files_per_case':['metrics.parquet','inject_time.txt'],'maximum_file_bytes':MAX_FILE_BYTES,
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('triage_bench/public_temporal_data.py','triage_bench/public_temporal_audit.py','scripts/prepare_public_temporal.py')},
        'conditions':'Known injection boundary; 18 new grouped development cases only. No hosted calls. Keep all other Train Ticket telemetry and all Sock Shop reserve telemetry undownloaded.',
        'sizing':'Measure complete named and temporal request sizes before inference; do not drop candidates or measurements to fit.'}
    dump(output,result);return result


def temporal_body(state,columns,boundary):
    request=body(state,'named');presentation=json.loads(request['state']);windows=latency_windows(columns,boundary)
    presentation['latency_time_windows']={'offset_seconds':[[0,60],[60,300],[300,721]],
        'endpoints':'Each interval includes its start and excludes its end; offsets use the supplied incident boundary. Units apply to time offsets only; metric values retain source scale.',
        'fields':['median','signed_change','missing_fraction','rows'],
        'signed_change_definition':state['signed_change_definition'],
        'caution':'Timing can preserve transient or sustained symptoms; collection and aggregation delays are unknown. Timing and magnitude alone do not prove origin.',
        'series':{name:[[None if w[k] is None else float(format(w[k],'.8g')) if k!='rows' else w[k] for k in ('median','signed_change','missing_fraction','rows')] for w in row['windows']] for name,row in windows.items()}}
    request['state']=json.dumps(presentation,sort_keys=True,separators=(',',':'),allow_nan=False)
    return request


def prepare(plan_path,index_file,folder,context_tokens=32768):
    import pyarrow.parquet as pq
    plan_path=Path(plan_path);committed(plan_path);p=load(plan_path);index_file=Path(index_file);folder=Path(folder)
    if folder.exists():raise ValueError('Preparation folder already exists.')
    if p['revision']!=REVISION or sha(index_file.read_bytes())!=p['index_sha256']:raise ValueError('Changed source index.')
    for n,digest in p['source_sha256'].items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Preparation source drift.')
    rows=pq.read_table(index_file).to_pylist();indexed={r['case']:r for r in rows}
    if partition(rows)!=p['assignments']:raise ValueError('Preparation assignments changed.')
    selected=[a for a in p['assignments'] if a['split']=='development']
    if len(selected)!=18 or p['download_split']!='development' or p['maximum_cases']!=18:raise ValueError('Unexpected preparation budget.')
    folder.mkdir(parents=True);dump(folder/'assignments.json',p['assignments']);packets=[];references=[];downloads=[];sizes=[]
    base=f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}'
    for number,a in enumerate(selected,1):
        source_case=a['source_case'];row=indexed[source_case]
        tree=json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source_case}'))
        sources={r['path']:r for r in tree if r['type']=='file'};directory=folder/'raw'/a['id'];directory.mkdir(parents=True)
        for name in ('metrics.parquet','inject_time.txt'):
            entry=sources[source_case+'/'+name]
            if not 0<entry['size']<=MAX_FILE_BYTES:raise ValueError('Source exceeds preparation cap.')
            data=fetch(base+'/'+source_case+'/'+name,entry['size'])
            expected=entry['lfs']['oid'] if 'lfs' in entry else entry['oid']
            actual=sha(data) if 'lfs' in entry else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            if len(data)!=entry['size'] or actual!=expected:raise ValueError('Publisher hash or size mismatch.')
            (directory/name).write_bytes(data);downloads.append({'id':a['id'],'name':name,'bytes':len(data),'sha256':sha(data),'publisher_hash':expected})
        boundary=int((directory/'inject_time.txt').read_text())
        if boundary!=row['inject_time']:raise ValueError('Boundary mismatch.')
        columns=pq.read_table(directory/'metrics.parquet').to_pydict();state=state_from_metrics(columns,boundary)
        if state['window_rows']!={'before':row['normal_timesteps'],'after':row['faulty_timesteps']}:raise ValueError('Source timeline differs from index.')
        # Reference joins never repair or select candidates.
        if row['root_cause_service'] not in state['services']:raise ValueError('Published cause absent from observed candidates.')
        requests={'named':body(state,'named'),'temporal':temporal_body(state,columns,boundary)}
        sizes.append({'id':a['id'],'candidates':len(state['services']),'metric_series':sum(len(ms) for ms in state['services'].values()),
            'request_bytes':{arm:len(encoded(request)) for arm,request in requests.items()},
            'fits_conservative_context_bound':{arm:len(encoded(request))+512<=context_tokens for arm,request in requests.items()}})
        packets.append({'id':a['id'],'state':state,'requests':requests})
        references.append({'id':a['id'],'group':a['group'],'target':row['root_cause_service'],'fault':row['fault']})
        print(f'Prepared fresh development {number}/18',flush=True)
    dump(folder/'development.inputs.json',packets);dump(folder/'development.references.json',references);dump(folder/'request-sizing.json',sizes)
    names=('assignments.json','development.inputs.json','development.references.json','request-sizing.json')
    result={'schema':'public-temporal-development-1','revision':REVISION,'dataset':'RE2-TT','downloaded_cases':18,'hosted_calls':0,
        'plan_sha256':sha(plan_path.read_bytes()),'files':{n:sha((folder/n).read_bytes()) for n in names},'downloads':downloads,
        'declared_context_tokens':context_tokens,'sizing_rule':'Request bytes plus 512 must fit declared context_tokens. This conservative bound is not an exact tokenizer count.',
        'fits_context':all(all(r['fits_conservative_context_bound'].values()) for r in sizes),'candidate_retrieval_failures':0,
        'sealed_cases':72,'condition':'All named measurements and observed candidates retained; no reference or source path forwarded.'}
    dump(folder/'manifest.json',result);return result


def validate(plan_path,folder):
    import pyarrow.parquet as pq
    plan=load(plan_path);folder=Path(folder);m=load(folder/'manifest.json')
    if m['plan_sha256']!=sha(Path(plan_path).read_bytes()) or m['revision']!=REVISION or m['downloaded_cases']!=18 or m['sealed_cases']!=72 or m['hosted_calls']!=0:raise ValueError('Changed preparation manifest.')
    for name,digest in m['files'].items():
        if name not in {'assignments.json','development.inputs.json','development.references.json','request-sizing.json'} or sha((folder/name).read_bytes())!=digest:raise ValueError('Changed preparation file.')
    for d in m['downloads']:
        if d['name'] not in {'metrics.parquet','inject_time.txt'}:raise ValueError('Unknown source file.')
        path=folder/'raw'/d['id']/d['name']
        if sha(path.read_bytes())!=d['sha256'] or path.stat().st_size!=d['bytes']:raise ValueError('Changed source measurement.')
    assignments=load(folder/'assignments.json')
    if assignments!=plan['assignments']:raise ValueError('Changed assignments.')
    expected={a['id'] for a in assignments if a['split']=='development'}
    packets=load(folder/'development.inputs.json');refs=load(folder/'development.references.json');sizes=load(folder/'request-sizing.json')
    if len(packets)!=18 or {p['id'] for p in packets}!={r['id'] for r in refs} or {p['id'] for p in packets}!=expected:raise ValueError('Changed preparation identities.')
    if {p.name for p in (folder/'raw').iterdir()}!=expected:raise ValueError('Sealed telemetry entered development.')
    computed_sizes=[]
    for packet,ref in zip(packets,refs):
        if packet['id']!=ref['id'] or ref['target'] not in packet['state']['services']:raise ValueError('Reference join failed.')
        directory=folder/'raw'/packet['id'];columns=pq.read_table(directory/'metrics.parquet').to_pydict();boundary=int((directory/'inject_time.txt').read_text())
        state=state_from_metrics(columns,boundary)
        if state!=packet['state'] or packet['requests']!={'named':body(state,'named'),'temporal':temporal_body(state,columns,boundary)}:raise ValueError('Request reconstruction failed.')
        for request in packet['requests'].values():
            if any(term in json.dumps(request) for term in ('re2tt_','root_cause_service','source_case',packet['id'])):raise ValueError('Answer metadata entered request.')
        byte_counts={arm:len(encoded(request)) for arm,request in packet['requests'].items()}
        computed_sizes.append({'id':packet['id'],'candidates':len(state['services']),'metric_series':sum(len(ms) for ms in state['services'].values()),'request_bytes':byte_counts,
            'fits_conservative_context_bound':{arm:n+512<=m['declared_context_tokens'] for arm,n in byte_counts.items()}})
    if computed_sizes!=sizes or m['fits_context']!=all(all(r['fits_conservative_context_bound'].values()) for r in sizes):raise ValueError('Changed sizing result.')
    return m
