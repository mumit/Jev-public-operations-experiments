"""Pre-measurement controlled notes; preserve frozen binding/verdict semantics."""
import copy
import json
from .public_data import sha
from .public_evidence_data import select
from .public_evidence_features import card
from .public_claim_features import DURATIONS, numeric, POLICY, CLASSES
from .public_claim_reference import evaluate
from .public_report_features import FIELDS, request as report_request
from .public_binding_features import request as binding_request

ARMS = ('bound', 'scoped')
# These sentences are fixed before opening any new telemetry. Choices depend only
# on case/service identity, never verdicts. They are authored controls, not reports
# collected from analysts or an independently reviewed language reference.
TEXT = {
    'metric_material': (
        '{s} has an eligible {channel} change whose absolute scaled magnitude is {test} three.',
        'The {channel} change at {s}, under the declared eligibility rule, has a magnitude {test} 3.',
        'Under the change policy, {s} registers an absolute scaled {channel} change {test} 3.0.',
    ),
    'metric_direction': (
        'The eligible signed {channel} change at {s} is {direction}.',
        'For {s}, the eligible {channel} change is {direction}.',
        '{s} records an eligible signed change in {channel} that is {direction}.',
    ),
    'duration_material': (
        'With eligible samples, {s} has an absolute relative change in {measure} {duration} 25%.',
        'Eligible measurements put the absolute relative {measure} change at {s} {duration} one quarter.',
        'For eligible samples of {s}, {measure} changes by {duration} 25% in absolute relative magnitude.',
    ),
    'span_adequacy': (
        '{s} has at least five recorded spans in each of the two windows.',
        'Both windows for {s} contain five or more recorded spans.',
        'Neither recorded window count for {s} is below five spans.',
    ),
    'causality': (
        '{s} caused the incident described by these observations.',
        'The observed incident originated in {s}.',
        'The incident was caused by {s}.',
    ),
    'health': (
        'The supplied measurements establish that {s} is healthy.',
        'These observations establish the health of {s}: the service is healthy.',
        '{s} is healthy, as established by the supplied observations.',
    ),
}


def digest(value):
    return int(sha(value.encode()), 16)


def strongest_channel(observation):
    eligible = [k for k, v in observation['metrics'].items()
                if numeric(v.get('signed_change')) and all(numeric(v.get(f)) and 0 <= v[f] <= .2
                for f in ('before_missing_fraction', 'after_missing_fraction'))]
    names = eligible or sorted(observation['metrics'])
    if not names:
        raise ValueError('No observed metric channel.')
    return min(names, key=lambda k: (-abs(observation['metrics'][k]['signed_change'])
               if k in eligible else 0, k))


def compose(source, dataset):
    chosen = select(source)
    observations = [card(source, service) for service, _ in chosen]
    if len(observations) != 2 or observations[0]['service'] == observations[1]['service']:
        raise ValueError('Two distinct observed services required.')
    kinds = ('metric_material', 'duration_material', 'causality',
             'metric_direction', 'span_adequacy', 'health')
    claims, annotations, refs = {}, {}, {}
    for i, (field, kind) in enumerate(zip(FIELDS, kinds)):
        obs = observations[0 if i < 3 else 1]
        identity = source['id'] + '::' + field
        asserted = True if kind in ('causality', 'health', 'span_adequacy') else digest(identity) % 2 == 0
        prop = {'kind': kind, 'asserted': asserted}
        if kind in ('metric_material', 'metric_direction'):
            prop['channel'] = strongest_channel(obs)
        if kind == 'duration_material':
            prop['measure'] = DURATIONS[digest(identity + '::measure') % len(DURATIONS)]
        phrase = TEXT[kind][digest(identity + '::wording') % len(TEXT[kind])]
        claims[field] = phrase.format(s=obs['service'], channel=prop.get('channel'),
            measure=prop.get('measure'), test='at least' if asserted else 'below',
            direction='greater than zero' if asserted else 'zero or negative',
            duration='at least' if asserted else 'less than')
        annotations[field] = {'service': obs['service'], 'selection': chosen[0 if i < 3 else 1][1]}
        refs[field] = {**evaluate(obs, prop), 'service': obs['service']}
    identifier = 'FRC-' + sha(source['id'].encode())[:12]
    packet = {'id': identifier, 'case_id': source['id'], 'dataset': dataset,
              'observations': observations, 'statements': claims, 'claim_sources': annotations}
    # Reuse the exact frozen numerical policy, instructions and Choice criteria.
    # All questions bind an exact sentence/service; no inferred text extraction.
    packet['requests'] = {'report': report_request(observations, claims, 'report')}
    state = json.loads(packet['requests']['report']['state'])
    state['report'] = 'Operations note. Each sentence below is a separate assertion.\n' + '\n'.join(claims.values())
    packet['requests']['report']['state'] = json.dumps(state, sort_keys=True, separators=(',', ':'), allow_nan=False)
    bound = binding_request(packet, 'bound')
    scoped = {f: {'scoped': binding_request(packet, 'scoped', f)} for f in FIELDS}
    packet['requests'] = {'bound': bound}
    packet['claim_requests'] = scoped
    report = state['report']
    spans = {}
    cursor = 0
    for field, sentence in claims.items():
        start = report.index(sentence, cursor)
        spans[field] = {'start': start, 'end': start + len(sentence), 'service': annotations[field]['service']}
        cursor = start + len(sentence)
    # Supplied span metadata is an authoring audit, not an extractor score.
    packet['supplied_bindings'] = spans
    return packet, {'id': identifier, 'answers': refs}


def bodies(packet):
    return [packet['requests']['bound']] + [packet['claim_requests'][f]['scoped'] for f in FIELDS]
