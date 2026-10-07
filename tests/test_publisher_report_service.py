import json
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from triage_bench.app import App,handler_for
from triage_bench.publisher_report_service import PublisherReportStudy
from triage_bench.publisher_scope_preview import preview
from triage_bench.study_page import return_path,render_study
from scripts.verify_publisher_reports import verify
from triage_bench import publisher_report_data as data

class PublisherServiceTests(unittest.TestCase):
    def test_public_replay_with_no_source_cache_or_inference(self):
        with patch('triage_bench.publisher_report_trial.run',side_effect=AssertionError('No inference')):
            r=verify()
        self.assertEqual((r['actual_calls'],r['evaluation_correct_displays'],r['evaluation_wrong_displays']),(144,63,6))
        self.assertFalse(r['source_snapshot_replay'])

    def test_reference_reveal_keeps_original_reply_and_input_hidden(self):
        study=PublisherReportStudy();hidden=study.claim('evaluation','gh-april-2023-c1')
        self.assertIsNone(hidden['reference']);self.assertIsNone(hidden['request'])
        self.assertNotIn('correct_display',hidden['outcomes']['jev'])
        revealed=study.claim('evaluation','gh-april-2023-c1',reveal=True)
        self.assertEqual(revealed['reference']['choice'],'supported')
        self.assertTrue(revealed['outcomes']['jev']['wrong_display'])
        self.assertIsNone(study.claim('evaluation','gh-april-2023-c1')['reference'])
        self.assertEqual(hidden['row'],revealed['row'])

    def test_local_input_is_explicit_and_matches_recorded_claim(self):
        study=PublisherReportStudy()
        r=study.claim('evaluation','gh-april-2023-c1',include_input=True)
        if r['exact_input_available']:
            state=json.loads(r['request']['state'])
            self.assertEqual(state['claim'],r['claim']['claim'])
            self.assertEqual(set(state),{'claim','report_excerpt'})

    def test_scoped_preview_requires_explicit_selection_and_has_no_result(self):
        if not data.audit.CACHE.exists():return
        choices=preview('gh-april-2023')
        self.assertEqual(len(choices['sections']),7)
        self.assertNotIn('report_excerpt',choices)
        self.assertFalse(choices['scored']);self.assertEqual(choices['provider_calls'],0)
        section=next(s for s in choices['sections'] if s['label'].startswith('March 31'))
        scoped=preview('gh-april-2023',section['id'])
        self.assertIn('On March 31',scoped['report_excerpt'])
        self.assertNotIn('On March 29',scoped['report_excerpt'])
        self.assertLess(scoped['scoped_bytes'],scoped['full_bytes'])
        self.assertEqual(scoped['retained_blocks'],[0,10,11,12,13])

    def test_article_returns_to_selected_claim(self):
        value='/report-comparison?phase=evaluation&source=gh-april-2023&claim=gh-april-2023-c5&round=2'
        self.assertEqual(return_path(value),value)
        html=render_study(PublisherReportStudy(),{'doc':'publisher-results','return':value}).decode()
        self.assertIn('Jev reads single-incident reports well',html)
        self.assertIn('claim=gh-april-2023-c5&amp;round=2',html)

    def test_http_get_is_read_only_and_rejects_external_origin(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(App()));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.server_port)
        try:
            with patch('triage_bench.publisher_report_trial.run',side_effect=AssertionError('No inference')):
                with urlopen(base+'/api/report-comparison') as response:self.assertEqual(json.load(response)['actual_calls'],144)
                with urlopen(base+'/report-comparison') as response:self.assertIn(b'Repeated errors',response.read())
            for request,code in [(Request(base+'/api/report-comparison',headers={'Origin':'https://example.org'}),403),(Request(base+'/api/report-comparison',data=b'{}'),405)]:
                with self.assertRaises(HTTPError) as error:urlopen(request)
                self.assertEqual(error.exception.code,code);error.exception.close()
        finally:server.shutdown();server.server_close();thread.join()
