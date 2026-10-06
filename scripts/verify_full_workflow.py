"""Replay twenty-six studies and actual dependent bindings without inference."""
import json
from triage_bench.public_rca_stages import load,committed
from triage_bench.full_workflow_trial import RESULT,score
from scripts.verify_subject_robustness import verify as previous
from scripts.verify_public_fresh_claims import protected_absence

def verify():
    previous();committed(RESULT);r=score()
    if r!=load(RESULT):raise ValueError('Complete workflow assessment changed.')
    if r['actual_calls']>324 or r['raw_answers']>8262 or any(r[k]!=0 for k in ('new_recordings','human_reviews','independent_reviews')):raise ValueError('Workflow budget/provenance changed.')
    return {'status':'verified','recorded_calls':r['actual_calls'],'raw_answers':r['raw_answers'],'valid_answers':r['valid_answers'],'human_reviews':0,'independent_reviews':0,'candidate_passes':r['candidate_passes'],'protected_unopened':protected_absence(),'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
