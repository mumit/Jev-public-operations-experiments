"""Frozen optional-question task on new controlled wording, no numerical inference."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import clarification_trial as original,clarification_focus_trial as previous,optional_clarification_data as data
from .optional_clarification_features import request,decision,parser_decision,assessment

PLAN=data.PLAN
BASE=data.BASE
SOURCES=previous.SOURCES+('triage_bench/optional_clarification_features.py','triage_bench/optional_clarification_data.py','triage_bench/optional_clarification_trial.py','scripts/run_optional_clarification.py')

def protocol_path(phase='development'):
    if phase!='development':raise ValueError('Only controlled new-wording development is authorized.')
    return ROOT/'checkpoints/optional-clarification-protocol-2026-10-06.json'
def result_path():return ROOT/'checkpoints/optional-clarification-results-2026-10-06.json'
def output(phase='development'):
    protocol_path(phase);return BASE/'development-hosted-2026-10-06-v1'

def prior_identity():
    # Historical results were replayed before this task. Check their committed
    # closure and saved bytes here; full replay remains in the publication CLI.
    for t in (original,previous):
        for path in (t.PLAN,t.protocol_path(),t.result_path()):committed(path)
        p=load(t.PLAN);result=load(t.result_path());summary=load(t.output()/'summary.json')
        for name,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Historical clarification dependency changed.')
        if result['protocol_sha256']!=sha(t.protocol_path().read_bytes()) or summary['protocol_sha256']!=result['protocol_sha256'] or result['run_summary_sha256']!=sha((t.output()/'summary.json').read_bytes()):raise ValueError('Historical run identity changed.')
        for folder,files in ((t.data.DATA,load(t.protocol_path())['data_sha256']),(t.output(),summary['files'])):
            for name,digest in files.items():
                if sha((folder/name).read_bytes())!=digest:raise ValueError('Historical clarification bytes changed.')
    return load(previous.PLAN)

def plan(profile):
    profile_check(profile);p=prior_identity();packets,refs=data.reconstruct()
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the pinned profile.')
    if {p['text'] for p in packets}&{p['text'] for p in load(original.data.DATA/'inputs.json')}:raise ValueError('New wording repeats an inspected statement.')
    record={'schema':'optional-clarification-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'claims':92,'families':23,'rounds':3,'arms':['direct','checklist'],'candidate':'direct','maximum_calls':552,'maximum_answers':1932,'maximum_request_bytes':24000,
      'authorization':'The user selected optional clarification suggestions alongside required field entry on 2026-10-06 and authorized continuation until blocked, committing major steps. Publication and pushes remain authorized.',
      'data':'Freeze all new statements and manually declared needed-field/reference-question patterns before inference. Twenty-three families, two variants and two already inspected public application catalogs: 92 controlled statements. Nineteen familiar policy situations plus unavailable channel, missing subject+channel, bare assertion topic and repair request. Each application has 12 complete-wording, 28 needs-question and 6 outside-task statements. Same-assistant new-wording development, not independent or held-out incident evidence. No measurements or new recording.',
      'contract':'One optional question, using service/channel/kind/polarity/window order. A question is necessary only when that field needs clarification; necessary questions in another order are separate from unnecessary ones. no_question means no suggestion, never ready, approval, a completed entry or numerical truth. Explicit selection remains mandatory for every field; Jev cannot fill, bind or change anything. Keep all omissions and ambiguous no-question answers in scoring. Outside-task requests receive a boundary explanation.',
      'comparators':'Fresh field-specific six-question input remains byte-identical to clarification_focus_features.request(packet,focused); its six-field 0.70 boundary and whole-card quarantine stay unchanged. Map its existing ready disposition to no_suggestion only in this NEW task; historical readiness scores stay untouched. Direct is one Choice question on identical state, with the same option-score boundary 0.70 applied to its sole required answer. The shorter question and fewer score events both change, so this is a task-format comparison, not an isolated threshold improvement. The frozen literal parser maps to the same optional actions without calls or fitted parameters.',
      'execution':'Commit source, text/reference patterns and plan before pack preparation, then pack and exact request hashes before 552 once-only calls. Three rounds rotate card order and alternate paired-arm order. Preserve raw replies, whole-statement invalid-answer quarantine and global wrong-checkpoint/envelope/context/HTTP/network/validation stops. No retry, repair, threshold fitting, reference-guided request change or case replacement.',
      'scoring':'Gate direct in every application and round, overall plus complete_wording/needs_question/outside_task strata: complete valid responses, >=95% correct canonical action/next question, >=90% correct displayed actions, zero displayed unnecessary questions, zero displayed no-question on ambiguity, zero wrong scope displays. Count necessary/canonical questions, wrong order, missed clarification including withholding, silent misses, withheld ambiguities, actual responses and paired gains/losses separately. No readiness or full-mask promotion is claimed. A failed candidate cannot be replaced with an inspected comparator.',
      'limits':'Same assistant writes text and references under a conservative declared policy. Public catalogs are microservice applications, not representative telecom reports. Controlled question correctness is not measured usefulness, analyst effort, entry correctness, independent judgment or production readiness. A passing controlled result would precede a separately frozen transfer or participant protocol. Protected allocations stay unopened.',
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
      'evidence_sha256':{str(path.relative_to(ROOT)):sha(path.read_bytes()) for path in (original.PLAN,original.protocol_path(),original.result_path(),previous.PLAN,previous.protocol_path(),previous.result_path(),original.data.ORIGIN,*(original.data.DATA/n for n in ('inputs.json','references.json','manifest.json')))}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'claims':92,'families':23,'maximum_calls':552,'maximum_answers':1932,'new_recordings':0}

def check_plan():
    committed(PLAN);p=load(PLAN);prior_identity()
    if p['schema']!='optional-clarification-plan-1' or p['maximum_calls']!=552 or p['maximum_answers']!=1932 or p['candidate']!='direct':raise ValueError('Optional plan changed.')
    for name,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Optional producer or evidence changed: '+name)
    return p

def prepare():return data.prepare(check_plan)

def requests(phase='development'):
    protocol_path(phase);p=check_plan();data.validate(check_plan);packets=load(data.DATA/'inputs.json');jobs=[]
    for n in (1,2,3):
        for i,packet in enumerate(packets[n-1:]+packets[:n-1]):
            arms=('checklist','direct') if (i+n)%2 else ('direct','checklist')
            for arm in arms:
                b=request(packet,arm);wire=encoded(b).decode()
                if any(x in wire for x in ('source_packet','reference',packet['id'],packet['family'])):raise ValueError('Reference metadata leaked.')
                jobs.append({'id':packet['id']+'::'+arm+'::r'+str(n),'card_id':packet['id'],'arm':arm,'phase':phase,'round':n,'request_sha256':sha(encoded(b)),'body':b})
    if len(jobs)!=p['maximum_calls'] or sum(len(j['body']['questions']) for j in jobs)!=p['maximum_answers']:raise ValueError('Optional budget changed.')
    return jobs
def freeze():
    p=check_plan();jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if largest>p['maximum_request_bytes']:raise ValueError('Optional clarification wire cap exceeded before inference.')
    r={'schema':'optional-clarification-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='development'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    if r['schema']!='optional-clarification-protocol-1' or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs] or r['calls']!=len(jobs) or r['largest_request_bytes']!=max(len(encoded(j['body'])) for j in jobs) or r['data_sha256']!={n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')}:raise ValueError('Exact clarification protocol changed.')
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
            print(f"Optional clarification {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'optional-clarification-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'optional-clarification-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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
    rows,summary=verified_rows('development');index={(r['card_id'],r['round'],r['arm']):r for r in rows};packets=load(data.DATA/'inputs.json');refs={r['id']:r for r in load(data.DATA/'references.json')};panels={};outcomes=[];paired=[]
    counts=('valid','workflow_correct','correct_display','question_needed','question_displayed','necessary_question','canonical_question','unnecessary_question','wrong_order_question','silent_miss','missed_clarification','withheld_ambiguity','wrong_scope','withheld')
    for p in packets:
        ref=refs[p['id']];pd=parser_decision(p)
        for n in (1,2,3):
            predictions={arm:decision(index.get((p['id'],n,arm)),arm) for arm in ('direct','checklist')};predictions['parser']=pd
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
            for comparator in ('checklist','parser'):
                paired.append({'dataset':dataset,'round':n,'comparator':comparator,'correct_display_gains':sum(oi[p['id'],n,'direct']['correct_display'] and not oi[p['id'],n,comparator]['correct_display'] for p in ps),'correct_display_losses':sum(oi[p['id'],n,comparator]['correct_display'] and not oi[p['id'],n,'direct']['correct_display'] for p in ps)})
    costs={arm:{'actual_calls':sum(r['arm']==arm for r in rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows if r['arm']==arm),'valid_answers':sum(len(r.get('answers',{})) for r in rows if r['arm']==arm),'quarantined_statements':sum(bool(r.get('quarantined_sentences')) for r in rows if r['arm']==arm),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_ms':sum(r['latency_ms'] for r in rows if r['arm']==arm)} for arm in ('direct','checklist')}
    return {'schema':'optional-clarification-results-1','claims':92,'families':23,'actual_calls':summary['attempted_calls'],'answer_opportunities':1932,'valid_answers':sum(len(r.get('answers',{})) for r in rows),'candidate_passes':summary['status']=='completed' and all(p['passes'] for p in panels.values() if p['method']=='direct'),'new_recordings':0,'human_entries':0,'human_reviews':0,'independent_reviews':0,'parser_unique_entries':92,'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'costs':costs,'panels':list(panels.values()),'paired':paired,'outcomes':outcomes}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Optional assessment changed.')
    return r
