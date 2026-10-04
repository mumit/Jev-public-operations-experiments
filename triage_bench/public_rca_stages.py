"""Verified stage gates and failure-inclusive scoring, separate from inference."""
import json
import math
from pathlib import Path
import subprocess
from triage_bench.public_data import sha
from triage_bench.public_rca_data import dump
from triage_bench.public_rca_models import infer

ROOT=Path(__file__).resolve().parents[1]
THRESHOLDS=(.5,.6,.7,.8,.9,.95,.99,1.)


def load(path):return json.loads(Path(path).read_text())


def committed(path):
    path=Path(path).resolve();name=str(path.relative_to(ROOT))
    result=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True)
    if result.returncode or sha(result.stdout)!=sha(path.read_bytes()):
        raise ValueError('Commit the unchanged stage checkpoint before calls.')


def verify_hosted(folder,protocol,split,require_complete=True):
    folder=Path(folder);summary=load(folder/'summary.json')
    if summary['split']!=split or (require_complete and summary['status']!='completed') or summary['protocol_sha256']!=sha(Path(protocol).read_bytes()):
        raise ValueError('Complete matching hosted evidence is required.')
    for name,digest in summary['evidence_sha256'].items():
        if sha((folder/name).read_bytes())!=digest:raise ValueError('Hosted evidence changed.')
    rows=[json.loads(s) for s in (folder/'responses.jsonl').read_text().splitlines()]
    expected=load(protocol)['requests'][split]
    if len(rows)>len(expected) or (require_complete and len(rows)!=len(expected)) or any((require_complete and r['status']!='ok') or {'id':r['id'],'request_sha256':r['request_sha256']}!=e for r,e in zip(rows,expected)):
        raise ValueError('Hosted request joins differ from freeze.')
    from triage_bench.public_rca_trial import normalize
    requests=load(folder/'requests.json')
    if [{'id':r['id'],'request_sha256':r['request_sha256']} for r in requests]!=expected:raise ValueError('Recorded requests differ.')
    from triage_bench.hosted import encoded
    if any(sha(encoded(r['body']))!=r['request_sha256'] for r in requests):raise ValueError('Recorded request body changed.')
    for row,request in zip(rows,requests):
        if row['status']=='ok':
            choice,probabilities,confidence=normalize(row['raw_response'],request['body']['questions']['cause']['criteria'])
            if (choice,probabilities,confidence)!=(row['choice'],row['probabilities'],row.get('provider_confidence')):raise ValueError('Normalized response changed.')
    return rows


def verify_local(folder,data):
    folder=Path(folder);m=load(folder/'manifest.json')
    for name,digest in m['files'].items():
        if sha((folder/name).read_bytes())!=digest:raise ValueError('Local evidence changed.')
    for name,key in [('train.inputs.json','training_source'),('train.references.json','training_references')]:
        if sha((Path(data)/name).read_bytes())!=m[key]:raise ValueError('Training data drift.')
    model=load(folder/'fitted.json');train=load(Path(data)/'train.inputs.json')
    if model['training_ids']!=[r['id'] for r in train]:raise ValueError('Model trained on another split.')
    from triage_bench.public_rca_models import fit
    if model!=fit(train,load(Path(data)/'train.references.json')):raise ValueError('Fitted model does not reproduce from training-only evidence.')
    return model


