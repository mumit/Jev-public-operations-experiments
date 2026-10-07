"""Once-only publisher-report comparison with fixed source and evaluation gates."""
import json
import time
import urllib.request
import urllib.error
from .paths import ROOT
from .public_rca_stages import committed
from .public_sentence_features import validate_reply,GlobalReplyError
from .profile import profile_check
from .runner import NoRedirect,clean_api_key
from .hosted import encoded,redact
from . import publisher_report_data as data
from .publisher_report_features import request,rules,CHOICES
from .publisher_report_scoring import score as assess
from .report_source_audit import digest

PLAN=ROOT/'checkpoints/publisher-report-protocol-2026-10-07.json'
BASE=ROOT/'runs/publisher-report'
PUBLIC=ROOT/'runs/publisher-report/public-evidence-v1'
SOURCES=('triage_bench/publisher_report_features.py','triage_bench/publisher_report_data.py','triage_bench/publisher_report_scoring.py','triage_bench/publisher_report_trial.py','scripts/run_publisher_reports.py','triage_bench/report_source_audit.py','triage_bench/profile.py','triage_bench/hosted.py','triage_bench/runner.py','triage_bench/public_sentence_features.py','triage_bench/public_rca_trial.py')

def dump(path,value):
    with path.open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')

def result_path(phase):return ROOT/('checkpoints/publisher-report-'+phase+'-results-2026-10-07.json')
def destination(phase):
    if phase not in {'development','evaluation'}:raise ValueError('Unknown phase.')
    return BASE/(phase+'-hosted-2026-10-07-v1')

def jobs(phase):
    packets,_=data.packets(phase);planned=[]
    for n in (1,2,3):
        for p in packets[n-1:]+packets[:n-1]:
            b=request(p);wire=encoded(b)
            if len(wire)>16000:raise ValueError('Conservative report wire cap exceeded before calls.')
            if set(b['state'] and json.loads(b['state']))!={'report_excerpt','claim'}:raise ValueError('Input allowlist changed.')
            planned.append({'id':p['id']+'::r'+str(n),'claim_id':p['id'],'phase':phase,'round':n,'request_sha256':digest(wire),'body':b})
    if len(planned)!=72:raise ValueError('Request denominator changed.')
    return planned

def freeze():
    data.committed_inputs();d,claims,refs=data.metadata();phases={};baseline=[]
    for phase in ('development','evaluation'):
        planned=jobs(phase);packets,_=data.packets(phase)
        phases[phase]=[{k:v for k,v in j.items() if k!='body'} for j in planned]
        baseline.extend({'id':p['id'],'prediction':rules(p),'excerpt_sha256':p['excerpt_sha256']} for p in packets)
    p={'schema':'publisher-report-protocol-1','design_sha256':digest((ROOT/data.DESIGN).read_bytes()),'claims_sha256':digest(data.CLAIMS.read_bytes()),'references_sha256':digest(data.REFERENCES.read_bytes()),'source_sha256':{n:digest((ROOT/n).read_bytes()) for n in SOURCES},'profile':d['profile'],'requests':phases,'baseline':baseline,'rounds':3,'calls_per_phase':72,'maximum_calls':144,'maximum_request_bytes':16000,'retry_count':0,'failure_policy':'Global envelope/checkpoint/context/HTTP/network errors stop immediately. Invalid Choice fields are retained and withheld; never repair or retry. Keep all 24 planned claims in every round denominator.','review_status':'Assistant-authored claims and references on publisher-written sources; no independent reference review.','full_text_publication':'Full source snapshots and exact full-text requests stay local. Public evidence contains answer projections and precommitted literal-rule predictions; exact request and rule replay requires matching source snapshots.'}
    dump(PLAN,p)
    return {'requests':144,'development_calls':72,'evaluation_calls_conditional':72,'rule_displays_development':sum(b['prediction']['displayed'] for b in baseline[:24]),'rule_displays_evaluation':sum(b['prediction']['displayed'] for b in baseline[24:])}

def check(local=True):
    committed(PLAN);data.committed_inputs();p=data.load(PLAN)
    if p['design_sha256']!=digest((ROOT/data.DESIGN).read_bytes()) or p['claims_sha256']!=digest(data.CLAIMS.read_bytes()) or p['references_sha256']!=digest(data.REFERENCES.read_bytes()):raise ValueError('Frozen text or design changed.')
    for n,h in p['source_sha256'].items():
        if digest((ROOT/n).read_bytes())!=h:raise ValueError('Frozen producer changed: '+n)
    if p['schema']!='publisher-report-protocol-1' or p['maximum_calls']!=144 or p['retry_count'] or p['calls_per_phase']!=72:raise ValueError('Budget changed.')
    if local:
        baseline=[]
        for phase in ('development','evaluation'):
            planned=jobs(phase);packets,_=data.packets(phase)
            if p['requests'][phase]!=[{k:v for k,v in j.items() if k!='body'} for j in planned]:raise ValueError('Exact request changed.')
            baseline.extend({'id':s['id'],'prediction':rules(s),'excerpt_sha256':s['excerpt_sha256']} for s in packets)
        if baseline!=p['baseline']:raise ValueError('Literal baseline changed.')
    return p

def evaluation_gate():
    r=verify('development')
    if not r['candidate_passes']:raise ValueError('Frozen hybrid failed development; evaluation calls remain blocked.')
    return r

