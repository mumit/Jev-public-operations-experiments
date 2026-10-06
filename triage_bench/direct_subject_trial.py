"""Prospective actual-subject extraction without a proposed binding."""
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
from .separate_subject_trial import SOURCES as OLD_SOURCES, body as prior_body, decisions as old_decisions, references as original_references

PLAN=ROOT/'checkpoints/direct-subject-plan-2026-10-05.json'
PROTOCOL=ROOT/'checkpoints/direct-subject-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/direct-subject-results-2026-10-05.json'
OUT=ROOT/'runs/direct-subject/hosted-2026-10-05-v1'
ARMS=('clean_baseline','wrong_baseline','clean_checked','wrong_checked','clean_direct','wrong_direct')
CALL_ARMS=('direct_subject','clean_checked','wrong_checked','clean_baseline','wrong_baseline')
SUBJECT_PROTOCOL=ROOT/'checkpoints/direct-subject-text-protocol-2026-10-05.json'
VERDICT_PROTOCOL=ROOT/'checkpoints/direct-subject-verdict-protocol-2026-10-05.json'
SOURCES=OLD_SOURCES+('triage_bench/direct_subject_trial.py','scripts/run_direct_subject.py')


def decisions(record,arm):
    if arm not in ARMS:raise ValueError('Unknown direct-subject input.')
    return old_decisions(record,'wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline')


def body(p,record,arm):
    if arm in ('clean_baseline','wrong_baseline','clean_checked','wrong_checked'):
        return prior_body(p,record,arm)
    if arm!='direct_subject':raise ValueError('Unknown direct-subject call.')
    # Inventory comes from observed inputs, never reviewed subject answers.
    services=list(p['services'])
    if len(services)!=len(set(services)) or 'unresolved' in services:raise ValueError('Invalid observed inventory.')
    questions={}
    for c in p['candidates']:
        if record['export']['reviews'][c['id']]['decision']!='confirm':continue
        questions[c['id']+'_subject']={'type':'choice','instructions':
            'Identify the subject of the EXACT sentence in the full note context. '
            'Select the observed service that the note uniquely identifies as the subject of this endorsed assertion. '
            'Resolve a pronoun only from an unambiguous antecedent in the note; a request to check a service can introduce that service as an antecedent. '
            'Select unresolved when the subject is not unique, is outside the observed inventory, or the sentence is not one endorsed assertion. '
            'Use only the note, not service health or incident causality. Exact sentence: '+c['text'],
            'criteria':{**{service:'The unique assertion subject in the note is '+service+'.' for service in services},
                'unresolved':'The note does not identify one endorsed assertion with a unique observed service.'}}
    return {'model':MODEL,'state':json.dumps({'note':p['note'],'observed_services':services},separators=(',',':')),'questions':questions}


