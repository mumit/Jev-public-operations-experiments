"""Fresh typed controls versus focused and calculated explicit-claim requests."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import explicit_claim_trial as prior
from .explicit_format_features import ARMS,request

PLAN=ROOT/'checkpoints/explicit-format-plan-2026-10-06.json'
BASE=ROOT/'runs/explicit-format'
SOURCES=prior.SOURCES+('triage_bench/explicit_format_features.py','triage_bench/explicit_format_trial.py','scripts/run_explicit_format.py')

def protocol_path(phase='development'):
    if phase!='development':raise ValueError('This diagnostic opens no fresh recordings.')
    return ROOT/'checkpoints/explicit-format-protocol-2026-10-06.json'

def result_path():return ROOT/'checkpoints/explicit-format-results-2026-10-06.json'
def output(phase='development'):
    protocol_path(phase);return BASE/'development-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile);p=prior.check_plan()
    if any(p[k]!=profile[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep recorded profile.')
    r={'schema':'explicit-format-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'candidate':'calculated','claims':250,'rounds':3,'maximum_calls':2250,'maximum_request_bytes':16000,
      'authorization':'User selected explicit analyst-entered claims and continuation until blocked on 2026-10-06. This diagnoses the failed typed request before any fresh panel is opened.',
      'comparison':'Typed controls are exact fresh unchanged first-experiment bodies. Focused produces one literal positive or negative comparison and only the relevant task policy, with selected raw facts. Calculated has identical focused questions plus deterministic validity, minimum recorded count, absolute metric magnitude or duration relative change. It supplies no reference, selected-assertion truth or verdict. This delegates validity/arithmetic to code; it is not evidence of improved unaided model arithmetic. Focused changes wording, state and policy scope together, so differences cannot isolate one factor.',
      'execution':'Commit producers/plan, then all 2250 exact once-only request hashes before inference. Rotate claims and three arms for three rounds. Fixed 0.70 display gate, original references, full denominators, raw quarantine, global stopping; no retry, repair or threshold change. Use only 250 inspected development claims; zero new recordings or human/independent entries.',
      'gate':'Calculated is the prospective candidate. Per application/fixture panel and round require complete calls, >=95% correct, >=90% correct displayed, zero wrong displays; exact evaluator agreement remains required. Record paired gains and losses against contemporary typed and focused controls. A passed diagnostic does not open the failed original confirmation automatically; any fresh candidate confirmation requires a separately frozen protocol.',
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
      'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [prior.PLAN,prior.protocol_path('development'),prior.result_path('development'),*(prior.data.folder('development')/n for n in ('inputs.json','references.json','manifest.json'))]}}
    with PLAN.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'maximum_calls':2250,'new_recordings':0,'candidate':'calculated'}

def check_plan():
    committed(PLAN);p=load(PLAN);prior.verify('development')
    if p['schema']!='explicit-format-plan-1' or p['maximum_calls']!=2250 or p['candidate']!='calculated':raise ValueError('Explicit format identity changed.')
    for n,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Explicit format sources/evidence changed: '+n)
    return p

def requests(phase='development'):
    protocol_path(phase);check_plan();packets=load(prior.data.folder('development')/'inputs.json');jobs=[]
    for n in (1,2,3):
        for i,p in enumerate(packets[n-1:]+packets[:n-1]):
            shift=(i+n-1)%3
            for arm in ARMS[shift:]+ARMS[:shift]:
                b=request(p['observation'],p['claim'],arm);jobs.append({'id':p['id']+'::explicit-format::'+arm+'::r'+str(n),'card_id':p['id'],'arm':arm,'phase':phase,'round':n,'request_sha256':sha(encoded(b)),'body':b})
    return jobs

def freeze():
    p=check_plan();jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if len(jobs)!=p['maximum_calls'] or largest>p['maximum_request_bytes']:raise ValueError('Format request budget changed.')
    r={'schema':'explicit-format-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='development'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    if r['schema']!='explicit-format-protocol-1' or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs] or r['calls']!=len(jobs) or r['largest_request_bytes']!=max(len(encoded(j['body'])) for j in jobs):raise ValueError('Explicit format protocol changed.')
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
            print(f"Explicit format {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'explicit-format-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'explicit-format-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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
    rows,summary=verified_rows('development');index={(r['card_id'],r['arm'],r['round']):r for r in rows};packets=load(prior.data.folder('development')/'inputs.json');refs={r['id']:r for r in load(prior.data.folder('development')/'references.json')};outcomes=[];panels={}
    for p in packets:
        for n in (1,2,3):
            for arm in ARMS:
                row=index.get((p['id'],arm,n),{});a=row.get('answers',{}).get('claim_verdict');valid=bool(a and 'claim' not in row.get('quarantined_sentences',[]));display=bool(valid and a['probabilities'][a['choice']]>=.7);ref=refs[p['id']]['answer']
                o={'id':p['id'],'dataset':p['dataset'],'category':p['category'],'kind':p['claim']['kind'],'asserted':p['claim']['asserted'],'round':n,'arm':arm,'reference':ref,'choice':a['choice'] if valid else 'unavailable','valid':valid,'correct':bool(valid and a['choice']==ref),'correct_display':bool(display and a['choice']==ref),'wrong_display':bool(display and a['choice']!=ref)}
                outcomes.append(o);key=(p['dataset'],arm,n);v=panels.setdefault(key,{'dataset':p['dataset'],'arm':arm,'round':n,'claims':0,'valid':0,'correct':0,'correct_display':0,'wrong_display':0})
                for k in ('valid','correct','correct_display','wrong_display'):v[k]+=int(o[k])
                v['claims']+=1
    for v in panels.values():v['passes']=bool(v['valid']==v['claims'] and v['correct']>=.95*v['claims'] and v['correct_display']>=.9*v['claims'] and v['wrong_display']==0)
    oi={(o['id'],o['arm'],o['round']):o for o in outcomes};paired=[]
    for dataset in sorted({p['dataset'] for p in packets}):
        for n in (1,2,3):
            for comparator in ('typed','focused'):
                selected=[p for p in packets if p['dataset']==dataset];gains=losses=0
                for p in selected:
                    a=oi[p['id'],'calculated',n]['correct_display'];b=oi[p['id'],comparator,n]['correct_display'];gains+=a and not b;losses+=b and not a
                paired.append({'dataset':dataset,'round':n,'candidate':'calculated','comparator':comparator,'correct_display_gains':gains,'correct_display_losses':losses})
    costs=[{'arm':arm,'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_ms':sum(r['latency_ms'] for r in rows if r['arm']==arm)} for arm in ARMS]
    return {'schema':'explicit-format-results-1','claims':250,'opportunities':2250,'actual_calls':summary['attempted_calls'],'valid_answers':sum(o['valid'] for o in outcomes),'candidate':'calculated','candidate_passes':summary['status']=='completed' and all(v['passes'] for v in panels.values() if v['arm']=='calculated'),
      'new_recordings':0,'human_entries':0,'human_reviews':0,'independent_reviews':0,'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'panels':list(panels.values()),'paired':paired,'costs':costs,'outcomes':outcomes}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Explicit format assessment changed.')
    return r
