"""Compare fresh answers under one new literal reference contract."""
from .literal_claim_features import ARMS
from .publisher_report_features import jev
from .publisher_report_scoring import assess

def score(packets,references,rows,complete,baseline):
    index={(r['claim_id'],r['arm'],r['round']):r for r in rows};allowed={(p['id'],a,n) for p in packets for a in ARMS for n in (1,2,3)}
    if len(index)!=len(rows) or set(index)-allowed:raise ValueError('Invalid reply join.')
    refs={r['id']:r['choice'] for r in references};outcomes=[];panels=[];pairs=[];gates=[]
    for n in (1,2,3):
        for p in packets:
            for arm in ARMS:
                pred=jev(index.get((p['id'],arm,n)));rule=baseline[p['id']][arm]
                outcomes.append({'id':p['id'],'topic':p['topic'],'arm':arm,'round':n,'reference':refs[p['id']],
                    'prediction':pred,**assess(pred,refs[p['id']]),'literal_rule':rule,'rule_outcome':assess(rule,refs[p['id']])})
        for a in ARMS:
            for topic in ('all','service_impact','cause_certainty','recovery_scope'):
                items=[o for o in outcomes if o['round']==n and o['arm']==a and (topic=='all' or o['topic']==topic)]
                panels.append({'arm':a,'round':n,'topic':topic,'claims':len(items),
                    **{k:sum(o[k] for o in items) for k in ('valid','correct_choice','correct_display','wrong_display','withheld')}})
        control={o['id']:o for o in outcomes if o['round']==n and o['arm']=='legacy'}
        candidate={o['id']:o for o in outcomes if o['round']==n and o['arm']=='literal'}
        gains=[i for i in candidate if candidate[i]['correct_display'] and not control[i]['correct_display']]
        losses=[i for i in candidate if control[i]['correct_display'] and not candidate[i]['correct_display']]
        pairs.append({'round':n,'gains':gains,'losses':losses})
        criteria={'no_wrong_display':not any(o['wrong_display'] for o in candidate.values()),
            'at_least_five_correct_displays':sum(o['correct_display'] for o in candidate.values())>=5,
            'no_correct_display_losses':not losses,
            'both_previous_error_claims_correctly_displayed':all(candidate[i]['correct_display'] for i in ('gh-april-2023-c1','gh-april-2023-c5')),
            'confirmation_claim_correctly_displayed':candidate['gh-april-2023-c3']['correct_display']}
        gates.append({'round':n,'criteria':criteria,'passes':all(criteria.values())})
    return {'outcomes':outcomes,'panels':panels,'paired':pairs,'gates':gates,'candidate':'literal',
        'complete_evidence':complete,'candidate_passes':bool(complete and all(g['passes'] for g in gates))}
