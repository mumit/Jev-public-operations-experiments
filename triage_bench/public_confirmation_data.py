"""Frozen confirmation packs for untouched Train Ticket and Sock Shop reserves."""
import hashlib,json
from pathlib import Path
from .paths import ROOT
from .public_data import REVISION,REPOSITORY,sha,fetch
from .public_rca_data import state_from_metrics,dump
from .public_format_trial import body
from .public_rca_stages import load,committed
from .hosted import encoded

PLAN=ROOT/'checkpoints/public-confirmation-plan-2026-10-04.json'
BASE=ROOT/'runs/public-confirmation'
INDEX=ROOT/'runs/public-data/preflight-2026-10-03-v1/cases.parquet'
COUNTS={'confirmation':54}


def folder(split):
    if split not in COUNTS:raise ValueError('Unknown confirmation split.')
    return BASE/(split+'-data-2026-10-04-v1')


def check_plan():
    p=load(PLAN);committed(PLAN)
    if p['schema']!='public-confirmation-plan-1' or p['counts']!=COUNTS or p['maximum_calls']!=162:raise ValueError('Changed confirmation plan.')
    for mapping in ('source_sha256','evidence_sha256'):
        for name,digest in p[mapping].items():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or sha((ROOT/path).read_bytes())!=digest:raise ValueError('Confirmation source or evidence drift.')
    return p


def prepare(split):
    import pyarrow.parquet as pq
    p=check_plan();destination=folder(split)
    if destination.exists():raise ValueError('Pack already exists; no repeat downloads.')
    from .public_confirmation_trial import eligibility
    eligibility()
    if sha(INDEX.read_bytes())!=p['index_sha256']:raise ValueError('Index drift.')
    rows={r['case']:r for r in pq.read_table(INDEX).to_pylist()};selected=[a for a in p['assignments'] if a['split']==split]
    if len(selected)!=COUNTS[split]:raise ValueError('Unexpected case budget.')
    destination.mkdir(parents=True);packets=[];refs=[];downloads=[];sizes=[]
    base=f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}'
    for number,a in enumerate(selected,1):
        row=rows[a['source_case']];tree=json.loads(fetch(f"https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{a['source_case']}"))
        sources={r['path']:r for r in tree if r['type']=='file'};directory=destination/'raw'/a['id'];directory.mkdir(parents=True)
        for name in ('metrics.parquet','inject_time.txt'):
            entry=sources[a['source_case']+'/'+name]
            if not 0<entry['size']<=5_000_000:raise ValueError('Publisher file exceeds cap.')
            data=fetch(base+'/'+a['source_case']+'/'+name,entry['size']);expected=entry['lfs']['oid'] if 'lfs' in entry else entry['oid']
            actual=sha(data) if 'lfs' in entry else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            if len(data)!=entry['size'] or actual!=expected:raise ValueError('Publisher checksum mismatch.')
            (directory/name).write_bytes(data);downloads.append({'id':a['id'],'name':name,'bytes':len(data),'sha256':sha(data),'publisher_hash':expected})
        boundary=int((directory/'inject_time.txt').read_text())
        if boundary!=row['inject_time']:raise ValueError('Injection boundary drift.')
        state=state_from_metrics(pq.read_table(directory/'metrics.parquet').to_pydict(),boundary)
        if state['window_rows']!={'before':row['normal_timesteps'],'after':row['faulty_timesteps']}:raise ValueError('Source timeline drift.')
        request=body(state,'named');packets.append({'id':a['id'],'state':state,'request':request})
        refs.append({'id':a['id'],'group':a['group'],'fault':row['fault'],'target':row['root_cause_service']})
        # Never add or remove candidates based on the answer.
        if row['root_cause_service'] not in state['services']:raise ValueError('Reference absent from observed candidates.')
        sizes.append({'id':a['id'],'request_bytes':len(encoded(request)),'candidates':len(state['services'])})
        print(f'Prepared confirmation {split} {number}/{COUNTS[split]}',flush=True)
    dump(destination/'inputs.json',packets);dump(destination/'references.json',refs);dump(destination/'sizing.json',sizes)
    m={'schema':'public-confirmation-pack-1','split':split,'cases':len(packets),'revision':REVISION,'plan_sha256':sha(PLAN.read_bytes()),
       'files':{name:sha((destination/name).read_bytes()) for name in ('inputs.json','references.json','sizing.json')},'downloads':downloads,
       'largest_request_bytes':max(r['request_bytes'] for r in sizes),'fits_empirical_wire_cap':all(r['request_bytes']<=p['maximum_request_bytes'] for r in sizes)}
    dump(destination/'manifest.json',m);validate(split);return m


