"""Fixed selective gates by whole report, verdict class and recorded round."""
from .literal_claim_features import ARMS
from .publisher_report_features import jev
from .publisher_report_scoring import assess
from .selective_report_data import CHOICES,TOPICS

COUNTS=('valid','correct_choice','correct_display','wrong_display','withheld')

def score(packets,references,rows,complete,baseline):
    index={(r['claim_id'],r['arm'],r['round']):r for r in rows}
    allowed={(p['id'],a,n) for p in packets for a in ARMS for n in (1,2,3)}
    if len(index)!=len(rows) or set(index)-allowed:raise ValueError('Invalid reply join.')
    refs={r['id']:r['choice'] for r in references};outcomes=[];panels=[];pairs=[];gates=[]
    sources=list(dict.fromkeys(p['source_id'] for p in packets))
    for n in (1,2,3):
        for p in packets:
            for arm in ARMS:
                pred=jev(index.get((p['id'],arm,n)));rule=baseline[p['id']][arm]
                outcomes.append({'id':p['id'],'source_id':p['source_id'],'topic':p['topic'],'arm':arm,'round':n,
                    'reference':refs[p['id']],'prediction':pred,**assess(pred,refs[p['id']]),
                    'literal_rule':rule,'rule_outcome':assess(rule,refs[p['id']])})
        current=[o for o in outcomes if o['round']==n]
        for arm in ARMS:
            for source in ['all',*sources]:
                for verdict in ['all',*CHOICES]:
                    items=[o for o in current if o['arm']==arm and (source=='all' or o['source_id']==source) and (verdict=='all' or o['reference']==verdict)]
                    panels.append({'arm':arm,'round':n,'source_id':source,'reference_class':verdict,
                        'claims':len(items),**{k:sum(o[k] for o in items) for k in COUNTS}})
            for topic in TOPICS:
                items=[o for o in current if o['arm']==arm and o['topic']==topic]
                panels.append({'arm':arm,'round':n,'source_id':'all','topic':topic,'reference_class':'all',
                    'claims':len(items),**{k:sum(o[k] for o in items) for k in COUNTS}})
        control={o['id']:o for o in current if o['arm']=='legacy'}
        candidate={o['id']:o for o in current if o['arm']=='literal'}
        gains=[i for i in candidate if candidate[i]['correct_display'] and not control[i]['correct_display']]
        losses=[i for i in candidate if control[i]['correct_display'] and not candidate[i]['correct_display']]
        pairs.append({'round':n,'gains':gains,'losses':losses,'control_wrong_displays':sum(o['wrong_display'] for o in control.values()),
            'comparative_error_opportunity':any(o['wrong_display'] for o in control.values())})
        for source in ['all',*sources]:
            items=[o for o in candidate.values() if source=='all' or o['source_id']==source]
            criteria={'no_wrong_display':not any(o['wrong_display'] for o in items),
                'complete_recorded_evidence':complete and all(o['valid'] for o in items),
                'no_correct_display_losses':not any(i in losses for i in [o['id'] for o in items])}
            if source!='all':
                criteria['at_least_six_correct_displays']=sum(o['correct_display'] for o in items)>=6
                criteria['all_three_classes_correctly_displayed']=all(any(o['correct_display'] and o['reference']==c for o in items) for c in CHOICES)
            gates.append({'source_id':source,'round':n,'criteria':criteria,'passes':all(criteria.values())})
    return {'outcomes':outcomes,'panels':panels,'paired':pairs,'gates':gates,'candidate':'literal',
        'complete_evidence':complete,'candidate_passes':bool(complete and all(g['passes'] for g in gates))}
