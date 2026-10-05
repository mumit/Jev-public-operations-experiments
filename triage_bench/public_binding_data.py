"""Reuse frozen reports and references without selecting new claims."""
import json,copy
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_binding_features import FIELDS,ARMS,request
from .hosted import encoded
BASE=ROOT/'runs/public-claim-binding'
DATA=BASE/'diagnostic-data-2026-10-05-v1'
PLAN=ROOT/'checkpoints/public-claim-binding-plan-2026-10-05.json'
SOURCE=ROOT/'runs/public-report-reading/diagnostic-data-2026-10-05-v1/inputs.json'
REFSOURCE=SOURCE.with_name('references.json')

def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='public-claim-binding-plan-1' or p['maximum_calls']!=672:raise ValueError('Binding plan identity.')
    for mapping in ('source_sha256','evidence_sha256'):
        for n,d in p[mapping].items():
            if sha((ROOT/n).read_bytes())!=d:raise ValueError('Binding prerequisite drift.')
    return p

def reconstruct():
    check_plan();packets=[]
    for source in load(SOURCE):
        packet={k:copy.deepcopy(v) for k,v in source.items() if k!='requests'}
        packet['requests']={a:request(source,a) for a in ('lookup','bound')}
        packet['claim_requests']={f:{a:request(source,a,f) for a in ('single','scoped')} for f in FIELDS}
        packets.append(packet)
    refs=load(REFSOURCE)
    if len(packets)!=16 or len({p['case_id'] for p in packets})!=16:raise ValueError('Binding allocation drift.')
    return packets,refs

def bodies(packet):
    return list(packet['requests'].values())+[b for per in packet['claim_requests'].values() for b in per.values()]

def prepare():
    p=check_plan();packets,refs=reconstruct();largest=max(len(encoded(b)) for c in packets for b in bodies(c))
    if largest>p['maximum_request_bytes']:raise ValueError('Binding size failure before calls.')
    DATA.mkdir(parents=True)
    for n,v in [('inputs.json',packets),('references.json',refs)]:
        with (DATA/n).open('x') as s:s.write(json.dumps(v,indent=2)+'\n')
    m={'schema':'public-claim-binding-data-1','reports':16,'claims':96,'service_cards':32,'recordings':16,'largest_request_bytes':largest,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    with (DATA/'manifest.json').open('x') as s:s.write(json.dumps(m,indent=2)+'\n')
    return m

def validate():
    p=check_plan();m=load(DATA/'manifest.json');packets,refs=reconstruct()
    if m['schema']!='public-claim-binding-data-1' or m['plan_sha256']!=sha(PLAN.read_bytes()) or (m['reports'],m['claims'],m['service_cards'],m['recordings'])!=(16,96,32,16) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Binding manifest drift.')
    for n,d in m['files'].items():
        if sha((DATA/n).read_bytes())!=d:raise ValueError('Binding evidence drift.')
    if load(DATA/'inputs.json')!=packets or load(DATA/'references.json')!=refs:raise ValueError('Binding reconstruction drift.')
    largest=max(len(encoded(b)) for c in packets for b in bodies(c))
    if m['largest_request_bytes']!=largest or largest>p['maximum_request_bytes']:raise ValueError('Binding size drift.')
    return m
