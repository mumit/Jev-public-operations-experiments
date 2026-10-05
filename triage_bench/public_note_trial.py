"""Once-only, two-stage note extraction and dependent bound-verdict diagnostic."""
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
from .public_fresh_claim_trial import SOURCES as PREVIOUS_SOURCES
from .public_binding_trial import answers
from .public_note_data import PLAN, DATA, check_plan, validate
from .public_note_features import ARMS, DIMENSIONS, extraction, parser, annotated, semantics, verdict_request

BASE = ROOT / 'runs/public-note-extraction'
RESULT = ROOT / 'checkpoints/public-note-extraction-results-2026-10-05.json'
SOURCES = tuple(dict.fromkeys(PREVIOUS_SOURCES + (
    'triage_bench/public_fresh_claim_trial.py', 'triage_bench/public_note_features.py',
    'triage_bench/public_note_data.py', 'triage_bench/public_note_trial.py', 'scripts/run_public_notes.py')))


def protocol_path(phase):
    if phase not in ('extraction', 'verdict'):
        raise ValueError('Unknown note phase.')
    return ROOT / ('checkpoints/public-note-' + phase + '-protocol-2026-10-05.json')


def output(phase):
    protocol_path(phase)
    return BASE / (phase + '-hosted-2026-10-05-v1')


def plan(profile):
    from scripts.verify_public_fresh_claims import verify
    profile_check(profile); verify()
    if PLAN.exists():
        raise ValueError('Note plan already exists.')
    previous = load(ROOT / 'checkpoints/public-fresh-claims-plan-2026-10-05.json')
    if any(profile[k] != previous[k] for k in ('model', 'endpoint', 'context_tokens')):
        raise ValueError('Keep recorded profile.')
    record = {'schema': 'public-note-extraction-plan-1',
        'decision': 'User authorized ordinary-note extraction diagnostic after fresh confirmation, 2026-10-05.',
        'model': MODEL, 'endpoint': profile['endpoint'], 'context_tokens': profile['context_tokens'],
        'maximum_request_bytes': 79840, 'reports': 9, 'candidates': 108, 'actionable_claims': 54, 'rounds': 3,
        'arms': list(ARMS), 'dimensions': list(DIMENSIONS), 'maximum_calls': 108, 'maximum_answers': 2916,
        'data': 'Reuse all nine now-inspected fresh-confirmation recordings. No downloads, new telemetry or protected-panel access. Full observed service/channel inventory, not only annotated subjects. Repeated cases share three fault groups; this is a diagnostic on inspected data.',
        'text': 'Controlled prose authored by the assistant from six earlier typed meanings. Per note: six resolvable single claims; one unresolved single health assertion; one compound with two atomic assertions; four non-assertions (heading, requested check, question, unendorsed quotation). Generic punctuation segmentation supplies twelve candidates. Swap complete subject blocks by identity hash, not verdict. New pronouns test local context. Freeze all prose, spans and separate annotations before inference. Not authentic or independently authored analyst notes.',
        'target': 'Classify sentence candidates, resolve one service and map a bounded semantic family. Compound sentences go to review without splitting. Unresolved service and unmapped meaning also go to review. This does not measure unrestricted atomic-claim extraction. Disclose nine atomic assertions per report, six routable, one ambiguous and two in a compound.',
        'extraction': 'One Jev request per note/round: six independent Choice questions per candidate for role, service, kind, channel, duration measure and polarity. Every question sees full prose but no telemetry, references or other replies. Code composes them. Accept only a single assertion, unique observed service, mapped kind/polarity and required channel/measure, each relevant chosen probability >=0.70. No margin calibration or retuning.',
        'comparators': 'Conservative literal parser has no learned parameters, probabilities or pronoun resolution. Annotated control supplies gold bindings and measures only verdict capacity, not extraction performance. Earlier fitted ML predicts a different target and remains unscored here.',
        'verdict': 'After actual extraction replies, frozen code constructs one bound-batch request per note/arm/round from accepted text and assigned services. Retain full note and only ledgers of accepted subjects. Use unchanged numerical policy/Choice verdict criteria. Do not correct model bindings with annotations. Freeze exact dependent requests and extraction evidence fingerprint in a separate committed protocol before those calls. Zero accepted candidates yields an explicit application skip, not a fabricated reply. Verdict display requires accepted extraction and chosen verdict probability >=0.70; probabilities are not calibrated risk estimates.',
        'execution': 'Commit literal producers and plan before preparation; commit all exact extraction request/reference hashes before 27 calls. Then commit dependent protocol before at most 81 verdict calls. Three cyclic rounds, no retries/warmup/request repair/threshold search. Stop on HTTP/network/model/context errors or three consecutive malformed replies. Missing calls retain denominators. Maximum 1944 extraction answers plus 972 verdict answers (twelve candidates per call); actual dependent budget may be lower. 30-second timeout, one-megabyte reply cap.',
        'scoring': 'Report role agreement over all 108 sentence candidates; assertion precision/recall; service and exact kind/polarity/relevant channel/measure over 54 routable gold claims; accepted correct bindings, missed claims, accepted nonclaims/review-only claims; conditional verdict accuracy on correctly bound claims; end-to-end correctness requires correct extraction AND verdict, never a coincidentally correct verdict on the wrong service; whole-six note accuracy and displayed coverage. Review-only ambiguous/compound atomic claims are disclosed outside the six-routable verdict denominator. Preserve every gold claim, including withheld or missing. Show rounds and applications separately, paired losses from annotated control, consistency and actual costs.',
        'research_gate': 'Jev in each application and every round: complete successful calls; role agreement >=90%; service and exact semantics >=90% on routable claims; accepted correct bindings >=90%; zero accepted nonclaims or review-only candidates; end-to-end correctness >=90%; whole-six note correctness >=90%; zero unsafe displayed verdicts; at least half reference-supported routable claims correctly displayed. If no supported references, support criterion is not assessable. Parser is a comparator; annotated control is correct by construction for extraction. No new panel opens on a pass.',
        'limits': 'Authored prose on inspected measurements with assistant annotations, a bounded taxonomy and only nine reports. Ordinary-style phrasing does not establish authentic-report performance. Sentence segmentation and independent choices do not extract arbitrary spans or split compound assertions. Public pretraining exposure unknown. No specialist-reviewed semantics, causal diagnosis, analyst benefit, production reliability or telecom readiness. Keep all historical failures visible.',
        'source_sha256': {n: sha((ROOT / n).read_bytes()) for n in SOURCES},
        'evidence_sha256': {n: sha((ROOT / n).read_bytes()) for n in ('checkpoints/public-fresh-claims-plan-2026-10-05.json', 'checkpoints/public-fresh-claims-results-2026-10-05.json')}}
    with PLAN.open('x') as f:
        f.write(json.dumps(record, indent=2) + '\n')
    return {'status': 'frozen', 'maximum_calls': 108, 'new_telemetry_opened': 0}


