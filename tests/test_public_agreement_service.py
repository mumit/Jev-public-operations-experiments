import unittest
from unittest.mock import patch
from triage_bench.public_agreement_service import PublicAgreementStudy
from triage_bench.study_page import return_path
from triage_bench.public_agreement_policy import assess

class InspectorTests(unittest.TestCase):
    def test_answers_stay_hidden_and_outputs_remain_visible(self):
        row={'case_id':'x','round':1,'status':'ok','choice':'a','probabilities':{'a':.8,'b':.2,'insufficient_evidence':0.}}
        controls={'x':{'ml':{'choice':'b'}}};refs=[{'id':'x','group':'g/b/cpu','fault':'cpu','target':'b'}]
        panel={'routing':assess([row],refs,controls,rounds=1)};study=PublicAgreementStudy('.')
        with patch.object(study,'verified',return_value={'datasets':{'Train Ticket':panel},'policy':{}}),patch('triage_bench.public_agreement_service.load',side_effect=[[{'id':'x','request':{'state':'{}'}}],controls]),patch('pathlib.Path.read_text',return_value='{"case_id":"x"}\n'):
            hidden=study.case('Train Ticket','x');self.assertIsNone(hidden['reference']);self.assertEqual(hidden['outcomes'][0]['ml_choice'],'b')
            self.assertFalse(set(hidden['outcomes'][0])&{'target','group','fault','base_correct','retained_correct','base_wrong','retained_wrong','raw_correct','ml_correct'})
        with patch.object(study,'verified',return_value={'datasets':{'Train Ticket':panel},'policy':{}}),patch('triage_bench.public_agreement_service.load',side_effect=[[{'id':'x','request':{'state':'{}'}}],controls]),patch('pathlib.Path.read_text',return_value='{"case_id":"x"}\n'):
            revealed=study.case('Train Ticket','x',True);self.assertEqual(revealed['reference']['target'],'b');self.assertTrue(revealed['outcomes'][0]['base_wrong'])
    def test_reader_return_preserves_case(self):
        p='/agreement?dataset=Train+Ticket&case=AGR-test&round=2#inspect'
        self.assertEqual(return_path(p),p);self.assertEqual(return_path('https://outside.test/agreement'),'/public-format')
