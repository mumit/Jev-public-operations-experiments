"""Prospective subject-conflict check on inspected controlled notes."""
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
from .public_sentence_features import validate_reply, GlobalReplyError
from .assistant_review_trial import REVIEWS, check_reviews
from .binding_corruption_trial import SOURCES as OLD_SOURCES, body as prior_body, altered

PLAN=ROOT/'checkpoints/subject-check-plan-2026-10-05.json'
PROTOCOL=ROOT/'checkpoints/subject-check-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/subject-check-results-2026-10-05.json'
OUT=ROOT/'runs/subject-check/hosted-2026-10-05-v1'
ARMS=('clean_baseline','wrong_baseline','clean_checked','wrong_checked')
SOURCES=OLD_SOURCES+('triage_bench/subject_check_trial.py','scripts/run_subject_check.py')


def decisions(record,arm):
    if arm not in ARMS:raise ValueError('Unknown subject-check input.')
    return altered(record,'service_bound' if arm.startswith('wrong_') else 'clean_bound')['export']['reviews']


def body(p,record,arm):
    decision=decisions(record,arm)
    request=prior_body(p,record,'service_bound' if arm.startswith('wrong_') else 'clean_bound')
    if arm.endswith('baseline'):return request
    questions={}
    for c in p['candidates']:
        d=decision[c['id']]
        if d['decision']!='confirm':continue
        service=d['values']['service'];sid=c['id'];old=request['questions'][sid+'_verdict']
        prefix=old['instructions'].split('Assess only the exact statement bound to service ')[0]
        questions[sid+'_subject']={'type':'choice','instructions':
            'Check the proposed service binding against the EXACT sentence in the full note context. '
            'The proposal may be incorrect. Identify the endorsed assertion subject from the note itself, not from this proposal or the measurements. '
            'Resolve a pronoun only from an unambiguous antecedent in the note; a request to check a service can introduce that service as an antecedent. '
            'Select matched only when the note uniquely identifies the proposed service as the subject; conflict when it uniquely identifies a different service; '
            'unresolved when the subject is not unique or the sentence is not one endorsed assertion. Do not infer incident causality or service health. '
            f'Proposed service: {service}. Exact sentence: '+c['text'],
            'criteria':{'matched':'The unique subject in the note is the proposed service.','conflict':'The unique subject in the note is a different service.','unresolved':'The note does not identify one endorsed assertion with a unique subject.'}}
        questions[sid+'_verdict']={'type':'choice','instructions':prefix+
            'Assess the exact ORIGINAL sentence in the full note context. '
            f'The proposed service binding is {service}; it may be incorrect. '
            'Identify the subject from the note itself, not the proposal. Use the facts for that subject to judge the original sentence. '
            'Do not reinterpret the sentence as about a different service. If the note does not identify a unique subject, choose unanswerable. '
            'The subject check is a separate question; do not use conflict as a substitute for an evidence verdict. Exact original sentence: '+c['text'],
            'criteria':copy.deepcopy(old['criteria'])}
    return {**request,'questions':questions}


