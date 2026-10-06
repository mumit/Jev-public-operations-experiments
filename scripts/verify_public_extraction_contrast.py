"""Verify sixteen studies and the separately frozen extraction contrasts, without calls."""
import json
from triage_bench.paths import ROOT
from triage_bench.public_rca_stages import load, committed
from triage_bench.public_note_v2_data import DATA
from triage_bench.public_contrast_features import ARMS, validate_changes
from triage_bench.public_contrast_trial import RESULT, check_plan, score, verified_rows, requests, protocol_path
from scripts.verify_public_sentence_review import verify as previous
from scripts.verify_public_fresh_claims import protected_absence


def verify():
    previous(); check_plan(); committed(RESULT)
    result = score()
    if result != load(RESULT):
        raise ValueError('Extraction-contrast assessment changed.')
    packets = {p['id']: p for p in load(DATA / 'inputs.json')}
    for packet in packets.values(): validate_changes(packet)
    planned = requests('extraction')
    for job in planned:
        if job['arm'] == 'baseline' and job['body'] != packets[job['card_id']]['extraction_request']:
            raise ValueError('Fresh baseline changed the historical body.')
    erows, _ = verified_rows('extraction', complete=True)
    vrows, _ = verified_rows('verdict', complete=True)
    if len(erows) != 108 or len(vrows) != 108 or any(sum(r['arm'] == arm for r in erows) != 27 or sum(r['arm'] == arm for r in vrows) != 27 for arm in ARMS):
        raise ValueError('Contrast arm or job budget changed.')
    if load(protocol_path('extraction'))['planned_answers'] != 7776 or result['actual_calls'] > 216 or result['raw_answers'] > 9072:
        raise ValueError('Contrast call or answer cap changed.')
    return {'status': 'verified', 'recorded_calls': result['actual_calls'],
        'raw_answers': result['raw_answers'], 'normalized_answers': result['normalized_answers'],
        'quarantined_sentences': result['quarantined_sentences'], 'reports': 9, 'inputs': 4,
        'sentence_candidates': 108, 'routable_claims': 54, 'atomic_assertions': 81,
        'candidate': 'combined', 'research_gate': result['research_gate'], 'new_recordings_opened': 0,
        'protected_unopened': protected_absence(), 'new_hosted_calls': 0}


if __name__ == '__main__': print(json.dumps(verify(), indent=2))
