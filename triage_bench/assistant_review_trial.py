"""Once-only comparison on explicitly assistant-reviewed controlled notes."""
import copy
import json
import time
import urllib.error
import urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load, committed
from .hosted import encoded, redact
from .runner import NoRedirect, clean_api_key
from .profile import MODEL, profile_check
from .public_note_language_data import DATA
from .public_note_language_trial import SOURCES as OLD_SOURCES, RESULT as OLD_RESULT
from .public_note_features import accept, semantics, verdict_request
from .public_sentence_features import validate_reply, GlobalReplyError
from .claim_review import validate as validate_review, reviewed_request, fingerprint

REVIEWS = ROOT / 'checkpoints/assistant-review-decisions-2026-10-05.json'
PLAN = ROOT / 'checkpoints/assistant-review-plan-2026-10-05.json'
PROTOCOL = ROOT / 'checkpoints/assistant-review-protocol-2026-10-05.json'
RESULT = ROOT / 'checkpoints/assistant-review-results-2026-10-05.json'
OUT = ROOT / 'runs/assistant-review/hosted-2026-10-05-v1'
ARMS = ('bound_text', 'explicit_meaning')
SOURCES = OLD_SOURCES + ('triage_bench/claim_review.py', 'triage_bench/assistant_review_trial.py',
    'scripts/prepare_assistant_reviews.py', 'scripts/run_assistant_review.py')


def bindings(p, record):
    decisions = record['export']['reviews']
    return {c['id']: accept(p, decisions[c['id']]['values']) if decisions[c['id']]['decision']=='confirm'
        else {'accepted':False,'review_reason':'assistant_withheld'} for c in p['candidates']}


def body(p, record, arm):
    if arm == 'bound_text': return verdict_request(p, bindings(p,record))
    if arm != 'explicit_meaning': raise ValueError('Unknown assistant-review input.')
    request = reviewed_request(p, record['export']['reviews'])
    if request:
        for q in request['questions'].values():
            q['instructions'] = q['instructions'].replace('analyst-confirmed','assistant-reviewed').replace('The analyst confirmed','The assistant reviewed and selected')
    return request


def check_reviews():
    committed(REVIEWS); raw=load(REVIEWS)
    if raw['schema']!='assistant-review-decisions-1' or raw['human_review'] is not False or raw['independent_review'] is not False or raw['blinded'] is not False:
        raise ValueError('Assistant review provenance changed.')
    packets=load(DATA/'inputs.json'); records=raw['records']
    if len(records)!=27 or len({r['note_id'] for r in records})!=27 or {r['note_id'] for r in records}!={p['id'] for p in packets}:
        raise ValueError('Review note set changed.')
    by_id={p['id']:p for p in packets}
    for r in records:
        p=by_id[r['note_id']]; v=validate_review(r['export'])
        if r['dataset']!=p['dataset'] or r['wording']!=p['wording'] or r['note_sha256']!=sha(p['note'].encode()) or r['note_id']!=r['export']['note_id']:
            raise ValueError('Review note provenance changed.')
        if r['sentences'] != [{'id':c['id'],'text':c['text'],'decision':r['export']['reviews'][c['id']]} for c in p['candidates']] or len(v['confirmed'])!=6 or len(v['withheld'])!=6:
            raise ValueError('Full sentence review changed.')
    return packets,records


