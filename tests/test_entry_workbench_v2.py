import copy,unittest
from unittest.mock import patch
from triage_bench.entry_workbench_v2_service import EntryWorkbenchV2
from triage_bench import entry_walkthrough as old

class WorkbenchTests(unittest.TestCase):
 def test_reuses_verified_known_examples_without_reference_leak(self):
  s=EntryWorkbenchV2();p=old.reconstruct()
  with patch.object(s.original,'pack',return_value={'available':True,**copy.deepcopy(p),'protocol_sha256':'frozen'}):
   r=s.examples();self.assertEqual(r['mode'],'software_demo');self.assertEqual(len(r['examples']),10);self.assertEqual(r['scored_participants'],0);self.assertNotIn('reference',r['examples'][0]);self.assertEqual(r['source_protocol_sha256'],'frozen')
 def test_original_failure_blocks_new_examples(self):
  s=EntryWorkbenchV2()
  with patch.object(s.original,'pack',return_value={'available':False,'error':'Changed'}):self.assertFalse(s.examples()['available'])
if __name__=='__main__':unittest.main()
