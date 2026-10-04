"""Grouped, pinned RCAEval metric data. Source answers never enter input states."""
import json
from pathlib import Path
from triage_bench.public_data import REVISION, REPOSITORY, fetch, sha, metric_packet
import hashlib

SPLITS = ('train', 'development', 'calibration', 'evaluation')
FAULTS = ('cpu', 'delay', 'disk', 'loss', 'mem', 'socket')
ASSIGNMENTS = {
 'checkoutservice': ('development','calibration','development','train','train','evaluation'),
 'currencyservice': ('train','development','calibration','evaluation','calibration','train'),
 'emailservice': ('calibration','evaluation','train','development','train','development'),
 'productcatalogservice': ('development','train','evaluation','calibration','development','train'),
 'recommendationservice': ('evaluation','train','development','train','evaluation','calibration'),
}
COUNTS = {'train':30, 'development':24, 'calibration':18, 'evaluation':18}


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def partition(index):
    groups, ids = {}, set()
    selected = [r for r in index if r['dataset'] == 'RE2-OB']
    if len(selected) != 90:
        raise ValueError('Expected all 90 RE2-OB source cases.')
    plan = []
    for row in sorted(selected, key=lambda r: r['case']):
        service, fault = row['root_cause_service'], row['fault']
        split = ASSIGNMENTS[service][FAULTS.index(fault)]
        group = f'{service}/{fault}'
        identifier = 'PUB-' + sha(row['case'].encode())[:12]
        if identifier in ids:
            raise ValueError('Duplicate public case.')
        ids.add(identifier)
        groups.setdefault((split, group), []).append(row['repetition'])
        plan.append({'id':identifier, 'split':split, 'group':group, 'source_case':row['case']})
    if len(groups) != 30 or any(sorted(reps) != [1,2,3] for reps in groups.values()):
        raise ValueError('Expected three repeats in each service/fault group.')
    for split in SPLITS:
        rows = [r for r in plan if r['split'] == split]
        if len(rows) != COUNTS[split] or {r['group'].split('/')[1] for r in rows} != set(FAULTS):
            raise ValueError('Unexpected split size or fault coverage.')
    for group in ('checkoutservice/cpu','currencyservice/delay','emailservice/socket'):
        if any(r['split'] != 'development' for r in plan if r['group'] == group):
            raise ValueError('Inspected group escaped development.')
    return plan


def state_from_metrics(columns, boundary):
    normalized={'time':columns['time']};original_services={}
    for column,values in columns.items():
        if column=='time':continue
        service,metric=column.rsplit('_',1)
        key=service.lower()+'_'+metric
        if key in normalized:raise ValueError('Case normalization would merge distinct metric series.')
        normalized[key]=values;original_services[service.lower()]=service
    complete = metric_packet(normalized, boundary, limit=1000)
    # Full summaries, unlike the exploratory top-12 preflight.
    evidence = {}
    for e in sorted(complete['metric_evidence'], key=lambda e:e['source_column']):
        signed = e['change_score']
        if signed is not None and e['after_median'] < e['before_median']:
            signed = -signed
        def rounded(v):
            return None if v is None else float(format(v, '.8g'))
        evidence.setdefault(original_services[e['service']], {})[e['metric']] = [rounded(e['before_median']), rounded(e['after_median']), rounded(signed),
                rounded(e['before_missing']/complete['windows']['before_rows']),
                rounded(e['after_missing']/complete['windows']['after_rows'])]
    return {'condition':'A known fault-injection interval in a controlled benchmark. Select its originating faulty service; symptoms can propagate.',
            'columns':['before_median','after_median','signed_change','before_missing_fraction','after_missing_fraction'],
            'signed_change_definition':'(after_median-before_median)/max(before_p90-before_p10,abs(before_median)*0.01,1e-12). Magnitude measures a shift, not causality or probability.',
            'window_rows':{'before':complete['windows']['before_rows'],'after':complete['windows']['after_rows']},
            'services':evidence}