def plan(profile):
    profile_check(profile); fingerprint(); committed(REVIEWS)
    previous=load(ROOT/'checkpoints/public-note-language-plan-2026-10-05.json')
    if any(profile[k]!=previous[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'assistant-review-plan-1','authorization':'User asked to proceed without human decisions on 2026-10-05. Same-assistant diagnostic only.',
        'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':79840,
        'notes':27,'source_recordings':9,'sentence_decisions':324,'confirmed_claims':162,'human_reviews':0,'independent_reviews':0,
        'rounds':3,'arms':list(ARMS),'candidate':'explicit_meaning','maximum_calls':162,'maximum_answers':972,
        'task':'Judge six assistant-reviewed claims per note against unchanged service fact ledgers. Same notes/claims/services/measurements for both inputs. No extraction calls or fresh telemetry.',
        'comparison':'bound_text uses frozen sentence/service binding. explicit_meaning additionally supplies the reviewed kind/channel/measure/polarity and declares assistant authorship. This is a question-wording package, not an isolated kind-only causal effect.',
        'reference_policy':'Existing bounded numerical annotations, reopened only after review decisions were committed. Audit review/reference agreement before freezing exact requests; any mismatch stops, with no post-reference correction under this plan.',
        'execution':'Commit plan and new producers, then audit against existing references and commit exact rendered requests before 162 once-only calls. Rotate note/input order across three rounds. No retries, threshold fitting or repairs. Preserve malformed fields; access/envelope/model/context/network failure stops. An existing output directory prohibits another run.',
        'display':'Preserve verdict probability >=0.70; human/assistant confirmation is distinct from a model probability. No automatic extraction boundary is changed.',
        'gate':'In each application, wording and round require complete calls, every confirmed binding matching existing reference, every verdict correct, zero wrong displayed verdicts, >=90% displayed claim coverage and >=90% whole-six displayed notes. Explicit meaning must lose no correct verdict or correct display versus contemporary bound text. Passing authorizes no operational deployment or protected data.',
        'limits':'Same assistant wrote and previously inspected notes and annotations. This is a controlled workflow/input diagnostic, not independent validation, human equivalence, authentic-report extraction, reviewer effort, causal diagnosis or telecom readiness.',
        'sources':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [REVIEWS,OLD_RESULT,ROOT/'checkpoints/claim-review-workflow-2026-10-05.json',DATA/'inputs.json',DATA/'manifest.json']}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'status':'planned','maximum_calls':162,'human_reviews':0,'new_recordings':0}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='assistant-review-plan-1' or p['maximum_calls']!=162 or p['maximum_answers']!=972 or p['human_reviews']!=0:raise ValueError('Review task/budget changed.')
    for n,digest in {**p['sources'],**p['evidence']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Review source or evidence changed: '+n)
    return p


def audit():
    check_plan();packets,records=check_reviews();refs={r['id']:r for r in load(DATA/'references.json')};results=[]
    for p,r in zip(packets,records):
        if p['id']!=r['note_id']:raise ValueError('Review order changed.')
        bound=bindings(p,r); original=r['export']['proposal'];annotations=refs[p['id']]['annotations'];mismatches=[]
        for a in annotations:
            b=bound[a['id']]
            if bool(b['accepted'])!=bool(a['actionable']) or (b['accepted'] and (b['role']!=a['role'] or b['service']!=a['service'] or semantics(b)!=semantics(a))):
                mismatches.append(a['id'])
        v=validate_review(r['export'])
        corrected_relevant=[]
        for c in p['candidates']:
            b=bound[c['id']];old=original[c['id']]
            if b['accepted'] and (old.get('role')!=b['role'] or old.get('service')!=b['service'] or semantics(old)!=semantics(b)):
                corrected_relevant.append(c['id'])
        results.append({'note_id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'confirmed':len(v['confirmed']),
            'withheld':len(v['withheld']),'changed_field_sentences':len(v['corrections']), 'changed_relevant_bindings':corrected_relevant,
            'previously_withheld_confirmed':[c['id'] for c in p['candidates'] if bound[c['id']]['accepted'] and not original[c['id']]['accepted']],
            'reference_mismatches':mismatches})
    return {'reviewer':'assistant, same author','human_reviews':0,'independent_reviews':0,'notes':results,'reference_agreement':not any(r['reference_mismatches'] for r in results)}


def requests():
    check_plan();packets,records=check_reviews();indexed={r['note_id']:r for r in records};result=[]
    for n in (1,2,3):
        offset=n-1
        for i,p in enumerate(packets[offset:]+packets[:offset]):
            start=(i+offset)%2
            for arm in ARMS[start:]+ARMS[:start]:
                request=body(p,indexed[p['id']],arm)
                result.append({'id':p['id']+'::assistant-review::'+arm+'::r'+str(n),'card_id':p['id'],'arm':arm,'round':n,
                    'request_sha256':sha(encoded(request)),'body':request})
    return result


def freeze():
    p=check_plan();review_audit=audit()
    if not review_audit['reference_agreement']:raise ValueError('Review/reference mismatch: preserve decisions and stop before inference.')
    jobs=requests();largest=max(len(encoded(j['body'])) for j in jobs)
    if len(jobs)!=p['maximum_calls'] or sum(len(j['body']['questions']) for j in jobs)!=p['maximum_answers'] or largest>p['maximum_request_bytes']:
        raise ValueError('Review request budget or wire cap exceeded.')
    record={'schema':'assistant-review-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'reference_sha256':sha((DATA/'references.json').read_bytes()),
        'review_sha256':sha(REVIEWS.read_bytes()),'audit':review_audit,'planned_calls':len(jobs),'planned_answers':972,
        'largest_request_bytes':largest,'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    with PROTOCOL.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k not in ('requests','audit')}


def check():
    p=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL);jobs=requests()
    expected={'schema':'assistant-review-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'reference_sha256':sha((DATA/'references.json').read_bytes()),
        'review_sha256':sha(REVIEWS.read_bytes()),'audit':audit(),'planned_calls':len(jobs),'planned_answers':sum(len(j['body']['questions']) for j in jobs),
        'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}
    if protocol!=expected or not protocol['audit']['reference_agreement'] or protocol['planned_calls']!=162 or protocol['planned_answers']!=972 or protocol['largest_request_bytes']>p['maximum_request_bytes']:
        raise ValueError('Exact assistant-review protocol changed.')
    return p,jobs


def run(profile):
    p,jobs=check();profile_check(profile)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Review profile changed.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('Server-side key required.')
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.mkdir()
    (OUT/'requests.json').write_text(json.dumps(jobs,indent=2)+'\n');rows=[];reason=None
    opener=urllib.request.build_opener(NoRedirect())
    with (OUT/'responses.jsonl').open('x') as stream:
        for job in jobs:
            row={k:v for k,v in job.items() if k!='body'};start=time.perf_counter()
            try:
                request=urllib.request.Request(profile['endpoint'],data=encoded(job['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(request,timeout=30) as response:content=response.read(1048577)
                if len(content)>1048576:raise ValueError('Oversized response.')
                raw=json.loads(content);row['raw_response']=redact(raw,key)
                if not isinstance(raw,dict) or raw.get('model')!=MODEL:raise GlobalReplyError('checkpoint_mismatch')
                row.update(validate_reply(raw,job['body'],p['context_tokens']))
                tokens=row['usage'].get('input_tokens')
                if isinstance(tokens,bool) or not isinstance(tokens,int) or not 1<=tokens<=p['context_tokens']:raise GlobalReplyError('usage_or_context_failure')
            except urllib.error.HTTPError as error:
                reason='provider_http_'+str(error.code);row.update(status='error',error=reason);error.close()
            except (GlobalReplyError,OSError,ValueError,KeyError,TypeError) as error:
                reason='request_or_validation_failure';row.update(status='error',error=type(error).__name__)
            row=redact(row,key);row['latency_ms']=(time.perf_counter()-start)*1000;rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            print(f"Assistant review {len(rows)}/{len(jobs)} {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'assistant-review-hosted-1','planned_calls':len(jobs),'attempted_calls':len(rows),'failed':sum(r['status']=='error' for r in rows),
        'unattempted_calls':len(jobs)-len(rows),'status':'completed' if len(rows)==len(jobs) and not reason else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows():
    p,jobs=check();summary=load(OUT/'summary.json')
    if summary['schema']!='assistant-review-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Review run identity changed.')
    for n,digest in summary['files'].items():
        if sha((OUT/n).read_bytes())!=digest:raise ValueError('Review run file changed.')
    if load(OUT/'requests.json')!=jobs:raise ValueError('Review saved requests changed.')
    rows=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(jobs):raise ValueError('Extra review responses.')
    for r,j in zip(rows,jobs):
        if any(r.get(k)!=v for k,v in j.items() if k!='body') or r['status'] not in ('ok','ok_with_review','error'):raise ValueError('Review response identity changed.')
        if r['status']!='error':
            validated=validate_reply(r['raw_response'],j['body'],p['context_tokens'])
            if any(r.get(k)!=v for k,v in validated.items()):raise ValueError('Review normalized answer changed.')
        if isinstance(r.get('latency_ms'),bool) or not isinstance(r.get('latency_ms'),(float,int)) or r['latency_ms']<0:raise ValueError('Invalid recorded latency.')
    complete=len(rows)==len(jobs) and not any(r['status']=='error' for r in rows)
    if (summary['planned_calls'],summary['attempted_calls'],summary['failed'],summary['unattempted_calls'],summary['status'])!=(len(jobs),len(rows),sum(r['status']=='error' for r in rows),len(jobs)-len(rows),'completed' if complete else 'incomplete_or_failed'):
        raise ValueError('Review run denominators changed.')
    if not complete or summary['stopped_reason']:raise ValueError('Complete review calls required; preserve failure and stop.')
    return rows


def assess(packets,refs,rows):
    indexed={(r['card_id'],r['arm'],r['round']):r for r in rows};panels={};costs={}
    for wording in ('all','plain','negated','boundary'):
        panels[wording]={}
        for dataset in sorted({p['dataset'] for p in packets}):
            selected=[p for p in packets if p['dataset']==dataset and (wording=='all' or p['wording']==wording)];arms={};passes=[]
            for arm in ARMS:
                metrics=[]
                for n in (1,2,3):
                    outcomes=[];complete=True;whole=0
                    for p in selected:
                        row=indexed.get((p['id'],arm,n),{});complete=complete and row.get('status') in ('ok','ok_with_review');note=[]
                        for a in refs[p['id']]['annotations']:
                            if not a['actionable']:continue
                            answer=row.get('answers',{}).get(a['id']+'_verdict');correct=bool(answer and answer['choice']==a['verdict']);shown=bool(answer and answer['probabilities'][answer['choice']]>=.70)
                            note.append({'note_id':p['id'],'sentence':a['id'],'reference':a['verdict'],'choice':answer['choice'] if answer else 'unavailable',
                                'correct':correct,'displayed':shown,'wrong_displayed':shown and not correct})
                        outcomes+=note;whole+=int(all(o['correct'] and o['displayed'] for o in note))
                    metrics.append({'round':n,'complete':complete,'denominator':len(selected)*6,'correct':sum(o['correct'] for o in outcomes),
                        'correct_displayed':sum(o['correct'] and o['displayed'] for o in outcomes),'wrong_displayed':sum(o['wrong_displayed'] for o in outcomes),
                        'whole_notes_displayed':whole,'notes':len(selected),'outcomes':outcomes})
                arms[arm]=metrics
            for a,b in zip(arms['bound_text'],arms['explicit_meaning']):
                passes.append(bool(b['complete'] and b['correct']==b['denominator'] and b['wrong_displayed']==0 and b['correct_displayed']/b['denominator']>=.9 and b['whole_notes_displayed']/b['notes']>=.9 and b['correct']>=a['correct'] and b['correct_displayed']>=a['correct_displayed']))
            panels[wording][dataset]={'arms':arms,'candidate_passes_by_round':passes,'candidate_passes':all(passes)}
    for arm in ARMS:
        rr=[r for r in rows if r['arm']==arm];costs[arm]={'calls':len(rr),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rr),'summed_latency_seconds':sum(r['latency_ms'] for r in rr)/1000}
    return {'panels':panels,'candidate_passes':all(p['candidate_passes'] for group in panels.values() for p in group.values()),'costs':costs}


def score():
    rows=verified_rows();packets,_=check_reviews();refs={r['id']:r for r in load(DATA/'references.json')};assessment=assess(packets,refs,rows)
    return {'schema':'assistant-review-results-1','reviewer':'assistant, same author','human_reviews':0,'independent_reviews':0,
        'calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),
        'valid_answers':sum(len(r.get('answers',{})) for r in rows),'audit':audit(),**assessment,
        'new_recordings':0,'protocol_sha256':sha(PROTOCOL.read_bytes()),'run_summary_sha256':sha((OUT/'summary.json').read_bytes())}