def plan(profile):
    profile_check(profile);check_reviews();old=load(ROOT/'checkpoints/binding-corruption-plan-2026-10-05.json')
    if any(profile[k]!=old[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'subject-check-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'authorization':'User selected the recommended explicit subject-conflict check on 2026-10-05.',
        'notes':27,'source_recordings':9,'rounds':3,'claims_per_note':6,'arms':list(ARMS),'candidate':'checked','maximum_calls':324,'maximum_answers':2916,'maximum_request_bytes':79840,
        'inputs':'Two exact contemporary sentence/service baselines, clean and bijectively swapped services. Two checked inputs add six independent subject questions and rewrite six verdict instructions to judge original text rather than trust the proposal. Same six claims, full note, both service ledgers and numerical policy; no polarity corruption.',
        'task':'matched/conflict/unresolved checks use the full note, ignoring telemetry as a source of subject identity. Verdicts assess original sentences independently. Application composition never changes a supplied service or accepts a hidden replacement.',
        'reference_policy':'After committing this plan, reuse original numerical verdicts and reviewed service annotations. All six checked clean subjects are matched; swapped subjects are conflict even when their numerical verdict would be invariant. Verify the old reviewed subjects against annotations before freezing. No reference enters a request.',
        'display':'Baseline displays selected-verdict probability >=0.70. Checked display additionally requires subject=matched and selected-subject probability >=0.70. Any invalid field quarantines both decisions for its sentence; preserve valid siblings and raw inconsistent choices. Missing probabilities or questions never produce display.',
        'score':'Full planned denominators for subject correctness, verdict correctness, correct safe display, unsafe display, wrong-verdict display and withholding. Unsafe means wrong supplied subject OR wrong original verdict. Report application/style/round and named/pronoun subjects, plus losses/gains versus fresh matched baseline. All corrupted bindings are unsafe even when verdicts coincide.',
        'gate':'In every application/style/round require complete calls, every clean and corrupted subject classification correct, clean verdicts all correct with no loss of correct safe display against contemporary clean baseline and >=90% clean claim coverage. Require zero unsafe corrupted displays and fewer wrong-verdict displays than contemporary wrong baseline. Passing authorizes only a diagnostic candidate on inspected notes, not protected data or operational deployment.',
        'execution':'Commit plan/producers before preparation, then exact request/reference fingerprints before 324 once-only calls. Rotate note and arm orders over three rounds. No retries, repairs, threshold search, fresh data or post-result input changes. Existing output directory prohibits rerun; global identity/envelope/usage/context/network failure stops.',
        'limits':'Same author wrote and previously inspected the notes and annotations. Zero human or independent reviews. Only uniquely resolvable confirmed assertions are called, so unresolved-subject recognition and authentic reports are not evaluated. Controlled all-six subject swaps are not organic error rates. The checked request is a wording-and-question package, not an isolated extra-question effect. No source-service repair or analyst usefulness measurement.',
        'sources':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (REVIEWS,DATA/'inputs.json',DATA/'manifest.json',ROOT/'checkpoints/binding-corruption-results-2026-10-05.json')}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'status':'planned','maximum_calls':324,'maximum_answers':2916,'new_recordings':0}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='subject-check-plan-1' or p['maximum_calls']!=324 or p['maximum_answers']!=2916 or p['arms']!=list(ARMS):raise ValueError('Subject-check task/budget changed.')
    for n,digest in {**p['sources'],**p['evidence']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Subject-check source/evidence changed: '+n)
    return p


def references():
    check_plan();packets,records=check_reviews();old={r['id']:r for r in load(DATA/'references.json')};refs={}
    for p,r in zip(packets,records):
        if p['id']!=r['note_id']:raise ValueError('Review order changed.')
        refs[p['id']]={}
        for a in old[p['id']]['annotations']:
            if not a['actionable']:continue
            v=r['export']['reviews'][a['id']]
            if v['decision']!='confirm' or v['values']['service']!=a['service']:raise ValueError('Original subject annotation mismatch.')
            refs[p['id']][a['id']]={'verdict':a['verdict'],'service':a['service'],'subject_form':'direct_name' if a['service'] in a['text'] else 'pronoun'}
    return refs


def requests():
    check_plan();packets,records=check_reviews();index={r['note_id']:r for r in records};jobs=[]
    for n in (1,2,3):
        offset=n-1
        for i,p in enumerate(packets[offset:]+packets[:offset]):
            start=(i+offset)%len(ARMS)
            for arm in ARMS[start:]+ARMS[:start]:
                request=body(p,index[p['id']],arm)
                jobs.append({'id':p['id']+'::subject-check::'+arm+'::r'+str(n),'card_id':p['id'],'arm':arm,'round':n,'request_sha256':sha(encoded(request)),'body':request})
    return jobs


def expected_protocol():
    jobs=requests()
    return {'schema':'subject-check-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'reference_sha256':sha((DATA/'references.json').read_bytes()),
        'references':references(),'planned_calls':len(jobs),'planned_answers':sum(len(j['body']['questions']) for j in jobs),
        'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}


def freeze():
    p=check_plan();record=expected_protocol()
    if record['planned_calls']!=324 or record['planned_answers']!=2916 or record['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Subject-check wire cap/budget exceeded.')
    with PROTOCOL.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k not in ('requests','references')}


def check():
    p=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL)
    if protocol!=expected_protocol() or protocol['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Exact subject-check protocol changed.')
    return p,requests()


