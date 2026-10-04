import copy,json,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from triage_bench.app import App,handler_for
from triage_bench.public_temporal_service import PublicTemporalStudy
from triage_bench.study_page import return_path

class TemporalServiceTests(unittest.TestCase):
    def test_unavailable_or_mismatched_assessment_never_exposes_results(self):
        study=PublicTemporalStudy('/unavailable')
        with patch.object(study,'verified',side_effect=ValueError('changed')):
            self.assertFalse(study.overview()['available']);self.assertEqual(study.overview()['metrics'],{})
            with self.assertRaises(ValueError):study.case('x')
        with patch('triage_bench.public_temporal_service.committed'),patch('triage_bench.public_temporal_service.load',side_effect=[{'status':'completed'},{'wrong':'assessment'}]),patch('triage_bench.public_temporal_service.score',return_value={'failed_or_missing':0}):
            with self.assertRaisesRegex(ValueError,'Unverified'):study.verified()

    def test_case_hides_reference_derived_fields_without_mutating_source(self):
        rounds=[{'round':1,'top1_correct':True,'target_in_shortlist':True,'wrong_leads':2}]
        original={'id':'x','target':'a','group':'a/cpu','fault':'cpu','arms':{'named':{'rounds':rounds}}}
        assessment={'cases':[original]}
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=root/'data';data.mkdir();output=root/'output';output.mkdir()
            (data/'development.inputs.json').write_text(json.dumps([{'id':'x','requests':{'named':{'state':'{}'},'temporal':{'state':'{"latency_time_windows": {}}'}}}]))
            (output/'responses.jsonl').write_text(json.dumps({'case_id':'x','arm':'named'})+'\n');(output/'controls.json').write_text(json.dumps({'x':{'ml':{}}}))
            study=PublicTemporalStudy(root)
            with patch.object(study,'verified',return_value=assessment),patch('triage_bench.public_temporal_service.DATA',data),patch('triage_bench.public_temporal_service.OUTPUT',output):
                hidden=study.case('x');self.assertIsNone(hidden['reference']);self.assertNotIn('target',hidden['case']);self.assertNotIn('group',hidden['case'])
                for k in ('top1_correct','target_in_shortlist','wrong_leads'):self.assertNotIn(k,hidden['case']['arms']['named']['rounds'][0])
                self.assertEqual(study.case('x',reveal=True)['reference']['target'],'a');self.assertTrue(original['arms']['named']['rounds'][0]['top1_correct'])

    def test_loopback_viewer_and_reader_are_read_only(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(App()));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
        try:
            with patch('triage_bench.public_temporal_service.PublicTemporalStudy.overview',return_value={'available':False}),patch('urllib.request.build_opener') as inference:
                for path in ('/temporal','/public-temporal.js','/api/public-temporal','/study?doc=public-temporal&return=%2Ftemporal%3Fcase%3Dx%23input'):
                    with urlopen(base+path) as response:self.assertEqual(response.status,200)
                inference.assert_not_called()
            self.assertEqual(return_path('/temporal?case=x#input'),'/temporal?case=x#input')
            with self.assertRaises(HTTPError) as error:urlopen(Request(base+'/api/public-temporal',headers={'Origin':'https://outside.example'}))
            self.assertEqual(error.exception.code,403)
        finally:server.shutdown();server.server_close();thread.join()
