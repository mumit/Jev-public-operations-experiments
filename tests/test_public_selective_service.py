import json,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from triage_bench.public_selective_service import PublicSelectiveStudy
from triage_bench.app import App,handler_for
from triage_bench.study_page import return_path

class SelectiveServiceTests(unittest.TestCase):
    def test_incomplete_and_changed_results_stay_unavailable(self):
        study=PublicSelectiveStudy('/unavailable')
        with patch.object(study,'verified',side_effect=ValueError('drift')):
            self.assertFalse(study.overview()['available']);self.assertEqual(study.overview()['stages'],{})
            with self.assertRaises(ValueError):study.case('evaluation','x')
        with patch('triage_bench.public_selective_service.committed'),patch('triage_bench.public_selective_service.verified_rows'),patch('triage_bench.public_selective_service.load',return_value={'failed_or_missing':0}),patch('triage_bench.public_selective_service.score',return_value={'failed_or_missing':1}):
            with self.assertRaisesRegex(ValueError,'recomputation'):study.verified('evaluation')

    def test_reference_fields_hidden_without_altering_recorded_outcomes(self):
        row={'id':'x','round':1,'target':'a','group':'a/cpu','fault':'cpu','leads':['a'],'correct_first':True,'cause_included':True,'wrong_leads':0,'raw_correct_first':True}
        a={'selective':{'outcomes':[row],'policy':{}},'failed_or_missing':0}
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=root/'data';data.mkdir();run=root/'run';run.mkdir()
            (data/'inputs.json').write_text(json.dumps([{'id':'x','request':{'state':'{}'}}]))
            (run/'responses.jsonl').write_text(json.dumps({'case_id':'x','round':1})+'\n');(run/'controls.json').write_text(json.dumps({'x':{}}))
            study=PublicSelectiveStudy(root)
            with patch.object(study,'verified',return_value=a),patch('triage_bench.public_selective_service.folder',return_value=data),patch('triage_bench.public_selective_service.output',return_value=run),patch('triage_bench.public_selective_service.confirmation_folder',return_value=data),patch('triage_bench.public_selective_service.confirmation_output',return_value=run):
                hidden=study.case('calibration','x');self.assertIsNone(hidden['reference'])
                for key in ('target','group','correct_first','cause_included','wrong_leads','raw_correct_first'):self.assertNotIn(key,hidden['outcomes'][0])
                self.assertEqual(study.case('calibration','x',True)['reference']['target'],'a');self.assertTrue(row['correct_first'])
                reserve=study.case('train-ticket-reserve','x');self.assertIsNone(reserve['reference']);self.assertNotIn('target',reserve['outcomes'][0]);self.assertEqual(reserve['split'],'train-ticket-reserve')

    def test_loopback_routes_reader_and_origin_do_not_invoke_inference(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(App()));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
        try:
            with patch('triage_bench.public_selective_service.PublicSelectiveStudy.overview',return_value={'available':False}),patch('urllib.request.build_opener') as inference:
                for path in ('/selective','/public-selective.js','/api/public-selective','/study?doc=public-selective&return=%2Fselective%3Fsplit%3Dcalibration%23inspect'):
                    with urlopen(base+path) as response:self.assertEqual(response.status,200)
                inference.assert_not_called()
            self.assertEqual(return_path('/selective?split=calibration#inspect'),'/selective?split=calibration#inspect')
            with self.assertRaises(HTTPError) as error:urlopen(Request(base+'/api/public-selective',headers={'Origin':'https://outside.example'}))
            self.assertEqual(error.exception.code,403)
        finally:server.shutdown();server.server_close();thread.join()
