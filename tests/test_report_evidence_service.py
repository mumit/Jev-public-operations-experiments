import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from triage_bench.app import App,handler_for
from triage_bench.paths import ROOT
from triage_bench.report_evidence_service import ReportEvidenceStudy
from triage_bench.study_page import render_study

class ReportEvidenceTests(unittest.TestCase):
    def test_no_calls_no_full_text_and_failed_sources_visible(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No network')):
            result=ReportEvidenceStudy().overview()
        self.assertEqual(result['new_provider_calls'],0)
        self.assertEqual(len(result['sources']),12)
        self.assertEqual(sum(s['primary'] for s in result['sources']),8)
        failures=[s for s in result['sources'] if s['status']=='unavailable']
        self.assertEqual(len(failures),2)
        self.assertTrue(all(s['raw_sha256'] and s['failure_reason'] for s in failures))
        self.assertTrue(all(s['display_title']==s['title_observed'] for s in failures))
        self.assertNotIn('blocks',result['sources'][5])
        self.assertNotIn('text',result['sources'][0]['input_prefix'])
        for allocation in ('development','evaluation'):
            self.assertEqual(sum(s['primary'] and s['allocation']==allocation for s in result['sources']),4)

    def test_article_links_return_to_selected_source(self):
        value='/report-evidence?allocation=evaluation&source=cf-kv-2023'
        rendered=render_study(ReportEvidenceStudy(),{'doc':'report-evidence','return':value}).decode()
        self.assertIn('Reading publisher-written incident reports',rendered)
        self.assertIn('/report-evidence?allocation=evaluation&amp;source=cf-kv-2023',rendered)

    def test_routes_read_only_and_origin_protected(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(App()))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://127.0.0.1:'+str(server.server_port)
        try:
            with urlopen(base+'/api/report-evidence') as response:
                self.assertEqual(json.load(response)['new_provider_calls'],0)
            with urlopen(base+'/report-evidence') as response:
                self.assertIn(b'What does the report actually establish?',response.read())
            for request,code in [(Request(base+'/api/report-evidence',headers={'Origin':'https://example.org'}),403),(Request(base+'/api/report-evidence',data=b'{}'),405)]:
                with self.assertRaises(HTTPError) as error:urlopen(request)
                self.assertEqual(error.exception.code,code)
                error.exception.close()
        finally:server.shutdown();server.server_close();thread.join()