def plan(profile):
    profile_check(profile);check_reviews();old=load(ROOT/'checkpoints/separate-subject-plan-2026-10-05.json')
    if any(profile[k]!=old[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'direct-subject-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'authorization':'User authorized direct subject extraction without a proposed binding on 2026-10-05.',
        'notes':27,'source_recordings':9,'rounds':3,'claims_per_note':6,'arms':list(ARMS),'call_arms':list(CALL_ARMS),'candidate':'direct',
        'maximum_calls':405,'maximum_answers':2430,'maximum_request_bytes':79840,
        'inputs':'Direct subject extraction sees the full unchanged note and complete observed service-name inventory, but no proposed service, measurements or reference. Fresh clean/wrong text-only proposal checks and unchanged numerical verdict requests are exact controls from the prior separate-call experiment. Six confirmed claims per note; no new notes or measurements.',
        'phases':'Commit plan/producers, then both exact phase protocols before inference. First 243 subject calls yield 1458 answers: one direct and two proposal checks per note/round. All 162 numerical verdict calls then run regardless of any subject result, yielding 972 answers. Neither verdict request depends on subject results.',
        'reference_policy':'Reuse committed original numerical verdicts and reviewed subjects. Compare direct extracted service with original service separately from matched/conflict classification. Clean proposals must match; swapped proposals must conflict even with invariant verdicts. No reference enters requests.',
        'display':'Numerical verdict probability >=0.70. Proposal-check additionally requires matched subject probability >=0.70. Direct additionally requires extracted service exactly equal to the supplied service, with selected-subject probability >=0.70. Unresolved never matches. Union sentence quarantines across subject and verdict calls; missing calls/answers withhold. Application code never repairs or rebinds a proposal.',
        'score':'Full planned denominators by application/style/round and direct-name/pronoun. Separate original-verdict correctness, comparison correctness, unique direct-service accuracy, unsafe displays, wrong-verdict displays, safe coverage and paired gains/losses against contemporary baseline and proposal check. Direct subject replies are reused for clean and swapped composition; unique accuracy and actual call costs count them once.',
        'gate':'In every application/style/round require complete calls, every clean/corrupt subject comparison correct, every clean verdict correct, no safe clean display loss against contemporary baseline and >=90% clean coverage. Corrupted inputs must display zero unsafe guidance and strictly fewer wrong verdicts than wrong baseline. Proposal-check is a diagnostic comparator and cannot replace the candidate. No protected data or operational promotion.',
        'execution':'405 once-only calls; no retries, repairs, threshold changes or fresh recordings. Rotate three subject call types and note order across rounds, then two verdict types. Existing output directory blocks rerun; global identity/envelope/usage/context/network failures stop execution.',
        'limits':'Same assistant authored and inspected these controlled notes and references; zero human/independent reviews. Every tested confirmed subject uniquely resolves; unresolved cases and authentic reports remain untested. Direct changes instructions and answer options as well as removing proposals, so any difference concerns the full task package, not proof of anchoring. Shared verdict replies and shared direct subject replies are not independent observations. No source-service repair or analyst usefulness measurement.',
        'sources':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (REVIEWS,DATA/'inputs.json',DATA/'manifest.json',ROOT/'checkpoints/separate-subject-results-2026-10-05.json')}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'status':'planned','maximum_calls':405,'maximum_answers':2430,'new_recordings':0}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='direct-subject-plan-1' or p['maximum_calls']!=405 or p['maximum_answers']!=2430 or p['arms']!=list(ARMS):raise ValueError('Direct-subject task/budget changed.')
    for n,digest in {**p['sources'],**p['evidence']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Direct-subject source/evidence changed: '+n)
    return p


def references():
    check_plan();return original_references()


def requests():
    check_plan();packets,records=check_reviews();index={r['note_id']:r for r in records};jobs=[]
    for phase,arms in (('text',('direct_subject','clean_checked','wrong_checked')),('verdict',('clean_baseline','wrong_baseline'))):
        for n in (1,2,3):
            offset=n-1
            for i,p in enumerate(packets[offset:]+packets[:offset]):
                start=(i+offset)%len(arms)
                for arm in arms[start:]+arms[:start]:
                    request=body(p,index[p['id']],arm)
                    jobs.append({'id':p['id']+'::direct-subject::'+arm+'::r'+str(n),'card_id':p['id'],'arm':arm,'phase':phase,'round':n,'request_sha256':sha(encoded(request)),'body':request})
    return jobs


def phase_protocol(phase):
    jobs=[j for j in requests() if j['phase']==phase]
    return {'schema':'direct-subject-phase-1','phase':phase,'plan_sha256':sha(PLAN.read_bytes()),'reference_sha256':sha((DATA/'references.json').read_bytes()),
        'references':references(),'planned_calls':len(jobs),'planned_answers':sum(len(j['body']['questions']) for j in jobs),
        'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}


def expected_protocol():
    return {'schema':'direct-subject-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'references':references(),
        'planned_calls':405,'planned_answers':2430,'phases':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (SUBJECT_PROTOCOL,VERDICT_PROTOCOL)}}


def freeze():
    p=check_plan()
    for phase,path,calls,answers in (('text',SUBJECT_PROTOCOL,243,1458),('verdict',VERDICT_PROTOCOL,162,972)):
        r=phase_protocol(phase)
        if r['planned_calls']!=calls or r['planned_answers']!=answers or r['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Direct-subject wire cap/budget exceeded.')
        with path.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    record=expected_protocol()
    with PROTOCOL.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k!='references'}


def check():
    p=check_plan();committed(PROTOCOL)
    for phase,path in (('text',SUBJECT_PROTOCOL),('verdict',VERDICT_PROTOCOL)):
        committed(path)
        if load(path)!=phase_protocol(phase):raise ValueError('Exact direct-subject phase changed.')
    if load(PROTOCOL)!=expected_protocol():raise ValueError('Exact direct-subject protocol changed.')
    return p,requests()


