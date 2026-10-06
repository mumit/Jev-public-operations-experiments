"""Verify twenty-one completed studies and separate subject and verdict composition without inference."""
import json
from triage_bench.public_rca_stages import load, committed
from triage_bench.separate_subject_trial import RESULT, score
from scripts.verify_subject_check import verify as previous
from scripts.verify_public_fresh_claims import protected_absence

def verify():
    previous();committed(RESULT);r=score()
    if r!=load(RESULT):raise ValueError('Separate-subject assessment changed.')
    if r['calls']!=486 or r['raw_answers']!=3888 or r['new_recordings']!=0 or r['human_reviews']!=0 or r['independent_reviews']!=0:raise ValueError('Separate-subject budget/provenance changed.')
    return {'status':'verified','recorded_calls':r['calls'],'raw_answers':r['raw_answers'],'valid_answers':r['valid_answers'],'human_reviews':0,'independent_reviews':0,'candidate_passes':r['candidate_passes'],'protected_unopened':protected_absence(),'new_hosted_calls':0}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
