import unittest
from unittest.mock import patch
from triage_bench.public_confirmation_trial import eligibility,POLICY,score
from triage_bench.public_confirmation_data import prepare

class ConfirmationTests(unittest.TestCase):
    def test_reserve_download_is_blocked_before_network_when_gate_fails(self):
        with patch('triage_bench.public_confirmation_data.check_plan',return_value={}),patch('triage_bench.public_confirmation_data.folder') as folder,patch('triage_bench.public_confirmation_trial.eligibility',side_effect=ValueError('sealed')),patch('triage_bench.public_confirmation_data.fetch') as fetch:
            folder.return_value.exists.return_value=False
            with self.assertRaisesRegex(ValueError,'sealed'):prepare('confirmation')
            fetch.assert_not_called()

    def test_confirmation_requires_matching_error_free_fixed_policy(self):
        a={'failed_or_missing':0,'selective':{'policy':POLICY,'per_round':[{'wrong_leads':0,'shown':1}]*3}}
        b={'selected':{'policy':POLICY}}
        with patch('triage_bench.public_confirmation_trial.verify_boundary',return_value=b),patch('triage_bench.public_confirmation_trial.committed'),patch('triage_bench.public_confirmation_trial.selective_score',return_value=a),patch('triage_bench.public_confirmation_trial.load',return_value=a):
            self.assertEqual(eligibility(),a)
            a['selective']['per_round'][0]={'wrong_leads':1,'shown':1}
            with self.assertRaisesRegex(ValueError,'gate failed'):eligibility()

    def test_scoring_keeps_applications_separate_and_never_selects_a_boundary(self):
        refs=[{'id':'t','group':'a/cpu','fault':'cpu','target':'a'},{'id':'s','group':'b/cpu','fault':'cpu','target':'b'}]
        rows=[{'id':i,'case_id':i,'round':n,'status':'ok','choice':'a','probabilities':{'a':.8,'b':.2,'insufficient_evidence':0}} for i in ('t','s') for n in (1,2,3)]
        controls={i:{arm:{'choice':r['target'],'ranking':[{'service':r['target']}]} for arm in ('ml','change','resource')} for i,r in zip(('t','s'),refs)}
        def fixture(path):return refs if str(path).endswith('references.json') else controls
        with patch('triage_bench.public_confirmation_trial.verified_rows',return_value=(rows,{'failed':0,'unattempted':0})),patch('triage_bench.public_confirmation_trial.load',side_effect=fixture),patch('triage_bench.public_confirmation_trial.check_plan',return_value={'assignments':[{'id':'t','dataset':'Train Ticket'},{'id':'s','dataset':'Sock Shop'}]}),patch('triage_bench.public_confirmation_trial.sha',return_value='fixture'),patch('pathlib.Path.read_bytes',return_value=b'fixture'):
            r=score()
            self.assertEqual(r['policy'],POLICY)
            self.assertEqual(r['datasets']['Train Ticket']['selective']['per_round'][0]['wrong_leads'],0)
            self.assertEqual(r['datasets']['Sock Shop']['selective']['per_round'][0]['wrong_leads'],1)
            self.assertEqual(r['datasets']['Sock Shop']['curves'],[])
