"""Frozen fresh-collection test of Jev/ML disagreement; no fitting or threshold search."""
import json,time,urllib.request,urllib.error
from pathlib import Path
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed,verify_local
from .public_rca_trial import MODEL,normalize,SOURCES as OLD_SOURCES
from .public_rca_models import infer
from .public_agreement_policy import POLICY,assess
from .public_agreement_data import PLAN,INDEX,BASE,COUNTS,folder,check_plan,validate,partition
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import profile_check

RESULTS=ROOT/'checkpoints/public-agreement-results-2026-10-04.json'
SOURCES=tuple(dict.fromkeys(OLD_SOURCES+('triage_bench/public_agreement_data.py','triage_bench/public_agreement_policy.py','triage_bench/public_agreement_trial.py','scripts/run_public_agreement.py','triage_bench/public_selective_policy.py','triage_bench/public_format_data.py','triage_bench/public_format_trial.py','uv.lock')))

def eligibility():
    from scripts.verify_public_confirmation import verify
    return verify()

def protocol_path(split='evaluation'):return ROOT/'checkpoints/public-agreement-protocol-2026-10-04.json'
def output(split='evaluation'):return BASE/'evaluation-hosted-2026-10-04-v1'

def freeze_plan(profile):
    import pyarrow.parquet as pq
    profile_check(profile);eligibility()
    if PLAN.exists():raise ValueError('Agreement plan exists.')
    audit_plan=ROOT/'checkpoints/public-agreement-audit-plan-2026-10-04.json';audit_result=ROOT/'checkpoints/public-agreement-audit-results-2026-10-04.json'
    committed(audit_plan);committed(audit_result);audit=load(audit_result)
    if len(audit['profiles'])!=10 or any(not r['unique_sorted_times'] or not set(r['metric_suffixes'])<={'cpu','mem','diskio','socket','workload','error','latency-50','latency-90'} for r in audit['profiles']):raise ValueError('RE1 schema is incompatible.')
    previous=load(ROOT/'checkpoints/public-confirmation-plan-2026-10-04.json')
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(previous['model'],previous['endpoint'],previous['context_tokens']):raise ValueError('Keep the Jev profile.')
    histories=('public-data','public-rca','public-format','public-temporal','public-selective','public-confirmation','public-agreement')
    hashes=sorted({sha(p.read_bytes()) for name in histories for p in (ROOT/'runs'/name).rglob('metrics.parquet')})
    assignments=partition(pq.read_table(INDEX).to_pylist(),load(audit_plan)['cases'])
    p={'schema':'public-agreement-plan-1','decision':'User selected Jev/ML disagreement as an analyst-review trigger on 2026-10-04.',
       'counts':COUNTS,'dataset_counts':{'Train Ticket':50,'Sock Shop':50},'reserved_cases':{'Train Ticket':70,'Sock Shop':70},'assignments':assignments,'revision':previous['revision'],'index_sha256':previous['index_sha256'],
       'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':previous['maximum_request_bytes'],'maximum_calls':300,'rounds':3,'policy':POLICY,
       'input':'Unchanged named metric summaries and originating-service question. Retain all observed services and source metric names. Missing diskio/socket features remain unavailable, not observed zero. All before/after rows use the supplied injection boundary.',
       'route':'Apply the frozen 0.70 single-lead policy first. An eligible lead is retained when ML agrees. Otherwise mark review required, preserving both model choices for inspection; do not substitute ML. Already withheld cases remain withheld.',
       'selection':'Direct paired evaluation, no development inference, calibration, grid search, refitting, candidate filtering or prompt changes. RE1 groups selected before telemetry using sorted service index minus fault index modulo five in {1,2}; all five repetitions stay together. Audit groups are development only.',
       'reporting':'Each application and round separately: base/retained correct and wrong leads, wrong/correct leads sent to review, review count, base withholding, both-wrong agreements, disagreements with only Jev/ML correct or neither correct, distinct affected cases, per-fault results, repeated display consistency and unchanged ML/change/resource rankings.',
       'research_gate':'Each round starts with a wrong shown lead, routes at least one to review, retains correct coverage and reduces the wrong fraction among retained leads. No base errors means no opportunity to test error reduction. This is descriptive, not a user operational error budget.',
       'execution':'300 serial calls maximum, three rounds with rotated case order, no retries or warmup. Stop on HTTP/version/network/context errors or three consecutive malformed responses. Failed/missing calls withhold and retain their denominator. Commit plan before telemetry, exact request fingerprints before calls.',
       'limits':'New RE1 recordings of familiar applications/faults, not unseen families or new networks. Controlled injected faults and supplied boundaries; public pretraining exposure unknown. Agreement is not a confidence guarantee. No analyst investigation benefit is measured.',
       'historical_metric_sha256':hashes,'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
       'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (audit_plan,audit_result,ROOT/'checkpoints/public-confirmation-results-2026-10-04.json',ROOT/'checkpoints/public-format-protocol-2026-10-03.json')}}
    PLAN.write_text(json.dumps(p,indent=2)+'\n');return {'status':'frozen','maximum_calls':300,'dataset_counts':p['dataset_counts'],'sealed_reserve_cases':140}

def requests(split='evaluation'):
    validate(split);packets=load(folder(split)/'inputs.json');result=[]
    for number in range(1,4):
        offset=number-1
        for packet in packets[offset:]+packets[:offset]:
            result.append({'id':f"{packet['id']}::named::r{number}",'case_id':packet['id'],'arm':'named','round':number,'body':packet['request'],'request_sha256':sha(encoded(packet['request']))})
    return result

def controls(split='evaluation'):
    p=load(ROOT/'checkpoints/public-format-protocol-2026-10-03.json');model=verify_local(ROOT/p['local'],ROOT/p['historical_data'])
    return {r['id']:infer(r['state'],model) for r in load(folder(split)/'inputs.json')}

def freeze_stage(split='evaluation'):
    eligibility();p=check_plan();path=protocol_path()
    if path.exists():raise ValueError('Agreement protocol exists.')
    m=validate(split)
    if not m['fits_empirical_wire_cap']:raise ValueError('Agreement request exceeds empirical cap.')
    r={'schema':'public-agreement-stage-1','split':split,'maximum_calls':300,'plan_sha256':sha(PLAN.read_bytes()),'manifest_sha256':sha((folder(split)/'manifest.json').read_bytes()),
       'requests':[{k:v for k,v in r.items() if k!='body'} for r in requests()]}
    path.write_text(json.dumps(r,indent=2)+'\n');return {'status':'frozen','maximum_calls':300}

def check_stage(split='evaluation'):
    p=check_plan();path=protocol_path();committed(path);s=load(path);planned=requests()
    if s['schema']!='public-agreement-stage-1' or s['split']!=split or s['maximum_calls']!=300 or s['plan_sha256']!=sha(PLAN.read_bytes()) or s['manifest_sha256']!=sha((folder(split)/'manifest.json').read_bytes()):raise ValueError('Agreement stage drift.')
    if s['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned] or any(len(encoded(r['body']))>p['maximum_request_bytes'] for r in planned):raise ValueError('Agreement request drift.')
    return p,s,planned
def run(split,profile):
    p,stage,planned=check_stage(split);profile_check(profile)
    eligibility()
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(p['model'],p['endpoint'],p['context_tokens']):raise ValueError('Profile drift.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('Server-side Jev key required.')
    local=controls(split);destination=output(split);destination.mkdir()
    (destination/'requests.json').write_text(json.dumps(planned,indent=2)+'\n');(destination/'controls.json').write_text(json.dumps(local,indent=2)+'\n')
    rows=[];reason=None;consecutive=0;opener=urllib.request.build_opener(NoRedirect())
    with (destination/'responses.jsonl').open('x') as stream:
        for request in planned:
            row={k:v for k,v in request.items() if k!='body'};row['status']='ok';start=time.perf_counter()
            try:
                wire=urllib.request.Request(profile['endpoint'],data=encoded(request['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(wire,timeout=30) as response:content=response.read(1048577)
                if len(content)>1048576:raise ValueError('Oversized response.')
                raw=json.loads(content);row['raw_response']=redact(raw,key)
                if not isinstance(raw,dict) or raw.get('model')!=MODEL:reason='checkpoint_mismatch'
                row['choice'],row['probabilities'],row['provider_confidence']=normalize(raw,request['body']['questions']['cause']['criteria'])
                count=raw.get('usage',{}).get('input_tokens')
                if isinstance(count,bool) or not isinstance(count,int) or count<1:raise ValueError('Missing token usage.')
                row['usage']=raw['usage']
                if count>p['context_tokens']:reason='reported_context_overflow';raise ValueError('Input exceeds context.')
            except urllib.error.HTTPError as error:row.update(status='error',error='Provider HTTP '+str(error.code));reason='provider_http_'+str(error.code)
            except (OSError,ValueError,KeyError,TypeError) as error:
                row.update(status='error',error='Validation or request failure: '+type(error).__name__)
                if isinstance(error,OSError):reason='network_error'
            row=redact(row,key);row['latency_ms']=(time.perf_counter()-start)*1000;rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            print(f"Agreement {split} {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-agreement-hosted-1','split':split,'planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),
      'unattempted':len(planned)-len(rows),'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed','stopped_reason':reason,
      'protocol_sha256':sha(protocol_path(split).read_bytes()),'files':{name:sha((destination/name).read_bytes()) for name in ('requests.json','responses.jsonl','controls.json')}}
    (destination/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows(split,complete=False):
    p,stage,planned=check_stage(split);destination=output(split);s=load(destination/'summary.json')
    if s['protocol_sha256']!=sha(protocol_path(split).read_bytes()) or s['split']!=split or set(s['files'])!={'requests.json','responses.jsonl','controls.json'}:raise ValueError('Summary drift.')
    for name,digest in s['files'].items():
        if sha((destination/name).read_bytes())!=digest:raise ValueError('Recorded evidence drift.')
    if load(destination/'requests.json')!=planned or load(destination/'controls.json')!=controls(split):raise ValueError('Request or local control drift.')
    rows=[json.loads(line) for line in (destination/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(planned):raise ValueError('Too many calls.')
    for row,request in zip(rows,planned):
        if any(row.get(k)!=v for k,v in request.items() if k!='body') or row['status'] not in {'ok','error'}:raise ValueError('Response identity drift.')
        if row['status']=='ok' and (normalize(row['raw_response'],request['body']['questions']['cause']['criteria'])!=(row['choice'],row['probabilities'],row['provider_confidence']) or row['usage']!=row['raw_response']['usage'] or not 0<row['usage']['input_tokens']<=p['context_tokens']):raise ValueError('Response normalization drift.')
    failed=sum(r['status']!='ok' for r in rows);status='completed' if len(rows)==len(planned) and not failed else 'incomplete_or_failed'
    if (s['planned'],s['attempted'],s['failed'],s['unattempted'],s['status'])!=(len(planned),len(rows),failed,len(planned)-len(rows),status):raise ValueError('Denominator drift.')
    if complete and status!='completed':raise ValueError('Complete successful stage required.')
    return rows,s


def score(split='evaluation'):
    rows,s=verified_rows(split);refs=load(folder(split)/'references.json');assignment={r['id']:r for r in check_plan()['assignments']};local=load(output()/'controls.json');datasets={}
    for name in ('Train Ticket','Sock Shop'):
        rr=[r for r in refs if assignment[r['id']]['dataset']==name];ids={r['id'] for r in rr};actual=[r for r in rows if r['case_id'] in ids]
        result=assess(actual,rr,local)
        baseline={arm:{'cases':len(rr),'correct_first':sum(local[r['id']][arm]['choice']==r['target'] for r in rr),'cause_in_first_three':sum(r['target'] in [x['service'] for x in local[r['id']][arm]['ranking'][:3]] for r in rr)} for arm in ('ml','change','resource')}
        by_fault={f:assess(actual,[r for r in rr if r['fault']==f],local)['per_round'] for f in sorted({r['fault'] for r in rr})}
        datasets[name]={'cases':len(rr),'groups':len({r['group'] for r in rr}),'routing':result,'controls':baseline,'by_fault':by_fault}
    usage={}
    for r in rows:
        for k,v in r.get('usage',{}).items():
            if 'token' in k and isinstance(v,(int,float)) and not isinstance(v,bool):usage[k]=usage.get(k,0)+v
    return {'schema':'public-agreement-assessment-1','cases':100,'planned_calls':300,'failed_or_missing':s['failed']+s['unattempted'],'policy':POLICY,'datasets':datasets,'usage':usage,
       'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(protocol_path().read_bytes()),'summary_sha256':sha((output()/'summary.json').read_bytes())}}
