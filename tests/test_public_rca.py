import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from triage_bench.public_rca_data import ASSIGNMENTS,FAULTS,partition,state_from_metrics,COUNTS,dump
from triage_bench.public_rca_models import fit,infer,vector,FEATURES
from triage_bench.public_rca_trial import body,normalize,check
from triage_bench.public_rca_stages import committed
from triage_bench.public_data import sha
from triage_bench.hosted import encoded


class PublicRCAStudyTests(unittest.TestCase):
    def index(self):
        return [{'dataset':'RE2-OB','case':f're2ob_{s}_{f}_{i}','root_cause_service':s,'fault':f,'repetition':i}
                for s in ASSIGNMENTS for f in FAULTS for i in (1,2,3)]

    def state(self):
        return state_from_metrics({'time':[1700000000+i for i in range(6)],
               'handler_cpu':[1.,1.,1.,20.,20.,20.],'downstream_latency-90':[1.,1.,1.,2.,2.,2.],
               'PassthroughCluster_workload':[4.,4.,4.,4.,4.,4.]},1700000003)

    def test_group_disjointness_all_fault_coverage_and_inspected_exclusions(self):
        plan=partition(self.index())
        self.assertEqual(len(plan),90)
        groups={}
        for row in plan:groups.setdefault(row['group'],set()).add(row['split'])
        self.assertTrue(all(len(s)==1 for s in groups.values()))
        for split,count in COUNTS.items():
            rows=[r for r in plan if r['split']==split]
            self.assertEqual(len(rows),count)
            self.assertEqual({r['group'].split('/')[1] for r in rows},set(FAULTS))
        for group in ('checkoutservice/cpu','currencyservice/delay','emailservice/socket'):
            self.assertEqual(groups[group],{'development'})
        with self.assertRaises(ValueError):partition(self.index()[:-1])

    def test_source_name_normalization_preserves_observed_identity(self):
        state=self.state()
        self.assertIn('PassthroughCluster',state['services'])
        self.assertNotIn('passthroughcluster',state['services'])
        self.assertEqual(len(state['services']['handler']['cpu']),5)
        duplicate={'time':[1700000000+i for i in range(6)],'Handler_cpu':[1.]*6,'handler_cpu':[1.]*6}
        with self.assertRaises(ValueError):state_from_metrics(duplicate,1700000003)

    def test_all_summaries_and_candidates_enter_body_without_answers(self):
        state=self.state();request=body(state)
        self.assertEqual(json.loads(request['state']),state)
        self.assertEqual(set(request['questions']['cause']['criteria']),set(state['services'])|{'insufficient_evidence'})
        self.assertNotIn('root_cause',request['state'])
        self.assertNotIn('source_case',request['state'])

    def test_missing_metric_is_not_zero_shift(self):
        self.assertNotEqual(vector({}),vector({'cpu':[1.,1.,0.,0.,0.]}))
        self.assertEqual(len(vector({})),len(FEATURES))

    def test_fitted_margins_reconstruct_and_identifiers_do_not_enter_ml_features(self):
        state=self.state();train=[{'id':'train-1','state':state},{'id':'train-2','state':state}]
        model=fit(train,[{'id':'train-1','target':'handler'},{'id':'train-2','target':'handler'}])
        self.assertEqual(model['training_ids'],['train-1','train-2'])
        outputs=infer(state,model)
        for row in outputs['ml']['ranking']:
            self.assertAlmostEqual(row['score'],sum(row['contributions'])+model['intercept'],places=10)
        renamed=copy.deepcopy(state);renamed['services']['renamed']=renamed['services'].pop('handler')
        score=lambda s,name: next(r['score'] for r in infer(s,model)['ml']['ranking'] if r['service']==name)
        self.assertEqual(score(state,'handler'),score(renamed,'renamed'))

    def test_malformed_or_changed_provider_outputs_are_not_success(self):
        options=('handler','insufficient_evidence')
        raw={'model':'jev-1.13.0','answers':{'cause':{'choice':'handler','probabilities':{'handler':.9,'insufficient_evidence':.1}}}}
        self.assertEqual(normalize(raw,options)[0],'handler')
        for bad in [[],{**raw,'answers':None},{**raw,'model':'jev-latest'}]:
            with self.assertRaises(ValueError):normalize(bad,options)
        for probs in [{'handler':True,'insufficient_evidence':0},{'handler':float('nan'),'insufficient_evidence':.1},
                      {'handler':.2,'insufficient_evidence':.8},{'handler':.9}]:
            bad=copy.deepcopy(raw);bad['answers']['cause']['probabilities']=probs
            with self.assertRaises(ValueError):normalize(bad,options)

    def test_only_quantized_probability_rounding_is_normalized(self):
        raw={'model':'jev-1.13.0','answers':{'cause':{'choice':'handler','probabilities':{'handler':.90,'insufficient_evidence':.09}}}}
        _,dist,_=normalize(raw,('handler','insufficient_evidence'))
        self.assertAlmostEqual(sum(dist.values()),1.)
        raw['answers']['cause']['probabilities']['handler']=.8991
        with self.assertRaises(ValueError):normalize(raw,('handler','insufficient_evidence'))

    def test_uncommitted_stage_gate_is_rejected(self):
        with tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parents[1]/'checkpoints',suffix='.json') as file:
            file.write(b'{}');file.flush()
            with self.assertRaises(ValueError):committed(file.name)

    def evidence(self,folder,complete=True):
        data=folder/'data';local=folder/'local';hosted=folder/'hosted'
        for p in (data,local,hosted):p.mkdir()
        state=self.state()
        train=[{'id':'train','state':state}]
        dump(data/'train.inputs.json',train);dump(data/'train.references.json',[{'id':'train','target':'handler'}])
        model=fit(train,[{'id':'train','target':'handler'}]);dump(local/'fitted.json',model)
        dump(local/'manifest.json',{'files':{'fitted.json':sha((local/'fitted.json').read_bytes())},
            'training_source':sha((data/'train.inputs.json').read_bytes()),'training_references':sha((data/'train.references.json').read_bytes())})
        packets=[{'id':f'dev-{i}','state':state} for i in (1,2)]
        dump(data/'development.inputs.json',packets)
        dump(data/'development.references.json',[{'id':p['id'],'group':'handler/cpu','target':'handler','fault':'cpu'} for p in packets])
        requests=[{'id':p['id'],'body':body(p['state']),'request_sha256':sha(encoded(body(p['state'])))} for p in packets]
        protocol=folder/'protocol.json';dump(protocol,{'requests':{'development':[{'id':r['id'],'request_sha256':r['request_sha256']} for r in requests]}})
        dump(hosted/'requests.json',requests)
        raw={'model':'jev-1.13.0','answers':{'cause':{'choice':'handler','probabilities':{'handler':.9,'downstream':.05,'PassthroughCluster':.03,'insufficient_evidence':.02}}}}
        choice,dist,conf=normalize(raw,requests[0]['body']['questions']['cause']['criteria'])
        rows=[{'id':r['id'],'request_sha256':r['request_sha256'],'status':'ok','choice':choice,'probabilities':dist,'provider_confidence':conf,'raw_response':raw,'latency_ms':10} for r in (requests if complete else requests[:1])]
        (hosted/'responses.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        dump(hosted/'summary.json',{'split':'development','status':'completed' if complete else 'incomplete_or_failed',
             'protocol_sha256':sha(protocol.read_bytes()),'evidence_sha256':{p.name:sha(p.read_bytes()) for p in hosted.iterdir() if p.is_file()}})
        return data,protocol,local,hosted

    def test_missing_responses_keep_full_denominator_and_cannot_unlock_next_stage(self):
        from triage_bench.public_rca_stages import score,verify_hosted
        with tempfile.TemporaryDirectory() as temporary:
            data,protocol,local,hosted=self.evidence(Path(temporary),complete=False)
            result=score(data,protocol,local,hosted,'development')
            self.assertEqual(result['metrics']['jev']['correct'],1)
            self.assertEqual(result['metrics']['jev']['cases'],2)
            self.assertEqual(result['failed_or_missing'],1)
            self.assertEqual(result['curves'][0]['review'],1)
            with self.assertRaises(ValueError):verify_hosted(hosted,protocol,'development')

    def test_changed_requests_and_training_model_fail_recomputation(self):
        from triage_bench.public_rca_stages import score,verify_local
        with tempfile.TemporaryDirectory() as temporary:
            data,protocol,local,hosted=self.evidence(Path(temporary))
            requests=json.loads((hosted/'requests.json').read_text());requests[0]['body']['state']='changed'
            dump(hosted/'requests.json',requests)
            summary=json.loads((hosted/'summary.json').read_text());summary['evidence_sha256']['requests.json']=sha((hosted/'requests.json').read_bytes());dump(hosted/'summary.json',summary)
            with self.assertRaisesRegex(ValueError,'request body changed'):score(data,protocol,local,hosted,'development')
            model=json.loads((local/'fitted.json').read_text());model['intercept']+=1;dump(local/'fitted.json',model)
            manifest=json.loads((local/'manifest.json').read_text());manifest['files']['fitted.json']=sha((local/'fitted.json').read_bytes());dump(local/'manifest.json',manifest)
            with self.assertRaisesRegex(ValueError,'does not reproduce'):verify_local(local,data)