def run(profile):
    p,jobs=check();profile_check(profile)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Direct subject profile changed.')
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
            print(f"Direct subject {len(rows)}/{len(jobs)} {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'direct-subject-hosted-1','planned_calls':len(jobs),'attempted_calls':len(rows),'failed':sum(r['status']=='error' for r in rows),
        'unattempted_calls':len(jobs)-len(rows),'status':'completed' if len(rows)==len(jobs) and not reason else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows():
    p,jobs=check();summary=load(OUT/'summary.json')
    if summary['schema']!='direct-subject-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Direct subject run identity changed.')
    for n,digest in summary['files'].items():
        if sha((OUT/n).read_bytes())!=digest:raise ValueError('Direct subject run file changed.')
    if load(OUT/'requests.json')!=jobs:raise ValueError('Direct subject saved requests changed.')
    rows=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(jobs):raise ValueError('Extra review responses.')
    for r,j in zip(rows,jobs):
        if any(r.get(k)!=v for k,v in j.items() if k!='body') or r['status'] not in ('ok','ok_with_review','error'):raise ValueError('Direct subject response identity changed.')
        if r['status']!='error':
            validated=validate_reply(r['raw_response'],j['body'],p['context_tokens'])
            if any(r.get(k)!=v for k,v in validated.items()):raise ValueError('Direct subject normalized answer changed.')
        if isinstance(r.get('latency_ms'),bool) or not isinstance(r.get('latency_ms'),(float,int)) or r['latency_ms']<0:raise ValueError('Invalid recorded latency.')
    complete=len(rows)==len(jobs) and not any(r['status']=='error' for r in rows)
    if (summary['planned_calls'],summary['attempted_calls'],summary['failed'],summary['unattempted_calls'],summary['status'])!=(len(jobs),len(rows),sum(r['status']=='error' for r in rows),len(jobs)-len(rows),'completed' if complete else 'incomplete_or_failed'):
        raise ValueError('Direct subject run denominators changed.')
    if not complete or summary['stopped_reason']:raise ValueError('Complete review calls required; preserve failure and stop.')
    return rows


def composed_row(index,note,arm,n,record):
    if arm not in ARMS:raise ValueError('Unknown composed workflow.')
    if arm.endswith('baseline'):return copy.deepcopy(index.get((note,arm,n),{}))
    subject_arm='direct_subject' if arm.endswith('direct') else arm
    subject=copy.deepcopy(index.get((note,subject_arm,n),{}))
    verdict=index.get((note,'wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline',n),{})
    row=copy.deepcopy(subject);row['answers']={**subject.get('answers',{}),**verdict.get('answers',{})}
    row['quarantined_sentences']=sorted(set(subject.get('quarantined_sentences',[]))|set(verdict.get('quarantined_sentences',[])))
    valid=all(r.get('status') in ('ok','ok_with_review') for r in (subject,verdict))
    row['status']='ok_with_review' if valid and row['quarantined_sentences'] else 'ok' if valid else 'error'
    row['source_call_ids']=[subject.get('id'),verdict.get('id')]
    row['direct']=arm.endswith('direct')
    row['proposed_services']={sid:d['values']['service'] for sid,d in decisions(record,arm).items() if d['decision']=='confirm'}
    return row


def decision(row,sid,checked):
    answers=row.get('answers',{});v=answers.get(sid+'_verdict');s=answers.get(sid+'_subject') if checked else None
    quarantined=sid in row.get('quarantined_sentences',[]);eligible=not quarantined and row.get('status') in ('ok','ok_with_review')
    direct=row.get('direct',False)
    subject=(('unresolved' if s['choice']=='unresolved' else 'matched' if s['choice']==row.get('proposed_services',{}).get(sid) else 'conflict') if direct else s['choice']) if eligible and s else 'unavailable'
    shown=bool(eligible and v and v['probabilities'][v['choice']]>=.70 and (not checked or s and subject=='matched' and s['probabilities'][s['choice']]>=.70))
    return {'verdict':v['choice'] if eligible and v else 'unavailable','subject':subject,'extracted_service':s['choice'] if direct and eligible and s else None,'displayed':shown,'quarantined':quarantined}