def run(profile):
    p,jobs=check();profile_check(profile)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Subject check profile changed.')
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
            print(f"Subject check {len(rows)}/{len(jobs)} {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'subject-check-hosted-1','planned_calls':len(jobs),'attempted_calls':len(rows),'failed':sum(r['status']=='error' for r in rows),
        'unattempted_calls':len(jobs)-len(rows),'status':'completed' if len(rows)==len(jobs) and not reason else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows():
    p,jobs=check();summary=load(OUT/'summary.json')
    if summary['schema']!='subject-check-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Subject check run identity changed.')
    for n,digest in summary['files'].items():
        if sha((OUT/n).read_bytes())!=digest:raise ValueError('Subject check run file changed.')
    if load(OUT/'requests.json')!=jobs:raise ValueError('Subject check saved requests changed.')
    rows=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(jobs):raise ValueError('Extra review responses.')
    for r,j in zip(rows,jobs):
        if any(r.get(k)!=v for k,v in j.items() if k!='body') or r['status'] not in ('ok','ok_with_review','error'):raise ValueError('Subject check response identity changed.')
        if r['status']!='error':
            validated=validate_reply(r['raw_response'],j['body'],p['context_tokens'])
            if any(r.get(k)!=v for k,v in validated.items()):raise ValueError('Subject check normalized answer changed.')
        if isinstance(r.get('latency_ms'),bool) or not isinstance(r.get('latency_ms'),(float,int)) or r['latency_ms']<0:raise ValueError('Invalid recorded latency.')
    complete=len(rows)==len(jobs) and not any(r['status']=='error' for r in rows)
    if (summary['planned_calls'],summary['attempted_calls'],summary['failed'],summary['unattempted_calls'],summary['status'])!=(len(jobs),len(rows),sum(r['status']=='error' for r in rows),len(jobs)-len(rows),'completed' if complete else 'incomplete_or_failed'):
        raise ValueError('Subject check run denominators changed.')
    if not complete or summary['stopped_reason']:raise ValueError('Complete review calls required; preserve failure and stop.')
    return rows


def decision(row,sid,checked):
    answers=row.get('answers',{});v=answers.get(sid+'_verdict');subject=answers.get(sid+'_subject') if checked else None
    quarantined=sid in row.get('quarantined_sentences',[])
    eligible=not quarantined and row.get('status') in ('ok','ok_with_review')
    shown=bool(eligible and v and v['probabilities'][v['choice']]>=.70 and (not checked or subject and subject['choice']=='matched' and subject['probabilities'][subject['choice']]>=.70))
    return {'verdict':v['choice'] if eligible and v else 'unavailable','subject':subject['choice'] if eligible and subject else 'unavailable','displayed':shown,'quarantined':quarantined}


