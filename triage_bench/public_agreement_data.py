"""Fresh RE1 transfer packs. Audit groups and sealed reserves never enter evaluation."""
import hashlib,json
from pathlib import Path
from .paths import ROOT
from .public_data import REVISION,REPOSITORY,sha,fetch
from .public_rca_data import state_from_metrics,dump
from .public_format_trial import body
from .public_rca_stages import load,committed
from .hosted import encoded

PLAN=ROOT/'checkpoints/public-agreement-plan-2026-10-04.json'
BASE=ROOT/'runs/public-agreement'
INDEX=ROOT/'runs/public-data/preflight-2026-10-03-v1/cases.parquet'
COUNTS={'evaluation':100}
FAULTS=('cpu','delay','disk','loss','mem')

def partition(index,audit_cases):
    result=[]
    for dataset,name in [('RE1-TT','Train Ticket'),('RE1-SS','Sock Shop')]:
        rows=sorted((r for r in index if r['dataset']==dataset),key=lambda r:r['case']);services=sorted({r['root_cause_service'] for r in rows})
        if len(rows)!=125 or len(services)!=5:raise ValueError('Unexpected RE1 panel.')
        groups={}
        for row in rows:
            service,fault=row['root_cause_service'],row['fault'];offset=(services.index(service)-FAULTS.index(fault))%5
            split='development' if row['case'] in audit_cases else 'evaluation' if offset in (1,2) else 'reserve'
            result.append({'id':'AGR-'+sha(row['case'].encode())[:12],'dataset':name,'suite':dataset,'source_case':row['case'],'group':dataset+'/'+service+'/'+fault,'split':split})
            groups.setdefault(service+'/'+fault,[]).append((split,row['repetition']))
        if len(groups)!=25 or any(len({s for s,n in v})!=1 or sorted(n for s,n in v)!=[1,2,3,4,5] for v in groups.values()):raise ValueError('Group separation failed.')
        for split,count in [('development',5),('evaluation',50),('reserve',70)]:
            chosen=[r for r in result if r['dataset']==name and r['split']==split]
            if len(chosen)!=count:raise ValueError('Unexpected split count.')
            if split=='evaluation' and any(sum(r['group'].endswith('/'+f) for r in chosen)!=10 for f in FAULTS):raise ValueError('Fault balance failed.')
    if len({r['id'] for r in result})!=250:raise ValueError('Case ID collision.')
    return result

def folder(split='evaluation'):
    if split not in COUNTS:raise ValueError('Unknown agreement split.')
    return BASE/(split+'-data-2026-10-04-v1')

def check_plan():
    p=load(PLAN);committed(PLAN)
    if p['schema']!='public-agreement-plan-1' or p['counts']!=COUNTS or p['maximum_calls']!=300 or p['revision']!=REVISION or sha(INDEX.read_bytes())!=p['index_sha256']:raise ValueError('Agreement plan drift.')
    for mapping in ('source_sha256','evidence_sha256'):
        for name,digest in p[mapping].items():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or sha((ROOT/path).read_bytes())!=digest:raise ValueError('Agreement source/evidence drift.')
    return p

def reconstruct(directory,row):
    import pyarrow.parquet as pq
    boundary=int((directory/'inject_time.txt').read_text())
    if boundary!=row['inject_time']:raise ValueError('Source boundary drift.')
    state=state_from_metrics(pq.read_table(directory/'metrics.parquet').to_pydict(),boundary)
    if state['window_rows']!={'before':row['normal_timesteps'],'after':row['faulty_timesteps']}:raise ValueError('Timeline drift.')
    if row['root_cause_service'] not in state['services']:raise ValueError('Published cause absent. Do not repair candidates from labels.')
    return state,body(state,'named')

