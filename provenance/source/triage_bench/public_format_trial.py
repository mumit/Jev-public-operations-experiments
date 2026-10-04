"""Matched Jev presentation arms, frozen before any calls."""
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

from .public_data import sha
from .public_rca_data import dump
from .public_format_data import ARMS, COUNTS, transform, validate
from .public_rca_trial import MODEL, ROOT, SOURCES as OLD_SOURCES, body as original_body, normalize
from .public_rca_stages import committed, verify_local
from .runner import NoRedirect, clean_api_key
from .experiment3.hosted import redact, encoded
from .experiment3.task_fit_trial import profile_check

SOURCES=OLD_SOURCES+('triage_bench/public_format_data.py','triage_bench/public_format_trial.py',
                     'triage_bench/public_format_stages.py','scripts/run_public_format.py')


def body(state,arm):return original_body(transform(state,arm))


def requests(data,split):
    if split not in COUNTS:raise ValueError('Unknown hosted split.')
    packets=json.loads((Path(data)/f'{split}.inputs.json').read_text());result=[]
    for i,p in enumerate(packets):
        # Rotate the first arm across cases to balance provider/time/order effects.
        for arm in ARMS[i%3:]+ARMS[:i%3]:
            request=body(p['state'],arm)
            result.append({'id':p['id']+'::'+arm,'case_id':p['id'],'arm':arm,
                           'body':request,'request_sha256':sha(encoded(request))})
    return result


def freeze(data,historical,local,output,profile):
    profile_check(profile);validate(data);model=verify_local(local,historical)
    output=Path(output)
    if output.exists():raise ValueError('Protocol already exists.')
    plans={};largest=0
    for split in COUNTS:
        rows=requests(data,split)
        largest=max(largest,max(len(encoded(r['body'])) for r in rows))
        plans[split]=[{k:r[k] for k in ('id','request_sha256')} for r in rows]
    if largest+512>profile['context_tokens']:raise ValueError('Request exceeds conservative context byte bound.')
    protocol={'schema':'public-format-protocol-1','arms':list(ARMS),'counts':COUNTS,
        'data_manifest_sha256':sha((Path(data)/'manifest.json').read_bytes()),
        'historical_data':str(Path(historical).resolve().relative_to(ROOT)),
        'historical_manifest_sha256':sha((Path(historical)/'manifest.json').read_bytes()),
        'local':str(Path(local).resolve().relative_to(ROOT)),
        'local_model_sha256':sha((Path(local)/'fitted.json').read_bytes()),
        'local_training_cases':len(model['training_ids']),
        'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},
        'requests':plans,'maximum_hosted_calls':sum(len(v) for v in plans.values()),
        'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],'largest_request_bytes':largest,
        'questions':original_body({'services':{'example':{}}})['questions'],
        'primary':'Paired failure-inclusive service matches: named versus compact; explained versus named. Same values, candidates, model and questions.',
        'development':'24 previously inspected Online Boutique cases. Fresh contemporaneous calls for all three arms; historical responses are a separate repeat diagnostic.',
        'calibration':'18 previously uninspected Sock Shop cases in six groups. Keep all arms fixed. Select each arm threshold from the historical grid by maximum coverage with zero observed errors, lowest threshold tie. No qualifying threshold means no recommendations.',
        'evaluation':'36 Sock Shop cases in twelve groups, once after committed calibration boundary. Another 36 Sock Shop cases remain undownloaded and unscored.',
        'controls':'Frozen change/resource rankings and Online Boutique-trained ML. No fitting or service-identity feature changes. ML is a transfer control, not Sock Shop-trained optimal ML.',
        'execution':'234 calls maximum; three per case, balanced cyclic arm order, serial, no retries or warmup, 30s timeout. Stop on HTTP/version/network errors or three consecutive malformed responses. Missing calls count as errors.',
        'research_criteria':'Author-set zero-observed-error display criterion; no operational error budget or minimum coverage. Every recommendation needs analyst review.',
        'selection':'Retain all three predeclared arms unchanged through evaluation. New tuning requires another protocol and untouched groups.'}
    dump(output,protocol);return protocol


def check(protocol,data):
    validate(data)
    if protocol['data_manifest_sha256']!=sha((Path(data)/'manifest.json').read_bytes()):raise ValueError('Input data drift.')
    for name,digest in protocol['source_sha256'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Frozen source drift: '+name)
    historical=ROOT/protocol['historical_data'];local=ROOT/protocol['local']
    from .public_rca_data import validate as validate_old
    validate_old(historical);verify_local(local,historical)
    if protocol['historical_manifest_sha256']!=sha((historical/'manifest.json').read_bytes()) or protocol['local_model_sha256']!=sha((local/'fitted.json').read_bytes()):raise ValueError('Historical control drift.')
    for split in COUNTS:
        planned=[{k:r[k] for k in ('id','request_sha256')} for r in requests(data,split)]
        if planned!=protocol['requests'][split]:raise ValueError('Frozen presentation requests drift.')


def claim(protocol_path,split,output):
    """A different output directory must not silently repeat a frozen split."""
    relative=str(Path(output).resolve().relative_to(ROOT.resolve()))
    directory=ROOT/'runs/public-format/execution';directory.mkdir(parents=True,exist_ok=True)
    path=directory/(sha(Path(protocol_path).read_bytes())+'-'+split+'.json')
    try:
        with path.open('x') as stream:
            json.dump({'split':split,'output':relative},stream)
    except FileExistsError as error:
        raise ValueError('This protocol split already has an execution claim; no retries or repeated evaluation.') from error


def run(data,protocol_path,output,profile,split,candidate,boundary):
    from .public_format_stages import gate
    protocol=json.loads(Path(protocol_path).read_text());check(protocol,data);committed(protocol_path);profile_check(profile)
    if (profile['model'],profile['endpoint'],profile['context_tokens'])!=(protocol['model'],protocol['endpoint'],protocol['context_tokens']):raise ValueError('Profile differs from freeze.')
    if split!='development':gate(data,protocol_path,split,candidate,boundary)
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('A server-side Jev key is required.')
    output=Path(output)
    if output.exists():raise ValueError('Hosted runs are immutable; do not repeat evaluation.')
    planned=requests(data,split);claim(protocol_path,split,output)
    output.mkdir(parents=True);dump(output/'requests.json',planned)
    opener=urllib.request.build_opener(NoRedirect());rows=[];reason=None;consecutive=0
    with (output/'responses.jsonl').open('x') as stream:
        for request in planned:
            row={k:request[k] for k in ('id','case_id','arm','request_sha256')};row['status']='ok';start=time.perf_counter()
            try:
                wire=urllib.request.Request(profile['endpoint'],data=encoded(request['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(wire,timeout=30) as response:content=response.read(1048577)
                if len(content)>1048576:raise ValueError('Oversized response.')
                raw=json.loads(content)
                if not isinstance(raw,dict):raise ValueError('Malformed provider response.')
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
            print(f"Input format Jev {len(rows)}/{len(planned)} {row['arm']} {row['status']}",flush=True)
            if reason or consecutive>=3:reason=reason or 'three_consecutive_failures';break
    summary={'schema':'public-format-hosted-1','split':split,'planned':len(planned),'attempted':len(rows),
        'failed':sum(r['status']!='ok' for r in rows),'unattempted':len(planned)-len(rows),
        'status':'completed' if len(rows)==len(planned) and all(r['status']=='ok' for r in rows) else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(Path(protocol_path).read_bytes()),
        'evidence_sha256':{p.name:sha(p.read_bytes()) for p in output.iterdir() if p.is_file()}}
    dump(output/'summary.json',summary);return summary
