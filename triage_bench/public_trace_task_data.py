"""Fresh development groups; the earlier 22-case evaluation panel stays protected."""
import hashlib
import json
from pathlib import Path
from .paths import ROOT
from .public_data import REVISION, REPOSITORY, sha, fetch
from .public_rca_data import dump
from .public_rca_stages import load, committed
from .public_trace_data_v2 import PLAN as PREVIOUS, INDEX, reconstruct as old_reconstruct
from .public_trace_task_features import changes, requests, ARMS
from .hosted import encoded

PLAN = ROOT / 'checkpoints/public-trace-task-plan-2026-10-04.json'
BASE = ROOT / 'runs/public-trace-task'
COUNTS = {'development': 16, 'evaluation': 22}
DEVELOPMENT = {'RE3-TT/ts-auth-service/f3', 'RE3-TT/ts-route-service/f3',
               'RE3-OB/adservice/f5', 'RE3-OB/emailservice/f1'}


def partition(previous):
    result = []
    for source in previous:
        split = 'previous_development' if source['split'] == 'development' else source['split']
        if source['group'] in DEVELOPMENT:
            if split != 'reserve':
                raise ValueError('New development must come from untouched reserves.')
            split = 'development'
        result.append({**source, 'id': 'TQA-' + sha(source['source_case'].encode())[:12], 'split': split})
    if len(result) != 60 or len({r['source_case'] for r in result}) != 60:
        raise ValueError('Trace task case identity drift.')
    for name, expected in [('Train Ticket', (10, 10, 3, 7)), ('Online Boutique', (6, 12, 6, 6))]:
        counts = tuple(sum(r['dataset'] == name and r['split'] == s for r in result)
                       for s in ('development', 'evaluation', 'reserve', 'previous_development'))
        if counts != expected:
            raise ValueError('Trace task allocation drift.')
    groups = {}
    for row in result:
        groups.setdefault(row['group'], set()).add(row['split'])
    if any(len(s) != 1 for s in groups.values()):
        raise ValueError('Trace task group leakage.')
    return result


def arms(split):
    if split == 'development':
        return ARMS
    if split == 'evaluation':
        return ('traces', 'trace_deltas')
    raise ValueError('Unknown task split.')


def folder(split):
    arms(split)
    return BASE / (split + '-data-2026-10-04-v1')


def check_plan():
    committed(PLAN)
    p = load(PLAN)
    if (p['schema'], p['counts'], p['revision'], p['maximum_calls']) != ('public-trace-task-plan-1', COUNTS, REVISION, 324):
        raise ValueError('Task plan identity changed.')
    if sha(INDEX.read_bytes()) != p['index_sha256'] or p['assignments'] != partition(load(PREVIOUS)['assignments']):
        raise ValueError('Task allocation changed.')
    for mapping in ('source_sha256', 'evidence_sha256'):
        for name, digest in p[mapping].items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or sha((ROOT / path).read_bytes()) != digest:
                raise ValueError('Task source or prerequisite changed.')
    return p


def reconstruct(directory, row):
    state, context, old = old_reconstruct(directory, row)
    delta = changes(context, row['inject_time'] - row['time_start'], row['time_end'] + 1 - row['inject_time'])
    actual = requests(state, context, delta)
    if any(actual[arm] != old[arm] for arm in ('metrics', 'traces')):
        raise ValueError('Original metric/trace control changed.')
    return state, context, delta, actual


def sizing(packet, split):
    return {'id': packet['id'], 'candidates': len(packet['state']['services']),
            'trace_services': len(packet['trace_context']['services']),
            'request_bytes': {a: len(encoded(packet['requests'][a])) for a in arms(split)}}


