"""Confirm the frozen selective policy on both remaining public reserve sets."""
import json,time,urllib.request,urllib.error
from pathlib import Path
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed,verify_local
from .public_rca_trial import MODEL,normalize
from .public_rca_models import infer
from .public_selective_policy import evaluate
from .public_temporal_trial import shortlist
from .public_confirmation_data import PLAN,INDEX,BASE,COUNTS,folder,check_plan,validate
from .public_selective_trial import verify_boundary,score as selective_score,RESULTS as SELECTIVE_RESULTS,BOUNDARY
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import profile_check

RESULTS=ROOT/'checkpoints/public-confirmation-results-2026-10-04.json'
SOURCES=('triage_bench/public_confirmation_data.py','triage_bench/public_confirmation_trial.py','scripts/run_public_confirmation.py','uv.lock',
 'triage_bench/public_selective_policy.py','triage_bench/public_selective_trial.py','triage_bench/public_selective_data.py')
POLICY={'threshold':.7,'margin':0.,'maximum_leads':1}


def eligibility():
    boundary=verify_boundary();committed(SELECTIVE_RESULTS);a=selective_score('evaluation')
    if a!=load(SELECTIVE_RESULTS) or a['failed_or_missing'] or boundary['selected']['policy']!=POLICY or a['selective']['policy']!=POLICY:raise ValueError('Confirmation requires complete unchanged selective evidence.')
    if any(r['wrong_leads'] or not r['shown'] for r in a['selective']['per_round']):raise ValueError('Confirmation gate failed; reserves stay unopened.')
    return a


def protocol_path(split='confirmation'):return ROOT/'checkpoints/public-confirmation-protocol-2026-10-04.json'
def output(split='confirmation'):return BASE/'confirmation-hosted-2026-10-04-v1'


