"""Separately frozen, once-only incident-selection diagnostic."""
import json
import time
import urllib.request
import urllib.error
from .paths import ROOT
from . import incident_scope_data as data
from . import publisher_report_trial as previous
from .incident_scope_features import ARMS,request
from .incident_scope_scoring import score as assess
from .publisher_report_features import rules,CHOICES
from .public_sentence_features import validate_reply,GlobalReplyError
from .public_rca_stages import committed
from .profile import profile_check
from .runner import NoRedirect,clean_api_key
from .hosted import encoded,redact
from .report_source_audit import digest

PROTOCOL=ROOT/'checkpoints/publisher-incident-scope-protocol-2026-10-07.json'
RESULT=ROOT/'checkpoints/publisher-incident-scope-results-2026-10-07.json'
LOCAL=ROOT/'runs/incident-scope/hosted-2026-10-07-v1'
PUBLIC=ROOT/'runs/incident-scope/public-evidence-v1'
SOURCES=tuple(dict.fromkeys((*previous.SOURCES,'triage_bench/incident_scope_features.py','triage_bench/incident_scope_data.py',
    'triage_bench/incident_scope_scoring.py','triage_bench/incident_scope_trial.py','scripts/run_incident_scope.py',
    'triage_bench/publisher_scope_preview.py','triage_bench/publisher_report_trial.py')))

def dump(path,value):
    with path.open('x') as f:f.write(json.dumps(value,indent=2)+'\n')

def jobs():
    packets,_=data.packets();planned=[]
    for n in (1,2,3):
        for p in packets[n-1:]+packets[:n-1]:
            order=ARMS[n-1:]+ARMS[:n-1]
            for arm in order:
                body=request(p,arm);wire=encoded(body)
                if len(wire)>16000:raise ValueError('Wire cap exceeded before inference.')
                expected={'claim','report_excerpt'} | ({'selected_incident'} if arm!='full' else set())
                if set(json.loads(body['state']))!=expected:raise ValueError('Input allowlist changed.')
                planned.append({'id':p['id']+'::'+arm+'::r'+str(n),'claim_id':p['id'],'arm':arm,'round':n,
                    'request_sha256':digest(wire),'body':body})
    if len(planned)!=54:raise ValueError('Budget changed.')
    return planned

def freeze():
    previous.verify('development',local=False);previous.verify('evaluation',local=False)
    planned=jobs();packets,_=data.packets();baseline={}
    for p in packets:
        baseline[p['id']]={arm:rules({**p,'report':p['scoped_report'] if arm=='selected_section' else p['report']}) for arm in ARMS}
    protocol={'schema':'publisher-incident-scope-protocol-1','plan_sha256':digest(data.PLAN.read_bytes()),
        'pack_sha256':digest(data.PACK.read_bytes()),'previous_protocol_sha256':digest(previous.PLAN.read_bytes()),
        'source_sha256':{s:digest((ROOT/s).read_bytes()) for s in SOURCES},'profile':previous.check(local=False)['profile'],
        'requests':[{k:v for k,v in j.items() if k!='body'} for j in planned],'baseline':baseline,
        'maximum_calls':54,'rounds':3,'calls_per_arm':18,'retry_count':0,'maximum_request_bytes':16000,
        'candidate':'selected_section','review_status':'Assistant selection fixtures and references; zero actual analyst entries or independent reviews.'}
    dump(PROTOCOL,protocol)
    return {'requests':54,'unique_claims':6,'arms':list(ARMS),'maximum_request_bytes':max(len(encoded(j['body'])) for j in planned)}

