"""Preserve and verify preparation failures without promoting them to model evidence."""
import hashlib,json
from .paths import ROOT
from .public_data import sha,REVISION,REPOSITORY,fetch
from .public_rca_stages import load,committed
from . import explicit_native_v2_data as failed

AUDIT=ROOT/'checkpoints/explicit-native-v2-preparation-failure-2026-10-06.json'

def snapshot():
    import pyarrow.parquet as pq
    plan=load(failed.PLAN);files=[];outside=[]
    for a in plan['assignments']:
        source=a['source_case'];tree={e['path']:e for e in json.loads(fetch(f'https://huggingface.co/api/datasets/{REPOSITORY}/tree/{REVISION}/{source}')) if e['type']=='file'}
        for name in ('metrics.parquet','inject_time.txt'):
            path=failed.DATA/'raw'/a['id']/name;raw=path.read_bytes();e=tree[source+'/'+name];publisher=e['lfs']['oid'] if 'lfs' in e else e['oid'];actual=sha(raw) if 'lfs' in e else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
            if len(raw)!=e['size'] or actual!=publisher:raise ValueError('Third preparation publisher checksum differs.')
            files.append({'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':sha(raw),'publisher_hash':publisher})
        ts=pq.read_table(failed.DATA/'raw'/a['id']/'metrics.parquet',columns=['time']).column('time').to_pylist();boundary=int((failed.DATA/'raw'/a['id']/'inject_time.txt').read_text())
        if not min(ts)<boundary<=max(ts):outside.append({'recording':a['id'],'time_start':min(ts),'time_end':max(ts),'declared_incident_time':boundary,'before_rows':sum(t<boundary for t in ts),'after_rows':sum(t>=boundary for t in ts)})
    if len(outside)!=1 or outside[0]['after_rows']!=0:raise ValueError('Expected missing post-incident window changed.')
    r={'schema':'explicit-preparation-failure-1','plan_sha256':sha(failed.PLAN.read_bytes()),'recordings_downloaded':15,'hosted_calls':0,'inputs_prepared':0,'references_prepared':0,'status':'failed_before_protocol_or_inference','reason':'A recording ends before its declared injection time, outside the frozen two-window input contract. No rows, onset, source groups or references were repaired.','decision_required':'Retain missing post-incident evidence under a new contract or replace the entire group under a new allocation.','publisher_verification':'Rechecked pinned metadata after the exception, not an original execution journal.','outside_declared_window':outside,'files':files}
    with AUDIT.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    return {'recordings':15,'hosted_calls':0,'outside_window':outside}

def verify():
    import pyarrow.parquet as pq
    previous=failed.verify_failure();earlier=failed.failed.verify_failure();committed(AUDIT);audit=load(AUDIT);committed(failed.PLAN)
    for plan_path in (failed.PLAN,failed.failed.PLAN,failed.failed.failed.PLAN):
        committed(plan_path);plan=load(plan_path)
        for name,digest in {**plan['source_sha256'],**plan['evidence_sha256']}.items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Failed preparation source/evidence changed: '+name)
    if audit['schema']!='explicit-preparation-failure-1' or audit['plan_sha256']!=sha(failed.PLAN.read_bytes()) or audit['hosted_calls']!=0 or len(audit['files'])!=30:raise ValueError('Third failure audit changed.')
    for a in audit['files']:
        raw=(ROOT/a['path']).read_bytes();actual=sha(raw) if len(a['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if len(raw)!=a['bytes'] or sha(raw)!=a['sha256'] or actual!=a['publisher_hash']:raise ValueError('Third failure bytes changed.')
    for item in audit['outside_declared_window']:
        directory=failed.DATA/'raw'/item['recording'];ts=pq.read_table(directory/'metrics.parquet',columns=['time']).column('time').to_pylist();boundary=int((directory/'inject_time.txt').read_text())
        if item!={'recording':item['recording'],'time_start':min(ts),'time_end':max(ts),'declared_incident_time':boundary,'before_rows':sum(t<boundary for t in ts),'after_rows':sum(t>=boundary for t in ts)} or boundary<=max(ts):raise ValueError('Missing-window evidence changed.')
    if any((failed.DATA/n).exists() for n in ('inputs.json','references.json','manifest.json')) or failed.BASE.joinpath('confirmation-hosted-2026-10-06-v1').exists() or (ROOT/'checkpoints/explicit-native-v2-protocol-2026-10-06.json').exists():raise ValueError('Failed native v2 preparation was promoted or overwritten.')
    return {'status':'verified','downloaded_recordings':audit['recordings_downloaded']+previous['recordings_downloaded']+earlier['recordings_downloaded'],'hosted_calls':0,'inputs_prepared':0,'references_prepared':0,'decision_required':audit['decision_required'],'outside_window':audit['outside_declared_window']}
