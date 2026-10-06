"""Prospective text-only subject check with separate numerical verdict calls."""
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
from .subject_check_trial import SOURCES as OLD_SOURCES, body as joint_body, decisions as old_decisions, references as original_references, decision as joint_decision

PLAN=ROOT/'checkpoints/separate-subject-plan-2026-10-05.json'
PROTOCOL=ROOT/'checkpoints/separate-subject-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/separate-subject-results-2026-10-05.json'
OUT=ROOT/'runs/separate-subject/hosted-2026-10-05-v1'
ARMS=('clean_baseline','wrong_baseline','clean_joint','wrong_joint','clean_checked','wrong_checked')
SUBJECT_PROTOCOL=ROOT/'checkpoints/separate-subject-text-protocol-2026-10-05.json'
VERDICT_PROTOCOL=ROOT/'checkpoints/separate-subject-verdict-protocol-2026-10-05.json'
SOURCES=OLD_SOURCES+('triage_bench/separate_subject_trial.py','scripts/run_separate_subject.py')


def decisions(record,arm):
    if arm not in ARMS:raise ValueError('Unknown separate-subject input.')
    return old_decisions(record,'wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline')


def body(p,record,arm):
    if arm not in ARMS:raise ValueError('Unknown separate-subject input.')
    if arm.endswith('baseline'):return joint_body(p,record,arm)
    request=joint_body(p,record,('wrong_' if arm.startswith('wrong_') else 'clean_')+'checked')
    if arm.endswith('joint'):return request
    return {**request,'state':json.dumps({'note':p['note']},separators=(',',':')),
        'questions':{k:v for k,v in request['questions'].items() if k.endswith('_subject')}}


