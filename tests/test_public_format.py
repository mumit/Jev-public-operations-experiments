import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from triage_bench.public_format_data import ARMS, SERVICES, FIELDS, FAULTS, partition, transform, restore
from triage_bench.public_format_trial import body,requests,claim
from triage_bench.public_format_stages import score,selected
from triage_bench.public_rca_trial import body as historical_body


def state():
    return {'condition':'known incident','columns':list(FIELDS),'signed_change_definition':'fixed formula',
        'window_rows':{'before':720,'after':721},
        'services':{'a':{'socket':[9,22,144.44444,0,0],'cpu':[None,0,None,1,0]},
                    'b':{'mem':[100,80,-2,0,.25]}}}


class PublicFormatTests(unittest.TestCase):
    def test_group_assignment_reserves_untouched_repetitions(self):
        index=[{'dataset':'RE2-SS','case':f'{s}_{f}_{r}','root_cause_service':s,'fault':f,'repetition':r}
               for s in SERVICES for f in FAULTS for r in (1,2,3)]
        plan=partition(index)
        self.assertEqual({s:sum(a['split']==s for a in plan) for s in ('calibration','evaluation','reserve')},
                         {'calibration':18,'evaluation':36,'reserve':36})
        for group in {a['group'] for a in plan}:
            self.assertEqual(len({a['split'] for a in plan if a['group']==group}),1)
        with self.assertRaises(ValueError):partition(index[:-1])

    def test_transform_is_lossless_for_missing_zero_and_negative_values(self):
        original=state();saved=copy.deepcopy(original)
        for arm in ARMS:
            result=transform(original,arm)
            self.assertEqual(restore(result,arm),saved)
            self.assertEqual(set(result['services']),{'a','b'})
            if arm!='compact':self.assertIsNone(result['services']['a']['cpu']['signed_change'])
        self.assertEqual(original,saved)
        self.assertNotIn('metric_definitions',transform(original,'named'))
        self.assertIn('metric_definitions',transform(original,'explained'))

    def test_questions_and_candidates_stay_identical_to_frozen_control(self):
        control=historical_body(state())
        for arm in ARMS:
            request=body(state(),arm)
            self.assertEqual(request['questions'],control['questions'])
            self.assertEqual(request['model'],control['model'])
            self.assertNotIn('reference',request['state'])
        self.assertEqual(body(state(),'compact'),control)

    def test_cyclic_order_balances_first_position_and_preserves_case_joins(self):
        with tempfile.TemporaryDirectory() as temporary:
            data=Path(temporary)
            (data/'development.inputs.json').write_text(json.dumps([{'id':str(i),'state':state()} for i in range(3)]))
            planned=requests(data,'development')
            self.assertEqual([r['arm'] for r in planned[::3]],list(ARMS))
            self.assertEqual(len({r['id'] for r in planned}),9)
            for r in planned:self.assertEqual(r['id'],r['case_id']+'::'+r['arm'])

    def test_missing_calls_stay_in_every_arm_denominator(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=root/'data';data.mkdir();hosted=root/'hosted';hosted.mkdir()
            protocol=root/'protocol.json';protocol.write_text(json.dumps({'local':'local','historical_data':'historical'}))
            (hosted/'summary.json').write_text('{}')
            packets=[{'id':str(i),'state':state()} for i in range(24)]
            refs=[{'id':str(i),'target':'a','fault':'socket','group':'g'+str(i//3)} for i in range(24)]
            (data/'development.inputs.json').write_text(json.dumps(packets));(data/'development.references.json').write_text(json.dumps(refs))
            rows=[{'id':'0::compact','case_id':'0','arm':'compact','status':'ok','choice':'a','probabilities':{'a':.7,'b':.2,'insufficient_evidence':.1},'latency_ms':1,'usage':{'input_tokens':10}},
                  {'id':'0::named','case_id':'0','arm':'named','status':'error','latency_ms':2}]
            controls={a:{'choice':'a'} for a in ('change','resource','ml')}
            with patch('triage_bench.public_format_stages.check'),patch('triage_bench.public_format_stages.verify_hosted',return_value=rows),patch('triage_bench.public_format_stages.verify_local',return_value={}),patch('triage_bench.public_format_stages.infer',return_value=controls):
                result=score(data,protocol,hosted,'development')
            self.assertEqual(result['failed_or_missing'],71)
            self.assertEqual(result['metrics']['compact']['correct'],1)
            for arm in ARMS:self.assertEqual(result['metrics'][arm]['cases'],24)
            self.assertEqual(result['metrics']['named']['withheld'],24)
            self.assertEqual(result['comparisons']['named_vs_compact']['regressions'],['0'])

    def test_calibration_selects_coverage_then_lower_threshold_or_none(self):
        curves=[{'threshold':.5,'suggestions':10,'wrong':1}, {'threshold':.6,'suggestions':8,'wrong':0}, {'threshold':.7,'suggestions':8,'wrong':0}]
        assessment={'curves':{'compact':curves,'named':curves,'explained':[{'threshold':1,'suggestions':0,'wrong':0}]}}
        result=selected(assessment)
        self.assertEqual(result['compact']['threshold'],.6)
        self.assertIsNone(result['explained'])

    def test_once_only_claim_rejects_another_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);protocol=root/'protocol.json';protocol.write_text('{}')
            with patch('triage_bench.public_format_trial.ROOT',root):
                claim(protocol,'evaluation',root/'one')
                with self.assertRaisesRegex(ValueError,'already has an execution claim'):claim(protocol,'evaluation',root/'two')

