"""Once-only 2x2 extraction-definition diagnostic and dependent verdicts."""
import json
import time
import urllib.error
import urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load, committed
from .profile import MODEL, profile_check
from .hosted import encoded, redact
from .runner import NoRedirect, clean_api_key
from .public_note_v2_data import DATA, validate
from .public_sentence_trial import SOURCES as PREVIOUS_SOURCES, RESULT as PREVIOUS_RESULT
from .public_note_features import DIMENSIONS, semantics, verdict_request
from .public_sentence_features import extract, validate_reply, GlobalReplyError
from .public_contrast_features import ARMS, extraction_request, validate_changes, ROLE, MEANING

PLAN = ROOT / 'checkpoints/public-extraction-contrast-plan-2026-10-05.json'
BASE = ROOT / 'runs/public-extraction-contrast'
RESULT = ROOT / 'checkpoints/public-extraction-contrast-results-2026-10-05.json'
SOURCES = PREVIOUS_SOURCES + ('triage_bench/public_contrast_features.py',
    'triage_bench/public_contrast_trial.py', 'scripts/run_public_extraction_contrast.py')


def protocol_path(phase):
    if phase not in ('extraction', 'verdict'):
        raise ValueError('Unknown contrast phase.')
    return ROOT / ('checkpoints/public-contrast-' + phase + '-protocol-2026-10-05.json')


def output(phase):
    protocol_path(phase)
    return BASE / (phase + '-hosted-2026-10-05-v1')


