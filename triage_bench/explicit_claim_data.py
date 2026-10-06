"""Controlled field-entry fixtures, independent references and fresh grouped metrics."""
import copy,json,hashlib
from .paths import ROOT
from .public_data import sha,REVISION,REPOSITORY,fetch
from .public_rca_stages import load,committed
from .public_rca_data import state_from_metrics,dump
from .public_fresh_claim_data import DATA as OLD_DATA
from .public_claim_reference import evaluate as oracle
from .explicit_claim_features import KINDS,DURATIONS,request

BASE=ROOT/'runs/explicit-claims'
PLAN=ROOT/'checkpoints/explicit-claims-plan-2026-10-06.json'
INDEX=ROOT/'runs/public-data/preflight-2026-10-03-v1/cases.parquet'

def folder(phase):
    if phase not in ('development','confirmation'):raise ValueError('Unknown explicit-claim phase.')
    return BASE/(phase+'-data-2026-10-06-v1')

def entries(observation,identifier,dataset,recording,category):
    rows=[];channels=sorted(observation['metrics']);channel=channels[int(sha((identifier+'channel').encode()),16)%len(channels)]
    measure=DURATIONS[int(sha((identifier+'duration').encode()),16)%len(DURATIONS)]
    for kind in KINDS:
        for asserted in (True,False):
            claim={'service':observation['service'],'kind':kind,'asserted':asserted}
            if kind.startswith('metric_'):claim['channel']=channel
            if kind=='duration_material':claim['measure']=measure
            rows.append({'id':identifier+'-'+kind+'-'+str(int(asserted)),'recording':recording,'dataset':dataset,
              'category':category,'observation':copy.deepcopy(observation),'claim':claim})
    return rows

def boundaries():
    o={'service':'example-service','metrics':{'cpu':{'signed_change':3.,'before_missing_fraction':.2,'after_missing_fraction':.2}},
       'trace':{'before':{'spans':5,**{m:100. for m in DURATIONS}},'after':{'spans':5,**{m:125. for m in DURATIONS}}},'window_seconds':{'before':900,'after':900}}
    fixtures=[]
    for label,value,missing,kind in [('metric_equal',3.,.2,'metric_material'),('metric_below',2.999,.2,'metric_material'),('metric_decrease',-3.,.2,'metric_material'),('missing_excess',3.,.200001,'metric_material'),('missing_value',None,.2,'metric_material'),('direction_zero',0.,.2,'metric_direction'),('direction_negative',-1.,.2,'metric_direction')]:
        z=copy.deepcopy(o);z['metrics']['cpu'].update(signed_change=value,after_missing_fraction=missing)
        fixtures.append((label,z,{'kind':kind,'channel':'cpu'},'unanswerable' if value is None or missing>.2 else value>0 if kind=='metric_direction' else abs(value)>=3))
    for label,b,a,count,truth in [('duration_equal',100.,125.,5,True),('duration_below',100.,124.999,5,False),('duration_decrease',100.,75.,5,True),('duration_zero_start',0.,125.,5,'unanswerable'),('duration_few_spans',100.,125.,4,'unanswerable'),('duration_missing',None,125.,5,'unanswerable')]:
        z=copy.deepcopy(o);z['trace']['before']['duration_median_us']=b;z['trace']['after']['duration_median_us']=a;z['trace']['after']['spans']=count
        fixtures.append((label,z,{'kind':'duration_material','measure':'duration_median_us'},truth))
    for label,count,truth in [('spans_equal',5,True),('spans_few',4,False),('spans_zero',0,False)]:
        z=copy.deepcopy(o);z['trace']['after']['spans']=count;fixtures.append((label,z,{'kind':'span_adequacy'},truth))
    z=copy.deepcopy(o);z['trace']=None
    fixtures.append(('trace_absent',z,{'kind':'span_adequacy'},'unanswerable'))
    result=[]
    for label,z,c,truth in fixtures:
        for asserted in (True,False):
            claim={'service':z['service'],**c,'asserted':asserted}
            answer='unanswerable' if truth=='unanswerable' else 'supported' if truth==asserted else 'contradicted'
            result.append({'id':'ECB-'+label+'-'+str(int(asserted)),'dataset':'Policy fixtures','recording':label,'category':'constructed_boundary','observation':z,'claim':claim,'fixture_answer':answer})
    return result

