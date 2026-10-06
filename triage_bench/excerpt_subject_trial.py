"""Prospective full-prefix versus latest-explicit-name literal excerpt subject extraction."""
import copy
import re
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
from .prefix_subject_trial import SOURCES as OLD_SOURCES, body as prior_body, decisions as old_decisions, references as original_references, note_prefix

PLAN=ROOT/'checkpoints/excerpt-subject-plan-2026-10-06.json'
PROTOCOL=ROOT/'checkpoints/excerpt-subject-protocol-2026-10-06.json'
RESULT=ROOT/'checkpoints/excerpt-subject-results-2026-10-06.json'
OUT=ROOT/'runs/excerpt-subject/hosted-2026-10-06-v1'
ARMS=('clean_baseline','wrong_baseline','clean_prefix','wrong_prefix','clean_excerpt','wrong_excerpt')
CALL_ARMS=('prefix_subject','excerpt_subject','clean_baseline','wrong_baseline')
SUBJECT_PROTOCOL=ROOT/'checkpoints/excerpt-subject-text-protocol-2026-10-06.json'
VERDICT_PROTOCOL=ROOT/'checkpoints/excerpt-subject-verdict-protocol-2026-10-06.json'
SOURCES=OLD_SOURCES+('triage_bench/excerpt_subject_trial.py','scripts/run_excerpt_subject.py')


def decisions(record,arm):
    if arm not in ARMS:raise ValueError('Unknown excerpt-subject input.')
    return old_decisions(record,'wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline')


def excerpt_context(p,sid):
    prefix=note_prefix(p,sid)
    lines=prefix.splitlines(keepends=True)
    services=p['services']
    if not services or len(set(services))!=len(services) or any(not isinstance(x,str) or not x for x in services):
        raise ValueError('Observed service inventory is invalid.')
    patterns={service:re.compile(r'(?<![\w-])'+re.escape(service)+r'(?![\w-])') for service in services}
    for i in range(len(lines)-1,-1,-1):
        mentioned=[service for service,pattern in patterns.items() if pattern.search(lines[i])]
        if mentioned:
            start=sum(len(line) for line in lines[:i]) if len(mentioned)==1 else 0
            return {'note':prefix[start:], 'start_sentence':p['candidates'][i]['id'] if len(mentioned)==1 else p['candidates'][0]['id'],
                    'end_sentence':sid,'latest_named_sentence':p['candidates'][i]['id'],'mentioned_services':mentioned,
                    'selection':'single_name' if len(mentioned)==1 else 'multiple_names_full_prefix','start_offset':start,'end_offset':len(prefix)}
    return {'note':prefix,'start_sentence':p['candidates'][0]['id'],'end_sentence':sid,'latest_named_sentence':None,
            'mentioned_services':[],'selection':'no_name_full_prefix','start_offset':0,'end_offset':len(prefix)}


def body(p,record,arm,sid=None):
    if arm in ('clean_baseline','wrong_baseline'):
        if sid is not None:raise ValueError('Verdict baseline remains a six-question batch.')
        return prior_body(p,record,arm)
    if arm not in ('prefix_subject','excerpt_subject'):raise ValueError('Unknown excerpt-subject call.')
    request=prior_body(p,record,'prefix_subject',sid)
    if arm=='excerpt_subject':
        state=json.loads(request['state']);state['note']=excerpt_context(p,sid)['note']
        request['state']=json.dumps(state,separators=(',',':'))
    return request


