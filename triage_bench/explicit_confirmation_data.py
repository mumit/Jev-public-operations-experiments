"""Fresh grouped metrics for the separately selected calculated-fact candidate."""
import hashlib,json
from .paths import ROOT
from .public_data import sha,REVISION,REPOSITORY,fetch
from .public_rca_data import dump
from .public_rca_stages import load
from . import explicit_claim_data as original

PLAN=ROOT/'checkpoints/explicit-confirmation-plan-2026-10-06.json'
BASE=ROOT/'runs/explicit-confirmation'
DATA=BASE/'confirmation-data-2026-10-06-v1'

def allocation():
    import pyarrow.parquet as pq
    index=[r for r in pq.read_table(original.INDEX).to_pylist() if r['dataset']=='RE1-OB']
    groups=sorted({r['root_cause_service']+'/'+r['fault'] for r in index},key=lambda g:sha(('explicit-claims-v1/'+g).encode()))[3:6]
    rows=[{'id':'ECC-'+sha(r['case'].encode())[:12],'source_case':r['case'],'group':'RE1-OB/'+r['root_cause_service']+'/'+r['fault'],'dataset':'Online Boutique'} for r in sorted(index,key=lambda r:r['case']) if r['root_cause_service']+'/'+r['fault'] in groups]
    if len(rows)!=15 or any(sum(a['group']==g for a in rows)!=5 for g in {a['group'] for a in rows}) or {r['source_case'] for r in rows}&{r['source_case'] for r in original.allocation()}:raise ValueError('Confirmation groups overlap sealed original allocation.')
    return rows

def reconstruct(plan):
    import pyarrow.parquet as pq
    index={r['case']:r for r in pq.read_table(original.INDEX).to_pylist()};rows=[]
    for a in plan['assignments']:
        for i,o in enumerate(original.fresh_observations(DATA/'raw'/a['id'],index[a['source_case']])):
            rows.extend(original.entries(o,a['id']+'-'+str(i),a['dataset'],a['id'],'fresh_public_metrics'))
    return rows

def prepare(check_plan):
    p=check_plan()
    if DATA.exists():raise ValueError('Fresh confirmation already started; never overwrite.')
    names={d.name for d in ROOT.glob('runs/**/raw/*')}
    for a in p['assignments']:
        if any(n.endswith(sha(a['source_case'].encode())[:12]) for n in names):raise ValueError('Assigned confirmation recording was opened.')
    seen=set(p['historical_metric_sha256']);downloads=[];DATA.mkdir(parents=True)
    for a in p['assignments']:
        source=a['source_case'];directory=DATA/'raw'/a['id'];directory.mkdir(parents=True)
        tree={e['path']:e for e in json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source}')) if e['type']=='file'}
        for name in ('metrics.parquet','inject_time.txt'):
            e=tree[source+'/'+name]
            if not 0<e['size']<=5_000_000:raise ValueError('Frozen source cap exceeded.')
            raw=fetch(f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{source}/{name}',e['size']);digest=e['lfs']['oid'] if 'lfs' in e else e['oid']
            actual=sha(raw) if 'lfs' in e else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
            if len(raw)!=e['size'] or actual!=digest:raise ValueError('Publisher checksum mismatch.')
            if name=='metrics.parquet':
                if sha(raw) in seen:raise ValueError('Fresh metric bytes previously opened or duplicate.')
                seen.add(sha(raw))
            (directory/name).write_bytes(raw);downloads.append({'id':a['id'],'name':name,'bytes':len(raw),'sha256':sha(raw),'publisher_hash':digest})
        print(f'Prepared calculated confirmation {len(downloads)//2}/15',flush=True)
    rows=reconstruct(p);dump(DATA/'inputs.json',rows);dump(DATA/'references.json',original.references(rows))
    m={'schema':'explicit-confirmation-data-1','claims':360,'recordings':15,'plan_sha256':sha(PLAN.read_bytes()),'absence_checked_before_download':True,'downloads':downloads,'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    dump(DATA/'manifest.json',m);validate(check_plan);return m

def validate(check_plan):
    p=check_plan();m=load(DATA/'manifest.json')
    if (m['schema'],m['claims'],m['recordings'],m['plan_sha256'],m['absence_checked_before_download'])!=('explicit-confirmation-data-1',360,15,sha(PLAN.read_bytes()),True) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Fresh confirmation pack changed.')
    for n,digest in m['files'].items():
        if sha((DATA/n).read_bytes())!=digest:raise ValueError('Fresh pack fingerprint changed.')
    expected={(a['id'],n) for a in p['assignments'] for n in ('metrics.parquet','inject_time.txt')}
    if len(m['downloads'])!=30 or {(a['id'],a['name']) for a in m['downloads']}!=expected or {d.name for d in (DATA/'raw').iterdir()}!={a['id'] for a in p['assignments']}:raise ValueError('Fresh download coverage changed.')
    seen=set(p['historical_metric_sha256'])
    for a in m['downloads']:
        raw=(DATA/'raw'/a['id']/a['name']).read_bytes();actual=sha(raw) if len(a['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if len(raw)!=a['bytes'] or sha(raw)!=a['sha256'] or actual!=a['publisher_hash']:raise ValueError('Fresh publisher bytes changed.')
        if a['name']=='metrics.parquet':
            if sha(raw) in seen:raise ValueError('Reused fresh measurements.')
            seen.add(sha(raw))
    rows=reconstruct(p)
    if len(rows)!=360 or rows!=load(DATA/'inputs.json') or original.references(rows)!=load(DATA/'references.json'):raise ValueError('Fresh reconstruction changed.')
    return m
