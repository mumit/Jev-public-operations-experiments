"""Replay twenty-seven stages, preserving unopened explicit confirmation."""
import json
from triage_bench.explicit_claim_trial import verify as current,PLAN,data
from triage_bench.public_rca_stages import load
from triage_bench.public_data import sha
from scripts.verify_full_workflow import verify as previous
from scripts.verify_public_fresh_claims import protected_absence

def verify():
    previous();r=current('development')
    if r['actual_calls']!=750 or r['opportunities']!=750 or any(r[k] for k in ('human_entries','human_reviews','independent_reviews')):raise ValueError('Explicit comparison provenance/budget changed.')
    if data.folder('confirmation').exists():raise ValueError('Failed original candidate opened confirmation.')
    names={d.name for d in data.ROOT.glob('runs/**/raw/*')}
    for a in load(PLAN)['assignments']:
        if any(name.endswith(sha(a['source_case'].encode())[:12]) for name in names):raise ValueError('Allocated explicit confirmation already opened.')
    return {'status':'verified','recorded_calls':750,'valid_answers':r['valid_answers'],'candidate_passes':r['passes'],'human_entries':0,'human_reviews':0,'independent_reviews':0,'fresh_confirmation_unopened':15,'protected_unopened':protected_absence(),'new_hosted_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
