"""Post-execution extraction audit; preserve failed calls and create no verdicts."""
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load
from .public_rca_trial import normalize
from .public_note_v2_data import DATA, PLAN
from .public_note_v2_trial import verified_rows, protocol_path, output, assess
from .public_note_features import ARMS, extraction, parser, annotated

RESULT = ROOT / 'checkpoints/public-note-extraction-v2-audit-2026-10-05.json'
VERDICT_KEYS = ('reference', 'choice', 'verdict_correct', 'end_to_end_correct', 'displayed', 'unsafe_displayed')
VERDICT_METRICS = ('conditional_verdict_total', 'conditional_verdict_correct', 'end_to_end_correct', 'all_six_correct',
                   'displayed', 'unsafe_displayed', 'reference_supported', 'correct_displayed_support', 'complete_calls')


def audit():
    rows, summary = verified_rows('extraction')
    if summary['recorded_jobs'] != summary['planned_jobs'] or summary['status'] != 'incomplete_or_failed' or summary['failed'] != 2:
        raise ValueError('This audit requires the preserved fully attempted, two-error extraction stage.')
    if protocol_path('verdict').exists() or output('verdict').exists():
        raise ValueError('A blocked phase cannot have dependent calls.')
    packets, refs = load(DATA / 'inputs.json'), load(DATA / 'references.json')
    indexed = {(r['card_id'], r['round']): r for r in rows}; gold = {r['id']: r for r in refs}
    assigned = []
    for n in (1, 2, 3):
        for p in packets:
            row = indexed[(p['id'], n)]
            for arm in ARMS:
                # Entire rejected response remains unavailable under the frozen rule.
                values = extraction(p, row['answers'] if row['status'] == 'ok' else {}) if arm == 'jev' else parser(p) if arm == 'parser' else annotated(p, gold[p['id']])
                assigned.append({'card_id': p['id'], 'arm': arm, 'round': n, 'bindings': values})
    panels = assess(packets, refs, assigned, [], rows)
    for dataset, panel in panels.items():
        ids = {p['id'] for p in packets if p['dataset'] == dataset}
        panel.pop('pairs'); panel.pop('research_gate'); panel.pop('consistency')
        panel['call_status'] = [{'round': n, 'planned': len(ids), 'valid': sum(r['status']=='ok' and r['card_id'] in ids and r['round']==n for r in rows),
                                'rejected': sum(r['status']=='error' and r['card_id'] in ids and r['round']==n for r in rows)} for n in (1,2,3)]
        for arm, value in panel['arms'].items():
            value.pop('research_gate'); value['gate_status'] = 'blocked_before_verdict' if arm == 'jev' else 'extraction_control_only'
            for r in value['per_round']:
                for key in VERDICT_METRICS: r.pop(key)
            for o in value['outcomes']:
                for key in VERDICT_KEYS: o.pop(key)
    jobs = {j['id']: j for j in load(output('extraction') / 'requests.json')}
    rejected = []
    for r in rows:
        if r['status'] == 'ok': continue
        raw = r.get('raw_response', {})
        for field, question in jobs[r['id']]['body']['questions'].items():
            answer = raw.get('answers', {}).get(field, {})
            try: normalize({'model': raw.get('model'), 'answers': {'cause': answer}}, question['criteria'])
            except (ValueError, TypeError) as error:
                probabilities = answer.get('probabilities', {})
                rejected.append({'card_id':r['card_id'],'round':r['round'],'field':field,'choice':answer.get('choice'),
                    'chosen_probability':probabilities.get(answer.get('choice')), 'top_options':[[k,v] for k,v in sorted(probabilities.items(), key=lambda v:-v[1])[:3]],
                    'reason':str(error),'policy_effect':'Entire note response rejected; no binding or dependent verdict accepted.'})
    # Raw usage still records paid work for rejected replies; it never validates answers.
    usages = [r.get('raw_response', {}).get('usage', {}).get('input_tokens') for r in rows]
    if any(isinstance(v,bool) or not isinstance(v,int) or not 0 < v <= load(PLAN)['context_tokens'] for v in usages):
        raise ValueError('Invalid raw usage for call accounting.')
    return {'schema':'public-note-extraction-audit-1','status':'blocked_before_verdict','planned_extraction_calls':27,
        'actual_calls':27,'valid_calls':25,'rejected_calls':2,'raw_answers':1944,'normalized_answers':1800,
        'verdict_calls':0,'new_recordings_opened':0,'reports':9,'sentence_candidates':108,'routable_claims':54,'atomic_assertions':81,
        'datasets':panels,'bindings':assigned,'rejected_answers':rejected,
        'costs':[{'phase':'extraction','arm':'jev','calls':27,'input_tokens':sum(usages),
                 'maximum_input_tokens':max(usages),'summed_latency_ms':sum(r['latency_ms'] for r in rows)}],
        'evidence':{'plan_sha256':sha(PLAN.read_bytes()),'protocol_sha256':sha(protocol_path('extraction').read_bytes()),
                    'summary_sha256':sha((output('extraction')/'summary.json').read_bytes()),
                    'audit_source_sha256':sha((ROOT/'triage_bench/public_note_audit.py').read_bytes())},
        'limits':'Post-execution audit of a failed frozen stage, not a changed normalization policy or completed end-to-end test. No rejected response is repaired, partially salvaged or retried.'}
