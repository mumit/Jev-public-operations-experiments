"""Replay twenty-nine studies and preserved preparation failures without inference."""
import json
from scripts.verify_explicit_preparations import verify as previous
from triage_bench.explicit_missing_trial import verify as current

def verify():
    p=previous();r=current()
    if r['actual_calls']!=2160 or r['opportunities']!=2160 or r['reused_recordings']!=15 or r['missing_window_recordings']!=1 or any(r[k] for k in ('new_recordings','human_entries','human_reviews','independent_reviews')):raise ValueError('Missing-window provenance or budget changed.')
    return {'status':'verified','recorded_calls':r['actual_calls'],'valid_answers':r['valid_answers'],'candidate_passes':r['candidate_passes'],'new_recordings':0,'reused_recordings':15,'missing_window_recordings':1,'human_entries':0,'human_reviews':0,'independent_reviews':0,'original_confirmation_unopened':p['original_confirmation_unopened'],'protected_unopened':p['protected_unopened'],'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