def assess(packets,refs,rows):
    index={(r['card_id'],r['arm'],r['round']):r for r in rows};outcomes=[];panels={}
    _,records=check_reviews();records={r['note_id']:r for r in records}
    for p in packets:
        for arm in ARMS:
            checked=not arm.endswith('baseline');wrong=arm.startswith('wrong_')
            for n in (1,2,3):
                row=composed_row(index,p['id'],arm,n,records[p['id']])
                for sid,ref in refs[p['id']].items():
                    d=decision(row,sid,checked);control=decision(index.get((p['id'],'wrong_baseline' if wrong else 'clean_baseline',n),{}),sid,False)
                    correct=d['verdict']==ref['verdict'];safe=not wrong and correct
                    outcomes.append({'note_id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'arm':arm,'round':n,'sentence':sid,'reference':ref['verdict'],
                        'subject_reference':'conflict' if wrong else 'matched','subject_form':ref['subject_form'],**d,
                        'subject_correct':checked and d['subject']==('conflict' if wrong else 'matched'),'service_correct':arm.endswith('direct') and d['extracted_service']==ref['service'],'correct':correct,'safe':safe,
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
            for approach in ('direct','checked'):
                passes=[]
                for i in range(3):
                    c=arms['clean_'+approach][i]['strata']['all'];w=arms['wrong_'+approach][i]['strata']['all'];b=arms['clean_baseline'][i]['strata']['all'];wb=arms['wrong_baseline'][i]['strata']['all']
                    passes.append(bool(c['complete'] and w['complete'] and b['complete'] and wb['complete'] and c['subject_correct']==c['denominator'] and w['subject_correct']==w['denominator'] and c['correct']==c['denominator'] and c['correct_safe_displayed']>=b['correct_safe_displayed'] and c['correct_safe_displayed']/c['denominator']>=.9 and w['unsafe_displayed']==0 and w['wrong_verdict_displayed']<wb['wrong_verdict_displayed']))
                gates[approach]=passes
            panels[dataset][wording]={'arms':arms,'candidate_passes_by_round':gates['direct'],'candidate_passes':all(gates['direct']),'checked_passes_by_round':gates['checked'],'checked_passes':all(gates['checked'])}
    costs={arm:{'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_seconds':sum(r['latency_ms'] for r in rows if r['arm']==arm)/1000} for arm in CALL_ARMS}
    workflow_costs={}
    for arm in ARMS:
        source='direct_subject' if arm.endswith('direct') else arm
        baseline='wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline'
        workflow_costs[arm]={k:costs[source][k]+(costs[baseline][k] if not arm.endswith('baseline') else 0) for k in costs[source]}
    unique_subject=[]
    paired=[]
    for dataset in panels:
        for wording in ('all','plain','negated','boundary'):
            for n in (1,2,3):
                selected=[o for o in outcomes if o['dataset']==dataset and (wording=='all' or o['wording']==wording) and o['round']==n]
                direct=[o for o in selected if o['arm']=='clean_direct']
                unique_subject.append({'dataset':dataset,'wording':wording,'round':n,'denominator':len(direct),'correct':sum(o['service_correct'] for o in direct)})
                comparator={(o['note_id'],o['sentence']):o for o in selected if o['arm']=='clean_checked'}
                paired.append({'dataset':dataset,'wording':wording,'round':n,
                    'gains':sum(o['safe'] and o['displayed'] and not(comparator[(o['note_id'],o['sentence'])]['safe'] and comparator[(o['note_id'],o['sentence'])]['displayed']) for o in direct),
                    'losses':sum(comparator[(o['note_id'],o['sentence'])]['safe'] and comparator[(o['note_id'],o['sentence'])]['displayed'] and not(o['safe'] and o['displayed']) for o in direct)})
    return {'workflow_costs':workflow_costs,'unique_direct_subject':unique_subject,'paired_clean_displays':paired,'panels':panels,'outcomes':outcomes,'candidate_passes':all(p['candidate_passes'] for pp in panels.values() for p in pp.values()),'costs':costs}


def score():
    rows=verified_rows();packets,_=check_reviews();assessment=assess(packets,references(),rows)
    return {'schema':'direct-subject-results-1','calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),
        'valid_answers':sum(len(r.get('answers',{})) for r in rows),'human_reviews':0,'independent_reviews':0,'new_recordings':0,
        'protocol_sha256':sha(PROTOCOL.read_bytes()),'run_summary_sha256':sha((OUT/'summary.json').read_bytes()),**assessment}
