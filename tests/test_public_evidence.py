import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
from triage_bench.public_evidence_features import request,compose,ARMS,FIELDS
from triage_bench.public_evidence_reference import reference
from triage_bench.public_evidence_trial import answers,assess
from triage_bench.profile import MODEL


def observation(change=3.,missing=.2):
    values={'before_median':1.,'after_median':2.,'signed_change':change,'before_missing_fraction':missing,'after_missing_fraction':missing}
    b={'spans':5,'duration_median_us':100.,'duration_p90_us':200.,'uncovered_duration_median_us':0.,'uncovered_duration_p90_us':None}
    a={**b,'duration_median_us':125.,'duration_p90_us':150.}
    return {'service':'fixture','metrics':{'cpu':values},'trace':{'before':b,'after':a},'window_seconds':{'before':10,'after':20}}


class EvidenceTests(unittest.TestCase):
    def test_inclusive_thresholds_negative_changes_and_ties(self):
        o=observation(-3.);o['metrics']['mem']=copy.deepcopy(o['metrics']['cpu'])
        r=reference(o)
        self.assertEqual(r['answers']['metric_change'],['material'])
        self.assertEqual(r['answers']['trace_change'],['material'])
        self.assertEqual(r['answers']['trace_coverage'],['adequate'])
        self.assertEqual(r['answers']['metric_channel'],['cpu','mem'])
        o['metrics']['mem']['signed_change']=2.999;o['metrics']['cpu']['signed_change']=2.999
        o['trace']['after']['duration_median_us']=124.99;o['trace']['after']['duration_p90_us']=150.01
        r=reference(o);self.assertEqual(r['answers']['metric_change'],['quiet']);self.assertEqual(r['answers']['trace_change'],['quiet'])
        self.assertEqual(r['composition'],'no_material_change')

    def test_missing_and_nonpositive_values_are_unknown(self):
        o=observation(100,.200001);o['trace']=None
        r=reference(o)
        self.assertEqual(r['answers']['metric_change'],['unknown']);self.assertEqual(r['answers']['metric_channel'],['no_eligible_metric'])
        self.assertEqual(r['answers']['trace_change'],['unknown']);self.assertEqual(r['answers']['trace_coverage'],['absent'])
        self.assertEqual(r['composition'],'evidence_limited')
        o=observation();o['metrics']['cpu']['signed_change']=None
        for key in ('duration_median_us','duration_p90_us','uncovered_duration_median_us','uncovered_duration_p90_us'):o['trace']['before'][key]=0
        self.assertEqual(reference(o)['answers']['trace_change'],['unknown'])
        self.assertEqual(reference(o)['answers']['trace_coverage'],['adequate'])

    def test_sample_counts_apply_to_each_window(self):
        o=observation();o['trace']['after']['spans']=4
        self.assertEqual(reference(o)['answers']['trace_coverage'],['limited'])
        self.assertEqual(reference(o)['answers']['trace_change'],['unknown'])
        o['trace']['before']['spans']=o['trace']['after']['spans']=0
        self.assertEqual(reference(o)['answers']['trace_coverage'],['absent'])

    def test_calculated_arm_changes_only_arithmetic_state(self):
        o=observation();saved=copy.deepcopy(o);a,b=(request(o,arm) for arm in ARMS)
        self.assertEqual(a['questions'],b['questions']);bs=json.loads(b['state']);delta=bs.pop('calculated_changes')
        self.assertEqual(json.loads(a['state']),bs);self.assertEqual(o,saved)
        self.assertEqual(delta['trace_changes'][0],.25)
        self.assertEqual(delta['trace_changes'][4],-.5)
        self.assertNotIn('answers',bs);self.assertEqual(set(a['questions']),set(FIELDS))

    def test_parallel_answers_are_composed_in_code_and_missing_stays_unavailable(self):
        self.assertEqual(compose({'metric_change':'material','trace_change':'unknown'}),'change_supported')
        self.assertEqual(compose({'metric_change':'quiet','trace_change':'unknown'}),'evidence_limited')
        self.assertEqual(compose({}),'unavailable')

    def test_all_four_provider_answers_are_validated(self):
        o=observation();body=request(o,'observations');r=reference(o)
        raw={'model':MODEL,'answers':{k:{'choice':v[0],'probabilities':{opt:float(opt==v[0]) for opt in body['questions'][k]['criteria']}} for k,v in r['answers'].items()}}
        self.assertEqual(len(answers(raw,body)),4)
        raw['answers'].pop('trace_change')
        with self.assertRaises(ValueError):answers(raw,body)
        raw['model']='other'
        with self.assertRaises(ValueError):answers(raw,body)

    def test_failure_denominators_and_tied_channel_acceptance(self):
        o=observation();o['metrics']['mem']=copy.deepcopy(o['metrics']['cpu']);ref={'id':'card',**reference(o)}
        packet={'id':'card','case_id':'source','dataset':'fixture'}
        result=assess([], [packet], [ref])['fixture']
        self.assertFalse(result['research_gate']);self.assertEqual(result['arms']['calculated']['per_round'][0]['failed_or_missing'],1)
        rows=[]
        for arm in ARMS:
            for n in (1,2,3):
                rows.append({'card_id':'card','arm':arm,'round':n,'status':'ok','answers':{k:{'choice':v[-1],'probabilities':{v[-1]:1.}} for k,v in ref['answers'].items()}})
        result=assess(rows,[packet],[ref])['fixture']
        self.assertTrue(result['research_gate']);self.assertEqual(result['arms']['calculated']['per_round'][0]['all_correct'],1)
        rows[0]['status']='error'
        self.assertFalse(assess(rows,[packet],[ref])['fixture']['pairs'][0]['fix'])

    def test_wrong_support_and_withholding_are_visible(self):
        o=observation(.1);o['trace']['after']['duration_median_us']=o['trace']['before']['duration_median_us'];o['trace']['after']['duration_p90_us']=o['trace']['before']['duration_p90_us']
        ref={'id':'card',**reference(o)};packet={'id':'card','case_id':'source','dataset':'fixture'}
        row={'card_id':'card','arm':'calculated','round':1,'status':'ok','answers':{k:{'choice':v[0],'probabilities':{v[0]:1.}} for k,v in ref['answers'].items()}}
        row['answers']['metric_change']={'choice':'material','probabilities':{'material':.9,'quiet':.1}}
        a=assess([row],[packet],[ref])['fixture']['arms']['calculated']['per_round'][0]
        self.assertEqual(a['false_displayed_support'],1)
        row['answers']['metric_change']['probabilities']={'material':.6,'quiet':.4}
        a=assess([row],[packet],[ref])['fixture']['arms']['calculated']['per_round'][0]
        self.assertEqual(a['withheld'],1);self.assertEqual(a['false_displayed_support'],0)

    def test_reader_preserves_service_context(self):
        from triage_bench.study_page import return_path,render_study
        from triage_bench.paths import ROOT
        from types import SimpleNamespace
        value='/evidence-assessment?dataset=Train+Ticket&card=fixture&arm=calculated&round=2&field=trace_change#input'
        self.assertEqual(return_path(value),value)
        page=render_study(SimpleNamespace(root=ROOT),{'doc':'public-evidence','return':value}).decode()
        self.assertIn('card=fixture&amp;arm=calculated',page)
        self.assertIn('field=trace_change#input',page)

    def test_inspector_hides_numerical_reference_without_mutating_results(self):
        from triage_bench.public_evidence_service import PublicEvidenceStudy
        packet={'id':'card','dataset':'fixture','observation':observation()}
        ref={'id':'card',**reference(packet['observation'])}
        outcome={'id':'card','round':1,'choices':{},'field_correct':{},'all_correct':True,'reference_composition':'change_supported',
                 'composition_correct':True,'false_displayed_support':False,'correct_displayed_support':True}
        result={'datasets':{'fixture':{'arms':{'observations':{'outcomes':[outcome]}}}}}
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp);(dest/'responses.jsonl').write_text(json.dumps({'card_id':'card'})+'\n')
            with patch.object(PublicEvidenceStudy,'verified',return_value=result),patch('triage_bench.public_evidence_service.OUTPUT',dest),patch('triage_bench.public_evidence_service.load',side_effect=lambda p:[packet] if p.name=='inputs.json' else [ref]):
                study=PublicEvidenceStudy(dest);hidden=study.card('card')
                self.assertIsNone(hidden['reference'])
                for key in ('field_correct','reference_composition','composition_correct','false_displayed_support'):self.assertNotIn(key,hidden['outcomes']['observations'][0])
                self.assertEqual(study.card('card',True)['reference'],ref)
                self.assertIn('reference_composition',outcome)
