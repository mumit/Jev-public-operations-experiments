"""Read-only fresh confirmation with supplied bindings and actual call costs."""
import copy
import json
from pathlib import Path
from .public_rca_stages import load, committed
from .public_fresh_claim_data import DATA, PLAN, INDEX
from .public_fresh_claim_trial import RESULT, PROTOCOL, OUTPUT, SOURCES, score


class PublicFreshClaimStudy:
    def __init__(self, root):
        self.root = Path(root)
        self._signature = None
        self._result = None

    def verified(self):
        prerequisites = load(PLAN)['evidence_sha256']
        paths = [PLAN, PROTOCOL, RESULT, INDEX, *(self.root / n for n in prerequisites), *(self.root / n for n in SOURCES),
                 *sorted(DATA.rglob('*')), *sorted(OUTPUT.rglob('*'))]
        signature = tuple((str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in paths if p.is_file())
        if signature != self._signature:
            committed(RESULT)
            result = score()
            if result != load(RESULT):
                raise ValueError('Fresh assessment changed.')
            self._result, self._signature = result, signature
        return self._result

    def overview(self):
        try:
            result = copy.deepcopy(self.verified())
        except (OSError, ValueError, KeyError):
            return {'available': False, 'notes': ['Verified fresh confirmation is unavailable.']}
        packets = load(DATA / 'inputs.json')
        rows = [json.loads(line) for line in (OUTPUT / 'responses.jsonl').read_text().splitlines()]
        assignments = {r['id']: r for r in load(PLAN)['assignments']}
        for name, panel in result['datasets'].items():
            cards = [p for p in packets if p['dataset'] == name]
            panel['groups'] = len({assignments[p['case_id']]['group'] for p in cards})
            panel['report_choices'] = [{'id': p['id'], 'services': [o['service'] for o in p['observations']]} for p in cards]
            pairs = panel.pop('pairs')
            for value in panel['steps'].values():
                value['stable_fix_count'] = len(value.pop('stable_fixes'))
                value['stable_loss_count'] = len(value.pop('stable_losses'))
                value['round_changes'] = [{'round': n, 'fixes': sum(o['fix'] for o in pairs if o['round'] == n), 'losses': sum(o['loss'] for o in pairs if o['round'] == n)} for n in (1, 2, 3)]
            ids = {p['id'] for p in cards}
            panel['call_costs'] = []
            for arm, value in panel['arms'].items():
                value.pop('outcomes')
                for n in (1, 2, 3):
                    rr = [r for r in rows if r['card_id'] in ids and r['arm'] == arm and r['round'] == n]
                    panel['call_costs'].append({'arm': arm, 'round': n, 'calls': len(rr),
                        'input_tokens': sum(r.get('usage', {}).get('input_tokens', 0) for r in rr),
                        'summed_latency_ms': sum(r['latency_ms'] for r in rr)})
        return {'available': True, **result}

    def card(self, identifier, reveal=False):
        result = self.verified()
        packet = next(p for p in load(DATA / 'inputs.json') if p['id'] == identifier)
        outcomes = {arm: [copy.deepcopy(o) for o in value['outcomes'] if o['id'] == identifier]
                    for arm, value in result['datasets'][packet['dataset']]['arms'].items()}
        if not reveal:
            for group in outcomes.values():
                for outcome in group:
                    for key in ('reference', 'correct', 'unknown_to_decisive'):
                        outcome.pop(key)
        rows = [json.loads(line) for line in (OUTPUT / 'responses.jsonl').read_text().splitlines()]
        return {**packet, 'outcomes': outcomes, 'responses': [r for r in rows if r['card_id'] == identifier],
                'reference': next(r for r in load(DATA / 'references.json') if r['id'] == identifier) if reveal else None}
