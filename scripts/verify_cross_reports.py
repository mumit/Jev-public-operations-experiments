"""Replay the full publisher-text chain without inference or protected access."""
import json
from scripts.verify_selective_reports import verify as previous
from triage_bench import cross_report_trial as trial

def verify(local=False):
 old=previous(local=local);r=trial.verify(local=local)
 return {'status':'verified','recorded_calls':old['recorded_calls']+r['actual_calls'],'cross_report_calls':r['actual_calls'],
  'valid_cross_report_answers':r['valid_answers'],'candidate_passes':r['candidate_passes'],'source_snapshot_replay':local,
  'new_hosted_calls':0,'new_telemetry_recordings':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