def prepare(split):
    import pyarrow.parquet as pq
    p = check_plan()
    if split == 'evaluation':
        from .public_trace_task_trial import check_candidate
        check_candidate()
    destination = folder(split)
    if destination.exists():
        raise ValueError('Task pack exists; never overwrite.')
    selected = [r for r in p['assignments'] if r['split'] == split]
    if len(selected) != COUNTS[split]:
        raise ValueError('Task split count changed.')
    index = {r['case']: r for r in pq.read_table(INDEX).to_pylist()}
    # Check absence in both earlier trace data directories before opening new telemetry.
    previous = {r['source_case']: r['id'] for r in load(PREVIOUS)['assignments']}
    for row in selected:
        if any((ROOT / ('runs/public-traces/' + stage) / 'raw' / previous[row['source_case']]).exists()
               for stage in ('development-data-2026-10-04-v1', 'development-data-2026-10-04-v2', 'evaluation-data-2026-10-04-v2')):
            raise ValueError('Fresh task case was already opened by the earlier study.')
    destination.mkdir(parents=True)
    packets, references, downloads = [], [], []
    for assignment in selected:
        directory = destination / 'raw' / assignment['id']
        directory.mkdir(parents=True)
        source = assignment['source_case']
        entries = {r['path']: r for r in json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source}')) if r['type'] == 'file'}
        for name in ('metrics.parquet', 'traces.parquet', 'inject_time.txt'):
            entry = entries[source + '/' + name]
            if not 0 < entry['size'] <= 50_000_000:
                raise ValueError('Task source file exceeds cap.')
            raw = fetch(f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{source}/{name}', entry['size'])
            publisher = entry['lfs']['oid'] if 'lfs' in entry else entry['oid']
            actual = sha(raw) if 'lfs' in entry else hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
            if len(raw) != entry['size'] or actual != publisher:
                raise ValueError('Task publisher checksum mismatch.')
            (directory / name).write_bytes(raw)
            downloads.append({'id': assignment['id'], 'name': name, 'bytes': len(raw), 'sha256': sha(raw), 'publisher_hash': publisher})
        row = index[source]
        state, context, delta, actual = reconstruct(directory, row)
        packets.append({'id': assignment['id'], 'state': state, 'trace_context': context,
                        'trace_changes': delta, 'requests': {a: actual[a] for a in arms(split)}})
        references.append({'id': assignment['id'], 'group': assignment['group'], 'target': row['root_cause_service'], 'fault': row['fault']})
        print(f'Prepared trace task {split} {len(packets)}/{len(selected)}', flush=True)
    sizes = [sizing(p, split) for p in packets]
    for name, value in [('inputs.json', packets), ('references.json', references), ('sizing.json', sizes)]:
        dump(destination / name, value)
    manifest = {'schema': 'public-trace-task-pack-1', 'split': split, 'cases': len(packets), 'revision': REVISION,
                'plan_sha256': sha(PLAN.read_bytes()), 'downloads': downloads,
                'files': {n: sha((destination / n).read_bytes()) for n in ('inputs.json', 'references.json', 'sizing.json')},
                'largest_request_bytes': max(v for r in sizes for v in r['request_bytes'].values()),
                'fits_empirical_wire_cap': all(v <= p['maximum_request_bytes'] for r in sizes for v in r['request_bytes'].values())}
    dump(destination / 'manifest.json', manifest)
    validate(split)
    return manifest


def validate(split):
    import pyarrow.parquet as pq
    p = check_plan()
    directory = folder(split)
    m = load(directory / 'manifest.json')
    if (m['schema'], m['split'], m['cases'], m['revision'], m['plan_sha256']) != ('public-trace-task-pack-1', split, COUNTS[split], REVISION, sha(PLAN.read_bytes())):
        raise ValueError('Task pack identity changed.')
    if set(m['files']) != {'inputs.json', 'references.json', 'sizing.json'}:
        raise ValueError('Unexpected task pack files.')
    for name, digest in m['files'].items():
        if sha((directory / name).read_bytes()) != digest:
            raise ValueError('Task pack bytes changed.')
    selected = [r for r in p['assignments'] if r['split'] == split]
    ids = [r['id'] for r in selected]
    packets, refs = load(directory / 'inputs.json'), load(directory / 'references.json')
    if [r['id'] for r in packets] != ids or [r['id'] for r in refs] != ids or {d.name for d in (directory / 'raw').iterdir()} != set(ids):
        raise ValueError('Task pack cases changed.')
    if len(m['downloads']) != 3 * len(ids) or {(d['id'], d['name']) for d in m['downloads']} != {(i, n) for i in ids for n in ('metrics.parquet', 'traces.parquet', 'inject_time.txt')}:
        raise ValueError('Task downloads changed.')
    for d in m['downloads']:
        raw = (directory / 'raw' / d['id'] / d['name']).read_bytes()
        actual = sha(raw) if len(d['publisher_hash']) == 64 else hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
        if len(raw) != d['bytes'] or sha(raw) != d['sha256'] or actual != d['publisher_hash']:
            raise ValueError('Task publisher bytes changed.')
    index = {r['case']: r for r in pq.read_table(INDEX).to_pylist()}
    for packet, ref, assignment in zip(packets, refs, selected):
        row = index[assignment['source_case']]
        state, context, delta, actual = reconstruct(directory / 'raw' / assignment['id'], row)
        if packet != {'id': assignment['id'], 'state': state, 'trace_context': context, 'trace_changes': delta, 'requests': {a: actual[a] for a in arms(split)}}:
            raise ValueError('Task input reconstruction failed.')
        if ref != {'id': assignment['id'], 'group': assignment['group'], 'target': row['root_cause_service'], 'fault': row['fault']}:
            raise ValueError('Task reference reconstruction failed.')
        if any(term in json.dumps(packet['requests']) for term in ('re3tt_', 're3ob_', 'source_case', 'root_cause_service', 'operationName', 'methodName', 'traceID', 'spanID', assignment['id'])):
            raise ValueError('Source identity or answer metadata entered task requests.')
    sizes = [sizing(packet, split) for packet in packets]
    if load(directory / 'sizing.json') != sizes or m['largest_request_bytes'] != max(v for r in sizes for v in r['request_bytes'].values()) or m['fits_empirical_wire_cap'] != all(v <= p['maximum_request_bytes'] for r in sizes for v in r['request_bytes'].values()):
        raise ValueError('Task sizing changed.')
    return m
