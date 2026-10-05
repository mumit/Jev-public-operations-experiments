"""Reconstruct new notes on nine inspected recordings; no downloads or reserve access."""
import json
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load, committed
from .public_rca_data import dump
from .public_fresh_claim_data import DATA as PREVIOUS_DATA, PLAN as PREVIOUS_PLAN, INDEX, validate as previous_validate
from .public_trace_task_data import reconstruct as telemetry
from .public_evidence_features import card
from .public_note_features import compose
from .hosted import encoded

PLAN = ROOT / 'checkpoints/public-note-extraction-plan-2026-10-05.json'
DATA = ROOT / 'runs/public-note-extraction/data-2026-10-05-v1'


def check_plan():
    committed(PLAN)
    p = load(PLAN)
    if (p['schema'], p['maximum_calls']) != ('public-note-extraction-plan-1', 108):
        raise ValueError('Note plan identity changed.')
    for mapping in ('source_sha256', 'evidence_sha256'):
        for name, digest in p[mapping].items():
            if sha((ROOT / name).read_bytes()) != digest:
                raise ValueError('Note producer or prerequisite changed.')
    return p


def reconstruct():
    import pyarrow.parquet as pq
    previous_validate()
    index = {r['case']: r for r in pq.read_table(INDEX).to_pylist()}
    old = {p['case_id']: p for p in load(PREVIOUS_DATA / 'inputs.json')}
    refs = {r['id']: r for r in load(PREVIOUS_DATA / 'references.json')}
    result = []
    for a in load(PREVIOUS_PLAN)['assignments']:
        state, context, changes, requests = telemetry(PREVIOUS_DATA / 'raw' / a['id'], index[a['source_case']])
        source = {'trace_context': context, 'trace_changes': changes, 'requests': {'metrics': requests['metrics']}}
        services = sorted(json.loads(requests['metrics']['state'])['services'])
        observations = [card(source, s) for s in services]
        result.append(compose(old[a['id']], refs[old[a['id']]['id']], observations))
    return [r[0] for r in result], [r[1] for r in result]


def prepare():
    p = check_plan()
    if DATA.exists():
        raise ValueError('Note data already exists.')
    packets, references = reconstruct()
    DATA.mkdir(parents=True)
    for name, value in [('inputs.json', packets), ('references.json', references)]:
        dump(DATA / name, value)
    largest = max(len(encoded(p['extraction_request'])) for p in packets)
    m = {'schema': 'public-note-data-1', 'plan_sha256': sha(PLAN.read_bytes()), 'reports': len(packets),
         'candidates': sum(len(p['candidates']) for p in packets), 'actionable_claims': 54,
         'new_recordings_opened': 0, 'largest_extraction_request_bytes': largest,
         'fits_request_cap': largest <= p['maximum_request_bytes'],
         'files': {n: sha((DATA / n).read_bytes()) for n in ('inputs.json', 'references.json')}}
    dump(DATA / 'manifest.json', m)
    validate()
    return m


def validate():
    p = check_plan(); m = load(DATA / 'manifest.json')
    if m['schema'] != 'public-note-data-1' or m['plan_sha256'] != sha(PLAN.read_bytes()) or set(m['files']) != {'inputs.json', 'references.json'}:
        raise ValueError('Note data identity changed.')
    for n, digest in m['files'].items():
        if sha((DATA / n).read_bytes()) != digest:
            raise ValueError('Note data bytes changed.')
    packets, refs = reconstruct()
    if packets != load(DATA / 'inputs.json') or refs != load(DATA / 'references.json'):
        raise ValueError('Note data reconstruction changed.')
    largest = max(len(encoded(q['extraction_request'])) for q in packets)
    if (m['reports'], m['candidates'], m['actionable_claims'], m['new_recordings_opened'], m['largest_extraction_request_bytes'], m['fits_request_cap']) != (9, 108, 54, 0, largest, largest <= p['maximum_request_bytes']):
        raise ValueError('Note denominators or sizing changed.')
    for packet in packets:
        wire = encoded(packet['extraction_request']).decode()
        if any(s in wire for s in ('proposition', 'verdict', 'source_report_id', 'reference', 'source_case', 're3tt_', 're3ob_')) or packet['source_report_id'] in wire:
            raise ValueError('Gold or source identity entered extraction.')
        state = json.loads(packet['extraction_request']['state'])
        if set(state) != {'note', 'candidates', 'observed_service_inventory', 'metric_channel_inventory'}:
            raise ValueError('Unexpected extraction state.')
    return m
