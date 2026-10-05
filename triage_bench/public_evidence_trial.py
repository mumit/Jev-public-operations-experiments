"""Once-only evidence-assessment diagnostic with immutable numerical references."""
import json,time,urllib.request,urllib.error
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .public_rca_trial import normalize
from .profile import MODEL,profile_check
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .public_evidence_features import ARMS,FIELDS,POLICY,compose
from .public_evidence_data import PLAN,DATA,SOURCE,check_plan,validate
from .public_trace_task_trial import SOURCES as PREVIOUS_SOURCES

PROTOCOL=ROOT/'checkpoints/public-evidence-assessment-protocol-2026-10-04.json'
RESULT=ROOT/'checkpoints/public-evidence-assessment-results-2026-10-04.json'
OUTPUT=ROOT/'runs/public-evidence-assessment/diagnostic-hosted-2026-10-04-v1'
SOURCES=tuple(dict.fromkeys(PREVIOUS_SOURCES+('triage_bench/public_evidence_features.py','triage_bench/public_evidence_reference.py','triage_bench/public_evidence_data.py','triage_bench/public_evidence_trial.py','scripts/run_public_evidence.py')))


def plan(profile):
    from scripts.verify_public_trace_task import verify
    profile_check(profile);verify()
    if PLAN.exists():raise ValueError('Evidence plan already exists.')
    previous=load(ROOT/'checkpoints/public-trace-task-plan-2026-10-04.json')
    if any(profile[k]!=previous[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded Jev profile.')
    record={'schema':'public-evidence-assessment-plan-1','decision':'User selected evidence assessment on 2026-10-04.',
        'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'maximum_request_bytes':79840,
        'cards':32,'recordings':16,'rounds':3,'arms':list(ARMS),'fields':list(FIELDS),'maximum_calls':192,'primary':'calculated','policy':POLICY,
        'task':'Four independent Choice questions per observed service: metric material change, duration material change, recorded trace coverage, and strongest eligible metric channel. Code composes metric/trace classifications into change-supported, evidence-limited or no-material-change. This is not cause inference, anomaly detection or statistical significance.',
        'selection':'Use only already inspected trace-task development packets. Two service cards per recording: largest observed eligible metric/duration change, then an absent-trace candidate if available or the smallest observed change. Hash-based ties; no injected labels or prior Jev/ML choices. This intentionally selected diagnostic is not population sampling.',
        'references':'Separate numerical reference calculator reads source observations. abs(signed metric change)>=3 with each missing fraction <=0.20; abs(duration relative change)>=0.25 with positive numeric before, numeric after and >=5 spans EACH window. Inclusive boundaries; negative changes count. Any qualifying channel suffices. No eligible channel means unknown. Adequate coverage means >=5 spans each window, absent means zero both or null, otherwise limited. Strongest eligible metric may have tied acceptable answers.',
        'comparison':'Original single-service observations versus identical observations with already declared arithmetic trace changes. Identical questions; no computed classification, root-cause key or learned label enters either state. All reference conditions are explicitly defined in questions.',
        'controls':'Exact numerical rule control, correct by construction. Existing fitted ML remains preserved but predicts originating service, so its predictions cannot be scored as evidence-assessment answers. No ML training or candidate shortlist.',
        'execution':'Commit plan before preparing cards and exact request fingerprints before calls. Three serial cyclic rounds, no retries/warmup, 30s timeout. Stop on HTTP/network/model/context errors or three consecutive malformed replies. Every planned card/field remains in failure-inclusive denominators.',
        'scoring':'Per application, arm, field and round; all-four card accuracy, tied channel acceptance, composed outcomes, >=0.70 displayed composition requiring BOTH metric and trace choice probabilities, false displayed change-support, correct change-support coverage, paired fixes/losses and repeatability. Missing/failed calls are unavailable, not fabricated answers. 0.70 is inherited for diagnosis only, not calibrated for this task.',
        'research_gate':'Calculated arm requires complete success, >=90% correctness for EACH field in EACH round in EACH application, zero false displayed change-support, at least half of reference change-supported cards displayed correctly in each round, and no less all-four card correctness than original observations. Author-set diagnostic criteria; passing does not unlock any protected panel.',
        'reserves':'No new downloads. Protect 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and all 140 RE1 reserves. Fresh generalization requires a separate committed allocation and protocol.',
        'limits':'32 selected service cards from 16 inspected code-fault recordings, correlated within case/groups. Deterministic author-defined reference policy, not specialist judgment or an originating-service label. A program can answer every question exactly; this tests model evidence reading and arithmetic, not added value over rules or analyst benefit.',
        'documentation':'https://docs.typesafe.ai/introduction; accessed 2026-10-04. Independent questions share state; application code composes answers.',
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in ('checkpoints/public-trace-task-plan-2026-10-04.json','checkpoints/public-trace-task-development-results-2026-10-04.json',str(SOURCE.relative_to(ROOT)))}}
    PLAN.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':192,'fresh_cases_consumed':0}


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
    if PROTOCOL.exists():raise ValueError('Evidence protocol exists.')
    planned=requests()
    if len(planned)!=plan['maximum_calls']:raise ValueError('Call budget changed.')
    record={'schema':'public-evidence-assessment-protocol-1','maximum_calls':192,'plan_sha256':sha(PLAN.read_bytes()),
            'manifest_sha256':sha((DATA/'manifest.json').read_bytes()),'requests':[{k:v for k,v in r.items() if k!='body'} for r in planned]}
    PROTOCOL.write_text(json.dumps(record,indent=2)+'\n');return {'status':'frozen','maximum_calls':192}


def check():
    plan=check_plan();committed(PROTOCOL);protocol=load(PROTOCOL);planned=requests()
    if protocol['schema']!='public-evidence-assessment-protocol-1' or protocol['maximum_calls']!=len(planned) or len(planned)!=192 or protocol['plan_sha256']!=sha(PLAN.read_bytes()) or protocol['manifest_sha256']!=sha((DATA/'manifest.json').read_bytes()):raise ValueError('Evidence protocol drift.')
    if protocol['requests']!=[{k:v for k,v in r.items() if k!='body'} for r in planned] or any(len(encoded(r['body']))>plan['maximum_request_bytes'] for r in planned):raise ValueError('Evidence request drift.')
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
            print(f"Evidence assessment {len(rows)}/{len(planned)} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-evidence-assessment-hosted-1','planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),'unattempted':len(planned)-len(rows),
             'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed','stopped_reason':reason,
             'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUTPUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows(complete=False):
    plan,planned=check();summary=load(OUTPUT/'summary.json')
    if summary['schema']!='public-evidence-assessment-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Evidence summary drift.')
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
                    row=indexed.get((identifier,arm,n));ref=refs[identifier]
                    ans=row['answers'] if row and row['status']=='ok' else {}
                    choices={k:v['choice'] for k,v in ans.items()}
                    correct={k:choices.get(k) in ref['answers'][k] for k in FIELDS}
                    composed=compose(choices)
                    display=bool(ans and all(ans[k]['probabilities'][choices[k]]>=.7 for k in ('metric_change','trace_change')))
                    outcomes.append({'id':identifier,'round':n,'choices':choices,'field_correct':correct,'all_correct':all(correct.values()),'composition':composed,'reference_composition':ref['composition'],
                                     'composition_correct':composed==ref['composition'],'displayed':display,'false_displayed_support':display and composed=='change_supported' and ref['composition']!='change_supported',
                                     'correct_displayed_support':display and composed==ref['composition']=='change_supported','failed_or_missing':not bool(ans)})
                rr=[r for r in outcomes if r['round']==n]
                rounds.append({'round':n,'cards':len(ids),'field_correct':{k:sum(r['field_correct'][k] for r in rr) for k in FIELDS},'all_correct':sum(r['all_correct'] for r in rr),
                               'composition_correct':sum(r['composition_correct'] for r in rr),'displayed':sum(r['displayed'] for r in rr),'withheld':sum(not r['displayed'] for r in rr),
                               'false_displayed_support':sum(r['false_displayed_support'] for r in rr),'correct_displayed_support':sum(r['correct_displayed_support'] for r in rr),
                               'reference_support':sum(refs[i]['composition']=='change_supported' for i in ids),'failed_or_missing':sum(r['failed_or_missing'] for r in rr)})
            arms[arm]={'per_round':rounds,'outcomes':outcomes,'stable_all_correct_cards':[i for i in ids if all(r['all_correct'] for r in outcomes if r['id']==i)],
                       'stable_composition_cards':[i for i in ids if len({r['composition'] for r in outcomes if r['id']==i})==1]}
        pairs=[]
        for identifier in ids:
            for n in (1,2,3):
                a=next(r for r in arms['observations']['outcomes'] if r['id']==identifier and r['round']==n);b=next(r for r in arms['calculated']['outcomes'] if r['id']==identifier and r['round']==n)
                pairs.append({'id':identifier,'round':n,'fix':not a['all_correct'] and b['all_correct'] and not a['failed_or_missing'],
                              'loss':a['all_correct'] and not b['all_correct'] and not b['failed_or_missing']})
        primary=arms['calculated']['per_round'];base=arms['observations']['per_round']
        gate=all(not r['failed_or_missing'] and all(v/len(ids)>=.9 for v in r['field_correct'].values()) and not r['false_displayed_support'] and r['reference_support']>0 and r['correct_displayed_support']>=r['reference_support']/2 and r['all_correct']>=b['all_correct'] for r,b in zip(primary,base))
        datasets[dataset]={'cards':len(ids),'recordings':len({c['case_id'] for c in cards}),'arms':arms,'pairs':pairs,
                           'stable_fixes':[i for i in ids if all(p['fix'] for p in pairs if p['id']==i)],'stable_losses':[i for i in ids if all(p['loss'] for p in pairs if p['id']==i)],'research_gate':gate,
                           'reference_counts':{k:{choice:sum(choice in refs[i]['answers'][k] for i in ids) for choice in sorted({v for i in ids for v in refs[i]['answers'][k]})} for k in FIELDS}}
    return datasets


def score():
    rows,summary=verified_rows();datasets=assess(rows,load(DATA/'inputs.json'),load(DATA/'references.json'))
    return {'schema':'public-evidence-assessment-results-1','diagnostic_only':True,'cards':32,'recordings':16,'planned_calls':192,'questions_per_call':4,'planned_answers':768,
            'failed_or_missing_calls':summary['failed']+summary['unattempted'],'datasets':datasets,'research_gate':not(summary['failed']+summary['unattempted']) and all(d['research_gate'] for d in datasets.values()),
            'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(PROTOCOL.read_bytes()),'summary_sha256':sha((OUTPUT/'summary.json').read_bytes())}}
