"""Frozen language-only clarification assessment against a literal parser."""
import json,time,urllib.error,urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import validate_reply,GlobalReplyError
from . import explicit_missing_trial as previous, clarification_data as data
from .clarification_features import request,FIELDS,decision,parser,compose

PLAN=data.PLAN
BASE=data.BASE
SOURCES=previous.SOURCES+('triage_bench/clarification_features.py','triage_bench/clarification_data.py','triage_bench/clarification_trial.py','scripts/run_clarification.py')

def protocol_path(phase='development'):
    if phase!='development':raise ValueError('Only inspected-context language development is authorized.')
    return ROOT/'checkpoints/clarification-protocol-2026-10-06.json'
def result_path():return ROOT/'checkpoints/clarification-results-2026-10-06.json'
def output(phase='development'):
    protocol_path(phase);return BASE/'development-hosted-2026-10-06-v1'

def plan(profile):
    profile_check(profile);previous.verify();p=previous.check_plan()
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'clarification-plan-1','model':MODEL,'endpoint':p['endpoint'],'context_tokens':p['context_tokens'],'claims':76,'families':19,'variants':2,'rounds':3,'maximum_calls':228,'maximum_request_bytes':24000,
      'authorization':'User selected the recommended clarification-needs language task on 2026-10-06; continue until blocked, committing major steps.',
      'data':'Nineteen manually authored ambiguity families, two wording variants and two observed public application inventories. Use only names/channel catalogs from two already inspected packets, never measurements, cause labels, source paths or references. All texts/reference masks freeze before any model call. No new recording, reserve allocation, independent author or human review. Families and variants are correlated development cases, not 76 independent reports.',
      'contract':'Assess scope and clarity of service, channel, comparison kind, polarity and incident-window selection. Scope outside the metric task makes all entry fields not_applicable. Missing measurements do not make clear wording ambiguous. Never fill fields, calculate telemetry or execute actions. Code selects one question in service/channel/kind/polarity/window order from classified missing fields, or explains scope limits. Ready means the analyst may enter fields, not that a claim is true or automatically bound.',
      'execution':'Commit producers, manual text/reference patterns and plan before preparing the new pack. Commit separate inputs/references and exact request hashes before 228 once-only calls. Six Choice questions share each statement. Fixed 0.70 minimum across all selected options; whole-card quarantine on malformed fields and review on inconsistent scope/field labels. Rotate card order per round. No retry, answer repair, threshold tuning or further telemetry access.',
      'scoring':'For each application and each round, gate overall plus ready/clarify/outside_scope strata: complete valid classifications, >=95% correct workflow action/next question, >=90% exact six-field masks, >=90% correct displayed workflow actions, zero premature ready, zero displayed questions targeting an already clear field, zero incorrect scope displays. Literal parser has no model probability or fitted parameters. Score exact masks, needed fields, necessary questions, unnecessary questions, premature readiness, low-score withholding and actual calls separately. Paired display gains/losses against parser are diagnostic, not a substitute candidate.',
      'limits':'Controlled same-assistant language development. No authentic analyst notes, independent references, measured effort, downstream entry accuracy or numerical verdict inference. Public inventories are microservice applications, not representative telecom reports. Passing would support a bounded language role; promotion needs a separate protocol.',
      'contexts':data.contexts(),'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{str(path.relative_to(ROOT)):sha(path.read_bytes()) for path in (previous.PLAN,previous.protocol_path(),previous.result_path(),data.ORIGIN)}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'maximum_calls':228,'claims':76,'families':19,'new_recordings':0}

def check_plan():
    committed(PLAN);p=load(PLAN);previous.verify()
    if p['schema']!='clarification-plan-1' or p['maximum_calls']!=228 or p['contexts']!=data.contexts():raise ValueError('Clarification plan changed.')
    for name,digest in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Clarification producer or evidence changed: '+name)
    return p

def prepare():return data.prepare(check_plan)

def requests(phase='development'):
    protocol_path(phase);p=check_plan();data.validate(check_plan);packets=load(data.DATA/'inputs.json');jobs=[]
    for n in (1,2,3):
        for packet in packets[n-1:]+packets[:n-1]:
            b=request(packet);wire=encoded(b).decode()
            if any(x in wire for x in ('source_packet','reference',packet['id'],packet['family'])):raise ValueError('Reference metadata leaked into language wire.')
            jobs.append({'id':packet['id']+'::r'+str(n),'card_id':packet['id'],'phase':phase,'round':n,'request_sha256':sha(encoded(b)),'body':b})
    if len(jobs)!=p['maximum_calls']:raise ValueError('Clarification budget changed.')
    return jobs

