"""Fresh confirmation of calculated input, with focused raw-fact controls."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha,REVISION
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import explicit_format_trial as prior,explicit_confirmation_data as data
from .explicit_format_features import request
from .explicit_claim_features import evaluate

PLAN=data.PLAN
BASE=data.BASE
ARMS=('focused','calculated')
SOURCES=prior.SOURCES+('triage_bench/explicit_confirmation_data.py','triage_bench/explicit_confirmation_trial.py','scripts/run_explicit_confirmation.py')

def protocol_path(phase='confirmation'):
    if phase!='confirmation':raise ValueError('Unknown confirmation phase.')
    return ROOT/'checkpoints/explicit-confirmation-protocol-2026-10-06.json'
def result_path():return ROOT/'checkpoints/explicit-confirmation-results-2026-10-06.json'
def output(phase='confirmation'):
    protocol_path(phase);return BASE/'confirmation-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile);r=prior.verify()
    if not r['candidate_passes']:raise ValueError('Calculated development candidate must pass.')
    p=prior.check_plan()
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep recorded profile.')
    allocations=data.allocation();other=[]
    for path in (ROOT/'checkpoints').glob('*plan*.json'):other.extend(load(path).get('assignments',[]))
    if {a['source_case'] for a in allocations}&{a.get('source_case') for a in other}:raise ValueError('Confirmation cases already allocated.')
    record={'schema':'explicit-confirmation-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'revision':REVISION,'candidate':'calculated','assignments':allocations,'claims':360,'rounds':3,'maximum_calls':2160,'maximum_request_bytes':16000,
      'authorization':'User selected explicit analyst-entered claims and continuation until blocked on 2026-10-06. Calculated development passes; fresh confirmation is separately frozen before measurement access.',
      'allocation':'Fifteen previously unallocated RE1-OB recordings in the next three fixed hash-ranked whole service/fault groups (ranks 4-6). Original failed experiment ranks 1-3 remain allocated but unopened. Full groups retain all five repetitions. Select two observed services and channel names by the frozen identity-only hash, never cause labels or outcome features. Known injected interval is a supplied condition. No traces are supplied in this suite.',
      'execution':'Commit producers/plan before thirty pinned publisher-verified downloads. Reconstruct separate inputs/references; commit exact request hashes and pack fingerprints before once-only three-round focused and calculated calls. Keep existing request functions byte-exact for these new observations. Rotate order. No retries, repairs, thresholds or model changes. Preserve raw failures, quarantine and full denominators.',
      'scoring':'Candidate per round: complete calls, >=95% correct, >=90% correct displays, zero wrong displays at 0.70; exact evaluator must match all references. Compare actual paired gains/losses with focused raw-fact controls. Unanswerable is an evidence-limit answer, never a service recommendation. Confidence is not calibrated risk.',
      'limits':'All 360 field entries are assistant fixtures on fifteen fresh public recordings. Zero human entries/reviews/independent reviews, no measured analyst effort. Calculated input delegates validity/arithmetic to code and cannot show additional utility over exact policy execution. Fresh missing-trace decisions do not validate fresh trace-duration arithmetic. Protected earlier panels and original fifteen-case explicit allocation remain unopened.',
      'historical_metric_sha256':sorted({sha(p.read_bytes()) for p in ROOT.glob('runs/**/raw/*/metrics.parquet')}),
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [prior.PLAN,prior.protocol_path(),prior.result_path(),data.original.INDEX,data.original.PLAN]}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'maximum_calls':2160,'claims':360,'fresh_recordings':15}

def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='explicit-confirmation-plan-1' or p['assignments']!=data.allocation() or p['maximum_calls']!=2160 or p['revision']!=REVISION or not prior.verify()['candidate_passes']:raise ValueError('Fresh confirmation plan changed.')
    for n,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Fresh confirmation source/evidence changed: '+n)
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
    r={'schema':'explicit-confirmation-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='confirmation'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    if r['schema']!='explicit-confirmation-protocol-1' or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs] or r['calls']!=len(jobs) or r['largest_request_bytes']!=max(len(encoded(j['body'])) for j in jobs) or r['data_sha256']!={n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')}:raise ValueError('Fresh exact protocol changed.')
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
    summary = {'schema': 'explicit-confirmation-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'explicit-confirmation-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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
                outcomes.append(o);key=(arm,n);v=panels.setdefault(key,{'dataset':p['dataset'],'arm':arm,'round':n,'claims':0,'valid':0,'correct':0,'correct_display':0,'wrong_display':0,'rule_correct':0})
                for k in ('valid','correct','correct_display','wrong_display','rule_correct'):v[k]+=int(o[k])
                v['claims']+=1
    for v in panels.values():v['passes']=bool(v['valid']==v['claims'] and v['correct']>=.95*v['claims'] and v['correct_display']>=.9*v['claims'] and v['wrong_display']==0 and v['rule_correct']==v['claims'])
    oi={(o['id'],o['arm'],o['round']):o for o in outcomes};paired=[]
    for n in (1,2,3):
        gains=sum(oi[p['id'],'calculated',n]['correct_display'] and not oi[p['id'],'focused',n]['correct_display'] for p in packets);losses=sum(oi[p['id'],'focused',n]['correct_display'] and not oi[p['id'],'calculated',n]['correct_display'] for p in packets)
        paired.append({'dataset':'Online Boutique','round':n,'candidate':'calculated','comparator':'focused','correct_display_gains':gains,'correct_display_losses':losses})
    return {'schema':'explicit-confirmation-results-1','claims':360,'opportunities':2160,'actual_calls':summary['attempted_calls'],'valid_answers':sum(o['valid'] for o in outcomes),'candidate':'calculated','candidate_passes':summary['status']=='completed' and all(v['passes'] for v in panels.values() if v['arm']=='calculated'),'new_recordings':15,'human_entries':0,'human_reviews':0,'independent_reviews':0,
      'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'panels':list(panels.values()),'paired':paired,
      'costs':[{'arm':arm,'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_ms':sum(r['latency_ms'] for r in rows if r['arm']==arm)} for arm in ARMS],'outcomes':outcomes}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Fresh calculated assessment changed.')
    return r
