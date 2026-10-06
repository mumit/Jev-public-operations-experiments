"""Prepare only new prose on already inspected measurements; no downloads."""
from .paths import ROOT
from .public_data import sha
from .public_rca_data import dump
from .public_rca_stages import load, committed
from .public_note_v2_data import DATA as PREVIOUS_DATA, INDEX, validate as previous_validate
from .public_note_language_features import FORMS, compose, extraction_request, validate_changes
from .hosted import encoded

PLAN = ROOT / 'checkpoints/public-note-language-plan-2026-10-05.json'
DATA = ROOT / 'runs/public-note-language/data-2026-10-05-v1'


def check_plan():
    committed(PLAN); p = load(PLAN)
    if (p['schema'], p['maximum_calls'], p['candidate']) != ('public-note-language-plan-1', 324, 'meaning'):
        raise ValueError('Note language plan changed.')
    for mapping in ('source_sha256', 'evidence_sha256'):
        for name, digest in p[mapping].items():
            if sha((ROOT / name).read_bytes()) != digest:
                raise ValueError('Note language producer or prerequisite changed.')
    return p


def reconstruct():
    previous_validate()
    refs = {r['id']: r for r in load(PREVIOUS_DATA / 'references.json')}
    pairs = [compose(p, refs[p['id']], form) for p in load(PREVIOUS_DATA / 'inputs.json') for form in FORMS]
    return [p for p, _ in pairs], [r for _, r in pairs]


def prepare():
    p = check_plan()
    if DATA.exists(): raise ValueError('New note data already exists.')
    packets, references = reconstruct(); DATA.mkdir(parents=True)
    for name, value in [('inputs.json', packets), ('references.json', references)]: dump(DATA / name, value)
    largest = max(len(encoded(extraction_request(q, arm))) for q in packets for arm in ('baseline', 'meaning'))
    m = {'schema': 'public-note-language-data-1', 'plan_sha256': sha(PLAN.read_bytes()), 'reports': 27,
         'source_recordings': 9, 'wordings': list(FORMS), 'candidates': 324, 'actionable_claims': 162,
         'atomic_assertions': 243, 'new_recordings_opened': 0, 'largest_extraction_request_bytes': largest,
         'fits_request_cap': largest <= p['maximum_request_bytes'],
         'files': {n: sha((DATA / n).read_bytes()) for n in ('inputs.json', 'references.json')}}
    dump(DATA / 'manifest.json', m); validate(); return m


def validate():
    p = check_plan(); m = load(DATA / 'manifest.json')
    if m['schema'] != 'public-note-language-data-1' or m['plan_sha256'] != sha(PLAN.read_bytes()) or set(m['files']) != {'inputs.json', 'references.json'}:
        raise ValueError('Language data identity changed.')
    for n, digest in m['files'].items():
        if sha((DATA / n).read_bytes()) != digest: raise ValueError('Language data bytes changed.')
    packets, refs = reconstruct()
    if packets != load(DATA / 'inputs.json') or refs != load(DATA / 'references.json'):
        raise ValueError('Language data reconstruction changed.')
    largest = max(len(encoded(extraction_request(q, arm))) for q in packets for arm in ('baseline', 'meaning'))
    if (m['reports'], m['source_recordings'], m['candidates'], m['actionable_claims'], m['atomic_assertions'], m['new_recordings_opened'], m['largest_extraction_request_bytes'], m['fits_request_cap'], m['wordings']) != (27, 9, 324, 162, 243, 0, largest, largest <= p['maximum_request_bytes'], list(FORMS)):
        raise ValueError('Language denominators or sizing changed.')
    for packet in packets:
        validate_changes(packet)
        for arm in ('baseline', 'meaning'):
            wire = encoded(extraction_request(packet, arm)).decode()
            if any(v in wire for v in ('proposition', 'verdict', 'source_report_id', 'reference', 'parent_note_id', 'source_case', 're3tt_', 're3ob_', packet['source_report_id'], packet['parent_note_id'], packet['id'])):
                raise ValueError('Answer or source identity entered extraction.')
            import json
            if set(json.loads(extraction_request(packet, arm)['state'])) != {'note', 'candidates', 'observed_service_inventory', 'metric_channel_inventory', 'extraction_definitions'}:
                raise ValueError('Unexpected extraction state.')
    return m
