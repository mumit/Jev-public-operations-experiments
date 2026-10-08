import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench import selective_report_audit as a

class SelectiveAuditTests(unittest.TestCase):
    def test_inventory_retains_complete_sections_in_document_order(self):
        blocks=[{'text':'Intro'},{'text':'January 1 01:02 UTC (lasting 1 hour)'},{'text':'whole first block'},{'text':'January 2 03:04 UTC (lasting 20 minutes)'},{'text':'whole second block'}]
        sections=a.inventory(blocks)
        self.assertEqual([(s['start'],s['end']) for s in sections],[(1,3),(3,5)])

    def test_http_failure_is_preserved_without_retry_or_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);plan=root/'plan.json';plan.write_text(json.dumps({'sources':[{'id':'first','url':'https://github.blog/report','month':'January','year':2024}]}))
            with patch.object(a,'PLAN',plan),patch.object(a,'AUDIT',root/'audit.json'),patch.object(a,'CACHE',root/'cache'),patch.object(a,'committed'),patch('urllib.request.urlopen',side_effect=HTTPError('https://github.blog/report',404,'missing',{},None)) as fetch:
                result=a.audit();self.assertEqual(fetch.call_count,1)
                self.assertFalse(result['preparation_eligible']);self.assertEqual(result['sources'][0]['reason'],'source_http_404')
                self.assertEqual(result['new_provider_calls'],0)
                with self.assertRaises(ValueError):a.audit()

    def test_preparation_minimum_is_not_silently_reduced(self):
        blocks=[{'text':'Intro'},{'text':'March 1 01:02 UTC (lasting 1 hour)'},{'text':'Details'}]
        self.assertLess(len(a.inventory(blocks)),3)
