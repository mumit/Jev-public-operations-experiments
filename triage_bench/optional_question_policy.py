"""Gate only the required decision prefix; never bind fields or clear entry."""
from .optional_clarification_features import action,decision as all_fields
from .clarification_features import FIELDS,PRIORITY

def decision(row,policy):
    if policy=='all_fields':
        d=all_fields(row,'checklist');return {**d,'required_score_fields':list(FIELDS),'ignored_fields':[]}
    if policy!='first_question':raise ValueError('Unknown optional display policy.')
    valid=bool(row and row.get('status') in ('ok','ok_with_review') and not row.get('quarantined_sentences') and set(row.get('answers',{}))=={'claim_'+k for k in FIELDS})
    if not valid:return {'valid':False,'choice':None,'displayed':False,'minimum_score':None,'labels':None,'required_score_fields':[],'ignored_fields':[],**action(None)}
    labels={k:row['answers']['claim_'+k]['choice'] for k in FIELDS};required=['scope'];choice=None
    if labels['scope']=='outside_scope':choice='outside_scope'
    elif labels['scope']=='metric_check':
        for field in PRIORITY:
            required.append(field)
            if labels[field]=='clarify':choice=field;break
            if labels[field]!='clear':break
        else:choice='no_question'
    score=min(row['answers']['claim_'+k]['probabilities'][labels[k]] for k in required)
    visible=bool(choice is not None and score>=.70)
    return {'valid':True,'choice':choice,'displayed':visible,'minimum_score':score,'labels':labels,'required_score_fields':required,'ignored_fields':[k for k in FIELDS if k not in required],**action(choice if visible else None)}
