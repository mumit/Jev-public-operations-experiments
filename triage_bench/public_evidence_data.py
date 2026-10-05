"""Prepare a diagnostic from inspected data without accessing untouched panels."""
import json
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_evidence_features import card,request,ARMS
from .public_evidence_reference import reference
from .hosted import encoded

BASE=ROOT/'runs/public-evidence-assessment'
DATA=BASE/'diagnostic-data-2026-10-04-v1'
PLAN=ROOT/'checkpoints/public-evidence-assessment-plan-2026-10-04.json'
SOURCE=ROOT/'runs/public-trace-task/development-data-2026-10-04-v1/inputs.json'


def check_plan():
    committed(PLAN);plan=load(PLAN)
    if plan['schema']!='public-evidence-assessment-plan-1' or plan['maximum_calls']!=192:
        raise ValueError('Evidence plan identity changed.')
    for mapping in ('source_sha256','evidence_sha256'):
        for name,digest in plan[mapping].items():
            if sha((ROOT/name).read_bytes())!=digest:
                raise ValueError('Evidence source or prerequisites changed.')
    return plan


def select(packet):
    services=sorted(json.loads(packet['requests']['metrics']['state'])['services'])
    observations={s:card(packet,s) for s in services}
    strength={}
    for s,o in observations.items():
        # Selection reads observations only. No injected-service reference is loaded.
        metric=[abs(v['signed_change'])/3 for v in o['metrics'].values() if isinstance(v.get('signed_change'),(int,float)) and all(isinstance(v.get(k),(int,float)) and 0<=v[k]<=.2 for k in ('before_missing_fraction','after_missing_fraction'))]
        trace=o['trace'];duration=[]
        if trace is not None and min(trace[w]['spans'] for w in ('before','after'))>=5:
            for key in ('duration_median_us','duration_p90_us','uncovered_duration_median_us','uncovered_duration_p90_us'):
                b,a=trace['before'][key],trace['after'][key]
                if b is not None and a is not None and b>0:duration.append(abs((a-b)/b)/.25)
        strength[s]=max(metric+duration+[0.])
    tie=lambda s:sha((packet['id']+'::'+s).encode())
    strongest=min(services,key=lambda s:(-strength[s],tie(s)))
    remaining=[s for s in services if s!=strongest]
    gaps=[s for s in remaining if observations[s]['trace'] is None]
    other=min(gaps,key=tie) if gaps else min(remaining,key=lambda s:(strength[s],tie(s)))
    return [(strongest,'largest_observed_change'),(other,'coverage_gap' if gaps else 'smallest_observed_change')]


def reconstruct():
    check_plan();assignments={r['id']:r for r in load(ROOT/'checkpoints/public-trace-task-plan-2026-10-04.json')['assignments']}
    packets=[];references=[]
    for source in load(SOURCE):
        row=assignments[source['id']]
        if row['split']!='development':raise ValueError('Only inspected development is authorized.')
        for service,selection in select(source):
            observation=card(source,service);identifier='EVA-'+sha((source['id']+'::'+service).encode())[:12]
            packets.append({'id':identifier,'case_id':source['id'],'dataset':row['dataset'],'selection':selection,'observation':observation,
                            'requests':{arm:request(observation,arm) for arm in ARMS}})
            references.append({'id':identifier,**reference(observation)})
    if len(packets)!=32 or len({r['id'] for r in packets})!=32:raise ValueError('Service card count changed.')
    return packets,references


def prepare():
    plan=check_plan();packets,refs=reconstruct();DATA.mkdir(parents=True)
    largest=max(len(encoded(r)) for p in packets for r in p['requests'].values())
    if largest>plan['maximum_request_bytes']:raise ValueError('Request byte limit; no inference.')
    for name,value in [('inputs.json',packets),('references.json',refs)]:
        with (DATA/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')
    manifest={'schema':'public-evidence-assessment-data-1','cards':32,'recordings':16,'largest_request_bytes':largest,
              'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    with (DATA/'manifest.json').open('x') as stream:stream.write(json.dumps(manifest,indent=2)+'\n')
    return manifest


def validate():
    check_plan();manifest=load(DATA/'manifest.json');packets,refs=reconstruct()
    if manifest['plan_sha256']!=sha(PLAN.read_bytes()) or manifest['cards']!=32 or manifest['recordings']!=16:
        raise ValueError('Evidence data identity changed.')
    for name,digest in manifest['files'].items():
        if sha((DATA/name).read_bytes())!=digest:raise ValueError('Evidence data hash changed.')
    if load(DATA/'inputs.json')!=packets or load(DATA/'references.json')!=refs:
        raise ValueError('Evidence preparation or numerical references changed.')
    if manifest['largest_request_bytes']!=max(len(encoded(r)) for p in packets for r in p['requests'].values()):
        raise ValueError('Sizing changed.')
    return manifest
