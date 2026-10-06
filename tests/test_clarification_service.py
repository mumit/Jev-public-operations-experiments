import unittest,json
from types import SimpleNamespace
from unittest.mock import patch
from triage_bench.clarification_service import ClarificationStudy
from triage_bench.clarification_features import FIELDS,compose
from triage_bench.study_page import return_path,render_study
from triage_bench.paths import ROOT
from triage_bench import clarification_trial as original,clarification_focus_trial as focused

class InspectorTests(unittest.TestCase):
    def test_new_stages_hide_reference_and_keep_absent_rounds_reviewed(self):
        p={'id':'fixture','text':'Check CPU.','dataset':'Train Ticket','family':'fixture','variant':1,'inventory':{'example-service':['cpu']}}
        refs=[{'id':'fixture','labels':{},'decision':compose({})}]
        def load(path):
            return [p] if path.name=='inputs.json' else refs if path.name=='references.json' else []
        s=ClarificationStudy(ROOT)
        for phase,t in (('original',original),('focused',focused)):
            with patch.object(s,'verified',return_value={'outcomes':[{'id':'fixture'}]}),patch.object(t,'load',side_effect=load),patch('pathlib.Path.read_text',return_value=''):
                card=s.card('fixture',phase=phase);self.assertIsNone(card['reference']);self.assertIsNone(card['outcomes'])
                self.assertEqual(card['provider_calls'],0);self.assertEqual(card['server_writes'],0);self.assertFalse(card['human_review_recorded'])
                self.assertTrue(all(d['action']=='review' for v in card['decisions'].values() for d in v.values()))
                shown=s.card('fixture',True,phase);self.assertEqual(shown['reference'],refs[0]);self.assertEqual(len(shown['outcomes']),1)
    def test_unknown_phase_and_statement_are_rejected(self):
        s=ClarificationStudy(ROOT)
        with self.assertRaises(ValueError):s.trial('other')
        with patch.object(s,'verified',return_value={'outcomes':[]}),patch.object(focused,'load',return_value=[]):
            with self.assertRaises(ValueError):s.card('unknown')
    def test_reader_preserves_stage_arm_and_selection(self):
        path='/clarification?phase=focused&method=control&card=fixture&round=3#wire'
        self.assertEqual(return_path(path),path)
        html=render_study(SimpleNamespace(root=ROOT),{'doc':'clarification','return':path}).decode()
        self.assertIn('/clarification?phase=focused&amp;method=control&amp;card=fixture&amp;round=3#wire',html)
        self.assertNotIn('http://evil.example',render_study(SimpleNamespace(root=ROOT),{'doc':'clarification','return':'http://evil.example'}).decode())

if __name__=='__main__':unittest.main()
