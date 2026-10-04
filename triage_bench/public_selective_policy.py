"""Selective advisory policies; references are used only for scoring and calibration."""
THRESHOLDS=(.5,.6,.7,.8,.9,.95,.99,1.)
MARGINS=(0.,.1,.2)


def candidates():
    return [{'threshold':p,'margin':gap,'maximum_leads':size} for size in (1,2) for p in THRESHOLDS for gap in MARGINS]


def decision(row,policy):
    if not row or row.get('status')!='ok':return {'leads':[],'reason':'failed_or_missing','probability':None,'margin':None}
    choice=row['choice'];probabilities=row['probabilities']
    if choice=='insufficient_evidence':return {'leads':[],'reason':'insufficient_evidence','probability':probabilities[choice],'margin':None}
    p=probabilities[choice];runner_up=max((value for service,value in probabilities.items() if service!=choice),default=0)
    gap=p-runner_up
    if p+1e-9<policy['threshold']:reason='below_probability_boundary'
    elif gap+1e-9<policy['margin']:reason='below_margin_boundary'
    else:reason='shown'
    leads=[choice] if reason=='shown' else []
    # Alternative support is a fixed experimental rule, not a calibrated cause probability.
    if leads and policy['maximum_leads']==2:
        others=sorted(((s,v) for s,v in probabilities.items() if s not in {choice,'insufficient_evidence'} and v>0),key=lambda x:(-x[1],x[0]))
        if others and others[0][1]+1e-9>=.2 and others[0][1]/p+1e-9>=.5:leads.append(others[0][0])
    return {'leads':leads,'reason':reason,'probability':p,'margin':gap}


def evaluate(rows,references,policy,rounds=3):
    actual={(r['case_id'],r['round']):r for r in rows};outcomes=[]
    for ref in references:
        for number in range(1,rounds+1):
            row=actual.get((ref['id'],number));d=decision(row,policy)
            outcomes.append({'id':ref['id'],'group':ref['group'],'target':ref['target'],'fault':ref['fault'],'round':number,
                **d,'choice':row['choice'] if row and row['status']=='ok' else 'missing',
                'correct_first':bool(d['leads']) and d['leads'][0]==ref['target'],
                'cause_included':ref['target'] in d['leads'],'wrong_leads':sum(s!=ref['target'] for s in d['leads']),
                'raw_correct_first':bool(row and row['status']=='ok' and row['choice']==ref['target'])})
    per_round=[]
    for number in range(1,rounds+1):
        rs=[r for r in outcomes if r['round']==number]
        per_round.append({'round':number,'cases':len(references),'shown':sum(bool(r['leads']) for r in rs),
            'correct_first':sum(r['correct_first'] for r in rs),'cause_included':sum(r['cause_included'] for r in rs),
            'wrong_leads':sum(r['wrong_leads'] for r in rs),'total_leads':sum(len(r['leads']) for r in rs),
            'withheld':sum(not r['leads'] for r in rs),'correct_first_withheld':sum(r['raw_correct_first'] and not r['leads'] for r in rs),
            'wrong_first_withheld':sum(not r['raw_correct_first'] and not r['leads'] for r in rs),
            'failed_or_missing':sum(r['reason']=='failed_or_missing' for r in rs)})
    stable=sum(all(r['leads']==rs[0]['leads'] for r in rs) for ref in references if (rs:=[r for r in outcomes if r['id']==ref['id']]))
    return {'policy':policy,'per_round':per_round,'stable_display_cases':stable,'outcomes':outcomes}


def select(curves):
    eligible=[c for c in curves if c['policy']['maximum_leads']==1 and all(r['wrong_leads']==0 and r['shown']>0 for r in c['per_round'])]
    if not eligible:return None
    return sorted(eligible,key=lambda c:(-min(r['correct_first'] for r in c['per_round']),
        -sum(r['correct_first'] for r in c['per_round']),-c['stable_display_cases'],c['policy']['threshold'],c['policy']['margin']))[0]
