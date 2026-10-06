import unittest
from unittest.mock import patch
from triage_bench import explicit_confirmation_data as d,explicit_confirmation_trial as t,explicit_claim_data as original

class ExplicitConfirmationTests(unittest.TestCase):
    def test_fresh_whole_groups_do_not_consume_failed_original_allocation(self):
        rows=d.allocation();old=original.allocation()
        self.assertEqual(len(rows),15);self.assertEqual(len({r['group'] for r in rows}),3)
        self.assertFalse({r['source_case'] for r in rows}&{r['source_case'] for r in old})
        self.assertTrue(all(sum(r['group']==g for r in rows)==5 for g in {r['group'] for r in rows}))
    def test_confirmation_plan_stops_if_candidate_did_not_pass(self):
        profile={'model':t.MODEL,'endpoint':'https://api.typesafe.ai/v1/systemone','context_tokens':32768}
        with patch.object(t.prior,'verify',return_value={'candidate_passes':False}):
            with self.assertRaises(ValueError):t.plan(profile)
    def test_frozen_requests_use_candidate_functions_without_answers(self):
        p=original.boundaries()[0];p={k:v for k,v in p.items() if k!='fixture_answer'}
        with patch.object(t,'check_plan',return_value={'maximum_calls':6}),patch.object(d,'validate'),patch.object(t,'load',return_value=[p]):jobs=t.requests()
        self.assertEqual(len(jobs),6)
        for j in jobs:
            self.assertEqual(j['body'],t.request(p['observation'],p['claim'],j['arm']))
            self.assertNotIn('reference',j['body']['state']);self.assertNotIn('truth',j['body']['state'])
    def test_score_keeps_missing_calls_and_wrong_display_denominators(self):
        p=original.boundaries()[0];p={k:v for k,v in p.items() if k!='fixture_answer'}
        row={'card_id':p['id'],'round':1,'arm':'calculated','answers':{'claim_verdict':{'choice':'contradicted','probabilities':{'contradicted':.9,'supported':.1,'unanswerable':0}}},'usage':{'input_tokens':1},'latency_ms':1}
        def fake(path):return [p] if path.name=='inputs.json' else [{'id':p['id'],'answer':'supported'}]
        with patch.object(t,'verified_rows',return_value=([row],{'attempted_calls':1,'status':'incomplete_or_failed'})),patch.object(t,'load',side_effect=fake),patch.object(t,'sha',return_value='fixture'),patch('pathlib.Path.read_bytes',return_value=b'fixture'):
            r=t.score()
        self.assertFalse(r['candidate_passes']);panels=[p for p in r['panels'] if p['arm']=='calculated'];self.assertEqual(sum(p['claims'] for p in panels),3);self.assertEqual(sum(p['wrong_display'] for p in panels),1);self.assertEqual(r['actual_calls'],1)

if __name__=='__main__':unittest.main()
