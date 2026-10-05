"""Numerical references derived directly from observations, never injected labels."""
import math


def number(value):
    return isinstance(value, (float,int)) and not isinstance(value,bool) and math.isfinite(value)


def reference(observation):
    eligible = {}
    for channel, values in observation['metrics'].items():
        if number(values.get('signed_change')) and all(number(values.get(k)) and 0<=values[k]<=.2 for k in ('before_missing_fraction','after_missing_fraction')):
            eligible[channel] = abs(values['signed_change'])
    metric = 'unknown' if not eligible else 'material' if max(eligible.values())>=3 else 'quiet'
    channels = ['no_eligible_metric'] if not eligible else sorted(k for k,v in eligible.items() if v==max(eligible.values()))
    t = observation['trace'];durations = {}
    if t is None or (t['before']['spans']==0 and t['after']['spans']==0):
        coverage='absent'
    elif min(t['before']['spans'],t['after']['spans'])>=5:
        coverage='adequate'
        for key in ('duration_median_us','duration_p90_us','uncovered_duration_median_us','uncovered_duration_p90_us'):
            before,after=t['before'][key],t['after'][key]
            if number(before) and number(after) and before>0:
                durations[key]=(after-before)/before
    else:
        coverage='limited'
    trace='unknown' if not durations else 'material' if any(abs(v)>=.25 for v in durations.values()) else 'quiet'
    composed='change_supported' if 'material' in (metric,trace) else 'evidence_limited' if 'unknown' in (metric,trace) else 'no_material_change'
    return {'answers': {'metric_change':[metric],'trace_change':[trace],'trace_coverage':[coverage],'metric_channel':channels},
            'composition':composed,'evidence':{'eligible_metric_magnitudes':eligible,'eligible_duration_relative_changes':durations}}
