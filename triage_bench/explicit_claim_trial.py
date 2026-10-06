"""Frozen explicit-claim comparison with an exact evaluator and separate references."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha,REVISION
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from .full_workflow_trial import SOURCES as OLD_SOURCES
from . import explicit_claim_data as data
from .explicit_claim_features import evaluate,request

PLAN=data.PLAN
BASE=data.BASE
SOURCES=OLD_SOURCES+('triage_bench/explicit_claim_features.py','triage_bench/explicit_claim_data.py','triage_bench/explicit_claim_trial.py','scripts/run_explicit_claims.py')

def protocol_path(phase):
    data.folder(phase)
    return ROOT/f'checkpoints/explicit-claims-{phase}-protocol-2026-10-06.json'

def result_path(phase):
    data.folder(phase)
    return ROOT/f'checkpoints/explicit-claims-{phase}-results-2026-10-06.json'

def output(phase):
    data.folder(phase)
    return BASE/f'{phase}-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile)
    prior=load(ROOT/'checkpoints/full-workflow-plan-2026-10-06.json')
    if any(profile[k]!=prior[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep recorded profile.')
    assignments=data.allocation()
    previous=[]
    for path in (ROOT/'checkpoints').glob('*plan*.json'):
        previous.extend(load(path).get('assignments',[]))
    if {a['source_case'] for a in assignments}&{a.get('source_case') for a in previous}:raise ValueError('New panel already allocated.')
    n=len(data.development());historical=sorted({sha(p.read_bytes()) for p in ROOT.glob('runs/**/raw/*/metrics.parquet')})
    record={'schema':'explicit-claim-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
      'authorization':'User selected explicit analyst-entered claims on 2026-10-06 and authorized continuation until blocked, with milestone commits.',
      'revision':REVISION,'assignments':assignments,'development_claims':n,'confirmation_claims':360,'rounds':3,
      'maximum_calls':3*(n+360),'maximum_request_bytes':16000,'historical_metric_sha256':historical,
      'contract':'One service, a selected before/after window, one supported kind, one strict boolean assertion and only the applicable recorded channel or duration measure. Fields are authoritative. Canonical text is generated from them; no free-text extraction, pronoun binding, annotation lookup or draft-text override. Reject invalid/extra fields locally before evaluation. Window selection here is supplied experiment metadata, not anomaly detection.',
      'inputs':'Same assistant constructs field-entry fixtures for both arms. Development uses 18 already inspected service observations from nine recordings, all six kinds in both polarities, plus 34 hand-specified numerical boundary fixtures. Fresh confirmation, conditional on the unchanged development gate, uses fifteen previously unallocated RE1-OB recordings from three whole service/fault groups selected by a fixed hash of group identity. Select two observed services and their metric/duration names by fixed hashes, never cause labels or numerical verdicts. RE1 has no supplied traces; duration/count questions must retain missingness. Group/fault labels are allocation metadata and never enter model requests.',
      'comparison':'Jev receives one typed claim and only the selected raw measurements with the complete fixed policy, one question per call. Exact evaluator computes that same contract without learning or hosted calls. An earlier independently implemented reference module supplies public-policy answers; manually specified fixtures cross-check it. All code is authored by the same assistant: no independent human review or external ground truth for health/causality. Exact rule accuracy is implementation agreement with declared policy, not learned generalization.',
      'execution':'Commit producers and plan before preparation; freeze exact packets, references and all request hashes before once-only inference. Three rounds with rotating claim order. No retries, repaired choices, probability changes or model changes. Record raw replies/quarantine and all missing denominators. Confirm only if every development panel passes; failure preserves all fresh measurements unopened.',
      'gate':'Per dataset and round: all calls complete, at least 95% Jev correct verdicts, at least 90% correct display coverage, zero wrong displays at 0.70, and 100% exact evaluator agreement. Count unanswerable as a displayed evidence-limit answer, never a service recommendation. Policy fixtures are a separate gate. Confidence is a model score, not calibrated operational risk.',
      'preparation':'Both arms share the same supplied fields. Record 4 choices per metric/duration claim and 3 per other claim; this is a field count, not measured effort or error rate. Zero human entries, reviews and independent reviews. App field editing previews deterministic policy only, makes no model call and writes no server file. Public browser export remains a local draft, not a completed independent review.',
      'limits':'No authentic analyst reports, production operations, automatic text understanding, incident detection, root-cause ranking or network action. Fresh confirmation validates new metrics only, not fresh traces. Protected 22 RE3 cause-evaluation, 30 RE3 Sock Shop and 140 RE1 reserves stay unopened.',
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
      'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [data.OLD_DATA/'inputs.json',data.OLD_DATA/'references.json',data.OLD_DATA/'manifest.json',data.INDEX,ROOT/'checkpoints/full-workflow-results-2026-10-06.json']}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:record[k] for k in ('development_claims','confirmation_claims','maximum_calls')}

def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='explicit-claim-plan-1' or p['assignments']!=data.allocation() or p['revision']!=REVISION or p['maximum_calls']!=3*(p['development_claims']+360):raise ValueError('Explicit plan changed.')
    for n,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Explicit source/evidence changed: '+n)
    return p

def prepare(phase):
    if phase=='confirmation':
        committed(result_path('development'))
        if not score('development')['passes']:raise ValueError('Development gate failed; fresh panel stays unopened.')
    return data.prepare(phase,check_plan)

def requests(phase):
    p=check_plan();data.validate_pack(phase,check_plan);packets=load(data.folder(phase)/'inputs.json');jobs=[]
    for n in (1,2,3):
        rotated=packets[n-1:]+packets[:n-1]
        for row in rotated:
            b=request(row['observation'],row['claim']);jobs.append({'id':row['id']+'::explicit::r'+str(n),'card_id':row['id'],'phase':phase,'round':n,'request_sha256':sha(encoded(b)),'body':b})
    if len(jobs)!=3*p[phase+'_claims']:raise ValueError('Explicit call budget changed.')
    return jobs

def freeze(phase):
    p=check_plan();jobs=requests(phase);largest=max(len(encoded(j['body'])) for j in jobs)
    if largest>p['maximum_request_bytes']:raise ValueError('Wire cap exceeded.')
    record={'schema':'explicit-claim-protocol-1','phase':phase,'plan_sha256':sha(PLAN.read_bytes()),'planned_jobs':len(jobs),'planned_calls':len(jobs),'planned_answers':len(jobs),
       'largest_request_bytes':largest,'data_sha256':{n:sha((data.folder(phase)/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},
       'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path(phase).open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k!='requests'}

def check(phase):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path(phase));jobs=requests(phase)
    expected={n:sha((data.folder(phase)/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')}
    if r['schema']!='explicit-claim-protocol-1' or r['phase']!=phase or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['data_sha256']!=expected or r['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs]:raise ValueError('Explicit protocol changed.')
    if any(r[k]!=len(jobs) for k in ('planned_jobs','planned_calls','planned_answers')) or r['largest_request_bytes']!=max(len(encoded(j['body'])) for j in jobs):raise ValueError('Protocol budget changed.')
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
            print(f"Explicit claims {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'explicit-claim-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'explicit-claim-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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


def score(phase):
    rows,summary=verified_rows(phase);index={(r['card_id'],r['round']):r for r in rows};packets=load(data.folder(phase)/'inputs.json');refs={r['id']:r for r in load(data.folder(phase)/'references.json')};outcomes=[];panels={};rule_ns=0
    for p in packets:
        start=time.perf_counter_ns();rule=evaluate(p['observation'],p['claim']);rule_ns+=time.perf_counter_ns()-start
        for n in (1,2,3):
            row=index.get((p['id'],n),{});a=row.get('answers',{}).get('claim_verdict');valid=bool(a and 'claim' not in row.get('quarantined_sentences',[]));display=bool(valid and a['probabilities'][a['choice']]>=.7);ref=refs[p['id']]['answer']
            o={'id':p['id'],'dataset':p['dataset'],'category':p['category'],'round':n,'reference':ref,'rule_answer':rule['answer'],'rule_correct':rule['answer']==ref,'jev_choice':a['choice'] if valid else 'unavailable','valid':valid,'correct':bool(valid and a['choice']==ref),'display':display,'wrong_display':bool(display and a['choice']!=ref),'correct_display':bool(display and a['choice']==ref)}
            outcomes.append(o);key=p['dataset']+'::r'+str(n);panel=panels.setdefault(key,{'dataset':p['dataset'],'round':n,'claims':0,'valid':0,'correct':0,'correct_display':0,'wrong_display':0,'rule_correct':0})
            for k in ('valid','correct','correct_display','wrong_display','rule_correct'):panel[k]+=int(o[k])
            panel['claims']+=1
    for panel in panels.values():panel['passes']=bool(panel['valid']==panel['claims'] and panel['correct']>=.95*panel['claims'] and panel['correct_display']>=.90*panel['claims'] and panel['wrong_display']==0 and panel['rule_correct']==panel['claims'])
    return {'schema':'explicit-claim-results-1','phase':phase,'claims':len(packets),'opportunities':len(outcomes),'actual_calls':summary['attempted_calls'],
      'valid_answers':sum(o['valid'] for o in outcomes),'correct_answers':sum(o['correct'] for o in outcomes),'correct_displays':sum(o['correct_display'] for o in outcomes),'wrong_displays':sum(o['wrong_display'] for o in outcomes),
      'rule_correct':sum(o['rule_correct'] for o in outcomes),'passes':summary['status']=='completed' and all(p['passes'] for p in panels.values()),
      'usage_input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows),'summed_provider_latency_ms':sum(r['latency_ms'] for r in rows),
      'exact_evaluator_timing':{'measured_once_per_unique_claim':len(packets),'total_nanoseconds':rule_ns,'note':'Local single-pass diagnostic; replay timing varies and is excluded from immutable assessment comparison.'},
      'field_choices':sum(4 if 'channel' in p['claim'] or 'measure' in p['claim'] else 3 for p in packets),'human_entries':0,'human_reviews':0,'independent_reviews':0,
      'protocol_sha256':sha(protocol_path(phase).read_bytes()),'run_summary_sha256':sha((output(phase)/'summary.json').read_bytes()),'panels':list(panels.values()),'outcomes':outcomes}

def stable(result):
    r=dict(result);r.pop('exact_evaluator_timing');return r

def verify(phase):
    committed(result_path(phase));record=load(result_path(phase));current=score(phase)
    if stable(record)!=stable(current):raise ValueError('Explicit assessment changed.')
    return record
