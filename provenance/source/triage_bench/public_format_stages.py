"""Paired results and committed gates for the input study."""
import math
from pathlib import Path

from .public_data import sha
from .public_rca_data import dump
from .public_rca_stages import ROOT, THRESHOLDS, committed, load, verify_hosted, verify_local
from .public_format_data import ARMS, COUNTS
from .public_format_trial import check
from .public_rca_models import infer


def score(data,protocol_path,hosted,split):
    protocol=load(protocol_path);check(protocol,data);data=Path(data)
    rows=verify_hosted(hosted,protocol_path,split,require_complete=False);actual={r['id']:r for r in rows}
    model=verify_local(ROOT/protocol['local'],ROOT/protocol['historical_data'])
    refs={r['id']:r for r in load(data/f'{split}.references.json')};outcomes=[]
    packets=load(data/f'{split}.inputs.json')
    for p in packets:
        ref=refs[p['id']];controls=infer(p['state'],model)
        outcome={'id':p['id'],'group':ref['group'],'fault':ref['fault'],'target':ref['target'],
                 'choices':{a:r['choice'] for a,r in controls.items()},'probabilities':{},'provider_confidence':{}}
        for arm in ARMS:
            row=actual.get(p['id']+'::'+arm,{})
            if row and (row['case_id'],row['arm'])!=(p['id'],arm):raise ValueError('Recorded arm identity changed.')
            success=row.get('status')=='ok';outcome['choices'][arm]=row['choice'] if success else 'missing'
            outcome['probabilities'][arm]=row['probabilities'] if success else {}
            outcome['provider_confidence'][arm]=row.get('provider_confidence')
        outcomes.append(outcome)
    metrics={};groups={r['group'] for r in outcomes};faults={r['fault'] for r in outcomes}
    for arm in ('change','resource','ml')+ARMS:
        metrics[arm]={'correct':sum(r['choices'][arm]==r['target'] for r in outcomes),'cases':len(outcomes),
            'withheld':sum(r['choices'][arm] in {'missing','insufficient_evidence'} for r in outcomes),
            'groups_all_correct':sum(all(r['choices'][arm]==r['target'] for r in outcomes if r['group']==g) for g in groups),'groups':len(groups),
            'by_fault':{f:{'correct':sum(r['choices'][arm]==r['target'] for r in outcomes if r['fault']==f),'cases':sum(r['fault']==f for r in outcomes)} for f in sorted(faults)}}
    comparisons={}
    for old,new in [('compact','named'),('named','explained'),('compact','explained'),('ml','explained'),('change','explained')]:
        comparisons[new+'_vs_'+old]={'fixes':[r['id'] for r in outcomes if r['choices'][old]!=r['target'] and r['choices'][new]==r['target']],
            'regressions':[r['id'] for r in outcomes if r['choices'][old]==r['target'] and r['choices'][new]!=r['target']],
            'changed_choices':[r['id'] for r in outcomes if r['choices'][old]!=r['choices'][new]]}
    curves={}
    for arm in ARMS:
        curves[arm]=[]
        for threshold in THRESHOLDS:
            accepted=[r for r in outcomes if r['choices'][arm] not in {'missing','insufficient_evidence'} and r['probabilities'][arm][r['choices'][arm]]>=threshold]
            curves[arm].append({'threshold':threshold,'suggestions':len(accepted),'wrong':sum(r['choices'][arm]!=r['target'] for r in accepted),'review':len(outcomes)-len(accepted),'groups':len({r['group'] for r in accepted})})
    usage={};timing={}
    for arm in ARMS:
        arm_rows=[r for r in rows if r['arm']==arm];times=sorted(r['latency_ms'] for r in arm_rows)
        timing[arm]={'median_ms':(times[(len(times)-1)//2]+times[len(times)//2])/2 if times else None,'p95_ms':times[math.ceil(.95*len(times))-1] if times else None}
        usage[arm]={}
        for row in arm_rows:
            reported=row.get('usage')
            for name in ('input_tokens','output_tokens'):
                value=reported.get(name) if isinstance(reported,dict) else None
                if isinstance(value,int) and not isinstance(value,bool) and value>=0:usage[arm][name]=usage[arm].get(name,0)+value
    return {'schema':'public-format-assessment-1','split':split,'metrics':metrics,'outcomes':outcomes,'comparisons':comparisons,
        'curves':curves,'failed_or_missing':COUNTS[split]*3-sum(r['status']=='ok' for r in rows),
        'latency':timing,'usage':usage,'evidence':{'protocol':sha(Path(protocol_path).read_bytes()),'hosted_summary':sha((Path(hosted)/'summary.json').read_bytes())}}


def selected(assessment):
    result={}
    for arm in ARMS:
        rows=[r for r in assessment['curves'][arm] if r['wrong']==0 and r['suggestions']>0]
        result[arm]=sorted(rows,key=lambda r:(-r['suggestions'],r['threshold']))[0] if rows else None
    return result


def freeze_candidate(data,protocol,development,output):
    if Path(output).exists():raise ValueError('Candidate already exists.')
    check(load(protocol),data);committed(protocol);verify_hosted(development,protocol,'development')
    result={'schema':'public-format-candidate-1','protocol_sha256':sha(Path(protocol).read_bytes()),
            'development':str(Path(development).resolve().relative_to(ROOT)),
            'assessment':score(data,protocol,development,'development'),'selection':'All three arms and historical controls retained without changes.'}
    dump(output,result);return result


def gate(data,protocol,split,candidate,boundary):
    if split not in ('calibration','evaluation'):raise ValueError('Invalid gated split.')
    check(load(protocol),data);committed(protocol);committed(candidate);c=load(candidate)
    if c['protocol_sha256']!=sha(Path(protocol).read_bytes()):raise ValueError('Candidate belongs to another protocol.')
    development=ROOT/c['development'];verify_hosted(development,protocol,'development')
    if c['assessment']!=score(data,protocol,development,'development'):raise ValueError('Candidate assessment drift.')
    if split=='evaluation':
        committed(boundary);b=load(boundary)
        if b['candidate_sha256']!=sha(Path(candidate).read_bytes()):raise ValueError('Boundary belongs to another candidate.')
        calibration=ROOT/b['calibration'];verify_hosted(calibration,protocol,'calibration')
        assessment=score(data,protocol,calibration,'calibration')
        if b['assessment']!=assessment or b['selected']!=selected(assessment):raise ValueError('Boundary does not recompute.')


def freeze_boundary(data,protocol,candidate,calibration,output):
    if Path(output).exists():raise ValueError('Boundary already exists.')
    gate(data,protocol,'calibration',candidate,None);verify_hosted(calibration,protocol,'calibration')
    assessment=score(data,protocol,calibration,'calibration')
    result={'schema':'public-format-boundary-1','candidate_sha256':sha(Path(candidate).read_bytes()),
        'calibration':str(Path(calibration).resolve().relative_to(ROOT)),'selected':selected(assessment),'assessment':assessment,
        'meaning':'Research display thresholds only. All recommendations require analyst review.'}
    dump(output,result);return result
