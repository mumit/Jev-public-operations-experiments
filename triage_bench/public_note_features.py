"""Frozen controlled prose, sentence candidates and typed extraction composition."""
import copy
import json
import re
from .profile import MODEL
from .public_data import sha
from .public_claim_features import DURATIONS, ledger, request as claim_request

ARMS = ('jev', 'parser', 'annotated')
DIMENSIONS = ('role', 'service', 'kind', 'channel', 'measure', 'polarity')
KINDS = ('metric_material', 'metric_direction', 'duration_material', 'span_adequacy', 'health', 'causality', 'unmapped')
BOUNDARY = .70


def candidates(note):
    """Generic boundaries, independent of annotations; decimal points stay intact."""
    result, cursor = [], 0
    for part in re.split(r'(?<=[.!?])\s+', note):
        text = part.strip()
        if not text:
            continue
        start = note.index(text, cursor)
        result.append({'id': 's%02d' % (len(result) + 1), 'text': text, 'start': start, 'end': start + len(text)})
        cursor = start + len(text)
    return result


def compose(old, reference, observations):
    """Author prose from the six earlier meanings, without selecting by verdict."""
    fields = tuple(old['statements'])
    a, b = [o['service'] for o in old['observations']]
    props = [copy.deepcopy(reference['answers'][f]['proposition']) for f in fields]
    p0, p1, _, p3, _, _ = props
    sentences = [
        ('header', 'Operations handover.', None),
        ('a_metric', f"{a} has an eligible {p0['channel']} change with absolute scaled magnitude {'at least' if p0['asserted'] else 'below'} 3.0.", 0),
        ('a_duration', f"For the same service, eligible {p1['measure']} samples show an absolute relative change {'at least' if p1['asserted'] else 'less than'} 25%.", 1),
        ('a_cause', 'This service caused the incident.', 2),
        ('b_check', f'Check {b} after the handover.', None),
        ('b_metric', f"{b} has an eligible signed {p3['channel']} change that is {'greater than zero' if p3['asserted'] else 'zero or negative'}.", 3),
        ('b_count', 'Its recorded span count reaches five in both windows.', 4),
        ('b_health', 'That service is healthy.', 5),
        ('question', f'Did {a} become healthy?', None),
        ('quotation', f'The earlier ticket said, "{a} caused this incident", but the handover does not endorse that claim.', None),
        ('compound', f'{a} caused the incident and {b} is healthy.', None),
        ('ambiguous', f'One of {a} and {b} is unhealthy.', None),
    ]
    # Swap complete blocks, preserving local antecedents. This changes placement,
    # never meanings or class balance based on evidence truth.
    if int(sha(old['id'].encode()), 16) % 2:
        sentences = sentences[:1] + sentences[4:8] + sentences[1:4] + sentences[8:]
    note = '\n'.join(s[1] for s in sentences)
    spans = candidates(note)
    if len(spans) != len(sentences) or [s['text'] for s in spans] != [s[1] for s in sentences]:
        raise ValueError('Sentence authoring and generic boundaries disagree.')
    annotations = []
    for candidate, (category, _, index) in zip(spans, sentences):
        role = 'assertion' if index is not None or category == 'ambiguous' else 'multiple_assertions' if category == 'compound' else 'non_assertion'
        annotation = {**candidate, 'category': category, 'role': role, 'actionable': index is not None,
                      'service': 'ambiguous' if category == 'ambiguous' else 'none',
                      'kind': 'health' if category == 'ambiguous' else 'unmapped',
                      'channel': 'none_or_unclear', 'measure': 'none_or_unclear',
                      'polarity': 'negative' if category == 'ambiguous' else 'unclear'}
        if index is not None:
            prop = props[index]
            annotation.update(service=a if index < 3 else b, kind=prop['kind'],
                channel=prop.get('channel', 'none_or_unclear'), measure=prop.get('measure', 'none_or_unclear'),
                polarity='positive' if prop['asserted'] else 'negative',
                verdict=reference['answers'][fields[index]]['answer'], proposition=prop,
                facts=reference['answers'][fields[index]]['facts'])
        annotations.append(annotation)
    packet = {'id': 'NEX-' + sha(old['id'].encode())[:12], 'source_report_id': old['id'], 'dataset': old['dataset'],
              'note': note, 'candidates': spans, 'observations': observations,
              'services': sorted(o['service'] for o in observations),
              'channels': sorted({name for o in observations for name in o['metrics']})}
    packet['extraction_request'] = extraction_request(packet)
    return packet, {'id': packet['id'], 'annotations': annotations}


