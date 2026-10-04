"""Bounded fresh-development temporal comparison, with failure-inclusive shortlist scores."""
import json,time,urllib.request,urllib.error
from pathlib import Path
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed,verify_local
from .public_rca_trial import MODEL,normalize
from .public_rca_models import infer
from .public_repeat_trial import check as check_history
from .public_temporal_data import validate
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import profile_check

DATA=ROOT/'runs/public-temporal/development-2026-10-04-v1'
PLAN=ROOT/'checkpoints/public-temporal-preparation-2026-10-04.json'
PROTOCOL=ROOT/'checkpoints/public-temporal-development-protocol-2026-10-04.json'
OUTPUT=ROOT/'runs/public-temporal/comparison-development-2026-10-04-v1'
ARMS=('named','temporal');ROUNDS=3
SOURCES=('triage_bench/public_temporal_trial.py','scripts/run_public_temporal.py','uv.lock')


def requests():
    validate(PLAN,DATA);check_history(load(ROOT/'checkpoints/public-repeat-protocol-2026-10-03.json'))
    packets=load(DATA/'development.inputs.json');result=[]
    for number in range(1,ROUNDS+1):
        offset=number-1;ordered=packets[offset:]+packets[:offset]
        for index,p in enumerate(ordered):
            first=(index+number-1)%2
            for arm in ARMS[first:]+ARMS[:first]:
                request=p['requests'][arm];result.append({'id':f"{p['id']}::{arm}::r{number}",'case_id':p['id'],'arm':arm,'round':number,'body':request,'request_sha256':sha(encoded(request))})
    return result


def shortlist(row):
    if not row or row['status']!='ok' or row['choice']=='insufficient_evidence':return []
    # Keep the selected tied winner first, then break remaining ties by service ID.
    ordered=sorted(((s,p) for s,p in row['probabilities'].items() if s!='insufficient_evidence' and p>0),key=lambda item:(-item[1],item[0]!=row['choice'],item[0]))
    return [s for s,p in ordered[:3]]


def controls():
    original=load(ROOT/'checkpoints/public-format-protocol-2026-10-03.json')
    model=verify_local(ROOT/original['local'],ROOT/original['historical_data'])
    return {p['id']:infer(p['state'],model) for p in load(DATA/'development.inputs.json')}


def freeze(profile):
    profile_check(profile)
    if PROTOCOL.exists():raise ValueError('Development protocol exists.')
    probe=load(ROOT/'checkpoints/public-context-probe-2026-10-04.json');result=load(ROOT/'runs/public-temporal/context-probe-2026-10-04-v1/result.json')
    if result['protocol_sha256']!=sha((ROOT/'checkpoints/public-context-probe-2026-10-04.json').read_bytes()) or result['status']!='accepted' or not result['reported_input_within_declared_capacity']:raise ValueError('Accepted capacity probe required.')
    if result['raw_response']['model']!=MODEL or result['input_tokens']!=result['raw_response']['usage']['input_tokens']:raise ValueError('Invalid capacity evidence.')
    expected=load(ROOT/'checkpoints/public-repeat-protocol-2026-10-03.json')
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(expected['model'],expected['endpoint'],expected['context_tokens']):raise ValueError('Keep the original hosted profile.')
    plan=requests();maximum=max(len(encoded(r['body'])) for r in plan)
    if maximum!=result['request_bytes'] or maximum!=probe['request_bytes']:raise ValueError('Prepared requests exceed accepted size probe.')
    p={'schema':'public-temporal-development-protocol-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'maximum_calls':108,'rounds':ROUNDS,'cases':18,'groups':6,'maximum_request_bytes':maximum,
        'requests':[{k:v for k,v in r.items() if k!='body'} for r in plan],
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (PLAN,DATA/'manifest.json',ROOT/'checkpoints/public-context-probe-2026-10-04.json',ROOT/'runs/public-temporal/context-probe-2026-10-04-v1/result.json')},
        'comparison':'Same 18 development cases and cause-selection question. Temporal adds only calculated latency windows to the unchanged named measurements. Three serial rounds rotate case and arm order. No answer metadata enters requests.',
        'capacity':'All request byte sizes are bounded by the accepted 79,840-byte temporal probe (30,471 billable input tokens). This is empirical sizing evidence, not an exact tokenizer count for every request. Provider context rejection stops execution; no truncation.',
        'shortlist':'At most three positive-probability observed services in descending probability. Selected tied winner first; remaining ties by service ID. Withhold on insufficient_evidence, failed or missing response. Cause unconfirmed. No new display threshold is fitted.',
        'reporting':'Per-round first-choice correctness, shortlist inclusion and size, wrong leads, withheld responses, distribution, distinct-case choice/shortlist consistency and paired fixes/regressions. Frozen Online Boutique ML is a transfer control; its scores are not Jev probabilities.',
        'stop':'One execution; no retries/warmup, timeout 30 seconds. Stop on HTTP/network/version failure, reported input above capacity or three consecutive malformed responses. Full planned denominators.',
        'gate':'No automatic calibration promotion. An analyst shortlist has a different error/coverage tradeoff from one displayed service; obtain the intended inclusion-versus-withholding criterion before freezing a calibration boundary.',
        'limits':'Development exploration, six correlated groups. Existing 36 Sock Shop reserve and 72 later Train Ticket cases remain undownloaded. Three rounds are not new held-out cases or long-term reliability.'}
    with PROTOCOL.open('x') as stream:stream.write(json.dumps(p,indent=2)+'\n')
    return {'status':'frozen','cases':18,'maximum_calls':108,'rounds':ROUNDS}


