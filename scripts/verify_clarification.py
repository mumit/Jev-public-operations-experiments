"""Replay thirty studies and preserved preparation failures without inference."""
import json
from scripts.verify_explicit_missing import verify as previous
from triage_bench.clarification_trial import verify as current

def verify():
    p=previous();r=current()
    if r['actual_calls']!=228 or r['valid_fields']!=1368 or any(r[k] for k in ('new_recordings','human_reviews','independent_reviews')):raise ValueError('Clarification provenance or budget changed.')
    return {'status':'verified','recorded_calls':228,'valid_answers':r['valid_fields'],'candidate_passes':r['candidate_passes'],'new_recordings':0,'human_reviews':0,'independent_reviews':0,'original_confirmation_unopened':p['original_confirmation_unopened'],'protected_unopened':p['protected_unopened'],'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
