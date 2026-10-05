"""Open only the nine explicitly allocated reserves after the new plan commits."""
import hashlib
import json
from .paths import ROOT
from .public_data import REVISION, REPOSITORY, sha, fetch
from .public_rca_data import dump
from .public_rca_stages import load, committed
from .public_trace_task_data import PLAN as OLD_PLAN, reconstruct as telemetry
from .public_trace_data_v2 import INDEX
from .public_fresh_claim_features import compose, bodies
from .hosted import encoded

PLAN = ROOT / 'checkpoints/public-fresh-claims-plan-2026-10-05.json'
DATA = ROOT / 'runs/public-fresh-claims/confirmation-data-2026-10-05-v1'


def allocation():
    rows = [r for r in load(OLD_PLAN)['assignments'] if r['split'] == 'reserve']
    counts = {'RE3-TT/ts-auth-service/f4': 3, 'RE3-OB/emailservice/f4': 3, 'RE3-OB/emailservice/f5': 3}
    if len(rows) != 9 or {g: sum(r['group'] == g for r in rows) for g in {r['group'] for r in rows}} != counts:
        raise ValueError('Fresh grouped allocation changed.')
    return [{**r, 'id': 'FMC-' + sha(r['source_case'].encode())[:12], 'split': 'confirmation'} for r in rows]


def check_plan():
    committed(PLAN)
    p = load(PLAN)
    if (p['schema'], p['maximum_calls'], p['revision']) != ('public-fresh-claims-plan-1', 189, REVISION):
        raise ValueError('Fresh plan identity changed.')
    if p['assignments'] != allocation() or p['index_sha256'] != sha(INDEX.read_bytes()):
        raise ValueError('Fresh allocation/index changed.')
    for mapping in ('source_sha256', 'evidence_sha256'):
        for name, digest in p[mapping].items():
            if sha((ROOT / name).read_bytes()) != digest:
                raise ValueError('Fresh source or prerequisite changed.')
    return p


def reconstruct(directory, assignment, row):
    state, context, changes, requests = telemetry(directory, row)
    source = {'id': assignment['id'], 'state': state, 'trace_context': context,
              'trace_changes': changes, 'requests': {'metrics': requests['metrics']}}
    return compose(source, assignment['dataset'])


def prepare():
    import pyarrow.parquet as pq
    p = check_plan()
    if DATA.exists():
        raise ValueError('Fresh preparation already started; never overwrite.')
    raw_ids = {d.name for d in ROOT.glob('runs/**/raw/*') if d.is_dir()}
    for assignment in p['assignments']:
        aliases = {prefix + sha(assignment['source_case'].encode())[:12] for prefix in ('TRC-', 'TQA-', 'FMC-')}
        if aliases & raw_ids:
            raise ValueError('Allocated fresh recording was already opened.')
    index = {r['case']: r for r in pq.read_table(INDEX).to_pylist()}
    DATA.mkdir(parents=True)
    packets, refs, downloads = [], [], []
    for assignment in p['assignments']:
        source = assignment['source_case']
        directory = DATA / 'raw' / assignment['id']
        directory.mkdir(parents=True)
        entries = {r['path']: r for r in json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source}')) if r['type'] == 'file'}
        for name in ('metrics.parquet', 'traces.parquet', 'inject_time.txt'):
            entry = entries[source + '/' + name]
            if not 0 < entry['size'] <= 50_000_000:
                raise ValueError('Fresh source exceeds frozen size cap.')
            raw = fetch(f'https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{source}/{name}', entry['size'])
            publisher = entry['lfs']['oid'] if 'lfs' in entry else entry['oid']
            actual = sha(raw) if 'lfs' in entry else hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
            if len(raw) != entry['size'] or actual != publisher:
                raise ValueError('Fresh publisher checksum mismatch.')
            (directory / name).write_bytes(raw)
            downloads.append({'id': assignment['id'], 'name': name, 'bytes': len(raw), 'sha256': sha(raw), 'publisher_hash': publisher})
        packet, ref = reconstruct(directory, assignment, index[source])
        packets.append(packet)
        refs.append(ref)
        print(f'Prepared fresh controlled note {len(packets)}/9', flush=True)
    largest = max(len(encoded(b)) for packet in packets for b in bodies(packet))
    for name, value in [('inputs.json', packets), ('references.json', refs)]:
        dump(DATA / name, value)
    manifest = {'schema': 'public-fresh-claims-data-1', 'recordings': 9, 'reports': 9, 'claims': 54,
        'revision': REVISION, 'plan_sha256': sha(PLAN.read_bytes()), 'fresh_absence_check_before_download': True,
        'downloads': downloads, 'largest_request_bytes': largest,
        'fits_request_cap': largest <= p['maximum_request_bytes'],
        'files': {n: sha((DATA / n).read_bytes()) for n in ('inputs.json', 'references.json')}}
    dump(DATA / 'manifest.json', manifest)
    validate()
    return manifest


