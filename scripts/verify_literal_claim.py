"""Replay literal-policy and preceding publisher evidence without inference."""
import json
from scripts.verify_incident_scope import verify as previous
from triage_bench import literal_claim_trial as trial
def verify(local=False):
    old=previous(local=local);r=trial.verify(local=local)
    return {'status':'verified','recorded_calls':old['recorded_calls']+r['actual_calls'],'literal_calls':r['actual_calls'],'valid_literal_answers':r['valid_answers'],'candidate_passes':r['candidate_passes'],'source_snapshot_replay':local,'new_hosted_calls':0,'new_telemetry_recordings':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
