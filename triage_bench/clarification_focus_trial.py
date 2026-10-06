"""Paired instruction-only language development on the frozen clarification pack."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import clarification_trial as previous
from .clarification_features import FIELDS,decision,parser,compose
from .clarification_focus_features import request
from .clarification_trial import assessment

data=previous.data
PLAN=ROOT/'checkpoints/clarification-focus-plan-2026-10-06.json'
BASE=ROOT/'runs/clarification-focus'
SOURCES=previous.SOURCES+('triage_bench/clarification_focus_features.py','triage_bench/clarification_focus_trial.py','scripts/run_clarification_focus.py')

def protocol_path(phase='development'):
    if phase!='development':raise ValueError('Only paired inspected-text development is authorized.')
    return ROOT/'checkpoints/clarification-focus-protocol-2026-10-06.json'
def result_path():return ROOT/'checkpoints/clarification-focus-results-2026-10-06.json'
def output(phase='development'):
    protocol_path(phase);return BASE/'development-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile);previous.verify();p=previous.check_plan()
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'clarification-focus-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'claims':76,'families':19,'rounds':3,'arms':['control','focused'],'maximum_calls':456,'maximum_request_bytes':24000,
      'authorization':'User selected clarification-needs assessment and authorized continuation until blocked, committing major steps. Instruction-only paired diagnostic follows the failed original study.',
      'data':'Reuse all 76 frozen controlled statements, manual masks and public catalogs unchanged. No new text, recording, reference, independent author or human review. Familiar correlated development examples.',
      'treatment':'Control is byte-identical to the original request. Focused changes only six instruction strings, using shorter field-specific wording. State, question keys/types/options, reference labels, parser, compose order and selected-score boundary 0.70 stay fixed. Emphasize independence of missing fields and existing outside-scope not-applicable rule; do not add field bindings or numerical checks.',
      'execution':'Commit sources and plan, then exact request hashes before 456 once-only calls. Rotate card order and alternate control/focused order across cards and rounds. Whole-card invalid-field quarantine, inconsistent scope review and global failure stops are unchanged. No retry, answer repair, threshold tuning or protected telemetry access.',
      'scoring':p['scoring']+' Focused is the sole declared candidate. Score fresh control, focused and frozen parser separately; compare focused display gains/losses against both. Never replace a failed candidate with an inspected arm. Three rounds are repeated opportunities, not independent text.',
      'limits':p['limits'],
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
      'evidence_sha256':{str(path.relative_to(ROOT)):sha(path.read_bytes()) for path in (previous.PLAN,previous.protocol_path(),previous.result_path(),*(data.DATA/n for n in ('inputs.json','references.json','manifest.json')))}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'maximum_calls':456,'claims':76,'new_recordings':0}

def check_plan():
    committed(PLAN);p=load(PLAN);previous.verify()
    if p['schema']!='clarification-focus-plan-1' or p['maximum_calls']!=456:raise ValueError('Focused plan changed.')
    for name,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Focused producer or evidence changed: '+name)
    return p

def requests(phase='development'):
    protocol_path(phase);p=check_plan();data.validate(previous.check_plan);packets=load(data.DATA/'inputs.json');jobs=[]
    for n in (1,2,3):
        for i,packet in enumerate(packets[n-1:]+packets[:n-1]):
            arms=('control','focused') if (i+n)%2 else ('focused','control')
            for arm in arms:
                b=request(packet,arm);wire=encoded(b).decode()
                if any(x in wire for x in ('source_packet','reference',packet['id'],packet['family'])):raise ValueError('Reference metadata leaked.')
                jobs.append({'id':packet['id']+'::'+arm+'::r'+str(n),'card_id':packet['id'],'arm':arm,'phase':phase,'round':n,'request_sha256':sha(encoded(b)),'body':b})
    if len(jobs)!=p['maximum_calls']:raise ValueError('Focused budget changed.')
    return jobs
def freeze():
    p=check_plan();jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if largest>p['maximum_request_bytes']:raise ValueError('Clarification wire cap exceeded before inference.')
    r={'schema':'clarification-focus-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='development'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    if r['schema']!='clarification-focus-protocol-1' or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs] or r['calls']!=len(jobs) or r['largest_request_bytes']!=max(len(encoded(j['body'])) for j in jobs) or r['data_sha256']!={n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')}:raise ValueError('Exact clarification protocol changed.')
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
            print(f"Clarification {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'clarification-focus-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'clarification-focus-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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
    counts=('valid','field_correct','exact_mask','workflow_correct','correct_display','premature_ready','unnecessary_question','incorrect_scope','missing_needed_fields','unnecessary_fields','withheld')
    for p in packets:
        ref=refs[p['id']];plabels=parser(p);pd={'labels':plabels,'displayed':True,'minimum_score':None,**compose(plabels)}
        for n in (1,2,3):
            predictions={arm:decision(index.get((p['id'],n,arm))) for arm in ('control','focused')};predictions['parser']=pd
            for method,prediction in predictions.items():
                o={'id':p['id'],'dataset':p['dataset'],'family':p['family'],'variant':p['variant'],'round':n,'method':method,'reference_action':ref['decision']['action'],'reference_labels':ref['labels'],'prediction':prediction,**assessment(prediction,ref)};outcomes.append(o)
                for scope in ('overall',ref['decision']['action']):
                    key=(p['dataset'],n,method,scope);v=panels.setdefault(key,{'dataset':p['dataset'],'round':n,'method':method,'scope':scope,'claims':0,'field_opportunities':0,**{k:0 for k in counts}})
                    v['claims']+=1;v['field_opportunities']+=6
                    for k in counts:v[k]+=int(o[k])
    for v in panels.values():v['passes']=v['valid']==v['claims'] and v['workflow_correct']>=.95*v['claims'] and v['exact_mask']>=.9*v['claims'] and v['correct_display']>=.9*v['claims'] and not any(v[k] for k in ('premature_ready','unnecessary_question','incorrect_scope'))
    oi={(o['id'],o['round'],o['method']):o for o in outcomes}
    for dataset in ('Train Ticket','Online Boutique'):
        for n in (1,2,3):
            ps=[p for p in packets if p['dataset']==dataset]
            for comparator in ('control','parser'):
                paired.append({'dataset':dataset,'round':n,'comparator':comparator,'correct_display_gains':sum(oi[p['id'],n,'focused']['correct_display'] and not oi[p['id'],n,comparator]['correct_display'] for p in ps),'correct_display_losses':sum(oi[p['id'],n,comparator]['correct_display'] and not oi[p['id'],n,'focused']['correct_display'] for p in ps)})
    costs={arm:{'actual_calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_ms':sum(r['latency_ms'] for r in rows if r['arm']==arm)} for arm in ('control','focused')}
    return {'schema':'clarification-focus-results-1','claims':76,'families':19,'actual_calls':summary['attempted_calls'],'field_opportunities':2736,'valid_fields':sum(len(r.get('answers',{})) for r in rows),'candidate_passes':summary['status']=='completed' and all(p['passes'] for p in panels.values() if p['method']=='focused'),'new_recordings':0,'human_reviews':0,'independent_reviews':0,'parser_unique_entries':76,'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'costs':costs,'panels':list(panels.values()),'paired':paired,'outcomes':outcomes}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Focused assessment changed.')
    return r
