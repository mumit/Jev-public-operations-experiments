import unittest
from types import SimpleNamespace
from unittest.mock import patch
from triage_bench.entry_walkthrough_service import EntryWalkthrough
from triage_bench import entry_walkthrough as t
from triage_bench.study_page import render_study,return_path

class EntryServiceTests(unittest.TestCase):
    def test_normal_pack_hides_refs_and_preview_is_separate(self):
        pack=t.reconstruct();s=EntryWalkthrough()
        with patch.object(s,'verified',return_value={'protocol_sha256':'fixture'}),patch.object(t,'load',return_value=pack):
            for preview in (False,True):
                p=s.pack(preview);self.assertNotIn('references',p);self.assertNotIn('reference',p['tasks'][0]);self.assertEqual(p['mode'],'assistant_preview' if preview else 'participant');self.assertEqual(p['server_writes'],0)
                self.assertTrue(all('family' not in task for task in p['tasks']));self.assertEqual(len(s.references(preview)['references']),8)
    def test_unfrozen_participant_start_is_unavailable(self):
        s=EntryWalkthrough()
        with patch.object(s,'verified',side_effect=ValueError('Not frozen')):self.assertFalse(s.pack()['available'])
    def test_practice_and_original_inputs_not_mutated_by_redaction(self):
        pack=t.reconstruct();s=EntryWalkthrough()
        with patch.object(s,'verified',return_value={'protocol_sha256':'fixture'}),patch.object(t,'load',return_value=pack):
            s.pack();self.assertIn('references',pack);self.assertIn('family',pack['tasks'][0]);self.assertEqual(len(pack['practice']),2)
    def test_design_article_returns_to_walkthrough(self):
        path='/entry-walkthrough';self.assertEqual(return_path(path),path);html=render_study(SimpleNamespace(root=t.ROOT),{'doc':'optional-entry-evaluation'}).decode();self.assertIn('href="/entry-walkthrough"',html)
if __name__=='__main__':unittest.main()