def validate():
    import pyarrow.parquet as pq
    p = check_plan()
    m = load(DATA / 'manifest.json')
    if (m['schema'], m['recordings'], m['reports'], m['claims'], m['revision'], m['plan_sha256'], m['fresh_absence_check_before_download']) != ('public-fresh-claims-data-1', 9, 9, 54, REVISION, sha(PLAN.read_bytes()), True):
        raise ValueError('Fresh pack identity changed.')
    if set(m['files']) != {'inputs.json', 'references.json'}:
        raise ValueError('Fresh pack file set changed.')
    for name, digest in m['files'].items():
        if sha((DATA / name).read_bytes()) != digest:
            raise ValueError('Fresh prepared evidence changed.')
    expected = {(r['id'], n) for r in p['assignments'] for n in ('metrics.parquet', 'traces.parquet', 'inject_time.txt')}
    if len(m['downloads']) != 27 or {(r['id'], r['name']) for r in m['downloads']} != expected or {d.name for d in (DATA / 'raw').iterdir()} != {r['id'] for r in p['assignments']}:
        raise ValueError('Fresh download coverage changed.')
    for row in m['downloads']:
        raw = (DATA / 'raw' / row['id'] / row['name']).read_bytes()
        publisher = sha(raw) if len(row['publisher_hash']) == 64 else hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
        if len(raw) != row['bytes'] or sha(raw) != row['sha256'] or publisher != row['publisher_hash']:
            raise ValueError('Fresh telemetry bytes changed.')
    index = {r['case']: r for r in pq.read_table(INDEX).to_pylist()}
    pairs = [reconstruct(DATA / 'raw' / a['id'], a, index[a['source_case']]) for a in p['assignments']]
    packets, refs = [r[0] for r in pairs], [r[1] for r in pairs]
    if packets != load(DATA / 'inputs.json') or refs != load(DATA / 'references.json'):
        raise ValueError('Fresh report/reference reconstruction changed.')
    forbidden = ('source_case', 'root_cause_service', 're3tt_', 're3ob_', 'proposition', 'reference', 'publisher_hash')
    for packet in packets:
        for body in bodies(packet):
            wire = encoded(body).decode()
            if any(term in wire for term in forbidden) or packet['case_id'] in wire:
                raise ValueError('Answer or source metadata entered a request.')
        report = json.loads(packet['requests']['bound']['state'])['report']
        for field, span in packet['supplied_bindings'].items():
            if report[span['start']:span['end']] != packet['statements'][field] or span['service'] != packet['claim_sources'][field]['service']:
                raise ValueError('Supplied text/service annotation changed.')
    largest = max(len(encoded(b)) for packet in packets for b in bodies(packet))
    if m['largest_request_bytes'] != largest or m['fits_request_cap'] != (largest <= p['maximum_request_bytes']):
        raise ValueError('Fresh sizing changed.')
    return m