def plan(profile):
    profile_check(profile);check_reviews();old=load(ROOT/'checkpoints/subject-check-plan-2026-10-05.json')
    if any(profile[k]!=old[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'separate-subject-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'authorization':'User authorized the recommended separate text-only subject diagnostic on 2026-10-05.',
        'notes':27,'source_recordings':9,'rounds':3,'claims_per_note':6,'arms':list(ARMS),'candidate':'checked',
        'maximum_calls':486,'maximum_answers':3888,'maximum_request_bytes':79840,
        'inputs':'Fresh clean/wrong exact verdict baselines, fresh clean/wrong exact joint requests, and clean/wrong text-only subject requests. Text-only retains the previous joint subject questions verbatim but removes numerical ledgers and verdict questions. Full original note and each proposed service remain. No new notes, altered measurements, meaning or polarity.',
        'phases':'Commit plan/producers before preparation, then separate exact text/joint and verdict phase protocols before inference. First 324 text/joint calls yield 2916 answers. All 162 verdict calls then run regardless of subject decisions, yielding 972 answers. These verdict bodies do not depend on subject results. No request is conditionally skipped or rebound.',
        'reference_policy':'Reuse committed original numerical verdicts and assistant-reviewed service annotations. Clean subject references matched; every swapped subject conflict even with an invariant verdict. No reference enters any request.',
        'display':'Baseline verdict probability >=0.70. Joint additionally matched subject probability >=0.70. Separate combines its text-only subject with its corresponding contemporary baseline verdict, retaining the supplied service and both >=0.70 gates. Any invalid field quarantines its sentence in that call; union quarantine across the two calls blocks composition. Missing calls/answers never produce display.',
        'score':'Full planned denominators for independent subject and original-verdict accuracy, safe displays, unsafe displays (wrong supplied subject OR wrong original verdict), wrong-verdict displays, withholding, named/pronoun strata and paired gains/losses. Report each application/style/round, baseline and contemporary joint comparator separately. Costs count actual calls; composed workflow adds baseline and text-only calls, not duplicated inference.',
        'gate':'In every application/style/round require complete calls, every clean/corrupt subject correct, every clean verdict correct, no safe clean display loss against contemporary baseline and >=90% clean claim coverage. Corrupt inputs must display zero unsafe guidance and strictly fewer wrong verdicts than wrong baseline. Evaluate joint under the same criteria as a diagnostic comparator; it cannot substitute as candidate. No operational or protected-data promotion.',
        'execution':'486 once-only calls, no retries, post-result repairs, threshold search or fresh telemetry. Rotate four text/joint arms and notes over three rounds, then rotate two verdict arms and notes. Existing output directory blocks rerun; global identity/envelope/usage/context/network failure stops both phases.',
        'limits':'Same assistant authored and inspected controlled notes and references; zero human/independent reviews. All confirmed subjects uniquely resolve; unresolved cases and authentic reports untested. Splitting also removes verdict questions from subject context and retains authoritative verdict wording. This package does not isolate ledger removal alone or demonstrate independent reviewer reliability. Clean/wrong verdict replies are deliberately shared with baseline scoring; statistical independence is not claimed. No source-service repair, fresh incidents or analyst usefulness measurement.',
        'sources':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (REVIEWS,DATA/'inputs.json',DATA/'manifest.json',ROOT/'checkpoints/subject-check-results-2026-10-05.json')}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'status':'planned','maximum_calls':486,'maximum_answers':3888,'new_recordings':0}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='separate-subject-plan-1' or p['maximum_calls']!=486 or p['maximum_answers']!=3888 or p['arms']!=list(ARMS):raise ValueError('Separate-subject task/budget changed.')
    for n,digest in {**p['sources'],**p['evidence']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Separate-subject source/evidence changed: '+n)
    return p


def references():
    check_plan();return original_references()


def requests():
    check_plan();packets,records=check_reviews();index={r['note_id']:r for r in records};jobs=[]
    for phase,arms in (('text',('clean_joint','wrong_joint','clean_checked','wrong_checked')),('verdict',('clean_baseline','wrong_baseline'))):
        for n in (1,2,3):
            offset=n-1
            for i,p in enumerate(packets[offset:]+packets[:offset]):
                start=(i+offset)%len(arms)
                for arm in arms[start:]+arms[:start]:
                    request=body(p,index[p['id']],arm)
                    jobs.append({'id':p['id']+'::separate-subject::'+arm+'::r'+str(n),'card_id':p['id'],'arm':arm,'phase':phase,'round':n,'request_sha256':sha(encoded(request)),'body':request})
    return jobs


def phase_protocol(phase):
    jobs=[j for j in requests() if j['phase']==phase]
    return {'schema':'separate-subject-phase-1','phase':phase,'plan_sha256':sha(PLAN.read_bytes()),'reference_sha256':sha((DATA/'references.json').read_bytes()),
        'references':references(),'planned_calls':len(jobs),'planned_answers':sum(len(j['body']['questions']) for j in jobs),
        'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}


def expected_protocol():
    return {'schema':'separate-subject-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'references':references(),
        'planned_calls':486,'planned_answers':3888,'phases':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (SUBJECT_PROTOCOL,VERDICT_PROTOCOL)}}


def freeze():
    p=check_plan()
    for phase,path,calls,answers in (('text',SUBJECT_PROTOCOL,324,2916),('verdict',VERDICT_PROTOCOL,162,972)):
        r=phase_protocol(phase)
        if r['planned_calls']!=calls or r['planned_answers']!=answers or r['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Separate-subject wire cap/budget exceeded.')
        with path.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    record=expected_protocol()
    with PROTOCOL.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k!='references'}


def check():
    p=check_plan();committed(PROTOCOL)
    for phase,path in (('text',SUBJECT_PROTOCOL),('verdict',VERDICT_PROTOCOL)):
        committed(path)
        if load(path)!=phase_protocol(phase):raise ValueError('Exact separate-subject phase changed.')
    if load(PROTOCOL)!=expected_protocol():raise ValueError('Exact separate-subject protocol changed.')
    return p,requests()


