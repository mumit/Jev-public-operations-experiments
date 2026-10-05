"""Balanced authored claims on previously inspected public service observations."""
import json,copy
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_claim_features import ARMS,FIELDS,DURATIONS,request
from .public_claim_reference import evaluate
from .hosted import encoded
BASE=ROOT/'runs/public-claim-assessment'
DATA=BASE/'diagnostic-data-2026-10-05-v1'
PLAN=ROOT/'checkpoints/public-claim-assessment-plan-2026-10-05.json'
SOURCE=ROOT/'runs/public-evidence-assessment/diagnostic-data-2026-10-04-v1/inputs.json'

def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='public-claim-assessment-plan-1' or p['maximum_calls']!=192:raise ValueError('Claim plan identity.')
    for mapping in ('source_sha256','evidence_sha256'):
        for name,digest in p[mapping].items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Frozen claim source changed.')
    return p

def wording(p):
    yes=p['asserted'];kind=p['kind']
    if kind=='metric_material':return f"The {p['channel']} metric {'meets' if yes else 'does not meet'} the material-change policy."
    if kind=='metric_direction':return f"The eligible signed change for {p['channel']} {'is positive' if yes else 'is not positive'}."
    if kind=='duration_material':return f"The {p['measure']} measurement {'meets' if yes else 'does not meet'} the material duration-change policy."
    if kind=='span_adequacy':return f"{'Both windows have' if yes else 'At least one window has fewer than'} five recorded spans{' or more each' if yes else ''}."
    if kind=='causality':return f"This service {'caused' if yes else 'did not cause'} the incident."
    if kind=='health':return f"The supplied evidence establishes that this service {'is healthy' if yes else 'is unhealthy'}."
    raise ValueError('Unknown wording.')

def claims(source):
    o=source['observation'];seed=sha(source['id'].encode());candidates=[]
    for channel in sorted(o['metrics']):
        for kind in ('metric_material','metric_direction'):candidates.append({'kind':kind,'channel':channel,'asserted':True})
    candidates += [{'kind':'duration_material','measure':d,'asserted':True} for d in DURATIONS]
    candidates += [{'kind':'span_adequacy','asserted':True}]
    available=[p for p in candidates if evaluate(o,p)['answer']!='unanswerable']
    choose=lambda p:sha((seed+json.dumps(p,sort_keys=True)).encode())
    base=min(available,key=choose)
    opposite={**base,'asserted':False}
    unknown=[p for p in candidates if evaluate(o,p)['answer']=='unanswerable']
    unknown += [{'kind':'causality','asserted':bool(int(seed[:2],16)%2)},{'kind':'health','asserted':bool(int(seed[2:4],16)%2)}]
    chosen=[base,opposite,min(unknown,key=choose)]
    chosen.sort(key=lambda p:sha((seed+'order'+json.dumps(p,sort_keys=True)).encode()))
    return {field:wording(p) for field,p in zip(FIELDS,chosen)},{field:evaluate(o,p) for field,p in zip(FIELDS,chosen)}

def reconstruct():
    check_plan();packets=[];references=[]
    for source in load(SOURCE):
        statements,refs=claims(source);identifier='CLA-'+sha(source['id'].encode())[:12]
        packets.append({'id':identifier,'source_card':source['id'],'case_id':source['case_id'],'dataset':source['dataset'],
            'observation':copy.deepcopy(source['observation']),'statements':statements,
            'requests':{arm:request(source['observation'],statements,arm) for arm in ARMS}})
        if sorted(r['answer'] for r in refs.values())!=['contradicted','supported','unanswerable']:raise ValueError('Unbalanced claim card.')
        references.append({'id':identifier,'answers':refs})
    if len(packets)!=32 or len({p['case_id'] for p in packets})!=16:raise ValueError('Source allocation changed.')
    return packets,references

def prepare():
    p=check_plan();packets,refs=reconstruct();largest=max(len(encoded(r)) for c in packets for r in c['requests'].values())
    if largest>p['maximum_request_bytes']:raise ValueError('Sizing failure; no inference.')
    DATA.mkdir(parents=True)
    for n,v in [('inputs.json',packets),('references.json',refs)]:
        with (DATA/n).open('x') as s:s.write(json.dumps(v,indent=2)+'\n')
    m={'schema':'public-claim-assessment-data-1','cards':32,'claims':96,'recordings':16,'largest_request_bytes':largest,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    with (DATA/'manifest.json').open('x') as s:s.write(json.dumps(m,indent=2)+'\n')
    return m

def validate():
    check_plan();m=load(DATA/'manifest.json');packets,refs=reconstruct()
    if m['schema']!='public-claim-assessment-data-1' or m['plan_sha256']!=sha(PLAN.read_bytes()) or (m['cards'],m['claims'],m['recordings'])!=(32,96,16) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Claim manifest changed.')
    for n,d in m['files'].items():
        if sha((DATA/n).read_bytes())!=d:raise ValueError('Claim evidence hash changed.')
    if load(DATA/'inputs.json')!=packets or load(DATA/'references.json')!=refs:raise ValueError('Claim reconstruction changed.')
    if m['largest_request_bytes']!=max(len(encoded(r)) for p in packets for r in p['requests'].values()):raise ValueError('Claim sizing changed.')
    return m
