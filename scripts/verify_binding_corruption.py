"""Verify nineteen frozen stages without inference."""
import json
from triage_bench.public_rca_stages import load, committed
from triage_bench.binding_corruption_trial import RESULT, score
from scripts.verify_assistant_review import verify as previous
from scripts.verify_public_fresh_claims import protected_absence

def verify():
    previous();committed(RESULT);r=score()
    if r!=load(RESULT):raise ValueError('Corruption assessment changed.')
    if r['calls']!=405 or r['raw_answers']!=2430 or r['new_recordings']!=0 or r['human_reviews']!=0 or r['independent_reviews']!=0:raise ValueError('Corruption budget/provenance changed.')
    return {'status':'verified','recorded_calls':r['calls'],'raw_answers':r['raw_answers'],'valid_answers':r['valid_answers'],'human_reviews':0,'independent_reviews':0,'protected_unopened':protected_absence(),'new_hosted_calls':0}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
