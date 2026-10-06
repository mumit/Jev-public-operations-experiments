"""Versioned analyst decisions and local verdict previews. No provider access."""
import copy
import json
from pathlib import Path
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load
from .public_note_language_data import DATA
from .public_note_language_trial import RESULT
from .public_note_features import DIMENSIONS, accept, verdict_request
from .public_claim_features import DURATIONS, ledger

SPEC = ROOT / 'checkpoints/claim-review-workflow-2026-10-05.json'
SCHEMA = 'analyst-claim-review-1'


def fingerprint():
    spec = load(SPEC)
    for name, digest in spec['sha256'].items():
        if sha((ROOT / name).read_bytes()) != digest:
            raise ValueError('Review workflow source or evidence changed.')
    return sha(SPEC.read_bytes())


def packet(identifier):
    return copy.deepcopy(next(p for p in load(DATA / 'inputs.json') if p['id'] == identifier))


def proposal(identifier):
    return copy.deepcopy(next(b['bindings'] for b in load(RESULT)['bindings']
        if b['card_id'] == identifier and b['arm'] == 'meaning' and b['round'] == 1))


def options(p):
    return {'role': ['assertion', 'non_assertion', 'multiple_assertions'],
        'service': [*p['services'], 'ambiguous', 'none'],
        'kind': ['metric_material', 'metric_direction', 'duration_material', 'span_adequacy', 'health', 'causality', 'unmapped'],
        'channel': [*p['channels'], 'none_or_unclear'],
        'measure': [*DURATIONS, 'none_or_unclear'], 'polarity': ['positive', 'negative', 'unclear']}


def request_template(p):
    """Reuse numerical policy; make reviewed meaning explicit in a new request."""
    first = p['candidates'][0]['id']
    sample = {c['id']: {'accepted': c['id'] == first, 'service': p['services'][0]} for c in p['candidates']}
    question = verdict_request(p, sample)['questions'][first + '_verdict']
    prefix = question['instructions'].split('Assess only the exact statement bound to service ')[0]
    return {'model': 'jev-1.13.0', 'prefix': prefix, 'criteria': question['criteria'],
        'ledgers': {o['service']: ledger(o) for o in p['observations']},
        'note_json': json.dumps(p['note']),
        'ledger_json': {o['service']: json.dumps(ledger(o), sort_keys=True, separators=(',', ':'), allow_nan=False) for o in p['observations']}}


def reviewed_request(p, decisions):
    confirmed = [c for c in p['candidates'] if decisions.get(c['id'], {}).get('decision') == 'confirm']
    if not confirmed:
        return None
    t = request_template(p)
    services = sorted({decisions[c['id']]['values']['service'] for c in confirmed})
    questions = {}
    for c in confirmed:
        v = decisions[c['id']]['values']
        # Kind/polarity now influence the actual input rather than scoring alone.
        meaning = json.dumps({d: v[d] for d in DIMENSIONS if d != 'role'}, sort_keys=True, separators=(',', ':'))
        questions[c['id'] + '_verdict'] = {'type': 'choice', 'instructions': t['prefix'] +
            f"Assess the analyst-confirmed single assertion about service {v['service']}. Use only that service's facts. " +
            'The analyst confirmed this bounded meaning (positive means the defined property; negative means its opposite): ' + meaning +
            '. Resolve its pronoun using this binding and the full note context. Exact original sentence: ' + c['text'],
            'criteria': copy.deepcopy(t['criteria'])}
    return {'model': t['model'], 'state': json.dumps({'note': p['note'], 'services': [t['ledgers'][s] for s in services]},
        sort_keys=True, separators=(',', ':'), allow_nan=False), 'questions': questions}


def same_json(a, b):
    """Allow JSON numeric serialization, while keeping booleans distinct."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, dict) or isinstance(b, dict):
        return isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b) and all(same_json(a[k], b[k]) for k in a)
    if isinstance(a, list) or isinstance(b, list):
        return isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and all(same_json(x, y) for x, y in zip(a, b))
    return a == b


def validate(export, require_complete=True):
    """Validate choices and provenance; do not validate an analyst's judgment."""
    if not isinstance(export, dict) or set(export) != {'schema', 'workflow_sha256', 'note_id', 'proposal', 'reviews'}:
        raise ValueError('Unexpected review fields.')
    if export['schema'] != SCHEMA or export['workflow_sha256'] != fingerprint():
        raise ValueError('Review version or evidence does not match.')
    if not isinstance(export['note_id'], str):
        raise ValueError('Invalid note identifier.')
    try:
        p = packet(export['note_id'])
    except StopIteration as error:
        raise ValueError('Unknown note identifier.') from error
    original = proposal(p['id']); allowed = options(p)
    if not same_json(export['proposal'], original):
        raise ValueError('The recorded Jev proposal was changed.')
    reviews = export['reviews']
    ids = {c['id'] for c in p['candidates']}
    if not isinstance(reviews, dict) or set(reviews) - ids or (require_complete and set(reviews) != ids):
        raise ValueError('Review each sentence once before preparing a complete request.')
    corrected, confirmed, withheld = [], [], []
    for identifier, review in reviews.items():
        if not isinstance(review, dict):
            raise ValueError('Malformed sentence review.')
        if review.get('decision') == 'confirm':
            if set(review) != {'decision', 'values'} or not isinstance(review['values'], dict) or set(review['values']) != set(DIMENSIONS):
                raise ValueError('Confirm every binding dimension explicitly.')
            v = review['values']
            if any(not isinstance(v[d], str) or v[d] not in allowed[d] for d in DIMENSIONS):
                raise ValueError('A reviewed option is outside the declared inventory.')
            bound = accept(p, v)
            if not bound['accepted']:
                raise ValueError('Only a unique bounded single assertion can be confirmed. Withhold this sentence instead.')
            if (not v['kind'].startswith('metric_') and v['channel'] != 'none_or_unclear') or (v['kind'] != 'duration_material' and v['measure'] != 'none_or_unclear'):
                raise ValueError('Clear dimensions that do not apply to this assertion.')
            confirmed.append(identifier)
            changes = {d: {'from': original[identifier].get(d), 'to': v[d]} for d in DIMENSIONS if original[identifier].get(d) != v[d]}
            if changes: corrected.append({'sentence': identifier, 'changes': changes})
        elif review.get('decision') == 'withhold':
            if set(review) != {'decision', 'reason'} or review['reason'] not in ('non_assertion', 'multiple_assertions', 'unresolved', 'outside_policy'):
                raise ValueError('Choose a declared withholding reason.')
            withheld.append(identifier)
        else:
            raise ValueError('Choose confirm or withhold for every reviewed sentence.')
    request = reviewed_request(p, reviews)
    return {'note_id': p['id'], 'complete': set(reviews) == ids, 'confirmed': confirmed, 'withheld': withheld,
        'corrections': corrected, 'request': request,
        'request_sha256': sha(json.dumps(request, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()) if request else None,
        'status': 'local_preview_only', 'provider_calls': 0,
        'limits': 'Choices are structurally validated, not independently verified. Export records final decisions, not measured review time or intermediate edits.'}


def read_export(path):
    def unique(pairs):
        value = {}
        for k, v in pairs:
            if k in value: raise ValueError('Duplicate review JSON key.')
            value[k] = v
        return value
    def invalid(value): raise ValueError('Non-finite JSON value.')
    return json.loads(Path(path).read_text(), object_pairs_hook=unique, parse_constant=invalid)
