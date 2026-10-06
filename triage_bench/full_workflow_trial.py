"""Fresh complete-note automatic workflow versus trusted-field and parser controls."""
import copy
import json
import time
import urllib.error
import urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_sentence_features import extract,validate_reply,GlobalReplyError
from .public_note_features import DIMENSIONS,semantics,verdict_request,parser,annotated
from .public_note_language_features import extraction_request
from .public_note_language_data import DATA
from .subject_robustness_trial import SOURCES as OLD_SOURCES
from .excerpt_subject_trial import body as structured_body,check_reviews

PLAN=ROOT/'checkpoints/full-workflow-plan-2026-10-06.json'
RESULT=ROOT/'checkpoints/full-workflow-results-2026-10-06.json'
BASE=ROOT/'runs/full-workflow'
ARMS=('automatic','structured','parser')
SOURCES=OLD_SOURCES+('triage_bench/full_workflow_trial.py','scripts/run_full_workflow.py')


def protocol_path(phase):
    if phase not in ('initial','verdict'):raise ValueError('Unknown complete-workflow phase.')
    return ROOT/('checkpoints/full-workflow-'+phase+'-protocol-2026-10-06.json')


def output(phase):
    protocol_path(phase)
    return BASE/(phase+'-hosted-2026-10-06-v1')


