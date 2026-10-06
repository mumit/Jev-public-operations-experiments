"""Same fresh replies, two frozen optional-display policies; no field entry."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import optional_clarification_trial as previous
from .optional_clarification_features import request,assessment
from .optional_question_policy import decision

data=previous.data
PLAN=ROOT/'checkpoints/optional-question-plan-2026-10-06.json'
BASE=ROOT/'runs/optional-question'
SOURCES=previous.SOURCES+('triage_bench/optional_question_policy.py','triage_bench/optional_question_trial.py','scripts/run_optional_question.py')
def protocol_path(phase='development'):
    if phase!='development':raise ValueError('Only inspected-wording development is authorized.')
    return ROOT/'checkpoints/optional-question-protocol-2026-10-06.json'
def result_path():return ROOT/'checkpoints/optional-question-results-2026-10-06.json'
def output(phase='development'):
    protocol_path(phase);return BASE/'development-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile);previous.verify();p=load(previous.PLAN)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the pinned profile.')
    paths=(previous.PLAN,previous.protocol_path(),previous.result_path(),*(data.DATA/n for n in ('inputs.json','references.json','manifest.json')))
    record={'schema':'optional-question-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'claims':92,'families':23,'rounds':3,'policies':['all_fields','first_question'],'candidate':'first_question','maximum_calls':276,'maximum_answers':1656,'maximum_request_bytes':24000,
      'authorization':'User selected optional clarification alongside required explicit entry and continuation until blocked, committing major steps. Publication and pushes remain authorized.',
      'data':'Reuse the frozen 92 inspected optional statements and their references unchanged. Same assistant, two inspected public inventories, correlated development. No measurements, new recording or protected allocation.',
      'hypothesis':'Post-exposure diagnosis on previous checklist replies gave 252 correct displays under the first-question dependencies versus 187 under all-fields. These retrospective counts motivate the prospective fresh-reply comparison; they are not confirmation.',
      'contract':'One optional question in service/channel/kind/polarity/window order. Never fill fields, bind a claim, approve entry, declare readiness or compute truth. Required explicit entry remains unchanged.',
      'policies':'One shared unchanged six-field focused request per card and round. all_fields preserves previous score and consistency logic. first_question requires structurally valid answers for every field, then gates scope plus fields through the first clarify label. Outside-scope disposition requires scope only. No-question requires all six. Semantically inconsistent unused later labels are retained, not repaired; the result makes no full-mask claim. Any malformed unused field quarantines the whole card. Keep 0.70 and fixed question priority.',
      'execution':'Commit sources/plan, then exact protocol before 276 once-only calls and 1656 answers. Apply both policies to the same replies offline. No retries, repairs, reference-guided edits, threshold search or case removal. Global checkpoint/envelope/context/access/network/validation failure stops. Costs count shared calls once.',
      'scoring':'first_question sole candidate: in every application and round, overall plus complete_wording/needs_question/outside_task, require complete valid cards, >=95% correct canonical action, >=90% correct display, zero unnecessary displayed question, zero silent ambiguity miss, zero wrong scope display. Preserve necessary question, wrong order, missed clarification including withholding, and paired policy gains/losses. A failed candidate cannot be replaced by the inspected control.',
      'limits':'Fresh responses on inspected text are development, not independent text or incident validation. No human entry/review, utility, effort, field correctness or telecom readiness claim. If these gates fail, stop policy tuning and present the remaining task choice.',
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{str(x.relative_to(ROOT)):sha(x.read_bytes()) for x in paths}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'claims':92,'maximum_calls':276,'maximum_answers':1656,'new_recordings':0}

def check_plan():
    committed(PLAN);p=load(PLAN);previous.check_plan()
    if p['schema']!='optional-question-plan-1' or p['maximum_calls']!=276 or p['candidate']!='first_question':raise ValueError('Policy plan changed.')
    for n,d in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=d:raise ValueError('Policy dependency changed: '+n)
    return p

def requests(phase='development'):
    protocol_path(phase);p=check_plan();data.validate(previous.check_plan);packets=load(data.DATA/'inputs.json');jobs=[]
    for n in (1,2,3):
        for packet in packets[n-1:]+packets[:n-1]:
            body=request(packet,'checklist');wire=encoded(body).decode()
            if any(x in wire for x in ('source_packet','reference',packet['id'],packet['family'])):raise ValueError('Reference metadata leaked.')
            jobs.append({'id':packet['id']+'::shared::r'+str(n),'card_id':packet['id'],'arm':'shared','phase':phase,'round':n,'request_sha256':sha(encoded(body)),'body':body})
    if len(jobs)!=p['maximum_calls'] or sum(len(j['body']['questions']) for j in jobs)!=p['maximum_answers']:raise ValueError('Policy budget changed.')
    return jobs

def freeze():
    p=check_plan();jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if largest>p['maximum_request_bytes']:raise ValueError('Policy wire cap exceeded.')
    r={'schema':'optional-question-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='development'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    expected={'schema':'optional-question-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    if r!=expected:raise ValueError('Exact policy protocol changed.')
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
            print(f"Optional question policy {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'optional-question-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'optional-question-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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
    rows,summary=verified_rows('development');index={(r['card_id'],r['round']):r for r in rows};packets=load(data.DATA/'inputs.json');refs={r['id']:r for r in load(data.DATA/'references.json')};panels={};outcomes=[];paired=[]
    counts=('valid','workflow_correct','correct_display','question_needed','question_displayed','necessary_question','canonical_question','unnecessary_question','wrong_order_question','silent_miss','missed_clarification','withheld_ambiguity','wrong_scope','withheld')
    for p in packets:
        ref=refs[p['id']]
        for n in (1,2,3):
            predictions={arm:decision(index.get((p['id'],n)),arm) for arm in ('first_question','all_fields')}
            for method,prediction in predictions.items():
                o={'id':p['id'],'dataset':p['dataset'],'family':p['family'],'variant':p['variant'],'round':n,'method':method,'reference_scope':ref['scope'],'reference_choice':ref['choice'],'needed':ref['needed'],'prediction':prediction,**assessment(prediction,ref)};outcomes.append(o)
                for scope in ('overall',ref['scope']):
                    key=(p['dataset'],n,method,scope);v=panels.setdefault(key,{'dataset':p['dataset'],'round':n,'method':method,'scope':scope,'claims':0,**{k:0 for k in counts}})
                    v['claims']+=1
                    for k in counts:v[k]+=int(o[k])
    for v in panels.values():v['passes']=v['valid']==v['claims'] and v['workflow_correct']>=.95*v['claims'] and v['correct_display']>=.9*v['claims'] and not any(v[k] for k in ('unnecessary_question','silent_miss','wrong_scope'))
    oi={(o['id'],o['round'],o['method']):o for o in outcomes}
    for dataset in ('Train Ticket','Online Boutique'):
        for n in (1,2,3):
            ps=[p for p in packets if p['dataset']==dataset]
            for comparator in ('all_fields',):
                paired.append({'dataset':dataset,'round':n,'comparator':comparator,'correct_display_gains':sum(oi[p['id'],n,'first_question']['correct_display'] and not oi[p['id'],n,comparator]['correct_display'] for p in ps),'correct_display_losses':sum(oi[p['id'],n,comparator]['correct_display'] and not oi[p['id'],n,'first_question']['correct_display'] for p in ps)})
    costs={'shared':{'actual_calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),'valid_answers':sum(len(r.get('answers',{})) for r in rows),'quarantined_statements':sum(bool(r.get('quarantined_sentences')) for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows),'summed_latency_ms':sum(r['latency_ms'] for r in rows)}}
    return {'schema':'optional-question-results-1','claims':92,'families':23,'actual_calls':summary['attempted_calls'],'answer_opportunities':1656,'valid_answers':sum(len(r.get('answers',{})) for r in rows),'candidate_passes':summary['status']=='completed' and all(p['passes'] for p in panels.values() if p['method']=='first_question'),'new_recordings':0,'human_entries':0,'human_reviews':0,'independent_reviews':0,'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'costs':costs,'panels':list(panels.values()),'paired':paired,'outcomes':outcomes}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Optional assessment changed.')
    return r
