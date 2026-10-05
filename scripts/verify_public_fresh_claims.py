"""Verify all thirteen evidence stages and protected-panel absence, without calls."""
import json
from triage_bench.paths import ROOT
from triage_bench.public_data import sha
from triage_bench.public_rca_stages import load, committed
from triage_bench.public_fresh_claim_data import DATA, PLAN, OLD_PLAN, INDEX, validate
from triage_bench.public_fresh_claim_trial import RESULT, verified_rows, score
from scripts.verify_public_binding import verify as previous


def protected_absence():
    import pyarrow.parquet as pq
    raw_ids = {d.name for d in ROOT.glob('runs/**/raw/*') if d.is_dir()}
    protected = [r for r in load(OLD_PLAN)['assignments'] if r['split'] == 'evaluation']
    for assignment in protected:
        aliases = {prefix + sha(assignment['source_case'].encode())[:12] for prefix in ('TRC-', 'TQA-', 'FMC-')}
        if raw_ids & aliases:
            raise ValueError('Protected cause-evaluation recording has been opened.')
    reserves = [r for r in load(ROOT / 'checkpoints/public-agreement-plan-2026-10-04.json')['assignments'] if r['split'] == 'reserve']
    if len(reserves) != 140 or any(r['id'] in raw_ids for r in reserves):
        raise ValueError('RE1 protected reserve allocation or absence changed.')
    sock_shop = [r for r in pq.read_table(INDEX).to_pylist() if r['dataset'] == 'RE3-SS']
    if not sock_shop:
        raise ValueError('Protected RE3 Sock Shop index missing.')
    if any('TRC-' + sha(r['case'].encode())[:12] in raw_ids or 'FMC-' + sha(r['case'].encode())[:12] in raw_ids for r in sock_shop):
        raise ValueError('Unallocated RE3 Sock Shop recording opened.')
    return {'cause_evaluation_cases': len(protected), 're1_reserve_cases': len(reserves), 're3_sock_shop_cases': len(sock_shop)}


def verify():
    previous()
    validate()
    rows, summary = verified_rows(complete=True)
    committed(RESULT)
    if score() != load(RESULT):
        raise ValueError('Fresh assessment changed.')
    if {arm: sum(r['arm'] == arm for r in rows) for arm in ('bound', 'scoped')} != {'bound': 27, 'scoped': 162}:
        raise ValueError('Fresh arm denominators changed.')
    packets = load(DATA / 'inputs.json')
    if len(packets) != 9 or len({p['case_id'] for p in packets}) != 9:
        raise ValueError('Fresh recording identities changed.')
    return {'status': 'verified', 'recorded_calls': len(rows), 'recorded_answers': sum(len(r['answers']) for r in rows),
        'reports': 9, 'claims': 54, 'fresh_cases_consumed': 9, 'remaining_re3_reserves': 0,
        'protected_unopened': protected_absence(), 'automatic_extraction': 'not_evaluated', 'new_hosted_calls': 0}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