def score(data,protocol,local,hosted,split):
    data=Path(data);model=verify_local(local,data)
    rows=verify_hosted(hosted,protocol,split,require_complete=False);actual={r['id']:r for r in rows}
    packets=load(data/f'{split}.inputs.json');refs={r['id']:r for r in load(data/f'{split}.references.json')}
    outcomes=[];groups={}
    for packet in packets:
        ref=refs[packet['id']];row=actual.get(packet['id'],{})
        success=row.get('status')=='ok'
        controls=infer(packet['state'],model)
        outcomes.append({'id':packet['id'],'group':ref['group'],'target':ref['target'],'fault':ref['fault'],
                        'choices':{**{a:o['choice'] for a,o in controls.items()},'jev':row['choice'] if success else 'missing'},
                        'jev_probabilities':row['probabilities'] if success else {},'jev_confidence':row.get('provider_confidence')})
    metrics={}
    for arm in ('change','resource','ml','jev'):
        correct=sum(r['choices'][arm]==r['target'] for r in outcomes)
        metrics[arm]={'correct':correct,'cases':len(packets),'accuracy':correct/len(packets),
          'withheld':sum(r['choices'][arm] in {'insufficient_evidence','missing'} for r in outcomes),
          'groups_all_correct':sum(all(r['choices'][arm]==r['target'] for r in outcomes if r['group']==g) for g in {r['group'] for r in outcomes}),
          'groups':len({r['group'] for r in outcomes}),
          'by_fault':{f:{'correct':sum(r['choices'][arm]==r['target'] for r in outcomes if r['fault']==f),'cases':sum(r['fault']==f for r in outcomes)} for f in sorted({r['fault'] for r in outcomes})}}
    curves=[]
    for threshold in THRESHOLDS:
        accepted=[r for r in outcomes if r['choices']['jev'] not in {'insufficient_evidence','missing'} and r['jev_probabilities'][r['choices']['jev']]>=threshold]
        curves.append({'threshold':threshold,'suggestions':len(accepted),'wrong':sum(r['choices']['jev']!=r['target'] for r in accepted),
                       'review':len(packets)-len(accepted),'groups':len({r['group'] for r in accepted})})
    timings=sorted(r['latency_ms'] for r in rows);usage={}
    for row in rows:
        for k,v in (row.get('usage') if isinstance(row.get('usage'),dict) else {}).items():
            if 'token' in k and isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0:usage[k]=usage.get(k,0)+v
    comparison={a:{'jev_fixes':[r['id'] for r in outcomes if r['choices']['jev']==r['target'] and r['choices'][a]!=r['target']],
                   'jev_regressions':[r['id'] for r in outcomes if r['choices']['jev']!=r['target'] and r['choices'][a]==r['target']]} for a in ('change','resource','ml')}
    return {'schema':'public-rca-assessment-1','split':split,'metrics':metrics,'outcomes':outcomes,'curves':curves,'comparisons':comparison,
            'failed_or_missing':sum(r['choices']['jev']=='missing' for r in outcomes),'candidate_coverage':len(packets),
            'latency_median_ms':(timings[(len(timings)-1)//2]+timings[len(timings)//2])/2 if timings else None,
            'latency_p95_ms':timings[math.ceil(.95*len(timings))-1] if timings else None,'provider_usage':usage,
            'probability_note':'Jev choice probabilities only. ML scores are binary candidate margins, not a competing calibrated incident distribution.',
            'evidence':{'protocol':sha(Path(protocol).read_bytes()),'local_model':sha((Path(local)/'fitted.json').read_bytes()),
                        'hosted_summary':sha((Path(hosted)/'summary.json').read_bytes())}}


def freeze_candidate(data,protocol,local,hosted,output):
    from triage_bench.public_rca_trial import check
    if Path(output).exists():raise ValueError('Candidate checkpoint already exists.')
    check(load(protocol),data);committed(protocol)
    verify_hosted(hosted,protocol,'development')
    assessment=score(data,protocol,local,hosted,'development')
    candidate={'schema':'public-rca-candidate-1','protocol_sha256':sha(Path(protocol).read_bytes()),
               'data_manifest_sha256':sha((Path(data)/'manifest.json').read_bytes()),
               'local':str(Path(local).relative_to(ROOT)) if Path(local).is_absolute() else str(local),
               'development':str(Path(hosted).relative_to(ROOT)) if Path(hosted).is_absolute() else str(hosted),
               'local_model_sha256':sha((Path(local)/'fitted.json').read_bytes()),
               'development_summary_sha256':sha((Path(hosted)/'summary.json').read_bytes()),
               'assessment':assessment,'selection':'All four fixed methods retained. No development-driven transformation or hyperparameter change.'}
    dump(output,candidate);return candidate


def gate(data,protocol,split,candidate,boundary=None):
    c=load(candidate);committed(candidate)
    if c['protocol_sha256']!=sha(Path(protocol).read_bytes()) or c['data_manifest_sha256']!=sha((Path(data)/'manifest.json').read_bytes()):raise ValueError('Candidate freeze mismatch.')
    local=ROOT/c['local'];development=ROOT/c['development']
    verify_local(local,data);verify_hosted(development,protocol,'development')
    if c['local_model_sha256']!=sha((local/'fitted.json').read_bytes()) or c['development_summary_sha256']!=sha((development/'summary.json').read_bytes()):raise ValueError('Candidate evidence drift.')
    if split=='evaluation':
        if not boundary:raise ValueError('A committed calibration boundary is required.')
        b=load(boundary);committed(boundary)
        if b['candidate_sha256']!=sha(Path(candidate).read_bytes()):raise ValueError('Boundary candidate mismatch.')
        calibration=ROOT/b['calibration'];verify_hosted(calibration,protocol,'calibration')
        assessment=score(data,protocol,local,calibration,'calibration')
        choices=[p for p in assessment['curves'] if p['wrong']==0 and p['suggestions']>0]
        best=sorted(choices,key=lambda p:(-p['suggestions'],p['threshold']))[0] if choices else None
        if b['selected']!=best or b['assessment']!=assessment:raise ValueError('Boundary does not recompute.')


def freeze_boundary(data,protocol,candidate,calibration,output):
    if Path(output).exists():raise ValueError('Boundary checkpoint already exists.')
    gate(data,protocol,'calibration',candidate)
    verify_hosted(calibration,protocol,'calibration')
    c=load(candidate);assessment=score(data,protocol,ROOT/c['local'],calibration,'calibration')
    choices=[p for p in assessment['curves'] if p['wrong']==0 and p['suggestions']>0]
    selected=sorted(choices,key=lambda p:(-p['suggestions'],p['threshold']))[0] if choices else None
    boundary={'schema':'public-rca-boundary-1','candidate_sha256':sha(Path(candidate).read_bytes()),
              'calibration':str(Path(calibration).relative_to(ROOT)) if Path(calibration).is_absolute() else str(calibration),
              'selected':selected,'assessment':assessment,
              'meaning':'Author-set research display boundary; every report still needs analyst review. Zero observed calibration errors do not establish an operational error limit.'}
    dump(output,boundary);return boundary
