import unittest,json,tempfile
from pathlib import Path
from unittest.mock import patch,MagicMock
from triage_bench.public_selective_policy import decision,evaluate,select,candidates
from triage_bench.public_selective_data import prepare

class SelectiveTests(unittest.TestCase):
    def row(self,choice='a',probabilities=None,number=1):
        return {'case_id':'x','round':number,'status':'ok','choice':choice,'probabilities':probabilities or {'a':.6,'b':.3,'insufficient_evidence':.1}}

    def test_insufficient_evidence_competes_for_margin(self):
        row=self.row(probabilities={'a':.5,'b':.05,'insufficient_evidence':.45})
        self.assertEqual(decision(row,{'threshold':.5,'margin':.1,'maximum_leads':1})['leads'],[])
        self.assertEqual(decision(row,{'threshold':.5,'margin':0.,'maximum_leads':1})['leads'],['a'])
        self.assertEqual(decision(None,candidates()[0])['reason'],'failed_or_missing')
        self.assertEqual(decision(self.row('insufficient_evidence'),candidates()[0])['leads'],[])

    def test_alternative_rule_does_not_alter_first_choice(self):
        p={'threshold':.5,'margin':0.,'maximum_leads':2}
        self.assertEqual(decision(self.row(),p)['leads'],['a','b'])
        self.assertEqual(decision(self.row(probabilities={'a':.7,'b':.2,'insufficient_evidence':.1}),p)['leads'],['a'])
        self.assertEqual(decision(self.row(probabilities={'a':.5,'b':.5,'insufficient_evidence':0}),{**p,'margin':.1})['leads'],[])

    def test_calibration_uses_every_round_and_rejects_all_withheld(self):
        refs=[{'id':'x','group':'g','target':'a','fault':'loss'}]
        rows=[self.row(),self.row(number=2),self.row('b',{'a':.1,'b':.8,'insufficient_evidence':.1},3)]
        curve=evaluate(rows,refs,{'threshold':.5,'margin':0.,'maximum_leads':1})
        self.assertIsNone(select([curve]))
        empty=evaluate(rows,refs,{'threshold':1.,'margin':0.,'maximum_leads':1})
        self.assertIsNone(select([empty]))
        self.assertEqual(curve['per_round'][2]['wrong_leads'],1)

    def test_failure_denominators_and_correct_withheld_are_separate(self):
        refs=[{'id':'x','group':'g','target':'a','fault':'loss'}]
        r=evaluate([self.row()],refs,{'threshold':.7,'margin':0.,'maximum_leads':1})
        self.assertEqual([v['cases'] for v in r['per_round']],[1,1,1])
        self.assertEqual(r['per_round'][0]['correct_first_withheld'],1)
        self.assertEqual(r['per_round'][1]['failed_or_missing'],1)

    def test_evaluation_download_requires_boundary_before_network(self):
        with patch('triage_bench.public_selective_data.check_plan',return_value={}),patch('triage_bench.public_selective_data.folder') as folder,patch('triage_bench.public_selective_trial.verify_boundary',side_effect=ValueError('sealed')),patch('triage_bench.public_selective_data.fetch') as fetch:
            folder.return_value.exists.return_value=False
            with self.assertRaisesRegex(ValueError,'sealed'):prepare('evaluation')
            fetch.assert_not_called()

    def test_run_is_once_only_and_version_failure_redacts_saved_response(self):
        from triage_bench.public_selective_trial import run
        profile={'model':'jev-1.13.0','endpoint':'https://example.invalid','context_tokens':32768,'api_key':'fixture-key'}
        planned=[{'id':str(n),'case_id':'x','arm':'named','round':1,'request_sha256':'fixture','body':{'questions':{'cause':{'criteria':{'a':'a'}}}}} for n in range(2)]
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);protocol=root/'protocol.json';protocol.write_text('{}')
            response=MagicMock();response.__enter__.return_value=response;response.read.return_value=json.dumps({'model':'changed','echo':'fixture-key'}).encode()
            opener=MagicMock();opener.open.return_value=response
            with patch('triage_bench.public_selective_trial.check_stage',return_value=(profile,{},planned)),patch('triage_bench.public_selective_trial.controls',return_value={}),patch('triage_bench.public_selective_trial.output',return_value=root/'run'),patch('triage_bench.public_selective_trial.protocol_path',return_value=protocol),patch('urllib.request.build_opener',return_value=opener):
                result=run('calibration',profile)
                self.assertEqual(result['attempted'],1);self.assertEqual(result['unattempted'],1);self.assertEqual(result['stopped_reason'],'checkpoint_mismatch')
                self.assertNotIn('fixture-key',(root/'run/responses.jsonl').read_text())
                with self.assertRaises(FileExistsError):run('calibration',profile)
                self.assertEqual(opener.open.call_count,1)
