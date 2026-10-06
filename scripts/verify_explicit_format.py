"""Replay twenty-eight frozen studies without inference."""
import json
from triage_bench.explicit_format_trial import verify as current
from scripts.verify_explicit_claims import verify as previous

def verify():
    p=previous();r=current()
    if r['actual_calls']!=2250 or r['opportunities']!=2250 or any(r[k] for k in ('new_recordings','human_entries','human_reviews','independent_reviews')):raise ValueError('Explicit format provenance/budget changed.')
    return {'status':'verified','recorded_calls':2250,'valid_answers':r['valid_answers'],'candidate_passes':r['candidate_passes'],'new_recordings':0,'human_entries':0,'human_reviews':0,'independent_reviews':0,'fresh_confirmation_unopened':p['fresh_confirmation_unopened'],'protected_unopened':p['protected_unopened'],'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
