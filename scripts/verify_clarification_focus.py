"""Replay thirty-one studies and preserved preparation failures without inference."""
import json
from scripts.verify_clarification import verify as previous
from triage_bench.clarification_focus_trial import verify as current

def verify():
    p=previous();r=current()
    if r['actual_calls']!=456 or r['valid_fields']!=2734 or any(r[k] for k in ('new_recordings','human_reviews','independent_reviews')):raise ValueError('Focused clarification provenance or budget changed.')
    return {'status':'verified','recorded_calls':p['recorded_calls']+r['actual_calls'],'valid_answers':p['valid_answers']+r['valid_fields'],'candidate_passes':r['candidate_passes'],'new_recordings':0,'human_reviews':0,'independent_reviews':0,'original_confirmation_unopened':p['original_confirmation_unopened'],'protected_unopened':p['protected_unopened'],'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