def freeze():
    p=check_plan();jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if largest>p['maximum_request_bytes']:raise ValueError('Clarification wire cap exceeded before inference.')
    r={'schema':'clarification-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'calls':len(jobs),'largest_request_bytes':largest,'data_sha256':{n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with protocol_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'calls':len(jobs),'largest_request_bytes':largest}

def check(phase='development'):
    p=check_plan();committed(protocol_path(phase));r=load(protocol_path());jobs=requests(phase)
    if r['schema']!='clarification-protocol-1' or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs] or r['calls']!=len(jobs) or r['largest_request_bytes']!=max(len(encoded(j['body'])) for j in jobs) or r['data_sha256']!={n:sha((data.DATA/n).read_bytes()) for n in ('inputs.json','references.json','manifest.json')}:raise ValueError('Exact clarification protocol changed.')
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
    summary = {'schema': 'clarification-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'clarification-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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


def assessment(prediction,reference):
    target=reference['decision'];labels=prediction['labels'];displayed=prediction['displayed']
    mask=labels==reference['labels']
    raw=compose(labels) if labels else compose({})
    correct=raw['action']==target['action'] and (target['action']!='clarify' or raw['next_field']==target['next_field'])
    return {'valid':labels is not None,'field_correct':sum(labels.get(k)==reference['labels'][k] for k in FIELDS) if labels else 0,'exact_mask':mask,'workflow_correct':correct,'correct_display':bool(displayed and correct),'premature_ready':bool(displayed and prediction['action']=='ready' and target['action']!='ready'),'unnecessary_question':bool(displayed and prediction['action']=='clarify' and prediction['next_field'] not in target['needed']),'incorrect_scope':bool(displayed and ((prediction['action']=='outside_scope')!=(target['action']=='outside_scope'))),'missing_needed_fields':sum(k not in prediction['needed'] for k in target['needed']) if labels else len(target['needed']),'unnecessary_fields':sum(k not in target['needed'] for k in prediction['needed']),'withheld':not displayed}

def score():
    rows,summary=verified_rows('development');index={(r['card_id'],r['round']):r for r in rows};packets=load(data.DATA/'inputs.json');refs={r['id']:r for r in load(data.DATA/'references.json')};panels={};outcomes=[];paired=[]
    for p in packets:
        ref=refs[p['id']];plabels=parser(p);pd={'labels':plabels,'displayed':True,'minimum_score':None,**compose(plabels)}
        for n in (1,2,3):
            jd=decision(index.get((p['id'],n)));predictions={'jev':jd,'parser':pd}
            for method,prediction in predictions.items():
                o={'id':p['id'],'dataset':p['dataset'],'family':p['family'],'variant':p['variant'],'round':n,'method':method,'reference_action':ref['decision']['action'],'reference_labels':ref['labels'],'prediction':prediction,**assessment(prediction,ref)};outcomes.append(o)
                for scope in ('overall',ref['decision']['action']):
                    key=(p['dataset'],n,method,scope);v=panels.setdefault(key,{'dataset':p['dataset'],'round':n,'method':method,'scope':scope,'claims':0,'field_opportunities':0,**{k:0 for k in ('valid','field_correct','exact_mask','workflow_correct','correct_display','premature_ready','unnecessary_question','incorrect_scope','missing_needed_fields','unnecessary_fields','withheld')}})
                    v['claims']+=1;v['field_opportunities']+=6
                    for k in ('valid','field_correct','exact_mask','workflow_correct','correct_display','premature_ready','unnecessary_question','incorrect_scope','missing_needed_fields','unnecessary_fields','withheld'):v[k]+=int(o[k])
    for v in panels.values():v['passes']=v['valid']==v['claims'] and v['workflow_correct']>=.95*v['claims'] and v['exact_mask']>=.9*v['claims'] and v['correct_display']>=.9*v['claims'] and not any(v[k] for k in ('premature_ready','unnecessary_question','incorrect_scope'))
    oi={(o['id'],o['round'],o['method']):o for o in outcomes}
    for dataset in ('Train Ticket','Online Boutique'):
        for n in (1,2,3):
            ps=[p for p in packets if p['dataset']==dataset]
            paired.append({'dataset':dataset,'round':n,'correct_display_gains':sum(oi[p['id'],n,'jev']['correct_display'] and not oi[p['id'],n,'parser']['correct_display'] for p in ps),'correct_display_losses':sum(oi[p['id'],n,'parser']['correct_display'] and not oi[p['id'],n,'jev']['correct_display'] for p in ps)})
    return {'schema':'clarification-results-1','claims':76,'families':19,'actual_calls':summary['attempted_calls'],'field_opportunities':1368,'valid_fields':sum(len(r.get('answers',{})) for r in rows),'candidate_passes':summary['status']=='completed' and all(p['passes'] for p in panels.values() if p['method']=='jev'),'new_recordings':0,'human_reviews':0,'independent_reviews':0,'parser_unique_entries':76,'protocol_sha256':sha(protocol_path().read_bytes()),'run_summary_sha256':sha((output()/'summary.json').read_bytes()),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows),'summed_latency_ms':sum(r['latency_ms'] for r in rows),'panels':list(panels.values()),'paired':paired,'outcomes':outcomes}

def verify():
    committed(result_path());r=score()
    if r!=load(result_path()):raise ValueError('Clarification assessment changed.')
    return r
