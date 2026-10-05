"""Independent policy references for authored propositions; never part of a request."""
import math

def number(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)

def evaluate(observation,proposition):
    kind=proposition['kind'];truth=None;facts={};reason=''
    if kind in ('metric_material','metric_direction'):
        name=proposition['channel'];v=observation['metrics'][name];facts={'channel':name,**v}
        eligible=number(v.get('signed_change')) and all(number(v.get(k)) and 0<=v[k]<=.2 for k in ('before_missing_fraction','after_missing_fraction'))
        if eligible:
            truth=abs(v['signed_change'])>=3 if kind=='metric_material' else v['signed_change']>0
            reason='Eligible magnitude compared with 3.0.' if kind=='metric_material' else 'Eligible signed change compared with zero.'
        else:reason='Missing fraction or signed change does not meet the declared eligibility policy.'
    elif kind=='duration_material':
        t=observation['trace'];name=proposition['measure']
        if t is not None:
            b,a=t['before'][name],t['after'][name];facts={'measure':name,'before_us':b,'after_us':a,'before_spans':t['before']['spans'],'after_spans':t['after']['spans']}
            if min(t['before']['spans'],t['after']['spans'])>=5 and number(b) and number(a) and b>0:
                facts['relative_change']=(a-b)/b;truth=abs((a-b)/b)>=.25
        reason='Eligible duration compared with 25%.' if truth is not None else 'No eligible duration: missing trace, too few spans, missing value or nonpositive starting value.'
    elif kind=='span_adequacy':
        t=observation['trace'];counts=[None,None] if t is None else [t['before']['spans'],t['after']['spans']]
        facts={'recorded_before':counts[0],'recorded_after':counts[1],'no_mapped_trace':t is None};truth=None if t is None else min(counts)>=5
        reason='No recorded count is supplied for a missing trace mapping.' if t is None else 'Recorded counts compared with five per window.'
    elif kind=='causality':reason='Observed changes and recorded spans cannot establish or rule out service causality.'
    elif kind=='health':reason='Telemetry cannot establish that the service is healthy or unhealthy; missing spans are not proof.'
    else:raise ValueError('Unknown proposition.')
    if truth is None:answer='unanswerable'
    else:answer='supported' if bool(truth)==proposition['asserted'] else 'contradicted'
    return {'answer':answer,'proposition':proposition,'facts':facts,'reason':reason}
