"""Frozen selective-policy calibration and evaluation on fresh grouped cases."""
import json,time,urllib.request,urllib.error
from pathlib import Path
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed,verify_local
from .public_rca_trial import MODEL,normalize
from .public_rca_models import infer
from .public_selective_data import PLAN,INDEX,BASE,COUNTS,folder,check_plan,validate
from .public_selective_policy import candidates,decision,evaluate,select
from .public_temporal_trial import score as development_score,shortlist
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import profile_check

BOUNDARY=ROOT/'checkpoints/public-selective-boundary-2026-10-04.json'
RESULTS=ROOT/'checkpoints/public-selective-evaluation-2026-10-04.json'
SOURCES=('triage_bench/public_selective_data.py','triage_bench/public_selective_policy.py','triage_bench/public_selective_trial.py','scripts/run_public_selective.py','uv.lock',
 'triage_bench/public_format_trial.py','triage_bench/public_rca_data.py','triage_bench/public_rca_models.py','triage_bench/public_rca_trial.py','triage_bench/public_rca_stages.py',
 'triage_bench/hosted.py','triage_bench/runner.py','triage_bench/profile.py','triage_bench/public_data.py')


def protocol_path(split):return ROOT/f'checkpoints/public-selective-{split}-protocol-2026-10-04.json'
def output(split):return BASE/(split+'-hosted-2026-10-04-v1')


