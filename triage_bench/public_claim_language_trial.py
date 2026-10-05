"""Once-only written-claim diagnostic with immutable numerical references."""
import json,time,urllib.request,urllib.error
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_rca_trial import normalize
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_claim_language_features import ARMS,FIELDS,POLICY,CLASSES,FORMS
from .public_claim_language_data import PLAN,DATA,SOURCE,REFSOURCE,check_plan,validate
from .public_claim_trial import SOURCES as PREVIOUS_SOURCES

PROTOCOL=ROOT/'checkpoints/public-claim-language-protocol-2026-10-05.json'
RESULT=ROOT/'checkpoints/public-claim-language-results-2026-10-05.json'
OUTPUT=ROOT/'runs/public-claim-language/diagnostic-hosted-2026-10-05-v1'
SOURCES=tuple(dict.fromkeys(PREVIOUS_SOURCES+('triage_bench/public_claim_language_features.py','triage_bench/public_claim_language_data.py','triage_bench/public_claim_language_trial.py','scripts/run_public_claim_language.py')))

def plan(profile):
    from scripts.verify_public_claims import verify
    profile_check(profile);verify()
    if PLAN.exists():raise ValueError('Language plan exists.')
    previous=load(ROOT/'checkpoints/public-claim-assessment-plan-2026-10-05.json')
    if any(profile[k]!=previous[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Recorded profile required.')
    record={'schema':'public-claim-language-plan-1','decision':'User authorized wording diagnostic on 2026-10-05.',
        'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':24000,
        'propositions':152,'statements':456,'service_cards':32,'recordings':16,'rounds':3,'maximum_calls':456,'arms':list(ARMS),'fields':list(FIELDS),'forms':list(FORMS),'policy':POLICY,
        'task':'Three meaning-preserving wordings of one typed proposition per call. Independent Choice questions share an unchanged ledger and verdict instructions. No one-of-each-class composition. Field roles shuffled deterministically; no role, selection, reference or proposition metadata in requests.',
        'allocation':'All 96 previous propositions, one recorded-count proposition per card (32), and one signed-direction proposition on a hash-selected eligible actual zero per qualifying card (24). No altered observations. Selection uses source facts and fixed hashes only. Polarity of added propositions chosen by hash independently of verdict. All 16 inspected recordings remain correlated.',
        'wording':'Canonical frozen wording, direct numerical/active paraphrase, and alternate wording. Numerical alternatives deliberately use not below, not at least, neither zero nor negative and negated count quantifiers. Health and causality use scope-preserving rephrasing; health does not equate not unhealthy with healthy. Authored templates reviewed for proposition-level equivalence before calls; no specialist review claimed.',
        'comparison':'Fresh canonical control versus plain and rephrased wording in the new request structure. Ledger, service facts, eligibility, thresholds, model and criteria unchanged. Historical canonical responses remain preserved and are not pooled with this new control. Grouping and proposition mix differ from the previous diagnostic, so changes across studies cannot be attributed to wording alone.',
        'references':'Use the frozen independent typed-proposition evaluator on unchanged source observations. Missing mapped trace counts remain unknown; explicit recorded zero is numeric. Eligibility makes ineligible threshold/direction claims unanswerable. Health and cause remain unanswerable. No report generation, injection key or fetched source file.',
        'controls':'Typed evaluator is exact by construction, not a parser for arbitrary reports. Prior fitted ML predicts incident origin, so remains unscored. No ML fit or new model provider.',
        'execution':'Commit plan before preparation and exact request hashes before once-only serial calls. Three cyclic rounds, no retries/warmup. Preserve all planned question denominators. Stop HTTP/network/model/context errors or three consecutive malformed replies. 30s timeout; reported input usage must fit 32768 tokens.',
        'scoring':'Per application/form/class/round: verdict correctness, displayed correctness, false support and false contradiction, supported coverage, unknown-to-decisive errors, wording consistency, repeated regressions/fixes, and separate original/count/actual-zero strata. Selected probability >=0.70 displays; uncalibrated inherited diagnostic boundary.',
        'research_gate':'All calls succeed. In EACH application and round BOTH plain and rephrased reach >=90% correctness for EVERY reference class, display zero wrong verdicts of any class, display at least half of supported references correctly, and match or exceed the fresh canonical correct count. Canonical errors stay visible. Diagnostic checks, not operational validation or permission to consume protected telemetry.',
        'reserves':'No new data access. Protect 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves. Fresh confirmation requires a separate allocation and frozen protocol.',
        'limits':'152 authored propositions and 456 templated wordings on inspected controlled application telemetry, not real reports or held-out incidents. Rephrased triples and matched opposite propositions are correlated; no claim of 456 independent examples. Real world ambiguity, multiple statements and specialist policy remain untested.',
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('checkpoints/public-claim-assessment-plan-2026-10-05.json','checkpoints/public-claim-assessment-results-2026-10-05.json',str(SOURCE.relative_to(ROOT)),str(REFSOURCE.relative_to(ROOT)))}}
    PLAN.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':456,'propositions':152,'fresh_cases_consumed':0}


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
    record={'schema':'public-claim-language-protocol-1','maximum_calls':456,'plan_sha256':sha(PLAN.read_bytes()),
            'manifest_sha256':sha((DATA/'manifest.json').read_bytes()),'requests':[{k:v for k,v in r.items() if k!='body'} for r in planned]}
    PROTOCOL.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':456}


def check():
    plan=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL);planned=requests()
    if protocol['schema']!='public-claim-language-protocol-1' or protocol['maximum_calls']!=len(planned) or len(planned)!=456 or protocol['plan_sha256']!=sha(PLAN.read_bytes()) or protocol['manifest_sha256']!=sha((DATA/'manifest.json').read_bytes()):raise ValueError('Claim protocol drift.')
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
            print(f"Claim language {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-claim-language-hosted-1','planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),'unattempted':len(planned)-len(rows),
             'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed','stopped_reason':reason,
             'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUTPUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows(complete=False):
    plan,planned=check();summary=load(OUTPUT/'summary.json')
    if summary['schema']!='public-claim-language-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Claim summary drift.')
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
    indexed={(r['card_id'],r['round']):r for r in rows};refs={r['id']:r for r in references};datasets={}
    for dataset in sorted({p['dataset'] for p in packets}):
        cards=[p for p in packets if p['dataset']==dataset];ids=[p['id'] for p in cards];forms={}
        for form in FORMS:
            outcomes=[];rounds=[]
            for n in (1,2,3):
                for p in cards:
                    row=indexed.get((p['id'],n));ans=row['answers'].get(p['form_fields'][form]) if row and row['status']=='ok' else None
                    choice=ans['choice'] if ans else 'unavailable';reference=refs[p['id']]['answer'];display=bool(ans and ans['probabilities'][choice]>=.7)
                    outcomes.append({'id':p['id'],'round':n,'choice':choice,'reference':reference,'selection':p['selection'],'correct':choice==reference,'displayed':display,
                        'false_displayed_support':display and choice=='supported' and reference!='supported','false_displayed_contradiction':display and choice=='contradicted' and reference!='contradicted',
                        'unknown_to_decisive':reference=='unanswerable' and choice in ('supported','contradicted'),
                        'correct_displayed_support':display and choice==reference=='supported','failed_or_missing':not bool(ans)})
                rr=[r for r in outcomes if r['round']==n]
                rounds.append({'round':n,'propositions':len(rr),'correct':sum(r['correct'] for r in rr),'class_correct':{c:sum(r['correct'] for r in rr if r['reference']==c) for c in CLASSES},'class_total':{c:sum(r['reference']==c for r in rr) for c in CLASSES},
                    'displayed':sum(r['displayed'] for r in rr),'displayed_correct':sum(r['displayed'] and r['correct'] for r in rr),'wrong_displayed':sum(r['displayed'] and not r['correct'] for r in rr),'withheld':sum(not r['displayed'] for r in rr),
                    'false_displayed_support':sum(r['false_displayed_support'] for r in rr),'false_displayed_contradiction':sum(r['false_displayed_contradiction'] for r in rr),
                    'correct_displayed_support':sum(r['correct_displayed_support'] for r in rr),'reference_support':sum(r['reference']=='supported' for r in rr),'unknown_to_decisive':sum(r['unknown_to_decisive'] for r in rr),'failed_or_missing':sum(r['failed_or_missing'] for r in rr),
                    'strata':{s:{'total':sum(r['selection']==s for r in rr),'correct':sum(r['correct'] for r in rr if r['selection']==s),'wrong_displayed':sum(r['displayed'] and not r['correct'] for r in rr if r['selection']==s)} for s in ('original_claim','recorded_counts','measured_zero')},
                    'confusion':{c:{v:sum(r['reference']==c and r['choice']==v for r in rr) for v in (*CLASSES,'unavailable')} for c in CLASSES}})
            forms[form]={'per_round':rounds,'outcomes':outcomes,'stable_correct_ids':[i for i in ids if all(r['correct'] for r in outcomes if r['id']==i)]}
        pairs=[]
        for form in ('plain','rephrased'):
            for i in ids:
                for n in (1,2,3):
                    a=next(r for r in forms['canonical']['outcomes'] if (r['id'],r['round'])==(i,n));b=next(r for r in forms[form]['outcomes'] if (r['id'],r['round'])==(i,n))
                    pairs.append({'id':i,'form':form,'round':n,'fix':not a['correct'] and b['correct'] and not a['failed_or_missing'],'loss':a['correct'] and not b['correct'] and not b['failed_or_missing']})
        consistency=[{'round':n,'all_wordings_correct':sum(all(next(r for r in forms[f]['outcomes'] if r['id']==i and r['round']==n)['correct'] for f in FORMS) for i in ids),
            'same_verdict':sum(len({next(r for r in forms[f]['outcomes'] if r['id']==i and r['round']==n)['choice'] for f in FORMS})==1 for i in ids)} for n in (1,2,3)]
        gates={f:all(not r['failed_or_missing'] and all(r['class_total'][c]>0 and r['class_correct'][c]/r['class_total'][c]>=.9 for c in CLASSES) and not r['wrong_displayed'] and r['reference_support']>0 and r['correct_displayed_support']>=r['reference_support']/2 and r['correct']>=b['correct'] for r,b in zip(forms[f]['per_round'],forms['canonical']['per_round'])) for f in ('plain','rephrased')}
        datasets[dataset]={'propositions':len(ids),'service_cards':len({p['source_card'] for p in cards}),'recordings':len({p['case_id'] for p in cards}),'forms':forms,'pairs':pairs,'consistency':consistency,'form_gates':gates,'research_gate':all(gates.values()),
            'stable_fixes':[{ 'id':i,'form':f} for f in ('plain','rephrased') for i in ids if all(p['fix'] for p in pairs if p['id']==i and p['form']==f)],
            'stable_losses':[{ 'id':i,'form':f} for f in ('plain','rephrased') for i in ids if all(p['loss'] for p in pairs if p['id']==i and p['form']==f)]}
    return datasets

def score():
    rows,summary=verified_rows();datasets=assess(rows,load(DATA/'inputs.json'),load(DATA/'references.json'))
    return {'schema':'public-claim-language-results-1','diagnostic_only':True,'propositions':152,'statements':456,'service_cards':32,'recordings':16,'planned_calls':456,'questions_per_call':3,'planned_answers':1368,
        'failed_or_missing_calls':summary['failed']+summary['unattempted'],'datasets':datasets,'research_gate':not(summary['failed']+summary['unattempted']) and all(d['research_gate'] for d in datasets.values()),
        'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(PROTOCOL.read_bytes()),'summary_sha256':sha((OUTPUT/'summary.json').read_bytes())}}
