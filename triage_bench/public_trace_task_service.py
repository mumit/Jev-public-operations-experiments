"""Read-only factor comparison, with benchmark references hidden by default."""
import copy
import json
from pathlib import Path
from .public_rca_stages import load, committed
from .public_trace_task_data import folder
from .public_trace_task_trial import output, result_path, score, verified_rows, check_candidate


class PublicTraceTaskStudy:
    def __init__(self, root):
        self.root = Path(root)

    def verified(self, split):
        if split not in ('development', 'evaluation'):
            raise ValueError('Unknown task split.')
        if split == 'evaluation':
            check_candidate()
        path = result_path(split)
        committed(path)
        verified_rows(split, complete=True)
        assessment = score(split)
        if assessment != load(path):
            raise ValueError('Task results changed.')
        return assessment

    def overview(self):
        stages = {}
        for split in ('development', 'evaluation'):
            if split == 'evaluation' and not result_path(split).exists():
                continue
            try:
                assessment = self.verified(split)
            except (OSError, ValueError, KeyError):
                continue
            panels = {}
            for name, source in assessment['datasets'].items():
                panel = copy.deepcopy(source)
                panel['case_ids'] = list(dict.fromkeys(p['id'] for p in source['comparisons']['traces__trace_deltas']['pairs']))
                panel['comparisons'] = {k: {'baseline': v['baseline'], 'candidate': v['candidate'],
                                          'stable_fix_count': len(v['stable_fixes']),
                                          'stable_regression_count': len(v['stable_regressions'])}
                                        for k, v in source['comparisons'].items()}
                for arm in panel['arms'].values():
                    for value in arm.values():
                        value.pop('outcomes', None)
                panels[name] = panel
            stages[split] = {'datasets': panels, 'promotion_gate': assessment['promotion_gate']}
        if not stages:
            return {'available': False, 'notes': ['Complete verified trace-task evidence is unavailable.']}
        return {'available': True, 'stages': stages, 'primary': 'trace_deltas', 'policy': {'threshold': .7, 'margin': 0., 'maximum_leads': 1},
                'evaluation_recorded': 'evaluation' in stages,
                'condition': 'Fresh RE3 code-fault groups, supplied boundaries and published injected-service references. Rounds repeat cases, not independent incidents.'}

    def case(self, split, dataset, identifier, reveal=False):
        assessment = self.verified(split)
        if dataset not in assessment['datasets']:
            raise ValueError('Unknown task application.')
        source = assessment['datasets'][dataset]
        pairs = [p for p in source['comparisons']['traces__trace_deltas']['pairs'] if p['id'] == identifier]
        if not pairs:
            raise ValueError('Unknown task case.')
        packet = next(p for p in load(folder(split) / 'inputs.json') if p['id'] == identifier)
        rows = [json.loads(line) for line in (output(split) / 'responses.jsonl').read_text().splitlines()]
        outcomes = {}
        for arm, results in source['arms'].items():
            outcomes[arm] = [copy.deepcopy(r) for r in results['selective']['outcomes'] if r['id'] == identifier]
            if not reveal:
                for row in outcomes[arm]:
                    for key in ('group', 'target', 'fault', 'correct_first', 'cause_included', 'wrong_leads', 'raw_correct_first'):
                        row.pop(key)
        request = packet['requests'].get('metrics', packet['requests']['traces'])
        state = json.loads(request['state'])
        state.pop('trace_context', None)
        return {**packet, 'state': state, 'split': split, 'dataset': dataset, 'outcomes': outcomes,
                'responses': [r for r in rows if r['case_id'] == identifier],
                'controls': load(output(split) / 'controls.json')[identifier],
                'reference': {'target': pairs[0]['target'], 'fault': pairs[0]['fault']} if reveal else None}
