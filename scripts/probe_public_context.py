"""Once-only capacity probe on one inspected development request; no accuracy score."""
import argparse,json,time,urllib.request,urllib.error
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.public_data import sha
from triage_bench.hosted import encoded,redact
from triage_bench.public_rca_stages import load,committed
from triage_bench.public_temporal_data import validate
from triage_bench.public_rca_trial import normalize,MODEL
from triage_bench.app import load_env,profiles
from triage_bench.profile import profile_check
from triage_bench.runner import clean_api_key,NoRedirect

DATA=ROOT/'runs/public-temporal/development-2026-10-04-v1'
PLAN=ROOT/'checkpoints/public-temporal-preparation-2026-10-04.json'
PROTOCOL=ROOT/'checkpoints/public-context-probe-2026-10-04.json'
OUTPUT=ROOT/'runs/public-temporal/context-probe-2026-10-04-v1'


def request():
    validate(PLAN,DATA)
    packets=load(DATA/'development.inputs.json')
    p=max(packets,key=lambda r:len(encoded(r['requests']['temporal'])))
    return p['id'],p['requests']['temporal']


def freeze(profile):
    profile_check(profile)
    if PROTOCOL.exists():raise ValueError('Capacity protocol exists.')
    identifier,body=request()
    protocol={'schema':'public-context-probe-1','maximum_calls':1,'model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
        'case_id':identifier,'arm':'temporal','request_sha256':sha(encoded(body)),'request_bytes':len(encoded(body)),
        'source_sha256':sha(Path(__file__).read_bytes()),'manifest_sha256':sha((DATA/'manifest.json').read_bytes()),
        'purpose':'Capacity and actual billable token count for the largest prepared development request. Selection uses request size, not answers. No accuracy score, retries, calibration or sealed telemetry.',
        'limit':'Current lab byte bound failed. That is not proof of a token overflow. Provider validates the actual context limit. This separate single-call probe does not change any historical or preparation guard.'}
    with PROTOCOL.open('x') as stream:json.dump(protocol,stream,indent=2);stream.write('\n')
    return {'status':'frozen','maximum_calls':1,'request_bytes':protocol['request_bytes'],'case_id':identifier}


def run(profile):
    p=load(PROTOCOL);committed(PROTOCOL);profile_check(profile);identifier,body=request()
    if p['maximum_calls']!=1 or p['source_sha256']!=sha(Path(__file__).read_bytes()) or p['manifest_sha256']!=sha((DATA/'manifest.json').read_bytes()):raise ValueError('Capacity source or evidence drift.')
    if p['case_id']!=identifier or p['request_sha256']!=sha(encoded(body)):raise ValueError('Capacity request changed.')
    if (p['model'],p['endpoint'],p['context_tokens'])!=(profile['model'],profile['endpoint'],profile['context_tokens']):raise ValueError('Capacity profile changed.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('A server-side Jev key is required.')
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    # The fixed directory is the once-only claim; no output override or retry.
    OUTPUT.mkdir();(OUTPUT/'request.json').write_text(json.dumps(body,indent=2)+'\n')
    result={'schema':'public-context-probe-result-1','protocol_sha256':sha(PROTOCOL.read_bytes()),'request_sha256':p['request_sha256'],
        'request_bytes':p['request_bytes'],'attempted':1,'status':'error'}
    start=time.perf_counter();opener=urllib.request.build_opener(NoRedirect())
    try:
        wire=urllib.request.Request(profile['endpoint'],data=encoded(body),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
        with opener.open(wire,timeout=30) as response:content=response.read(1048577)
        if len(content)>1048576:raise ValueError('Oversized response.')
        raw=json.loads(content);result['raw_response']=redact(raw,key)
        normalize(raw,body['questions']['cause']['criteria'])
        usage=raw.get('usage',{});count=usage.get('input_tokens')
        if isinstance(count,bool) or not isinstance(count,int) or count<1:raise ValueError('Missing actual token count.')
        result.update(status='accepted',input_tokens=count,reported_input_within_declared_capacity=count<=profile['context_tokens'])
    except urllib.error.HTTPError as error:result.update(error='Provider HTTP '+str(error.code))
    except (OSError,ValueError,KeyError,TypeError) as error:result.update(error='Validation or request failure: '+type(error).__name__)
    result=redact(result,key);result['latency_ms']=(time.perf_counter()-start)*1000
    (OUTPUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return {k:v for k,v in result.items() if k not in {'raw_response'}}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('freeze','run'));parser.add_argument('--env-file',default=str(ROOT/'.env'));args=parser.parse_args()
    load_env(Path(args.env_file));profile=profiles()['jev'];print(json.dumps(freeze(profile) if args.action=='freeze' else run(profile)))
if __name__=='__main__':main()
