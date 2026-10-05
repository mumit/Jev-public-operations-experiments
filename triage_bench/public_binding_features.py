"""Isolate explicit claim binding, question grouping and service evidence scope."""
import json,copy
from .public_report_features import FIELDS,POLICY,CLASSES
ARMS=('lookup','bound','single','scoped')
EDGES=(('lookup','bound'),('bound','single'),('single','scoped'))

def request(packet,arm,field=None):
    if arm not in ARMS or (arm in ('single','scoped'))!=(field in FIELDS):raise ValueError('Binding request identity.')
    body=copy.deepcopy(packet['requests']['report'])
    if arm=='lookup':return body
    for i,f in enumerate(FIELDS,1):
        q=body['questions'][f];prefix=q['instructions'].split('Assess only sentence ')[0]
        service=packet['claim_sources'][f]['service'];claim=packet['statements'][f]
        q['instructions']=prefix+f'Claim ID C{i}, sentence {i} of the supplied report. Assess only this exact statement for service {service}. Use only its own service facts; do not transfer evidence between services. Statement: '+claim
    if arm in ('single','scoped'):body['questions']={field:body['questions'][field]}
    if arm=='scoped':
        state=json.loads(body['state']);service=packet['claim_sources'][field]['service']
        state['services']=[s for s in state['services'] if s['service']==service]
        if len(state['services'])!=1:raise ValueError('Unique service ledger required.')
        body['state']=json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False)
    return body