def check(local=True):
    committed(PROTOCOL);previous.check(local=False);data.packets(local=False);p=data.old.load(PROTOCOL)
    deps=((data.PLAN,'plan_sha256'),(data.PACK,'pack_sha256'),(previous.PLAN,'previous_protocol_sha256'))
    if any(digest(path.read_bytes())!=p[key] for path,key in deps):raise ValueError('Frozen dependency changed.')
    for name,h in p['source_sha256'].items():
        if digest((ROOT/name).read_bytes())!=h:raise ValueError('Frozen producer changed: '+name)
    if p['maximum_calls']!=54 or p['retry_count'] or p['candidate']!='selected_section':raise ValueError('Frozen protocol changed.')
    if local:
        planned=jobs();packets,_=data.packets()
        if p['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in planned]:raise ValueError('Exact input changed.')
        baseline={s['id']:{a:rules({**s,'report':s['scoped_report'] if a=='selected_section' else s['report']}) for a in ARMS} for s in packets}
        if baseline!=p['baseline']:raise ValueError('Literal rule projection changed.')
    return p

def run(profile):
    p=check();profile_check(profile)
    if any(profile[k]!=p['profile'][k] for k in ('model','endpoint','context_tokens')):raise ValueError('Pinned profile changed.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('Server-side credential required.')
    LOCAL.parent.mkdir(parents=True,exist_ok=True);LOCAL.mkdir()
    planned=jobs();dump(LOCAL/'requests.json',planned);rows=[];reason=None;opener=urllib.request.build_opener(NoRedirect())
    with (LOCAL/'responses.jsonl').open('x') as stream:
        for job in planned:
            row={k:v for k,v in job.items() if k!='body'};start=time.perf_counter()
            try:
                req=urllib.request.Request(profile['endpoint'],data=encoded(job['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(req,timeout=45) as response:raw_bytes=response.read(1048577)
                if len(raw_bytes)>1048576:raise ValueError('Oversized reply.')
                raw=json.loads(raw_bytes);row['raw_response']=redact(raw,key);row['raw_response_sha256']=digest(encoded(row['raw_response']))
                row.update(validate_reply(raw,job['body'],profile['context_tokens']))
            except GlobalReplyError as error:reason=str(error);row.update(status='error',error=reason)
            except urllib.error.HTTPError as error:reason='provider_http_'+str(error.code);error.close();row.update(status='error',error=reason)
            except (OSError,ValueError,TypeError,KeyError) as error:reason='request_or_validation_'+type(error).__name__;row.update(status='error',error=reason)
            row['latency_ms']=(time.perf_counter()-start)*1000;row=redact(row,key);rows.append(row)
            stream.write(json.dumps(row)+'\n');stream.flush()
            print(f"Incident scope {len(rows)}/54 {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'publisher-incident-scope-hosted-1','planned_calls':54,'attempted_calls':len(rows),'unattempted_calls':54-len(rows),
        'status':'completed' if len(rows)==54 and reason is None else 'incomplete_or_failed','stopped_reason':reason,
        'protocol_sha256':digest(PROTOCOL.read_bytes()),'files':{n:digest((LOCAL/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    dump(LOCAL/'summary.json',summary);return summary

def rows(local=True):
    p=check(local);folder=LOCAL if local else PUBLIC;summary=data.old.load(folder/'summary.json')
    if summary['protocol_sha256']!=digest(PROTOCOL.read_bytes()):raise ValueError('Run protocol changed.')
    for name,h in summary['files'].items():
        if digest((folder/name).read_bytes())!=h:raise ValueError('Run file changed.')
    rs=[json.loads(s) for s in (folder/'responses.jsonl').read_text().splitlines()]
    if len(rs)!=summary['attempted_calls'] or len(rs)>54 or summary['unattempted_calls']!=54-len(rs):raise ValueError('Run denominator changed.')
    if local and data.old.load(folder/'requests.json')!=jobs():raise ValueError('Saved inputs changed.')
    for row,job in zip(rs,p['requests']):
        if any(row.get(k)!=v for k,v in job.items()):raise ValueError('Reply join changed.')
        if 'raw_response' in row and digest(encoded(row['raw_response']))!=row['raw_response_sha256']:raise ValueError('Original reply payload changed.')
        if row['status'] in ('ok','ok_with_review'):
            normalized=validate_reply(row['raw_response'],{'questions':{'verdict':{'criteria':CHOICES}}},p['profile']['context_tokens'])
            if any(row.get(k)!=v for k,v in normalized.items()):raise ValueError('Normalized reply changed.')
        elif row['status']!='error':raise ValueError('Unknown reply status.')
    return rs,summary

def score(local=True):
    rs,summary=rows(local);packets,refs=data.packets(local);p=check(local)
    return {'schema':'publisher-incident-scope-results-1','actual_calls':len(rs),'valid_answers':sum(len(r.get('answers',{})) for r in rs),
        'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rs),'protocol_sha256':digest(PROTOCOL.read_bytes()),
        'human_entries':0,'human_reviews':0,'independent_reference_reviews':0,'new_telemetry_recordings':0,
        **assess(packets,refs,rs,summary['status']=='completed',p['baseline'])}

def verify(local=True):
    committed(RESULT);result=score(local)
    if result!=data.old.load(RESULT):raise ValueError('Recorded results changed.')
    return result

def export():
    verify();PUBLIC.parent.mkdir(parents=True,exist_ok=True);PUBLIC.mkdir()
    rs,summary=rows();projected=[]
    for row in rs:
        if 'raw_response' in row:
            raw=row['raw_response']
            if set(raw)!={'model','answers','usage'}:raise ValueError('Unexpected provider text; review locally before publication.')
        projected.append(row)
    (PUBLIC/'responses.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in projected))
    summary['files']={'responses.jsonl':digest((PUBLIC/'responses.jsonl').read_bytes())}
    summary['projection']='Original answer/usage payloads; full-text requests excluded.';dump(PUBLIC/'summary.json',summary)
    if score(local=False)!=data.old.load(RESULT):raise ValueError('Public projection does not replay.')
    return {'public_files':2,'actual_calls':len(rs),'full_text_requests_exported':0}
