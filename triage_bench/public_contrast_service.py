"""Read-only, fingerprint-verified inspection of extraction-contrast evidence."""
import copy
import json
from pathlib import Path
from .public_rca_stages import committed, load
from .public_note_v2_data import DATA, INDEX, PREVIOUS_DATA
from .public_contrast_trial import PLAN, RESULT, SOURCES, protocol_path, output, score


class PublicContrastStudy:
    def __init__(self, root):
        self.root = Path(root); self._signature = None; self._result = None

    def verified(self):
        paths = [PLAN, RESULT, INDEX, *(protocol_path(phase) for phase in ('extraction', 'verdict')),
            *(self.root / n for n in SOURCES), *(self.root / n for n in load(PLAN)['evidence_sha256']),
            *DATA.rglob('*'), *PREVIOUS_DATA.rglob('*'),
            *(p for phase in ('extraction', 'verdict') for p in output(phase).rglob('*'))]
        signature = tuple((str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in paths if p.is_file())
        if signature != self._signature:
            committed(RESULT); result = score()
            if result != load(RESULT):
                raise ValueError('Sentence-review results changed.')
            self._signature, self._result = signature, result
        return self._result

    def overview(self):
        try:
            result = copy.deepcopy(self.verified())
        except (OSError, ValueError, KeyError):
            return {'available': False, 'notes': ['Verified extraction-contrast evidence is unavailable. Restore all sixteen public assets.']}
        packets = load(DATA / 'inputs.json')
        for dataset, panel in result['datasets'].items():
            panel['report_choices'] = [{'id': p['id']} for p in packets if p['dataset'] == dataset]
            for comparison in panel['comparisons']: comparison.pop('pairs')
            for value in panel['arms'].values(): value.pop('outcomes')
        result.pop('bindings')
        return {'available': True, **result}

    def card(self, identifier, reveal=False):
        result = self.verified()
        packet = next(p for p in load(DATA / 'inputs.json') if p['id'] == identifier)
        panel = result['datasets'][packet['dataset']]
        outcomes = {arm: [copy.deepcopy(o) for o in value['outcomes'] if o['id'] == identifier] for arm, value in panel['arms'].items()}
        if not reveal:
            for group in outcomes.values():
                for o in group:
                    for key in ('category', 'actionable', 'gold_role', 'assertion_gold', 'gold_service', 'role_correct', 'service_correct',
                                'meaning_correct', 'binding_correct', 'reference', 'verdict_correct', 'end_to_end_correct', 'unsafe_displayed'):
                        o.pop(key, None)
        responses, jobs = [], []
        for phase in ('extraction', 'verdict'):
            responses += [json.loads(line) for line in (output(phase) / 'responses.jsonl').read_text().splitlines() if json.loads(line)['card_id'] == identifier]
            jobs += [r for r in load(output(phase) / 'requests.json') if r['card_id'] == identifier]
        return {**packet, 'bindings': [b for b in result['bindings'] if b['card_id'] == identifier],
            'outcomes': outcomes, 'responses': responses, 'jobs': jobs,
            'reference': next(r for r in load(DATA / 'references.json') if r['id'] == identifier) if reveal else None}
