"""Once-only explicit-binding diagnostic; no fresh telemetry access."""
import json,time,urllib.request,urllib.error
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_rca_trial import normalize
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_binding_features import ARMS,FIELDS,POLICY,CLASSES,EDGES
from .public_binding_data import PLAN,DATA,SOURCE,REFSOURCE,check_plan,validate
from .public_report_trial import SOURCES as PREVIOUS_SOURCES
PROTOCOL=ROOT/'checkpoints/public-claim-binding-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/public-claim-binding-results-2026-10-05.json'
OUTPUT=ROOT/'runs/public-claim-binding/diagnostic-hosted-2026-10-05-v1'
SOURCES=tuple(dict.fromkeys(PREVIOUS_SOURCES+('triage_bench/public_binding_features.py','triage_bench/public_binding_data.py','triage_bench/public_report_trial.py','scripts/run_public_reports.py')))

def plan(profile):
    from scripts.verify_public_reports import verify
    profile_check(profile);verify()
    if PLAN.exists():raise ValueError('Binding plan exists.')
    previous=load(ROOT/'checkpoints/public-report-reading-plan-2026-10-05.json')
    if any(profile[k]!=previous[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Recorded profile required.')
    record={'schema':'public-claim-binding-plan-1','decision':'User authorized explicit claim binding then service scoping on 2026-10-05.',
        'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':24000,
        'reports':16,'claims':96,'service_cards':32,'recordings':16,'rounds':3,'maximum_calls':672,'maximum_answers':1152,'arms':list(ARMS),'fields':list(FIELDS),'policy':POLICY,
        'task':'Four controlled steps: lookup replays the unchanged six-question report body; bound inserts stable C1-C6 claim IDs, exact sentence text and service in all six questions while retaining both ledgers and the original report; single filters bound to one question with the same field name and body state; scoped filters single state to the named service ledger while retaining the whole report. Compare adjacent steps separately.',
        'allocation':'All 16 frozen reports, all 96 unchanged claims and all references from the completed report-reading diagnostic. No reselection, edited sentences, changed measurements or fresh telemetry.',
        'references':'Frozen typed proposition evaluator references reused byte-for-byte. Report references and metadata never enter requests. All-six correctness requires six correct judgments, composed across six separate calls for single/scoped. Complete display requires all six probabilities >=0.70; failed/missing answers retain denominators.',
        'comparison':'Fresh lookup responses measure exact-request repeatability against historical report responses without pooling them. Lookup-to-bound isolates explicit text/service binding; bound-to-single isolates question grouping; single-to-scoped isolates removal of other-service ledger. Scoped retains original report assertions about both services; absent other-service facts are not zeros. No internal reasoning or parser capability is inferred.',
        'controls':'Numerical rules, ledgers, Choice criteria, model, context and inherited uncalibrated 0.70 threshold unchanged. Original direct-question control remains preserved but is not rerun here. Prior fitted ML predicts origin and stays unscored. Typed references are exact by construction, not unrestricted report parsing.',
        'execution':'Commit plan before preparation and exact request hashes before inference. Three serial cyclic rounds, arm order rotates by report and round; single/scoped claim order rotates. No warmup or retries. 48 calls each for lookup/bound, 288 each for single/scoped; 672 calls, 1152 verdicts. Stop on HTTP/network/model/context errors or three consecutive malformed replies. Timeout 30s, context limit 32768. No post-result tuning.',
        'scoring':'Per application/arm/class/round correctness, display errors/support/withholding, unknown-to-decisive errors, all-six report correctness, complete display, per-service results, adjacent paired fixes/losses and verdict/display consistency. Fresh lookup versus historical lookup kept separate.',
        'research_gate':'For EACH application and round each changed arm must have all own and predecessor calls successful, >=90% correct in EACH of all three reference classes, zero wrong displayed verdicts, correct displayed support >=half supported references, >=90% all-six report correctness, and total correct >=its immediate predecessor. Report all three step gates, fixes and regressions separately. Passing all gates is diagnostic capability, not proof of incremental gain; report no error opportunity if a predecessor is already entirely correct.',
        'reserves':'No new telemetry access. Protect 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves. Fresh confirmation needs separate allocation and protocol.',
        'limits':'Authored explicit numbered reports on inspected controlled application faults. Stable IDs and claim-service bindings come from stored structured metadata, not an evaluated text extractor. No real analyst report, specialist policy, held-out generalization, telecom readiness or added value versus template parsing established.',
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('checkpoints/public-report-reading-results-2026-10-05.json',str(SOURCE.relative_to(ROOT)),str(REFSOURCE.relative_to(ROOT)))}}
    PLAN.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':672,'planned_answers':1152,'fresh_cases_consumed':0}

def requests():
    validate();packets=load(DATA/'inputs.json');result=[]
    for number in (1,2,3):
        offset=number-1
        for i,packet in enumerate(packets[offset:]+packets[:offset]):
            start=(i+offset)%len(ARMS)
            for arm in ARMS[start:]+ARMS[:start]:
                fields=(None,) if arm in ('lookup','bound') else FIELDS[offset:]+FIELDS[:offset]
                for field in fields:
                    body=packet['requests'][arm] if field is None else packet['claim_requests'][field][arm]
                    result.append({'id':packet['id']+'::'+arm+'::'+(field or 'all')+'::r'+str(number),'card_id':packet['id'],'field':field,'arm':arm,'round':number,'request_sha256':sha(encoded(body)),'body':body})
    return result

def freeze():
    plan=check_plan()
    if PROTOCOL.exists():raise ValueError('Binding protocol exists.')
    planned=requests()
    if len(planned)!=plan['maximum_calls']:raise ValueError('Call budget changed.')
    record={'schema':'public-claim-binding-protocol-1','maximum_calls':672,'plan_sha256':sha(PLAN.read_bytes()),
            'manifest_sha256':sha((DATA/'manifest.json').read_bytes()),'requests':[{k:v for k,v in r.items() if k!='body'} for r in planned]}
    PROTOCOL.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':672}


def check():
    plan=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL);planned=requests()
    if protocol['schema']!='public-claim-binding-protocol-1' or protocol['maximum_calls']!=len(planned) or len(planned)!=672 or protocol['plan_sha256']!=sha(PLAN.read_bytes()) or protocol['manifest_sha256']!=sha((DATA/'manifest.json').read_bytes()):raise ValueError('Binding protocol drift.')
    if protocol['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned] or any(len(encoded(r['body']))>plan['maximum_request_bytes'] for r in planned):raise ValueError('Binding request drift.')
    return plan,planned


def answers(raw,body):
    if raw.get('model')!=MODEL or set(raw.get('answers',{}))!=set(body['questions']):raise ValueError('Answer field or model mismatch.')
    result={}
    for field in body['questions']:
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
            print(f"Claim binding {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-claim-binding-hosted-1','planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),'unattempted':len(planned)-len(rows),
             'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed','stopped_reason':reason,
             'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUTPUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows(complete=False):
    plan,planned=check();summary=load(OUTPUT/'summary.json')
    if summary['schema']!='public-claim-binding-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Binding summary drift.')
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
    indexed={(r['card_id'],r['arm'],r['round'],r['field']):r for r in rows};refs={r['id']:r for r in references};datasets={}
    for dataset in sorted({p['dataset'] for p in packets}):
        cards=[p for p in packets if p['dataset']==dataset];arms={}
        for arm in ARMS:
            outcomes=[];rounds=[]
            for n in (1,2,3):
                for p in cards:
                    for field in FIELDS:
                        row=indexed.get((p['id'],arm,n,None if arm in ('lookup','bound') else field))
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
        pairs=[];gates={};steps={}
        for before,after in EDGES:
            edge=before+'__'+after;ep=[]
            for a,b in zip(arms[before]['outcomes'],arms[after]['outcomes']):
                if (a['id'],a['field'],a['round'])!=(b['id'],b['field'],b['round']):raise ValueError('Binding pair order drift.')
                ep.append({'id':a['id'],'field':a['field'],'round':a['round'],'edge':edge,'fix':not a['correct'] and b['correct'] and not a['failed_or_missing'],'loss':a['correct'] and not b['correct'] and not b['failed_or_missing']})
            pairs.extend(ep)
            stable=lambda key:[{'id':p['id'],'field':f} for p in cards for f in FIELDS if all(o[key] for o in ep if o['id']==p['id'] and o['field']==f)]
            gates[after]=all(not r['failed_or_missing'] and not b['failed_or_missing'] and all(r['class_total'][c]>0 and r['class_correct'][c]/r['class_total'][c]>=.9 for c in CLASSES) and not r['wrong_displayed'] and r['reference_support']>0 and r['correct_displayed_support']>=r['reference_support']/2 and r['all_six_correct']/r['reports']>=.9 and r['correct']>=b['correct'] for r,b in zip(arms[after]['per_round'],arms[before]['per_round']))
            steps[edge]={'stable_fixes':stable('fix'),'stable_losses':stable('loss'),'predecessor_error_opportunities':[r['claims']-r['correct']-r['failed_or_missing'] for r in arms[before]['per_round']],'no_error_opportunity':all(r['correct']==r['claims'] for r in arms[before]['per_round'])}
        datasets[dataset]={'reports':len(cards),'claims':len(cards)*6,'arms':arms,'pairs':pairs,'steps':steps,'step_gates':gates,'research_gate':all(gates.values()),
            'consistency':{arm:{'stable_verdict_claims':sum(len({o['choice'] for o in arms[arm]['outcomes'] if o['id']==p['id'] and o['field']==f})==1 for p in cards for f in FIELDS),'stable_display_claims':sum(len({o['displayed'] for o in arms[arm]['outcomes'] if o['id']==p['id'] and o['field']==f})==1 for p in cards for f in FIELDS)} for arm in ARMS}}
    return datasets

def score():
    rows,summary=verified_rows();datasets=assess(rows,load(DATA/'inputs.json'),load(DATA/'references.json'))
    return {'schema':'public-claim-binding-results-1','diagnostic_only':True,'reports':16,'claims':96,'service_cards':32,'recordings':16,'planned_calls':672,'questions_per_call':{'lookup':6,'bound':6,'single':1,'scoped':1},'planned_answers':1152,
        'failed_or_missing_calls':summary['failed']+summary['unattempted'],'datasets':datasets,'research_gate':not(summary['failed']+summary['unattempted']) and all(d['research_gate'] for d in datasets.values()),
        'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(PROTOCOL.read_bytes()),'summary_sha256':sha((OUTPUT/'summary.json').read_bytes())}}
