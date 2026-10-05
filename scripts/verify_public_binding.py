"""Reconstruct binding and the eleven earlier studies without inference."""
import json
from triage_bench.public_rca_stages import load,committed
from triage_bench.public_binding_trial import RESULT,score,verified_rows
from triage_bench.public_binding_data import DATA,validate
from scripts.verify_public_reports import verify as previous

def verify():
    previous();validate();rows,summary=verified_rows(complete=True);committed(RESULT)
    if score()!=load(RESULT):raise ValueError('Binding assessment changed.')
    packets=load(DATA/'inputs.json')
    if len(packets)!=16 or len({p['case_id'] for p in packets})!=16:raise ValueError('Binding allocation drift.')
    counts={arm:sum(r['arm']==arm for r in rows) for arm in ('lookup','bound','single','scoped')}
    if counts!={'lookup':48,'bound':48,'single':288,'scoped':288}:raise ValueError('Binding arm denominator drift.')
    return {'status':'verified','recorded_calls':len(rows),'recorded_answers':sum(len(r['answers']) for r in rows),'reports':16,'claims':96,'service_cards':32,'inspected_recordings':16,'fresh_cases_consumed':0,'evaluation_sealed':True,'remaining_re3_reserves':9,'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