def assess(packets,refs,rows):
    index={(r['card_id'],r['arm'],r['round']):r for r in rows};outcomes=[];panels={}
    for p in packets:
        for arm in ARMS:
            checked=arm.endswith('checked');wrong=arm.startswith('wrong_')
            for n in (1,2,3):
                row=index.get((p['id'],arm,n),{})
                for sid,ref in refs[p['id']].items():
                    d=decision(row,sid,checked);control=decision(index.get((p['id'],'wrong_baseline' if wrong else 'clean_baseline',n),{}),sid,False)
                    correct=d['verdict']==ref['verdict'];safe=not wrong and correct
                    outcomes.append({'note_id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'arm':arm,'round':n,'sentence':sid,'reference':ref['verdict'],
                        'subject_reference':'conflict' if wrong else 'matched','subject_form':ref['subject_form'],**d,
                        'subject_correct':checked and d['subject']==('conflict' if wrong else 'matched'),'correct':correct,'safe':safe,
                        'unsafe_displayed':d['displayed'] and not safe,'wrong_verdict_displayed':d['displayed'] and not correct,
                        'control_correct':control['verdict']==ref['verdict'],'control_safe_displayed':control['displayed'] and not wrong and control['verdict']==ref['verdict'],
                        'complete':row.get('status') in ('ok','ok_with_review')})
    for dataset in sorted({p['dataset'] for p in packets}):
        panels[dataset]={}
        for wording in ('all','plain','negated','boundary'):
            arms={}
            for arm in ARMS:
                rounds=[]
                for n in (1,2,3):
                    rr=[o for o in outcomes if o['dataset']==dataset and (wording=='all' or o['wording']==wording) and o['arm']==arm and o['round']==n];strata={}
                    for name in ('all','direct_name','pronoun'):
                        selected=[o for o in rr if name=='all' or o['subject_form']==name]
                        strata[name]={'denominator':len(selected),'correct':sum(o['correct'] for o in selected),'subject_correct':sum(o['subject_correct'] for o in selected),
                            'correct_safe_displayed':sum(o['safe'] and o['displayed'] for o in selected),'unsafe_displayed':sum(o['unsafe_displayed'] for o in selected),
                            'wrong_verdict_displayed':sum(o['wrong_verdict_displayed'] for o in selected),'withheld':sum(not o['displayed'] for o in selected),
                            'quarantined':sum(o['quarantined'] for o in selected),'losses':sum(o['control_correct'] and not o['correct'] for o in selected),'gains':sum(not o['control_correct'] and o['correct'] for o in selected),
                            'safe_display_losses':sum(o['control_safe_displayed'] and not (o['safe'] and o['displayed']) for o in selected),'complete':all(o['complete'] for o in selected)}
                    rounds.append({'round':n,'strata':strata})
                arms[arm]=rounds
            passes=[]
            for i in range(3):
                c=arms['clean_checked'][i]['strata']['all'];w=arms['wrong_checked'][i]['strata']['all'];b=arms['clean_baseline'][i]['strata']['all'];wb=arms['wrong_baseline'][i]['strata']['all']
                passes.append(bool(c['complete'] and w['complete'] and b['complete'] and wb['complete'] and c['subject_correct']==c['denominator'] and w['subject_correct']==w['denominator'] and c['correct']==c['denominator'] and c['correct_safe_displayed']>=b['correct_safe_displayed'] and c['correct_safe_displayed']/c['denominator']>=.9 and w['unsafe_displayed']==0 and w['wrong_verdict_displayed']<wb['wrong_verdict_displayed']))
            panels[dataset][wording]={'arms':arms,'candidate_passes_by_round':passes,'candidate_passes':all(passes)}
    costs={arm:{'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_seconds':sum(r['latency_ms'] for r in rows if r['arm']==arm)/1000} for arm in ARMS}
    return {'panels':panels,'outcomes':outcomes,'candidate_passes':all(p['candidate_passes'] for pp in panels.values() for p in pp.values()),'costs':costs}


def score():
    rows=verified_rows();packets,_=check_reviews();assessment=assess(packets,references(),rows)
    return {'schema':'subject-check-results-1','calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),
        'valid_answers':sum(len(r.get('answers',{})) for r in rows),'human_reviews':0,'independent_reviews':0,'new_recordings':0,
        'protocol_sha256':sha(PROTOCOL.read_bytes()),'run_summary_sha256':sha((OUT/'summary.json').read_bytes()),**assessment}
