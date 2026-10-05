"""Read-only paired trace inspector; reference details require explicit reveal."""
import copy
import json
from pathlib import Path
from .public_rca_stages import load, committed
from .public_trace_data_v2 import folder
from .public_trace_trial_v2 import output, result_path, score, verified_rows


class PublicTraceStudy:
    def __init__(self, root):
        self.root = Path(root)

    def verified(self):
        path = result_path('development')
        committed(path)
        verified_rows('development', complete=True)
        assessment = score('development')
        if assessment != load(path):
            raise ValueError('Trace results changed.')
        return assessment

    def overview(self):
        try:
            assessment = self.verified()
        except (OSError, ValueError, KeyError):
            return {'available': False, 'notes': ['Complete verified trace development evidence is unavailable.']}
        panels = {}
        for name, panel in assessment['datasets'].items():
            panels[name] = {k: v for k, v in panel.items() if k not in ('pairs', 'stable_fixes', 'stable_regressions')}
            panels[name]['case_ids'] = list(dict.fromkeys(p['id'] for p in panel['pairs']))
            for arm in panels[name]['arms'].values():
                for result in arm.values():
                    result.pop('outcomes', None)
        return {'available': True, 'datasets': panels, 'promotion_gate': assessment['promotion_gate'],
                'policy': assessment['policy'], 'condition': 'RE3 code faults, supplied boundaries, published injected-service references. Development results guide research; they do not measure operational reliability.'}

    def case(self, dataset, identifier, reveal=False):
        assessment = self.verified()
        if dataset not in assessment['datasets']:
            raise ValueError('Unknown application.')
        pairs = [p for p in assessment['datasets'][dataset]['pairs'] if p['id'] == identifier]
        if not pairs:
            raise ValueError('Unknown trace case.')
        packet = next(p for p in load(folder('development') / 'inputs.json') if p['id'] == identifier)
        rows = [json.loads(line) for line in (output('development') / 'responses.jsonl').read_text().splitlines()]
        outcomes = {}
        for arm, results in assessment['datasets'][dataset]['arms'].items():
            outcomes[arm] = [copy.deepcopy(r) for r in results['selective']['outcomes'] if r['id'] == identifier]
            if not reveal:
                for row in outcomes[arm]:
                    for key in ('group', 'target', 'fault', 'correct_first', 'cause_included', 'wrong_leads', 'raw_correct_first'):
                        row.pop(key)
        return {**packet, 'state': json.loads(packet['requests']['metrics']['state']),
                'dataset': dataset, 'outcomes': outcomes,
                'responses': [r for r in rows if r['case_id'] == identifier],
                'controls': load(output('development') / 'controls.json')[identifier],
                'reference': {'target': pairs[0]['target'], 'fault': pairs[0]['fault']} if reveal else None}
