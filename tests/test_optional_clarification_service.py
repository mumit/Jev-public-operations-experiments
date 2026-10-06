import unittest,json
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from triage_bench.optional_clarification_service import OptionalClarificationStudy
from triage_bench.study_page import return_path,render_study
from triage_bench.paths import ROOT
from triage_bench import optional_clarification_trial as original,optional_question_trial as policy

class OptionalInspectorTests(unittest.TestCase):
    def test_both_stages_hide_reference_and_missing_replies_without_entry(self):
        p={'id':'fixture','text':'Check CPU.','dataset':'Train Ticket','family':'fixture','variant':1,'inventory':{'example-service':['cpu']}}
        refs=[{'id':'fixture','needed':['service'],'choice':'service'}]
        def load(path):return [p] if path.name=='inputs.json' else refs if path.name=='references.json' else []
        service=OptionalClarificationStudy(ROOT)
        for phase,t in (('format',original),('policy',policy)):
            with patch.object(service,'verified',return_value={'outcomes':[{'id':'fixture'}]}),patch.object(t,'load',side_effect=load),patch.object(Path,'read_text',return_value=''):
                c=service.card('fixture',phase=phase);self.assertIsNone(c['reference']);self.assertIsNone(c['outcomes']);self.assertEqual(c['provider_calls'],0);self.assertEqual(c['server_writes'],0);self.assertFalse(c['entry_autofill']);self.assertFalse(c['human_review_recorded']);self.assertNotIn('entry',c)
                self.assertTrue(all(d['action']=='review' for arm in c['decisions'].values() for d in arm.values()));self.assertEqual(service.card('fixture',True,phase)['reference'],refs[0])
    def test_unknown_stage_and_statement_rejected(self):
        s=OptionalClarificationStudy(ROOT)
        with self.assertRaises(ValueError):s.trial('unknown')
        with patch.object(s,'verified',return_value={'outcomes':[]}),patch.object(policy,'load',return_value=[]):
            with self.assertRaises(ValueError):s.card('unknown')
    def test_both_results_replay_and_raw_byte_drift_is_rejected(self):
        for t in (original,policy):self.assertFalse(t.verify()['candidate_passes'])
        real=Path.read_bytes
        def drift(path):return real(path)+b' ' if path==policy.output()/'responses.jsonl' else real(path)
        with patch.object(Path,'read_bytes',drift):
            with self.assertRaises(ValueError):policy.verify()
    def test_report_returns_to_policy_and_local_entry_fragment(self):
        path='/optional-clarification?phase=policy&arm=first_question&card=fixture&round=3#entry'
        self.assertEqual(return_path(path),path);html=render_study(SimpleNamespace(root=ROOT),{'doc':'optional-clarification','return':path}).decode();self.assertIn('phase=policy&amp;arm=first_question&amp;card=fixture&amp;round=3#entry',html)
if __name__=='__main__':unittest.main()
