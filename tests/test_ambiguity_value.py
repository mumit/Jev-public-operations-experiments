import copy,json,unittest
from unittest.mock import patch
from triage_bench import ambiguity_value_data as data,ambiguity_value_trial as trial
from triage_bench.ambiguity_value_features import request,rules,jev
from triage_bench.optional_clarification_features import request as historical

P={'text':'For alpha, CPU has material scaled magnitude between before and after this incident.','inventory':{'alpha':['cpu','mem'],'beta':['cpu','mem']}}
class ValueTests(unittest.TestCase):
 def test_request_is_unchanged_and_ignores_reference_metadata(self):
  x={**P,'id':'secret','family':'answer_key','needed':['service']};self.assertEqual(request(x),historical(P,'checklist'));self.assertNotIn('secret',json.dumps(request(x)));self.assertNotIn('answer_key',json.dumps(request(x)))
 def test_rule_catalog_alias_and_subject(self):
  self.assertEqual(rules(P)['choice'],'no_question')
  self.assertEqual(rules({**P,'text':P['text'].replace('CPU','CPU or memory')})['choice'],'channel')
  self.assertEqual(rules({**P,'text':P['text'].replace('alpha','unnamed handler')})['choice'],'service')
  self.assertEqual(rules({**P,'text':P['text'].replace('CPU','packet loss')})['choice'],'channel')
 def test_rule_corrections_and_ambiguous_comparison(self):
  self.assertEqual(rules({**P,'text':P['text']+' Final correction: For beta, memory has positive signed scaled change between before and after this incident.'})['choice'],'no_question')
  self.assertEqual(rules({**P,'text':P['text'].replace('has material scaled magnitude','shifted unfavorably')})['choice'],'kind')
 def test_new_pack_pairing_and_manual_masks(self):
  ps,rs=data.reconstruct();self.assertEqual(len(ps),48);self.assertEqual(len(rs),48)
  self.assertEqual({p['dataset'] for p in ps},{'Train Ticket','Online Boutique'})
  self.assertEqual(len({p['pair'] for p in ps}),24)
  for pair in {p['pair'] for p in ps}:self.assertEqual({p['variant'] for p in ps if p['pair']==pair},{1,2})
  self.assertTrue(all(r['choice']==(r['needed'][0] if r['needed'] else 'no_question') for r in rs))
 def test_quarantine_unused_field_and_boundary(self):
  fields=('scope','service','channel','kind','polarity','window')
  answers={f'claim_{f}':{'choice':'metric_check' if f=='scope' else 'clarify' if f=='service' else 'clear','probabilities':{'metric_check':1} if f=='scope' else {'clarify':.7,'clear':.3} if f=='service' else {'clear':1}} for f in fields}
  row={'status':'ok','answers':answers,'quarantined_sentences':[]};self.assertTrue(jev(row)['displayed']);row['quarantined_sentences']=['claim'];self.assertFalse(jev(row)['valid'])
 def test_missing_jobs_remain_in_all_panels(self):
  ps,rs=data.reconstruct();r=trial.score_rows(ps,rs,[],False);self.assertEqual(len(r['outcomes']),288);self.assertFalse(r['candidate_passes']);self.assertEqual(sum(p['valid'] for p in r['panels'] if p['category']=='overall' and p['method']=='jev'),0)
 def test_rules_cannot_win_declared_model_gate_by_substitution(self):
  ps,rs=data.reconstruct()
  with patch.object(trial,'jev',side_effect=lambda row:{'valid':False,'displayed':False,'choice':None}):
   r=trial.score_rows(ps,rs,[]);self.assertFalse(r['candidate_passes']);self.assertTrue(any(p['correct_display'] for p in r['panels'] if p['method']=='rules'))
if __name__=='__main__':unittest.main()
