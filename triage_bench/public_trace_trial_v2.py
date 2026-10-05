"""Paired metric-only/trace-context requests; preserve completed historical producers."""
import json,time,urllib.request,urllib.error
from pathlib import Path
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed,verify_local
from .public_rca_trial import MODEL,normalize,SOURCES as OLD_SOURCES
from .public_rca_models import infer
from .public_trace_data_v2 import PLAN,BASE,INDEX,COUNTS,ARMS,folder,partition,check_plan,validate,verify_audit
from .public_trace_features import trace_ranking
from .public_selective_policy import evaluate
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import profile_check

SOURCES=tuple(dict.fromkeys(OLD_SOURCES+('scripts/audit_public_traces.py','triage_bench/public_trace_wire.py','triage_bench/public_trace_data.py','triage_bench/public_trace_trial.py','scripts/run_public_traces.py','triage_bench/public_trace_features.py','triage_bench/public_trace_data_v2.py','triage_bench/public_trace_trial_v2.py','scripts/run_public_traces_v2.py','triage_bench/public_selective_policy.py','triage_bench/public_format_data.py','triage_bench/public_format_trial.py','uv.lock')))
POLICY={'threshold':.7,'margin':0.,'maximum_leads':1}
CANDIDATE=ROOT/'checkpoints/public-traces-v2-candidate-2026-10-04.json'

def result_path(split):return ROOT/f'checkpoints/public-traces-v2-{split}-results-2026-10-04.json'
def protocol_path(split):return ROOT/f'checkpoints/public-traces-v2-{split}-protocol-2026-10-04.json'
def output(split):return BASE/(split+'-hosted-2026-10-04-v2')

def eligibility(split):
    if split=='evaluation':return check_candidate()
    if split!='development':raise ValueError('Unknown trace stage.')

