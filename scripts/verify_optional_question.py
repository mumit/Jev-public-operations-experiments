"""Replay preserved operations studies without inference."""
import json
from scripts.verify_optional_clarification import verify as previous
from triage_bench.optional_question_trial import verify as current

def verify():
    p=previous();r=current()
    if r['actual_calls']!=276 or r['valid_answers']!=1656 or any(r[k] for k in ('new_recordings','human_entries','human_reviews','independent_reviews')):raise ValueError('Optional provenance or budget changed.')
    return {'status':'verified','recorded_calls':p['recorded_calls']+r['actual_calls'],'valid_answers':p['valid_answers']+r['valid_answers'],'candidate_passes':r['candidate_passes'],'new_recordings':0,'human_entries':0,'human_reviews':0,'independent_reviews':0,'original_confirmation_unopened':p['original_confirmation_unopened'],'protected_unopened':p['protected_unopened'],'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
