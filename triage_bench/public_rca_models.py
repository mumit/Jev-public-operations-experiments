"""Fixed metric-ranking controls trained only on the public training groups."""
import json
import math
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from triage_bench.public_rca_data import dump

METRICS=('cpu','mem','diskio','socket','workload','error','latency-50','latency-90')
RESOURCES={'cpu','mem','diskio','socket'}
FEATURES=[f'{metric}:{field}' for metric in METRICS for field in ('signed_log_shift','available','before_missing','after_missing')]


def vector(metrics):
    result=[]
    for name in METRICS:
        row=metrics.get(name)
        if row is None or row[2] is None:
            result.extend([0.,0.,row[3] if row else 1.,row[4] if row else 1.])
        else:
            shift=row[2]
            result.extend([math.copysign(math.log1p(abs(shift)),shift),1.,row[3],row[4]])
    if not all(math.isfinite(x) for x in result):raise ValueError('Non-finite ML features.')
    return result


def fit(train, references):
    targets={r['id']:r['target'] for r in references}
    X,y=[],[]
    for packet in train:
        for service,metrics in packet['state']['services'].items():
            X.append(vector(metrics)); y.append(int(service==targets[packet['id']]))
    scaler=StandardScaler(); scaled=scaler.fit_transform(X)
    classifier=LogisticRegression(C=1.,class_weight='balanced',solver='lbfgs',max_iter=2000,random_state=47)
    classifier.fit(scaled,y)
    if max(classifier.n_iter_)>=2000:raise ValueError('ML fitting did not converge.')
    return {'schema':'public-rca-linear-1','features':FEATURES,'training_ids':[r['id'] for r in train],
            'training_candidate_rows':len(X),'training_positive_rows':sum(y),'C':1.,'class_weight':'balanced',
            'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),
            'coef':classifier.coef_[0].tolist(),'intercept':float(classifier.intercept_[0]),
            'n_iter':classifier.n_iter_.tolist(),'probability_note':'Binary candidate logits rank services. They are not a calibrated distribution over incident causes.'}


def infer(state, model):
    outputs={}
    for arm,allowed in [('change',set(METRICS)),('resource',RESOURCES)]:
        values=[]
        for service,metrics in state['services'].items():
            scores=[abs(row[2]) for metric,row in metrics.items() if metric in allowed and row[2] is not None]
            values.append({'service':service,'score':max(scores) if scores else None})
        ranking=sorted(values,key=lambda r:(-(r['score'] if r['score'] is not None else -1),r['service']))
        choice=ranking[0]['service'] if ranking[0]['score'] is not None and ranking[0]['score']>0 else 'insufficient_evidence'
        outputs[arm]={'choice':choice,'ranking':ranking,'confidence':None}
    ranking=[]
    for service,metrics in state['services'].items():
        raw=vector(metrics); scaled=(np.asarray(raw)-model['mean'])/model['scale']
        contributions=scaled*np.asarray(model['coef'])
        margin=float(contributions.sum()+model['intercept'])
        ranking.append({'service':service,'score':margin,'raw_vector':raw,
                        'contributions':contributions.tolist()})
    ranking.sort(key=lambda r:(-r['score'],r['service']))
    outputs['ml']={'choice':ranking[0]['service'],'ranking':ranking,'confidence':None}
    return outputs


def run_local(data,output):
    from triage_bench.public_rca_data import validate
    from triage_bench.public_data import sha
    validate(data);data=Path(data);output=Path(output)
    if output.exists():raise ValueError('Local public study runs are immutable.')
    train=json.loads((data/'train.inputs.json').read_text());refs=json.loads((data/'train.references.json').read_text())
    model=fit(train,refs)
    output.mkdir(parents=True);dump(output/'fitted.json',model)
    # No calibration/evaluation predictions before candidate freeze.
    packets=json.loads((data/'development.inputs.json').read_text())
    dump(output/'predictions.json',[{'id':r['id'],'outputs':infer(r['state'],model)} for r in packets])
    manifest={'schema':'public-rca-local-run-1','split':'development',
              'files':{p.name:sha(p.read_bytes()) for p in output.glob('*.json')},
              'training_source':sha((data/'train.inputs.json').read_bytes()),
              'training_references':sha((data/'train.references.json').read_bytes())}
    dump(output/'manifest.json',manifest)
    return manifest
