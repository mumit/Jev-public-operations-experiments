import json,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
from scripts import probe_public_context as context
from triage_bench.public_data import sha
from triage_bench.hosted import encoded

class ContextProbeTests(unittest.TestCase):
    def test_once_only_context_probe_does_not_retry_or_score_answers(self):
        profile={'model':'jev-1.13.0','endpoint':'https://example.invalid','context_tokens':32768,'api_key':'fixture-key'}
        body={'state':'input','questions':{'cause':{'criteria':{'a':None}}}}
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=root/'data';data.mkdir();(data/'manifest.json').write_text('{}');protocol=root/'protocol.json';output=root/'output'
            p={'model':profile['model'],'endpoint':profile['endpoint'],'context_tokens':32768,'maximum_calls':1,'case_id':'x','request_bytes':len(encoded(body)),'request_sha256':sha(encoded(body)),
                'source_sha256':sha(Path(context.__file__).read_bytes()),'manifest_sha256':sha((data/'manifest.json').read_bytes())}
            protocol.write_text(json.dumps(p));response=MagicMock();response.__enter__.return_value=response
            response.read.return_value=json.dumps({'model':'jev-1.13.0','answers':{'cause':{'choice':'a','probabilities':{'a':1},'confidence':.9}},'usage':{'input_tokens':200},'echo':'fixture-key'}).encode()
            opener=MagicMock();opener.open.return_value=response
            with patch.object(context,'PROTOCOL',protocol),patch.object(context,'DATA',data),patch.object(context,'OUTPUT',output),patch.object(context,'request',return_value=('x',body)),patch.object(context,'committed'),patch('urllib.request.build_opener',return_value=opener):
                result=context.run(profile);self.assertEqual(result['status'],'accepted');self.assertEqual(result['input_tokens'],200)
                self.assertNotIn('correct',result);self.assertNotIn('fixture-key',(output/'result.json').read_text())
                with self.assertRaises(FileExistsError):context.run(profile)
                self.assertEqual(opener.open.call_count,1)
