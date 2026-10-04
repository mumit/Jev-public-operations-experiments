import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer

from triage_bench.app import App,handler_for
from triage_bench.public_format_service import PublicFormatStudy
from triage_bench.study_page import return_path
from test_public_format import state


class PublicFormatServiceTests(unittest.TestCase):
    def test_missing_data_never_fabricates_comparison_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            study=PublicFormatStudy(temporary);study.protocol.parent.mkdir()
            study.protocol.write_text(json.dumps({'counts':{'development':24}}))
            result=study.overview()
            self.assertFalse(result['data_available']);self.assertEqual(result['results'],{})
            self.assertEqual(result['available_splits'],[])

    def test_presentation_is_inspectable_but_reference_requires_reveal(self):
        with tempfile.TemporaryDirectory() as temporary:
            study=PublicFormatStudy(temporary);study.protocol.parent.mkdir();study.data.mkdir(parents=True)
            study.protocol.write_text(json.dumps({'local':'local','historical_data':'historical'}))
            (study.data/'development.inputs.json').write_text(json.dumps([{'id':'one','state':state()}]))
            model={'features':['example'],'intercept':0};controls={'ml':{'choice':'a','ranking':[]}}
            with patch.object(study,'overview',return_value={'available_splits':['development'],'boundary':{}}),patch('triage_bench.public_format_service.verify_local',return_value=model),patch('triage_bench.public_format_service.infer',return_value=controls):
                result=study.case('development','one','named')
                self.assertIsNone(result['reference']);self.assertIsNone(result['jev'])
                self.assertEqual(result['presentation']['services']['a']['socket']['after_median'],22)
                self.assertEqual(result['base_request']['questions'],result['request']['questions'])
                (study.data/'development.references.json').write_text(json.dumps([{'id':'one','target':'a','fault':'socket'}]))
                self.assertEqual(study.case('development','one','named',True)['reference']['target'],'a')

    def test_sealed_evaluation_cannot_expose_inputs_or_references(self):
        study=PublicFormatStudy('/unavailable')
        with patch.object(study,'overview',return_value={'available_splits':['development']}):
            with self.assertRaisesRegex(ValueError,'sealed'):study.case('evaluation','any','explained',True)

    def test_unverified_boundary_never_enters_case_display(self):
        with tempfile.TemporaryDirectory() as temporary:
            study=PublicFormatStudy(temporary);study.protocol.parent.mkdir();study.data.mkdir(parents=True)
            study.protocol.write_text(json.dumps({'counts':{'development':24,'calibration':18,'evaluation':36}}))
            (study.data/'manifest.json').write_text('{}');study.boundary.write_text('{}')
            for split in ('development','calibration'):
                (study.data/f'{split}.inputs.json').write_text('[]')
                hosted=study.root/f'runs/public-format/{split}-2026-10-03-v1'
                hosted.mkdir(parents=True);(hosted/'summary.json').write_text('{}')
            def gate_stub(data,protocol,split,candidate,boundary):
                if split=='evaluation':raise ValueError('Boundary drift')
            with patch('triage_bench.public_format_service.check'),patch('triage_bench.public_format_service.gate',side_effect=gate_stub),patch('triage_bench.public_format_service.score',return_value={}):
                result=study.overview()
                self.assertEqual(result['boundary'],{});self.assertEqual(result['boundary_results'],[])
                self.assertNotIn('evaluation',result['available_splits'])
                self.assertIn('failed verification',result['notes'][0])

    def test_http_assets_origin_protection_and_safe_reader_context(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(App()))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            for path in ('/public-format','/public-format.js'):
                with urlopen(base+path) as response:
                    self.assertEqual(response.status,200);self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
            with self.assertRaises(HTTPError) as error:urlopen(Request(base+'/api/public-format',headers={'Origin':'https://outside.example'}))
            self.assertEqual(error.exception.code,403)
            context='/public-format?split=evaluation&case=FMT-example&arm=named#input'
            self.assertEqual(return_path(context),context)
        finally:server.shutdown();server.server_close();thread.join()
