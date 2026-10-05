"""Verify task wording, arithmetic, fresh groups and recorded calls without inference."""
import json
from triage_bench.paths import ROOT
from triage_bench.public_rca_stages import load, committed
from triage_bench.public_trace_task_data import PLAN, BASE, folder, check_plan, validate
from triage_bench import public_trace_task_trial as trial
from triage_bench.public_trace_task_features import requests as build
from scripts.verify_public_traces import verify as verify_previous


def verify():
    verify_previous()
    plan = check_plan()
    stages = ['development']
    if trial.CANDIDATE.exists():
        trial.check_candidate()
        if trial.result_path('evaluation').exists():
            stages.append('evaluation')
    elif folder('evaluation').exists() or trial.protocol_path('evaluation').exists():
        raise ValueError('Task evaluation opened without promotion.')
    calls = 0
    for split in stages:
        validate(split)
        rows, _ = trial.verified_rows(split, complete=True)
        committed(trial.result_path(split))
        if trial.score(split) != load(trial.result_path(split)):
            raise ValueError('Task assessment changed.')
        for packet in load(folder(split) / 'inputs.json'):
            actual = build(packet['state'], packet['trace_context'], packet['trace_changes'])
            if packet['requests'] != {a: actual[a] for a in packet['requests']}:
                raise ValueError('Task factor reconstruction changed.')
        calls += len(rows)
    sealed = [r for r in plan['assignments'] if r['split'] == 'reserve']
    if len(sealed) != 9 or any(p.name == r['id'] for r in sealed for p in BASE.rglob('*') if p.is_dir()):
        raise ValueError('Task reserve entered this study.')
    previous = load(ROOT / 'checkpoints/public-traces-v2-plan-2026-10-04.json')['assignments']
    for row in sealed:
        old = next(r for r in previous if r['source_case'] == row['source_case'])
        if any(p.name == old['id'] for p in (ROOT / 'runs/public-traces').rglob('*') if p.is_dir()):
            raise ValueError('Remaining reserve entered the earlier trace study.')
    if not trial.CANDIDATE.exists():
        evaluation = {r['id'] for r in plan['assignments'] if r['split'] == 'evaluation'}
        if any(p.name in evaluation for p in BASE.rglob('*') if p.is_dir()):
            raise ValueError('Protected evaluation leaked into task development.')
    return {'status': 'verified', 'recorded_calls': calls, 'stages': stages,
            'development_cases': 16, 'remaining_re3_reserves': 9,
            'evaluation_sealed': not trial.CANDIDATE.exists(), 'new_hosted_calls': 0}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
