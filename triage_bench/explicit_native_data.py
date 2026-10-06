"""Preserve failed-schema recordings and prepare a disjoint native-name confirmation."""
import hashlib,json
from .paths import ROOT
from .public_data import sha,REVISION,REPOSITORY,fetch
from .public_rca_data import dump
from .public_rca_stages import load
from . import explicit_claim_data as original,explicit_confirmation_data as failed
from .explicit_native_features import observations

PLAN=ROOT/'checkpoints/explicit-native-plan-2026-10-06.json'
BASE=ROOT/'runs/explicit-native'
DATA=BASE/'confirmation-data-2026-10-06-v1'
AUDIT=ROOT/'checkpoints/explicit-confirmation-preparation-failure-2026-10-06.json'

def allocation():
    import pyarrow.parquet as pq
    index=[r for r in pq.read_table(original.INDEX).to_pylist() if r['dataset']=='RE1-OB']
    groups=sorted({r['root_cause_service']+'/'+r['fault'] for r in index},key=lambda g:sha(('explicit-claims-v1/'+g).encode()))[6:9]
    rows=[{'id':'ECN-'+sha(r['case'].encode())[:12],'source_case':r['case'],'group':'RE1-OB/'+r['root_cause_service']+'/'+r['fault'],'dataset':'Online Boutique'} for r in sorted(index,key=lambda r:r['case']) if r['root_cause_service']+'/'+r['fault'] in groups]
    if len(rows)!=15 or any(sum(a['group']==g for a in rows)!=5 for g in {a['group'] for a in rows}):raise ValueError('Native confirmation groups changed.')
    if {r['source_case'] for r in rows}&{r['source_case'] for r in original.allocation()+failed.allocation()}:raise ValueError('Native allocation overlaps earlier explicit groups.')
    return rows

def failure_audit():
    p=load(failed.PLAN);files=[]
    for a in p['assignments']:
        source=a['source_case'];tree={e['path']:e for e in json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source}')) if e['type']=='file'}
        for name in ('metrics.parquet','inject_time.txt'):
            path=failed.DATA/'raw'/a['id']/name;raw=path.read_bytes();e=tree[source+'/'+name];publisher=e['lfs']['oid'] if 'lfs' in e else e['oid'];actual=sha(raw) if 'lfs' in e else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
            if len(raw)!=e['size'] or actual!=publisher:raise ValueError('Failed preparation publisher bytes differ.')
            files.append({'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':sha(raw),'publisher_hash':publisher})
    audit={'schema':'explicit-preparation-failure-1','plan_sha256':sha(failed.PLAN.read_bytes()),'recordings_downloaded':15,'hosted_calls':0,'inputs_prepared':0,'references_prepared':0,'status':'failed_before_protocol_or_inference','reason':'Older metric adapter rejects native load and latency channel names. Preserve source names; do not alias load to workload or latency to a percentile.','publisher_verification':'Rechecked pinned publisher metadata after the preparation exception; not an original execution journal.','files':files}
    with AUDIT.open('x') as f:f.write(json.dumps(audit,indent=2)+'\n')
    return {'downloaded_recordings':15,'hosted_calls':0,'files':30}

