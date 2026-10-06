"""Missing-window contract: preserve observed rows, leave absent aggregates unknown."""
import math,re
from .public_data import percentile

from .public_data import METRICS
CHANNELS=tuple(sorted(set(METRICS)|{'load','latency'}))

def observations(columns,boundary):
    times=columns.get('time')
    if not isinstance(times,list) or not times or any(type(t) is not int or not 1_000_000_000<=t<10_000_000_000 for t in times) or times!=sorted(set(times)) or type(boundary) is not int or not 1_000_000_000<=boundary<10_000_000_000:raise ValueError('Invalid native metric timeline.')
    before=[i for i,t in enumerate(times) if t<boundary];after=[i for i,t in enumerate(times) if t>=boundary];services={}
    def finite(values):return [float(v) for v in values if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)]
    def rounded(v):return None if v is None else float(format(v,'.8g'))
    for column,values in columns.items():
        if column=='time':continue
        if not isinstance(column,str) or '_' not in column:raise ValueError('Unsupported native metric name.')
        service,channel=column.rsplit('_',1)
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*',service) or channel not in CHANNELS or len(values)!=len(times):raise ValueError('Unknown native channel or service; no metadata passthrough.')
        left=finite([values[i] for i in before]);right=finite([values[i] for i in after]);b=percentile(left,.5);a=percentile(right,.5);q10=percentile(left,.1);q90=percentile(left,.9)
        change=(a-b)/max(q90-q10,abs(b)*.01,1e-12) if b is not None and a is not None else None
        metrics=services.setdefault(service,{})
        if channel in metrics:raise ValueError('Duplicate native metric.')
        metrics[channel]={'before_median':rounded(b),'after_median':rounded(a),'signed_change':rounded(change),'before_missing_fraction':rounded(1-len(left)/len(before)) if before else None,'after_missing_fraction':rounded(1-len(right)/len(after)) if after else None}
    windows={'before':max(times[i] for i in before)-min(times[i] for i in before)+1 if before else None,'after':max(times[i] for i in after)-min(times[i] for i in after)+1 if after else None}
    return services,windows,{'before':len(before),'after':len(after)}
