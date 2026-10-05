"""Frozen four-step trace/task comparison on fresh development groups."""
import json,time,urllib.request,urllib.error
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed,verify_local
from .public_rca_trial import MODEL,normalize
from .public_rca_models import infer
from .public_trace_task_data import PLAN,BASE,INDEX,COUNTS,arms,folder,partition,check_plan,validate,PREVIOUS
from .public_trace_task_features import ARMS,INSTRUCTION,COLUMNS
from .public_trace_features import trace_ranking
from .public_trace_trial_v2 import SOURCES as PREVIOUS_SOURCES
from .public_selective_policy import evaluate
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import profile_check

SOURCES=tuple(dict.fromkeys(PREVIOUS_SOURCES+('triage_bench/public_trace_task_features.py','triage_bench/public_trace_task_data.py','triage_bench/public_trace_task_trial.py','scripts/run_public_trace_task.py')))
POLICY={'threshold':.7,'margin':0.,'maximum_leads':1}
PRIMARY='trace_deltas'
CANDIDATE=ROOT/'checkpoints/public-trace-task-candidate-2026-10-04.json'
def result_path(split):return ROOT/f'checkpoints/public-trace-task-{split}-results-2026-10-04.json'
def protocol_path(split):return ROOT/f'checkpoints/public-trace-task-{split}-protocol-2026-10-04.json'
def output(split):return BASE/(split+'-hosted-2026-10-04-v1')
def eligibility(split):
    if split=='evaluation':return check_candidate()
    if split!='development':raise ValueError('Unknown task split.')

def freeze_plan(profile):
    profile_check(profile)
    from scripts.verify_public_traces import verify
    verify()
    previous=load(PREVIOUS)
    if PLAN.exists():raise ValueError('Task plan exists.')
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(previous['model'],previous['endpoint'],previous['context_tokens']):raise ValueError('Keep the Jev profile.')
    p={'schema':'public-trace-task-plan-1','decision':'User selected a trace-aware full-candidate Jev task and explicit trace changes on 2026-10-04.',
       'revision':previous['revision'],'index_sha256':previous['index_sha256'],'assignments':partition(previous['assignments']),'counts':COUNTS,'arms':list(ARMS),'evaluation_arms':['traces',PRIMARY],'primary':PRIMARY,'rounds':3,
       'maximum_calls':324,'stage_calls':{'development':192,'evaluation':132},'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':previous['maximum_request_bytes'],'policy':POLICY,
       'question':INSTRUCTION,'change_columns':list(COLUMNS),
       'inputs':'Four ordered controls: original named metrics; identical metrics plus original compact trace context; same trace input with the trace-aware question/insufficient-evidence criterion; same revised question with trace_changes. Every metric value, service candidate and per-service choice criterion remains unchanged. Trace changes use the rounded observations already supplied, signed relative changes, elapsed-window-normalized recorded span rates and a five-spans-per-window flag. No references, learned labels or ML choices enter requests.',
       'allocation':'Reassign only four untouched reserve service/fault groups to development: ten Train Ticket and six Online Boutique cases. Preserve the existing 22-case evaluation panel unchanged. Nine RE3 reserves, RE3 Sock Shop and all 140 RE1 reserves stay unopened. Earlier 13 trace development cases are excluded, not replayed.',
       'controls':'Unchanged fitted Online Boutique metric ML and change/resource rankings; fixed uncovered-duration ranking remains a differently informed transparent control, not fitted ML.',
       'comparisons':'Development isolates added traces, revised task wording and arithmetic changes in sequence. Primary trace_deltas versus original trace wording/input. trace_task is diagnostic and cannot substitute as candidate after seeing results.',
       'promotion':'Require complete successful development. In each application primary must fix at least one distinct original-trace first-choice failure in all three rounds, lose no distinct metric or original-trace success in all three rounds, and in every round have no lower unfiltered correctness, no more displayed wrong leads, no lower displayed correct coverage than either original control, plus nonempty displayed correct guidance. Otherwise evaluation stays sealed. This descriptive research gate is not an operational error budget.',
       'execution':'Three serial rounds with cyclic arm and case order, no retries/warmup, 30s timeout. Commit source/data plan before downloads and exact requests before calls. Stop on HTTP/model-version/network/context errors or three consecutive malformed responses. Failed/missing responses keep denominators. No refitting, threshold search or post-result arm substitution.',
       'limits':'RE3 code faults in familiar applications, supplied incident boundaries, published injected-service references and unknown public pretraining exposure. Development repeats are not independent cases. No operational reliability, analyst benefit, anomaly-detection or telecom readiness claim.',
       'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('checkpoints/public-traces-v2-plan-2026-10-04.json','checkpoints/public-traces-v2-development-results-2026-10-04.json','checkpoints/public-format-protocol-2026-10-03.json')}}
    PLAN.write_text(json.dumps(p,indent=2)+'\n');return {'status':'frozen','maximum_calls':324,'stage_calls':p['stage_calls'],'remaining_re3_reserves':9}

def requests(split):
    validate(split);packets=load(folder(split)/'inputs.json');result=[];available=arms(split)
    for number in (1,2,3):
        offset=number-1
        for i,packet in enumerate(packets[offset:]+packets[:offset]):
            start=(i+offset)%len(available)
            for arm in available[start:]+available[:start]:
                request=packet['requests'][arm];result.append({'id':f"{packet['id']}::{arm}::r{number}",'case_id':packet['id'],'arm':arm,'round':number,'body':request,'request_sha256':sha(encoded(request))})
    return result

def controls(split):
    p=load(ROOT/'checkpoints/public-format-protocol-2026-10-03.json');model=verify_local(ROOT/p['local'],ROOT/p['historical_data'])
    return {r['id']:{**infer(r['state'],model),'trace_duration':trace_ranking(r['trace_context'],r['state']['services'])} for r in load(folder(split)/'inputs.json')}

def freeze_stage(split):
    eligibility(split);p=check_plan();path=protocol_path(split)
    if path.exists():raise ValueError('Task stage protocol exists.')
    m=validate(split)
    if not m['fits_empirical_wire_cap']:raise ValueError('Task requests exceed empirical cap; no calls.')
    r={'schema':'public-trace-task-stage-1','split':split,'maximum_calls':p['stage_calls'][split],'plan_sha256':sha(PLAN.read_bytes()),'manifest_sha256':sha((folder(split)/'manifest.json').read_bytes()),'requests':[{k:v for k,v in r.items() if k!='body'} for r in requests(split)]}
    path.write_text(json.dumps(r,indent=2)+'\n');return {'status':'frozen','maximum_calls':r['maximum_calls']}

def check_stage(split):
    p=check_plan();path=protocol_path(split);committed(path);s=load(path);planned=requests(split)
    if s['schema']!='public-trace-task-stage-1' or s['split']!=split or s['maximum_calls']!=p['stage_calls'][split] or s['plan_sha256']!=sha(PLAN.read_bytes()) or s['manifest_sha256']!=sha((folder(split)/'manifest.json').read_bytes()) or len(planned)!=p['stage_calls'][split]:raise ValueError('Task stage identity drift.')
    if s['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned] or any(len(encoded(r['body']))>p['maximum_request_bytes'] for r in planned):raise ValueError('Task request drift.')
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
                if not isinstance(raw,dict) or raw.get('model')!=MODEL:reason='checkpoint_mismatch';raise ValueError('Unexpected model version.')
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
            print(f"Trace task {split} {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-trace-task-hosted-1','split':split,'planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),
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
        if row['status']=='ok' and (row['raw_response'].get('model')!=MODEL or normalize(row['raw_response'],request['body']['questions']['cause']['criteria'])!=(row['choice'],row['probabilities'],row['provider_confidence']) or row['usage']!=row['raw_response']['usage'] or not 0<row['usage']['input_tokens']<=p['context_tokens']):raise ValueError('Response normalization drift.')
    failed=sum(r['status']!='ok' for r in rows);status='completed' if len(rows)==len(planned) and not failed else 'incomplete_or_failed'
    if (s['planned'],s['attempted'],s['failed'],s['unattempted'],s['status'])!=(len(planned),len(rows),failed,len(planned)-len(rows),status):raise ValueError('Denominator drift.')
    if complete and (status!='completed' or s['stopped_reason']):raise ValueError('Complete successful stage required.')
    return rows,s


def paired(rows,refs,baseline,candidate):
    indexed={(r['case_id'],r['arm'],r['round']):r for r in rows};pairs=[]
    for ref in refs:
        for n in (1,2,3):
            a=indexed.get((ref['id'],baseline,n));b=indexed.get((ref['id'],candidate,n))
            ac=bool(a and a['status']=='ok' and a['choice']==ref['target']);bc=bool(b and b['status']=='ok' and b['choice']==ref['target'])
            pairs.append({'id':ref['id'],'round':n,'target':ref['target'],'fault':ref['fault'],'baseline_correct':ac,'candidate_correct':bc,'fix':bc and not ac,'regression':ac and not bc})
    return {'baseline':baseline,'candidate':candidate,'pairs':pairs,'stable_fixes':[r['id'] for r in refs if all(p['fix'] for p in pairs if p['id']==r['id'])],'stable_regressions':[r['id'] for r in refs if all(p['regression'] for p in pairs if p['id']==r['id'])]}

def gate(results,comparisons):
    primary=results[PRIMARY]
    if not comparisons['traces__trace_deltas']['stable_fixes']:return False
    for control in ('metrics','traces'):
        if control not in results:continue
        if comparisons[control+'__trace_deltas']['stable_regressions']:return False
        if any(y['correct_first']<x['correct_first'] for x,y in zip(results[control]['unfiltered']['per_round'],primary['unfiltered']['per_round'])):return False
        if any(y['wrong_leads']>x['wrong_leads'] or y['correct_first']<x['correct_first'] or not y['correct_first'] for x,y in zip(results[control]['selective']['per_round'],primary['selective']['per_round'])):return False
    return True

def score(split):
    rows,s=verified_rows(split);refs=load(folder(split)/'references.json');local=load(output(split)/'controls.json');assignment={a['id']:a for a in check_plan()['assignments']};datasets={}
    for name in ('Train Ticket','Online Boutique'):
        rr=[r for r in refs if assignment[r['id']]['dataset']==name];ids={r['id'] for r in rr};results={}
        for arm in arms(split):
            actual=[r for r in rows if r['arm']==arm and r['case_id'] in ids]
            results[arm]={'selective':evaluate(actual,rr,POLICY),'unfiltered':evaluate(actual,rr,{'threshold':0.,'margin':0.,'maximum_leads':1})}
        comparisons={a+'__'+b:paired(rows,rr,a,b) for a,b in (('metrics','traces'),('traces','trace_task'),('trace_task',PRIMARY),('metrics',PRIMARY),('traces',PRIMARY)) if a in results and b in results}
        baseline={arm:{'cases':len(rr),'correct_first':sum(local[r['id']][arm]['choice']==r['target'] for r in rr)} for arm in ('ml','change','resource','trace_duration')}
        datasets[name]={'cases':len(rr),'groups':len({r['group'] for r in rr}),'arms':results,'comparisons':comparisons,'promotion_gate':gate(results,comparisons),'controls':baseline}
    return {'schema':'public-trace-task-assessment-1','split':split,'planned_calls':check_plan()['stage_calls'][split],'failed_or_missing':s['failed']+s['unattempted'],'policy':POLICY,'primary':PRIMARY,'datasets':datasets,
        'promotion_gate':not(s['failed']+s['unattempted']) and all(p['promotion_gate'] for p in datasets.values()),'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(protocol_path(split).read_bytes()),'summary_sha256':sha((output(split)/'summary.json').read_bytes())}}

def check_candidate():
    committed(CANDIDATE);c=load(CANDIDATE);path=result_path('development');committed(path);verified_rows('development',complete=True);a=score('development')
    if not a['promotion_gate'] or a!=load(path) or c!={'schema':'public-trace-task-candidate-1','arm':PRIMARY,'plan_sha256':sha(PLAN.read_bytes()),'development_sha256':sha(path.read_bytes()),'policy':POLICY}:raise ValueError('Task development failed promotion; evaluation stays sealed.')
    return c

def promote():
    if CANDIDATE.exists():raise ValueError('Task candidate exists.')
    path=result_path('development');committed(path);verified_rows('development',complete=True);a=score('development')
    if a!=load(path) or not a['promotion_gate']:raise ValueError('Task development failed promotion; evaluation stays sealed.')
    c={'schema':'public-trace-task-candidate-1','arm':PRIMARY,'plan_sha256':sha(PLAN.read_bytes()),'development_sha256':sha(path.read_bytes()),'policy':POLICY}
    CANDIDATE.write_text(json.dumps(c,indent=2)+'\n');return c
