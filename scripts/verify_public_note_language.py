"""Verify seventeen stages and new controlled wording, without inference."""
import json
from triage_bench.public_rca_stages import load, committed
from triage_bench.public_note_language_data import DATA, validate
from triage_bench.public_note_language_features import FORMS, ARMS, validate_changes
from triage_bench.public_note_language_trial import RESULT, check_plan, score, verified_rows, protocol_path
from scripts.verify_public_extraction_contrast import verify as previous
from scripts.verify_public_fresh_claims import protected_absence


def verify():
    previous(); check_plan(); validate(); committed(RESULT)
    result = score()
    if result != load(RESULT): raise ValueError('New wording assessment changed.')
    packets = load(DATA / 'inputs.json')
    if len(packets) != 27 or len({p['parent_note_id'] for p in packets}) != 9:
        raise ValueError('Wording or recording count changed.')
    for form in FORMS:
        if sum(p['wording'] == form for p in packets) != 9: raise ValueError('Missing wording stratum.')
    for p in packets: validate_changes(p)
    erows,_=verified_rows('extraction',complete=True); vrows,_=verified_rows('verdict',complete=True)
    if len(erows)!=162 or len(vrows)!=162 or any(sum(r['arm']==a for r in erows)!=81 or sum(r['arm']==a for r in vrows)!=81 for a in ARMS):
        raise ValueError('New wording jobs changed.')
    if load(protocol_path('extraction'))['planned_answers']!=11664 or result['actual_calls']>324 or result['raw_answers']>13608:
        raise ValueError('New wording budget changed.')
    return {'status':'verified','recorded_calls':result['actual_calls'],'raw_answers':result['raw_answers'],
        'normalized_answers':result['normalized_answers'],'quarantined_sentences':result['quarantined_sentences'],
        'reports':27,'source_recordings':9,'wordings':list(FORMS),'candidate':'meaning',
        'research_gate':result['research_gate'],'new_recordings_opened':0,
        'protected_unopened':protected_absence(),'new_hosted_calls':0}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
