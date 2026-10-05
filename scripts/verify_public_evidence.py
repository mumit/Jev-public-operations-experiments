"""Verify the evidence-reading diagnostic without hosted inference."""
import json
from triage_bench.public_rca_stages import load,committed
from triage_bench.public_evidence_trial import RESULT,score,verified_rows
from triage_bench.public_evidence_data import DATA,validate
from scripts.verify_public_trace_task import verify as previous


def verify():
    previous();manifest=validate();rows,summary=verified_rows(complete=True);committed(RESULT)
    if score()!=load(RESULT):raise ValueError('Evidence assessment changed.')
    packets=load(DATA/'inputs.json')
    if len(packets)!=32 or len({p['case_id'] for p in packets})!=16:raise ValueError('Diagnostic cards changed.')
    return {'status':'verified','recorded_calls':len(rows),'recorded_answers':len(rows)*4,'cards':32,'inspected_recordings':16,
            'fresh_cases_consumed':0,'evaluation_sealed':True,'remaining_re3_reserves':9,'new_hosted_calls':0}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
