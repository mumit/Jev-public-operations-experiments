"""Once-only sentence-review replay and dependent bound-verdict comparison."""
import copy
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
from .public_note_v2_trial import SOURCES as PREVIOUS_SOURCES, assess as original_assess
from .public_note_features import ARMS, DIMENSIONS, parser, annotated, semantics, verdict_request
from .public_sentence_features import extract, validate_reply, GlobalReplyError, whole_note_counterfactual

PLAN = ROOT / 'checkpoints/public-sentence-review-plan-2026-10-05.json'
BASE = ROOT / 'runs/public-sentence-review'
RESULT = ROOT / 'checkpoints/public-sentence-review-results-2026-10-05.json'
SOURCES = PREVIOUS_SOURCES + ('triage_bench/public_note_audit.py',
    'triage_bench/public_sentence_features.py', 'triage_bench/public_sentence_trial.py',
    'scripts/run_public_sentence_review.py')


def protocol_path(phase):
    if phase not in ('extraction', 'verdict'):
        raise ValueError('Unknown sentence-review phase.')
    return ROOT / ('checkpoints/public-sentence-' + phase + '-protocol-2026-10-05.json')


def output(phase):
    protocol_path(phase)
    return BASE / (phase + '-hosted-2026-10-05-v1')


def plan(profile):
    from scripts.verify_public_notes import verify
    profile_check(profile); verify()
    previous = load(ROOT / 'checkpoints/public-note-extraction-v2-plan-2026-10-05.json')
    if any(profile[k] != previous[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Keep the recorded profile.')
    record = {k: copy.deepcopy(v) for k, v in previous.items() if k not in ('source_sha256', 'evidence_sha256')}
    record.update(schema='public-sentence-review-plan-1',
        decision='User selected sentence-level review on 2026-10-05.',
        extraction='Replay the exact v2 extraction bodies on the same nine inspected notes, three rounds. Keep definitions, options, inputs, numerical policy, strict Choice normalizer and 0.70 acceptance/display boundaries unchanged.',
        failure_handling='Validate model, answer envelope, usage and context globally. Wrong model, unexpected answer fields, invalid global shape/usage/context, HTTP or network error stops the run. Missing or malformed individual answers quarantine their entire sentence, including an invalid unused dimension; independently valid siblings remain eligible. Keep raw invalid choices. Never choose argmax, invent probabilities, retry or repair. Apply the same per-sentence policy to dependent verdict replies. A globally valid reply with quarantined sentences is completed work with lost sentence coverage, not a successful judgment of those sentences.',
        comparison='Historical whole-note results remain unchanged. Separately apply the old whole-note validator to each NEW extraction reply offline to measure policy losses on identical responses, without extra model calls or counterfactual verdicts. Historical/new differences also include response variability and cannot isolate the policy effect.',
        execution='Commit this source and plan, then exact extraction request/reference hashes before 27 once-only calls. Commit dependent bindings/request hashes and extraction summary before at most 81 verdict calls. Three cyclic rounds, 108 maximum calls, 2916 maximum answers. Stop on global reply/HTTP/network/context errors or three consecutive other malformed replies. Missing calls and quarantined sentences retain all scoring denominators. No retry, tuning, request repair or protected telemetry access.',
        source_sha256={n: sha((ROOT / n).read_bytes()) for n in SOURCES},
        evidence_sha256={str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in
            [ROOT / 'checkpoints/public-note-extraction-v2-audit-2026-10-05.json',
             ROOT / 'checkpoints/public-note-extraction-v2-plan-2026-10-05.json',
             *(DATA / n for n in ('inputs.json', 'references.json', 'manifest.json'))]})
    with PLAN.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    return {'status': 'frozen', 'maximum_calls': 108, 'new_telemetry_opened': 0}


def check_plan():
    committed(PLAN); p = load(PLAN)
    if (p['schema'], p['maximum_calls']) != ('public-sentence-review-plan-1', 108):
        raise ValueError('Sentence-review plan identity changed.')
    for mapping in ('source_sha256', 'evidence_sha256'):
        for name, digest in p[mapping].items():
            if sha((ROOT / name).read_bytes()) != digest:
                raise ValueError('Sentence-review source or prerequisite changed.')
    return p


def bindings():
    rows, _ = verified_rows('extraction', complete=True)
    indexed = {(r['card_id'], r['round']): r for r in rows}
    refs = {r['id']: r for r in load(DATA / 'references.json')}
    result = []
    for n in (1, 2, 3):
        for packet in load(DATA / 'inputs.json'):
            for arm in ARMS:
                values = extract(packet, indexed[(packet['id'], n)]) if arm == 'jev' else parser(packet) if arm == 'parser' else annotated(packet, refs[packet['id']])
                result.append({'card_id': packet['id'], 'arm': arm, 'round': n, 'bindings': values})
    return result


def requests(phase):
    m = validate()
    if not m['fits_request_cap']:
        raise ValueError('Note extraction wire cap exceeded before calls.')
    packets = load(DATA / 'inputs.json')
    assigned = {(r['card_id'], r['arm'], r['round']): r['bindings'] for r in bindings()} if phase == 'verdict' else {}
    result = []
    for n in (1, 2, 3):
        offset = n - 1
        for i, packet in enumerate(packets[offset:] + packets[:offset]):
            order = ('jev',) if phase == 'extraction' else ARMS if (i + offset) % 2 == 0 else ARMS[::-1]
            for arm in order:
                body = packet['extraction_request'] if phase == 'extraction' else verdict_request(packet, assigned[(packet['id'], arm, n)])
                result.append({'id': packet['id'] + '::' + phase + '::' + arm + '::r' + str(n),
                    'card_id': packet['id'], 'phase': phase, 'arm': arm, 'round': n,
                    'request_sha256': sha(encoded(body)) if body else None, 'body': body})
    if phase == 'extraction' and len(result) != 27 or phase == 'verdict' and len(result) != 81:
        raise ValueError('Note job budget changed.')
    return result


def freeze(phase):
    p = check_plan(); path = protocol_path(phase)
    if path.exists():
        raise ValueError('Note phase already frozen.')
    planned = requests(phase)
    largest = max((len(encoded(r['body'])) for r in planned if r['body']), default=0)
    if largest > p['maximum_request_bytes']:
        raise ValueError('Dependent wire cap exceeded; no calls authorized.')
    record = {'schema': 'public-sentence-protocol-1', 'phase': phase, 'plan_sha256': sha(PLAN.read_bytes()),
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
    if protocol['schema'] != 'public-sentence-protocol-1' or protocol['phase'] != phase or protocol['plan_sha256'] != sha(PLAN.read_bytes()) or protocol['manifest_sha256'] != sha((DATA / 'manifest.json').read_bytes()) or protocol['reference_sha256'] != sha((DATA / 'references.json').read_bytes()):
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
    destination = output(phase); destination.mkdir()
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
            print(f"Note {phase} {len(rows)}/{len(planned)} round {row['round']} {row['status']}", flush=True)
            consecutive = consecutive + 1 if row['status'] == 'error' else 0
            if reason or consecutive >= 3:
                reason = reason or 'three_consecutive_failures'; break
    summary = {'schema': 'public-sentence-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'public-sentence-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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


def assess(packets, references, assigned, verdict_rows, extraction_rows):
    def completed_rows(rows):
        return [{**r, 'status': 'ok' if r['status'] == 'ok_with_review' else r['status']} for r in rows]
    result = original_assess(packets, references, assigned, completed_rows(verdict_rows), completed_rows(extraction_rows))
    for dataset, panel in result.items():
        ids = {p['id'] for p in packets if p['dataset'] == dataset}
        panel['validation'] = [{'phase': phase, 'round': n,
            'globally_valid_replies': sum(r['status'] in ('ok', 'ok_with_review') for r in selected),
            'replies_with_review': sum(r['status'] == 'ok_with_review' for r in selected),
            'invalid_fields': sum(len(r.get('field_errors', {})) for r in selected),
            'quarantined_sentences': sum(len(r.get('quarantined_sentences', [])) for r in selected)}
            for phase, rows in [('extraction', extraction_rows), ('verdict', verdict_rows)] for n in (1, 2, 3)
            for selected in [[r for r in rows if r['card_id'] in ids and r['round'] == n]]]
    return result


def counterfactual(packets, refs, rows):
    gold = {r['id']: r for r in refs}; indexed = {(r['card_id'], r['round']): r for r in rows}
    result = []
    for dataset in sorted({p['dataset'] for p in packets}):
        for n in (1, 2, 3):
            current = whole = recovered = lost = 0
            for packet in [p for p in packets if p['dataset'] == dataset]:
                row = indexed.get((packet['id'], n), {})
                sentence = extract(packet, row)
                note = whole_note_counterfactual(packet, row) if row.get('status') in ('ok', 'ok_with_review') else {}
                for a in gold[packet['id']]['annotations']:
                    if not a['actionable']: continue
                    def correct(bindings):
                        v = bindings.get(a['id'], {})
                        return bool(v.get('accepted') and v.get('role') == 'assertion' and
                            v.get('service') == a['service'] and semantics(v) == semantics(a))
                    sc, wc = correct(sentence), correct(note)
                    current += sc; whole += wc; recovered += sc and not wc; lost += wc and not sc
            result.append({'dataset': dataset, 'round': n, 'routable_claims': sum(p['dataset'] == dataset for p in packets) * 6,
                'sentence_correct_bindings': current, 'whole_note_correct_bindings': whole,
                'recovered_correct_bindings': recovered, 'lost_correct_bindings': lost})
    return result


def score():
    erows, es = verified_rows('extraction'); vrows, vs = verified_rows('verdict')
    assigned = load(protocol_path('verdict'))['bindings']
    packets, refs = load(DATA / 'inputs.json'), load(DATA / 'references.json')
    datasets = assess(packets, refs, assigned, vrows, erows)
    costs = [{'phase': phase, 'arm': arm, 'calls': len(rr),
        'input_tokens': sum(r.get('usage', r.get('raw_response', {}).get('usage', {})).get('input_tokens', 0) for r in rr),
        'summed_latency_ms': sum(r['latency_ms'] for r in rr)}
        for phase, rows in [('extraction', erows), ('verdict', vrows)] for arm in (('jev',) if phase == 'extraction' else ARMS)
        for rr in [[r for r in rows if r['arm'] == arm and r['status'] != 'skipped_no_accepted_claims']]]
    return {'schema': 'public-sentence-results-1', 'reports': 9, 'sentence_candidates': 108, 'routable_claims': 54,
        'atomic_assertions_in_notes': 81, 'new_recordings_opened': 0,
        'actual_calls': es['attempted_calls'] + vs['attempted_calls'],
        'normalized_answers': sum(len(r.get('answers', {})) for r in erows + vrows),
        'raw_answers': sum(len(r.get('raw_response', {}).get('answers', {})) for r in erows + vrows),
        'quarantined_sentences': sum(len(r.get('quarantined_sentences', [])) for r in erows + vrows),
        'costs': costs, 'datasets': datasets, 'same_reply_counterfactual': counterfactual(packets, refs, erows),
        'bindings': assigned,
        'research_gate': es['status'] == vs['status'] == 'completed' and all(v['research_gate'] for v in datasets.values()),
        'evidence': {'plan_sha256': sha(PLAN.read_bytes()), 'extraction_protocol_sha256': sha(protocol_path('extraction').read_bytes()),
                    'verdict_protocol_sha256': sha(protocol_path('verdict').read_bytes()),
                    'extraction_summary_sha256': sha((output('extraction') / 'summary.json').read_bytes()),
                    'verdict_summary_sha256': sha((output('verdict') / 'summary.json').read_bytes())}}
