import unittest
from unittest.mock import patch
from triage_bench.public_trace_service import PublicTraceStudy
from triage_bench.study_page import return_path, DOCUMENTS


class TraceServiceTests(unittest.TestCase):
    def test_case_reference_is_hidden_until_reveal(self):
        reference = {'id': 'case', 'target': 'a', 'fault': 'f1'}
        outcome = {**reference, 'group': 'answer-group', 'correct_first': True,
                   'cause_included': True, 'wrong_leads': 0, 'raw_correct_first': True,
                   'choice': 'a', 'round': 1}
        assessment = {'datasets': {'Train Ticket': {'pairs': [reference],
                       'arms': {arm: {'selective': {'outcomes': [outcome]}} for arm in ('metrics', 'traces')}}}}
        service = PublicTraceStudy('.')
        packet = {'id': 'case', 'state': {}, 'trace_context': {}, 'requests': {}}
        with patch.object(service, 'verified', return_value=assessment), \
             patch('triage_bench.public_trace_service.load', side_effect=lambda p: [packet] if p.name == 'inputs.json' else {'case': {}}), \
             patch('pathlib.Path.read_text', return_value=''):
            hidden = service.case('Train Ticket', 'case')
            self.assertIsNone(hidden['reference'])
            for arm in ('metrics', 'traces'):
                for key in ('target', 'fault', 'group', 'raw_correct_first', 'correct_first'):
                    self.assertNotIn(key, hidden['outcomes'][arm][0])
            visible = service.case('Train Ticket', 'case', True)
            self.assertEqual(visible['reference'], {'target': 'a', 'fault': 'f1'})

    def test_reader_keeps_selected_trace_context(self):
        path = '/traces?dataset=Train+Ticket&case=TRC-case&arm=traces&round=2#evidence'
        self.assertEqual(return_path(path), path)
        self.assertEqual(DOCUMENTS['public-traces'], 'docs/public-traces.md')
