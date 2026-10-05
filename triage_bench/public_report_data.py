"""Deterministic six-claim reports on already inspected paired service cards."""
import copy,json
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_claim_language_data import catalogue
from .public_claim_reference import evaluate
from .public_report_features import FIELDS,ARMS,text,request
from .hosted import encoded
BASE=ROOT/'runs/public-report-reading'
DATA=BASE/'diagnostic-data-2026-10-05-v1'
PLAN=ROOT/'checkpoints/public-report-reading-plan-2026-10-05.json'
SOURCE=ROOT/'runs/public-claim-assessment/diagnostic-data-2026-10-05-v1/inputs.json'
REFSOURCE=SOURCE.with_name('references.json')

def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='public-report-reading-plan-1' or p['maximum_calls']!=96:raise ValueError('Report plan identity.')
    for mapping in ('source_sha256','evidence_sha256'):
        for n,d in p[mapping].items():
            if sha((ROOT/n).read_bytes())!=d:raise ValueError('Report prerequisite drift.')
    return p

def compose(sources,refs):
    groups={}
    for source in sources:groups.setdefault(source['case_id'],[]).append(source)
    packets=[];references=[]
    for case,group in sorted(groups.items()):
        if len(group)!=2 or len({s['dataset'] for s in group})!=1:raise ValueError('Two same-recording cards required.')
        identifier='RPT-'+sha(case.encode())[:12];selected=[]
        for source in sorted(group,key=lambda s:s['observation']['service']):
            options=catalogue(source,refs[source['id']])
            for key,prop,stratum in sorted(options,key=lambda v:sha((identifier+source['id']+v[0]).encode()))[:3]:
                selected.append({'source_card':source['id'],'service':source['observation']['service'],'proposition':prop,'selection':stratum,'text':text(source['observation'],prop),'reference':evaluate(source['observation'],prop)})
        selected.sort(key=lambda v:sha((identifier+v['source_card']+json.dumps(v['proposition'],sort_keys=True)).encode()))
        observations=[copy.deepcopy(s['observation']) for s in sorted(group,key=lambda s:s['observation']['service'])]
        claims={f:v['text'] for f,v in zip(FIELDS,selected)}
        packets.append({'id':identifier,'case_id':case,'dataset':group[0]['dataset'],'observations':observations,'statements':claims,
            'claim_sources':{f:{k:v[k] for k in ('service','source_card','selection')} for f,v in zip(FIELDS,selected)},
            'requests':{arm:request(observations,claims,arm) for arm in ARMS}})
        references.append({'id':identifier,'answers':{f:{**v['reference'],'proposition':v['proposition'],'service':v['service']} for f,v in zip(FIELDS,selected)}})
    return packets,references

def reconstruct():
    check_plan();packets,refs=compose(load(SOURCE),{r['id']:r for r in load(REFSOURCE)})
    if len(packets)!=16 or len({s['source_card'] for p in packets for s in p['claim_sources'].values()})!=32:raise ValueError('Report allocation drift.')
    return packets,refs

def prepare():
    p=check_plan();packets,refs=reconstruct();largest=max(len(encoded(b)) for c in packets for b in c['requests'].values())
    if largest>p['maximum_request_bytes']:raise ValueError('Report sizing failure before calls.')
    DATA.mkdir(parents=True)
    for n,v in [('inputs.json',packets),('references.json',refs)]:
        with (DATA/n).open('x') as s:s.write(json.dumps(v,indent=2)+'\n')
    m={'schema':'public-report-reading-data-1','reports':16,'claims':96,'service_cards':32,'recordings':16,'largest_request_bytes':largest,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    with (DATA/'manifest.json').open('x') as s:s.write(json.dumps(m,indent=2)+'\n')
    return m

def validate():
    p=check_plan();m=load(DATA/'manifest.json');packets,refs=reconstruct()
    if m['schema']!='public-report-reading-data-1' or m['plan_sha256']!=sha(PLAN.read_bytes()) or (m['reports'],m['claims'],m['service_cards'],m['recordings'])!=(16,96,32,16) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Report manifest drift.')
    for n,d in m['files'].items():
        if sha((DATA/n).read_bytes())!=d:raise ValueError('Report evidence drift.')
    if load(DATA/'inputs.json')!=packets or load(DATA/'references.json')!=refs:raise ValueError('Report reconstruction drift.')
    largest=max(len(encoded(b)) for c in packets for b in c['requests'].values())
    if m['largest_request_bytes']!=largest or largest>p['maximum_request_bytes']:raise ValueError('Report size drift.')
    return m
