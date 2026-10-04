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
from triage_bench.public_rca_service import PublicRCAStudy
from triage_bench.study_page import return_path


class PublicRCAServiceTests(unittest.TestCase):
    def test_fresh_clone_never_fabricates_predictions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'checkpoints').mkdir()
            (root/'checkpoints/public-rca-protocol-2026-10-03.json').write_text(json.dumps({'counts':{'development':24},'condition':'known incident'}))
            overview=PublicRCAStudy(root).overview()
            self.assertFalse(overview['data_available']);self.assertEqual(overview['results'],{})
            self.assertEqual(overview['available_splits'],[])

    def test_public_reader_return_path_and_unknown_section(self):
        value='/public-rca?split=development&case=PUB-example#decision'
        self.assertEqual(return_path(value),value)
        self.assertNotEqual(return_path('/public-rca#unknown'),'/public-rca#unknown')

    def test_boundary_keeps_held_out_error_visible_without_reference_answers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);study=PublicRCAStudy(root)
            study.protocol.parent.mkdir();study.data.mkdir(parents=True)
            study.protocol.write_text(json.dumps({'counts':{},'condition':'known incident'}))
            (study.data/'manifest.json').write_text('{}')
            study.boundary.write_text(json.dumps({'selected':{'threshold':0.5}}))
            for split in ('train','development','calibration','evaluation'):
                (study.data/f'{split}.inputs.json').write_text('[]')
                if split!='train':
                    hosted=root/f'runs/public-rca/{split}-2026-10-03-v1'
                    hosted.mkdir(parents=True);(hosted/'summary.json').write_text('{}')
            result={'metrics':{},'outcomes':[{'target':'answer'}],'comparisons':{},
                    'curves':[{'threshold':0.5,'suggestions':18,'wrong':1,'review':0}]}
            with patch('triage_bench.public_rca_service.check'),patch('triage_bench.public_rca_service.gate'),patch('triage_bench.public_rca_service.verify_hosted'),patch('triage_bench.public_rca_service.score',return_value=result):
                overview=study.overview()
            self.assertEqual(overview['boundary_results']['evaluation']['wrong'],1)
            self.assertNotIn('outcomes',overview['results']['evaluation'])
            self.assertNotIn('comparisons',overview['results']['evaluation'])

    def test_sealed_evaluation_cannot_be_inspected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);study=PublicRCAStudy(root)
            study.protocol.parent.mkdir();study.data.mkdir(parents=True)
            study.protocol.write_text(json.dumps({'counts':{},'condition':'known incident'}))
            (study.data/'manifest.json').write_text('{}')
            for split in ('train','development'):(study.data/f'{split}.inputs.json').write_text('[]')
            with patch('triage_bench.public_rca_service.check'),patch('triage_bench.public_rca_service.gate',side_effect=ValueError('sealed')),patch('triage_bench.public_rca_service.verify_hosted') as hosted:
                self.assertNotIn('evaluation',study.overview()['available_splits'])
                with self.assertRaisesRegex(ValueError,'sealed'):study.case('evaluation','PUB-example',True)
                hosted.assert_not_called()

    def test_http_assets_and_origin_protection(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(App()))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            for path in ('/public-rca','/public-rca.js','/public-rca.css'):
                with urlopen(base+path) as response:
                    self.assertEqual(response.status,200);self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
            with self.assertRaises(HTTPError) as error:urlopen(Request(base+'/api/public-rca',headers={'Origin':'https://outside.example'}))
            self.assertEqual(error.exception.code,403)
        finally:server.shutdown();server.server_close();thread.join()
