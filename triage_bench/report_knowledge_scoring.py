"""Require a corrected interpretation, preserved ordinary answers and no wrong displays."""
from .report_knowledge_features import ARMS
from .publisher_report_features import jev
from .publisher_report_scoring import assess
from .report_knowledge_data import CHOICES

COUNTS=('valid','correct_choice','correct_display','wrong_display','withheld')
TARGET='cf-power-2024-c5'
COMPANIONS=('cf-power-2024-c10','cf-power-2024-c11','cf-power-2024-c12')

def score(packets,references,rows,complete,baseline):
 index={(r['claim_id'],r['arm'],r['round']):r for r in rows};allowed={(p['id'],a,n) for p in packets for a in ARMS for n in (1,2,3)}
 if len(index)!=len(rows) or set(index)-allowed:raise ValueError('Invalid reply join.')
 refs={r['id']:r['choice'] for r in references};outcomes=[];panels=[];pairs=[];gates=[];sources=list(dict.fromkeys(p['source_id'] for p in packets))
 for n in (1,2,3):
  for p in packets:
   for a in ARMS:
    pred=jev(index.get((p['id'],a,n)));rule=baseline[p['id']][a]
    outcomes.append({'id':p['id'],'source_id':p['source_id'],'topic':p['topic'],'arm':a,'round':n,'reference':refs[p['id']],'prediction':pred,**assess(pred,refs[p['id']]),'literal_rule':rule,'rule_outcome':assess(rule,refs[p['id']])})
  current=[o for o in outcomes if o['round']==n]
  for a in ARMS:
   for s in ['all',*sources]:
    for c in ['all',*CHOICES]:
     items=[o for o in current if o['arm']==a and (s=='all' or o['source_id']==s) and (c=='all' or o['reference']==c)]
     panels.append({'arm':a,'round':n,'source_id':s,'reference_class':c,'claims':len(items),**{k:sum(o[k] for o in items) for k in COUNTS}})
  control={o['id']:o for o in current if o['arm']=='literal'};candidate={o['id']:o for o in current if o['arm']=='knowledge'}
  choice_gains=[i for i in candidate if candidate[i]['correct_choice'] and not control[i]['correct_choice']]
  choice_losses=[i for i in candidate if control[i]['correct_choice'] and not candidate[i]['correct_choice']]
  gains=[i for i in candidate if candidate[i]['correct_display'] and not control[i]['correct_display']]
  losses=[i for i in candidate if control[i]['correct_display'] and not candidate[i]['correct_display']]
  pairs.append({'round':n,'choice_gains':choice_gains,'choice_losses':choice_losses,'gains':gains,'losses':losses,'control_wrong_displays':sum(o['wrong_display'] for o in control.values())})
  for s in ['all',*sources]:
   items=[o for o in candidate.values() if s=='all' or o['source_id']==s];ids={o['id'] for o in items}
   criteria={'complete_valid_evidence':complete and all(o['valid'] for o in items),'no_wrong_displays':not any(o['wrong_display'] for o in items),'no_correct_choice_losses':not any(i in ids for i in choice_losses),'no_correct_display_losses':not any(i in ids for i in losses)}
   if s=='all':
    criteria.update(at_least_one_correct_choice_gain=bool(choice_gains),original_failure_correctly_chosen_and_displayed=candidate[TARGET]['correct_display'],all_companions_correctly_chosen_and_displayed=all(candidate[i]['correct_display'] for i in COMPANIONS))
   else:
    criteria.update(six_correct_displays_minimum=sum(o['correct_display'] for o in items)>=6,all_classes_correctly_displayed=all(any(o['correct_display'] and o['reference']==c for o in items) for c in CHOICES))
   gates.append({'source_id':s,'round':n,'criteria':criteria,'passes':all(criteria.values())})
 return {'outcomes':outcomes,'panels':panels,'paired':pairs,'gates':gates,'candidate':'knowledge','complete_evidence':complete,'candidate_passes':complete and all(g['passes'] for g in gates)}
