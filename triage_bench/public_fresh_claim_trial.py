"""Frozen, once-only fresh-measurement confirmation of two report candidates."""
import json
import time
import urllib.request
import urllib.error
from .paths import ROOT
from .public_data import sha, REVISION
from .public_rca_stages import load, committed
from .profile import MODEL, profile_check
from .hosted import encoded, redact
from .runner import NoRedirect, clean_api_key
from .public_binding_trial import SOURCES as PREVIOUS_SOURCES, answers
from .public_fresh_claim_features import ARMS, FIELDS, POLICY, CLASSES
from .public_fresh_claim_data import PLAN, DATA, OLD_PLAN, INDEX, allocation, check_plan, validate

PROTOCOL = ROOT / 'checkpoints/public-fresh-claims-protocol-2026-10-05.json'
RESULT = ROOT / 'checkpoints/public-fresh-claims-results-2026-10-05.json'
OUTPUT = ROOT / 'runs/public-fresh-claims/confirmation-hosted-2026-10-05-v1'
SOURCES = tuple(dict.fromkeys(PREVIOUS_SOURCES + (
    'triage_bench/public_binding_trial.py', 'triage_bench/public_fresh_claim_features.py',
    'triage_bench/public_fresh_claim_data.py', 'triage_bench/public_fresh_claim_trial.py',
    'scripts/run_public_fresh_claims.py')))


