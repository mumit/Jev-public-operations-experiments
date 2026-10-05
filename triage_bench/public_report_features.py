"""Paired atomic and report judgments against identical multi-service facts."""
import json,copy
from .public_claim_features import request as original,ledger,POLICY,CLASSES
from .public_claim_language_features import variants
FIELDS=tuple('statement_'+x for x in 'abcdef')
ARMS=('atomic','report')

def text(observation,proposition):
    sentence=variants(proposition)['plain']
    service=observation['service']
    return f'For service {service}: '+sentence.replace('this service',service).replace('This service',service)

def request(observations,claims,arm):
    if arm not in ARMS or set(claims)!=set(FIELDS) or len(observations)!=2:raise ValueError('Report identity.')
    names=[o['service'] for o in observations]
    if len(set(names))!=2:raise ValueError('Distinct services required.')
    # Reuse every numerical/verdict instruction and criterion from the frozen task.
    template=original(observations[0],{f:'unused' for f in ('statement_a','statement_b','statement_c')},'ledger')
    instruction=template['questions']['statement_a']['instructions'].split('Statement: ')[0]
    instruction=instruction.replace('supplied service observations','supplied observations for the explicitly named service')
    state={'services':[ledger(o) for o in observations]}
    if arm=='report':state['report']='Operations note. Each numbered sentence is a separate assertion.\n'+'\n'.join(f'{i}. {claims[f]}' for i,f in enumerate(FIELDS,1))
    return {'model':template['model'],'state':json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False),
        'questions':{f:{'type':'choice','instructions':instruction+(f'Assess only sentence {i} in the supplied report. Use only facts for its explicitly named service; do not transfer evidence between services.' if arm=='report' else 'Statement: '+claims[f]),'criteria':copy.deepcopy(template['questions']['statement_a']['criteria'])} for i,f in enumerate(FIELDS,1)}}
