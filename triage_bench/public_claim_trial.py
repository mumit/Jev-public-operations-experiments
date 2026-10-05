"""Once-only written-claim diagnostic with immutable numerical references."""
import json,time,urllib.request,urllib.error
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_rca_trial import normalize
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_claim_features import ARMS,FIELDS,POLICY,CLASSES
from .public_claim_data import PLAN,DATA,SOURCE,check_plan,validate
from .public_evidence_trial import SOURCES as PREVIOUS_SOURCES

PROTOCOL=ROOT/'checkpoints/public-claim-assessment-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/public-claim-assessment-results-2026-10-05.json'
OUTPUT=ROOT/'runs/public-claim-assessment/diagnostic-hosted-2026-10-05-v1'
SOURCES=tuple(dict.fromkeys(PREVIOUS_SOURCES+('triage_bench/public_claim_features.py','triage_bench/public_claim_reference.py','triage_bench/public_claim_data.py','triage_bench/public_claim_trial.py','scripts/run_public_claims.py')))


def plan(profile):
    from scripts.verify_public_evidence import verify
    profile_check(profile);verify()
    if PLAN.exists():raise ValueError('Claim plan already exists.')
    previous=load(ROOT/'checkpoints/public-evidence-assessment-plan-2026-10-04.json')
    if any(profile[k]!=previous[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded Jev profile.')
    record={'schema':'public-claim-assessment-plan-1','decision':'User selected written-claim assessment on 2026-10-05.',
        'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':24000,
        'cards':32,'claims':96,'recordings':16,'rounds':3,'arms':list(ARMS),'fields':list(FIELDS),'maximum_calls':192,'primary':'ledger','policy':POLICY,
        'task':'Judge each authored written statement as supported, contradicted or unanswerable from supplied telemetry. Three independent Choice questions share one service observation per call; they cannot see each other responses.',
        'selection':'Reuse all 32 evidence-assessment service cards from 16 inspected recordings. Select a hash-ranked decidable proposition and its opposite plus a hash-ranked unanswerable proposition. Shuffle their field positions by hash. Each card contains one of each verdict; this balance is not supplied in requests. No injected label, source filename, prior prediction or reference answer enters requests.',
        'claims':'Fixed templates cover metric magnitude, signed direction, duration magnitude and recorded span adequacy; unanswerable variants add insufficient observations, service health and causality. Positive and negative wording applies to multiple verdicts. These are constructed test claims, not actual analyst reports. Matched opposite statements share a fact and remain correlated.',
        'references':'Independent typed-proposition evaluator reads raw observations. Explicit numerical eligibility and thresholds match questions; an ineligible metric or duration claim is unanswerable, not contradicted. An absent trace mapping supplies no count; an explicit recorded zero is different. Neither establishes health or causality. Neither health nor incident origin is inferable here. Verdicts and proposition metadata stay separate from requests.',
        'comparison':'Raw observations versus a fact ledger replacing their representation. The ledger preserves original metric values and trace observations, adds absolute changes, eligibility flags and eligible duration arithmetic. Identical statements/questions. No claim-specific verdict, causal label or policy material/quiet classification enters the ledger.',
        'controls':'The typed reference evaluator is exact by construction and is not a parser for unrestricted analyst text. Earlier fitted ML predicts originating service and is unscored for this different target. No new ML fit.',
        'execution':'Commit plan before preparation and exact protocol before calls. Three serial cyclic rounds, no retries or warmup; 30s timeout. Stop on network/HTTP/model/context errors or three consecutive malformed replies. Retain failed/missing questions in planned denominators.',
        'scoring':'Per application, arm, class and round: verdict accuracy, three-claim card accuracy, displayed verdict accuracy at selected probability >=0.70, false displayed support, correct displayed support coverage, confusion counts, paired fixes/losses and stability. Probabilities are not calibrated. Missing answers are unavailable.',
        'research_gate':'Ledger requires complete calls, >=90% correctness for each reference class in each round in each application, zero false displayed supported verdicts, at least half of reference supported claims displayed correctly in every round, and total correct verdicts no lower than raw observations in every application/round. Author-set diagnostic criteria; no automatic promotion or new data access.',
        'reserves':'No fresh telemetry access. Protect 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves. A separate frozen allocation/protocol precedes any fresh generalization study.',
        'limits':'96 templated claims on 32 selected cards from 16 inspected controlled public code-fault recordings. Not held-out incidents, authentic reports, specialist references or evidence of telecom readiness. Balance and opposite claims can induce artifacts; model instruction forbids cross-statement inference but shared state does not establish answer independence statistically.',
        'documentation':'https://docs.typesafe.ai/introduction; checked 2026-10-04. Independent Choice questions share state.',
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('checkpoints/public-evidence-assessment-plan-2026-10-04.json','checkpoints/public-evidence-assessment-results-2026-10-04.json',str(SOURCE.relative_to(ROOT)))}}
    PLAN.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':192,'claims':96,'fresh_cases_consumed':0}


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
    record={'schema':'public-claim-assessment-protocol-1','maximum_calls':192,'plan_sha256':sha(PLAN.read_bytes()),
            'manifest_sha256':sha((DATA/'manifest.json').read_bytes()),'requests':[{k:v for k,v in r.items() if k!='body'} for r in planned]}
    PROTOCOL.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':192}


def check():
    plan=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL);planned=requests()
    if protocol['schema']!='public-claim-assessment-protocol-1' or protocol['maximum_calls']!=len(planned) or len(planned)!=192 or protocol['plan_sha256']!=sha(PLAN.read_bytes()) or protocol['manifest_sha256']!=sha((DATA/'manifest.json').read_bytes()):raise ValueError('Claim protocol drift.')
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
            print(f"Claim assessment {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-claim-assessment-hosted-1','planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),'unattempted':len(planned)-len(rows),
             'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed','stopped_reason':reason,
             'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUTPUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows(complete=False):
    plan,planned=check();summary=load(OUTPUT/'summary.json')
    if summary['schema']!='public-claim-assessment-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Claim summary drift.')
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
        cards=[p for p in packets if p['dataset']==dataset];ids=[p['id'] for p in cards];arms={}
        for arm in ARMS:
            outcomes=[];rounds=[]
            for n in (1,2,3):
                for identifier in ids:
                    row=indexed.get((identifier,arm,n));ans=row['answers'] if row and row['status']=='ok' else {}
                    for field in FIELDS:
                        reference=refs[identifier]['answers'][field]['answer'];answer=ans.get(field);choice=answer['choice'] if answer else 'unavailable'
                        displayed=bool(answer and answer['probabilities'][choice]>=.7)
                        outcomes.append({'id':identifier,'field':field,'round':n,'choice':choice,'reference':reference,'correct':choice==reference,'displayed':displayed,
                            'false_displayed_support':displayed and choice=='supported' and reference!='supported',
                            'correct_displayed_support':displayed and choice==reference=='supported','failed_or_missing':not bool(answer)})
                rr=[r for r in outcomes if r['round']==n]
                rounds.append({'round':n,'claims':len(rr),'correct':sum(r['correct'] for r in rr),'class_correct':{c:sum(r['correct'] for r in rr if r['reference']==c) for c in CLASSES},
                    'class_total':{c:sum(r['reference']==c for r in rr) for c in CLASSES},'all_three_correct':sum(all(r['correct'] for r in rr if r['id']==i) for i in ids),
                    'displayed':sum(r['displayed'] for r in rr),'displayed_correct':sum(r['displayed'] and r['correct'] for r in rr),'withheld':sum(not r['displayed'] for r in rr),
                    'false_displayed_support':sum(r['false_displayed_support'] for r in rr),'correct_displayed_support':sum(r['correct_displayed_support'] for r in rr),
                    'reference_support':sum(r['reference']=='supported' for r in rr),'failed_or_missing':sum(r['failed_or_missing'] for r in rr),
                    'confusion':{c:{v:sum(r['reference']==c and r['choice']==v for r in rr) for v in (*CLASSES,'unavailable')} for c in CLASSES}})
            stable=[{'id':i,'field':f} for i in ids for f in FIELDS if all(r['correct'] for r in outcomes if r['id']==i and r['field']==f)]
            arms[arm]={'per_round':rounds,'outcomes':outcomes,'stable_correct_claims':stable}
        pairs=[]
        for identifier in ids:
            for field in FIELDS:
                for n in (1,2,3):
                    a=next(r for r in arms['observations']['outcomes'] if (r['id'],r['field'],r['round'])==(identifier,field,n));b=next(r for r in arms['ledger']['outcomes'] if (r['id'],r['field'],r['round'])==(identifier,field,n))
                    pairs.append({'id':identifier,'field':field,'round':n,'fix':not a['correct'] and b['correct'] and not a['failed_or_missing'],'loss':a['correct'] and not b['correct'] and not b['failed_or_missing']})
        gate=all(not r['failed_or_missing'] and all(r['class_correct'][c]/r['class_total'][c]>=.9 for c in CLASSES) and not r['false_displayed_support'] and r['correct_displayed_support']>=r['reference_support']/2 and r['correct']>=b['correct'] for r,b in zip(arms['ledger']['per_round'],arms['observations']['per_round']))
        datasets[dataset]={'cards':len(ids),'claims':len(ids)*3,'recordings':len({c['case_id'] for c in cards}),'arms':arms,'pairs':pairs,
            'stable_fixes':[{'id':i,'field':f} for i in ids for f in FIELDS if all(r['fix'] for r in pairs if r['id']==i and r['field']==f)],
            'stable_losses':[{'id':i,'field':f} for i in ids for f in FIELDS if all(r['loss'] for r in pairs if r['id']==i and r['field']==f)],'research_gate':gate}
    return datasets

def score():
    rows,summary=verified_rows();datasets=assess(rows,load(DATA/'inputs.json'),load(DATA/'references.json'))
    return {'schema':'public-claim-assessment-results-1','diagnostic_only':True,'cards':32,'claims':96,'recordings':16,'planned_calls':192,'questions_per_call':3,'planned_answers':576,
        'failed_or_missing_calls':summary['failed']+summary['unattempted'],'datasets':datasets,'research_gate':not(summary['failed']+summary['unattempted']) and all(d['research_gate'] for d in datasets.values()),
        'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(PROTOCOL.read_bytes()),'summary_sha256':sha((OUTPUT/'summary.json').read_bytes())}}