def prepare(split='evaluation'):
    import pyarrow.parquet as pq
    p=check_plan();destination=folder(split)
    if destination.exists():raise ValueError('Agreement pack already started; no overwrite.')
    rows={r['case']:r for r in pq.read_table(INDEX).to_pylist()};selected=[a for a in p['assignments'] if a['split']==split]
    destination.mkdir(parents=True);packets=[];refs=[];downloads=[];sizes=[];seen=set(p['historical_metric_sha256'])
    base=f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}'
    for number,a in enumerate(selected,1):
        row=rows[a['source_case']];tree=json.loads(fetch(f"https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{a['source_case']}"))
        sources={r['path']:r for r in tree if r['type']=='file'};directory=destination/'raw'/a['id'];directory.mkdir(parents=True)
        for name in ('metrics.parquet','inject_time.txt'):
            entry=sources[a['source_case']+'/'+name]
            if not 0<entry['size']<=5_000_000:raise ValueError('Publisher file exceeds cap.')
            data=fetch(base+'/'+a['source_case']+'/'+name,entry['size']);expected=entry['lfs']['oid'] if 'lfs' in entry else entry['oid']
            actual=sha(data) if 'lfs' in entry else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            if len(data)!=entry['size'] or actual!=expected:raise ValueError('Publisher hash mismatch.')
            if name=='metrics.parquet':
                if sha(data) in seen:raise ValueError('Previously opened or duplicate metric file.')
                seen.add(sha(data))
            (directory/name).write_bytes(data);downloads.append({'id':a['id'],'name':name,'bytes':len(data),'sha256':sha(data),'publisher_hash':expected})
        state,request=reconstruct(directory,row);packets.append({'id':a['id'],'state':state,'request':request})
        refs.append({'id':a['id'],'group':a['group'],'fault':row['fault'],'target':row['root_cause_service']})
        sizes.append({'id':a['id'],'request_bytes':len(encoded(request)),'candidates':len(state['services']),'metric_names':sorted({m for metrics in state['services'].values() for m in metrics})})
        print(f'Prepared agreement {number}/100',flush=True)
    for name,value in [('inputs.json',packets),('references.json',refs),('sizing.json',sizes)]:dump(destination/name,value)
    m={'schema':'public-agreement-pack-1','split':split,'cases':100,'revision':REVISION,'plan_sha256':sha(PLAN.read_bytes()),
       'files':{name:sha((destination/name).read_bytes()) for name in ('inputs.json','references.json','sizing.json')},'downloads':downloads,
       'largest_request_bytes':max(r['request_bytes'] for r in sizes),'fits_empirical_wire_cap':all(r['request_bytes']<=p['maximum_request_bytes'] for r in sizes),'reserved_cases':140}
    dump(destination/'manifest.json',m);validate(split);return m

def validate(split='evaluation'):
    import pyarrow.parquet as pq
    p=check_plan();directory=folder(split);m=load(directory/'manifest.json')
    if (m['schema'],m['split'],m['cases'],m['revision'],m['plan_sha256'],m['reserved_cases'])!=('public-agreement-pack-1',split,100,REVISION,sha(PLAN.read_bytes()),140):raise ValueError('Pack identity drift.')
    if set(m['files'])!={'inputs.json','references.json','sizing.json'}:raise ValueError('Unknown pack files.')
    for name,digest in m['files'].items():
        if sha((directory/name).read_bytes())!=digest:raise ValueError('Pack fingerprint drift.')
    audit=load(ROOT/'checkpoints/public-agreement-audit-plan-2026-10-04.json')
    index=pq.read_table(INDEX).to_pylist()
    if p['assignments']!=partition(index,audit['cases']):raise ValueError('Group assignment drift.')
    expected={a['id']:a for a in p['assignments'] if a['split']==split}
    packets=load(directory/'inputs.json');refs=load(directory/'references.json');sizes=load(directory/'sizing.json')
    if len(packets)!=100 or len(refs)!=100 or [r['id'] for r in packets]!=list(expected) or [r['id'] for r in refs]!=list(expected):raise ValueError('Case identity drift.')
    if {d.name for d in (directory/'raw').iterdir()}!=set(expected):raise ValueError('Undeclared raw case.')
    if len(m['downloads'])!=200 or {(d['id'],d['name']) for d in m['downloads']}!={(i,n) for i in expected for n in ('metrics.parquet','inject_time.txt')}:raise ValueError('Download identity drift.')
    seen=set(p['historical_metric_sha256'])
    for d in m['downloads']:
        data=(directory/'raw'/d['id']/d['name']).read_bytes()
        if len(data)!=d['bytes'] or sha(data)!=d['sha256']:raise ValueError('Raw evidence drift.')
        actual=sha(data) if len(d['publisher_hash'])==64 else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        if actual!=d['publisher_hash']:raise ValueError('Publisher fingerprint drift.')
        if d['name']=='metrics.parquet':
            if sha(data) in seen:raise ValueError('Previously opened metric file.')
            seen.add(sha(data))
    computed=[];indexed={r['case']:r for r in index}
    for packet,ref in zip(packets,refs):
        a=expected[packet['id']];row=indexed[a['source_case']]
        if ref!={'id':a['id'],'group':a['group'],'fault':row['fault'],'target':row['root_cause_service']}:raise ValueError('Reference drift.')
        state,request=reconstruct(directory/'raw'/packet['id'],row)
        if state!=packet['state'] or request!=packet['request']:raise ValueError('Input reconstruction failed.')
        if any(term in json.dumps(request) for term in ('re1tt_','re1ss_','root_cause_service','source_case',packet['id'],'scoring_points')):raise ValueError('Answer metadata entered request.')
        computed.append({'id':a['id'],'request_bytes':len(encoded(request)),'candidates':len(state['services']),'metric_names':sorted({m for metrics in state['services'].values() for m in metrics})})
    if computed!=sizes or m['largest_request_bytes']!=max(r['request_bytes'] for r in sizes) or m['fits_empirical_wire_cap']!=all(r['request_bytes']<=p['maximum_request_bytes'] for r in sizes):raise ValueError('Sizing drift.')
    return m
