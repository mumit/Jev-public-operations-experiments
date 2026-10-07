"""Frozen fresh-wording value test; no protected access or participant records."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import optional_question_trial as previous
from . import ambiguity_value_data as data
from .ambiguity_value_features import request,rules,jev
from .optional_clarification_features import assessment

PLAN=ROOT/'checkpoints/ambiguity-value-plan-2026-10-06.json'
BASE=ROOT/'runs/ambiguity-value'
SOURCES=previous.SOURCES+('triage_bench/ambiguity_value_features.py','triage_bench/ambiguity_value_data.py','triage_bench/ambiguity_value_trial.py','scripts/run_ambiguity_value.py')
def protocol_path(phase='development'):
    if phase!='development':raise ValueError('Only controlled wording development is authorized.')
    return ROOT/'checkpoints/ambiguity-value-protocol-2026-10-06.json'
def result_path():return ROOT/'checkpoints/ambiguity-value-results-2026-10-06.json'
def output(phase='development'):
    protocol_path(phase);return BASE/'development-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile);previous.verify();p=load(previous.PLAN)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep pinned hosted profile.')
    paths=(previous.PLAN,previous.protocol_path(),previous.result_path(),*(previous.data.DATA/n for n in ('inputs.json','references.json','manifest.json')))
    record={'schema':'ambiguity-value-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'claims':48,'pairs':24,'rounds':3,'candidate':'jev','maximum_calls':144,'maximum_answers':864,'maximum_request_bytes':24000,
     'authorization':'The user selected fresh ambiguity tasks versus simple rules, clearer separate UI and continuation until no option remains, committing major steps. Source/public model evidence publication remains authorized; participant exports and assessments remain private.',
     'data':'48 new controlled statements: twelve pairs per existing application catalog. Complete wording, explicit omissions and subtler ambiguity. Pair members differ in wording and declared omissions; two pairs are complete-wording invariance controls. Same-assistant authored patterns and masks before inference, known semantic families, not independently written reports or held-out incidents. No fresh measurements, recording or protected source.',
     'candidate_contract':'Keep the exact focused six-field request, pinned Jev 1.13.0, whole-card malformed-field quarantine, first-question dependency policy, fixed priority and 0.70 unchanged. Optional question only, no field entry, readiness, numerical verdict or incident action.',
     'rules':'Fixed literal rules recognize named subjects, catalog channel aliases, magnitude/direction wording, final corrections, conflicts and explicit windows. No labels, family IDs, fitted parameters, model output or post-result edits. Rules can ask unnecessary questions; preserve them. Form validation alone only identifies empty selected fields and is not a text-ambiguity predictor.',
     'gates':'In each application and each round require all cards structurally valid, zero unnecessary or wrong-order displayed questions, zero silent ambiguity misses or wrong scope, >=90% canonical necessary-question coverage overall and separately in omission/subtle categories, no loss of correct displayed actions versus rules overall, and at least two subtle-category correct-display gains with zero paired losses there. Every gate must pass before recommending another participant comparison. These are research criteria, not operational reliability claims.',
     'execution':'Commit all producers and this plan before preparation; commit exact pack/request hashes before 144 once-only calls. No retries, response repair, threshold tuning, post-result text/rule changes or case replacement. Preserve partial/invalid results and stop on global access/network/identity/envelope/context failures. One shared request per statement/round; rules scored offline on those same inputs.',
     'limits':'Controlled wording and references share an author. Correct-display gains do not measure user effort or genuine-report performance. Failure ends this clarification policy tuning; no protected panel opens. Keep original walkthrough/core/interface untouched; revised learning UI is a separate unscored sandbox.',
     'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{str(x.relative_to(ROOT)):sha(x.read_bytes()) for x in paths}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'claims':48,'maximum_calls':144,'maximum_answers':864,'new_recordings':0}

def check_plan():
    committed(PLAN);p=load(PLAN);previous.check_plan()
    if p['schema']!='ambiguity-value-plan-1' or p['maximum_calls']!=144 or p['candidate']!='jev':raise ValueError('Value plan changed.')
    for n,d in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=d:raise ValueError('Value dependency changed: '+n)
    return p

def requests(phase='development'):
    protocol_path(phase);p=check_plan();data.validate(check_plan);packets=load(data.DATA/'inputs.json');jobs=[]
    for n in (1,2,3):
        for packet in packets[n-1:]+packets[:n-1]:
            body=request(packet);wire=encoded(body).decode()
            if any(x in wire for x in (packet['id'],packet['family'],packet['pair'],'reference_origin')):raise ValueError('Value request leaked reference metadata.')
            jobs.append({'id':packet['id']+'::jev::r'+str(n),'card_id':packet['id'],'arm':'jev','phase':phase,'round':n,'request_sha256':sha(encoded(body)),'body':body})
    if len(jobs)!=p['maximum_calls'] or sum(len(j['body']['questions']) for j in jobs)!=p['maximum_answers']:raise ValueError('Value call budget changed.')
    return jobs

def freeze():
    p=check_plan();jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if largest>p['maximum_request_bytes']:raise ValueError('Value wire cap exceeded.')
    r={'schema':'ambiguity-value-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='development'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    expected={'schema':'ambiguity-value-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    if r!=expected:raise ValueError('Exact value protocol changed.')
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
    summary = {'schema': 'ambiguity-value-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'ambiguity-value-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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

def score_rows(packets,refs,rows,complete=True):
    index={(r['card_id'],r['round']):r for r in rows};reference={r['id']:r for r in refs};outcomes=[];panels=[]
    for packet in packets:
        for n in (1,2,3):
            for method,pred in (('jev',jev(index.get((packet['id'],n)))),('rules',rules(packet))):
                outcomes.append({'id':packet['id'],'dataset':packet['dataset'],'category':packet['category'],'family':packet['family'],'pair':packet['pair'],'variant':packet['variant'],'round':n,'method':method,'reference_choice':reference[packet['id']]['choice'],'needed':reference[packet['id']]['needed'],'prediction':pred,**assessment(pred,reference[packet['id']])})
    keys=('valid','correct_display','necessary_question','canonical_question','unnecessary_question','wrong_order_question','silent_miss','missed_clarification','wrong_scope','withheld')
    paired=[]
    for dataset in ('Train Ticket','Online Boutique'):
        for n in (1,2,3):
            for category in ('overall','complete','omission','subtle'):
                by_method={}
                for method in ('jev','rules'):
                    os=[o for o in outcomes if o['dataset']==dataset and o['round']==n and o['method']==method and (category=='overall' or o['category']==category)]
                    p={'dataset':dataset,'round':n,'category':category,'method':method,'claims':len(os),'needed_questions':sum(bool(o['needed']) for o in os),**{k:sum(int(o[k]) for o in os) for k in keys}}
                    by_method[method]=p;panels.append(p)
                js={o['id']:o for o in outcomes if o['dataset']==dataset and o['round']==n and o['method']=='jev' and (category=='overall' or o['category']==category)}
                rs={o['id']:o for o in outcomes if o['dataset']==dataset and o['round']==n and o['method']=='rules' and (category=='overall' or o['category']==category)}
                gains=sum(js[k]['correct_display'] and not rs[k]['correct_display'] for k in js);losses=sum(rs[k]['correct_display'] and not js[k]['correct_display'] for k in js)
                j=by_method['jev'];gates={'all_valid':j['valid']==j['claims'],'no_unsafe_display':not any(j[k] for k in ('unnecessary_question','wrong_order_question','silent_miss','wrong_scope')),
                 'necessary_coverage':j['canonical_question']>=.90*j['needed_questions'],
                 'no_overall_display_loss':category!='overall' or j['correct_display']>=by_method['rules']['correct_display'],
                 'subtle_added_value':category!='subtle' or gains>=2 and losses==0}
                paired.append({'dataset':dataset,'round':n,'category':category,'gains':gains,'losses':losses,'gates':gates,'passes':all(gates.values())})
    return {'outcomes':outcomes,'panels':panels,'paired':paired,'candidate_passes':complete and all(p['passes'] for p in paired)}

def score():
    rows,summary=verified_rows('development');r=score_rows(load(data.DATA/'inputs.json'),load(data.DATA/'references.json'),rows,summary['status']=='completed')
    return {'schema':'ambiguity-value-results-1','claims':48,'pairs':24,'actual_calls':summary['attempted_calls'],'valid_answers':sum(len(r.get('answers',{})) for r in rows),'new_recordings':0,'human_entries':0,'human_reviews':0,'independent_reviews':0,'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows),'summed_latency_ms':sum(r['latency_ms'] for r in rows),**r}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Value assessment changed.')
    return r
