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
from triage_bench.public_repeat_service import PublicRepeatStudy
from triage_bench.study_page import return_path
from test_public_repeat import fixture,assess


class ReplayServiceTests(unittest.TestCase):
    def test_missing_or_uncommitted_evidence_never_exposes_predictions(self):
        with tempfile.TemporaryDirectory() as temporary:
            study=PublicRepeatStudy(temporary)
            for error in (OSError('absent'),ValueError('uncommitted')):
                with patch.object(study,'verified',side_effect=error):
                    result=study.overview()
                    self.assertFalse(result['available']);self.assertEqual(result['cases'],[]);self.assertEqual(result['metrics'],{})
                    with self.assertRaises(type(error)):study.case('x')

    def test_recorded_assessment_must_equal_complete_recomputation(self):
        study=PublicRepeatStudy('/unavailable')
        with patch('triage_bench.public_repeat_service.committed'),patch('triage_bench.public_repeat_service.verified_rows',return_value=({},[])) as verified,patch('triage_bench.public_repeat_service.score',return_value={'correct':1}),patch('triage_bench.public_repeat_service.load',return_value={'correct':2}):
            with self.assertRaisesRegex(ValueError,'differs'):study.verified()
            verified.assert_called_once_with(study.protocol,study.folder,complete=True)

    def test_reference_reveal_does_not_mutate_cached_case(self):
        p,rows,refs,original=fixture();assessment=assess(p,rows,refs,original)
        with tempfile.TemporaryDirectory() as temporary:
            study=PublicRepeatStudy(temporary);study.folder.mkdir(parents=True)
            (study.folder/'requests.json').write_text(json.dumps([{'case_id':'x','arm':'named','body':{'state':'input'},'request_sha256':'same'}]))
            old=Path(temporary)/'runs/public-format/evaluation-2026-10-03-v1/responses.jsonl';old.parent.mkdir(parents=True)
            old.write_text(json.dumps({'id':'x::named','choice':'a'})+'\n')
            with patch.object(study,'verified',return_value=(p,rows,assessment)):
                hidden=study.case('x');self.assertIsNone(hidden['reference']);self.assertNotIn('target',hidden['case']);self.assertNotIn('group',hidden['case'])
                self.assertNotIn('correct',hidden['case']['arms']['named']['original'])
                self.assertNotIn('correct',hidden['case']['arms']['named']['repeats'][0])
                revealed=study.case('x',reveal=True);self.assertEqual(revealed['reference']['target'],'a')
                self.assertTrue(revealed['case']['arms']['named']['original']['correct'])
                self.assertNotIn('target',study.case('x')['case'])
                with self.assertRaises(ValueError):study.case('unknown')
                with self.assertRaises(ValueError):study.case('x','unknown')

    def test_loopback_routes_return_context_and_read_only_http(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(App()))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            with patch('triage_bench.public_repeat_service.PublicRepeatStudy.overview',return_value={'available':False}),patch('urllib.request.build_opener') as inference:
                for path in ('/repeatability','/public-repeat.js','/public-repeat.css','/api/public-repeat','/study?doc=public-repeat&return=%2Frepeatability%3Fcase%3Dx%23wire'):
                    with urlopen(base+path) as response:self.assertEqual(response.status,200)
                inference.assert_not_called()
            self.assertEqual(return_path('/repeatability?case=x#wire'),'/repeatability?case=x#wire')
            with self.assertRaises(HTTPError) as error:urlopen(Request(base+'/api/public-repeat',headers={'Origin':'https://outside.example'}))
            self.assertEqual(error.exception.code,403)
            with self.assertRaises(HTTPError) as error:urlopen(Request(base+'/api/public-repeat',method='POST',data=b'{}'))
            self.assertEqual(error.exception.code,405)
        finally:server.shutdown();server.server_close();thread.join()