def check():
    p=load(PROTOCOL)
    if p['schema']!='public-temporal-development-protocol-1' or p['maximum_calls']!=108 or p['rounds']!=3:raise ValueError('Changed development protocol.')
    for mapping in ('source_sha256','evidence_sha256'):
        for name,digest in p[mapping].items():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or sha((ROOT/path).read_bytes())!=digest:raise ValueError('Development source or evidence drift.')
    planned=requests()
    if [{k:v for k,v in r.items() if k!='body'} for r in planned]!=p['requests'] or max(len(encoded(r['body'])) for r in planned)!=p['maximum_request_bytes']:raise ValueError('Development request drift.')
    return p,planned


def run(profile):
    p,planned=check();committed(PROTOCOL);profile_check(profile)
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(p['model'],p['endpoint'],p['context_tokens']):raise ValueError('Profile differs from freeze.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('Server-side Jev key required.')
    OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.mkdir()
    (OUTPUT/'requests.json').write_text(json.dumps(planned,indent=2)+'\n');local=controls();(OUTPUT/'controls.json').write_text(json.dumps(local,indent=2)+'\n')
    rows=[];reason=None;consecutive=0;opener=urllib.request.build_opener(NoRedirect())
    with (OUTPUT/'responses.jsonl').open('x') as stream:
        for request in planned:
            row={k:v for k,v in request.items() if k!='body'};row['status']='ok';start=time.perf_counter()
            try:
                wire=urllib.request.Request(profile['endpoint'],data=encoded(request['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(wire,timeout=30) as response:content=response.read(1048577)
                if len(content)>1048576:raise ValueError('Oversized response.')
                raw=json.loads(content);row['raw_response']=redact(raw,key)
                if not isinstance(raw,dict) or raw.get('model')!=MODEL:reason='checkpoint_mismatch'
                row['choice'],row['probabilities'],row['provider_confidence']=normalize(raw,request['body']['questions']['cause']['criteria'])
                count=raw.get('usage',{}).get('input_tokens')
                if isinstance(count,bool) or not isinstance(count,int) or count<1:raise ValueError('Missing input usage.')
                row['usage']=raw['usage']
                if count>p['context_tokens']:reason='reported_context_overflow';raise ValueError('Input usage exceeds capacity.')
            except urllib.error.HTTPError as error:row.update(status='error',error='Provider HTTP '+str(error.code));reason='provider_http_'+str(error.code)
            except (OSError,ValueError,KeyError,TypeError) as error:
                row.update(status='error',error='Validation or request failure: '+type(error).__name__)
                if isinstance(error,OSError):reason='network_error'
            row=redact(row,key);row['latency_ms']=(time.perf_counter()-start)*1000;rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            print(f"Development {len(rows)}/108 {row['arm']} round {row['round']} {row['status']}",flush=True)
            consecutive=consecutive+1 if row['status']!='ok' else 0
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-temporal-hosted-1','planned':108,'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),
        'unattempted':108-len(rows),'status':'completed' if len(rows)==108 and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{name:sha((OUTPUT/name).read_bytes()) for name in ('requests.json','responses.jsonl','controls.json')}}
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def score():
    p,planned=check();s=load(OUTPUT/'summary.json')
    if s['protocol_sha256']!=sha(PROTOCOL.read_bytes()):raise ValueError('Summary protocol changed.')
    for name,digest in s['files'].items():
        if name not in {'requests.json','responses.jsonl','controls.json'} or sha((OUTPUT/name).read_bytes())!=digest:raise ValueError('Development evidence changed.')
    if set(s['files'])!={'requests.json','responses.jsonl','controls.json'} or load(OUTPUT/'requests.json')!=planned or load(OUTPUT/'controls.json')!=controls():raise ValueError('Recorded requests or transfer controls changed.')
    rows=[json.loads(line) for line in (OUTPUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>108:raise ValueError('Too many responses.')
    for row,request in zip(rows,planned):
        if any(row.get(k)!=v for k,v in request.items() if k!='body') or row['status'] not in {'ok','error'}:raise ValueError('Response join changed.')
        if row['status']=='ok':
            values=normalize(row['raw_response'],request['body']['questions']['cause']['criteria'])
            if values!=(row['choice'],row['probabilities'],row['provider_confidence']) or row['usage']!=row['raw_response']['usage'] or row['usage']['input_tokens']>p['context_tokens']:raise ValueError('Changed normalized response.')
    failed=sum(r['status']!='ok' for r in rows)
    if (s['attempted'],s['failed'],s['unattempted'],s['status'])!=(len(rows),failed,108-len(rows),'completed' if len(rows)==108 and not failed else 'incomplete_or_failed'):raise ValueError('Changed planned denominator.')
    refs={r['id']:r for r in load(DATA/'development.references.json')};actual={r['id']:r for r in rows};cases=[]
    for identifier,ref in refs.items():
        case={**ref,'arms':{}}
        for arm in ARMS:
            rs=[]
            for number in range(1,4):
                row=actual.get(f'{identifier}::{arm}::r{number}');leads=shortlist(row);ok=row is not None and row['status']=='ok'
                rs.append({'round':number,'status':row['status'] if row else 'missing','choice':row['choice'] if ok else 'missing','top1_correct':ok and row['choice']==ref['target'],
                    'shortlist':leads,'target_in_shortlist':ref['target'] in leads,'wrong_leads':sum(x!=ref['target'] for x in leads),'withheld':not leads})
            case['arms'][arm]={'rounds':rs,'choice_stable':all(r['status']=='ok' for r in rs) and len({r['choice'] for r in rs})==1,
                'shortlist_stable':all(r['status']=='ok' for r in rs) and all(r['shortlist']==rs[0]['shortlist'] for r in rs)}
        cases.append(case)
    metrics={}
    for arm in ARMS:
        rounds=[]
        for n in range(3):
            rs=[c['arms'][arm]['rounds'][n] for c in cases]
            rounds.append({'round':n+1,'cases':18,'top1_correct':sum(r['top1_correct'] for r in rs),'target_in_shortlist':sum(r['target_in_shortlist'] for r in rs),'shown_shortlists':sum(not r['withheld'] for r in rs),
                'wrong_leads':sum(r['wrong_leads'] for r in rs),'total_leads':sum(len(r['shortlist']) for r in rs),'withheld':sum(r['withheld'] for r in rs),'failed_or_missing':sum(r['status']!='ok' for r in rs)})
        metrics[arm]={'choice_stable_cases':sum(c['arms'][arm]['choice_stable'] for c in cases),'shortlist_stable_cases':sum(c['arms'][arm]['shortlist_stable'] for c in cases),'per_round':rounds}
    baseline=load(OUTPUT/'controls.json');local={}
    for name in ('ml','change','resource'):
        local[name]={'cases':18,'top1_correct':sum(baseline[i][name]['choice']==r['target'] for i,r in refs.items()),
            'top3_inclusion':sum(r['target'] in [x['service'] for x in baseline[i][name]['ranking'][:3]] for i,r in refs.items())}
    paired=[{'round':n+1,'top1_fixes':[c['id'] for c in cases if not c['arms']['named']['rounds'][n]['top1_correct'] and c['arms']['temporal']['rounds'][n]['top1_correct']],
        'top1_regressions':[c['id'] for c in cases if c['arms']['named']['rounds'][n]['top1_correct'] and not c['arms']['temporal']['rounds'][n]['top1_correct']],
        'shortlist_fixes':[c['id'] for c in cases if not c['arms']['named']['rounds'][n]['target_in_shortlist'] and c['arms']['temporal']['rounds'][n]['target_in_shortlist']],
        'shortlist_regressions':[c['id'] for c in cases if c['arms']['named']['rounds'][n]['target_in_shortlist'] and not c['arms']['temporal']['rounds'][n]['target_in_shortlist']]} for n in range(3)]
    return {'schema':'public-temporal-development-assessment-1','distinct_cases':18,'distinct_groups':6,'response_slots':108,'failed_or_missing':failed+108-len(rows),
        'metrics':metrics,'controls':local,'paired':paired,'cases':cases,'evidence':{'protocol_sha256':sha(PROTOCOL.read_bytes()),'summary_sha256':sha((OUTPUT/'summary.json').read_bytes())},
        'next_gate':'Calibration remains sealed until the analyst shortlist inclusion-versus-withholding criterion is selected. No operational error rate, investigation benefit or improvement claim from development.'}
