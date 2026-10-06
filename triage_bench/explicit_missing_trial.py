"""Fresh confirmation of calculated input, with focused raw-fact controls."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha,REVISION
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import explicit_format_trial as prior,explicit_missing_data as data
from .explicit_format_features import request
from .explicit_claim_features import evaluate

PLAN=data.PLAN
BASE=data.BASE
ARMS=('focused','calculated')
from . import explicit_native_v2_trial as preserved
from .explicit_preparation_audit import verify as verify_failures, AUDIT
SOURCES=preserved.SOURCES+('triage_bench/explicit_missing_features.py','triage_bench/explicit_missing_data.py','triage_bench/explicit_missing_trial.py','scripts/run_explicit_missing.py')

def protocol_path(phase='confirmation'):
    if phase!='confirmation':raise ValueError('Unknown confirmation phase.')
    return ROOT/'checkpoints/explicit-missing-protocol-2026-10-06.json'
def result_path():return ROOT/'checkpoints/explicit-missing-results-2026-10-06.json'
def output(phase='confirmation'):
    protocol_path(phase);return BASE/'confirmation-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile);r=prior.verify()
    if not r['candidate_passes']:raise ValueError('Calculated development candidate must pass.')
    p=prior.check_plan()
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep recorded profile.')
    verify_failures();allocations=load(data.previous.PLAN)['assignments']
    record={'schema':'explicit-missing-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'revision':REVISION,'candidate':'calculated','assignments':allocations,'claims':360,'rounds':3,'maximum_calls':2160,'maximum_request_bytes':16000,
      'authorization':'User selected retention of the incomplete recording as missing evidence and continuation until blocked on 2026-10-06.',
      'allocation':'Reuse exactly the fifteen already opened ranks 10-12 RE1-OB recordings from the preserved native-v2 preparation failure. No downloads, additional allocation, case replacement, onset repair or fabricated rows. Retain all five repetitions per whole service/fault group and the same identity-only service/channel selection. Schema and window coverage were inspected before this protocol; this is post-preparation confirmation, not a wholly untouched panel. Original ranks 1-3 and all earlier protected panels remain unopened.',
      'missing_contract':'Sorted unique genuine timestamps and the original declared boundary are required. Either window may have zero rows. An absent window has null duration, medians and missing fraction; scaled change is null if either median is unavailable. The actual row count is zero, not a measured metric or span count. Missing traces remain null. Both assertion polarities are unanswerable for ineligible comparisons. Keep original channel names, allowlist and arithmetic on complete windows.',
      'execution':'Commit this contract, producers and plan before constructing new claims from the preserved publisher-verified sources. Commit separate inputs/references/coverage hashes and exact requests before 2160 once-only focused/calculated calls. Keep both request functions, evaluator, independent references and 0.70 display gates unchanged. Rotate order; preserve raw failures, quarantine and full denominators. No retries or repairs.',
      'scoring':'Calculated candidate must complete all calls; in every round and every declared panel require >=95% correct, >=90% correct displays, zero wrong displays and exact evaluator agreement. Panels are overall, complete windows, missing window, metric comparisons on complete windows and other claim kinds on complete windows. Missing-window panel includes all 24 claims per round and both polarities. No group exclusion or score-boundary adjustment after results.',
      'limits':'360 assistant-entered fixtures on fifteen previously downloaded public recordings; zero new recordings or human/independent reviews. Four of six claim kinds are unanswerable without traces or causal/health evidence; report those separately. Calculated input delegates arithmetic/validity to code and cannot establish utility over exact computation, authentic analyst performance, duration transfer on fresh traces or telecom readiness.',
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
      'evidence_sha256':{str(path.relative_to(ROOT)):sha(path.read_bytes()) for path in [prior.PLAN,prior.protocol_path(),prior.result_path(),data.original.INDEX,data.previous.PLAN,AUDIT]}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'maximum_calls':2160,'claims':360,'recordings':15,'new_recordings':0,'missing_window_recordings':1}

def check_plan():
    verify_failures();committed(PLAN);p=load(PLAN)
    if p['schema']!='explicit-missing-plan-1' or p['assignments']!=load(data.previous.PLAN)['assignments'] or p['maximum_calls']!=2160 or p['revision']!=REVISION or not prior.verify()['candidate_passes']:raise ValueError('Missing-window plan changed.')
    for n,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Missing-window source/evidence changed: '+n)
    return p

def prepare():return data.prepare(check_plan)

def requests(phase='confirmation'):
    protocol_path(phase);p=check_plan();data.validate(check_plan);packets=load(data.DATA/'inputs.json');jobs=[]
    for n in (1,2,3):
        for i,row in enumerate(packets[n-1:]+packets[:n-1]):
            shift=(i+n-1)%2
            for arm in ARMS[shift:]+ARMS[:shift]:
                b=request(row['observation'],row['claim'],arm);wire=encoded(b).decode()
                if any(term in wire for term in ('source_case','root_cause_service',row['id'],'reference','re1ob_')):raise ValueError('Metadata leaked into confirmation wire.')
                jobs.append({'id':row['id']+'::confirmation::'+arm+'::r'+str(n),'card_id':row['id'],'arm':arm,'phase':phase,'round':n,'request_sha256':sha(encoded(b)),'body':b})
    if len(jobs)!=p['maximum_calls']:raise ValueError('Fresh call budget changed.')
    return jobs

def freeze():
    p=check_plan();jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if largest>p['maximum_request_bytes']:raise ValueError('Fresh wire cap exceeded.')
    r={'schema':'explicit-missing-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','coverage.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='confirmation'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    if r['schema']!='explicit-missing-protocol-1' or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs] or r['calls']!=len(jobs) or r['largest_request_bytes']!=max(len(encoded(j['body'])) for j in jobs) or r['data_sha256']!={n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','coverage.json','manifest.json')}:raise ValueError('Fresh exact protocol changed.')
    return p,jobs

def run(phase, profile):
    p, planned = check(phase); profile_check(profile)
    if any(profile[k] != p[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Explicit profile changed.')
    key = clean_api_key(profile.get('api_key', ''))
    if not key:
        raise ValueError('Server-side key required.')
    destination = output(phase); destination.parent.mkdir(parents=True, exist_ok=True); destination.mkdir()
    (destination / 'requests.json').write_text(json.dumps(planned, indent=2) + '\n')
    rows, reason, consecutive = [], None, 0
    opener = urllib.request.build_opener(NoRedirect())
    with (destination / 'responses.jsonl').open('x') as stream:
        for req in planned:
            row = {k: v for k, v in req.items() if k != 'body'}
            row['status'] = 'ok' if req['body'] else 'skipped_no_accepted_claims'
            start = time.perf_counter()
            if req['body']:
                try:
                    wire = urllib.request.Request(profile['endpoint'], data=encoded(req['body']), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key}, method='POST')
                    with opener.open(wire, timeout=30) as response:
                        content = response.read(1048577)
                    if len(content) > 1048576:
                        raise ValueError('Oversized provider response.')
                    raw = json.loads(content); row['raw_response'] = redact(raw, key)
                    if not isinstance(raw, dict) or raw.get('model') != MODEL:
                        reason = 'checkpoint_mismatch'; raise ValueError('Wrong model.')
                    row.update(validate_reply(raw, req['body'], p['context_tokens']))
                    tokens = row['usage'].get('input_tokens')
                    if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 1:
                        raise ValueError('Missing usage.')
                    if tokens > p['context_tokens']:
                        reason = 'reported_context_overflow'; raise ValueError('Context overflow.')
                except GlobalReplyError as error:
                    row.update(status='error', error=str(error)); reason = str(error)
                except urllib.error.HTTPError as error:
                    row.update(status='error', error='Provider HTTP ' + str(error.code)); reason = 'provider_http_' + str(error.code);error.close()
                except (OSError, ValueError, KeyError, TypeError) as error:
                    row.update(status='error', error='Validation or request failure: ' + type(error).__name__)
                    reason = 'network_error' if isinstance(error,OSError) else 'request_or_validation_failure'
            row = redact(row, key); row['latency_ms'] = (time.perf_counter() - start) * 1000 if req['body'] else 0
            rows.append(row); stream.write(json.dumps(row) + '\n'); stream.flush()
            print(f"Explicit confirmation {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'explicit-missing-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
        'planned_calls': sum(bool(r['body']) for r in planned), 'recorded_jobs': len(rows),
        'attempted_calls': sum(r['status'] != 'skipped_no_accepted_claims' for r in rows),
        'failed': sum(r['status'] == 'error' for r in rows), 'unattempted_jobs': len(planned) - len(rows),
        'status': 'completed' if len(rows) == len(planned) and all(r['status'] != 'error' for r in rows) else 'incomplete_or_failed',
        'stopped_reason': reason, 'protocol_sha256': sha(protocol_path(phase).read_bytes()),
        'files': {n: sha((destination / n).read_bytes()) for n in ('requests.json', 'responses.jsonl')}}
    (destination / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def verified_rows(phase, complete=False):
    p, planned = check(phase); dest = output(phase); summary = load(dest / 'summary.json')
    if summary['schema'] != 'explicit-missing-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
        raise ValueError('Explicit hosted identity changed.')
    for name, digest in summary['files'].items():
        if sha((dest / name).read_bytes()) != digest:
            raise ValueError('Explicit hosted bytes changed.')
    if load(dest / 'requests.json') != planned:
        raise ValueError('Explicit saved requests changed.')
    rows = [json.loads(line) for line in (dest / 'responses.jsonl').read_text().splitlines()]
    if len(rows) > len(planned):
        raise ValueError('Extra note jobs.')
    for row, req in zip(rows, planned):
        if any(row.get(k) != v for k, v in req.items() if k != 'body') or row['status'] not in ('ok', 'ok_with_review', 'error', 'skipped_no_accepted_claims'):
            raise ValueError('Explicit response identity changed.')
        if bool(req['body']) == (row['status'] == 'skipped_no_accepted_claims'):
            raise ValueError('Skip does not match zero accepted claims.')
        if row['status'] == 'skipped_no_accepted_claims' and any(k in row for k in ('answers', 'raw_response', 'usage')):
            raise ValueError('Application skip fabricated provider evidence.')
        if row['status'] in ('ok', 'ok_with_review'):
            validated = validate_reply(row['raw_response'], req['body'], p['context_tokens'])
            if any(row.get(k) != v for k, v in validated.items()):
                raise ValueError('Sentence normalized reply changed.')
    status = 'completed' if len(rows) == len(planned) and not any(r['status'] == 'error' for r in rows) else 'incomplete_or_failed'
    if (summary['planned_jobs'], summary['planned_calls'], summary['recorded_jobs'], summary['attempted_calls'], summary['failed'], summary['unattempted_jobs'], summary['status']) != (len(planned), sum(bool(r['body']) for r in planned), len(rows), sum(r['status'] != 'skipped_no_accepted_claims' for r in rows), sum(r['status'] == 'error' for r in rows), len(planned) - len(rows), status):
        raise ValueError('Explicit hosted denominators changed.')
    if complete and (status != 'completed' or summary['stopped_reason']):
        raise ValueError('Complete note evidence required.')
    return rows, summary


def score():
    rows,summary=verified_rows('confirmation');index={(r['card_id'],r['arm'],r['round']):r for r in rows};packets=load(data.DATA/'inputs.json');refs={r['id']:r for r in load(data.DATA/'references.json')};outcomes=[];panels={}
    for p in packets:
        rule=evaluate(p['observation'],p['claim'])
        for n in (1,2,3):
            for arm in ARMS:
                row=index.get((p['id'],arm,n),{});a=row.get('answers',{}).get('claim_verdict');valid=bool(a and 'claim' not in row.get('quarantined_sentences',[]));display=bool(valid and a['probabilities'][a['choice']]>=.7);ref=refs[p['id']]['answer']
                o={'id':p['id'],'dataset':p['dataset'],'category':p['category'],'kind':p['claim']['kind'],'round':n,'arm':arm,'reference':ref,'rule_answer':rule['answer'],'rule_correct':rule['answer']==ref,'choice':a['choice'] if valid else 'unavailable','valid':valid,'correct':bool(valid and a['choice']==ref),'correct_display':bool(display and a['choice']==ref),'wrong_display':bool(display and a['choice']!=ref)}
                outcomes.append(o)
                scopes=['overall',p['category']]
                if p['category']=='complete_windows':scopes.append('complete_metrics' if p['claim']['kind'].startswith('metric_') else 'complete_other_kinds')
                for scope in scopes:
                    key=(arm,n,scope);v=panels.setdefault(key,{'dataset':p['dataset'],'scope':scope,'arm':arm,'round':n,'claims':0,'valid':0,'correct':0,'correct_display':0,'wrong_display':0,'rule_correct':0})
                    for k in ('valid','correct','correct_display','wrong_display','rule_correct'):v[k]+=int(o[k])
                    v['claims']+=1
    for v in panels.values():v['passes']=bool(v['valid']==v['claims'] and v['correct']>=.95*v['claims'] and v['correct_display']>=.9*v['claims'] and v['wrong_display']==0 and v['rule_correct']==v['claims'])
    oi={(o['id'],o['arm'],o['round']):o for o in outcomes};paired=[]
    for n in (1,2,3):
        gains=sum(oi[p['id'],'calculated',n]['correct_display'] and not oi[p['id'],'focused',n]['correct_display'] for p in packets);losses=sum(oi[p['id'],'focused',n]['correct_display'] and not oi[p['id'],'calculated',n]['correct_display'] for p in packets)
        paired.append({'dataset':'Online Boutique','round':n,'candidate':'calculated','comparator':'focused','correct_display_gains':gains,'correct_display_losses':losses})
    return {'schema':'explicit-missing-results-1','claims':360,'opportunities':2160,'actual_calls':summary['attempted_calls'],'valid_answers':sum(o['valid'] for o in outcomes),'candidate':'calculated','candidate_passes':summary['status']=='completed' and all(v['passes'] for v in panels.values() if v['arm']=='calculated'),'new_recordings':0,'reused_recordings':15,'missing_window_recordings':1,'prior_failed_preparation_recordings':45,'human_entries':0,'human_reviews':0,'independent_reviews':0,
      'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'panels':list(panels.values()),'paired':paired,
      'costs':[{'arm':arm,'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_ms':sum(r['latency_ms'] for r in rows if r['arm']==arm)} for arm in ARMS],'outcomes':outcomes}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Fresh calculated assessment changed.')
    return r
