"""Bounded, exact-request replay of inspected public inputs."""
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
from .paths import ROOT
from .public_data import sha
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import profile_check
from .public_rca_trial import MODEL,normalize
from .public_rca_stages import load,committed,verify_hosted
from .public_format_trial import check as check_original

ARMS=('compact','named','explained')
ROUNDS=5
ORIGINAL='checkpoints/public-format-protocol-2026-10-03.json'
BOUNDARY='checkpoints/public-format-boundary-2026-10-03.json'
DATA='runs/public-data/input-format-2026-10-03-v1'
SOURCES=('triage_bench/public_repeat_trial.py','triage_bench/public_repeat_results.py','scripts/run_public_repeat.py','uv.lock')


def selection(root=ROOT):
    """Predeclared targeted failures plus deterministic all-correct controls."""
    root=Path(root);all_rows=[]
    for split in ('calibration','evaluation'):
        record=load(root/(BOUNDARY if split=='calibration' else 'checkpoints/public-format-evaluation-2026-10-03.json'))
        assessment=record['assessment'] if split=='calibration' else record
        for row in assessment['outcomes']:all_rows.append({'split':split,**row})
    errors=[r for r in all_rows if any(r['choices'][a]!=r['target'] for a in ARMS)]
    controls=[]
    for fault in sorted({r['fault'] for r in all_rows}):
        eligible=[r for r in all_rows if r['fault']==fault and all(r['choices'][a]==r['target'] for a in ARMS)]
        if not eligible:raise ValueError('Missing all-correct control for '+fault)
        controls.append(min(eligible,key=lambda r:r['id']))
    chosen=sorted([dict(r,role='inspected_error') for r in errors]+[dict(r,role='all_correct_control') for r in controls],key=lambda r:r['id'])
    if len(chosen)!=12 or len({r['id'] for r in chosen})!=12:raise ValueError('Unexpected diagnostic selection.')
    return [{k:r[k] for k in ('id','split','role','group','fault')} for r in chosen]


def plan(root=ROOT):
    root=Path(root);cases=selection(root);original=load(root/ORIGINAL)
    check_original(original,root/DATA)
    saved={}
    for split in ('calibration','evaluation'):
        folder=root/f'runs/public-format/{split}-2026-10-03-v1'
        verify_hosted(folder,root/ORIGINAL,split)
        for r in load(folder/'requests.json'):saved[(r['case_id'],r['arm'])]=r
    planned=[]
    for round_number in range(1,ROUNDS+1):
        offset=(round_number-1)%len(cases);order=cases[offset:]+cases[:offset]
        for index,case in enumerate(order):
            first=(index+round_number-1)%len(ARMS);arms=ARMS[first:]+ARMS[:first]
            for arm in arms:
                source=saved[(case['id'],arm)]
                planned.append({'id':f"{case['id']}::{arm}::r{round_number}",'case_id':case['id'],'split':case['split'],
                    'arm':arm,'round':round_number,'request_sha256':source['request_sha256'],'body':source['body']})
    if len(planned)!=180:raise ValueError('Unexpected call plan.')
    return cases,planned


def freeze(output,profile):
    profile_check(profile);output=Path(output)
    if output.exists():raise ValueError('Replay protocol already exists.')
    original=load(ROOT/ORIGINAL)
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(original['model'],original['endpoint'],original['context_tokens']):raise ValueError('Keep the original hosted profile.')
    cases,planned=plan();largest=max(len(encoded(r['body'])) for r in planned)
    if largest+512>profile['context_tokens']:raise ValueError('Context byte bound failed.')
    evidence=[ORIGINAL,BOUNDARY,'checkpoints/public-format-evaluation-2026-10-03.json',DATA+'/manifest.json']
    for split in ('calibration','evaluation'):evidence += [f'runs/public-format/{split}-2026-10-03-v1/'+n for n in ('summary.json','requests.json','responses.jsonl')]
    protocol={'schema':'public-repeat-protocol-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'rounds':ROUNDS,'distinct_cases':len(cases),'distinct_groups':len({r['group'] for r in cases}),'maximum_calls':len(planned),
        'cases':cases,'requests':[{k:v for k,v in r.items() if k!='body'} for r in planned],
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{n:sha((ROOT/n).read_bytes()) for n in evidence},
        'thresholds':{a:r['threshold'] for a,r in load(ROOT/BOUNDARY)['selected'].items()},'largest_request_bytes':largest,
        'selection':'All six inspected calibration/evaluation cases with any Jev reference error, plus lexicographically first all-three-correct case for each of six faults. Selection is outcome-based and not representative.',
        'execution':'Five serial rounds. Rotate case starting position by round and first arm by position plus round. Copy exact historical request bodies; no timestamps, seeds, hints, examples or references enter the wire. No retries or warmup; timeout 30 seconds; stop on HTTP/version/network errors or three consecutive malformed responses.',
        'primary':'Per-round choices, correctness and frozen display status on 12 distinct inspected cases; per-case choice and display consistency across five rounds and separately against the original response.',
        'research_gate':'Keep reserve sealed if any call fails/is missing, any named-input displayed recommendation is wrong, or any named choice/display decision changes across the five new rounds, or named loses an originally correct service selection. This is an author-set diagnostic criterion, not an operational error budget.',
        'limits':'Five nearby rounds do not establish long-term stability, provider internals or absence of caching. Correlated and outcome-selected cases do not estimate population accuracy. Repeats are not new held-out evidence. No original thresholds or predictions change.'}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(protocol,indent=2)+'\n');return protocol