def freeze_plan(profile):
    profile_check(profile)
    if PLAN.exists():raise ValueError('Selection plan already exists.')
    source=ROOT/'checkpoints/public-temporal-preparation-2026-10-04.json';prep=load(source)
    dev=ROOT/'checkpoints/public-temporal-development-results-2026-10-04.json';committed(dev)
    if development_score()!=load(dev):raise ValueError('Development evidence changed.')
    previous=load(ROOT/'checkpoints/public-temporal-development-protocol-2026-10-04.json')
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(previous['model'],previous['endpoint'],previous['context_tokens']):raise ValueError('Keep the existing Jev profile.')
    paths=(source,dev,ROOT/'checkpoints/public-format-protocol-2026-10-03.json',ROOT/'checkpoints/public-context-probe-result-2026-10-04.json')
    p={'schema':'public-selective-plan-1','decision':'User chose fewer wrong leads, accepting more withholding, on 2026-10-04.',
       'revision':prep['revision'],'index_sha256':prep['index_sha256'],'assignments':prep['assignments'],'counts':COUNTS,
       'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':previous['maximum_request_bytes'],
       'maximum_calls':162,'rounds':3,'input':'Unchanged named summaries, question and every observed candidate. No temporal windows, labels or reference paths in requests.',
       'candidate_policies':candidates(),'alternative_rule':'For the diagnostic two-lead comparator, second service probability >=0.20 and >=0.50 of the selected probability. Fixed before calibration; not a causal justification.',
       'selection':'Eligible single-lead policies show at least one recommendation per round with zero observed wrong leads in every calibration round. Maximize minimum correct displays per round, then total correct displays, then distinct-case display stability. Lowest probability threshold then lowest margin break ties. If none qualify, withhold all and stop before evaluation.',
       'margin':'Selected probability minus the largest other option probability, including insufficient_evidence. Threshold and margin comparisons include 1e-9 normalization tolerance.',
       'comparison':'Report unfiltered first choice, original up-to-three shortlist, fixed supported-alternative comparator, calibrated single-or-withhold policy and unchanged ML/change/resource controls separately.',
       'gates':'Commit this plan before calibration download; commit stage request fingerprints before calls. Complete calibration, recompute and commit boundary before evaluation download. Run each stage once. No post-evaluation tuning; both reserve sets remain undownloaded.',
       'execution':'Serial, three case-rotated rounds; no retries or warmup. 30-second timeout. Stop HTTP/network/version/context errors or three malformed responses. Missing slots remain in denominators.',
       'capacity':'Keep full named input under the previously accepted 79,840-byte empirical cap; actual reported input must be <=32,768. No truncation. Sizing failure stops before calls.',
       'limits':'Author-set research rule, not an operational error budget. One injected cause per case; alternatives necessarily add benchmark wrong leads. Three rounds are not independent test cases; six calibration and twelve evaluation groups. No verified analyst investigation benefit.',
       'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}}
    PLAN.write_text(json.dumps(p,indent=2)+'\n');return {'status':'frozen','maximum_calls':162,'calibration_cases':18,'evaluation_cases':36}


def requests(split):
    validate(split);packets=load(folder(split)/'inputs.json');planned=[]
    for number in range(1,4):
        offset=number-1
        for packet in packets[offset:]+packets[:offset]:
            request=packet['request'];planned.append({'id':f"{packet['id']}::named::r{number}",'case_id':packet['id'],'arm':'named','round':number,
                'body':request,'request_sha256':sha(encoded(request))})
    return planned


def controls(split):
    p=load(ROOT/'checkpoints/public-format-protocol-2026-10-03.json');model=verify_local(ROOT/p['local'],ROOT/p['historical_data'])
    return {r['id']:infer(r['state'],model) for r in load(folder(split)/'inputs.json')}


def freeze_stage(split):
    p=check_plan();path=protocol_path(split)
    if path.exists():raise ValueError('Stage protocol already exists.')
    if split=='evaluation':verify_boundary()
    m=validate(split)
    if not m['fits_empirical_wire_cap']:raise ValueError('Request sizing exceeds empirical cap; no calls.')
    planned=requests(split)
    r={'schema':'public-selective-stage-1','split':split,'plan_sha256':sha(PLAN.read_bytes()),'manifest_sha256':sha((folder(split)/'manifest.json').read_bytes()),
       'maximum_calls':COUNTS[split]*3,'requests':[{k:v for k,v in r.items() if k!='body'} for r in planned],
       'boundary_sha256':sha(BOUNDARY.read_bytes()) if split=='evaluation' else None}
    path.write_text(json.dumps(r,indent=2)+'\n');return {'status':'frozen','split':split,'maximum_calls':r['maximum_calls']}


def check_stage(split):
    p=check_plan();path=protocol_path(split);stage=load(path);committed(path);planned=requests(split)
    if stage['schema']!='public-selective-stage-1' or stage['split']!=split or stage['plan_sha256']!=sha(PLAN.read_bytes()) or stage['manifest_sha256']!=sha((folder(split)/'manifest.json').read_bytes()):raise ValueError('Stage protocol drift.')
    if stage['maximum_calls']!=COUNTS[split]*3 or stage['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned]:raise ValueError('Stage request drift.')
    if any(len(encoded(r['body']))>p['maximum_request_bytes'] for r in planned):raise ValueError('Request exceeds cap.')
    if split=='evaluation' and stage['boundary_sha256']!=sha(BOUNDARY.read_bytes()):raise ValueError('Evaluation boundary drift.')
    return p,stage,planned


def run(split,profile):
    p,stage,planned=check_stage(split);profile_check(profile)
    if split=='evaluation':verify_boundary()
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
            print(f"Selective {split} {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-selective-hosted-1','split':split,'planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),
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
    rows,s=verified_rows(split);refs=load(folder(split)/'references.json')
    curves=[]
    for policy in candidates():
        result=evaluate(rows,refs,policy);result.pop('outcomes');curves.append(result)
    selected=select(curves) if split=='calibration' else verify_boundary()['selected']
    policy=selected['policy'] if selected else {'threshold':2.,'margin':0.,'maximum_leads':1}
    shown=evaluate(rows,refs,policy)
    comparators={name:evaluate(rows,refs,p) for name,p in [('unfiltered_first',{'threshold':0.,'margin':0.,'maximum_leads':1}),('supported_alternative',{'threshold':0.,'margin':0.,'maximum_leads':2})]}
    top3=[]
    for number in range(1,4):
        actual={r['case_id']:r for r in rows if r['round']==number};lists=[(ref,shortlist(actual.get(ref['id']))) for ref in refs]
        top3.append({'round':number,'cases':len(refs),'cause_included':sum(ref['target'] in leads for ref,leads in lists),
            'wrong_leads':sum(sum(s!=ref['target'] for s in leads) for ref,leads in lists),'total_leads':sum(len(leads) for ref,leads in lists),'withheld':sum(not leads for ref,leads in lists)})
    local=load(output(split)/'controls.json');baseline={name:{'cases':len(refs),'correct_first':sum(local[r['id']][name]['choice']==r['target'] for r in refs),
        'cause_in_first_three':sum(r['target'] in [s['service'] for s in local[r['id']][name]['ranking'][:3]] for r in refs)} for name in ('ml','change','resource')}
    return {'schema':'public-selective-assessment-1','split':split,'cases':len(refs),'groups':len({r['group'] for r in refs}),'rounds':3,'planned_calls':COUNTS[split]*3,
        'failed_or_missing':s['failed']+s['unattempted'],'selected':selected,'selective':shown,'comparators':comparators,'original_shortlist':top3,'controls':baseline,
        'curves':curves if split=='calibration' else [],'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(protocol_path(split).read_bytes()),'summary_sha256':sha((output(split)/'summary.json').read_bytes())}}


def freeze_boundary():
    if BOUNDARY.exists():raise ValueError('Boundary already frozen.')
    verified_rows('calibration',complete=True);assessment=score('calibration')
    b={'schema':'public-selective-boundary-1','plan_sha256':sha(PLAN.read_bytes()),'assessment':assessment,'selected':assessment['selected'],
       'meaning':'User preference: fewer wrong leads. Zero observed errors across three calibration rounds are not an operational guarantee. No post-evaluation changes.'}
    BOUNDARY.write_text(json.dumps(b,indent=2)+'\n');return {'status':'frozen','selected':b['selected']}


def verify_boundary():
    check_plan();committed(BOUNDARY);b=load(BOUNDARY);verified_rows('calibration',complete=True)
    if b['schema']!='public-selective-boundary-1' or b['plan_sha256']!=sha(PLAN.read_bytes()) or b['assessment']!=score('calibration') or b['selected']!=b['assessment']['selected']:raise ValueError('Boundary failed recomputation.')
    if not b['selected']:raise ValueError('No useful error-free calibration policy; evaluation stays sealed.')
    return b
