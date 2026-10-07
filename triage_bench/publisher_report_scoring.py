"""Failure-inclusive matched reading scores and unchanged research gates."""
from .publisher_report_features import rules,jev,hybrid

METHODS=('rules','jev','hybrid')

def assess(prediction,reference):
    correct=prediction['choice']==reference
    return {'correct_choice':bool(prediction['valid'] and correct),'correct_display':bool(prediction['displayed'] and correct),'wrong_display':bool(prediction['displayed'] and not correct),'withheld':not prediction['displayed'],'valid':prediction['valid']}

def score(packets,refs,rows,complete,rule_predictions=None):
    by_id={r['id']:r['choice'] for r in refs};index={(r['claim_id'],r['round']):r for r in rows}
    if len(index)!=len(rows):raise ValueError('Duplicate replies.')
    outcomes=[];panels=[];gates=[];paired=[]
    for n in (1,2,3):
        for packet in packets:
            rule=rule_predictions[packet['id']] if rule_predictions is not None else rules(packet);j=jev(index.get((packet['id'],n)));h=hybrid(rule,j)
            for method,pred in zip(METHODS,(rule,j,h)):
                outcomes.append({'id':packet['id'],'source_id':packet['source_id'],'topic':packet['topic'],'round':n,'method':method,'reference':by_id[packet['id']],'prediction':pred,**assess(pred,by_id[packet['id']])})
        criteria=[('overall','all')]+[('incident',s) for s in dict.fromkeys(p['source_id'] for p in packets)]+[('topic',t) for t in ('service_impact','cause_certainty','recovery_scope')]+[('reference',r) for r in ('supported','contradicted','not_established')]
        for kind,key in criteria:
            selected=lambda o:o['round']==n and (kind=='overall' or kind=='incident' and o['source_id']==key or kind=='topic' and o['topic']==key or kind=='reference' and o['reference']==key)
            for method in METHODS:
                os=[o for o in outcomes if o['method']==method and selected(o)]
                panel={'kind':kind,'key':key,'round':n,'method':method,'claims':len(os),**{k:sum(o[k] for o in os) for k in ('valid','correct_choice','correct_display','wrong_display','withheld')}}
                panels.append(panel)
                if method=='hybrid' and kind in {'overall','incident','topic'}:
                    criteria={'no_wrong_display':panel['wrong_display']==0,'correct_display_coverage':panel['correct_display']>=.8*panel['claims']}
                    gates.append({'kind':kind,'key':key,'round':n,'criteria':criteria,'passes':all(criteria.values())})
        r={o['id']:o for o in outcomes if o['round']==n and o['method']=='rules'};h={o['id']:o for o in outcomes if o['round']==n and o['method']=='hybrid'}
        gains=sum(h[i]['correct_display'] and not r[i]['correct_display'] for i in r);losses=sum(r[i]['correct_display'] and not h[i]['correct_display'] for i in r)
        pair={'round':n,'gains':gains,'losses':losses,'passes':gains>=2 and losses==0};paired.append(pair)
    return {'outcomes':outcomes,'panels':panels,'paired':paired,'gates':gates,'complete_evidence':complete,'candidate_passes':bool(complete and all(g['passes'] for g in gates) and all(p['passes'] for p in paired))}
