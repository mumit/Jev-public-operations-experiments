"""Reconstruct disagreement evidence and paired outcomes without hosted calls."""
import hashlib,json
from triage_bench.paths import ROOT
from triage_bench.public_data import sha
from triage_bench.public_rca_stages import load,committed
from triage_bench.public_agreement_data import check_plan,validate,BASE
from triage_bench.public_agreement_trial import verified_rows,score,RESULTS
from scripts.audit_public_agreement import check,PLAN as AUDIT_PLAN,RESULT as AUDIT_RESULT,FOLDER as AUDIT_FOLDER,INDEX

def verify_audit():
    import pyarrow.parquet as pq
    p=check();committed(AUDIT_RESULT);m=load(AUDIT_RESULT)
    if m!=load(AUDIT_FOLDER/'manifest.json') or m['plan_sha256']!=sha(AUDIT_PLAN.read_bytes()) or m['new_hosted_calls']!=0:raise ValueError('Audit evidence drift.')
    indexed={r['case']:r for r in pq.read_table(INDEX).to_pylist()};expected={('AGR-'+sha(case.encode())[:12],n) for case in p['cases'] for n in ('metrics.parquet','inject_time.txt')}
    if len(m['files'])!=20 or {(r['path'].split('/')[1],r['path'].split('/')[2]) for r in m['files']}!=expected:raise ValueError('Audit file identities drift.')
    for f in m['files']:
        raw=(AUDIT_FOLDER/f['path']).read_bytes()
        if len(raw)!=f['bytes'] or sha(raw)!=f['sha256']:raise ValueError('Audit source drift.')
        actual=sha(raw) if len(f['publisher_hash'])==64 else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if actual!=f['publisher_hash']:raise ValueError('Audit publisher hash drift.')
    profiles=[]
    for case in p['cases']:
        identifier='AGR-'+sha(case.encode())[:12];directory=AUDIT_FOLDER/'raw'/identifier;t=pq.read_table(directory/'metrics.parquet');times=t.column('time').to_pylist();boundary=int((directory/'inject_time.txt').read_text())
        if boundary!=indexed[case]['inject_time']:raise ValueError('Audit boundary drift.')
        profiles.append({'id':identifier,'source_case':case,'dataset':indexed[case]['dataset'],'columns':t.schema.names,'rows':t.num_rows,'metric_suffixes':sorted({n.rsplit('_',1)[1] for n in t.schema.names if n!='time'}),'time_type':str(t.schema.field('time').type),'unique_sorted_times':times==sorted(set(times)),'before':sum(x<boundary for x in times),'after':sum(x>=boundary for x in times)})
    if profiles!=m['profiles']:raise ValueError('Audit reconstruction failed.')
    return m

def verify():
    verify_audit();p=check_plan();validate();verified_rows('evaluation',complete=True);committed(RESULTS)
    a=score()
    if a!=load(RESULTS):raise ValueError('Agreement assessment drift.')
    for panel in a['datasets'].values():
        for r in panel['routing']['per_round']:
            if r['base_shown']!=r['retained']+r['review_required'] or r['base_correct']!=r['retained_correct']+r['correct_routed_to_review'] or r['base_wrong']!=r['retained_wrong']+r['wrong_routed_to_review'] or r['retained']+r['review_required']+r['base_withheld']!=50:raise ValueError('Paired routing denominators do not balance.')
    reserved={r['id'] for r in p['assignments'] if r['split']=='reserve'}
    if len(reserved)!=140 or any(path.name in reserved for path in BASE.rglob('*') if path.is_dir()):raise ValueError('Sealed reserve entered the experiment.')
    return {'status':'verified','recorded_calls':300,'distinct_train_ticket_cases':50,'distinct_sock_shop_cases':50,'schema_audit_cases':10,'remaining_unopened_re1_cases':140,'new_hosted_calls':0}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
