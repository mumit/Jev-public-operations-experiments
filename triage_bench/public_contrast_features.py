"""Frozen speech-act and assertion-family contrasts on unchanged inspected notes."""
import copy
import json

ARMS = ('baseline', 'role', 'meaning', 'combined')
ROLE = (
    'Classify the endorsed speech act, not its truth, telemetry eligibility or evidence strength. '
    'assertion means one endorsed bounded policy assertion. An eligibility qualifier and its numeric '
    'condition form one policy assertion here. Positive, negative and zero values can all be asserted. '
    'For example, "A service has an eligible signed metric change at or below zero" and the positive '
    'version each assert one property. "Zero or negative" describes alternatives for that one property, '
    'not separate independently checkable assertions. "Recorded span count is at least five in each '
    'window" and "That service is healthy" each assert one property too. An unresolved subject or '
    'unproven truth does not change an assertion into a non-assertion. '
    'non_assertion means no endorsed factual assertion: a heading, requested check, question, or '
    'quotation explicitly not endorsed. "Investigate a service" is a request; "Is a service healthy?" '
    'is a question. multiple_assertions means at least two independently checkable endorsed assertions: '
    '"A service caused an incident and another service is healthy" has a cause assertion and a health '
    'assertion. The same distinction applies if both assertions concern one service. Count assertions, '
    'not service names: "One of two services is unhealthy" is one assertion with an ambiguous subject.'
)
MEANING = (
    'Map the single assertion family from the written property, not telemetry truth or operational '
    'implications. Both a defined positive property and its opposite belong to the same family; '
    'polarity is classified separately. '
    'metric_material compares eligible absolute scaled metric change with exactly 3.0 (at least or '
    'below); metric_direction compares eligible signed metric change with zero (greater than zero '
    'or zero/negative). The eligibility qualifier belongs to this bounded policy property. '
    'duration_material compares eligible absolute relative duration change with exactly 25% '
    '(at least or below). span_adequacy concerns at least five recorded spans in EACH window, '
    'or a window below five. A sentence about recorded span counts is span_adequacy; it does not '
    'assert service health. health requires an explicit assertion that a service is healthy or '
    'unhealthy, including "That service is healthy". Do not turn a count or numerical change into '
    'a health assertion. causality asserts that a service caused or did not cause the incident. '
    'Use unmapped for other thresholds, non-assertions or multiple assertion families. A sentence '
    'asserting both incident origin and service health has multiple families, even for one subject.'
)


def extraction_request(packet, arm):
    if arm not in ARMS:
        raise ValueError('Unknown extraction contrast.')
    body = copy.deepcopy(packet['extraction_request'])
    if arm == 'baseline':
        return body
    state = json.loads(body['state'])
    if arm in ('role', 'combined'):
        state['extraction_definitions']['role'] = ROLE
    if arm in ('meaning', 'combined'):
        state['extraction_definitions']['kind'] = MEANING
    body['state'] = json.dumps(state, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return body


def validate_changes(packet):
    original = packet['extraction_request']; before = json.loads(original['state'])
    for arm in ARMS:
        body = extraction_request(packet, arm); after = json.loads(body['state'])
        changed = {d for d in before['extraction_definitions'] if before['extraction_definitions'][d] != after['extraction_definitions'][d]}
        expected = set() if arm == 'baseline' else {'role'} if arm == 'role' else {'kind'} if arm == 'meaning' else {'role', 'kind'}
        if changed != expected or body['questions'] != original['questions'] or body['model'] != original['model']:
            raise ValueError('Contrast changed an unplanned question or definition.')
        after['extraction_definitions'] = before['extraction_definitions']
        if after != before or arm == 'baseline' and body != original:
            raise ValueError('Contrast changed notes, inventories or baseline bytes.')