def verify_failure():
    audit=load(AUDIT)
    if audit['schema']!='explicit-preparation-failure-1' or audit['plan_sha256']!=sha(failed.PLAN.read_bytes()) or audit['hosted_calls']!=0 or len(audit['files'])!=30:raise ValueError('Preparation-failure audit changed.')
    for a in audit['files']:
        raw=(ROOT/a['path']).read_bytes();actual=sha(raw) if len(a['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if len(raw)!=a['bytes'] or sha(raw)!=a['sha256'] or actual!=a['publisher_hash']:raise ValueError('Failed preparation bytes changed.')
    if any((failed.DATA/n).exists() for n in ('inputs.json','references.json','manifest.json')) or failed.BASE.joinpath('confirmation-hosted-2026-10-06-v1').exists() or (ROOT/'checkpoints/explicit-confirmation-protocol-2026-10-06.json').exists():raise ValueError('Failed preparation promoted or overwritten.')
    return audit

def reconstruct(plan):
    import pyarrow.parquet as pq
    index={r['case']:r for r in pq.read_table(original.INDEX).to_pylist()};rows=[]
    for a in plan['assignments']:
        directory=DATA/'raw'/a['id'];boundary=int((directory/'inject_time.txt').read_text());r=index[a['source_case']]
        if boundary!=r['inject_time'] or r['has_traces']:raise ValueError('Native index conditions changed.')
        services,windows,counts=observations(pq.read_table(directory/'metrics.parquet').to_pydict(),boundary)
        if counts!={'before':r['normal_timesteps'],'after':r['faulty_timesteps']}:raise ValueError('Native window rows changed.')
        names=sorted(services,key=lambda s:sha(('explicit-services/'+r['case']+'/'+s).encode()))[:2]
        if len(names)!=2:raise ValueError('Two observed services required.')
        for i,s in enumerate(names):
            o={'service':s,'metrics':services[s],'trace':None,'window_seconds':windows}
            rows.extend(original.entries(o,a['id']+'-'+str(i),a['dataset'],a['id'],'fresh_native_metrics'))
    return rows

def prepare(check_plan):
    p=check_plan()
    if DATA.exists():raise ValueError('Native confirmation started; never overwrite.')
    names={d.name for d in ROOT.glob('runs/**/raw/*')}
    for a in p['assignments']:
        if any(n.endswith(sha(a['source_case'].encode())[:12]) for n in names):raise ValueError('Native confirmation already opened.')
    seen=set(p['historical_metric_sha256']);downloads=[];DATA.mkdir(parents=True)
    for a in p['assignments']:
        source=a['source_case'];directory=DATA/'raw'/a['id'];directory.mkdir(parents=True)
        tree={e['path']:e for e in json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source}')) if e['type']=='file'}
        for name in ('metrics.parquet','inject_time.txt'):
            e=tree[source+'/'+name]
            if not 0<e['size']<=5_000_000:raise ValueError('Native source exceeds frozen cap.')
            raw=fetch(f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{source}/{name}',e['size']);publisher=e['lfs']['oid'] if 'lfs' in e else e['oid'];actual=sha(raw) if 'lfs' in e else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
            if len(raw)!=e['size'] or actual!=publisher:raise ValueError('Native publisher mismatch.')
            if name=='metrics.parquet':
                if sha(raw) in seen:raise ValueError('Native fresh bytes already inspected or duplicate.')
                seen.add(sha(raw))
            (directory/name).write_bytes(raw);downloads.append({'id':a['id'],'name':name,'bytes':len(raw),'sha256':sha(raw),'publisher_hash':publisher})
        print(f'Prepared native confirmation {len(downloads)//2}/15',flush=True)
    rows=reconstruct(p);dump(DATA/'inputs.json',rows);dump(DATA/'references.json',original.references(rows))
    m={'schema':'explicit-native-data-1','claims':360,'recordings':15,'plan_sha256':sha(PLAN.read_bytes()),'absence_checked_before_download':True,'downloads':downloads,'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    dump(DATA/'manifest.json',m);validate(check_plan);return m

def validate(check_plan):
    p=check_plan();m=load(DATA/'manifest.json')
    if (m['schema'],m['claims'],m['recordings'],m['plan_sha256'],m['absence_checked_before_download'])!=('explicit-native-data-1',360,15,sha(PLAN.read_bytes()),True) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Native pack identity changed.')
    for n,digest in m['files'].items():
        if sha((DATA/n).read_bytes())!=digest:raise ValueError('Native pack bytes changed.')
    expected={(a['id'],n) for a in p['assignments'] for n in ('metrics.parquet','inject_time.txt')}
    if len(m['downloads'])!=30 or {(a['id'],a['name']) for a in m['downloads']}!=expected or {d.name for d in (DATA/'raw').iterdir()}!={a['id'] for a in p['assignments']}:raise ValueError('Native download set changed.')
    seen=set(p['historical_metric_sha256'])
    for a in m['downloads']:
        raw=(DATA/'raw'/a['id']/a['name']).read_bytes();actual=sha(raw) if len(a['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if len(raw)!=a['bytes'] or sha(raw)!=a['sha256'] or actual!=a['publisher_hash']:raise ValueError('Native publisher bytes changed.')
        if a['name']=='metrics.parquet':
            if sha(raw) in seen:raise ValueError('Native metrics not fresh.')
            seen.add(sha(raw))
    rows=reconstruct(p)
    if len(rows)!=360 or rows!=load(DATA/'inputs.json') or original.references(rows)!=load(DATA/'references.json'):raise ValueError('Native reconstruction changed.')
    return m