def development():
    rows=[]
    for p in load(OLD_DATA/'inputs.json'):
        for i,o in enumerate(p['observations']):rows.extend(entries(o,'ECL-'+sha((p['id']+str(i)).encode())[:12],p['dataset'],p['case_id'],'inspected_public'))
    return rows+boundaries()

def allocation():
    import pyarrow.parquet as pq
    index=[r for r in pq.read_table(INDEX).to_pylist() if r['dataset']=='RE1-OB']
    groups=sorted({r['root_cause_service']+'/'+r['fault'] for r in index},key=lambda g:sha(('explicit-claims-v1/'+g).encode()))[:3]
    chosen=[{'id':'ECF-'+sha(r['case'].encode())[:12],'source_case':r['case'],'group':'RE1-OB/'+r['root_cause_service']+'/'+r['fault'],'dataset':'Online Boutique'} for r in sorted(index,key=lambda r:r['case']) if r['root_cause_service']+'/'+r['fault'] in groups]
    if len(chosen)!=15 or any(sum(a['group']==g for a in chosen)!=5 for g in {a['group'] for a in chosen}):raise ValueError('Fresh group size changed.')
    return chosen

def fresh_observations(directory,row):
    import pyarrow.parquet as pq
    boundary=int((directory/'inject_time.txt').read_text())
    if boundary!=row['inject_time']:raise ValueError('Boundary differs from pinned index.')
    table=pq.read_table(directory/'metrics.parquet').to_pydict();state=state_from_metrics(table,boundary)
    if state['window_rows']!={'before':row['normal_timesteps'],'after':row['faulty_timesteps']}:raise ValueError('Window row mismatch.')
    times=table['time'];before=[t for t in times if t<boundary];after=[t for t in times if t>=boundary]
    names=sorted(state['services'],key=lambda s:sha(('explicit-services/'+row['case']+'/'+s).encode()))[:2]
    if len(names)!=2:raise ValueError('Two observed services required.')
    return [{'service':s,'metrics':{m:dict(zip(state['columns'],v)) for m,v in state['services'][s].items()},'trace':None,
      'window_seconds':{'before':int(max(before)-min(before)+1),'after':int(max(after)-min(after)+1)}} for s in names]

def references(rows):
    refs=[]
    for p in rows:
        c=p['claim'];prop={k:v for k,v in c.items() if k!='service'}
        r=oracle(p['observation'],prop)
        if 'fixture_answer' in p and p['fixture_answer']!=r['answer']:raise ValueError('Hand-specified fixture and independent reference disagree.')
        refs.append({'id':p['id'],**r})
    return refs

