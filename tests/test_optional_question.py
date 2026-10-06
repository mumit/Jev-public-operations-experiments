import copy,unittest
from pathlib import Path
from unittest.mock import patch
from triage_bench import optional_question_policy as f,optional_question_trial as t,optional_clarification_data as d
from triage_bench.clarification_features import FIELDS
from triage_bench.optional_clarification_features import request,assessment

class PolicyTests(unittest.TestCase):
    def row(self,labels=None,scores=None):
        labels=labels or {'scope':'metric_check',**{k:'clear' for k in FIELDS if k!='scope'}};scores=scores or {}
        return {'status':'ok','quarantined_sentences':[],'answers':{'claim_'+k:{'choice':v,'probabilities':{v:scores.get(k,.95)}} for k,v in labels.items()}}
    def test_later_low_scores_do_not_gate_first_question_and_are_preserved(self):
        row=self.row();row['answers']['claim_service']['choice']='clarify';row['answers']['claim_service']['probabilities']={'clarify':.9};row['answers']['claim_window']['probabilities']={'clear':.4};before=copy.deepcopy(row)
        control=f.decision(row,'all_fields');candidate=f.decision(row,'first_question')
        self.assertFalse(control['displayed']);self.assertTrue(candidate['displayed']);self.assertEqual(candidate['choice'],'service');self.assertEqual(candidate['required_score_fields'],['scope','service']);self.assertEqual(row,before)
    def test_all_prior_fields_are_required_and_boundary_is_unchanged(self):
        row=self.row(scores={'service':.69});row['answers']['claim_channel']={'choice':'clarify','probabilities':{'clarify':.99}}
        self.assertFalse(f.decision(row,'first_question')['displayed']);row['answers']['claim_service']['probabilities']['clear']=.7
        r=f.decision(row,'first_question');self.assertTrue(r['displayed']);self.assertEqual(r['required_score_fields'],['scope','service','channel']);self.assertEqual(r['minimum_score'],.7)
    def test_no_question_still_requires_all_six_and_does_not_clear_entry(self):
        r=f.decision(self.row(scores={'window':.69}),'first_question');self.assertFalse(r['displayed']);self.assertEqual(set(r['required_score_fields']),set(FIELDS));r=f.decision(self.row(),'first_question');self.assertEqual(r['action'],'no_suggestion');self.assertNotIn('entry',r);self.assertNotEqual(r['action'],'ready')
    def test_outside_scope_retains_unneeded_labels_but_never_repairs_them(self):
        row=self.row();row['answers']['claim_scope']={'choice':'outside_scope','probabilities':{'outside_scope':.9}};row['answers']['claim_window']['probabilities']={'clear':.2}
        r=f.decision(row,'first_question');self.assertTrue(r['displayed']);self.assertEqual(r['choice'],'outside_scope');self.assertEqual(r['required_score_fields'],['scope']);self.assertEqual(r['labels']['window'],'clear')
    def test_unused_malformed_field_quarantines_and_inconsistent_prefix_withholds(self):
        row=self.row();row['answers']['claim_service']={'choice':'clarify','probabilities':{'clarify':.9}};row['quarantined_sentences']=['claim_window'];self.assertFalse(f.decision(row,'first_question')['valid'])
        row=self.row();del row['answers']['claim_window'];self.assertFalse(f.decision(row,'first_question')['displayed'])
        row=self.row();row['answers']['claim_service']={'choice':'not_applicable','probabilities':{'not_applicable':.9}};self.assertFalse(f.decision(row,'first_question')['displayed'])
    def test_shared_requests_and_costs_are_not_duplicated_by_policy(self):
        packets=d.reconstruct()[0]
        with patch.object(t,'check_plan',return_value={'maximum_calls':276,'maximum_answers':1656}),patch.object(d,'validate'),patch.object(t,'load',return_value=packets):jobs=t.requests()
        self.assertEqual(len(jobs),276);self.assertEqual(len({j['id'] for j in jobs}),276);self.assertEqual(jobs[0]['body'],request(packets[0],'checklist'));self.assertEqual({j['arm'] for j in jobs},{'shared'})
    def test_missing_replies_retain_both_policy_denominators(self):
        packets,refs=d.reconstruct()
        with patch.object(t,'verified_rows',return_value=([],{'attempted_calls':0,'status':'incomplete_or_failed'})),patch.object(t,'load',side_effect=[packets,refs]),patch.object(t,'sha',return_value='fixture'),patch.object(Path,'read_bytes',return_value=b''):
            result=t.score()
        self.assertEqual(len(result['outcomes']),552);self.assertEqual(result['costs']['shared']['actual_calls'],0);self.assertFalse(result['candidate_passes'])
        ps=[p for p in result['panels'] if p['method']=='first_question' and p['scope']=='overall'];self.assertEqual(sum(p['missed_clarification'] for p in ps),168)
    def test_silent_misses_survive_prefix_policy(self):
        r=assessment(f.decision(self.row(),'first_question'),{'choice':'service','needed':['service']});self.assertTrue(r['silent_miss']);self.assertTrue(r['missed_clarification'])
if __name__=='__main__':unittest.main()