def extraction_request(packet):
    state = {'note': packet['note'], 'candidates': packet['candidates'],
             'observed_service_inventory': packet['services'], 'metric_channel_inventory': packet['channels']}
    questions = {}
    for i, candidate in enumerate(packet['candidates']):
        intro = (f'Read candidates[{i}].text in the full note context. Identify what the sentence says, '
                 'not whether telemetry would establish it. Resolve a pronoun only from an unambiguous antecedent in this note. ')
        definitions = {
            'role': ('Classify its speech act. An endorsed factual assertion is assertion. A question, requested check, heading, '
                     'or quotation explicitly not endorsed is non_assertion. Two or more independently checkable assertions in '
                     'one sentence are multiple_assertions, even if about one service.', {
                'assertion': 'One endorsed factual assertion.', 'non_assertion': 'No endorsed factual assertion.',
                'multiple_assertions': 'At least two independently checkable endorsed assertions.'}),
            'service': ('Which single service is the subject of the endorsed assertion? Use the service inventory. '
                        'Select ambiguous for unresolved subjects or multiple service subjects. Select none for non-assertions.', {
                **{s: 'This service is the unique subject.' for s in packet['services']},
                'ambiguous': 'No unique service can be resolved.', 'none': 'No endorsed assertion.'}),
            'kind': ('Identify the assertion family. metric_material compares absolute scaled change to exactly 3.0; '
                     'metric_direction compares eligible signed change to zero; duration_material compares absolute relative '
                     'duration change to exactly 25%; span_adequacy concerns at least five recorded spans in each window; '
                     'health asserts service health or unhealth; causality asserts incident origin. Use unmapped for other '
                     'thresholds, non-assertions or multiple assertion families.', {
                'metric_material': 'Absolute scaled metric change at the inclusive three-unit boundary.',
                'metric_direction': 'Positive signed metric change versus zero or negative.',
                'duration_material': 'Absolute relative duration change at the inclusive 25% boundary.',
                'span_adequacy': 'At least five recorded spans in each window.',
                'health': 'The service is healthy or unhealthy.', 'causality': 'The service caused or did not cause the incident.',
                'unmapped': 'Outside these single-assertion definitions.'}),
            'channel': ('Which metric channel does this assertion name? Select none_or_unclear for other assertion types, '
                        'non-assertions, multiple channels or an unnamed channel.', {
                **{c: 'The assertion names this metric channel.' for c in packet['channels']},
                'none_or_unclear': 'No uniquely named metric channel.'}),
            'measure': ('Which duration measure does this assertion name? Select none_or_unclear when not a duration assertion, '
                        'not named or not uniquely resolvable.', {
                **{m: 'The assertion names this duration measure.' for m in DURATIONS},
                'none_or_unclear': 'No uniquely named duration measure.'}),
            'polarity': ('Select positive when it asserts the defined positive property: magnitude >=3, signed change >0, '
                         'duration magnitude >=25%, >=5 spans in EACH window, healthy, or caused the incident. Select negative '
                         'for the opposite: below 3, zero or negative, less than 25%, a window below five, unhealthy, or did not '
                         'cause the incident. Select unclear for non-assertions, multiple assertions or unmapped meanings.', {
                'positive': 'Asserts the defined positive property.', 'negative': 'Asserts its opposite.',
                'unclear': 'No unique mapped polarity.'}),
        }
        for dimension in DIMENSIONS:
            text, criteria = definitions[dimension]
            questions[candidate['id'] + '_' + dimension] = {'type': 'choice', 'instructions': intro + text, 'criteria': criteria}
    return {'model': MODEL, 'state': json.dumps(state, sort_keys=True, separators=(',', ':'), allow_nan=False), 'questions': questions}


def accept(packet, values, probabilities=None):
    required = ['role', 'service', 'kind', 'polarity']
    reason = None
    if values.get('role') != 'assertion':
        reason = 'not_single_assertion'
    elif values.get('service') not in packet['services']:
        reason = 'unresolved_service'
    elif values.get('kind') not in KINDS[:-1] or values.get('polarity') not in ('positive', 'negative'):
        reason = 'unmapped_meaning'
    elif values['kind'].startswith('metric_'):
        required.append('channel')
        if values.get('channel') not in packet['channels']:
            reason = 'unresolved_channel'
    elif values['kind'] == 'duration_material':
        required.append('measure')
        if values.get('measure') not in DURATIONS:
            reason = 'unresolved_measure'
    probability = min((probabilities.get(k, 0) for k in required), default=0) if probabilities is not None else None
    if not reason and probability is not None and probability < BOUNDARY:
        reason = 'low_extraction_probability'
    return {**values, 'accepted': not bool(reason), 'review_reason': reason, 'minimum_required_probability': probability}


