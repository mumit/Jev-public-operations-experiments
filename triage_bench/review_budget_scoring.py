"""Prospective 90% correct-display floor, 10% review ceiling and no wrong displays."""
from .report_knowledge_features import ARMS
from .publisher_report_features import jev
from .publisher_report_scoring import assess
from .review_budget_data import CHOICES

COUNTS=('valid','correct_choice','correct_display','wrong_display','withheld')
SCOPES=('incident_fact','report_knowledge')

def score(packets,references,rows,complete,baseline):
 index={(r['claim_id'],r['arm'],r['round']):r for r in rows};allowed={(p['id'],a,n) for p in packets for a in ARMS for n in (1,2,3)}
 if len(index)!=len(rows) or set(index)-allowed:raise ValueError('Invalid reply join.')
 refs={r['id']:r['choice'] for r in references};outcomes=[];panels=[];pairs=[];gates=[];sources=list(dict.fromkeys(p['source_id'] for p in packets))
 for n in (1,2,3):
  for p in packets:
   for a in ARMS:
    pred=jev(index.get((p['id'],a,n)));rule=baseline[p['id']][a]
    outcomes.append({'id':p['id'],'source_id':p['source_id'],'topic':p['topic'],'assertion_scope':p['assertion_scope'],'arm':a,'round':n,'reference':refs[p['id']],'prediction':pred,**assess(pred,refs[p['id']]),'literal_rule':rule,'rule_outcome':assess(rule,refs[p['id']])})
  current=[o for o in outcomes if o['round']==n]
  for a in ARMS:
   for s in ['all',*sources]:
    for c in ['all',*CHOICES]:
     for scope in ['all',*SCOPES]:
      items=[o for o in current if o['arm']==a and (s=='all' or o['source_id']==s) and (c=='all' or o['reference']==c) and (scope=='all' or o['assertion_scope']==scope)]
      panels.append({'arm':a,'round':n,'source_id':s,'reference_class':c,'assertion_scope':scope,'claims':len(items),**{k:sum(o[k] for o in items) for k in COUNTS}})
  control={o['id']:o for o in current if o['arm']=='literal'};candidate={o['id']:o for o in current if o['arm']=='knowledge'}
  pairs.append({'round':n,'choice_gains':[i for i in candidate if candidate[i]['correct_choice'] and not control[i]['correct_choice']],'choice_losses':[i for i in candidate if control[i]['correct_choice'] and not candidate[i]['correct_choice']],'gains':[i for i in candidate if candidate[i]['correct_display'] and not control[i]['correct_display']],'losses':[i for i in candidate if control[i]['correct_display'] and not candidate[i]['correct_display']],'control_wrong_displays':sum(o['wrong_display'] for o in control.values())})
  for s in ['all',*sources]:
   items=[o for o in candidate.values() if s=='all' or o['source_id']==s]
   criteria={'complete_valid_evidence':complete and all(o['valid'] for o in current if s=='all' or o['source_id']==s),'no_wrong_displays':not any(o['wrong_display'] for o in items)}
   if s=='all':criteria.update(ninety_percent_correct_display_floor=10*sum(o['correct_display'] for o in items)>=9*len(items),ten_percent_review_ceiling=10*sum(o['withheld'] for o in items)<=len(items))
   else:criteria['all_classes_correctly_displayed']=all(any(o['correct_display'] and o['reference']==c for o in items) for c in CHOICES)
   gates.append({'source_id':s,'round':n,'criteria':criteria,'passes':all(criteria.values())})
 return {'outcomes':outcomes,'panels':panels,'paired':pairs,'gates':gates,'candidate':'knowledge','complete_evidence':complete,'candidate_passes':complete and all(g['passes'] for g in gates)}
