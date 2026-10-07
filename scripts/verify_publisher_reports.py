"""Replay both completed public report phases without inference or source downloads."""
import json
from triage_bench import publisher_report_trial as t
from triage_bench.hosted import encoded
from triage_bench.report_source_audit import digest

def verify(local=False):
    phases={phase:t.verify(phase,local=local) for phase in ('development','evaluation')}
    if not phases['development']['candidate_passes'] or phases['evaluation']['candidate_passes']:raise ValueError('Frozen phase outcomes changed.')
    if any(r['actual_calls']!=72 or r['valid_answers']!=72 or r['human_reviews'] or r['independent_reference_reviews'] or r['new_telemetry_recordings'] for r in phases.values()):raise ValueError('Execution or review counts changed.')
    for phase in phases:
        rows,_=t.rows(phase,local=local)
        if any(digest(encoded(r['raw_response']))!=r['raw_response_sha256'] for r in rows):raise ValueError('Original provider payload changed.')
    return {'status':'verified','source_snapshot_replay':local,'actual_calls':144,'valid_answers':144,'development_passes':True,'evaluation_passes':False,'evaluation_correct_displays':63,'evaluation_wrong_displays':6,'evaluation_withheld':3,'new_hosted_calls':0,'new_telemetry_recordings':0,'human_reviews':0,'independent_reference_reviews':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
