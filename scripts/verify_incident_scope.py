"""Replay publisher report and explicit-selection evidence without inference."""
import json
from scripts.verify_publisher_reports import verify as previous
from triage_bench import incident_scope_trial as trial

def verify(local=False):
    old=previous(local=local);result=trial.verify(local=local)
    return {'status':'verified','recorded_calls':old['actual_calls']+result['actual_calls'],'scope_calls':result['actual_calls'],'valid_scope_answers':result['valid_answers'],'candidate_passes':result['candidate_passes'],'source_snapshot_replay':local,'new_hosted_calls':0,'new_telemetry_recordings':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