def extraction(packet, answers):
    return {c['id']: accept(packet, {d: answers.get(c['id'] + '_' + d, {}).get('choice', 'unavailable') for d in DIMENSIONS},
        {d: a.get('probabilities', {}).get(a.get('choice'), 0) for d in DIMENSIONS
         for a in [answers.get(c['id'] + '_' + d, {})]}) for c in packet['candidates']}


def parser(packet):
    """Conservative literal parser: no fitting, pronoun resolution or probabilities."""
    results = {}
    for c in packet['candidates']:
        text = c['text']; lower = text.lower()
        names = [s for s in packet['services'] if re.search(r'(?<![\w-])' + re.escape(s) + r'(?![\w-])', text)]
        channels = [s for s in packet['channels'] if re.search(r'(?<![\w-])' + re.escape(s) + r'(?![\w-])', text)]
        measures = [s for s in DURATIONS if s in text]
        role = 'non_assertion' if (text.endswith('?') or lower.startswith('check ') or 'does not endorse' in lower or lower == 'operations handover.') else 'multiple_assertions' if (' caused ' in lower and ' is healthy' in lower) else 'assertion'
        kind = ('metric_material' if 'absolute scaled magnitude' in lower and re.search(r'\b3\.0\b', lower) else
                'metric_direction' if 'signed' in lower and ('greater than zero' in lower or 'zero or negative' in lower) else
                'duration_material' if 'absolute relative change' in lower and '25%' in lower else
                'span_adequacy' if 'span count reaches five in both windows' in lower else
                'health' if 'healthy' in lower else 'causality' if 'caused the incident' in lower else 'unmapped')
        values = {'role': role, 'service': names[0] if len(names) == 1 else 'ambiguous' if role == 'assertion' else 'none',
                  'kind': kind, 'channel': channels[0] if len(channels) == 1 else 'none_or_unclear',
                  'measure': measures[0] if len(measures) == 1 else 'none_or_unclear',
                  'polarity': 'negative' if any(s in lower for s in ('below', 'less than', 'zero or negative', 'unhealthy', 'did not cause')) else 'positive'}
        if role != 'assertion':
            values.update(kind='unmapped', polarity='unclear', service='ambiguous' if role == 'multiple_assertions' else 'none')
        results[c['id']] = accept(packet, values)
    return results


def annotated(packet, reference):
    results = {}
    for annotation in reference['annotations']:
        values = {d: annotation[d] for d in DIMENSIONS}
        results[annotation['id']] = accept(packet, values)
    return results


def semantics(values):
    return tuple(values.get(k) for k in ('kind', 'polarity')) + ((values.get('channel'),) if str(values.get('kind')).startswith('metric_') else (values.get('measure'),) if values.get('kind') == 'duration_material' else ())


def verdict_request(packet, bindings):
    accepted = [c for c in packet['candidates'] if bindings[c['id']]['accepted']]
    if not accepted:
        return None
    observed = {o['service']: o for o in packet['observations']}
    services = sorted({bindings[c['id']]['service'] for c in accepted})
    control = claim_request(observed[services[0]], dict.fromkeys(('statement_a', 'statement_b', 'statement_c'), ''), 'ledger')
    prefix = control['questions']['statement_a']['instructions'].split('Statement: ')[0].replace('supplied service observations', 'supplied observations for its named service')
    criteria = control['questions']['statement_a']['criteria']
    return {'model': MODEL,
        'state': json.dumps({'note': packet['note'], 'services': [ledger(observed[s]) for s in services]}, sort_keys=True, separators=(',', ':'), allow_nan=False),
        'questions': {c['id'] + '_verdict': {'type': 'choice', 'instructions': prefix +
            f"Assess only the exact statement bound to service {bindings[c['id']]['service']}. Use only that service's facts. "
            'Resolve its pronoun using this binding and the full note context. Statement: ' + c['text'], 'criteria': copy.deepcopy(criteria)} for c in accepted}}
