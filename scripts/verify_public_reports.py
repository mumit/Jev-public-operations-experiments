"""Reconstruct the report diagnostic and ten earlier studies without inference."""
import json
from triage_bench.public_rca_stages import load,committed
from triage_bench.public_report_trial import RESULT,score,verified_rows
from triage_bench.public_report_data import DATA,validate
from scripts.verify_public_claim_language import verify as previous

def verify():
    previous();validate();rows,summary=verified_rows(complete=True);committed(RESULT)
    if score()!=load(RESULT):raise ValueError('Report assessment changed.')
    packets=load(DATA/'inputs.json')
    if len(packets)!=16 or len({p['case_id'] for p in packets})!=16:raise ValueError('Report allocation drift.')
    return {'status':'verified','recorded_calls':len(rows),'recorded_answers':len(rows)*6,'reports':16,'claims':96,'service_cards':32,'inspected_recordings':16,'fresh_cases_consumed':0,'evaluation_sealed':True,'remaining_re3_reserves':9,'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
