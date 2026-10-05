"""Unbalanced proposition requests reusing inspected claims and measurements."""
import copy,json
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_claim_reference import evaluate
from .public_claim_language_features import FORMS,FIELDS,variants,request
from .hosted import encoded
BASE=ROOT/'runs/public-claim-language'
DATA=BASE/'diagnostic-data-2026-10-05-v1'
PLAN=ROOT/'checkpoints/public-claim-language-plan-2026-10-05.json'
SOURCE=ROOT/'runs/public-claim-assessment/diagnostic-data-2026-10-05-v1/inputs.json'
REFSOURCE=SOURCE.with_name('references.json')

def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='public-claim-language-plan-1' or p['maximum_calls']!=456:raise ValueError('Language plan identity.')
    for mapping in ('source_sha256','evidence_sha256'):
        for n,d in p[mapping].items():
            if sha((ROOT/n).read_bytes())!=d:raise ValueError('Language prerequisites changed.')
    return p

def catalogue(source,reference):
    o=source['observation'];out=[('original_'+f,copy.deepcopy(reference['answers'][f]['proposition']),'original_claim') for f in FIELDS]
    seed=sha(source['id'].encode())
    out.append(('counts',{'kind':'span_adequacy','asserted':bool(int(seed[:2],16)%2)},'recorded_counts'))
    zeros=[k for k,v in o['metrics'].items() if v.get('signed_change')==0 and all(isinstance(v.get(n),(int,float)) and 0<=v[n]<=.2 for n in ('before_missing_fraction','after_missing_fraction'))]
    if zeros:
        channel=min(zeros,key=lambda k:sha((seed+'zero'+k).encode()))
        out.append(('zero',{'kind':'metric_direction','channel':channel,'asserted':bool(int(seed[2:4],16)%2)},'measured_zero'))
    return out

def reconstruct():
    check_plan();refs={x['id']:x for x in load(REFSOURCE)};packets=[];references=[]
    for source in load(SOURCE):
        for key,prop,selection in catalogue(source,refs[source['id']]):
            identifier='CLL-'+sha((source['id']+'::'+key).encode())[:12];texts=variants(prop)
            forms=sorted(FORMS,key=lambda f:sha((identifier+'::'+f).encode()))
            form_fields=dict(zip(FORMS,[next(field for field,form in zip(FIELDS,forms) if form==f) for f in FORMS]))
            statements={field:texts[form] for field,form in zip(FIELDS,forms)};reference=evaluate(source['observation'],prop)
            packets.append({'id':identifier,'source_card':source['id'],'case_id':source['case_id'],'dataset':source['dataset'],'selection':selection,
                'observation':copy.deepcopy(source['observation']),'statements':statements,'form_fields':form_fields,
                'requests':{'ledger':request(source['observation'],statements)}})
            references.append({'id':identifier,'answer':reference['answer'],'proposition':prop,'facts':reference['facts'],'reason':reference['reason']})
    if len(packets)!=152 or len({p['source_card'] for p in packets})!=32 or len({p['case_id'] for p in packets})!=16:raise ValueError('Language allocation changed.')
    return packets,references

def prepare():
    p=check_plan();packets,refs=reconstruct();largest=max(len(encoded(c['requests']['ledger'])) for c in packets)
    if largest>p['maximum_request_bytes']:raise ValueError('Request size failure before inference.')
    DATA.mkdir(parents=True)
    for n,v in [('inputs.json',packets),('references.json',refs)]:
        with (DATA/n).open('x') as s:s.write(json.dumps(v,indent=2)+'\n')
    m={'schema':'public-claim-language-data-1','propositions':152,'statements':456,'service_cards':32,'recordings':16,'largest_request_bytes':largest,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    with (DATA/'manifest.json').open('x') as s:s.write(json.dumps(m,indent=2)+'\n')
    return m

def validate():
    check_plan();m=load(DATA/'manifest.json');packets,refs=reconstruct()
    if m['schema']!='public-claim-language-data-1' or m['plan_sha256']!=sha(PLAN.read_bytes()) or (m['propositions'],m['statements'],m['service_cards'],m['recordings'])!=(152,456,32,16) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Language manifest changed.')
    for n,d in m['files'].items():
        if sha((DATA/n).read_bytes())!=d:raise ValueError('Language evidence hash changed.')
    if load(DATA/'inputs.json')!=packets or load(DATA/'references.json')!=refs:raise ValueError('Language reconstruction changed.')
    if m['largest_request_bytes']!=max(len(encoded(p['requests']['ledger'])) for p in packets):raise ValueError('Language sizing changed.')
    return m
