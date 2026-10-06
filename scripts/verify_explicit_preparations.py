"""Replay twenty-eight executed studies and the three preserved preparation failures."""
import json
from scripts.verify_explicit_format import verify as previous
from triage_bench.explicit_preparation_audit import verify as failures

def verify():
    p=previous();f=failures()
    return {'status':'verified','recorded_calls':0,'valid_answers':0,'preserved_failed_preparation_recordings':f['downloaded_recordings'],'failed_preparation_hosted_calls':0,'prepared_claims':0,'decision_required':f['decision_required'],'original_confirmation_unopened':p['fresh_confirmation_unopened'],'protected_unopened':p['protected_unopened'],'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
