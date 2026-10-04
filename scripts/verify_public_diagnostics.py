"""Recompute later public diagnostics without provider calls or new downloads."""
import json
from triage_bench.paths import ROOT
from triage_bench.public_data import sha
from triage_bench.hosted import encoded
from triage_bench.public_rca_stages import load,committed
from triage_bench.public_repeat_results import score as repeat_score,verified_rows
from triage_bench.public_temporal_audit import audit
from triage_bench.public_temporal_data import validate
from triage_bench.public_temporal_trial import score as temporal_score
from scripts.probe_public_context import PROTOCOL as CAPACITY_PROTOCOL,OUTPUT as CAPACITY_OUTPUT,request as capacity_request
from triage_bench.public_rca_trial import normalize


def verify():
    protocol=ROOT/'checkpoints/public-repeat-protocol-2026-10-03.json';folder=ROOT/'runs/public-repeat/diagnostic-2026-10-03-v1'
    assessment=ROOT/'checkpoints/public-repeat-results-2026-10-03.json';committed(protocol);committed(assessment)
    verified_rows(protocol,folder,complete=True)
    if repeat_score(protocol,folder)!=load(assessment):raise ValueError('Replay assessment changed.')
    if json.loads(json.dumps(audit()))!=load(ROOT/'checkpoints/public-temporal-audit-2026-10-03.json'):raise ValueError('Exploratory audit changed.')
    validate(ROOT/'checkpoints/public-temporal-preparation-2026-10-04.json',ROOT/'runs/public-temporal/development-2026-10-04-v1')
    p=load(CAPACITY_PROTOCOL);r=load(CAPACITY_OUTPUT/'result.json');identifier,body=capacity_request();committed(CAPACITY_PROTOCOL)
    if sha((ROOT/'scripts/probe_public_context.py').read_bytes())!=p['source_sha256']:raise ValueError('Context probe source changed.')
    if r['protocol_sha256']!=sha(CAPACITY_PROTOCOL.read_bytes()) or load(CAPACITY_OUTPUT/'request.json')!=body or r['request_sha256']!=sha(encoded(body)) or identifier!=p['case_id']:raise ValueError('Context probe request changed.')
    normalize(r['raw_response'],body['questions']['cause']['criteria'])
    if r['status']!='accepted' or r['input_tokens']!=r['raw_response']['usage']['input_tokens'] or r['reported_input_within_declared_capacity']!=(r['input_tokens']<=p['context_tokens']):raise ValueError('Context probe result changed.')
    if {k:v for k,v in r.items() if k!='raw_response'}!=load(ROOT/'checkpoints/public-context-probe-result-2026-10-04.json'):raise ValueError('Recorded capacity assessment changed.')
    checkpoint=ROOT/'checkpoints/public-temporal-development-results-2026-10-04.json';committed(checkpoint)
    result=temporal_score()
    if result['failed_or_missing'] or result!=load(checkpoint):raise ValueError('Development assessment changed.')
    return {'status':'verified','replay_calls':180,'capacity_probe_calls':1,'development_calls':108,'development_cases':18,'new_hosted_calls':0,
        'sealed_train_ticket_cases':72,'sealed_sock_shop_reserve_cases':36}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
