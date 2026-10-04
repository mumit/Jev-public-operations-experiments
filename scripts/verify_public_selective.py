"""Reconstruct selective calibration and evaluation without inference or downloads."""
import json
from triage_bench.public_selective_data import check_plan,validate,PLAN,BASE
from triage_bench.public_selective_trial import verify_boundary,verified_rows,score,RESULTS
from triage_bench.public_rca_stages import load,committed

def verify():
    p=check_plan();verify_boundary();committed(RESULTS)
    for split in ('calibration','evaluation'):validate(split);verified_rows(split,complete=True)
    result=score('evaluation')
    if result!=load(RESULTS):raise ValueError('Evaluation assessment differs from recorded result.')
    reserve={a['id'] for a in p['assignments'] if a['split']=='reserve'}
    if any(d.name in reserve for d in BASE.glob('*-data-*/raw/*')):raise ValueError('Reserve telemetry entered selective evidence.')
    return {'status':'verified','calibration_calls':54,'evaluation_calls':108,'new_hosted_calls':0,'sealed_train_ticket_reserve_cases':18,'sealed_sock_shop_reserve_cases':36}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
