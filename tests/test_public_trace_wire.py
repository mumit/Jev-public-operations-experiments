import unittest
from triage_bench.public_trace_features import summarize_rows
from triage_bench.public_trace_wire import compact, expand


class TraceWireTests(unittest.TestCase):
    def test_round_trip_preserves_nulls_codes_dependencies_and_gaps(self):
        context = summarize_rows([
            {'traceID': 't', 'spanID': 's', 'parentSpanID': None,
             'serviceName': 'a', 'startTime': 1000000, 'startTimeMillis': 1000,
             'duration': 500, 'statusCode': None}], 2, 1, 2, ['a', 'absent'])
        wire = compact(context)
        self.assertEqual(expand(wire), context)
        self.assertEqual(wire['candidates_without_spans'], ['absent'])
        self.assertIn('service_columns', wire)
        self.assertNotIn('service_columns', context)

    def test_v2_evaluation_guard_still_precedes_download(self):
        from unittest.mock import patch
        from triage_bench import public_trace_data_v2 as data, public_trace_trial_v2 as trial
        with patch.object(data, 'check_plan', return_value={}), \
             patch.object(trial, 'check_candidate', side_effect=ValueError('sealed')), \
             patch.object(data, 'folder') as destination, patch.object(data, 'fetch') as download:
            with self.assertRaisesRegex(ValueError, 'sealed'):
                data.prepare('evaluation')
            destination.assert_not_called()
            download.assert_not_called()
