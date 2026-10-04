"""A new input-presentation study; historical data and summaries stay frozen."""
import copy
import hashlib
import json
from pathlib import Path

from .public_data import REVISION, REPOSITORY, fetch, sha
from .public_rca_data import dump, state_from_metrics, FAULTS

ARMS = ('compact', 'named', 'explained')
SERVICES = ('carts', 'catalogue', 'orders', 'payment', 'user')
COUNTS = {'development':24, 'calibration':18, 'evaluation':36}
FIELDS = ('before_median', 'after_median', 'signed_change', 'before_missing_fraction', 'after_missing_fraction')
# Interpret the labels conservatively: the downloaded index does not specify units.
# These definitions do not name a fault, select a service or add measurements.
DEFINITIONS = {
    'cpu':'Observed CPU usage metric. Values retain the source scale; no conversion to cores or percent is assumed.',
    'mem':'Observed memory usage metric. Values retain the source scale; no conversion to bytes or utilization percent is assumed.',
    'diskio':'Observed disk I/O metric. Values retain the source scale; no conversion to bytes per second or operations per second is assumed.',
    'socket':'Observed socket metric. Values retain the source scale. Compare the raw before/after medians as well as signed_change; signed_change is not a raw count ratio.',
    'workload':'Observed workload metric. Values retain the source scale; no conversion to requests per second is assumed.',
    'error':'Observed error metric. Values retain the source scale; no conversion to an error count or error fraction is assumed.',
    'latency-50':'Observed latency metric labelled latency-50. Values retain the source scale; no conversion to seconds or milliseconds is assumed.',
    'latency-90':'Observed latency metric labelled latency-90. Values retain the source scale; no conversion to seconds or milliseconds is assumed.',
}


def transform(state, arm):
    if arm not in ARMS:raise ValueError('Unknown input arm.')
    if tuple(state['columns']) != FIELDS:raise ValueError('Unknown summary layout.')
    result=copy.deepcopy(state)
    if arm=='compact':return result
    result['services']={service:{metric:dict(zip(FIELDS,values,strict=True)) for metric,values in metrics.items()}
                        for service,metrics in state['services'].items()}
    if arm=='explained':
        result['metric_definitions']={m:DEFINITIONS[m] for m in sorted({m for rows in state['services'].values() for m in rows})}
        result['field_definitions']={
            'before_median':'Median measurement before the supplied incident boundary, in source units.',
            'after_median':'Median measurement at or after that boundary, in the same source units.',
            'signed_change':'Dimensionless baseline-scaled median difference using signed_change_definition. Its sign gives direction. A large value is a change, not a probability, causal attribution or before/after ratio. Flat baselines can produce large scores for modest raw changes.',
            'before_missing_fraction':'Fraction of unavailable measurements before the boundary, between 0 and 1.',
            'after_missing_fraction':'Fraction of unavailable measurements at or after the boundary, between 0 and 1.',
        }
    return result


def restore(state, arm):
    """Prove named inputs preserve every measurement, candidate and shared definition."""
    result=copy.deepcopy(state)
    if arm=='compact':return result
    result.pop('metric_definitions',None);result.pop('field_definitions',None)
    result['services']={service:{metric:[values[f] for f in FIELDS] for metric,values in metrics.items()}
                        for service,metrics in state['services'].items()}
    return result


def partition(index):
    rows=sorted((r for r in index if r['dataset']=='RE2-SS'),key=lambda r:r['case'])
    if len(rows)!=90:raise ValueError('Expected all 90 Sock Shop index entries.')
    plan=[];groups={}
    for row in rows:
        service,fault=row['root_cause_service'],row['fault']
        si,fi=SERVICES.index(service),FAULTS.index(fault)
        offset=(si-fi)%len(SERVICES)
        split='calibration' if offset==0 else 'evaluation' if offset in (1,2) else 'reserve'
        group=service+'/'+fault
        plan.append({'id':'FMT-'+sha(row['case'].encode())[:12], 'split':split,'group':group,'source_case':row['case']})
        groups.setdefault(group,[]).append(row['repetition'])
    if len(groups)!=30 or any(sorted(v)!=[1,2,3] for v in groups.values()):raise ValueError('Unexpected source repetitions.')
    if len({r['id'] for r in plan})!=90:raise ValueError('Identifier collision.')
    for split,count in [('calibration',18),('evaluation',36),('reserve',36)]:
        chosen=[r for r in plan if r['split']==split]
        if len(chosen)!=count or {r['group'].split('/')[1] for r in chosen}!=set(FAULTS):raise ValueError('Split counts or coverage differ.')
    return plan


