"""Controlled binding corruption on inspected notes; no extraction or new data."""
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
from .public_claim_reference import evaluate
from .assistant_review_trial import SOURCES as OLD_SOURCES, REVIEWS, check_reviews, body as clean_body

PLAN=ROOT/'checkpoints/binding-corruption-plan-2026-10-05.json'
PROTOCOL=ROOT/'checkpoints/binding-corruption-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/binding-corruption-results-2026-10-05.json'
OUT=ROOT/'runs/binding-corruption/hosted-2026-10-05-v1'
ARMS=('clean_bound','clean_meaning','service_bound','service_meaning','polarity_meaning')
SOURCES=OLD_SOURCES+('triage_bench/binding_corruption_trial.py','scripts/run_binding_corruption.py')


def altered(record,arm):
    if arm not in ARMS:raise ValueError('Unknown corruption arm.')
    r=copy.deepcopy(record)
    confirmed=[v['values'] for v in r['export']['reviews'].values() if v['decision']=='confirm']
    services=sorted({v['service'] for v in confirmed})
    if len(confirmed)!=6 or len(services)!=2:raise ValueError('Expected six claims on two services.')
    for v in confirmed:
        if arm.startswith('service_'):v['service']=services[1-services.index(v['service'])]
        elif arm=='polarity_meaning':v['polarity']='negative' if v['polarity']=='positive' else 'positive'
    return r


def body(p,record,arm):
    r=altered(record,arm)
    request=clean_body(p,r,'bound_text' if arm.endswith('bound') else 'explicit_meaning')
    if request['state']!=clean_body(p,record,'bound_text')['state']:raise ValueError('Corruption changed evidence or note.')
    return request


