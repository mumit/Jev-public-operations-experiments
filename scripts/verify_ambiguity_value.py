"""Replay preserved studies and fresh controlled clarification evidence without inference."""
import json
from scripts.verify_optional_question import verify as previous
from triage_bench.ambiguity_value_trial import verify as current

def verify():
    p = previous()
    r = current()
    if r['actual_calls'] != 144 or r['valid_answers'] != 864 or r['candidate_passes'] or any(r[k] for k in ('new_recordings', 'human_entries', 'human_reviews', 'independent_reviews')):
        raise ValueError('Fresh clarification provenance, budget or frozen outcome changed.')
    return {'status': 'verified', 'recorded_calls': p['recorded_calls'] + r['actual_calls'], 'valid_answers': p['valid_answers'] + r['valid_answers'], 'candidate_passes': False, 'new_recordings': 0, 'human_entries': 0, 'human_reviews': 0, 'independent_reviews': 0, 'original_confirmation_unopened': p['original_confirmation_unopened'], 'protected_unopened': p['protected_unopened'], 'new_hosted_calls': 0}

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
