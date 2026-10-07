import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from triage_bench import publisher_report_data as data,publisher_report_trial as trial
from triage_bench.publisher_report_features import request,rules,jev,hybrid,CHOICES
from triage_bench.publisher_report_scoring import score
from triage_bench.profile import MODEL
from triage_bench.public_sentence_features import validate_reply,GlobalReplyError


def row(identifier,n=1,choice='supported',probability=1):
    others=[k for k in CHOICES if k!=choice]
    return {'claim_id':identifier,'round':n,'status':'ok','answers':{'verdict':{'choice':choice,'probabilities':{choice:probability,others[0]:1-probability,others[1]:0}}}}

class PublisherReportTests(unittest.TestCase):
    def test_literal_polarity_and_qualification_guard(self):
        packet={'claim':'Traffic was impacted.','report':'Traffic was not impacted.'}
        self.assertEqual(rules(packet)['choice'],'contradicted')
        packet['claim']='Traffic was not impacted.'
        self.assertEqual(rules(packet)['choice'],'supported')
        packet['report']='Traffic was not impacted. However, some paths failed.'
        self.assertFalse(rules(packet)['displayed'])
        packet['report']='Traffic was not impacted.\n\nTraffic was impacted.'
        self.assertEqual(rules(packet)['reason'],'literal_conflict')

    def test_request_allowlist_excludes_annotations_and_metadata(self):
        packet={'report':'Observed text.','claim':'A claim.','reference':'contradicted','id':'answer-bearing','source_id':'private','topic':'secret','allocation':'evaluation'}
        r=request(packet);self.assertEqual(json.loads(r['state']),{'report_excerpt':'Observed text.','claim':'A claim.'})
        self.assertEqual(r['questions']['verdict']['type'],'choice')
        self.assertNotIn('answer-bearing',json.dumps(r))

    def test_fixed_boundary_invalid_and_conflicting_replies(self):
        low=jev(row('x',probability=.6999));high=jev(row('x',probability=.70))
        self.assertFalse(low['displayed']);self.assertTrue(high['displayed'])
        rule={'valid':True,'choice':'contradicted','displayed':True,'reason':'literal','matched_blocks':[0]}
        self.assertEqual(hybrid(rule,high)['reason'],'rules_jev_conflict')
        self.assertEqual(hybrid(rule,low)['via'],'rules')
        self.assertFalse(hybrid(rule,jev(None))['displayed'])

    def test_global_model_and_inconsistent_probabilities_never_repaired(self):
        raw={'model':MODEL,'answers':{'verdict':{'type':'choice','choice':'supported','probabilities':{'supported':.1,'contradicted':.8,'not_established':.1}}},'usage':{'input_tokens':100}}
        validated=validate_reply(raw,request({'report':'text','claim':'claim'}),32768)
        self.assertTrue(validated['field_errors']);self.assertFalse(jev(validated)['valid'])
        raw['model']='different'
        with self.assertRaises(GlobalReplyError):validate_reply(raw,request({'report':'text','claim':'claim'}),32768)

    def test_frozen_whole_incident_slots_and_exact_spans(self):
        d,c,r=data.metadata();self.assertEqual(len(c),48);self.assertEqual(len(r),48)
        if data.audit.CACHE.exists():
            for phase in ('development','evaluation'):
                packets,refs=data.packets(phase)
                self.assertEqual(len(packets),24)
                self.assertEqual(len({p['incident_group'] for p in packets}),4)
                self.assertTrue(all(len(p['report'].encode())<=14000 for p in packets))
            changed=copy.deepcopy(data.load(data.REFERENCES));changed['references'][0]['evidence_spans'][0]['block']=999
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'refs.json';path.write_text(json.dumps(changed))
                with patch.object(data,'REFERENCES',path),self.assertRaisesRegex(ValueError,'outside'):
                    data.packets('development')

    def test_missing_replies_and_small_panels_remain_in_denominators(self):
        packets=[{'id':'x','source_id':'s','topic':'service_impact','report':'A report.','claim':'A claim.'}]
        result=score(packets,[{'id':'x','choice':'supported'}],[],False)
        self.assertFalse(result['candidate_passes'])
        panel=next(p for p in result['panels'] if p['method']=='hybrid' and p['kind']=='incident')
        self.assertEqual((panel['claims'],panel['correct_display'],panel['withheld']),(1,0,1))
        with self.assertRaisesRegex(ValueError,'Duplicate'):score(packets,[{'id':'x','choice':'supported'}],[row('x'),row('x')],True)

    def test_wrong_eligible_jev_cannot_replace_a_correct_rule(self):
        packet={'id':'x','source_id':'s','topic':'service_impact','report':'Traffic was not impacted.','claim':'Traffic was not impacted.'}
        result=score([packet],[{'id':'x','choice':'supported'}],[row('x',n,choice='contradicted') for n in (1,2,3)],True)
        self.assertFalse(result['candidate_passes'])
        self.assertTrue(all(p['losses']==1 for p in result['paired']))

    def test_evaluation_gate_stops_before_source_or_provider_access(self):
        with patch.object(trial,'verify',return_value={'candidate_passes':False}),patch.object(trial,'check') as check,patch.object(trial.urllib.request,'build_opener') as network:
            with self.assertRaisesRegex(ValueError,'failed development'):trial.run('evaluation',{})
            check.assert_not_called();network.assert_not_called()