def plan(profile):
    profile_check(profile);check_reviews();old=load(ROOT/'checkpoints/prefix-subject-plan-2026-10-06.json')
    if any(profile[k]!=old[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'excerpt-subject-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'authorization':'User authorized the remaining staged research plan and continuation until blocked on 2026-10-06.',
        'notes':27,'source_recordings':9,'rounds':3,'claims_per_note':6,'arms':list(ARMS),'call_arms':list(CALL_ARMS),'candidate':'excerpt',
        'maximum_calls':1134,'maximum_answers':1944,'maximum_request_bytes':79840,
        'inputs':'One confirmed subject per request in both full-prefix and excerpt arms. Comparator is the exact earlier prefix body. Only state.note differs. Scan source sentences backward from the queried claim for complete observed service names, with word/hyphen boundaries and exact case. Start at the latest sentence naming exactly one service, through the queried claim. If that latest named sentence names multiple services, or no sentence names a service, retain the full prefix. Preserve every character in the selected slice and complete inventories. Never rewrite pronouns, insert reference subjects or send proposals, measurements, later text or other subject questions to subject calls. Verdict bodies remain exact six-question baselines.',
        'phases':'Commit plan/producers, then both exact phase protocols before inference. First 972 subject calls yield 972 answers: prefix and excerpt for every confirmed claim/note/round. Run all 162 independent verdict calls afterward, yielding 972 answers regardless of subject decisions. No conditional skipping or service rebinding.',
        'reference_policy':'Reuse committed original numerical verdicts and reviewed unique subjects. Direct service accuracy counts each actual subject reply once; clean and swapped comparisons reuse that reply. No annotation enters request construction, except the already confirmed claim selection; neither subject names nor verdict references are supplied as answers.',
        'display':'Both subject workflows require extracted service equal to the supplied proposal and selected-subject probability >=0.70, with the unchanged numerical verdict probability >=0.70. Unresolved never matches. Union sentence quarantine across the selected subject call and corresponding verdict batch. Missing calls/answers withhold; preserve valid siblings. Never repair or rebind proposals.',
        'score':'Full planned denominators per application/style/round and named/pronoun strata. Original verdict correctness, unique extracted-service accuracy, comparison correctness, safe/unsafe displays, wrong-verdict displays, withholding and paired excerpt-versus-fresh-prefix display/service gains and losses. Count 1134 actual calls once, retaining overlap across composed workflows. Record the literal context selection for every confirmed claim before calls.',
        'gate':'In every application/style/round require complete calls, every clean/corrupt subject comparison correct, every clean verdict correct, no safe clean display loss against contemporary baseline and >=90% coverage. Corrupted inputs must display zero unsafe guidance and strictly fewer wrong verdicts than wrong baseline. Full prefix is the comparator and cannot replace the declared excerpt candidate. No operational or protected-data promotion.',
        'execution':'1134 once-only calls, no retries, post-result repairs, text edits, threshold changes or fresh recordings. Rotate notes, confirmed sentence order and paired subject arm order over three rounds, then rotate two verdict arms. Existing output directory blocks rerun; global identity/envelope/usage/context/network failures stop.',
        'limits':'The same assistant authored and inspected notes and references, with zero human/independent reviews. This string-selection rule is a diagnostic for uniquely resolvable inspected claims, not a general discourse policy. Unresolved, future-dependent, quoted and intervening-context challenges remain a separate planned study. Previous prefix replies are historical; fresh paired prefix requests isolate the new truncation under the same single-question grouping. Shared replies are not independent incidents. No causal, analyst-usefulness or operational-reliability claim.',
        'sources':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (REVIEWS,DATA/'inputs.json',DATA/'manifest.json',ROOT/'checkpoints/prefix-subject-results-2026-10-06.json')}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'status':'planned','maximum_calls':1134,'maximum_answers':1944,'new_recordings':0}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='excerpt-subject-plan-1' or p['maximum_calls']!=1134 or p['maximum_answers']!=1944 or p['arms']!=list(ARMS):raise ValueError('Excerpt-subject task/budget changed.')
    for n,digest in {**p['sources'],**p['evidence']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Excerpt-subject source/evidence changed: '+n)
    return p


def references():
    check_plan();return original_references()


def requests():
    check_plan();packets,records=check_reviews();index={r['note_id']:r for r in records};jobs=[]
    for phase in ('text','verdict'):
        for n in (1,2,3):
            offset=n-1
            for i,p in enumerate(packets[offset:]+packets[:offset]):
                record=index[p['id']]
                sentences=[c['id'] for c in p['candidates'] if record['export']['reviews'][c['id']]['decision']=='confirm'] if phase=='text' else [None]
                if phase=='text':
                    start=offset%len(sentences);sentences=sentences[start:]+sentences[:start]
                for j,sid in enumerate(sentences):
                    arms=('prefix_subject','excerpt_subject') if phase=='text' else ('clean_baseline','wrong_baseline')
                    start=(i+j+offset)%2
                    for arm in arms[start:]+arms[:start]:
                        request=body(p,record,arm,sid)
                        jobs.append({'id':p['id']+'::excerpt-subject::'+arm+'::'+(sid or 'batch')+'::r'+str(n),'card_id':p['id'],'arm':arm,'phase':phase,'sentence':sid,'round':n,'request_sha256':sha(encoded(request)),'body':request})
    return jobs


def phase_protocol(phase):
    jobs=[j for j in requests() if j['phase']==phase]
    return {'schema':'excerpt-subject-phase-1','phase':phase,'plan_sha256':sha(PLAN.read_bytes()),'reference_sha256':sha((DATA/'references.json').read_bytes()),
        'references':references(),'contexts':[{ 'note_id':p['id'],'sentence':c['id'],**excerpt_context(p,c['id'])} for p,r in zip(*check_reviews()) for c in p['candidates'] if r['export']['reviews'][c['id']]['decision']=='confirm'] if phase=='text' else [],'planned_calls':len(jobs),'planned_answers':sum(len(j['body']['questions']) for j in jobs),
        'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}


def expected_protocol():
    return {'schema':'excerpt-subject-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'references':references(),
        'planned_calls':1134,'planned_answers':1944,'phases':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (SUBJECT_PROTOCOL,VERDICT_PROTOCOL)}}


def freeze():
    p=check_plan()
    for phase,path,calls,answers in (('text',SUBJECT_PROTOCOL,972,972),('verdict',VERDICT_PROTOCOL,162,972)):
        r=phase_protocol(phase)
        if r['planned_calls']!=calls or r['planned_answers']!=answers or r['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Excerpt-subject wire cap/budget exceeded.')
        with path.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    record=expected_protocol()
    with PROTOCOL.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k!='references'}