def freeze_plan(profile):
    import pyarrow.parquet as pq
    profile_check(profile);audit=verify_audit()
    from scripts.verify_public_agreement import verify
    verify()
    if PLAN.exists():raise ValueError('Trace plan exists.')
    if any(not r['microsecond_millis_consistent'] or r['duplicate_span_keys'] or r['missing_trace_or_span_ids'] or not r['trace_before'] or not r['trace_after'] for r in audit['profiles']):raise ValueError('Trace audit failed compatibility checks.')
    previous=load(ROOT/'checkpoints/public-agreement-plan-2026-10-04.json')
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(previous['model'],previous['endpoint'],previous['context_tokens']):raise ValueError('Keep the Jev profile.')
    p={'schema':'public-traces-plan-1','decision':'User authorized richer causal evidence for Jev on 2026-10-04. Compare observed trace context with metric-only on the same RE3 code faults.',
       'revision':previous['revision'],'index_sha256':previous['index_sha256'],'assignments':partition(pq.read_table(INDEX).to_pylist()),'counts':COUNTS,'arms':list(ARMS),'rounds':3,'maximum_calls':210,'stage_calls':{'development':78,'evaluation':132},
       'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':previous['maximum_request_bytes'],'policy':POLICY,
       'inputs':'Preserve named metric summaries, all observed candidates and questions. Trace arm adds exact-matched per-service before/after rows with declared column names, retaining all recorded span counts, inclusive and observed-child-uncovered median/p90 durations in microseconds, raw source status-code counts/missing fractions, observed cross-service parent/child link counts and coverage diagnostics. No source IDs, operation text, fault labels, case paths or reference answers enter requests.',
       'trace_limits':'Parent links are possible dependencies, not proven causes. Uncovered duration includes unobserved work and is not CPU time. Window by span start within metric interval; crossing-window counts remain visible. Missing parent links, status codes and service spans remain unavailable. Exact names only; no answer-based mapping or candidate repair.',
       'controls':'Unchanged fitted Online Boutique metric ML and change/resource rankings. A separately labeled trace-duration ranking uses positive relative growth of median uncovered duration, at least five spans each window, numerical floor one microsecond. It is not fitted ML and has different information from metric-only controls.',
       'promotion':'Before opening any evaluation telemetry, each application must have no first-choice correctness regression in any development round, no increase in wrong displayed leads, no loss of correct displayed coverage, nonempty displayed correct guidance, at least one distinct reference match fixed by traces in all three rounds, and no distinct metric success lost in all three rounds. Otherwise leave evaluation sealed and request the next research decision. This descriptive gate is not an operational error budget.',
       'execution':'Balanced cyclic arm order across cases/rounds, serial, three rounds, no retries or warmup. Commit exact requests before calls. Stop on HTTP/version/network/context errors or three consecutive malformed responses. Missing/failed predictions keep denominators. No prompt/threshold search or ML refitting.',
       'allocation':'Intact source service/fault groups. Development has 7 Train Ticket and 6 Online Boutique cases; evaluation 10/12; reserve 13/12. All RE1 reserves and RE3 Sock Shop remain unopened. Evaluation is not available as development feedback.',
       'limits':'RE3 code faults in familiar applications, supplied boundaries and published injected-service references. Paired input comparison, not an RE1-to-RE3 accuracy gain. Public pretraining exposure unknown; no measured analyst benefit, automatic routing or telecom readiness.',
       'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('checkpoints/public-traces-plan-2026-10-04.json','checkpoints/public-traces-sizing-2026-10-04.json','checkpoints/public-traces-audit-plan-2026-10-04.json','checkpoints/public-traces-audit-results-2026-10-04.json','checkpoints/public-agreement-results-2026-10-04.json','checkpoints/public-format-protocol-2026-10-03.json')}}
    PLAN.write_text(json.dumps(p,indent=2)+'\n');return {'status':'frozen','maximum_calls':210,'stage_calls':p['stage_calls'],'reserved_re3_cases':25}

def requests(split):
    validate(split);packets=load(folder(split)/'inputs.json');result=[]
    for number in range(1,4):
        offset=number-1
        for i,packet in enumerate(packets[offset:]+packets[:offset]):
            arms=ARMS[(i+offset)%2:]+ARMS[:(i+offset)%2]
            for arm in arms:
                request=packet['requests'][arm];result.append({'id':f"{packet['id']}::{arm}::r{number}",'case_id':packet['id'],'arm':arm,'round':number,'body':request,'request_sha256':sha(encoded(request))})
    return result

def controls(split):
    p=load(ROOT/'checkpoints/public-format-protocol-2026-10-03.json');model=verify_local(ROOT/p['local'],ROOT/p['historical_data'])
    return {r['id']:{**infer(r['state'],model),'trace_duration':trace_ranking(r['trace_context'],r['state']['services'])} for r in load(folder(split)/'inputs.json')}

def freeze_stage(split):
    eligibility(split);p=check_plan();path=protocol_path(split)
    if path.exists():raise ValueError('Trace stage protocol exists.')
    m=validate(split)
    if not m['fits_empirical_wire_cap']:raise ValueError('Trace requests exceed unchanged empirical cap; no calls.')
    r={'schema':'public-traces-stage-1','split':split,'maximum_calls':p['stage_calls'][split],'plan_sha256':sha(PLAN.read_bytes()),'manifest_sha256':sha((folder(split)/'manifest.json').read_bytes()),'requests':[{k:v for k,v in r.items() if k!='body'} for r in requests(split)]}
    path.write_text(json.dumps(r,indent=2)+'\n');return {'status':'frozen','maximum_calls':r['maximum_calls']}

def check_stage(split):
    p=check_plan();path=protocol_path(split);committed(path);s=load(path);planned=requests(split)
    if s['schema']!='public-traces-stage-1' or s['split']!=split or s['maximum_calls']!=p['stage_calls'][split] or s['plan_sha256']!=sha(PLAN.read_bytes()) or s['manifest_sha256']!=sha((folder(split)/'manifest.json').read_bytes()) or len(planned)!=p['stage_calls'][split]:raise ValueError('Trace stage identity drift.')
    if s['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned] or any(len(encoded(r['body']))>p['maximum_request_bytes'] for r in planned):raise ValueError('Trace request drift.')
    return p,s,planned
def run(split,profile):
    p,stage,planned=check_stage(split);profile_check(profile)
    eligibility(split)
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
            print(f"Traces {split} {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-traces-hosted-1','split':split,'planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),
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


def score(split):
    rows,s=verified_rows(split);refs=load(folder(split)/'references.json');local=load(output(split)/'controls.json');assignment={a['id']:a for a in check_plan()['assignments']};datasets={}
    for name in ('Train Ticket','Online Boutique'):
        rr=[r for r in refs if assignment[r['id']]['dataset']==name];ids={r['id'] for r in rr};arm_results={}
        for arm in ARMS:
            actual=[r for r in rows if r['arm']==arm and r['case_id'] in ids]
            arm_results[arm]={'selective':evaluate(actual,rr,POLICY),'unfiltered':evaluate(actual,rr,{'threshold':0.,'margin':0.,'maximum_leads':1})}
        indexed={(r['case_id'],r['arm'],r['round']):r for r in rows};pairs=[]
        for ref in rr:
            for n in (1,2,3):
                a=indexed.get((ref['id'],'metrics',n));b=indexed.get((ref['id'],'traces',n));ac=bool(a and a['status']=='ok' and a['choice']==ref['target']);bc=bool(b and b['status']=='ok' and b['choice']==ref['target'])
                pairs.append({'id':ref['id'],'round':n,'target':ref['target'],'fault':ref['fault'],'metrics_correct':ac,'traces_correct':bc,'fix':bc and not ac,'regression':ac and not bc})
        stable_fixes=[r['id'] for r in rr if all(p['fix'] for p in pairs if p['id']==r['id'])];stable_regressions=[r['id'] for r in rr if all(p['regression'] for p in pairs if p['id']==r['id'])]
        a=arm_results['metrics'];b=arm_results['traces'];gate=bool(stable_fixes) and not stable_regressions and all(y['correct_first']>=x['correct_first'] for x,y in zip(a['unfiltered']['per_round'],b['unfiltered']['per_round'])) and all(y['wrong_leads']<=x['wrong_leads'] and y['correct_first']>=x['correct_first'] and y['correct_first']>0 for x,y in zip(a['selective']['per_round'],b['selective']['per_round']))
        baseline={arm:{'cases':len(rr),'correct_first':sum(local[r['id']][arm]['choice']==r['target'] for r in rr)} for arm in ('ml','change','resource','trace_duration')}
        datasets[name]={'cases':len(rr),'groups':len({r['group'] for r in rr}),'arms':arm_results,'pairs':pairs,'stable_fixes':stable_fixes,'stable_regressions':stable_regressions,'promotion_gate':gate,'controls':baseline}
    return {'schema':'public-traces-assessment-1','split':split,'planned_calls':check_plan()['stage_calls'][split],'failed_or_missing':s['failed']+s['unattempted'],'policy':POLICY,'datasets':datasets,
        'promotion_gate':not(s['failed']+s['unattempted']) and all(p['promotion_gate'] for p in datasets.values()),'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(protocol_path(split).read_bytes()),'summary_sha256':sha((output(split)/'summary.json').read_bytes())}}

def check_candidate():
    committed(CANDIDATE);c=load(CANDIDATE);path=result_path('development');committed(path);verified_rows('development',complete=True);a=score('development')
    if not a['promotion_gate'] or a!=load(path) or c!={'schema':'public-traces-candidate-1','arm':'traces','plan_sha256':sha(PLAN.read_bytes()),'development_sha256':sha(path.read_bytes()),'policy':POLICY}:raise ValueError('Trace development failed promotion; evaluation stays sealed.')
    return c

def promote():
    if CANDIDATE.exists():raise ValueError('Trace candidate exists.')
    path=result_path('development');committed(path);verified_rows('development',complete=True);a=score('development')
    if a!=load(path) or not a['promotion_gate']:raise ValueError('Trace development failed promotion; evaluation stays sealed.')
    c={'schema':'public-traces-candidate-1','arm':'traces','plan_sha256':sha(PLAN.read_bytes()),'development_sha256':sha(path.read_bytes()),'policy':POLICY}
    CANDIDATE.write_text(json.dumps(c,indent=2)+'\n');return c
