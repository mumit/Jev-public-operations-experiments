"""New controlled wording; fixed earlier meanings and family-only treatment."""
import copy
import json
from .public_data import sha
from .public_note_features import candidates
from .public_note_v2_features import extraction_request as baseline
from .public_contrast_features import MEANING

ARMS = ('baseline', 'meaning')
FORMS = ('plain', 'negated', 'boundary')


def compose(old, reference, form):
    if form not in FORMS:
        raise ValueError('Unknown note wording.')
    refs = {a['category']: a for a in reference['annotations']}
    a, b = refs['a_metric']['service'], refs['b_metric']['service']
    p0, p1, p3 = (refs[k]['proposition'] for k in ('a_metric', 'a_duration', 'b_metric'))
    ch, measure, direction = p0['channel'], p1['measure'], p3['channel']
    if form == 'plain':
        texts = [
            'Shift summary.',
            f"{a}'s eligible {ch} metric has an absolute scaled change {'of at least' if p0['asserted'] else 'below'} 3.0.",
            f"For this service, the eligible {measure} absolute relative change is {'no less than' if p1['asserted'] else 'less than'} 25%.",
            'This service brought about the incident.',
            f'Please investigate {b} next.',
            f"{b}'s eligible {direction} signed change is {'positive' if p3['asserted'] else 'nonpositive'}.",
            'For that service, each recorded window contains at least five spans.',
            'The same service is in a healthy state.',
            f'Is {a} healthy now?',
            f'The previous ticket attributed the incident to {a}, but this note does not adopt that attribution.',
            f'{a} brought about the incident while {b} is healthy.',
            f'Either {a} or {b} is unhealthy.',
        ]
    elif form == 'negated':
        texts = [
            'Handover brief.',
            f"The absolute scaled change in {a}'s eligible {ch} metric {'is not below' if p0['asserted'] else 'does not reach'} 3.0.",
            f"Its eligible {measure} change, in absolute relative terms, is {'not below' if p1['asserted'] else 'below'} 25%.",
            'This service caused the incident.',
            f'Would you check {b} after the handover?',
            f"For {b}, the eligible signed {direction} change is {'not zero or negative' if p3['asserted'] else 'not greater than zero'}.",
            'Neither recorded window for this service has fewer than five spans.',
            'That service is healthy.',
            f'Could {a} be healthy?',
            f"Do not treat the earlier \"{a} caused the incident\" quotation as this handover's conclusion.",
            f"{a} is the incident's cause, and {b} remains healthy.",
            f'One of these services, {a} or {b}, is unhealthy.',
        ]
    else:
        texts = [
            'Status note.',
            f"{a} {'meets' if p0['asserted'] else 'falls short of'} the eligible {ch} absolute-scaled-change cutoff of 3.0.",
            f"The same service {'meets' if p1['asserted'] else 'falls short of'} the 25% absolute-relative-change cutoff for eligible {measure}.",
            'I attribute the incident to this service.',
            f'Next action: inspect {b}.',
            f"{b} has eligible {direction} signed change {'above' if p3['asserted'] else 'at or below'} 0.",
            'Both windows for this service meet the recorded-count minimum of 5 spans.',
            'This service is healthy.',
            f'Does {a} qualify as healthy?',
            f'A previous note blamed {a}; that allegation remains unendorsed here.',
            f'{a} caused the incident; {b} is healthy.',
            f'The unhealthy service is one of {a} and {b}.',
        ]
    categories = ('header', 'a_metric', 'a_duration', 'a_cause', 'b_check', 'b_metric', 'b_count', 'b_health', 'question', 'quotation', 'compound', 'ambiguous')
    entries = list(zip(categories, texts))
    identifier = 'NWL-' + sha((old['id'] + '::' + form).encode())[:12]
    if int(sha(identifier.encode()), 16) % 2:
        entries = entries[:1] + entries[4:8] + entries[1:4] + entries[8:]
    note = '\n'.join(t for _, t in entries)
    spans = candidates(note)
    if len(spans) != 12 or [s['text'] for s in spans] != [t for _, t in entries]:
        raise ValueError('Generic sentence boundaries disagree with controlled text.')
    annotations = []
    for span, (category, _) in zip(spans, entries):
        annotation = copy.deepcopy(refs[category])
        annotation.update(span)
        annotations.append(annotation)
    packet = {'id': identifier, 'source_report_id': old['source_report_id'], 'parent_note_id': old['id'],
        'dataset': old['dataset'], 'wording': form, 'note': note, 'candidates': spans,
        'observations': copy.deepcopy(old['observations']), 'services': copy.deepcopy(old['services']), 'channels': copy.deepcopy(old['channels'])}
    packet['extraction_request'] = baseline(packet)
    return packet, {'id': identifier, 'annotations': annotations}


def extraction_request(packet, arm):
    if arm not in ARMS:
        raise ValueError('Unknown input.')
    body = copy.deepcopy(packet['extraction_request'])
    if arm == 'meaning':
        state = json.loads(body['state'])
        state['extraction_definitions']['kind'] = MEANING
        body['state'] = json.dumps(state, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return body


def validate_changes(packet):
    before = json.loads(packet['extraction_request']['state'])
    body = extraction_request(packet, 'meaning'); after = json.loads(body['state'])
    if after['extraction_definitions']['kind'] != MEANING or body['questions'] != packet['extraction_request']['questions'] or body['model'] != packet['extraction_request']['model']:
        raise ValueError('Unplanned task change.')
    after['extraction_definitions']['kind'] = before['extraction_definitions']['kind']
    if after != before or extraction_request(packet, 'baseline') != packet['extraction_request']:
        raise ValueError('Unplanned note or definition change.')