def plan(profile):
    profile_check(profile);check_reviews()
    old=load(ROOT/'checkpoints/assistant-review-plan-2026-10-05.json')
    if any(profile[k]!=old[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    record={'schema':'binding-corruption-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'authorization':'User selected the recommended controlled service/meaning corruption diagnostic on 2026-10-05.',
        'notes':27,'source_recordings':9,'rounds':3,'claims_per_note':6,'arms':list(ARMS),'maximum_calls':405,'maximum_answers':2430,'maximum_request_bytes':79840,
        'transformation':'Swap the two confirmed services bijectively for all six claims, or reverse every confirmed polarity for explicit meaning. Do not choose corruptions by verdict or repair text. Both original service ledgers remain in exactly the same state bytes.',
        'controls':'clean_bound and clean_meaning exactly reuse the previous request bodies. service_bound changes only binding service in bound questions; service_meaning changes service in explicit questions; polarity_meaning changes only typed polarity. All sentences, note context, facts, question IDs, criteria, model and numerical policy stay unchanged.',
        'reference_policy':'Score every answer against the existing ORIGINAL sentence verdict, not the corrupted proposition. After committing this plan, also calculate a separate altered-proposition verdict for diagnostics. An absent metric channel remains unknown. References never enter requests.',
        'diagnostic':'Divergent means original and altered proposition verdicts differ; only this stratum can distinguish preserved literal verdict from following the altered proposition. Invariant answers cannot establish correct binding. Report direct-name and pronoun sentences separately, and each application/style/round. A matching altered verdict is compatible with following the binding, not proof of internal reasoning.',
        'display':'Keep >=0.70 selected-verdict probability. Report original correct, correct displayed, wrong displayed, withheld, and matching altered verdict on full planned denominators. Invalid fields remain quarantined and count unavailable.',
        'decision':'No candidate, tuning or promotion. For each corrupted input, diagnose losses versus its matched fresh clean control; report all paired gains/losses and invariant cases. Existing instructions declare bindings authoritative; errors against original sentences measure workflow vulnerability, not instruction-following failure.',
        'execution':'Commit plan and producers before preparation; commit exact request and diagnostic-reference hashes before 405 once-only calls. Rotate note/arm order over three rounds. No retries, response repair, threshold search or post-result input changes. Existing output directory forbids rerun; global failure stops.',
        'limits':'Same-author controlled notes on nine inspected recordings, zero human and independent reviews, no fresh telemetry. Artificial corruption prevalence is not an organic error rate. Repeated wording/rounds are not independent incidents. No protected data access, operational reliability, specialist validity or telecom readiness claim.',
        'sources':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (REVIEWS,DATA/'inputs.json',DATA/'manifest.json',ROOT/'checkpoints/assistant-review-results-2026-10-05.json')}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'status':'planned','maximum_calls':405,'maximum_answers':2430,'new_recordings':0}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='binding-corruption-plan-1' or p['maximum_calls']!=405 or p['maximum_answers']!=2430 or p['arms']!=list(ARMS):raise ValueError('Corruption budget changed.')
    for n,digest in {**p['sources'],**p['evidence']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Corruption source or evidence changed: '+n)
    return p


def references():
    check_plan();packets,records=check_reviews();old={r['id']:r for r in load(DATA/'references.json')};out={}
    for p,r in zip(packets,records):
        observed={o['service']:o for o in p['observations']};sentences={c['id']:c['text'] for c in p['candidates']};out[p['id']]={}
        for arm in ARMS:
            decisions=altered(r,arm)['export']['reviews'];items={}
            for a in old[p['id']]['annotations']:
                if not a['actionable']:continue
                v=decisions[a['id']]['values'];prop={'kind':v['kind'],'asserted':v['polarity']=='positive'}
                if v['kind'].startswith('metric_'):prop['channel']=v['channel']
                if v['kind']=='duration_material':prop['measure']=v['measure']
                observation=observed[v['service']]
                if v['kind'].startswith('metric_') and v['channel'] not in observation['metrics']:
                    diagnostic={'answer':'unanswerable','proposition':prop,'facts':{'channel':v['channel'],'absent_channel':True},'reason':'No observation for this metric channel on the altered service.'}
                else:diagnostic=evaluate(observation,prop)
                if arm.startswith('clean_') and diagnostic['answer']!=a['verdict']:raise ValueError('Original reference mismatch.')
                items[a['id']]={'original':a['verdict'],'altered':diagnostic['answer'],'divergent':a['verdict']!=diagnostic['answer'],
                    'subject_form':'direct_name' if a['service'] in sentences[a['id']] else 'pronoun',
                    'original_binding':r['export']['reviews'][a['id']]['values'],'supplied_binding':v,'diagnostic':diagnostic}
            out[p['id']][arm]=items
    return out


def requests():
    check_plan();packets,records=check_reviews();indexed={r['note_id']:r for r in records};jobs=[]
    for n in (1,2,3):
        offset=n-1
        for i,p in enumerate(packets[offset:]+packets[:offset]):
            start=(i+offset)%len(ARMS)
            for arm in ARMS[start:]+ARMS[:start]:
                request=body(p,indexed[p['id']],arm)
                jobs.append({'id':p['id']+'::binding-corruption::'+arm+'::r'+str(n),'card_id':p['id'],'arm':arm,'round':n,'request_sha256':sha(encoded(request)),'body':request})
    return jobs


def expected_protocol():
    p=check_plan();jobs=requests();refs=references()
    return {'schema':'binding-corruption-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'reference_sha256':sha((DATA/'references.json').read_bytes()),
        'diagnostic_references':refs,'planned_calls':len(jobs),'planned_answers':sum(len(j['body']['questions']) for j in jobs),
        'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}


def freeze():
    record=expected_protocol();p=check_plan()
    if record['planned_calls']!=405 or record['planned_answers']!=2430 or record['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Corruption budget/wire cap exceeded.')
    with PROTOCOL.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {k:v for k,v in record.items() if k not in ('requests','diagnostic_references')}


def check():
    p=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL)
    if protocol!=expected_protocol() or protocol['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Exact corruption protocol changed.')
    return p,requests()


def run(profile):
    p,jobs=check();profile_check(profile)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Corruption profile changed.')
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
            print(f"Binding corruption {len(rows)}/{len(jobs)} {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'binding-corruption-hosted-1','planned_calls':len(jobs),'attempted_calls':len(rows),'failed':sum(r['status']=='error' for r in rows),
        'unattempted_calls':len(jobs)-len(rows),'status':'completed' if len(rows)==len(jobs) and not reason else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows():
    p,jobs=check();summary=load(OUT/'summary.json')
    if summary['schema']!='binding-corruption-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Corruption run identity changed.')
    for n,digest in summary['files'].items():
        if sha((OUT/n).read_bytes())!=digest:raise ValueError('Corruption run file changed.')
    if load(OUT/'requests.json')!=jobs:raise ValueError('Corruption saved requests changed.')
    rows=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(jobs):raise ValueError('Extra review responses.')
    for r,j in zip(rows,jobs):
        if any(r.get(k)!=v for k,v in j.items() if k!='body') or r['status'] not in ('ok','ok_with_review','error'):raise ValueError('Corruption response identity changed.')
        if r['status']!='error':
            validated=validate_reply(r['raw_response'],j['body'],p['context_tokens'])
            if any(r.get(k)!=v for k,v in validated.items()):raise ValueError('Corruption normalized answer changed.')
        if isinstance(r.get('latency_ms'),bool) or not isinstance(r.get('latency_ms'),(float,int)) or r['latency_ms']<0:raise ValueError('Invalid recorded latency.')
    complete=len(rows)==len(jobs) and not any(r['status']=='error' for r in rows)
    if (summary['planned_calls'],summary['attempted_calls'],summary['failed'],summary['unattempted_calls'],summary['status'])!=(len(jobs),len(rows),sum(r['status']=='error' for r in rows),len(jobs)-len(rows),'completed' if complete else 'incomplete_or_failed'):
        raise ValueError('Corruption run denominators changed.')
    if not complete or summary['stopped_reason']:raise ValueError('Complete review calls required; preserve failure and stop.')
    return rows


def assess(packets,refs,rows):
    indexed={(r['card_id'],r['arm'],r['round']):r for r in rows};panels={};outcomes=[]
    for p in packets:
        for arm in ARMS:
            for n in (1,2,3):
                row=indexed.get((p['id'],arm,n),{})
                for sid,ref in refs[p['id']][arm].items():
                    answer=row.get('answers',{}).get(sid+'_verdict');choice=answer['choice'] if answer else 'unavailable'
                    shown=bool(answer and answer['probabilities'][choice]>=.70)
                    control='clean_bound' if arm.endswith('bound') else 'clean_meaning'
                    ca=indexed.get((p['id'],control,n),{}).get('answers',{}).get(sid+'_verdict')
                    cc=bool(ca and ca['choice']==ref['original']);cs=bool(ca and ca['probabilities'][ca['choice']]>=.70)
                    outcomes.append({'note_id':p['id'],'dataset':p['dataset'],'wording':p['wording'],'arm':arm,'round':n,'sentence':sid,
                        'original':ref['original'],'altered':ref['altered'],'divergent':ref['divergent'],'subject_form':ref['subject_form'],
                        'choice':choice,'displayed':shown,'correct':choice==ref['original'],'matches_altered':choice==ref['altered'],
                        'control_correct':cc,'control_displayed':cs,'call_complete':row.get('status') in ('ok','ok_with_review')})
    for dataset in sorted({p['dataset'] for p in packets}):
        panels[dataset]={}
        for wording in ('all','plain','negated','boundary'):
            panels[dataset][wording]={}
            for arm in ARMS:
                result=[]
                for n in (1,2,3):
                    rr=[o for o in outcomes if o['dataset']==dataset and (wording=='all' or o['wording']==wording) and o['arm']==arm and o['round']==n]
                    strata={}
                    for name in ('all','divergent','invariant','direct_name','pronoun','divergent_direct_name','divergent_pronoun'):
                        selected=[o for o in rr if (not name.startswith('divergent') or o['divergent']) and (name!='invariant' or not o['divergent']) and ('direct_name' not in name or o['subject_form']=='direct_name') and ('pronoun' not in name or o['subject_form']=='pronoun')]
                        strata[name]={'denominator':len(selected),'correct':sum(o['correct'] for o in selected),'correct_displayed':sum(o['correct'] and o['displayed'] for o in selected),
                            'wrong_displayed':sum(not o['correct'] and o['displayed'] for o in selected),'withheld':sum(not o['displayed'] for o in selected),'matches_altered':sum(o['matches_altered'] for o in selected),
                            'losses':sum(o['control_correct'] and not o['correct'] for o in selected),'gains':sum(not o['control_correct'] and o['correct'] for o in selected),
                            'display_losses':sum(o['control_correct'] and o['control_displayed'] and not (o['correct'] and o['displayed']) for o in selected),'complete':all(o['call_complete'] for o in selected)}
                    result.append({'round':n,'strata':strata})
                panels[dataset][wording][arm]=result
    return {'panels':panels,'outcomes':outcomes,'costs':{arm:{'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_seconds':sum(r['latency_ms'] for r in rows if r['arm']==arm)/1000} for arm in ARMS}}


def score():
    rows=verified_rows();packets,_=check_reviews();assessment=assess(packets,references(),rows)
    return {'schema':'binding-corruption-results-1','calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),
        'valid_answers':sum(len(r.get('answers',{})) for r in rows),'human_reviews':0,'independent_reviews':0,'new_recordings':0,
        'protocol_sha256':sha(PROTOCOL.read_bytes()),'run_summary_sha256':sha((OUT/'summary.json').read_bytes()),**assessment}