def prepare(phase,check_plan):
    plan=check_plan();destination=folder(phase)
    if destination.exists():raise ValueError('Never overwrite a prepared pack.')
    downloads=[]
    if phase=='development':rows=development()
    else:
        # The caller verifies the development gate before any new measurement is opened.
        import pyarrow.parquet as pq
        index={r['case']:r for r in pq.read_table(INDEX).to_pylist()};seen=set(plan['historical_metric_sha256']);rows=[]
        destination.mkdir(parents=True)
        for a in plan['assignments']:
            source=a['source_case'];directory=destination/'raw'/a['id'];directory.mkdir(parents=True)
            tree={e['path']:e for e in json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source}')) if e['type']=='file'}
            for name in ('metrics.parquet','inject_time.txt'):
                e=tree[source+'/'+name]
                if not 0<e['size']<=5_000_000:raise ValueError('Frozen source size cap exceeded.')
                data=fetch(f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{source}/{name}',e['size'])
                digest=e['lfs']['oid'] if 'lfs' in e else e['oid'];actual=sha(data) if 'lfs' in e else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
                if len(data)!=e['size'] or actual!=digest:raise ValueError('Publisher checksum mismatch.')
                if name=='metrics.parquet':
                    if sha(data) in seen:raise ValueError('Measurement already opened or duplicated.')
                    seen.add(sha(data))
                (directory/name).write_bytes(data);downloads.append({'id':a['id'],'name':name,'bytes':len(data),'sha256':sha(data),'publisher_hash':digest})
            for i,o in enumerate(fresh_observations(directory,index[source])):rows.extend(entries(o,a['id']+'-'+str(i),a['dataset'],a['id'],'fresh_public_metrics'))
            print(f'Prepared explicit fresh measurements {len(downloads)//2}/15',flush=True)
    destination.mkdir(parents=True,exist_ok=phase=='confirmation')
    # References stay in a separate file and never enter the wire packets.
    fixtures={p['id']:p.pop('fixture_answer') for p in rows if 'fixture_answer' in p}
    refs=references([{**p,**({'fixture_answer':fixtures[p['id']]} if p['id'] in fixtures else {})} for p in rows])
    dump(destination/'inputs.json',rows);dump(destination/'references.json',refs)
    m={'schema':'explicit-claim-data-1','phase':phase,'plan_sha256':sha(PLAN.read_bytes()),'claims':len(rows),'downloads':downloads,
       'files':{n:sha((destination/n).read_bytes()) for n in ('inputs.json','references.json')}}
    dump(destination/'manifest.json',m);return m

def validate_pack(phase,check_plan):
    p=check_plan();d=folder(phase);m=load(d/'manifest.json')
    if m['schema']!='explicit-claim-data-1' or m['phase']!=phase or m['plan_sha256']!=sha(PLAN.read_bytes()) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Explicit pack identity changed.')
    for n,digest in m['files'].items():
        if sha((d/n).read_bytes())!=digest:raise ValueError('Explicit pack bytes changed.')
    if phase=='development':rows=development()
    else:
        import pyarrow.parquet as pq
        index={r['case']:r for r in pq.read_table(INDEX).to_pylist()};rows=[];seen=set(p['historical_metric_sha256'])
        expected={(a['id'],n) for a in p['assignments'] for n in ('metrics.parquet','inject_time.txt')}
        if len(m['downloads'])!=30 or {(a['id'],a['name']) for a in m['downloads']}!=expected or {r.name for r in (d/'raw').iterdir()}!={a['id'] for a in p['assignments']}:raise ValueError('Fresh download allocation changed.')
        for a in m['downloads']:
            raw=(d/'raw'/a['id']/a['name']).read_bytes();actual=sha(raw) if len(a['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
            if len(raw)!=a['bytes'] or sha(raw)!=a['sha256'] or actual!=a['publisher_hash']:raise ValueError('Publisher or local bytes changed.')
            if a['name']=='metrics.parquet':
                if sha(raw) in seen:raise ValueError('Reused fresh metric bytes.')
                seen.add(sha(raw))
        for a in p['assignments']:
            for i,o in enumerate(fresh_observations(d/'raw'/a['id'],index[a['source_case']])):rows.extend(entries(o,a['id']+'-'+str(i),a['dataset'],a['id'],'fresh_public_metrics'))
    refs=references(rows)
    for r in rows:r.pop('fixture_answer',None)
    if rows!=load(d/'inputs.json') or refs!=load(d/'references.json') or len(rows)!=m['claims']:raise ValueError('Explicit reconstruction changed.')
    for row in rows:
        wire=json.dumps(request(row['observation'],row['claim']))
        if any(x in wire for x in ('source_case','root_cause_service',row['id'],'fixture_answer','reference')):raise ValueError('Reference metadata entered wire.')
    return m