def validate(split):
    import pyarrow.parquet as pq
    p=check_plan();directory=folder(split);m=load(directory/'manifest.json')
    if sha(INDEX.read_bytes())!=p['index_sha256']:raise ValueError('Pinned index changed.')
    if (m['split'],m['cases'],m['revision'],m['plan_sha256'])!=(split,COUNTS[split],REVISION,sha(PLAN.read_bytes())):raise ValueError('Pack identity drift.')
    if set(m['files'])!={'inputs.json','references.json','sizing.json'}:raise ValueError('Unknown pack files.')
    for name,digest in m['files'].items():
        if sha((directory/name).read_bytes())!=digest:raise ValueError('Pack file drift.')
    expected={a['id']:a for a in p['assignments'] if a['split']==split}
    packets=load(directory/'inputs.json');refs=load(directory/'references.json');sizes=load(directory/'sizing.json')
    if len(packets)!=COUNTS[split] or {r['id'] for r in packets}!=set(expected) or {r['id'] for r in refs}!=set(expected):raise ValueError('Case identity drift.')
    if {d.name for d in (directory/'raw').iterdir()}!=set(expected):raise ValueError('Undeclared raw case.')
    if len(m['downloads'])!=COUNTS[split]*2 or {(d['id'],d['name']) for d in m['downloads']}!={(i,n) for i in expected for n in ('metrics.parquet','inject_time.txt')}:raise ValueError('Changed download identities.')
    for d in m['downloads']:
        data=(directory/'raw'/d['id']/d['name']).read_bytes()
        if len(data)!=d['bytes'] or sha(data)!=d['sha256']:raise ValueError('Measurement hash drift.')
        expected_hash=sha(data) if len(d['publisher_hash'])==64 else hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        if expected_hash!=d['publisher_hash']:raise ValueError('Publisher evidence drift.')
    computed=[];index={r['case']:r for r in pq.read_table(INDEX).to_pylist()}
    for packet,ref in zip(packets,refs):
        a=expected[packet['id']];row=index[a['source_case']];raw=directory/'raw'/packet['id'];boundary=int((raw/'inject_time.txt').read_text())
        if boundary!=row['inject_time'] or ref!={'id':a['id'],'group':a['group'],'fault':row['fault'],'target':row['root_cause_service']}:raise ValueError('Reference drift.')
        state=state_from_metrics(pq.read_table(raw/'metrics.parquet').to_pydict(),boundary)
        if state!=packet['state'] or body(state,'named')!=packet['request']:raise ValueError('Request reconstruction failed.')
        if any(term in json.dumps(packet['request']) for term in ('re2tt_','root_cause_service','source_case',packet['id'])):raise ValueError('Answer metadata entered wire.')
        computed.append({'id':packet['id'],'request_bytes':len(encoded(packet['request'])),'candidates':len(state['services'])})
    if computed!=sizes or m['largest_request_bytes']!=max(r['request_bytes'] for r in sizes) or m['fits_empirical_wire_cap']!=all(r['request_bytes']<=p['maximum_request_bytes'] for r in sizes):raise ValueError('Sizing drift.')
    return m