def build(folder, index_file):
    import pyarrow.parquet as pq
    folder = Path(folder)
    if folder.exists():
        raise ValueError('Public study packs are immutable; use another folder.')
    index_bytes = Path(index_file).read_bytes()
    index = pq.read_table(index_file).to_pylist()
    assignments = partition(index)
    indexed = {r['case']:r for r in index}
    folder.mkdir(parents=True)
    dump(folder/'assignments.json',assignments)
    packets = {s:[] for s in SPLITS}; references = {s:[] for s in SPLITS}; downloads=[]
    base=f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}'
    for i,a in enumerate(assignments):
        case=a['source_case']; row=indexed[case]
        tree=json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{case}'))
        sources={r['path']:r for r in tree if r['type']=='file'}
        for name in ('metrics.parquet','inject_time.txt'):
            source=sources[f'{case}/{name}']
            data=fetch(f'{base}/{case}/{name}',source['size'])
            expected=source['lfs']['oid'] if 'lfs' in source else source['oid']
            actual=sha(data) if 'lfs' in source else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            if len(data)!=source['size'] or actual!=expected:
                raise ValueError('Publisher source hash or size mismatch.')
            target=folder/'raw'/a['id']/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
            downloads.append({'id':a['id'],'name':name,'bytes':len(data),'sha256':sha(data),'publisher_hash':expected})
        boundary=int((target.parent/'inject_time.txt').read_text())
        if boundary!=row['inject_time']: raise ValueError('Boundary mismatch.')
        columns=pq.read_table(target.parent/'metrics.parquet').to_pydict()
        state=state_from_metrics(columns,boundary)
        if state['window_rows']!={'before':row['normal_timesteps'],'after':row['faulty_timesteps']}:
            raise ValueError('Window counts differ from source index.')
        if row['root_cause_service'] not in state['services']:
            raise ValueError('Published cause absent from observed candidates; do not silently repair candidate sets.')
        packets[a['split']].append({'id':a['id'],'state':state})
        references[a['split']].append({'id':a['id'],'group':a['group'],'target':row['root_cause_service'],'fault':row['fault']})
        print(f"Prepared public metrics {i+1}/90",flush=True)
    for split in SPLITS:
        dump(folder/f'{split}.inputs.json',packets[split]); dump(folder/f'{split}.references.json',references[split])
    names=['assignments.json']+[f'{s}.{kind}.json' for s in SPLITS for kind in ('inputs','references')]
    manifest={'schema':'public-rca-pack-1','revision':REVISION,'dataset':'RE2-OB','counts':COUNTS,
              'index_sha256':sha(index_bytes),'files':{n:sha((folder/n).read_bytes()) for n in names},'downloads':downloads,
              'condition':'Known fault boundary; metric summaries only; original labels; no network actions.'}
    dump(folder/'manifest.json',manifest)
    return validate(folder)


def validate(folder):
    folder=Path(folder); m=json.loads((folder/'manifest.json').read_text())
    if m['revision']!=REVISION or m['counts']!=COUNTS:raise ValueError('Unexpected dataset manifest.')
    for n,h in m['files'].items():
        if sha((folder/n).read_bytes())!=h: raise ValueError('Public pack fingerprint mismatch.')
    assignments=json.loads((folder/'assignments.json').read_text())
    groups={};ids=set()
    for split in SPLITS:
        packets=json.loads((folder/f'{split}.inputs.json').read_text());refs=json.loads((folder/f'{split}.references.json').read_text())
        if len(packets)!=COUNTS[split] or {r['id'] for r in packets}!={r['id'] for r in refs}:raise ValueError('Split join or count mismatch.')
        for packet,ref in zip(packets,refs):
            if packet['id']!=ref['id'] or packet['id'] in ids:raise ValueError('Case identity collision.')
            ids.add(packet['id']);groups.setdefault(ref['group'],set()).add(split)
            if ref['target'] not in packet['state']['services']:raise ValueError('Missing cause in candidates.')
            state=json.dumps(packet['state'])
            if any(x in state for x in ('source_case','root_cause_service','scoring_points','re2ob_','inject_time')):raise ValueError('Answer metadata entered state.')
        if {r['id'] for r in packets}!={a['id'] for a in assignments if a['split']==split}:raise ValueError('Assignment drift.')
    if len(groups)!=30 or any(len(s)!=1 for s in groups.values()):raise ValueError('Group leakage.')
    for d in m['downloads']:
        p=folder/'raw'/d['id']/d['name']
        if sha(p.read_bytes())!=d['sha256'] or p.stat().st_size!=d['bytes']:raise ValueError('Raw data changed.')
    return m
