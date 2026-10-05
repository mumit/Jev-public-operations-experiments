"""Verify fifteen historical stages and sentence-review results without inference."""
import json
from triage_bench.paths import ROOT
from triage_bench.public_rca_stages import load, committed
from triage_bench.public_note_v2_data import DATA
from triage_bench.public_note_v2_trial import requests as old_requests
from triage_bench.public_sentence_trial import PLAN, RESULT, check_plan, score, verified_rows, requests, protocol_path
from scripts.verify_public_notes import verify as previous
from scripts.verify_public_fresh_claims import protected_absence


def verify():
    previous(); check_plan(); committed(RESULT)
    if score() != load(RESULT):
        raise ValueError('Sentence-review assessment changed.')
    old = old_requests('extraction'); current = requests('extraction')
    if [(r['card_id'], r['round'], r['body'], r['request_sha256']) for r in current] != [(r['card_id'], r['round'], r['body'], r['request_sha256']) for r in old]:
        raise ValueError('The extraction replay changed historical request bodies.')
    erows, es = verified_rows('extraction', complete=True)
    vrows, vs = verified_rows('verdict', complete=True)
    if len(erows) != 27 or len(vrows) != 81:
        # Answer counts are carried by exact phase protocols, not invented replies.
        raise ValueError('Sentence-review job budget changed.')
    result = load(RESULT)
    if load(protocol_path('extraction'))['planned_answers'] != 1944 or result['actual_calls'] > 108 or result['raw_answers'] > 2916:
        raise ValueError('Sentence-review call or answer cap changed.')
    return {'status': 'verified', 'recorded_calls': result['actual_calls'],
        'raw_answers': result['raw_answers'], 'normalized_answers': result['normalized_answers'],
        'quarantined_sentences': result['quarantined_sentences'], 'reports': 9,
        'sentence_candidates': 108, 'routable_claims': 54, 'atomic_assertions': 81,
        'research_gate': result['research_gate'], 'new_recordings_opened': 0,
        'protected_unopened': protected_absence(), 'new_hosted_calls': 0}


if __name__ == '__main__': print(json.dumps(verify(), indent=2))