def plan(profile):
    profile_check(profile);prior=load(ROOT/'checkpoints/subject-robustness-plan-2026-10-06.json')
    if any(profile[k]!=prior[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep recorded profile.')
    record={'schema':'full-workflow-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
      'authorization':'User authorized complete-report workflow comparison and structured-input alternative on 2026-10-06.',
      'candidate':'automatic','reports':27,'source_recordings':9,'rounds':3,'sentence_candidates':324,'routable_claims':162,
      'maximum_calls':324,'maximum_answers':8262,'maximum_request_bytes':79840,
      'inputs':'Start automatic and parser workflows from all twelve literal sentence candidates per note, not six confirmed claims. Automatic uses the exact earlier family-only extraction request, unchanged definitions, complete inventories and observations, and sentence-level validation. Parser uses the frozen conservative literal parser without fitting or model probabilities. Neither can insert annotations or repaired subjects. Automatic full-note context avoids the information loss found in truncation diagnostics. This is a fresh complete-workflow comparison, not a new context transformation or controlled causal attribution.',
      'structured_control':'Trusted-field upper bound from the six committed assistant-confirmed claims. Its bound-text numerical bodies are exact contemporary clean controls. Selection and field correctness are supplied by construction, not automatic Jev extraction or measured analyst effort. Zero human and independent reviews. Report its assumption explicitly; the whole-flow comparison changes both preparation and request grouping.',
      'execution':'Commit producers/plan then exact initial protocol before 162 independent calls: 81 automatic six-dimension extraction calls and 81 structured numerical verdict batches. Freeze actual extraction replies, bindings, parser outputs and all dependent bodies before at most 162 further automatic/parser numerical calls. No accepted claim means an explicit skipped job, no provider call. Rotate notes and paired arms for three rounds. Global faults stop. No retry, annotation lookup, post-result repair or threshold change.',
      'bindings':'Use only validated actual automatic fields with required selected probabilities >=0.70, plus union sentence quarantine. A malformed unused dimension blocks its sentence. Parser has no probabilities. Numerical verdict calls receive actual accepted bindings unchanged. Accepted wrong subjects, role, kind, polarity or channel/measure fail end-to-end scoring even with a coincidentally correct verdict.',
      'scoring':'Separate role, service, semantic binding, accepted correct/wrong claims, accepted nonclaims/review-only sentences, conditional verdicts, end-to-end correct claims, complete-six-note success, safe/unsafe displays, supported coverage, missing jobs, quarantine and actual costs per application/wording/round. Structured extraction is labeled supplied by construction; no fake extraction reply/probability. Preserve all six routable and twelve candidate denominators.',
      'gate':'Only automatic is the candidate. In every application/wording/round require complete calls, >=90% role/service/meaning/accepted-correct/end-to-end/whole-six coverage, zero accepted wrong binding or nonclaim/review-only item, zero unsafe displays and >=half reference-supported display coverage. Structured and parser are controls, not substitute candidates. Failure unlocks no protected data.',
      'limits':'The same assistant authored and inspected all notes and references. This measures fresh replies on inspected recordings, not authentic reports, independent review, user effort, anomaly detection, cause attribution or operational reliability.',
      'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
      'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [DATA/'inputs.json',DATA/'references.json',DATA/'manifest.json',ROOT/'checkpoints/assistant-review-decisions-2026-10-05.json',ROOT/'checkpoints/subject-robustness-results-2026-10-06.json']}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'maximum_calls':324,'maximum_answers':8262,'new_recordings':0}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='full-workflow-plan-1' or p['maximum_calls']!=324 or p['maximum_answers']!=8262:raise ValueError('Complete workflow budget changed.')
    for n,d in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=d:raise ValueError('Complete workflow source/evidence changed: '+n)
    return p


def bindings():
    rows,_=verified_rows('initial',complete=True);idx={(r['card_id'],r['arm'],r['round']):r for r in rows};refs={r['id']:r for r in load(DATA/'references.json')}
    return [{'card_id':p['id'],'arm':arm,'round':n,'bindings':extract(p,idx[(p['id'],'automatic',n)]) if arm=='automatic' else parser(p) if arm=='parser' else {sid:{**d,'accepted':bool(next(a['actionable'] for a in refs[p['id']]['annotations'] if a['id']==sid))} for i,(sid,d) in enumerate(annotated(p,refs[p['id']]).items())}}
       for n in (1,2,3) for p in load(DATA/'inputs.json') for arm in ARMS]


def requests(phase):
    check_plan();packets,records=check_reviews();record_index={r['note_id']:r for r in records}
    bound={(b['card_id'],b['arm'],b['round']):b['bindings'] for b in bindings()} if phase=='verdict' else {}
    jobs=[]
    for n in (1,2,3):
        shift=n-1
        for i,p in enumerate(packets[shift:]+packets[:shift]):
            arms=('automatic','structured') if phase=='initial' else ('automatic','parser')
            start=(i+shift)%2
            for arm in arms[start:]+arms[:start]:
                b=(extraction_request(p,'meaning') if arm=='automatic' else structured_body(p,record_index[p['id']],'clean_baseline')) if phase=='initial' else verdict_request(p,bound[(p['id'],arm,n)])
                jobs.append({'id':p['id']+'::full-workflow::'+phase+'::'+arm+'::r'+str(n),'card_id':p['id'],'phase':phase,'arm':arm,'round':n,'request_sha256':sha(encoded(b)) if b else None,'body':b})
    if phase not in ('initial','verdict') or len(jobs)!=162:raise ValueError('Complete workflow job budget changed.')
    return jobs


def freeze(phase):
    p=check_plan();jobs=requests(phase);largest=max((len(encoded(j['body'])) for j in jobs if j['body']),default=0)
    if largest>p['maximum_request_bytes']:raise ValueError('Complete workflow wire cap exceeded.')
    record={'schema':'full-workflow-protocol-1','phase':phase,'plan_sha256':sha(PLAN.read_bytes()),'planned_jobs':len(jobs),
      'planned_calls':sum(bool(j['body']) for j in jobs),'planned_answers':sum(len(j['body']['questions']) for j in jobs if j['body']),
      'largest_request_bytes':largest,'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    if phase=='verdict':record.update(bindings=bindings(),initial_summary_sha256=sha((output('initial')/'summary.json').read_bytes()))
    with protocol_path(phase).open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k not in ('bindings','requests')}


def check(phase):
    p=check_plan();path=protocol_path(phase);committed(path);record=load(path);jobs=requests(phase)
    if record['schema']!='full-workflow-protocol-1' or record['phase']!=phase or record['plan_sha256']!=sha(PLAN.read_bytes()):raise ValueError('Complete workflow protocol identity changed.')
    if record['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs]:raise ValueError('Complete workflow requests changed.')
    largest=max((len(encoded(j['body'])) for j in jobs if j['body']),default=0)
    if (record['planned_jobs'],record['planned_calls'],record['planned_answers'],record['largest_request_bytes'])!=(len(jobs),sum(bool(j['body']) for j in jobs),sum(len(j['body']['questions']) for j in jobs if j['body']),largest):raise ValueError('Complete workflow denominators changed.')
    if phase=='verdict' and (record['bindings']!=bindings() or record['initial_summary_sha256']!=sha((output('initial')/'summary.json').read_bytes())):raise ValueError('Actual dependent bindings changed.')
    return p,jobs

def run(phase, profile):
    p, planned = check(phase); profile_check(profile)
    if any(profile[k] != p[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Note profile changed.')
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
            print(f"Full workflow {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'full-workflow-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'full-workflow-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
        raise ValueError('Note hosted identity changed.')
    for name, digest in summary['files'].items():
        if sha((dest / name).read_bytes()) != digest:
            raise ValueError('Note hosted bytes changed.')
    if load(dest / 'requests.json') != planned:
        raise ValueError('Note saved requests changed.')
    rows = [json.loads(line) for line in (dest / 'responses.jsonl').read_text().splitlines()]
    if len(rows) > len(planned):
        raise ValueError('Extra note jobs.')
    for row, req in zip(rows, planned):
        if any(row.get(k) != v for k, v in req.items() if k != 'body') or row['status'] not in ('ok', 'ok_with_review', 'error', 'skipped_no_accepted_claims'):
            raise ValueError('Note response identity changed.')
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
        raise ValueError('Note hosted denominators changed.')
    if complete and (status != 'completed' or summary['stopped_reason']):
        raise ValueError('Complete note evidence required.')
    return rows, summary


def assess(packets,refs,bound,initial,verdict):
    if isinstance(refs,list):refs={r['id']:r for r in refs}
    bi={(b['card_id'],b['arm'],b['round']):b['bindings'] for b in bound};ir={(r['card_id'],r['arm'],r['round']):r for r in initial};vi={(r['card_id'],r['arm'],r['round']):r for r in verdict};outcomes=[];panels={}
    for p in packets:
        for arm in ARMS:
            for n in (1,2,3):
                er=ir.get((p['id'],'automatic',n)) if arm=='automatic' else None
                vr=(ir if arm=='structured' else vi).get((p['id'],arm,n),{});bindings_for_note=bi.get((p['id'],arm,n),{})
                for ref in refs[p['id']]['annotations']:
                    sid=ref['id'];b=bindings_for_note.get(sid,{});a=vr.get('answers',{}).get(sid+'_verdict')
                    eligible=bool(b.get('accepted'));quarantine=sid in vr.get('quarantined_sentences',[])
                    binding_correct=b.get('role')==ref['role'] and b.get('service')==ref['service'] and semantics(b)==semantics(ref)
                    correct=bool(ref['actionable'] and eligible and binding_correct and a and not quarantine and a['choice']==ref['verdict'])
                    display=bool(eligible and a and not quarantine and a['probabilities'][a['choice']]>=.70)
                    outcomes.append({'note_id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'arm':arm,'round':n,'sentence':sid,'actionable':ref['actionable'],
                      'role_correct':b.get('role')==ref['role'],'service_correct':b.get('service')==ref['service'],'meaning_correct':semantics(b)==semantics(ref),
                      'accepted':eligible,'binding_correct':binding_correct,'verdict_correct':bool(a and a['choice']==ref.get('verdict') and not quarantine),'choice':a['choice'] if a else 'unavailable',
                      'end_correct':correct,'displayed':display,'unsafe_displayed':display and not correct,'reference_supported':ref.get('verdict')=='supported',
                      'complete':bool(vr.get('status') in ('ok','ok_with_review','skipped_no_accepted_claims') and (arm!='automatic' or er and er['status'] in ('ok','ok_with_review'))),
                      'quarantined':quarantine or bool(er and sid in er.get('quarantined_sentences',[]))})
    for d in sorted({p['dataset'] for p in packets}):
        panels[d]={}
        for wording in ('all','plain','negated','boundary'):
            arms={}
            for arm in ARMS:
                rounds=[]
                for n in (1,2,3):
                    rr=[o for o in outcomes if o['dataset']==d and (wording=='all' or o['wording']==wording) and o['arm']==arm and o['round']==n];aa=[o for o in rr if o['actionable']];notes={o['note_id'] for o in rr}
                    m={'round':n,'candidate_denominator':len(rr),'claim_denominator':len(aa),'notes':len(notes),'role_correct':sum(o['role_correct'] for o in rr),
                      'service_correct':sum(o['service_correct'] for o in aa),'meaning_correct':sum(o['meaning_correct'] for o in aa),'accepted_correct':sum(o['accepted'] and o['binding_correct'] for o in aa),
                      'accepted_wrong':sum(o['accepted'] and not o['binding_correct'] for o in aa),'accepted_nonclaim_or_review':sum(o['accepted'] and not o['actionable'] for o in rr),
                      'conditional_verdict_total':sum(o['accepted'] and o['binding_correct'] for o in aa),'conditional_verdict_correct':sum(o['accepted'] and o['binding_correct'] and o['verdict_correct'] for o in aa),
                      'end_correct':sum(o['end_correct'] for o in aa),'safe_displayed':sum(o['displayed'] and o['end_correct'] for o in aa),'unsafe_displayed':sum(o['unsafe_displayed'] for o in rr),
                      'complete_six':sum(all(o['end_correct'] for o in aa if o['note_id']==identifier) for identifier in notes),'supported_denominator':sum(o['reference_supported'] for o in aa),
                      'supported_displayed':sum(o['reference_supported'] and o['displayed'] and o['end_correct'] for o in aa),'quarantined':sum(o['quarantined'] for o in rr),'complete':all(o['complete'] for o in rr)}
                    m['passes']=bool(m['complete'] and m['role_correct']/m['candidate_denominator']>=.9 and all(m[k]/m['claim_denominator']>=.9 for k in ('service_correct','meaning_correct','accepted_correct','end_correct')) and m['complete_six']/m['notes']>=.9 and not m['accepted_wrong'] and not m['accepted_nonclaim_or_review'] and not m['unsafe_displayed'] and m['supported_denominator'] and m['supported_displayed']>=m['supported_denominator']/2)
                    rounds.append(m)
                arms[arm]=rounds
            panels[d][wording]={'arms':arms,'candidate_passes':all(r['passes'] for r in arms['automatic'])}
    costs=[{'phase':phase,'arm':arm,'calls':sum(r['status']!='skipped_no_accepted_claims' for r in rows if r['arm']==arm),
      'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_ms':sum(r['latency_ms'] for r in rows if r['arm']==arm and r['status']!='skipped_no_accepted_claims')}
      for phase,rows in (('initial',initial),('verdict',verdict)) for arm in ARMS if any(r['arm']==arm for r in rows)]
    return {'panels':panels,'outcomes':outcomes,'costs':costs,'candidate_passes':all(p['candidate_passes'] for pp in panels.values() for p in pp.values())}


def score():
    initial,isummary=verified_rows('initial',complete=True);verdict,vsummary=verified_rows('verdict',complete=True);assigned=load(protocol_path('verdict'))['bindings']
    return {'schema':'full-workflow-results-1','actual_calls':isummary['attempted_calls']+vsummary['attempted_calls'],'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in initial+verdict),
      'valid_answers':sum(len(r.get('answers',{})) for r in initial+verdict),'human_reviews':0,'independent_reviews':0,'new_recordings':0,
      'initial_protocol_sha256':sha(protocol_path('initial').read_bytes()),'verdict_protocol_sha256':sha(protocol_path('verdict').read_bytes()),
      **assess(load(DATA/'inputs.json'),load(DATA/'references.json'),assigned,initial,verdict)}
