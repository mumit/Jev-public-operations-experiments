import ast
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from scripts.restore_evidence import restore
from triage_bench.paths import ROOT
from triage_bench.provenance import migration,verify_sources,reject_historical_inference
from triage_bench.study_page import render_study,return_path
from triage_bench.app import App


class MigrationTests(unittest.TestCase):
    def test_historical_sources_and_extracted_helpers_match(self):
        for expected in migration()['historical_source_sets']:verify_sources(expected)
        for archive,active,names in [('runner.py','runner.py',{'NoRedirect','clean_api_key'}),
             ('experiment3/hosted.py','hosted.py',{'encoded','redact'}),('experiment3/task_fit_trial.py','profile.py',{'profile_check'})]:
            def nodes(path):
                return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names}
            self.assertEqual(nodes(ROOT/'provenance/source/triage_bench'/archive),nodes(ROOT/'triage_bench'/active))

    def test_completed_protocols_cannot_run_even_in_another_directory(self):
        from triage_bench.public_rca_trial import run as rca
        from triage_bench.public_format_trial import run as presentation
        for name in migration()['historical_protocol_sha256']:
            protocol=ROOT/'checkpoints'/name
            with self.assertRaisesRegex(ValueError,'read-only'):reject_historical_inference(protocol)
            with patch('urllib.request.build_opener') as network:
                with self.assertRaisesRegex(ValueError,'read-only'):
                    if 'format' in name:presentation(None,protocol,'runs/different',{},'evaluation',None,None)
                    else:rca(None,protocol,'runs/different',{},'evaluation',None,None)
                network.assert_not_called()

    def test_source_paths_and_unknown_fingerprints_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unsafe'):verify_sources({'../outside':'digest'})
        with self.assertRaisesRegex(ValueError,'drift'):verify_sources({'triage_bench/profile.py':'bad'})

    def test_all_public_articles_render_with_safe_return_context(self):
        app=App()
        for doc in ('public-rca','public-format','public-data','evidence','handoff','migration'):
            html=render_study(app,{'doc':doc,'return':'/public-format?arm=named#input'}).decode()
            self.assertIn('href="/public-format?arm=named#input"',html)
            self.assertIn('Public operations research',html)
            self.assertNotIn('/task-fit',html)
        self.assertEqual(return_path('https://outside.example/'),'/public-format')

    def archive(self,root,name='runs/public/example.json'):
        path=root/'bundle.tar.gz';data=b'{"public":true}'
        with tarfile.open(path,'w:gz') as bundle:
            item=tarfile.TarInfo(name);item.size=len(data);bundle.addfile(item,io.BytesIO(data))
        manifest={'archive_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'files':{name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}}}
        return path,manifest

    def test_restore_verifies_all_files_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);archive,manifest=self.archive(root)
            self.assertEqual(restore(archive,root,manifest)['files'],1)
            with self.assertRaisesRegex(ValueError,'overwritten'):restore(archive,root,manifest)
            self.assertEqual((root/'runs/public/example.json').read_bytes(),b'{"public":true}')

    def test_unsafe_and_corrupted_archives_leave_no_extracted_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);archive,manifest=self.archive(root,'runs/../../outside')
            with self.assertRaisesRegex(ValueError,'Unsafe'):restore(archive,root,manifest)
            self.assertFalse((root/'runs').exists())
            archive,manifest=self.archive(root);manifest['files']['runs/public/example.json']['sha256']='bad'
            with self.assertRaisesRegex(ValueError,'checksum'):restore(archive,root,manifest)
            self.assertFalse((root/'runs').exists())
