"""Matched diagnostic panels, complete denominators and one declared candidate."""
from .incident_scope_features import ARMS
from .publisher_report_features import jev
from .publisher_report_scoring import assess

def score(packets,references,rows,complete,baseline):
    index={(r['claim_id'],r['arm'],r['round']):r for r in rows}
    if len(index)!=len(rows):raise ValueError('Duplicate recorded opportunity.')
    allowed={(p['id'],a,n) for p in packets for a in ARMS for n in (1,2,3)}
    if set(index)-allowed:raise ValueError('Reply outside the planned denominator.')
    refs={r['id']:r['choice'] for r in references};outcomes=[];panels=[];pairs=[];gates=[]
    for n in (1,2,3):
        for p in packets:
            for arm in ARMS:
                pred=jev(index.get((p['id'],arm,n)))
                rule=baseline[p['id']][arm]
                outcomes.append({'id':p['id'],'arm':arm,'round':n,'topic':p['topic'],'reference':refs[p['id']],
                    'prediction':pred,**assess(pred,refs[p['id']]),'literal_rule':rule,'rule_outcome':assess(rule,refs[p['id']])})
        for arm in ARMS:
            for topic in ('all','service_impact','cause_certainty','recovery_scope'):
                items=[o for o in outcomes if o['arm']==arm and o['round']==n and (topic=='all' or o['topic']==topic)]
                panels.append({'arm':arm,'round':n,'topic':topic,'claims':len(items),
                    **{k:sum(o[k] for o in items) for k in ('valid','correct_choice','correct_display','wrong_display','withheld')}})
        control={o['id']:o for o in outcomes if o['round']==n and o['arm']=='full'}
        for arm in ARMS[1:]:
            items={o['id']:o for o in outcomes if o['round']==n and o['arm']==arm}
            gains=[i for i in items if items[i]['correct_display'] and not control[i]['correct_display']]
            losses=[i for i in items if control[i]['correct_display'] and not items[i]['correct_display']]
            pairs.append({'arm':arm,'round':n,'gains':gains,'losses':losses})
            if arm=='selected_section':
                criteria={'no_wrong_display':not any(o['wrong_display'] for o in items.values()),
                    'at_least_five_correct_displays':sum(o['correct_display'] for o in items.values())>=5,
                    'no_correct_display_losses':not losses,
                    'both_previous_error_claims_correctly_displayed':all(items[i]['correct_display'] for i in ('gh-april-2023-c1','gh-april-2023-c5'))}
                gates.append({'round':n,'criteria':criteria,'passes':all(criteria.values())})
    return {'outcomes':outcomes,'panels':panels,'paired':pairs,'gates':gates,'complete_evidence':complete,
        'candidate':'selected_section','candidate_passes':bool(complete and all(g['passes'] for g in gates))}