def check():
    p=check_plan();committed(PROTOCOL)
    for phase,path in (('text',SUBJECT_PROTOCOL),('verdict',VERDICT_PROTOCOL)):
        committed(path)
        if load(path)!=phase_protocol(phase):raise ValueError('Exact excerpt-subject phase changed.')
    if load(PROTOCOL)!=expected_protocol():raise ValueError('Exact excerpt-subject protocol changed.')
    return p,requests()


def run(profile):
    p,jobs=check();profile_check(profile)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Excerpt subject profile changed.')
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
            print(f"Excerpt subject {len(rows)}/{len(jobs)} {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'excerpt-subject-hosted-1','planned_calls':len(jobs),'attempted_calls':len(rows),'failed':sum(r['status']=='error' for r in rows),
        'unattempted_calls':len(jobs)-len(rows),'status':'completed' if len(rows)==len(jobs) and not reason else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows():
    p,jobs=check();summary=load(OUT/'summary.json')
    if summary['schema']!='excerpt-subject-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Excerpt subject run identity changed.')
    for n,digest in summary['files'].items():
        if sha((OUT/n).read_bytes())!=digest:raise ValueError('Excerpt subject run file changed.')
    if load(OUT/'requests.json')!=jobs:raise ValueError('Excerpt subject saved requests changed.')
    rows=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(jobs):raise ValueError('Extra review responses.')
    for r,j in zip(rows,jobs):
        if any(r.get(k)!=v for k,v in j.items() if k!='body') or r['status'] not in ('ok','ok_with_review','error'):raise ValueError('Excerpt subject response identity changed.')
        if r['status']!='error':
            validated=validate_reply(r['raw_response'],j['body'],p['context_tokens'])
            if any(r.get(k)!=v for k,v in validated.items()):raise ValueError('Excerpt subject normalized answer changed.')
        if isinstance(r.get('latency_ms'),bool) or not isinstance(r.get('latency_ms'),(float,int)) or r['latency_ms']<0:raise ValueError('Invalid recorded latency.')
    complete=len(rows)==len(jobs) and not any(r['status']=='error' for r in rows)
    if (summary['planned_calls'],summary['attempted_calls'],summary['failed'],summary['unattempted_calls'],summary['status'])!=(len(jobs),len(rows),sum(r['status']=='error' for r in rows),len(jobs)-len(rows),'completed' if complete else 'incomplete_or_failed'):
        raise ValueError('Excerpt subject run denominators changed.')
    if not complete or summary['stopped_reason']:raise ValueError('Complete review calls required; preserve failure and stop.')
    return rows


