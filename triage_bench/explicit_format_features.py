"""Focused wording and disclosed arithmetic preprocessing for explicit claims."""
import copy,json
from .explicit_claim_features import validate,facts,number,request as typed
from .profile import MODEL

ARMS=('typed','focused','calculated')

def statement(claim):
    k=claim['kind'];positive=claim['asserted'];s=claim['service']
    if k=='metric_material':return f"For {s}, the absolute scaled change in {claim['channel']} is {'at least' if positive else 'less than'} 3.0."
    if k=='metric_direction':return f"For {s}, the signed scaled change in {claim['channel']} is {'greater than zero' if positive else 'zero or negative'}."
    if k=='duration_material':return f"For {s}, the absolute relative change in {claim['measure']} is {'at least' if positive else 'less than'} 0.25."
    if k=='span_adequacy':return f"For {s}, {'both windows have at least five recorded spans' if positive else 'at least one window has fewer than five recorded spans'}."
    if k=='health':return f"{s} is {'healthy' if positive else 'unhealthy'}."
    return f"{s} {'caused' if positive else 'did not cause'} the incident."

def calculated(f,k):
    """Derived numeric facts and validity, never the selected assertion's verdict."""
    if k.startswith('metric_'):
        eligible=number(f['signed_change']) and all(number(f[n]) and 0<=f[n]<=.2 for n in ('before_missing_fraction','after_missing_fraction'))
        return {'observations_eligible':eligible,'absolute_scaled_change':abs(f['signed_change']) if eligible else None}
    if k in ('duration_material','span_adequacy'):
        counts=all(number(f[n]) and f[n]>=0 and f[n]==int(f[n]) for n in ('before_spans','after_spans'))
        if k=='span_adequacy':return {'recorded_counts_eligible':counts,'minimum_recorded_spans':min(f['before_spans'],f['after_spans']) if counts else None}
        eligible=counts and min(f['before_spans'],f['after_spans'])>=5 and number(f['before_us']) and number(f['after_us']) and f['before_us']>0 and f['after_us']>=0
        change=(f['after_us']-f['before_us'])/f['before_us'] if eligible else None
        return {'observations_eligible':eligible,'relative_change':change,'absolute_relative_change':abs(change) if change is not None else None}
    return {'measurement_limit':'Health and causality are outside the measurement policy.'}

def request(observation,claim,arm):
    if arm=='typed':return typed(observation,claim)
    if arm not in ARMS:raise ValueError('Unknown explicit representation.')
    validate(observation,claim);k=claim['kind'];f=facts(observation,claim)
    policy=(
      'Eligible metrics need a finite numeric signed_change and numeric before_missing_fraction and after_missing_fraction in [0,0.20]. For either a magnitude or direction statement, ineligible means unanswerable, regardless of assertion polarity. Absolute scaled change means abs(signed_change); 3.0 is inclusive. Zero is not positive.' if k.startswith('metric_') else
      'Eligible durations need finite nonnegative integer recorded counts, at least five spans in each window, finite numeric before_us>0 and after_us>=0. Relative change means (after_us-before_us)/before_us. Compare its absolute value with 0.25 exactly; the boundary is inclusive. Ineligible observations mean unanswerable, regardless of assertion polarity.' if k=='duration_material' else
      'Recorded counts must be finite nonnegative integers. Compare each window with five recorded spans. A recorded zero is a known count, not missing. A missing or invalid count means unanswerable, regardless of assertion polarity.' if k=='span_adequacy' else
      'These numerical observations cannot establish or rule out health or incident causality. Both positive and negative health/causality statements are unanswerable.')
    state={'service':claim['service'],'window_seconds':copy.deepcopy(observation['window_seconds']),'selected_observations':f}
    if arm=='calculated':state['calculated_observations']=calculated(f,k)
    instructions=('Judge this single statement against only the selected service observations. '+policy+' '
      'supported means eligible evidence establishes the statement; contradicted means eligible evidence establishes its opposite; unanswerable means neither is established. '
      +('Calculated observations are deterministic preprocessing of the same raw facts. Use the supplied eligibility and computed values; compare thresholds without rounding. ' if arm=='calculated' else '')
      +'Do not infer health, causality, missing values or a different service. Statement: '+statement(claim))
    return {'model':MODEL,'state':json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False),'questions':{'claim_verdict':{'type':'choice','instructions':instructions,
       'criteria':{'supported':'Eligible observations establish the stated comparison or assertion.','contradicted':'Eligible observations establish the opposite of the stated comparison or assertion.','unanswerable':'The observations cannot establish the statement or its opposite.'}}}}
