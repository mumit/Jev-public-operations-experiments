"""Reconstruct the trace audit, sizing attempts and paired evidence without model calls."""
import json
from triage_bench.paths import ROOT
from triage_bench.public_rca_stages import load, committed
from triage_bench import public_trace_data as original
from triage_bench import public_trace_data_v2 as data
from triage_bench import public_trace_trial_v2 as trial
from triage_bench.public_trace_wire import expand


def verify():
    original.verify_audit()
    first = original.validate('development')
    preflight = ROOT / 'checkpoints/public-traces-sizing-2026-10-04.json'
    committed(preflight)
    if load(preflight)['manifest'] != first or first['fits_empirical_wire_cap']:
        raise ValueError('Preserve the failed pre-inference sizing attempt.')
    if any(original.BASE.glob('*-hosted-2026-10-04-v1')):
        raise ValueError('The oversized protocol must have no model calls.')
    plan = data.check_plan()
    baseline = {p['id']: p for p in load(original.folder('development') / 'inputs.json')}
    for packet in load(data.folder('development') / 'inputs.json'):
        old = baseline[packet['id']]
        state = json.loads(packet['requests']['traces']['state'])
        if packet['trace_context'] != old['trace_context'] or expand(state['trace_context']) != old['trace_context']:
            raise ValueError('Trace table encoding lost observations or definitions.')
        if packet['requests']['metrics'] != old['requests']['metrics']:
            raise ValueError('Compact trace encoding changed metric-only requests.')
    stages = ['development']
    development = trial.result_path('development')
    committed(development)
    if trial.score('development') != load(development):
        raise ValueError('Development assessment changed.')
    if trial.CANDIDATE.exists():
        trial.check_candidate()
        if trial.result_path('evaluation').exists():
            stages.append('evaluation')
    elif data.folder('evaluation').exists() or trial.protocol_path('evaluation').exists():
        raise ValueError('Evaluation opened without promotion.')
    calls = 0
    for stage in stages:
        data.validate(stage)
        rows, _ = trial.verified_rows(stage, complete=True)
        result = trial.result_path(stage)
        committed(result)
        if trial.score(stage) != load(result):
            raise ValueError('Paired assessment changed.')
        calls += len(rows)
    sealed = {r['id'] for r in plan['assignments'] if r['split'] == 'reserve'}
    if any(p.name in sealed for p in data.BASE.rglob('*') if p.is_dir()):
        raise ValueError('Trace reserve entered the experiment.')
    return {'status': 'verified', 'recorded_calls': calls, 'stages': stages,
            'audit_cases': 7, 'development_cases': 13, 'reserved_re3_cases_at_stage_completion': 25,
            'evaluation_sealed': not trial.CANDIDATE.exists(), 'new_hosted_calls': 0}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
