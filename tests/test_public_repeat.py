import copy
import json
import urllib.error
from unittest.mock import MagicMock
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from triage_bench.paths import ROOT
from triage_bench.public_repeat_trial import selection,plan,run,ARMS,ROUNDS,ORIGINAL
from triage_bench.public_repeat_results import assess,displayed,verified_rows
from triage_bench.public_rca_stages import load
from triage_bench.hosted import encoded
from triage_bench.public_data import sha


def row(identifier,arm,number,choice='a',probability=.8):
    return {'id':f'{identifier}::{arm}::r{number}','case_id':identifier,'arm':arm,'round':number,
        'status':'ok','choice':choice,'probabilities':{choice:probability},'provider_confidence':.1}


def fixture():
    protocol={'cases':[{'id':'x','split':'evaluation','role':'all_correct_control','group':'g','fault':'delay'}],
        'thresholds':{'compact':.6,'named':.5,'explained':.5}}
    rows=[row('x',arm,n) for n in range(1,ROUNDS+1) for arm in ARMS]
    refs={'x':{'target':'a'}};original={('x',arm):row('x',arm,0) for arm in ARMS}
    return protocol,rows,refs,original


class PublicReplayTests(unittest.TestCase):
    def test_predeclared_targeted_selection_and_exact_wire_bytes(self):
        if not (ROOT/'runs/public-format/evaluation-2026-10-03-v1/summary.json').exists():self.skipTest('Restore public evidence for exact replay planning.')
        cases,planned=plan()
        self.assertEqual(len(cases),12);self.assertEqual(len(planned),180)
        self.assertEqual(sum(c['role']=='inspected_error' for c in cases),6)
        self.assertEqual({c['fault'] for c in cases if c['role']=='all_correct_control'},{'cpu','delay','disk','loss','mem','socket'})
        historical={}
        for split in ('calibration','evaluation'):
            for r in load(ROOT/f'runs/public-format/{split}-2026-10-03-v1/requests.json'):historical[(r['case_id'],r['arm'])]=r
        for request in planned:
            source=historical[(request['case_id'],request['arm'])]
            self.assertEqual(encoded(request['body']),encoded(source['body']))
            self.assertEqual(sha(encoded(request['body'])),request['request_sha256'])
            self.assertNotIn(request['case_id'],request['body']['state'])
        for arm in ARMS:
            self.assertEqual(sum(planned[i]['arm']==arm for i in range(0,len(planned),3)),20)
        for case in cases:
            self.assertEqual({r['round'] for r in planned if r['case_id']==case['id']},{1,2,3,4,5})

    def test_consistency_does_not_replace_correctness_or_original_response(self):
        p,rows,refs,original=fixture()
        for r in rows:
            if r['arm']=='named':r.update(choice='b',probabilities={'b':.8})
        result=assess(p,rows,refs,original)
        self.assertEqual(result['metrics']['named']['choice_stable_cases'],1)
        self.assertEqual(result['metrics']['named']['wrong_displayed_responses'],5)
        self.assertEqual(result['metrics']['named']['matches_original_choice_cases'],0)
        self.assertFalse(result['research_gate']['passed'])
        self.assertEqual(result['metrics']['named']['per_round'][0]['cases'],1)
        self.assertEqual(result['metrics']['named']['response_slots'],5)

    def test_choice_and_display_variability_are_separate(self):
        p,rows,refs,original=fixture()
        next(r for r in rows if r['arm']=='named' and r['round']==2)['probabilities']={'a':.49}
        result=assess(p,rows,refs,original)
        self.assertEqual(result['metrics']['named']['choice_stable_cases'],1)
        self.assertEqual(result['metrics']['named']['display_stable_cases'],0)
        self.assertEqual(result['metrics']['named']['wrong_displayed_responses'],0)
        self.assertFalse(result['research_gate']['passed'])

    def test_failed_and_missing_responses_keep_planned_denominators(self):
        p,rows,refs,original=fixture();rows.pop();rows[1]['status']='error'
        result=assess(p,rows,refs,original)
        self.assertEqual(result['response_slots'],15);self.assertEqual(result['failed_or_missing'],2)
        self.assertEqual(sum(r['failed_or_missing'] for r in result['metrics']['explained']['per_round']),1)
        self.assertFalse(result['research_gate']['passed'])

    def test_threshold_is_inclusive_and_uses_selected_probability(self):
        r=row('x','named',1,probability=.5)
        self.assertTrue(displayed(r,.5));self.assertFalse(displayed(r,.6))
        r.update(choice='insufficient_evidence',probabilities={'insufficient_evidence':1})
        self.assertFalse(displayed(r,.5));self.assertFalse(displayed(None,.5))

    def test_matched_round_fixes_and_regressions_remain_visible(self):
        p,rows,refs,original=fixture()
        for r in rows:
            if r['arm']=='compact':r.update(choice='b',probabilities={'b':.8})
            if r['arm']=='explained' and r['round']==3:r.update(choice='b',probabilities={'b':.8})
        result=assess(p,rows,refs,original)
        self.assertEqual(next(r for r in result['comparisons'] if r['round']==3 and r['comparison']=='named_vs_compact')['fixes'],['x'])
        self.assertEqual(next(r for r in result['comparisons'] if r['round']==3 and r['comparison']=='explained_vs_named')['regressions'],['x'])

    def test_once_only_execution_claim_prevents_another_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);protocol=root/'protocol.json';protocol.write_text(json.dumps({'model':'jev-1.13.0','endpoint':'https://example.invalid','context_tokens':32768}))
            profile={'model':'jev-1.13.0','endpoint':'https://example.invalid','context_tokens':32768,'api_key':'fixture-key'}
            claim=root/'runs/public-repeat/execution'/ (sha(protocol.read_bytes())+'.json');claim.parent.mkdir(parents=True);claim.write_text('{}')
            with patch('triage_bench.public_repeat_trial.ROOT',root),patch('triage_bench.public_repeat_trial.check',return_value=[]),patch('triage_bench.public_repeat_trial.committed'),patch('urllib.request.build_opener') as network:
                with self.assertRaisesRegex(ValueError,'claimed'):run(protocol,root/'another',profile)
                network.assert_not_called();self.assertFalse((root/'another').exists())

    def test_version_drift_stops_and_redacts_recorded_payload(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);protocol=root/'protocol.json'
            profile={'model':'jev-1.13.0','endpoint':'https://example.invalid','context_tokens':32768,'api_key':'fixture-key'}
            protocol.write_text(json.dumps({k:v for k,v in profile.items() if k!='api_key'}))
            planned=[{'id':str(n),'case_id':'x','arm':'named','round':1,'split':'evaluation','request_sha256':'fixture',
                'body':{'questions':{'cause':{'criteria':['a']}}}} for n in range(3)]
            response=MagicMock();response.__enter__.return_value=response
            response.read.return_value=json.dumps({'model':'changed-model','echo':'fixture-key'}).encode()
            opener=MagicMock();opener.open.return_value=response
            with patch('triage_bench.public_repeat_trial.ROOT',root),patch('triage_bench.public_repeat_trial.check',return_value=planned),patch('triage_bench.public_repeat_trial.committed'),patch('urllib.request.build_opener',return_value=opener):
                summary=run(protocol,root/'run',profile)
            self.assertEqual(summary['attempted'],1);self.assertEqual(summary['failed'],1)
            self.assertEqual(summary['unattempted'],2);self.assertEqual(summary['stopped_reason'],'checkpoint_mismatch')
            saved=(root/'run/responses.jsonl').read_text()
            self.assertNotIn('fixture-key',saved);self.assertIn('[redacted]',saved)

    def test_http_failure_stops_without_recording_error_body(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);protocol=root/'protocol.json'
            profile={'model':'jev-1.13.0','endpoint':'https://example.invalid','context_tokens':32768,'api_key':'fixture-key'}
            protocol.write_text(json.dumps({k:v for k,v in profile.items() if k!='api_key'}))
            planned=[{'id':str(n),'body':{},'round':1,'arm':'named'} for n in range(3)]
            opener=MagicMock();opener.open.side_effect=urllib.error.HTTPError(profile['endpoint'],429,'fixture-key',{},None)
            with patch('triage_bench.public_repeat_trial.ROOT',root),patch('triage_bench.public_repeat_trial.check',return_value=planned),patch('triage_bench.public_repeat_trial.committed'),patch('urllib.request.build_opener',return_value=opener):
                summary=run(protocol,root/'run',profile)
            self.assertEqual(summary['attempted'],1);self.assertEqual(summary['failed'],1)
            self.assertEqual(summary['stopped_reason'],'provider_http_429')
            self.assertNotIn('fixture-key',(root/'run/responses.jsonl').read_text())
