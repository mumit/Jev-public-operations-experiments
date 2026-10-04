"""Frozen disagreement routing. References enter scoring only, never decisions."""
from .public_selective_policy import decision
POLICY={'threshold':.7,'margin':0.,'maximum_leads':1}

def route(row,ml_choice):
    base=decision(row,POLICY)
    if not base['leads']:return {**base,'base_leads':[],'action':'withheld','ml_choice':ml_choice}
    if ml_choice not in row['probabilities'] or ml_choice=='insufficient_evidence':
        return {**base,'leads':[],'base_leads':base['leads'],'action':'review_required','reason':'ml_unavailable','ml_choice':ml_choice}
    if row['choice']!=ml_choice:
        return {**base,'leads':[],'base_leads':base['leads'],'action':'review_required','reason':'models_disagree','ml_choice':ml_choice}
    return {**base,'base_leads':base['leads'],'action':'lead','reason':'models_agree','ml_choice':ml_choice}

def assess(rows,references,controls,rounds=3):
    actual={(r['case_id'],r['round']):r for r in rows};outcomes=[]
    for ref in references:
        for number in range(1,rounds+1):
            row=actual.get((ref['id'],number));d=route(row,controls[ref['id']]['ml']['choice'])
            outcomes.append({'id':ref['id'],'group':ref['group'],'target':ref['target'],'fault':ref['fault'],'round':number,**d,
                'choice':row['choice'] if row and row['status']=='ok' else 'missing',
                'base_correct':bool(d['base_leads']) and d['base_leads'][0]==ref['target'],
                'retained_correct':bool(d['leads']) and d['leads'][0]==ref['target'],
                'base_wrong':bool(d['base_leads']) and d['base_leads'][0]!=ref['target'],
                'retained_wrong':bool(d['leads']) and d['leads'][0]!=ref['target'],
                'raw_correct':bool(row and row['status']=='ok' and row['choice']==ref['target']),
                'ml_correct':d['ml_choice']==ref['target']})
    per_round=[]
    for number in range(1,rounds+1):
        rs=[r for r in outcomes if r['round']==number];shown=sum(bool(r['base_leads']) for r in rs);retained=sum(bool(r['leads']) for r in rs)
        wrong=sum(r['base_wrong'] for r in rs);remaining=sum(r['retained_wrong'] for r in rs)
        per_round.append({'round':number,'cases':len(references),'base_shown':shown,'base_correct':sum(r['base_correct'] for r in rs),'base_wrong':wrong,
            'retained':retained,'retained_correct':sum(r['retained_correct'] for r in rs),'retained_wrong':remaining,
            'review_required':sum(r['action']=='review_required' for r in rs),'wrong_routed_to_review':sum(r['base_wrong'] and r['action']=='review_required' for r in rs),
            'correct_routed_to_review':sum(r['base_correct'] and r['action']=='review_required' for r in rs),
            'base_withheld':len(rs)-shown,'raw_correct_base_withheld':sum(r['raw_correct'] and not r['base_leads'] for r in rs),
            'wrong_rate_before':wrong/shown if shown else None,'wrong_rate_after':remaining/retained if retained else None,
            'agreements_both_wrong':sum(r['retained_wrong'] for r in rs),
            'disagreements_jev_correct':sum(r['action']=='review_required' and r['base_correct'] for r in rs),
            'disagreements_ml_correct':sum(r['action']=='review_required' and r['ml_correct'] for r in rs),
            'disagreements_both_wrong':sum(r['action']=='review_required' and not r['base_correct'] and not r['ml_correct'] for r in rs),
            'failed_or_missing':sum(r['reason']=='failed_or_missing' for r in rs)})
    opportunity=all(r['base_wrong']>0 for r in per_round)
    gate=opportunity and all(r['wrong_routed_to_review']>0 and r['retained_correct']>0 and r['wrong_rate_after']<r['wrong_rate_before'] for r in per_round)
    stable=sum(len({(r['action'],tuple(r['leads']),r['ml_choice']) for r in outcomes if r['id']==ref['id']})==1 for ref in references)
    return {'policy':POLICY,'per_round':per_round,'outcomes':outcomes,'stable_display_cases':stable,
        'distinct_wrong_cases_routed_to_review':sorted({r['id'] for r in outcomes if r['base_wrong'] and r['action']=='review_required'}),
        'distinct_correct_cases_routed_to_review':sorted({r['id'] for r in outcomes if r['base_correct'] and r['action']=='review_required'}),
        'distinct_wrong_cases_retained':sorted({r['id'] for r in outcomes if r['retained_wrong']}),
        'research_gate':'passed' if gate else 'failed' if opportunity else 'no_error_opportunity',
        'gate_definition':'Each round starts with a wrong shown lead, routes at least one to review, retains correct coverage and reduces the wrong fraction among retained leads. Descriptive research criterion; not an operational error guarantee.'}
