"""Verify completed reserve confirmation without inference or downloads."""
import json
from triage_bench.public_confirmation_data import check_plan,validate
from triage_bench.public_confirmation_trial import eligibility,verified_rows,score,RESULTS
from triage_bench.public_rca_stages import load,committed

def verify():
    check_plan();eligibility();validate('confirmation');verified_rows('confirmation',complete=True);committed(RESULTS)
    r=score()
    if r!=load(RESULTS):raise ValueError('Confirmation assessment drift.')
    return {'status':'verified','confirmation_calls':162,'distinct_train_ticket_cases':18,'distinct_sock_shop_cases':36,'new_hosted_calls':0,'remaining_unopened_cases_in_these_panels':0}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
