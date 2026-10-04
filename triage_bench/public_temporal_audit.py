"""Offline timing audit of inspected cases; no fitting, inference or new downloads."""
import math
from pathlib import Path
from .public_data import percentile,finite,sha
from .public_rca_stages import load
from .public_repeat_trial import check,DATA
from .paths import ROOT

WINDOWS=((0,60),(60,300),(300,721))


def latency_windows(columns,boundary):
    times=columns.get('time',[])
    if not times or any(isinstance(t,bool) or not isinstance(t,int) or not 1_000_000_000<=t<10_000_000_000 for t in times):raise ValueError('Expected epoch-second metric times.')
    if times!=sorted(set(times)) or not min(times)<boundary<=max(times):raise ValueError('Invalid timing boundary.')
    before=[i for i,t in enumerate(times) if t<boundary]
    result={}
    for name,values in sorted(columns.items()):
        if not name.endswith(('_latency-50','_latency-90')):continue
        if len(values)!=len(times):raise ValueError('Unequal metric timeline.')
        valid=finite([values[i] for i in before]);median=percentile(valid,.5)
        scale=max(percentile(valid,.9)-percentile(valid,.1),abs(median)*.01,1e-12) if median is not None else None
        windows=[]
        for low,high in WINDOWS:
            indices=[i for i,t in enumerate(times) if low<=t-boundary<high]
            vals=finite([values[i] for i in indices]);value=percentile(vals,.5)
            windows.append({'start_offset_seconds':low,'end_offset_seconds_exclusive':high,'rows':len(indices),
                'median':value,'signed_change':(value-median)/scale if value is not None and scale is not None else None,
                'missing_fraction':1-len(vals)/len(indices) if indices else None})
        result[name]={'before_median':median,'before_missing_fraction':1-len(valid)/len(before),'baseline_scale':scale,'windows':windows}
    return result


def audit(protocol_path=ROOT/'checkpoints/public-repeat-protocol-2026-10-03.json'):
    import pyarrow.parquet as pq
    protocol=load(protocol_path);check(protocol);cases=[];fingerprints={}
    for case in protocol['cases']:
        directory=ROOT/DATA/'raw'/case['id']
        for name in ('metrics.parquet','inject_time.txt'):
            p=directory/name;fingerprints[str(p.relative_to(ROOT))]=sha(p.read_bytes())
        columns=pq.read_table(directory/'metrics.parquet').to_pydict();boundary=int((directory/'inject_time.txt').read_text())
        cases.append({'id':case['id'],'input_only_latency_windows':latency_windows(columns,boundary)})
    return {'schema':'public-temporal-audit-1','cases':cases,'input_evidence_sha256':fingerprints,
        'source_sha256':sha(Path(__file__).read_bytes()),'windows_seconds':WINDOWS,
        'purpose':'Inspect information discarded by the existing medians on 12 already-inspected cases. Windows were chosen after inspecting failures; this is exploratory evidence, not a measured improvement or frozen candidate.',
        'limits':'No new calls, thresholds, causal labels or model scores. Temporal ordering alone cannot identify origin; scrape and aggregation delays are unknown. No reserve data downloaded.'}
