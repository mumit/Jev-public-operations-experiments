"""Verify all eighteen studies and assistant provenance without inference."""
import json
from triage_bench.public_rca_stages import load, committed
from triage_bench.assistant_review_trial import RESULT, score, check_reviews
from scripts.verify_public_note_language import verify as previous
from scripts.verify_public_fresh_claims import protected_absence


def verify():
    previous(); committed(RESULT); result=score()
    if result!=load(RESULT):raise ValueError('Assistant-review assessment changed.')
    packets,records=check_reviews()
    if result['calls']!=162 or result['raw_answers']!=972 or result['human_reviews']!=0 or result['independent_reviews']!=0 or result['new_recordings']!=0:
        raise ValueError('Assistant-review budget or provenance changed.')
    if sum(len(r['sentences']) for r in records)!=324 or sum(r['confirmed'] for r in result['audit']['notes'])!=162:
        raise ValueError('Assistant-review denominators changed.')
    return {'status':'verified','recorded_calls':result['calls'],'raw_answers':result['raw_answers'],'valid_answers':result['valid_answers'],
        'human_reviews':0,'independent_reviews':0,'notes':len(packets),'candidate_passes':result['candidate_passes'],
        'protected_unopened':protected_absence(),'new_hosted_calls':0}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
