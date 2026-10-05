"""Verify fourteen evidence stages, failed sizing and dependent bindings, without calls."""
import json
from triage_bench.paths import ROOT
from triage_bench.public_data import sha
from triage_bench.public_rca_stages import load, committed
from triage_bench.public_note_data import validate as sizing_data, PLAN as FIRST_PLAN, DATA as FIRST_DATA
from triage_bench.public_note_v2_data import DATA, validate
from triage_bench.public_note_v2_trial import protocol_path, verified_rows
from triage_bench.public_note_audit import RESULT, audit
from scripts.verify_public_fresh_claims import verify as previous, protected_absence


def verify():
    previous()
    first = sizing_data(); committed(ROOT / 'checkpoints/public-note-sizing-2026-10-05.json')
    failure = load(ROOT / 'checkpoints/public-note-sizing-2026-10-05.json')
    if failure != {'schema':'public-note-sizing-1','status':'pre_inference_wire_cap',
        'plan_sha256':sha(FIRST_PLAN.read_bytes()),'manifest_sha256':sha((FIRST_DATA/'manifest.json').read_bytes()),
        'largest_request_bytes':113081,'maximum_request_bytes':79840,'actual_calls':0,'protocol_created':False,
        'reason':'The frozen request planner rejected the over-cap body before creating an executable protocol.'} or first['fits_request_cap']:
        raise ValueError('Preserved pre-inference sizing failure changed.')
    if any((ROOT / ('checkpoints/public-note-' + phase + '-protocol-2026-10-05.json')).exists() or
           (ROOT / ('runs/public-note-extraction/' + phase + '-hosted-2026-10-05-v1')).exists() for phase in ('extraction','verdict')):
        raise ValueError('Over-cap version must have no hosted execution.')
    validate(); rows, summary = verified_rows('extraction')
    committed(RESULT); result = audit()
    if result != load(RESULT):
        raise ValueError('Blocked extraction audit changed.')
    if len(rows) != 27 or summary['failed'] != 2 or sum(len(r.get('answers', {})) for r in rows if r['status']=='ok') != 1800:
        raise ValueError('Extraction success/failure denominators changed.')
    if any(len(r['raw_response']['answers']) != 72 for r in rows):
        raise ValueError('Raw response question coverage changed.')
    if len(result['rejected_answers']) != 2 or protocol_path('verdict').exists():
        raise ValueError('Dependent phase must remain unexecuted.')
    return {'status':'verified_blocked_diagnostic','recorded_calls':27,'raw_answers':1944,'normalized_answers':1800,
            'valid_calls':25,'rejected_calls':2,'verdict_calls':0,'reports':9,'sentence_candidates':108,
            'routable_claims':54,'atomic_assertions':81,'pre_inference_sizing_calls':0,'new_recordings_opened':0,
            'protected_unopened':protected_absence(),'new_hosted_calls':0}


if __name__ == '__main__': print(json.dumps(verify(), indent=2))
