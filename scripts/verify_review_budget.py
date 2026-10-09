"""Replay the full publisher-text chain without inference or protected access."""
import json
from scripts.verify_report_knowledge import verify as previous
from triage_bench import review_budget_trial as trial

def verify(local=False):
 old=previous(local=local);r=trial.verify(local=local)
 return {'status':'verified','recorded_calls':old['recorded_calls']+r['actual_calls'],'review_budget_calls':r['actual_calls'],
  'valid_review_budget_answers':r['valid_answers'],'candidate_passes':r['candidate_passes'],'source_snapshot_replay':local,
  'new_hosted_calls':0,'new_telemetry_recordings':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