def run(phase,profile):
    if phase=='evaluation':evaluation_gate()
    p=check();profile_check(profile)
    if any(profile[k]!=p['profile'][k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the pinned profile.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('Server-side credential required.')
    folder=destination(phase);folder.parent.mkdir(parents=True,exist_ok=True);folder.mkdir()
    planned=jobs(phase);dump(folder/'requests.json',planned)
    opener=urllib.request.build_opener(NoRedirect());rows=[];reason=None
    with (folder/'responses.jsonl').open('x') as stream:
        for job in planned:
            row={k:v for k,v in job.items() if k!='body'};start=time.perf_counter()
            try:
                req=urllib.request.Request(profile['endpoint'],data=encoded(job['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(req,timeout=45) as response:raw_bytes=response.read(1048577)
                if len(raw_bytes)>1048576:raise ValueError('Oversized reply.')
                raw=json.loads(raw_bytes);row['raw_response']=redact(raw,key);row['raw_response_sha256']=digest(encoded(row['raw_response']))
                row.update(validate_reply(raw,job['body'],profile['context_tokens']))
            except GlobalReplyError as error:
                reason=str(error);row.update(status='error',error=reason)
            except urllib.error.HTTPError as error:
                reason='provider_http_'+str(error.code);error.close();row.update(status='error',error=reason)
            except (OSError,ValueError,TypeError,KeyError) as error:
                reason='request_or_validation_'+type(error).__name__;row.update(status='error',error=reason)
            row['latency_ms']=(time.perf_counter()-start)*1000;row=redact(row,key);rows.append(row)
            stream.write(json.dumps(row)+'\n');stream.flush()
            print(f"Publisher reports {phase} {len(rows)}/72 round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'publisher-report-hosted-1','phase':phase,'planned_calls':72,'attempted_calls':len(rows),'unattempted_calls':72-len(rows),'status':'completed' if len(rows)==72 and reason is None else 'incomplete_or_failed','stopped_reason':reason,'protocol_sha256':digest(PLAN.read_bytes()),'files':{n:digest((folder/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    dump(folder/'summary.json',summary);return summary

def rows(phase,local=True):
    p=check(local=local);folder=destination(phase) if local else PUBLIC/phase
    summary=data.load(folder/'summary.json');planned=p['requests'][phase]
    if summary['protocol_sha256']!=digest(PLAN.read_bytes()) or summary['phase']!=phase:raise ValueError('Run identity changed.')
    for name,h in summary['files'].items():
        if digest((folder/name).read_bytes())!=h:raise ValueError('Run evidence changed.')
    recorded=[json.loads(line) for line in (folder/'responses.jsonl').read_text().splitlines()]
    if len(recorded)>72 or len(recorded)!=summary['attempted_calls'] or summary['unattempted_calls']!=72-len(recorded):raise ValueError('Response denominator changed.')
    if local and data.load(folder/'requests.json')!=jobs(phase):raise ValueError('Saved requests changed.')
    for row,job in zip(recorded,planned):
        if any(row.get(k)!=v for k,v in job.items()):raise ValueError('Response join changed.')
        if row['status'] in ('ok','ok_with_review'):
            body={'questions':{'verdict':{'criteria':CHOICES}}}
            normalized=validate_reply(row['raw_response'],body,p['profile']['context_tokens'])
            if any(row.get(k)!=v for k,v in normalized.items()):raise ValueError('Normalized reply changed.')
        elif row['status']!='error':raise ValueError('Unknown response status.')
    return recorded,summary

def score(phase,local=True):
    recorded,summary=rows(phase,local);p=check(local=local)
    if local:
        packets,refs=data.packets(phase);result=assess(packets,refs,recorded,summary['status']=='completed')
    else:
        # Replay public recorded rule projections; no source fetch or inference.
        d,claims,refs=data.metadata();packets=[c for c in claims if c['allocation']==phase];rs=[r for r in refs if r['id'] in {c['id'] for c in packets}]
        baseline={b['id']:b['prediction'] for b in p['baseline']}
        result=assess(packets,rs,recorded,summary['status']=='completed',baseline)
    return {'schema':'publisher-report-results-1','phase':phase,'actual_calls':len(recorded),'valid_answers':sum(len(r.get('answers',{})) for r in recorded),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in recorded),'protocol_sha256':digest(PLAN.read_bytes()),'human_reviews':0,'independent_reference_reviews':0,'new_telemetry_recordings':0,**result}

def verify(phase,local=True):
    committed(result_path(phase));result=score(phase,local)
    if result!=data.load(result_path(phase)):raise ValueError('Recorded assessment changed.')
    return result

def export(phase):
    verify(phase);source=destination(phase);folder=PUBLIC/phase;folder.parent.mkdir(parents=True,exist_ok=True);folder.mkdir()
    original=[json.loads(s) for s in (source/'responses.jsonl').read_text().splitlines()];projected=[]
    for row in original:
        r={k:v for k,v in row.items() if k!='raw_response'}
        if 'raw_response' in row:
            raw=row['raw_response'];r['raw_response']={k:raw[k] for k in ('model','answers','usage') if k in raw}
            # Expected schema contains only labels, probabilities and numeric usage.
            if len(encoded(r['raw_response']))>4096:raise ValueError('Unexpected provider projection; preserve locally for review.')
        projected.append(r)
    (folder/'responses.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in projected))
    summary=data.load(source/'summary.json');summary['files']={'responses.jsonl':digest((folder/'responses.jsonl').read_bytes())};summary['projection']='model, answers and usage; full local reply hash retained; full-text requests excluded'
    dump(folder/'summary.json',summary)
    if score(phase,local=False)!=data.load(result_path(phase)):raise ValueError('Public projection does not replay.')
    return {'public_files':2,'actual_calls':len(projected),'full_text_requests_exported':0}
