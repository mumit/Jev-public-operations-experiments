"""Once-only paired report-reading diagnostic; no fresh telemetry access."""
import json,time,urllib.request,urllib.error
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_rca_trial import normalize
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_report_features import ARMS,FIELDS,POLICY,CLASSES
from .public_report_data import PLAN,DATA,SOURCE,REFSOURCE,check_plan,validate
from .public_claim_language_trial import SOURCES as PREVIOUS_SOURCES
PROTOCOL=ROOT/'checkpoints/public-report-reading-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/public-report-reading-results-2026-10-05.json'
OUTPUT=ROOT/'runs/public-report-reading/diagnostic-hosted-2026-10-05-v1'
SOURCES=tuple(dict.fromkeys(PREVIOUS_SOURCES+('triage_bench/public_report_features.py','triage_bench/public_report_data.py','triage_bench/public_report_trial.py','scripts/run_public_reports.py')))

def plan(profile):
    from scripts.verify_public_claim_language import verify
    profile_check(profile);verify()
    if PLAN.exists():raise ValueError('Report plan exists.')
    previous=load(ROOT/'checkpoints/public-claim-language-plan-2026-10-05.json')
    if any(profile[k]!=previous[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Recorded profile required.')
    record={'schema':'public-report-reading-plan-1','decision':'User authorized next short-report diagnostic on 2026-10-05.',
        'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':24000,
        'reports':16,'claims':96,'service_cards':32,'recordings':16,'rounds':3,'maximum_calls':96,'arms':list(ARMS),'fields':list(FIELDS),'policy':POLICY,
        'task':'Six independent verdict questions per request. Two services per report, three claims per service. Direct atomic control and numbered report share identical two-service ledgers, Choice criteria, numerical and verdict instructions. Report questions locate a numbered sentence; direct questions carry the identical sentence themselves. Every claim names its service explicitly.',
        'allocation':'Reuse all 32 service cards from 16 inspected recordings. Choose three propositions per card from the frozen wording catalogue by SHA256 order independent of reference class. Choose the frozen direct paraphrase, prepend explicit service, replace this-service phrases by that service. Deterministically shuffle six sentences. No new measurements, downloads, ambiguous pronouns or source injection labels.',
        'references':'Frozen typed proposition evaluator applied to each original service observation. Metadata and references stay outside requests. No class balancing or supplied class pattern. Whole-report correctness requires all six independent verdicts correct; whole-report complete display requires all six answers eligible at >=0.70.',
        'comparison':'Fresh atomic versus report judgments on identical claims and multi-service context. Older single-service answers remain separate. This diagnoses locating and judging explicit assertions, not extracting implicit claims from authentic prose. Prior ML predicts incident origin and remains unscored; typed evaluator is exact by construction and does not parse reports.',
        'execution':'Commit plan before preparation and exact hashes before inference. 96 serial calls, three cyclic rounds, paired arm order alternates; no retries or warmup. Stop on HTTP/network/model/context failure or three consecutive malformed replies. 30s timeout. Keep failed/missing denominators. Do not substitute or retune after results.',
        'scoring':'Per application/arm/class/round correctness, wrong displayed verdicts, support coverage, unknown-to-decisive errors, all-six report correctness and complete display, per-service results, stable paired fixes/losses and round consistency. Inherited uncalibrated display threshold 0.70 stays unchanged.',
        'research_gate':'In EACH application and round report must have all calls successful, >=90% correct for EACH reference class present, zero wrong displayed verdicts of any class, correct displayed support >=half of supported references, >=90% all-six report correctness, and total correct >=fresh atomic control. All classes must occur in each application. Diagnostic only; passing opens no protected data.',
        'reserves':'No new telemetry access. Protect 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves. Fresh confirmation needs separate allocation and evaluation protocol.',
        'limits':'Authored six-sentence notes on inspected controlled application faults. Numbered explicit assertions, correlated services and rounds; no authentic analyst reports, specialist-reviewed judgments, telecom validation or causal diagnosis. No added-value claim versus unrestricted parser.',
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('checkpoints/public-claim-language-results-2026-10-05.json',str(SOURCE.relative_to(ROOT)),str(REFSOURCE.relative_to(ROOT)))}}
    PLAN.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':96,'reports':16,'fresh_cases_consumed':0}

def requests():
    validate();packets=load(DATA/'inputs.json');result=[]
    for number in (1,2,3):
        offset=number-1
        for i,packet in enumerate(packets[offset:]+packets[:offset]):
            start=(i+offset)%len(ARMS)
            for arm in ARMS[start:]+ARMS[:start]:
                body=packet['requests'][arm]
                result.append({'id':packet['id']+'::'+arm+'::r'+str(number),'card_id':packet['id'],'arm':arm,'round':number,'request_sha256':sha(encoded(body)),'body':body})
    return result


def freeze():
    plan=check_plan()
    if PROTOCOL.exists():raise ValueError('Claim protocol exists.')
    planned=requests()
    if len(planned)!=plan['maximum_calls']:raise ValueError('Call budget changed.')
    record={'schema':'public-report-reading-protocol-1','maximum_calls':96,'plan_sha256':sha(PLAN.read_bytes()),
            'manifest_sha256':sha((DATA/'manifest.json').read_bytes()),'requests':[{k:v for k,v in r.items() if k!='body'} for r in planned]}
    PROTOCOL.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':96}


def check():
    plan=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL);planned=requests()
    if protocol['schema']!='public-report-reading-protocol-1' or protocol['maximum_calls']!=len(planned) or len(planned)!=96 or protocol['plan_sha256']!=sha(PLAN.read_bytes()) or protocol['manifest_sha256']!=sha((DATA/'manifest.json').read_bytes()):raise ValueError('Claim protocol drift.')
    if protocol['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned] or any(len(encoded(r['body']))>plan['maximum_request_bytes'] for r in planned):raise ValueError('Claim request drift.')
    return plan,planned


def answers(raw,body):
    if raw.get('model')!=MODEL or set(raw.get('answers',{}))!=set(FIELDS):raise ValueError('Answer field or model mismatch.')
    result={}
    for field in FIELDS:
        choice,probabilities,confidence=normalize({'model':MODEL,'answers':{'cause':raw['answers'][field]}},body['questions'][field]['criteria'])
        result[field]={'choice':choice,'probabilities':probabilities,'provider_confidence':confidence}
    return result


def run(profile):
    plan,planned=check();profile_check(profile)
    if any(profile[k]!=plan[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Profile drift.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('Server-side key required.')
    OUTPUT.mkdir();(OUTPUT/'requests.json').write_text(json.dumps(planned,indent=2)+'\n')
    rows=[];reason=None;consecutive=0;opener=urllib.request.build_opener(NoRedirect())
    with (OUTPUT/'responses.jsonl').open('x') as stream:
        for req in planned:
            row={k:v for k,v in req.items() if k!='body'};row['status']='ok';start=time.perf_counter()
            try:
                wire=urllib.request.Request(profile['endpoint'],data=encoded(req['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(wire,timeout=30) as response:content=response.read(1048577)
                if len(content)>1048576:raise ValueError('Oversized provider response.')
                raw=json.loads(content);row['raw_response']=redact(raw,key)
                if not isinstance(raw,dict) or raw.get('model')!=MODEL:reason='checkpoint_mismatch';raise ValueError('Wrong model.')
                row['answers']=answers(raw,req['body']);row['usage']=raw.get('usage',{})
                tokens=row['usage'].get('input_tokens')
                if isinstance(tokens,bool) or not isinstance(tokens,int) or tokens<1:raise ValueError('Missing input usage.')
                if tokens>plan['context_tokens']:reason='reported_context_overflow';raise ValueError('Context overflow.')
            except urllib.error.HTTPError as error:row.update(status='error',error='Provider HTTP '+str(error.code));reason='provider_http_'+str(error.code)
            except (OSError,ValueError,KeyError,TypeError) as error:
                row.update(status='error',error='Validation or request failure: '+type(error).__name__)
                if isinstance(error,OSError):reason='network_error'
            row=redact(row,key);row['latency_ms']=(time.perf_counter()-start)*1000;rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            print(f"Report reading {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-report-reading-hosted-1','planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),'unattempted':len(planned)-len(rows),
             'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed','stopped_reason':reason,
             'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUTPUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows(complete=False):
    plan,planned=check();summary=load(OUTPUT/'summary.json')
    if summary['schema']!='public-report-reading-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Claim summary drift.')
    for name,digest in summary['files'].items():
        if sha((OUTPUT/name).read_bytes())!=digest:raise ValueError('Saved evidence changed.')
    if load(OUTPUT/'requests.json')!=planned:raise ValueError('Saved requests changed.')
    rows=[json.loads(line) for line in (OUTPUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(planned):raise ValueError('Extra provider calls.')
    for row,req in zip(rows,planned):
        if any(row.get(k)!=v for k,v in req.items() if k!='body') or row['status'] not in {'ok','error'}:raise ValueError('Response identity changed.')
        if row['status']=='ok':
            tokens=row['usage'].get('input_tokens')
            if answers(row['raw_response'],req['body'])!=row['answers'] or row['usage']!=row['raw_response']['usage'] or isinstance(tokens,bool) or not isinstance(tokens,int) or not 0<tokens<=plan['context_tokens']:raise ValueError('Response normalization changed.')
    failed=sum(r['status']!='ok' for r in rows);status='completed' if len(rows)==len(planned) and not failed else 'incomplete_or_failed'
    if (summary['planned'],summary['attempted'],summary['failed'],summary['unattempted'],summary['status'])!=(len(planned),len(rows),failed,len(planned)-len(rows),status):raise ValueError('Planned denominators changed.')
    if complete and (status!='completed' or summary['stopped_reason']):raise ValueError('Complete evidence required.')
    return rows,summary


def assess(rows,packets,references):
    indexed={(r['card_id'],r['arm'],r['round']):r for r in rows};refs={r['id']:r for r in references};datasets={}
    for dataset in sorted({p['dataset'] for p in packets}):
        cards=[p for p in packets if p['dataset']==dataset];arms={}
        for arm in ARMS:
            outcomes=[];rounds=[]
            for n in (1,2,3):
                for p in cards:
                    row=indexed.get((p['id'],arm,n))
                    for field in FIELDS:
                        ans=row['answers'].get(field) if row and row['status']=='ok' else None
                        reference=refs[p['id']]['answers'][field]['answer'];choice=ans['choice'] if ans else 'unavailable';display=bool(ans and ans['probabilities'][choice]>=.7)
                        outcomes.append({'id':p['id'],'field':field,'service':p['claim_sources'][field]['service'],'round':n,'choice':choice,'reference':reference,'correct':choice==reference,'displayed':display,'failed_or_missing':not bool(ans),'unknown_to_decisive':reference=='unanswerable' and choice in ('supported','contradicted')})
                rr=[o for o in outcomes if o['round']==n];groups={p['id']:[o for o in rr if o['id']==p['id']] for p in cards}
                rounds.append({'round':n,'claims':len(rr),'reports':len(cards),'correct':sum(o['correct'] for o in rr),
                    'class_total':{c:sum(o['reference']==c for o in rr) for c in CLASSES},'class_correct':{c:sum(o['reference']==c and o['correct'] for o in rr) for c in CLASSES},
                    'displayed':sum(o['displayed'] for o in rr),'displayed_correct':sum(o['displayed'] and o['correct'] for o in rr),'wrong_displayed':sum(o['displayed'] and not o['correct'] for o in rr),'withheld':sum(not o['displayed'] for o in rr),
                    'correct_displayed_support':sum(o['displayed'] and o['choice']==o['reference']=='supported' for o in rr),'reference_support':sum(o['reference']=='supported' for o in rr),
                    'unknown_to_decisive':sum(o['unknown_to_decisive'] for o in rr),'failed_or_missing':sum(o['failed_or_missing'] for o in rr),
                    'all_six_correct':sum(all(o['correct'] for o in group) for group in groups.values()),'complete_display':sum(all(o['displayed'] for o in group) for group in groups.values()),
                    'complete_correct_display':sum(all(o['displayed'] and o['correct'] for o in group) for group in groups.values()),
                    'service_results':[{'id':p['id'],'service':s,'correct':sum(o['correct'] for o in groups[p['id']] if o['service']==s),'claims':sum(o['service']==s for o in groups[p['id']])} for p in cards for s in sorted({o['service'] for o in groups[p['id']]})],
                    'confusion':{c:{v:sum(o['reference']==c and o['choice']==v for o in rr) for v in (*CLASSES,'unavailable')} for c in CLASSES}})
            arms[arm]={'per_round':rounds,'outcomes':outcomes}
        pairs=[]
        for a,b in zip(arms['atomic']['outcomes'],arms['report']['outcomes']):
            if (a['id'],a['field'],a['round'])!=(b['id'],b['field'],b['round']):raise ValueError('Pair order drift.')
            pairs.append({'id':a['id'],'field':a['field'],'round':a['round'],'fix':not a['correct'] and b['correct'] and not a['failed_or_missing'],'loss':a['correct'] and not b['correct'] and not b['failed_or_missing']})
        stable=lambda key:[{'id':p['id'],'field':f} for p in cards for f in FIELDS if all(o[key] for o in pairs if o['id']==p['id'] and o['field']==f)]
        gate=all(not r['failed_or_missing'] and not b['failed_or_missing'] and all(r['class_total'][c]>0 and r['class_correct'][c]/r['class_total'][c]>=.9 for c in CLASSES) and not r['wrong_displayed'] and r['reference_support']>0 and r['correct_displayed_support']>=r['reference_support']/2 and r['all_six_correct']/r['reports']>=.9 and r['correct']>=b['correct'] for r,b in zip(arms['report']['per_round'],arms['atomic']['per_round']))
        datasets[dataset]={'reports':len(cards),'claims':len(cards)*6,'arms':arms,'pairs':pairs,'stable_fixes':stable('fix'),'stable_losses':stable('loss'),'research_gate':gate,
            'consistency':{arm:{'stable_verdict_claims':sum(len({o['choice'] for o in arms[arm]['outcomes'] if o['id']==p['id'] and o['field']==f})==1 for p in cards for f in FIELDS),'stable_display_claims':sum(len({o['displayed'] for o in arms[arm]['outcomes'] if o['id']==p['id'] and o['field']==f})==1 for p in cards for f in FIELDS)} for arm in ARMS}}
    return datasets

def score():
    rows,summary=verified_rows();datasets=assess(rows,load(DATA/'inputs.json'),load(DATA/'references.json'))
    return {'schema':'public-report-reading-results-1','diagnostic_only':True,'reports':16,'claims':96,'service_cards':32,'recordings':16,'planned_calls':96,'questions_per_call':6,'planned_answers':576,
        'failed_or_missing_calls':summary['failed']+summary['unattempted'],'datasets':datasets,'research_gate':not(summary['failed']+summary['unattempted']) and all(d['research_gate'] for d in datasets.values()),
        'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(PROTOCOL.read_bytes()),'summary_sha256':sha((OUTPUT/'summary.json').read_bytes())}}