def bindings():
    rows, _ = verified_rows('extraction', complete=True)
    indexed = {(r['card_id'], r['round']): r for r in rows}
    refs = {r['id']: r for r in load(DATA / 'references.json')}
    result = []
    for n in (1, 2, 3):
        for packet in load(DATA / 'inputs.json'):
            for arm in ARMS:
                values = extraction(packet, indexed[(packet['id'], n)]['answers']) if arm == 'jev' else parser(packet) if arm == 'parser' else annotated(packet, refs[packet['id']])
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
    record = {'schema': 'public-note-protocol-1', 'phase': phase, 'plan_sha256': sha(PLAN.read_bytes()),
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
    if protocol['schema'] != 'public-note-protocol-1' or protocol['phase'] != phase or protocol['plan_sha256'] != sha(PLAN.read_bytes()) or protocol['manifest_sha256'] != sha((DATA / 'manifest.json').read_bytes()) or protocol['reference_sha256'] != sha((DATA / 'references.json').read_bytes()):
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
                    row['answers'] = answers(raw, req['body']); row['usage'] = raw.get('usage', {})
                    tokens = row['usage'].get('input_tokens')
                    if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 1:
                        raise ValueError('Missing usage.')
                    if tokens > p['context_tokens']:
                        reason = 'reported_context_overflow'; raise ValueError('Context overflow.')
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
    summary = {'schema': 'public-note-hosted-1', 'phase': phase, 'planned_jobs': len(planned),
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
    if summary['schema'] != 'public-note-hosted-1' or summary['phase'] != phase or summary['protocol_sha256'] != sha(protocol_path(phase).read_bytes()) or set(summary['files']) != {'requests.json', 'responses.jsonl'}:
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
        if any(row.get(k) != v for k, v in req.items() if k != 'body') or row['status'] not in ('ok', 'error', 'skipped_no_accepted_claims'):
            raise ValueError('Note response identity changed.')
        if bool(req['body']) == (row['status'] == 'skipped_no_accepted_claims'):
            raise ValueError('Skip does not match zero accepted claims.')
        if row['status'] == 'skipped_no_accepted_claims' and any(k in row for k in ('answers', 'raw_response', 'usage')):
            raise ValueError('Application skip fabricated provider evidence.')
        if row['status'] == 'ok':
            tokens = row['usage'].get('input_tokens')
            if answers(row['raw_response'], req['body']) != row['answers'] or row['usage'] != row['raw_response']['usage'] or isinstance(tokens, bool) or not isinstance(tokens, int) or not 0 < tokens <= p['context_tokens']:
                raise ValueError('Note normalized reply changed.')
    status = 'completed' if len(rows) == len(planned) and not any(r['status'] == 'error' for r in rows) else 'incomplete_or_failed'
    if (summary['planned_jobs'], summary['planned_calls'], summary['recorded_jobs'], summary['attempted_calls'], summary['failed'], summary['unattempted_jobs'], summary['status']) != (len(planned), sum(bool(r['body']) for r in planned), len(rows), sum(r['status'] != 'skipped_no_accepted_claims' for r in rows), sum(r['status'] == 'error' for r in rows), len(planned) - len(rows), status):
        raise ValueError('Note hosted denominators changed.')
    if complete and (status != 'completed' or summary['stopped_reason']):
        raise ValueError('Complete note evidence required.')
    return rows, summary


def assess(packets, references, assigned, verdict_rows, extraction_rows):
    refs = {r['id']: r for r in references}
    bound = {(r['card_id'], r['arm'], r['round']): r['bindings'] for r in assigned}
    verdicts = {(r['card_id'], r['arm'], r['round']): r for r in verdict_rows}
    extracted = {(r['card_id'], r['round']): r for r in extraction_rows}
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
                    er = extracted.get((packet['id'], n))
                    if not vr or vr['status'] == 'error' or arm == 'jev' and (not er or er['status'] != 'ok'):
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
                         'research_gate': passed if arm == 'jev' else None,
                         'gate_status': ('passed' if passed else 'failed') if arm == 'jev' else 'comparator_not_candidate'}
        pairs = []
        for control, candidate in zip(arms['annotated']['outcomes'], arms['jev']['outcomes']):
            if control['actionable']:
                pairs.append({'id': control['id'], 'sentence': control['sentence'], 'round': control['round'],
                    'loss_from_control': control['end_to_end_correct'] and not candidate['end_to_end_correct'],
                    'fix_over_control': not control['end_to_end_correct'] and candidate['end_to_end_correct']})
        datasets[dataset] = {'reports': len(cards), 'routable_claims': len(cards) * 6,
            'atomic_assertions_in_notes': len(cards) * 9, 'groups': 1 if dataset == 'Train Ticket' else 2,
            'arms': arms, 'pairs': pairs, 'research_gate': arms['jev']['research_gate'],
            'consistency': {arm: {key: sum(len({o[key] for o in value['outcomes'] if o['id'] == p['id'] and o['sentence'] == c['id']}) == 1
                for p in cards for c in refs[p['id']]['annotations']) for key in ('role', 'service', 'accepted', 'choice', 'displayed')} for arm, value in arms.items()}}
    return datasets


def score():
    erows, es = verified_rows('extraction'); vrows, vs = verified_rows('verdict')
    assigned = load(protocol_path('verdict'))['bindings']
    datasets = assess(load(DATA / 'inputs.json'), load(DATA / 'references.json'), assigned, vrows, erows)
    costs = [{'phase': phase, 'arm': arm, 'calls': len(rr), 'input_tokens': sum(r.get('usage', {}).get('input_tokens', 0) for r in rr),
        'summed_latency_ms': sum(r['latency_ms'] for r in rr)}
        for phase, rows in [('extraction', erows), ('verdict', vrows)] for arm in (('jev',) if phase == 'extraction' else ARMS)
        for rr in [[r for r in rows if r['arm'] == arm and r['status'] != 'skipped_no_accepted_claims']]]
    return {'schema': 'public-note-results-1', 'reports': 9, 'sentence_candidates': 108, 'routable_claims': 54,
        'atomic_assertions_in_notes': 81, 'new_recordings_opened': 0,
        'actual_calls': es['attempted_calls'] + vs['attempted_calls'],
        'actual_answers': sum(len(r.get('answers', {})) for r in erows + vrows), 'costs': costs, 'datasets': datasets,
        'research_gate': es['status'] == vs['status'] == 'completed' and all(v['research_gate'] for v in datasets.values()),
        'evidence': {'plan_sha256': sha(PLAN.read_bytes()), 'extraction_protocol_sha256': sha(protocol_path('extraction').read_bytes()),
                    'verdict_protocol_sha256': sha(protocol_path('verdict').read_bytes()),
                    'extraction_summary_sha256': sha((output('extraction') / 'summary.json').read_bytes()),
                    'verdict_summary_sha256': sha((output('verdict') / 'summary.json').read_bytes())}}
