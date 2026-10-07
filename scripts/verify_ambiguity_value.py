"""Replay preserved studies and fresh controlled clarification evidence without inference."""
import json
from scripts.verify_optional_question import verify as previous
from triage_bench.ambiguity_value_trial import verify as current
from triage_bench.entry_walkthrough import verify as walkthrough
from scripts.verify_evidence import verify as original
from scripts.verify_public_diagnostics import verify as diagnostics
from scripts.verify_public_selective import verify as selective
from scripts.verify_public_confirmation import verify as confirmation
from scripts.verify_public_agreement import verify as agreement

def verify():
    # Later language verifiers recurse through traces; explicitly replay earlier
    # independent ranking studies and the frozen walkthrough interface as well.
    for check in (original, diagnostics, selective, confirmation, agreement, walkthrough):
        check()
    p = previous()
    r = current()
    if r['actual_calls'] != 144 or r['valid_answers'] != 864 or r['candidate_passes'] or any(r[k] for k in ('new_recordings', 'human_entries', 'human_reviews', 'independent_reviews')):
        raise ValueError('Fresh clarification provenance, budget or frozen outcome changed.')
    return {'status': 'verified', 'reported_count_scope': 'recent clarification-language studies only', 'recorded_calls': p['recorded_calls'] + r['actual_calls'], 'valid_answers': p['valid_answers'] + r['valid_answers'], 'candidate_passes': False, 'new_recordings': 0, 'human_entries': 0, 'human_reviews': 0, 'independent_reviews': 0, 'original_confirmation_unopened': p['original_confirmation_unopened'], 'protected_unopened': p['protected_unopened'], 'new_hosted_calls': 0}

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