def plan(profile):
    from scripts.verify_public_binding import verify
    profile_check(profile)
    verify()
    if PLAN.exists():
        raise ValueError('Fresh plan already exists.')
    previous = load(ROOT / 'checkpoints/public-claim-binding-plan-2026-10-05.json')
    if any(profile[k] != previous[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Keep the recorded profile.')
    record = {'schema': 'public-fresh-claims-plan-1',
        'decision': 'User authorized fresh confirmation and selected controlled notes written before measurement access on 2026-10-05.',
        'revision': REVISION, 'index_sha256': sha(INDEX.read_bytes()), 'assignments': allocation(),
        'model': MODEL, 'endpoint': profile['endpoint'], 'context_tokens': profile['context_tokens'],
        'maximum_request_bytes': 24000, 'maximum_source_file_bytes': 50000000,
        'reports': 9, 'claims': 54, 'recordings': 9, 'service_cards': 18, 'rounds': 3,
        'maximum_calls': 189, 'maximum_answers': 324, 'arms': list(ARMS), 'fields': list(FIELDS), 'policy': POLICY,
        'allocation': 'All nine untouched RE3 reserves: three Train Ticket auth f4, three Online Boutique email f4 and three email f5. Keep all repetitions of each fault group. Earlier 22-case cause-evaluation panel, RE3 Sock Shop and 140 RE1 reserves remain unopened. No candidate promotion from failed causal tasks is implied.',
        'preparation': 'Before download commit this plan and the literal text catalogue. Select the largest observed-change service and a coverage-gap or smallest-change service using the frozen observation-only selector. Six fixed proposition kinds per report; strongest eligible metric channel is selected from measurements, with deterministic fallback when none is eligible. Wording, polarity and duration measure depend on identity hashes, never reference classes. No balancing or case replacement.',
        'text': 'New controlled sentences authored by the assistant before new telemetry access, with explicit service names. Different prose is joined into an unnumbered note. This is not independent analyst authorship or authentic reporting. Freeze full rendered notes and numerical references before calls; no text editing after preparation.',
        'candidates': 'Bound: one six-question request with both ledgers. Scoped: six one-question requests, each with only its named service ledger and the same full note. Reuse the frozen binding helper, numerical policy and Choice criteria unchanged. This two-candidate comparison combines grouping and evidence scope; it does not isolate their effects.',
        'bindings': 'Preparation supplies exact claim spans, proposition meanings and explicit service names. Audit those bindings byte-for-byte. Automatic claim extraction and automatic service attribution are not implemented or scored; report these as not evaluated, separately from verdict accuracy. Do not call supplied annotation accuracy extractor performance.',
        'references': 'Unchanged typed evaluator computes each verdict from recorded observations. References stay in a separate file, out of requests. No injected cause answer is used. Code can evaluate these authored propositions exactly by construction; prior ML predicts a different target and is not a verdict comparator.',
        'execution': 'Commit source/text/allocation plan before download, then commit exact request/reference fingerprints before inference. Three serial cyclic rounds, 27 bound calls and 162 scoped calls, 324 total verdicts. No warmup, retries, refitting, threshold search, text repair or post-result substitution. Stop on HTTP/network/model/context errors or three consecutive malformed replies. Timeout 30s. Missing/failed responses retain denominators.',
        'research_gate': 'Each candidate separately, in each application and every round: complete successful calls, at least 90% correctness in each of all three reference classes, zero wrong displayed verdicts, correct displayed support at least half supported references, and at least 90% all-six report correctness. A missing reference class makes this gate not assessable, not passing. Overall requires both candidates to pass in both applications. Compare paired fixes/losses and display variability descriptively, without requiring a scoped accuracy gain over bound.',
        'limits': 'Nine new controlled-fault recordings in only three correlated fault groups. New measurements and new controlled wording change together, so historical differences cannot isolate those causes. Public pretraining exposure is unknown. Three rounds are repeats, not independent data. The inherited 0.70 display boundary is uncalibrated for this task. No authentic-report extraction, specialist review, causal diagnosis, analyst benefit, production error rate or telecom readiness is established.',
        'source_sha256': {n: sha((ROOT / n).read_bytes()) for n in SOURCES},
        'evidence_sha256': {n: sha((ROOT / n).read_bytes()) for n in (
            str(OLD_PLAN.relative_to(ROOT)), 'checkpoints/public-claim-binding-results-2026-10-05.json')}}
    with PLAN.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    return {'status': 'frozen', 'maximum_calls': 189, 'fresh_recordings_allocated': 9, 'telemetry_opened': 0}


def requests():
    m = validate()
    if not m['fits_request_cap']:
        raise ValueError('Fresh wire cap exceeded before calls.')
    packets = load(DATA / 'inputs.json')
    result = []
    for n in (1, 2, 3):
        offset = n - 1
        for i, packet in enumerate(packets[offset:] + packets[:offset]):
            order = ARMS if (i + offset) % 2 == 0 else ARMS[::-1]
            for arm in order:
                for field in ((None,) if arm == 'bound' else FIELDS[offset:] + FIELDS[:offset]):
                    body = packet['requests'][arm] if field is None else packet['claim_requests'][field][arm]
                    result.append({'id': packet['id'] + '::' + arm + '::' + (field or 'all') + '::r' + str(n),
                        'card_id': packet['id'], 'field': field, 'arm': arm, 'round': n,
                        'request_sha256': sha(encoded(body)), 'body': body})
    return result


def freeze():
    check_plan()
    if PROTOCOL.exists():
        raise ValueError('Fresh protocol already exists.')
    planned = requests()
    if len(planned) != 189:
        raise ValueError('Fresh call budget changed.')
    record = {'schema': 'public-fresh-claims-protocol-1', 'maximum_calls': 189,
        'plan_sha256': sha(PLAN.read_bytes()), 'manifest_sha256': sha((DATA / 'manifest.json').read_bytes()),
        'reference_sha256': sha((DATA / 'references.json').read_bytes()),
        'requests': [{k: v for k, v in r.items() if k != 'body'} for r in planned]}
    with PROTOCOL.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    return {'status': 'frozen', 'maximum_calls': 189, 'planned_answers': 324}


def check():
    p = check_plan()
    committed(PROTOCOL)
    protocol, planned = load(PROTOCOL), requests()
    if (protocol['schema'], protocol['maximum_calls'], len(planned)) != ('public-fresh-claims-protocol-1', 189, 189):
        raise ValueError('Fresh protocol identity changed.')
    if protocol['plan_sha256'] != sha(PLAN.read_bytes()) or protocol['manifest_sha256'] != sha((DATA / 'manifest.json').read_bytes()) or protocol['reference_sha256'] != sha((DATA / 'references.json').read_bytes()):
        raise ValueError('Fresh protocol preparation changed.')
    if protocol['requests'] != [{k: v for k, v in r.items() if k != 'body'} for r in planned]:
        raise ValueError('Fresh exact request plan changed.')
    return p, planned


def run(profile):
    p, planned = check()
    profile_check(profile)
    if any(profile[k] != p[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Fresh profile changed.')
    key = clean_api_key(profile.get('api_key', ''))
    if not key:
        raise ValueError('Server-side key required.')
    OUTPUT.mkdir()
    (OUTPUT / 'requests.json').write_text(json.dumps(planned, indent=2) + '\n')
    rows, reason, consecutive = [], None, 0
    opener = urllib.request.build_opener(NoRedirect())
    with (OUTPUT / 'responses.jsonl').open('x') as stream:
        for req in planned:
            row = {k: v for k, v in req.items() if k != 'body'}
            row['status'] = 'ok'
            start = time.perf_counter()
            try:
                wire = urllib.request.Request(profile['endpoint'], data=encoded(req['body']), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key}, method='POST')
                with opener.open(wire, timeout=30) as response:
                    content = response.read(1048577)
                if len(content) > 1048576:
                    raise ValueError('Oversized provider response.')
                raw = json.loads(content)
                row['raw_response'] = redact(raw, key)
                if not isinstance(raw, dict) or raw.get('model') != MODEL:
                    reason = 'checkpoint_mismatch'
                    raise ValueError('Wrong model.')
                row['answers'] = answers(raw, req['body'])
                row['usage'] = raw.get('usage', {})
                tokens = row['usage'].get('input_tokens')
                if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 1:
                    raise ValueError('Missing input usage.')
                if tokens > p['context_tokens']:
                    reason = 'reported_context_overflow'
                    raise ValueError('Context overflow.')
            except urllib.error.HTTPError as error:
                row.update(status='error', error='Provider HTTP ' + str(error.code))
                reason = 'provider_http_' + str(error.code)
            except (OSError, ValueError, KeyError, TypeError) as error:
                row.update(status='error', error='Validation or request failure: ' + type(error).__name__)
                if isinstance(error, OSError):
                    reason = 'network_error'
            row = redact(row, key)
            row['latency_ms'] = (time.perf_counter() - start) * 1000
            rows.append(row)
            stream.write(json.dumps(row) + '\n')
            stream.flush()
            print(f"Fresh claim confirmation {len(rows)}/189 round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] != 'ok' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'
                break
    summary = {'schema': 'public-fresh-claims-hosted-1', 'planned': 189, 'attempted': len(rows),
        'failed': sum(r['status'] != 'ok' for r in rows), 'unattempted': 189 - len(rows),
        'status': 'completed' if len(rows) == 189 and all(r['status'] == 'ok' for r in rows) else 'incomplete_or_failed',
        'stopped_reason': reason, 'protocol_sha256': sha(PROTOCOL.read_bytes()),
        'files': {n: sha((OUTPUT / n).read_bytes()) for n in ('requests.json', 'responses.jsonl')}}
    (OUTPUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def verified_rows(complete=False):
    p, planned = check()
    summary = load(OUTPUT / 'summary.json')
    if summary['schema'] != 'public-fresh-claims-hosted-1' or summary['protocol_sha256'] != sha(PROTOCOL.read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
        raise ValueError('Fresh hosted identity changed.')
    for name, digest in summary['files'].items():
        if sha((OUTPUT / name).read_bytes()) != digest:
            raise ValueError('Fresh hosted bytes changed.')
    if load(OUTPUT / 'requests.json') != planned:
        raise ValueError('Fresh saved requests changed.')
    rows = [json.loads(line) for line in (OUTPUT / 'responses.jsonl').read_text().splitlines()]
    if len(rows) > len(planned):
        raise ValueError('Extra fresh calls.')
    for row, req in zip(rows, planned):
        if any(row.get(k) != v for k, v in req.items() if k != 'body') or row['status'] not in {'ok', 'error'}:
            raise ValueError('Fresh response identity changed.')
        if row['status'] == 'ok':
            tokens = row['usage'].get('input_tokens')
            if answers(row['raw_response'], req['body']) != row['answers'] or row['usage'] != row['raw_response']['usage'] or isinstance(tokens, bool) or not isinstance(tokens, int) or not 0 < tokens <= p['context_tokens']:
                raise ValueError('Fresh response normalization changed.')
    failed = sum(r['status'] != 'ok' for r in rows)
    status = 'completed' if len(rows) == 189 and not failed else 'incomplete_or_failed'
    if (summary['planned'], summary['attempted'], summary['failed'], summary['unattempted'], summary['status']) != (189, len(rows), failed, 189 - len(rows), status):
        raise ValueError('Fresh planned denominators changed.')
    if complete and (status != 'completed' or summary['stopped_reason']):
        raise ValueError('Complete fresh evidence required.')
    return rows, summary


def assess(rows, packets, references):
    indexed = {(r['card_id'], r['arm'], r['round'], r['field']): r for r in rows}
    refs = {r['id']: r for r in references}
    datasets = {}
    for dataset in sorted({p['dataset'] for p in packets}):
        cards = [p for p in packets if p['dataset'] == dataset]
        arms = {}
        for arm in ARMS:
            outcomes, rounds = [], []
            for n in (1, 2, 3):
                for packet in cards:
                    for field in FIELDS:
                        row = indexed.get((packet['id'], arm, n, None if arm == 'bound' else field))
                        answer = row['answers'].get(field) if row and row['status'] == 'ok' else None
                        choice = answer['choice'] if answer else 'unavailable'
                        reference = refs[packet['id']]['answers'][field]['answer']
                        outcomes.append({'id': packet['id'], 'field': field, 'round': n,
                            'service': packet['claim_sources'][field]['service'], 'choice': choice, 'reference': reference,
                            'correct': choice == reference, 'displayed': bool(answer and answer['probabilities'][choice] >= .7),
                            'failed_or_missing': not bool(answer), 'unknown_to_decisive': reference == 'unanswerable' and choice in ('supported', 'contradicted')})
                rr = [o for o in outcomes if o['round'] == n]
                groups = [[o for o in rr if o['id'] == packet['id']] for packet in cards]
                rounds.append({'round': n, 'claims': len(rr), 'reports': len(cards),
                    'correct': sum(o['correct'] for o in rr),
                    'class_total': {c: sum(o['reference'] == c for o in rr) for c in CLASSES},
                    'class_correct': {c: sum(o['reference'] == c and o['correct'] for o in rr) for c in CLASSES},
                    'displayed': sum(o['displayed'] for o in rr), 'displayed_correct': sum(o['displayed'] and o['correct'] for o in rr),
                    'wrong_displayed': sum(o['displayed'] and not o['correct'] for o in rr),
                    'withheld': sum(not o['displayed'] for o in rr), 'failed_or_missing': sum(o['failed_or_missing'] for o in rr),
                    'correct_displayed_support': sum(o['displayed'] and o['choice'] == o['reference'] == 'supported' for o in rr),
                    'reference_support': sum(o['reference'] == 'supported' for o in rr),
                    'unknown_to_decisive': sum(o['unknown_to_decisive'] for o in rr),
                    'all_six_correct': sum(all(o['correct'] for o in g) for g in groups),
                    'complete_display': sum(all(o['displayed'] for o in g) for g in groups),
                    'complete_correct_display': sum(all(o['displayed'] and o['correct'] for o in g) for g in groups),
                    'confusion': {c: {v: sum(o['reference'] == c and o['choice'] == v for o in rr)
                        for v in (*CLASSES, 'unavailable')} for c in CLASSES}})
            covered = all(rounds[0]['class_total'][c] > 0 for c in CLASSES)
            passed = covered and all(not r['failed_or_missing'] and not r['wrong_displayed']
                and all(r['class_correct'][c] / r['class_total'][c] >= .9 for c in CLASSES)
                and r['correct_displayed_support'] >= r['reference_support'] / 2
                and r['all_six_correct'] / r['reports'] >= .9 for r in rounds)
            arms[arm] = {'per_round': rounds, 'outcomes': outcomes,
                'research_gate': passed, 'gate_status': 'passed' if passed else 'failed' if covered else 'insufficient_class_coverage'}
        pairs = []
        for a, b in zip(arms['bound']['outcomes'], arms['scoped']['outcomes']):
            pairs.append({'id': a['id'], 'field': a['field'], 'round': a['round'],
                'fix': not a['correct'] and b['correct'] and not a['failed_or_missing'],
                'loss': a['correct'] and not b['correct'] and not b['failed_or_missing']})
        stable = lambda key: [{'id': p['id'], 'field': f} for p in cards for f in FIELDS
            if all(o[key] for o in pairs if o['id'] == p['id'] and o['field'] == f)]
        datasets[dataset] = {'reports': len(cards), 'claims': len(cards) * 6, 'arms': arms, 'pairs': pairs,
            'steps': {'bound__scoped': {'stable_fixes': stable('fix'), 'stable_losses': stable('loss'),
                'no_error_opportunity': all(r['correct'] == r['claims'] for r in arms['bound']['per_round'])}},
            'step_gates': {a: arms[a]['research_gate'] for a in ARMS},
            'research_gate': all(arms[a]['research_gate'] for a in ARMS),
            'consistency': {arm: {'stable_verdict_claims': sum(len({o['choice'] for o in v['outcomes'] if o['id'] == p['id'] and o['field'] == f}) == 1 for p in cards for f in FIELDS),
                'stable_display_claims': sum(len({o['displayed'] for o in v['outcomes'] if o['id'] == p['id'] and o['field'] == f}) == 1 for p in cards for f in FIELDS)} for arm, v in arms.items()}}
    return datasets


def score():
    rows, summary = verified_rows()
    datasets = assess(rows, load(DATA / 'inputs.json'), load(DATA / 'references.json'))
    return {'schema': 'public-fresh-claims-results-1', 'fresh_recordings': 9, 'reports': 9, 'claims': 54,
        'recordings': 9, 'service_cards': 18, 'planned_calls': 189, 'planned_answers': 324,
        'questions_per_call': {'bound': 6, 'scoped': 1}, 'failed_or_missing_calls': summary['failed'] + summary['unattempted'],
        'datasets': datasets, 'research_gate': not (summary['failed'] + summary['unattempted']) and all(p['research_gate'] for p in datasets.values()),
        'extraction': {'claim_extraction': 'not_evaluated', 'automatic_service_attribution': 'not_evaluated', 'binding_source': 'preparation annotations'},
        'evidence': {'plan_sha256': sha(PLAN.read_bytes()), 'protocol_sha256': sha(PROTOCOL.read_bytes()),
            'summary_sha256': sha((OUTPUT / 'summary.json').read_bytes())}}