def build(folder,index_file,development):
    import pyarrow.parquet as pq
    folder=Path(folder);development=Path(development)
    if folder.exists():raise ValueError('Input-study packs are immutable.')
    from .public_rca_data import validate as validate_old
    old=validate_old(development)
    index_bytes=Path(index_file).read_bytes()
    if sha(index_bytes)!=old['index_sha256']:raise ValueError('Index revision differs from historical development.')
    index=pq.read_table(index_file).to_pylist();plan=partition(index);indexed={r['case']:r for r in index}
    folder.mkdir(parents=True);dump(folder/'assignments.json',plan)
    packets={'development':json.loads((development/'development.inputs.json').read_text()),'calibration':[],'evaluation':[]}
    refs={'development':json.loads((development/'development.references.json').read_text()),'calibration':[],'evaluation':[]}
    downloads=[];base=f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}'
    # Reserved rows are metadata only. Do not download their telemetry.
    for i,a in enumerate(r for r in plan if r['split']!='reserve'):
        case=a['source_case'];row=indexed[case]
        tree=json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{case}'))
        sources={r['path']:r for r in tree if r['type']=='file'}
        directory=folder/'raw'/a['id'];directory.mkdir(parents=True)
        for name in ('metrics.parquet','inject_time.txt'):
            source=sources[f'{case}/{name}'];content=fetch(f'{base}/{case}/{name}',source['size'])
            expected=source['lfs']['oid'] if 'lfs' in source else source['oid']
            actual=sha(content) if 'lfs' in source else hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()
            if actual!=expected or len(content)!=source['size']:raise ValueError('Publisher hash or size mismatch.')
            (directory/name).write_bytes(content)
            downloads.append({'id':a['id'],'name':name,'bytes':len(content),'sha256':sha(content),'publisher_hash':expected})
        boundary=int((directory/'inject_time.txt').read_text())
        if boundary!=row['inject_time']:raise ValueError('Source boundary mismatch.')
        state=state_from_metrics(pq.read_table(directory/'metrics.parquet').to_pydict(),boundary)
        if state['window_rows']!={'before':row['normal_timesteps'],'after':row['faulty_timesteps']}:raise ValueError('Window rows differ.')
        if row['root_cause_service'] not in state['services']:raise ValueError('Cause outside observed candidates; do not add it using the label.')
        packets[a['split']].append({'id':a['id'],'state':state})
        refs[a['split']].append({'id':a['id'],'group':a['group'],'target':row['root_cause_service'],'fault':row['fault']})
        print(f'Prepared new public input case {i+1}/54',flush=True)
    for split in COUNTS:
        dump(folder/f'{split}.inputs.json',packets[split]);dump(folder/f'{split}.references.json',refs[split])
    files=['assignments.json']+[f'{s}.{kind}.json' for s in COUNTS for kind in ('inputs','references')]
    dump(folder/'manifest.json',{'schema':'public-format-pack-1','revision':REVISION,'counts':COUNTS,
        'datasets':{'development':'RE2-OB','calibration':'RE2-SS','evaluation':'RE2-SS'},
        'development_manifest_sha256':sha((development/'manifest.json').read_bytes()),'index_sha256':sha(index_bytes),
        'files':{n:sha((folder/n).read_bytes()) for n in files},'downloads':downloads,'reserved_cases':36})
    return validate(folder)


def validate(folder):
    folder=Path(folder);m=json.loads((folder/'manifest.json').read_text())
    if m['revision']!=REVISION or m['counts']!=COUNTS or m['reserved_cases']!=36:raise ValueError('Unexpected manifest.')
    for name,digest in m['files'].items():
        if sha((folder/name).read_bytes())!=digest:raise ValueError('Changed input-study data.')
    plan=json.loads((folder/'assignments.json').read_text());ids=set();groups={}
    for split,count in COUNTS.items():
        packets=json.loads((folder/f'{split}.inputs.json').read_text());refs=json.loads((folder/f'{split}.references.json').read_text())
        if len(packets)!=count or len(refs)!=count:raise ValueError('Split size differs.')
        for p,r in zip(packets,refs):
            if p['id']!=r['id'] or p['id'] in ids:raise ValueError('Duplicate or mismatched input/reference identity.')
            ids.add(p['id']);groups.setdefault((m['datasets'][split],r['group']),set()).add(split)
            state=p['state']
            if r['target'] not in state['services']:raise ValueError('Candidate construction lost source cause.')
            if set(state)!= {'condition','columns','signed_change_definition','window_rows','services'}:raise ValueError('State allowlist changed.')
            if any(x in json.dumps(state) for x in ('source_case','root_cause_service','re2ss_','re2ob_','inject_time','scoring_points')):raise ValueError('Answer metadata in inputs.')
            for arm in ARMS:
                if restore(transform(state,arm),arm)!=state:raise ValueError('Presentation changed evidence.')
        if split!='development' and {p['id'] for p in packets}!={a['id'] for a in plan if a['split']==split}:raise ValueError('Group assignment drift.')
    if any(len(s)!=1 for s in groups.values()):raise ValueError('Group leakage.')
    reserved={a['id'] for a in plan if a['split']=='reserve'}
    if ids&reserved or any((folder/'raw'/identifier).exists() for identifier in reserved):raise ValueError('Reserved evidence entered the study.')
    for r in m['downloads']:
        path=folder/'raw'/r['id']/r['name']
        if path.stat().st_size!=r['bytes'] or sha(path.read_bytes())!=r['sha256']:raise ValueError('Changed source bytes.')
    return m