def plan(profile):
    from scripts.verify_public_sentence_review import verify
    profile_check(profile); verify()
    previous = load(ROOT / 'checkpoints/public-sentence-review-plan-2026-10-05.json')
    if any(profile[k] != previous[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Keep the recorded profile.')
    record = {'schema': 'public-extraction-contrast-plan-1',
        'decision': 'User authorized clearer speech-act and meaning definitions on 2026-10-05.',
        'model': MODEL, 'endpoint': profile['endpoint'], 'context_tokens': profile['context_tokens'],
        'maximum_request_bytes': 79840, 'reports': 9, 'candidates': 108, 'actionable_claims': 54,
        'rounds': 3, 'arms': list(ARMS), 'candidate': 'combined', 'maximum_calls': 216, 'maximum_answers': 9072,
        'allocation': 'All nine inspected notes and recordings, unchanged references, sentence boundaries, inventories and observations. Six routable versus nine atomic assertions per note. No downloads, new telemetry or protected panels.',
        'treatments': '2x2 definition changes: baseline exactly replays v2; role changes only the shared role definition; meaning changes only the shared kind definition; combined changes both. Questions, criteria, other definitions, notes and option keys remain byte-equivalent. Every question sees shared state, so effects can appear in other dimensions too. Contrasts contain generic labeled speech-act/family examples, not case annotations or telemetry verdict examples. This clarifies existing bounded-policy annotations; eligibility plus its numeric condition is one policy assertion here, not unrestricted atomic decomposition.',
        'definitions': {'role': ROLE, 'kind': MEANING},
        'comparison': 'Fresh contemporaneous baseline in three rounds; never pool it with historical baseline. Compare each changed arm with baseline and combined with each single change. Measure binding and end-to-end gains/losses by sentence, probability-boundary crossings, role/service/meaning errors and whole-six note coverage. Parser and supplied-annotation results from sentence review are labeled historical context, verified but not rerun or counted as current calls. Earlier fitted ML predicts injected origin, a different target, and remains unscored.',
        'failure_handling': previous['failure_handling'],
        'acceptance': 'Frozen sentence-level quarantine and strict Choice normalization. Require one mapped assertion, unique observed service, mapped polarity and relevant channel/measure, with every required probability >=0.70. All fields must validate, including unused dimensions. Verdict display also requires >=0.70. No threshold search or repairs.',
        'verdict': previous['verdict'],
        'execution': 'Commit producers and plan before freezing exact extraction hashes and unchanged reference fingerprints. Run once: 108 extraction calls (nine notes, four arms, three cyclic rounds). Freeze actual per-arm bindings, extraction summary and dependent request hashes before at most 108 verdict calls. Rotate all four arm orders by note/round. Maximum 7776 extraction answers plus 1296 verdict answers; no accepted sentences yields an explicit skip with no invented reply. Stop on HTTP/network/model/global envelope/usage/context errors or three consecutive other malformed replies. No retries, warmups, input edits or candidate substitution after results.',
        'scoring': previous['scoring'],
        'research_gate': 'Combined is the only candidate. Each application and every round must pass the inherited absolute role/service/meaning/accepted/end-to-end >=90%, all-six notes >=90%, complete-call, no accepted review-only/nonclaim, no unsafe display and >=half supported-display checks. Also require zero accepted wrong bindings, complete baseline calls, and no lower role, service, meaning, accepted-correct or end-to-end count than its fresh baseline in each round. Role-only and meaning-only are diagnostic; a better result cannot replace combined after inspection. Show fixes and regressions even when totals tie. Passing unlocks no protected data.',
        'limits': 'Definitions designed after inspecting earlier failures. Controlled notes, assistant annotations, only three fault groups, inspected telemetry, bounded taxonomy and unknown public pretraining exposure. Not an independent/authentic report test, specialist review, causal diagnosis or operational error estimate. A favorable fresh replay is still development, not fresh-data generalization.',
        'source_sha256': {n: sha((ROOT / n).read_bytes()) for n in SOURCES},
        'evidence_sha256': {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in
            [PREVIOUS_RESULT, ROOT / 'checkpoints/public-sentence-review-plan-2026-10-05.json',
             *(DATA / n for n in ('inputs.json', 'references.json', 'manifest.json'))]}}
    with PLAN.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    return {'status': 'frozen', 'maximum_calls': 216, 'new_telemetry_opened': 0}


def check_plan():
    committed(PLAN); p = load(PLAN)
    if (p['schema'], p['maximum_calls'], p['candidate']) != ('public-extraction-contrast-plan-1', 216, 'combined'):
        raise ValueError('Contrast plan identity changed.')
    for mapping in ('source_sha256', 'evidence_sha256'):
        for name, digest in p[mapping].items():
            if sha((ROOT / name).read_bytes()) != digest:
                raise ValueError('Contrast source or prerequisite changed.')
    return p


def bindings():
    rows, _ = verified_rows('extraction', complete=True)
    indexed = {(r['card_id'], r['arm'], r['round']): r for r in rows}
    return [{'card_id': p['id'], 'arm': arm, 'round': n,
             'bindings': extract(p, indexed[(p['id'], arm, n)])}
        for n in (1, 2, 3) for p in load(DATA / 'inputs.json') for arm in ARMS]


def requests(phase):
    manifest = validate()
    if not manifest['fits_request_cap']:
        raise ValueError('Historical note sizing changed.')
    packets = load(DATA / 'inputs.json')
    for packet in packets: validate_changes(packet)
    assigned = {(r['card_id'], r['arm'], r['round']): r['bindings'] for r in bindings()} if phase == 'verdict' else {}
    result = []
    for n in (1, 2, 3):
        offset = n - 1
        for i, packet in enumerate(packets[offset:] + packets[:offset]):
            start = (i + offset) % len(ARMS)
            for arm in ARMS[start:] + ARMS[:start]:
                body = extraction_request(packet, arm) if phase == 'extraction' else verdict_request(packet, assigned[(packet['id'], arm, n)])
                result.append({'id': packet['id'] + '::contrast::' + phase + '::' + arm + '::r' + str(n),
                    'card_id': packet['id'], 'phase': phase, 'arm': arm, 'round': n,
                    'request_sha256': sha(encoded(body)) if body else None, 'body': body})
    if phase not in ('extraction', 'verdict') or len(result) != 108:
        raise ValueError('Contrast job budget changed.')
    return result


def freeze(phase):
    p = check_plan(); path = protocol_path(phase)
    if path.exists():
        raise ValueError('Note phase already frozen.')
    planned = requests(phase)
    largest = max((len(encoded(r['body'])) for r in planned if r['body']), default=0)
    if largest > p['maximum_request_bytes']:
        raise ValueError('Dependent wire cap exceeded; no calls authorized.')
    record = {'schema': 'public-extraction-contrast-protocol-1', 'phase': phase, 'plan_sha256': sha(PLAN.read_bytes()),
        'manifest_sha256': sha((DATA / 'manifest.json').read_bytes()), 'reference_sha256': sha((DATA / 'references.json').read_bytes()),
        'planned_jobs': len(planned), 'planned_calls': sum(bool(r['body']) for r in planned),
        'planned_answers': sum(len(r['body']['questions']) for r in planned if r['body']), 'largest_request_bytes': largest,
        'requests': [{k: v for k, v in r.items() if k != 'body'} for r in planned]}
    if phase == 'verdict':
        record.update(extraction_summary_sha256=sha((output('extraction') / 'summary.json').read_bytes()), bindings=bindings())
    with path.open('x') as f:
        f.write(json.dumps(record, indent=2) + '\n')
    return {k: v for k, v in record.items() if k not in ('requests', 'bindings')}


def check(phase):
    p = check_plan(); path = protocol_path(phase); committed(path)
    protocol = load(path); planned = requests(phase)
    if protocol['schema'] != 'public-extraction-contrast-protocol-1' or protocol['phase'] != phase or protocol['plan_sha256'] != sha(PLAN.read_bytes()) or protocol['manifest_sha256'] != sha((DATA / 'manifest.json').read_bytes()) or protocol['reference_sha256'] != sha((DATA / 'references.json').read_bytes()):
        raise ValueError('Note phase preparation changed.')
    if protocol['requests'] != [{k: v for k, v in r.items() if k != 'body'} for r in planned]:
        raise ValueError('Note exact requests changed.')
    largest = max((len(encoded(r['body'])) for r in planned if r['body']), default=0)
    if (protocol['planned_jobs'], protocol['planned_calls'], protocol['planned_answers'], protocol['largest_request_bytes']) != (len(planned), sum(bool(r['body']) for r in planned), sum(len(r['body']['questions']) for r in planned if r['body']), largest) or largest > p['maximum_request_bytes']:
        raise ValueError('Note sizing/denominators changed.')
    if phase == 'verdict' and (protocol['bindings'] != bindings() or protocol['extraction_summary_sha256'] != sha((output('extraction') / 'summary.json').read_bytes())):
        raise ValueError('Dependent extraction bindings changed.')
    return p, planned


def run(phase, profile):
    p, planned = check(phase); profile_check(profile)
    if any(profile[k] != p[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Note profile changed.')
    key = clean_api_key(profile.get('api_key', ''))
    if not key:
        raise ValueError('Server-side key required.')
    destination = output(phase); destination.parent.mkdir(parents=True, exist_ok=True); destination.mkdir()
    (destination / 'requests.json').write_text(json.dumps(planned, indent=2) + '\n')
    rows, reason, consecutive = [], None, 0
    opener = urllib.request.build_opener(NoRedirect())
    with (destination / 'responses.jsonl').open('x') as stream:
        for req in planned:
            row = {k: v for k, v in req.items() if k != 'body'}
            row['status'] = 'ok' if req['body'] else 'skipped_no_accepted_claims'
            start = time.perf_counter()
            if req['body']:
                try:
                    wire = urllib.request.Request(profile['endpoint'], data=encoded(req['body']), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key}, method='POST')
                    with opener.open(wire, timeout=30) as response:
                        content = response.read(1048577)
                    if len(content) > 1048576:
                        raise ValueError('Oversized provider response.')
                    raw = json.loads(content); row['raw_response'] = redact(raw, key)
                    if not isinstance(raw, dict) or raw.get('model') != MODEL:
                        reason = 'checkpoint_mismatch'; raise ValueError('Wrong model.')
                    row.update(validate_reply(raw, req['body'], p['context_tokens']))
                    tokens = row['usage'].get('input_tokens')
                    if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 1:
                        raise ValueError('Missing usage.')
                    if tokens > p['context_tokens']:
                        reason = 'reported_context_overflow'; raise ValueError('Context overflow.')
                except GlobalReplyError as error:
                    row.update(status='error', error=str(error)); reason = str(error)
                except urllib.error.HTTPError as error:
                    row.update(status='error', error='Provider HTTP ' + str(error.code)); reason = 'provider_http_' + str(error.code)
                except (OSError, ValueError, KeyError, TypeError) as error:
                    row.update(status='error', error='Validation or request failure: ' + type(error).__name__)
                    if isinstance(error, OSError):
                        reason = 'network_error'
            row = redact(row, key); row['latency_ms'] = (time.perf_counter() - start) * 1000 if req['body'] else 0
            rows.append(row); stream.write(json.dumps(row) + '\n'); stream.flush()
            print(f"Contrast {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'public-extraction-contrast-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
        'planned_calls': sum(bool(r['body']) for r in planned), 'recorded_jobs': len(rows),
        'attempted_calls': sum(r['status'] != 'skipped_no_accepted_claims' for r in rows),
        'failed': sum(r['status'] == 'error' for r in rows), 'unattempted_jobs': len(planned) - len(rows),
        'status': 'completed' if len(rows) == len(planned) and all(r['status'] != 'error' for r in rows) else 'incomplete_or_failed',
        'stopped_reason': reason, 'protocol_sha256': sha(protocol_path(phase).read_bytes()),
        'files': {n: sha((destination / n).read_bytes()) for n in ('requests.json', 'responses.jsonl')}}
    (destination / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def verified_rows(phase, complete=False):
    p, planned = check(phase); dest = output(phase); summary = load(dest / 'summary.json')
    if summary['schema'] != 'public-extraction-contrast-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
        raise ValueError('Note hosted identity changed.')
    for name, digest in summary['files'].items():
        if sha((dest / name).read_bytes()) != digest:
            raise ValueError('Note hosted bytes changed.')
    if load(dest / 'requests.json') != planned:
        raise ValueError('Note saved requests changed.')
    rows = [json.loads(line) for line in (dest / 'responses.jsonl').read_text().splitlines()]
    if len(rows) > len(planned):
        raise ValueError('Extra note jobs.')
    for row, req in zip(rows, planned):
        if any(row.get(k) != v for k, v in req.items() if k != 'body') or row['status'] not in ('ok', 'ok_with_review', 'error', 'skipped_no_accepted_claims'):
            raise ValueError('Note response identity changed.')
        if bool(req['body']) == (row['status'] == 'skipped_no_accepted_claims'):
            raise ValueError('Skip does not match zero accepted claims.')
        if row['status'] == 'skipped_no_accepted_claims' and any(k in row for k in ('answers', 'raw_response', 'usage')):
            raise ValueError('Application skip fabricated provider evidence.')
        if row['status'] in ('ok', 'ok_with_review'):
            validated = validate_reply(row['raw_response'], req['body'], p['context_tokens'])
            if any(row.get(k) != v for k, v in validated.items()):
                raise ValueError('Sentence normalized reply changed.')
    status = 'completed' if len(rows) == len(planned) and not any(r['status'] == 'error' for r in rows) else 'incomplete_or_failed'
    if (summary['planned_jobs'], summary['planned_calls'], summary['recorded_jobs'], summary['attempted_calls'], summary['failed'], summary['unattempted_jobs'], summary['status']) != (len(planned), sum(bool(r['body']) for r in planned), len(rows), sum(r['status'] != 'skipped_no_accepted_claims' for r in rows), sum(r['status'] == 'error' for r in rows), len(planned) - len(rows), status):
        raise ValueError('Note hosted denominators changed.')
    if complete and (status != 'completed' or summary['stopped_reason']):
        raise ValueError('Complete note evidence required.')
    return rows, summary

def core_assess(packets, references, assigned, verdict_rows, extraction_rows):
    refs = {r['id']: r for r in references}
    bound = {(r['card_id'], r['arm'], r['round']): r['bindings'] for r in assigned}
    verdicts = {(r['card_id'], r['arm'], r['round']): r for r in verdict_rows}
    extracted = {(r['card_id'], r['arm'], r['round']): r for r in extraction_rows}
    datasets = {}
    for dataset in sorted({p['dataset'] for p in packets}):
        cards = [p for p in packets if p['dataset'] == dataset]; arms = {}
        for arm in ARMS:
            outcomes, rounds = [], []
            for n in (1, 2, 3):
                complete = True
                for packet in cards:
                    bindings_for_note = bound.get((packet['id'], arm, n), {})
                    vr = verdicts.get((packet['id'], arm, n))
                    er = extracted.get((packet['id'], arm, n))
                    if not vr or vr['status'] == 'error' or (not er or er['status'] != 'ok'):
                        complete = False
                    gold_by_span = {(a['start'], a['end']): a for a in refs[packet['id']]['annotations']}
                    # Gold spans retain the denominator even if a future boundary miss occurs.
                    for c in refs[packet['id']]['annotations']:
                        candidate = next((v for v in packet['candidates'] if (v['start'], v['end']) == (c['start'], c['end'])), None)
                        predicted = bindings_for_note.get(candidate['id'], {}) if candidate else {}
                        va = vr.get('answers', {}).get(c['id'] + '_verdict') if vr and vr['status'] == 'ok' else None
                        accepted = bool(predicted.get('accepted'))
                        service_correct = predicted.get('service') == c['service']
                        meaning_correct = semantics(predicted) == semantics(c)
                        binding_correct = predicted.get('role') == 'assertion' and service_correct and meaning_correct
                        verdict_correct = bool(va and va['choice'] == c.get('verdict'))
                        end_correct = c['actionable'] and accepted and binding_correct and verdict_correct
                        displayed = bool(accepted and va and va['probabilities'][va['choice']] >= .70)
                        outcomes.append({'id': packet['id'], 'sentence': c['id'], 'round': n, 'category': c['category'],
                            'actionable': c['actionable'], 'candidate_found': candidate is not None,
                            'gold_role': c['role'], 'role': predicted.get('role', 'unavailable'),
                            'role_correct': predicted.get('role') == c['role'], 'assertion_gold': c['role'] == 'assertion',
                            'service': predicted.get('service', 'unavailable'), 'gold_service': c['service'],
                            'service_correct': service_correct, 'meaning_correct': meaning_correct, 'binding_correct': binding_correct,
                            'accepted': accepted, 'review_reason': predicted.get('review_reason', 'missing'),
                            'choice': va['choice'] if va else 'unavailable', 'reference': c.get('verdict'),
                            'verdict_correct': verdict_correct, 'end_to_end_correct': bool(end_correct),
                            'displayed': displayed, 'unsafe_displayed': displayed and not end_correct})
                    extra = [v for v in packet['candidates'] if (v['start'], v['end']) not in gold_by_span]
                    if extra:
                        raise ValueError('Unannotated candidate: explicit extra-prediction scoring required.')
                rr = [o for o in outcomes if o['round'] == n]; actionable = [o for o in rr if o['actionable']]
                supported = [o for o in actionable if o['reference'] == 'supported']
                gold_assertions = sum(o['assertion_gold'] for o in rr)
                predictions = sum(o['role'] == 'assertion' for o in rr)
                tp = sum(o['assertion_gold'] and o['role'] == 'assertion' for o in rr)
                conditional = [o for o in actionable if o['accepted'] and o['binding_correct'] and o['choice'] != 'unavailable']
                rounds.append({'round': n, 'reports': len(cards), 'sentence_candidates': len(rr), 'candidate_found': sum(o['candidate_found'] for o in rr),
                    'role_correct': sum(o['role_correct'] for o in rr), 'gold_single_assertions': gold_assertions,
                    'predicted_single_assertions': predictions, 'true_positive_assertions': tp,
                    'assertion_precision': tp / predictions if predictions else None, 'assertion_recall': tp / gold_assertions,
                    'routable_claims': len(actionable), 'service_correct': sum(o['service_correct'] for o in actionable),
                    'meaning_correct': sum(o['meaning_correct'] for o in actionable),
                    'accepted_correct_bindings': sum(o['accepted'] and o['binding_correct'] for o in actionable),
                    'accepted_wrong_bindings': sum(o['accepted'] and not o['binding_correct'] for o in actionable),
                    'accepted_review_or_nonclaims': sum(o['accepted'] and not o['actionable'] for o in rr),
                    'withheld_routable_claims': sum(not o['accepted'] for o in actionable),
                    'ambiguous_subject_resolved_as_ambiguous': sum(o['category'] == 'ambiguous' and o['service'] == 'ambiguous' for o in rr),
                    'review_only_candidates': sum(not o['actionable'] and o['gold_role'] != 'non_assertion' for o in rr),
                    'atomic_assertions_in_notes': len(cards) * 9,
                    'conditional_verdict_total': len(conditional), 'conditional_verdict_correct': sum(o['verdict_correct'] for o in conditional),
                    'end_to_end_correct': sum(o['end_to_end_correct'] for o in actionable),
                    'all_six_correct': sum(all(o['end_to_end_correct'] for o in actionable if o['id'] == p['id']) for p in cards),
                    'displayed': sum(o['displayed'] for o in rr), 'unsafe_displayed': sum(o['unsafe_displayed'] for o in rr),
                    'reference_supported': len(supported), 'correct_displayed_support': sum(o['end_to_end_correct'] and o['displayed'] for o in supported),
                    'complete_calls': complete})
            passed = all(r['complete_calls'] and r['role_correct'] / r['sentence_candidates'] >= .9
                and r['service_correct'] / r['routable_claims'] >= .9 and r['meaning_correct'] / r['routable_claims'] >= .9
                and r['accepted_correct_bindings'] / r['routable_claims'] >= .9 and not r['accepted_review_or_nonclaims']
                and r['end_to_end_correct'] / r['routable_claims'] >= .9 and r['all_six_correct'] / r['reports'] >= .9
                and not r['unsafe_displayed'] and r['reference_supported'] > 0 and r['correct_displayed_support'] >= r['reference_supported'] / 2 for r in rounds)
            arms[arm] = {'per_round': rounds, 'outcomes': outcomes,
                         'research_gate': passed,
                         'gate_status': 'passed' if passed else 'failed'}
        datasets[dataset] = {'reports': len(cards), 'routable_claims': len(cards) * 6,
            'atomic_assertions_in_notes': len(cards) * 9, 'groups': 1 if dataset == 'Train Ticket' else 2,
            'arms': arms, 'research_gate': arms['combined']['research_gate'],
            'consistency': {arm: {key: sum(len({o[key] for o in value['outcomes'] if o['id'] == p['id'] and o['sentence'] == c['id']}) == 1
                for p in cards for c in refs[p['id']]['annotations']) for key in ('role', 'service', 'accepted', 'choice', 'displayed')} for arm, value in arms.items()}}
    return datasets


def assess(packets, references, assigned, verdict_rows, extraction_rows):
    def completed_rows(rows):
        return [{**r, 'status': 'ok' if r['status'] == 'ok_with_review' else r['status']} for r in rows]
    panels = core_assess(packets, references, assigned, completed_rows(verdict_rows), completed_rows(extraction_rows))
    for dataset, panel in panels.items():
        arms = panel['arms']; comparisons = []
        for control, candidate in (('baseline', 'role'), ('baseline', 'meaning'), ('baseline', 'combined'), ('role', 'combined'), ('meaning', 'combined')):
            paired = []
            for before, after in zip(arms[control]['outcomes'], arms[candidate]['outcomes']):
                if (before['id'], before['sentence'], before['round']) != (after['id'], after['sentence'], after['round']):
                    raise ValueError('Unmatched contrast outcomes.')
                if before['actionable']:
                    paired.append({'id': before['id'], 'sentence': before['sentence'], 'round': before['round'],
                        'binding_gain': after['accepted'] and after['binding_correct'] and not (before['accepted'] and before['binding_correct']),
                        'binding_loss': before['accepted'] and before['binding_correct'] and not (after['accepted'] and after['binding_correct']),
                        'end_to_end_gain': after['end_to_end_correct'] and not before['end_to_end_correct'],
                        'end_to_end_loss': before['end_to_end_correct'] and not after['end_to_end_correct'],
                        'new_wrong_binding': after['accepted'] and not after['binding_correct'] and not (before['accepted'] and not before['binding_correct'])})
            comparisons.append({'control': control, 'candidate': candidate,
                'per_round': [{'round': n, **{key: sum(p[key] for p in paired if p['round'] == n) for key in
                    ('binding_gain', 'binding_loss', 'end_to_end_gain', 'end_to_end_loss', 'new_wrong_binding')}} for n in (1, 2, 3)],
                'pairs': paired})
        baseline = arms['baseline']['per_round']; combined = arms['combined']['per_round']
        noninferior = all(b['complete_calls'] and not c['accepted_wrong_bindings'] and
            all(c[key] >= b[key] for key in ('role_correct', 'service_correct', 'meaning_correct', 'accepted_correct_bindings', 'end_to_end_correct'))
            for b, c in zip(baseline, combined))
        panel['research_gate'] = arms['combined']['research_gate'] and noninferior
        panel['candidate_gate'] = {'candidate': 'combined', 'absolute_pass': arms['combined']['research_gate'],
            'baseline_comparison_pass': noninferior, 'passed': panel['research_gate']}
        panel['comparisons'] = comparisons
        for arm, value in arms.items():
            value['gate_status'] = ('passed' if panel['research_gate'] else 'failed') if arm == 'combined' else 'diagnostic_not_candidate'
        ids = {p['id'] for p in packets if p['dataset'] == dataset}
        panel['validation'] = [{'phase': phase, 'arm': arm, 'round': n,
            'globally_valid_replies': sum(r['status'] in ('ok', 'ok_with_review') for r in selected),
            'replies_with_review': sum(r['status'] == 'ok_with_review' for r in selected),
            'invalid_fields': sum(len(r.get('field_errors', {})) for r in selected),
            'quarantined_sentences': sum(len(r.get('quarantined_sentences', [])) for r in selected)}
            for phase, rows in [('extraction', extraction_rows), ('verdict', verdict_rows)] for arm in ARMS for n in (1, 2, 3)
            for selected in [[r for r in rows if r['card_id'] in ids and r['arm'] == arm and r['round'] == n]]]
    return panels


def score():
    erows, es = verified_rows('extraction'); vrows, vs = verified_rows('verdict')
    assigned = load(protocol_path('verdict'))['bindings']
    datasets = assess(load(DATA / 'inputs.json'), load(DATA / 'references.json'), assigned, vrows, erows)
    costs = [{'phase': phase, 'arm': arm, 'calls': len(rr),
        'input_tokens': sum(r.get('usage', r.get('raw_response', {}).get('usage', {})).get('input_tokens', 0) for r in rr),
        'summed_latency_ms': sum(r['latency_ms'] for r in rr)}
        for phase, rows in [('extraction', erows), ('verdict', vrows)] for arm in ARMS
        for rr in [[r for r in rows if r['arm'] == arm and r['status'] != 'skipped_no_accepted_claims']]]
    return {'schema': 'public-extraction-contrast-results-1', 'reports': 9, 'sentence_candidates': 108,
        'routable_claims': 54, 'atomic_assertions_in_notes': 81, 'new_recordings_opened': 0,
        'candidate': 'combined', 'actual_calls': es['attempted_calls'] + vs['attempted_calls'],
        'normalized_answers': sum(len(r.get('answers', {})) for r in erows + vrows),
        'raw_answers': sum(len(r.get('raw_response', {}).get('answers', {})) for r in erows + vrows),
        'quarantined_sentences': sum(len(r.get('quarantined_sentences', [])) for r in erows + vrows),
        'costs': costs, 'datasets': datasets, 'bindings': assigned,
        'historical_controls': {dataset: {arm: value['per_round'] for arm, value in panel['arms'].items()}
            for dataset, panel in load(PREVIOUS_RESULT)['datasets'].items()},
        'research_gate': es['status'] == vs['status'] == 'completed' and all(v['research_gate'] for v in datasets.values()),
        'evidence': {'plan_sha256': sha(PLAN.read_bytes()), 'extraction_protocol_sha256': sha(protocol_path('extraction').read_bytes()),
                    'verdict_protocol_sha256': sha(protocol_path('verdict').read_bytes()),
                    'extraction_summary_sha256': sha((output('extraction') / 'summary.json').read_bytes()),
                    'verdict_summary_sha256': sha((output('verdict') / 'summary.json').read_bytes()),
                    'historical_control_sha256': sha(PREVIOUS_RESULT.read_bytes())}}
