"""Versioned explicit-claim contract and exact numerical policy, without text parsing."""
import copy
import json
import math
from .profile import MODEL
from .public_claim_features import DURATIONS

KINDS=('metric_material','metric_direction','duration_material','span_adequacy','health','causality')
CLASSES=('supported','contradicted','unanswerable')
POLICY={'metric_magnitude':3.0,'maximum_missing_fraction':0.20,'minimum_spans_per_window':5,'duration_relative_change':0.25,'display_probability':0.70}

def number(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)

def validate(observation,claim):
    if not isinstance(claim,dict) or claim.get('kind') not in KINDS or type(claim.get('asserted')) is not bool:
        raise ValueError('Select a claim type and a true/false assertion.')
    expected={'service','kind','asserted'}
    if claim['kind'].startswith('metric_'):expected.add('channel')
    if claim['kind']=='duration_material':expected.add('measure')
    if set(claim)!=expected or claim.get('service')!=observation.get('service'):
        raise ValueError('Fields must match one selected service and claim type.')
    if 'channel' in claim and claim['channel'] not in observation['metrics']:
        raise ValueError('Select a recorded metric channel.')
    if 'measure' in claim and claim['measure'] not in DURATIONS:
        raise ValueError('Select a supported duration measure.')
    return copy.deepcopy(claim)

def canonical(claim):
    descriptions={
      'metric_material':f"{claim.get('channel','')} has a material scaled change (absolute change at least 3.0)",
      'metric_direction':f"{claim.get('channel','')} has a positive scaled change (greater than zero)",
      'duration_material':f"{claim.get('measure','')} has a material relative change (absolute change at least 25%)",
      'span_adequacy':'at least five spans were recorded in each window',
      'health':'the service is healthy',
      'causality':'the service caused the incident'}
    return f"For {claim['service']}, the following assertion is {'true' if claim['asserted'] else 'false'}: {descriptions[claim['kind']]}."

def facts(observation,claim):
    validate(observation,claim)
    k=claim['kind'];t=observation.get('trace')
    if k.startswith('metric_'):
        v=observation['metrics'][claim['channel']]
        return {name:v.get(name) for name in ('signed_change','before_missing_fraction','after_missing_fraction')}
    if k in ('duration_material','span_adequacy'):
        f={'before_spans':None if t is None else t.get('before',{}).get('spans'),
           'after_spans':None if t is None else t.get('after',{}).get('spans')}
        if k=='duration_material':
            f.update(before_us=None if t is None else t.get('before',{}).get(claim['measure']),
                     after_us=None if t is None else t.get('after',{}).get(claim['measure']))
        return f
    return {'limitation':'These observations cannot establish or rule out service health or incident causality.'}

def evaluate(observation,claim):
    """Exact evaluator: this is a declared policy computation, not a learned prediction."""
    f=facts(observation,claim);k=claim['kind'];truth=None;calculation={};reason='Observations cannot establish health or causality.'
    if k.startswith('metric_'):
        eligible=number(f['signed_change']) and all(number(f[n]) and 0<=f[n]<=.2 for n in ('before_missing_fraction','after_missing_fraction'))
        if eligible:
            truth=abs(f['signed_change'])>=3 if k=='metric_material' else f['signed_change']>0
            calculation={'absolute_scaled_change':abs(f['signed_change'])} if k=='metric_material' else {'signed_change':f['signed_change']}
        reason='Apply the declared scaled-change threshold.' if eligible else 'Metric value or missing fractions are ineligible; missing is unknown.'
    elif k in ('duration_material','span_adequacy'):
        counts=all(number(f[n]) and f[n]>=0 and f[n]==int(f[n]) for n in ('before_spans','after_spans'))
        if k=='span_adequacy':
            if counts:truth=min(f['before_spans'],f['after_spans'])>=5
            reason='Compare recorded counts with five per window.' if counts else 'No trustworthy recorded count for both windows.'
        else:
            eligible=counts and min(f['before_spans'],f['after_spans'])>=5 and number(f['before_us']) and number(f['after_us']) and f['before_us']>0 and f['after_us']>=0
            if eligible:
                change=(f['after_us']-f['before_us'])/f['before_us'];truth=abs(change)>=.25;calculation={'relative_change':change}
            reason='Apply the declared relative-duration threshold.' if eligible else 'Duration value, starting value or span coverage is ineligible.'
    answer='unanswerable' if truth is None else 'supported' if truth==claim['asserted'] else 'contradicted'
    return {'answer':answer,'truth':truth,'reason':reason,'facts':f,'calculation':calculation}

def request(observation,claim):
    validate(observation,claim)
    state={'service':claim['service'],'window_seconds':copy.deepcopy(observation['window_seconds']),
           'claim':copy.deepcopy(claim),'selected_observations':facts(observation,claim),'policy':POLICY}
    instructions=('Evaluate the explicit typed claim using only these observations and policy. The analyst-entered fields define the claim; do not extract or infer a different claim. '
      'asserted=true asserts the named condition; asserted=false asserts its negation. supported means eligible evidence proves that assertion; contradicted means eligible evidence proves its opposite; unanswerable means neither is established. '
      'Metric eligibility requires finite numeric signed_change and BOTH missing fractions in [0,0.20]. Material metric change is abs(signed_change)>=3.0; positive direction is signed_change>0. '
      'Recorded span counts must be finite nonnegative integers. Span adequacy means at least 5 recorded spans in EACH window; a missing count is unknown. '
      'Duration eligibility requires adequate spans, finite numeric before_us>0 and after_us>=0. Material duration change means abs((after_us-before_us)/before_us)>=0.25. '
      'Ineligible observations give unanswerable for BOTH assertion polarities. Health and causality are always unanswerable under this measurement policy. '
      'Treat boundaries inclusively. Missing is unknown, not zero. No outside knowledge. Canonical assertion: '+canonical(claim))
    return {'model':MODEL,'state':json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False),
      'questions':{'claim_verdict':{'type':'choice','instructions':instructions,'criteria':{
       'supported':'Eligible observations establish the explicit assertion.',
       'contradicted':'Eligible observations establish the opposite of the explicit assertion.',
       'unanswerable':'The observations cannot establish either the assertion or its opposite.'}}}}