def run(profile):
    p,jobs=check();profile_check(profile)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Separate subject profile changed.')
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
            print(f"Separate subject {len(rows)}/{len(jobs)} {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'separate-subject-hosted-1','planned_calls':len(jobs),'attempted_calls':len(rows),'failed':sum(r['status']=='error' for r in rows),
        'unattempted_calls':len(jobs)-len(rows),'status':'completed' if len(rows)==len(jobs) and not reason else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows():
    p,jobs=check();summary=load(OUT/'summary.json')
    if summary['schema']!='separate-subject-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Separate subject run identity changed.')
    for n,digest in summary['files'].items():
        if sha((OUT/n).read_bytes())!=digest:raise ValueError('Separate subject run file changed.')
    if load(OUT/'requests.json')!=jobs:raise ValueError('Separate subject saved requests changed.')
    rows=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(jobs):raise ValueError('Extra review responses.')
    for r,j in zip(rows,jobs):
        if any(r.get(k)!=v for k,v in j.items() if k!='body') or r['status'] not in ('ok','ok_with_review','error'):raise ValueError('Separate subject response identity changed.')
        if r['status']!='error':
            validated=validate_reply(r['raw_response'],j['body'],p['context_tokens'])
            if any(r.get(k)!=v for k,v in validated.items()):raise ValueError('Separate subject normalized answer changed.')
        if isinstance(r.get('latency_ms'),bool) or not isinstance(r.get('latency_ms'),(float,int)) or r['latency_ms']<0:raise ValueError('Invalid recorded latency.')
    complete=len(rows)==len(jobs) and not any(r['status']=='error' for r in rows)
    if (summary['planned_calls'],summary['attempted_calls'],summary['failed'],summary['unattempted_calls'],summary['status'])!=(len(jobs),len(rows),sum(r['status']=='error' for r in rows),len(jobs)-len(rows),'completed' if complete else 'incomplete_or_failed'):
        raise ValueError('Separate subject run denominators changed.')
    if not complete or summary['stopped_reason']:raise ValueError('Complete review calls required; preserve failure and stop.')
    return rows


def composed_row(index,note,arm,n):
    row=copy.deepcopy(index.get((note,arm,n),{}))
    if not arm.endswith('checked'):return row
    v=index.get((note,'wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline',n),{})
    row['answers']={**row.get('answers',{}),**v.get('answers',{})}
    row['quarantined_sentences']=sorted(set(row.get('quarantined_sentences',[]))|set(v.get('quarantined_sentences',[])))
    valid=all(r.get('status') in ('ok','ok_with_review') for r in (row,v))
    row['status']='ok_with_review' if valid and row['quarantined_sentences'] else 'ok' if valid else 'error'
    row['source_call_ids']=[row.get('id'),v.get('id')]
    return row


def decision(row,sid,checked):
    return joint_decision(row,sid,checked)


def assess(packets,refs,rows):
    index={(r['card_id'],r['arm'],r['round']):r for r in rows};outcomes=[];panels={}
    for p in packets:
        for arm in ARMS:
            checked=not arm.endswith('baseline');wrong=arm.startswith('wrong_')
            for n in (1,2,3):
                row=composed_row(index,p['id'],arm,n)
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
            gates={}
            for approach in ('checked','joint'):
                passes=[]
                for i in range(3):
                    c=arms['clean_'+approach][i]['strata']['all'];w=arms['wrong_'+approach][i]['strata']['all'];b=arms['clean_baseline'][i]['strata']['all'];wb=arms['wrong_baseline'][i]['strata']['all']
                    passes.append(bool(c['complete'] and w['complete'] and b['complete'] and wb['complete'] and c['subject_correct']==c['denominator'] and w['subject_correct']==w['denominator'] and c['correct']==c['denominator'] and c['correct_safe_displayed']>=b['correct_safe_displayed'] and c['correct_safe_displayed']/c['denominator']>=.9 and w['unsafe_displayed']==0 and w['wrong_verdict_displayed']<wb['wrong_verdict_displayed']))
                gates[approach]=passes
            panels[dataset][wording]={'arms':arms,'candidate_passes_by_round':gates['checked'],'candidate_passes':all(gates['checked']),'joint_passes_by_round':gates['joint'],'joint_passes':all(gates['joint'])}
    costs={arm:{'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_seconds':sum(r['latency_ms'] for r in rows if r['arm']==arm)/1000} for arm in ARMS}
    workflow_costs={a:{k:costs[a][k]+(costs['wrong_baseline' if a.startswith('wrong_') else 'clean_baseline'][k] if a.endswith('checked') else 0) for k in costs[a]} for a in ARMS}
    return {'workflow_costs':workflow_costs,'panels':panels,'outcomes':outcomes,'candidate_passes':all(p['candidate_passes'] for pp in panels.values() for p in pp.values()),'costs':costs}


def score():
    rows=verified_rows();packets,_=check_reviews();assessment=assess(packets,references(),rows)
    return {'schema':'separate-subject-results-1','calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),
        'valid_answers':sum(len(r.get('answers',{})) for r in rows),'human_reviews':0,'independent_reviews':0,'new_recordings':0,
        'protocol_sha256':sha(PROTOCOL.read_bytes()),'run_summary_sha256':sha((OUT/'summary.json').read_bytes()),**assessment}