def composed_row(index,note,arm,n,record,sid):
    if arm not in ARMS:raise ValueError('Unknown composed workflow.')
    if arm.endswith('baseline'):return copy.deepcopy(index.get((note,arm,n,None),{}))
    subject_arm='excerpt_subject' if arm.endswith('excerpt') else 'prefix_subject'
    subject=copy.deepcopy(index.get((note,subject_arm,n,sid),{}))
    verdict=index.get((note,'wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline',n,None),{})
    row=copy.deepcopy(subject);row['answers']={**subject.get('answers',{}),**verdict.get('answers',{})}
    row['quarantined_sentences']=sorted(set(subject.get('quarantined_sentences',[]))|set(verdict.get('quarantined_sentences',[])))
    valid=all(r.get('status') in ('ok','ok_with_review') for r in (subject,verdict))
    row['status']='ok_with_review' if valid and row['quarantined_sentences'] else 'ok' if valid else 'error'
    row['source_call_ids']=[subject.get('id'),verdict.get('id')]
    row['direct']=True
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
    index={(r['card_id'],r['arm'],r['round'],r['sentence']):r for r in rows};outcomes=[];panels={}
    _,records=check_reviews();records={r['note_id']:r for r in records}
    for p in packets:
        for arm in ARMS:
            checked=not arm.endswith('baseline');wrong=arm.startswith('wrong_')
            for n in (1,2,3):
                for sid,ref in refs[p['id']].items():
                    row=composed_row(index,p['id'],arm,n,records[p['id']],sid)
                    d=decision(row,sid,checked);control=decision(index.get((p['id'],'wrong_baseline' if wrong else 'clean_baseline',n,None),{}),sid,False)
                    correct=d['verdict']==ref['verdict'];safe=not wrong and correct
                    outcomes.append({'note_id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'arm':arm,'round':n,'sentence':sid,'reference':ref['verdict'],
                        'subject_reference':'conflict' if wrong else 'matched','subject_form':ref['subject_form'],**d,
                        'subject_correct':checked and d['subject']==('conflict' if wrong else 'matched'),'service_correct':checked and d['extracted_service']==ref['service'],'correct':correct,'safe':safe,
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
            for approach in ('excerpt','prefix'):
                passes=[]
                for i in range(3):
                    c=arms['clean_'+approach][i]['strata']['all'];w=arms['wrong_'+approach][i]['strata']['all'];b=arms['clean_baseline'][i]['strata']['all'];wb=arms['wrong_baseline'][i]['strata']['all']
                    passes.append(bool(c['complete'] and w['complete'] and b['complete'] and wb['complete'] and c['subject_correct']==c['denominator'] and w['subject_correct']==w['denominator'] and c['correct']==c['denominator'] and c['correct_safe_displayed']>=b['correct_safe_displayed'] and c['correct_safe_displayed']/c['denominator']>=.9 and w['unsafe_displayed']==0 and w['wrong_verdict_displayed']<wb['wrong_verdict_displayed']))
                gates[approach]=passes
            panels[dataset][wording]={'arms':arms,'candidate_passes_by_round':gates['excerpt'],'candidate_passes':all(gates['excerpt']),'prefix_passes_by_round':gates['prefix'],'prefix_passes':all(gates['prefix'])}
    costs={arm:{'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_seconds':sum(r['latency_ms'] for r in rows if r['arm']==arm)/1000} for arm in CALL_ARMS}
    workflow_costs={}
    for arm in ARMS:
        source=arm if arm.endswith('baseline') else 'excerpt_subject' if arm.endswith('excerpt') else 'prefix_subject'
        baseline='wrong_baseline' if arm.startswith('wrong_') else 'clean_baseline'
        workflow_costs[arm]={k:costs[source][k]+(costs[baseline][k] if not arm.endswith('baseline') else 0) for k in costs[source]}
    unique_subject=[];paired=[]
    for dataset in panels:
        for wording in ('all','plain','negated','boundary'):
            for n in (1,2,3):
                selected=[o for o in outcomes if o['dataset']==dataset and (wording=='all' or o['wording']==wording) and o['round']==n]
                for approach in ('prefix','excerpt'):
                    rr=[o for o in selected if o['arm']=='clean_'+approach]
                    unique_subject.append({'dataset':dataset,'wording':wording,'round':n,'approach':approach,'denominator':len(rr),'correct':sum(o['service_correct'] for o in rr)})
                candidate=[o for o in selected if o['arm']=='clean_excerpt'];comparator={(o['note_id'],o['sentence']):o for o in selected if o['arm']=='clean_prefix'}
                paired.append({'dataset':dataset,'wording':wording,'round':n,
                    'gains':sum(o['safe'] and o['displayed'] and not(comparator[(o['note_id'],o['sentence'])]['safe'] and comparator[(o['note_id'],o['sentence'])]['displayed']) for o in candidate),
                    'losses':sum(comparator[(o['note_id'],o['sentence'])]['safe'] and comparator[(o['note_id'],o['sentence'])]['displayed'] and not(o['safe'] and o['displayed']) for o in candidate),
                    'service_gains':sum(o['service_correct'] and not comparator[(o['note_id'],o['sentence'])]['service_correct'] for o in candidate),
                    'service_losses':sum(comparator[(o['note_id'],o['sentence'])]['service_correct'] and not o['service_correct'] for o in candidate)})
    return {'workflow_costs':workflow_costs,'unique_subject':unique_subject,'paired_clean_displays':paired,'panels':panels,'outcomes':outcomes,'candidate_passes':all(p['candidate_passes'] for pp in panels.values() for p in pp.values()),'costs':costs}


def score():
    rows=verified_rows();packets,_=check_reviews();assessment=assess(packets,references(),rows)
    return {'schema':'excerpt-subject-results-1','calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),
        'valid_answers':sum(len(r.get('answers',{})) for r in rows),'human_reviews':0,'independent_reviews':0,'new_recordings':0,
        'protocol_sha256':sha(PROTOCOL.read_bytes()),'run_summary_sha256':sha((OUT/'summary.json').read_bytes()),**assessment}