def freeze_plan(profile):
    profile_check(profile);eligibility()
    if PLAN.exists():raise ValueError('Confirmation plan exists.')
    tt=ROOT/'checkpoints/public-temporal-preparation-2026-10-04.json';ss=ROOT/'checkpoints/public-format-plan-2026-10-03.json'
    assignments=[{**r,'split':'confirmation','dataset':name} for name,path in [('Train Ticket',tt),('Sock Shop',ss)] for r in load(path)['assignments'] if r['split']=='reserve']
    if len(assignments)!=54 or len({r['id'] for r in assignments})!=54:raise ValueError('Reserve assignment counts changed.')
    if {name:sum(r['dataset']==name for r in assignments) for name in ('Train Ticket','Sock Shop')}!={'Train Ticket':18,'Sock Shop':36}:raise ValueError('Reserve panel sizes changed.')
    previous=load(ROOT/'checkpoints/public-selective-plan-2026-10-04.json')
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(previous['model'],previous['endpoint'],previous['context_tokens']):raise ValueError('Keep the Jev profile.')
    p={'schema':'public-confirmation-plan-1','decision':'User selected confirmation on untouched reserve cases on 2026-10-04.',
       'counts':COUNTS,'dataset_counts':{'Train Ticket':18,'Sock Shop':36},'assignments':assignments,'revision':previous['revision'],'index_sha256':previous['index_sha256'],
       'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':previous['maximum_request_bytes'],'maximum_calls':162,'rounds':3,'policy':POLICY,
       'input':'Unchanged named summaries, question, every observed service, fixed 0.70 threshold and zero margin. Three serial rounds rotate case order; no retries or warmup.',
       'selection':'None. No grid search, calibration, threshold fitting, prompt changes, candidate filtering or ML refitting. All reference joins stay outside requests.',
       'reporting':'Each application separately: correct first choice, shown correct/wrong leads, coverage, correct choices lost to withholding, model insufficient evidence, distinct-case display consistency and unchanged ML/change/resource rankings. Do not pool repeated calls as independent cases.',
       'gate':'Complete calibration and evaluation must reproduce; the evaluation policy has nonempty coverage and no observed wrong displayed lead in every round. Commit this plan before downloading either reserve, then commit exact request fingerprints before calls.',
       'limits':'Controlled injected application faults with supplied boundaries; not telecom readiness, an operational error rate or measured analyst benefit. Public pretraining exposure is unknown.',
       'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
       'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (tt,ss,BOUNDARY,SELECTIVE_RESULTS,ROOT/'checkpoints/public-selective-plan-2026-10-04.json')}}
    PLAN.write_text(json.dumps(p,indent=2)+'\n');return {'status':'frozen','maximum_calls':162,'dataset_counts':p['dataset_counts']}


def requests(split='confirmation'):
    validate(split);packets=load(folder(split)/'inputs.json');result=[]
    for number in range(1,4):
        offset=number-1
        for packet in packets[offset:]+packets[:offset]:
            result.append({'id':f"{packet['id']}::named::r{number}",'case_id':packet['id'],'arm':'named','round':number,'body':packet['request'],'request_sha256':sha(encoded(packet['request']))})
    return result


def controls(split='confirmation'):
    p=load(ROOT/'checkpoints/public-format-protocol-2026-10-03.json');model=verify_local(ROOT/p['local'],ROOT/p['historical_data'])
    return {r['id']:infer(r['state'],model) for r in load(folder(split)/'inputs.json')}


def freeze_stage(split='confirmation'):
    eligibility();p=check_plan();path=protocol_path()
    if path.exists():raise ValueError('Confirmation protocol exists.')
    m=validate(split)
    if not m['fits_empirical_wire_cap']:raise ValueError('Confirmation request exceeds empirical cap.')
    r={'schema':'public-confirmation-stage-1','split':split,'maximum_calls':162,'plan_sha256':sha(PLAN.read_bytes()),'manifest_sha256':sha((folder(split)/'manifest.json').read_bytes()),
       'requests':[{k:v for k,v in r.items() if k!='body'} for r in requests()]}
    path.write_text(json.dumps(r,indent=2)+'\n');return {'status':'frozen','maximum_calls':162}


def check_stage(split='confirmation'):
    p=check_plan();path=protocol_path();committed(path);s=load(path);planned=requests()
    if s['schema']!='public-confirmation-stage-1' or s['split']!=split or s['maximum_calls']!=162 or s['plan_sha256']!=sha(PLAN.read_bytes()) or s['manifest_sha256']!=sha((folder(split)/'manifest.json').read_bytes()):raise ValueError('Confirmation stage drift.')
    if s['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned] or any(len(encoded(r['body']))>p['maximum_request_bytes'] for r in planned):raise ValueError('Confirmation request drift.')
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
            print(f"Confirmation {split} {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-confirmation-hosted-1','split':split,'planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),
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


def score(split='confirmation'):
    rows,s=verified_rows(split);refs=load(folder(split)/'references.json');assignment={r['id']:r for r in check_plan()['assignments']};local=load(output()/'controls.json');datasets={}
    for name in ('Train Ticket','Sock Shop'):
        rr=[r for r in refs if assignment[r['id']]['dataset']==name];ids={r['id'] for r in rr};actual=[r for r in rows if r['case_id'] in ids]
        result=evaluate(actual,rr,POLICY)
        unfiltered=evaluate(actual,rr,{'threshold':0.,'margin':0.,'maximum_leads':1})
        alternatives=evaluate(actual,rr,{'threshold':0.,'margin':0.,'maximum_leads':2})
        baseline={arm:{'cases':len(rr),'correct_first':sum(local[r['id']][arm]['choice']==r['target'] for r in rr),'cause_in_first_three':sum(r['target'] in [x['service'] for x in local[r['id']][arm]['ranking'][:3]] for r in rr)} for arm in ('ml','change','resource')}
        top3=[]
        for number in range(1,4):
            indexed={r['case_id']:r for r in actual if r['round']==number};lists=[(ref,shortlist(indexed.get(ref['id']))) for ref in rr]
            top3.append({'round':number,'cases':len(rr),'cause_included':sum(ref['target'] in leads for ref,leads in lists),'wrong_leads':sum(sum(s!=ref['target'] for s in leads) for ref,leads in lists),'total_leads':sum(len(leads) for ref,leads in lists),'withheld':sum(not leads for ref,leads in lists)})
        datasets[name]={'cases':len(rr),'groups':len({r['group'] for r in rr}),'selective':result,'comparators':{'unfiltered_first':unfiltered,'supported_alternative':alternatives},'original_shortlist':top3,'controls':baseline,'curves':[]}
    return {'schema':'public-confirmation-assessment-1','cases':54,'planned_calls':162,'failed_or_missing':s['failed']+s['unattempted'],'policy':POLICY,'datasets':datasets,
       'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(protocol_path().read_bytes()),'summary_sha256':sha((output()/'summary.json').read_bytes())}}
