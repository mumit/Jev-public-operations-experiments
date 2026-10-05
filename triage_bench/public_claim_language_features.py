"""Meaning-preserving statement variants; unchanged ledger and verdict instructions."""
from .public_claim_data import wording as canonical
from .public_claim_features import request as old_request,FIELDS,POLICY,CLASSES
FORMS=('canonical','plain','rephrased')
ARMS=('ledger',)

def variants(p):
    yes=p['asserted'];kind=p['kind'];first=canonical(p)
    if kind=='metric_material':
        channel=p['channel']
        plain=f"Under the declared eligibility policy, the absolute scaled change of {channel} is {'at least' if yes else 'less than'} 3."
        alternative=f"Under the declared eligibility policy, the magnitude of the {channel} signed change is {'not below' if yes else 'not at least'} three."
    elif kind=='metric_direction':
        channel=p['channel']
        plain=f"The eligible signed change for {channel} is {'greater than zero' if yes else 'zero or negative'}."
        alternative=f"The eligible signed change for {channel} is {'neither zero nor negative' if yes else 'not greater than zero'}."
    elif kind=='duration_material':
        name=p['measure']
        plain=f"Using eligible samples, {name} changes by {'at least' if yes else 'less than'} 25% in absolute relative magnitude."
        alternative=f"For eligible samples of {name}, the absolute relative change is {'not below' if yes else 'not at least'} 25%."
    elif kind=='span_adequacy':
        plain='Each window has a recorded span count of five or more.' if yes else 'One or both windows have a recorded span count below five.'
        alternative='Neither recorded window count is below five.' if yes else 'It is not the case that both recorded window counts are at least five.'
    elif kind=='health':
        word='healthy' if yes else 'unhealthy'
        plain=f"The supplied observations establish that this service is {word}."
        alternative=f"This service is {word}, as established by the supplied observations."
    elif kind=='causality':
        plain='This service caused the observed incident.' if yes else 'This service did not cause the observed incident.'
        alternative='The observed incident was caused by this service.' if yes else 'The observed incident was not caused by this service.'
    else:raise ValueError('Unknown wording proposition.')
    return {'canonical':first,'plain':plain,'rephrased':alternative}

def request(observation,statements):
    return old_request(observation,statements,'ledger')