def check(protocol):
    if protocol['schema']!='public-repeat-protocol-1' or protocol['maximum_calls']!=180 or protocol['rounds']!=ROUNDS:raise ValueError('Changed replay protocol.')
    for mapping in ('source_sha256','evidence_sha256'):
        for name,digest in protocol[mapping].items():
            p=Path(name)
            if p.is_absolute() or '..' in p.parts or sha((ROOT/p).read_bytes())!=digest:raise ValueError('Replay source or evidence drift.')
    cases,planned=plan()
    if cases!=protocol['cases'] or [{k:v for k,v in r.items() if k!='body'} for r in planned]!=protocol['requests']:raise ValueError('Replay plan drift.')
    if protocol['thresholds']!={a:r['threshold'] for a,r in load(ROOT/BOUNDARY)['selected'].items()}:raise ValueError('Frozen thresholds changed.')
    return planned


def run(protocol_path,output,profile):
    protocol=load(protocol_path);planned=check(protocol);committed(protocol_path);profile_check(profile)
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(protocol['model'],protocol['endpoint'],protocol['context_tokens']):raise ValueError('Profile differs from freeze.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('A server-side Jev key is required.')
    output=Path(output).resolve()
    if not output.is_relative_to(ROOT.resolve()) or output.exists():raise ValueError('Use a new output directory under this repository.')
    claims=ROOT/'runs/public-repeat/execution';claims.mkdir(parents=True,exist_ok=True)
    claim=claims/(sha(Path(protocol_path).read_bytes())+'.json')
    try:
        with claim.open('x') as stream:json.dump({'output':str(output.relative_to(ROOT.resolve()))},stream)
    except FileExistsError as error:raise ValueError('This replay has already been claimed; another directory cannot repeat it.') from error
    output.mkdir(parents=True);(output/'requests.json').write_text(json.dumps(planned,indent=2)+'\n')
    opener=urllib.request.build_opener(NoRedirect());rows=[];reason=None;consecutive=0
    with (output/'responses.jsonl').open('x') as stream:
        for request in planned:
            row={k:v for k,v in request.items() if k!='body'};row['status']='ok';start=time.perf_counter()
            try:
                wire=urllib.request.Request(profile['endpoint'],data=encoded(request['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(wire,timeout=30) as response:content=response.read(1048577)
                if len(content)>1048576:raise ValueError('Oversized response.')
                raw=json.loads(content)
                if not isinstance(raw,dict):raise ValueError('Malformed response.')
                row['raw_response']=redact(raw,key)
                if raw.get('model')!=MODEL:reason='checkpoint_mismatch'
                row['choice'],row['probabilities'],row['provider_confidence']=normalize(raw,request['body']['questions']['cause']['criteria'])
                row['usage']=redact(raw.get('usage'),key)
            except urllib.error.HTTPError as error:
                row.update(status='error',error='Provider HTTP '+str(error.code));reason='provider_http_'+str(error.code)
            except (ValueError,KeyError,TypeError,OSError) as error:
                row.update(status='error',error='Validation or request failure: '+type(error).__name__)
                if isinstance(error,OSError):reason='network_error'
            row=redact(row,key);row['latency_ms']=(time.perf_counter()-start)*1000
            rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            consecutive=consecutive+1 if row['status']!='ok' else 0
            print(f"Replay {len(rows)}/{len(planned)} round {row['round']} {row['arm']} {row['status']}",flush=True)
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-repeat-hosted-1','planned':len(planned),'attempted':len(rows),'failed':sum(r['status']!='ok' for r in rows),
        'unattempted':len(planned)-len(rows),'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(Path(protocol_path).read_bytes()),'evidence_sha256':{p.name:sha(p.read_bytes()) for p in output.iterdir() if p.is_file()}}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary
