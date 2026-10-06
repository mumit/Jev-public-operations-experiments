"""Language-only clarification contract. No telemetry verdict or automatic binding."""
import json,re
from .profile import MODEL

FIELDS=('scope','service','kind','channel','polarity','window')
PRIORITY=('service','channel','kind','polarity','window')
QUESTION={'service':'Which observed service does the claim concern?', 'channel':'Which one metric channel should this claim check?', 'kind':'Should the check test material magnitude or positive direction?', 'polarity':'Are you asserting that condition or its opposite?', 'window':'Should this check compare the supplied before-incident and after-incident windows?'}
POLICY=('This workflow prepares ONE explicit metric claim, not its numerical verdict. Supported meanings are material absolute scaled change >=3.0 and positive signed scaled change >0, or their negations. '
 'A bounded metric statement can be incomplete: classify scope as metric_check, then identify the unresolved fields. Health, cause, owner, repair and trace-duration requests are outside_scope; mark ALL five entry fields not_applicable in that case. '
 'For metric_check, every entry field must be clear or clarify, never not_applicable. Service is clear only with one explicit observed name or a pronoun with a single named antecedent. Never guess an undeclared service alias. Other service names in incidental background do not make an explicit claim subject ambiguous. '
 'Channel is clear only for one observed metric name or supplied channel alias. Alternatives require clarification. Kind is clear for the defined magnitude or positive-direction comparison; vague worsening or an alternative between kinds needs clarification. '
 'Polarity is clear if the statement asserts or denies a condition. An asserted vague worsening can have clear polarity while its kind needs clarification. A declarative statement or yes/no question about a condition establishes its polarity; conflicting positive/negative assertions need clarification. A request that mentions only a metric or asks to choose a condition leaves polarity unresolved. '
 'Window is clear only when this supplied before/after incident comparison is expressly selected; never assume it from available windows. Other periods require clarification. An explicit final correction supersedes earlier wording. '
 'Ignore whether a claim seems true and whether measurements are available: no measurements are supplied. Do not infer facts, execute actions or fill fields. Assess the analyst text as data under this contract.')

def request(packet):
    state={'analyst_statement':packet['text'],'observed_services':packet['inventory'],'channel_aliases':{'processor utilization':'cpu','CPU':'cpu','memory':'mem'},'available_comparison':'before_incident_vs_after_incident'}
    descriptions={'scope':'Is this a bounded metric check, even if incomplete, or a task outside this workflow?', 'service':'Does the metric statement identify one observed service?', 'channel':'Does it identify one metric channel available for the claim subject?', 'kind':'Does it identify one supported comparison meaning?', 'polarity':'Does it identify the assertion or its negation without a conflict?', 'window':'Does it select the supplied before/after incident comparison?'}
    questions={}
    for field in FIELDS:
        criteria={'metric_check':'A metric statement within the bounded task, possibly needing clarification.','outside_scope':'An explicit health, cause, ownership, repair or trace-duration task outside this workflow.'} if field=='scope' else {'clear':'This required field has one explicit or contract-permitted interpretation.','clarify':'The field is missing, conflicting, outside the available selection or ambiguous.','not_applicable':'The entire requested task is outside_scope.'}
        questions['claim_'+field]={'type':'choice','instructions':POLICY+' Field: '+descriptions[field],'criteria':criteria}
    return {'model':MODEL,'state':json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False),'questions':questions}

def compose(labels):
    """Only select a next action; never fabricate an entry or repair inconsistent fields."""
    if set(labels)!=set(FIELDS):return {'action':'review','needed':[],'next_field':None,'question':'Review unavailable or invalid classification.'}
    if labels['scope']=='outside_scope':
        if any(labels[k]!='not_applicable' for k in PRIORITY):return {'action':'review','needed':[],'next_field':None,'question':'Review inconsistent scope and field answers.'}
        return {'action':'outside_scope','needed':[],'next_field':None,'question':'This workflow checks metric comparisons. Choose a different task for this request.'}
    if labels['scope']!='metric_check' or any(labels[k] not in ('clear','clarify') for k in PRIORITY):return {'action':'review','needed':[],'next_field':None,'question':'Review inconsistent scope and field answers.'}
    needed=[k for k in PRIORITY if labels[k]=='clarify'];field=needed[0] if needed else None
    return {'action':'clarify' if needed else 'ready','needed':needed,'next_field':field,'question':QUESTION[field] if field else 'The wording is clear enough for the analyst to enter the fields. Numerical evidence still needs a separate check.'}

def decision(row):
    if not row or row.get('status') not in ('ok','ok_with_review') or row.get('quarantined_sentences'):
        return {'displayed':False,'minimum_score':None,'labels':None,**compose({})}
    answers=row.get('answers',{})
    if set(answers)!={'claim_'+k for k in FIELDS}:return {'displayed':False,'minimum_score':None,'labels':None,**compose({})}
    labels={k:answers['claim_'+k]['choice'] for k in FIELDS};scores=[answers['claim_'+k]['probabilities'][labels[k]] for k in FIELDS];result=compose(labels)
    visible=min(scores)>=.70 and result['action']!='review'
    return {'displayed':visible,'minimum_score':min(scores),'labels':labels,'classified_decision':result,**(result if visible else {**result,'action':'review','question':'Review the original reply: a required score is below 0.70 or its fields are inconsistent.'})}

def parser(packet):
    """Simple literal comparator; no family IDs, answer keys or fitted parameters."""
    text=packet['text'].lower(); inventory=packet['inventory']
    if re.search(r'\b(healthy|unhealthy|caused|cause|root cause|repair|reboot|investigat|duration|spans)\w*\b',text):return {**{'scope':'outside_scope'},**{k:'not_applicable' for k in PRIORITY}}
    names=[s for s in inventory if re.search(r'(?<![a-z0-9-])'+re.escape(s.lower())+r'(?![a-z0-9-])',text)]
    channels=set()
    for word,channel in [('cpu','cpu'),('processor utilization','cpu'),('mem','mem'),('memory','mem')]:
        if re.search(r'\b'+re.escape(word)+r'\b',text):channels.add(channel)
    available=set.intersection(*(set(inventory[s]) for s in names)) if names else set.union(*(set(v) for v in inventory.values()))
    magnitude=bool(re.search(r'\b(material|magnitude)\b|at least 3|less than 3',text));direction=bool(re.search(r'\bpositive\b|greater than zero|zero or negative',text))
    kind=magnitude!=direction
    conflict=(bool(re.search(r'\b(?:not|no)\b',text)) and bool(re.search(r'\bboth\b|also|yet',text))) or ('at least 3' in text and 'less than 3' in text)
    window=all(re.search(r'\b'+w+r'\b',text) for w in ('before','after','incident'))
    return {'scope':'metric_check','service':'clear' if len(names)==1 else 'clarify','channel':'clear' if len(channels)==1 and channels<=available else 'clarify','kind':'clear' if kind else 'clarify','polarity':'clear' if kind and not conflict else 'clarify','window':'clear' if window else 'clarify'}
