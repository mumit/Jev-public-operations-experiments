import unittest
from unittest.mock import patch
from triage_bench import explicit_preparation_audit as a

class PreparationAuditTests(unittest.TestCase):
    def test_all_failed_recordings_preserved_with_zero_inference(self):
        r=a.verify();self.assertEqual(r['downloaded_recordings'],45);self.assertEqual(r['hosted_calls'],0);self.assertEqual(r['inputs_prepared'],0);self.assertEqual(r['references_prepared'],0);self.assertEqual(r['outside_window'][0]['after_rows'],0)
    def test_publisher_checksums_and_declared_window_outside_recording(self):
        r=a.load(a.AUDIT);self.assertEqual(len(r['files']),30)
        v=r['outside_declared_window'][0];self.assertGreater(v['declared_incident_time'],v['time_end']);self.assertEqual(v['before_rows'],63)
        self.assertIn('after the exception',r['publisher_verification'])
    def test_attempted_failed_pack_promotion_is_rejected(self):
        original=a.failed.DATA
        from pathlib import Path
        exists=Path.exists
        def mocked(path):return True if path==original/'inputs.json' else exists(path)
        with patch('pathlib.Path.exists',mocked):
            with self.assertRaises(ValueError):a.verify()

if __name__=='__main__':unittest.main()
