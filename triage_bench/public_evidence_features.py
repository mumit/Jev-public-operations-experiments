"""Service-level observations and independent bounded Jev questions."""
import copy
import json
from .profile import MODEL
from .public_trace_task_features import changes

ARMS = ('observations', 'calculated')
FIELDS = ('metric_change', 'trace_change', 'trace_coverage', 'metric_channel')
POLICY = {'metric_magnitude': 3., 'maximum_missing_fraction': .2,
          'duration_relative_change': .25, 'minimum_spans_per_window': 5,
          'display_probability': .7}
DURATIONS = ('duration_median_us', 'duration_p90_us', 'uncovered_duration_median_us', 'uncovered_duration_p90_us')


def card(packet, service):
    state = json.loads(packet['requests']['metrics']['state'])
    return {'service': service, 'metrics': copy.deepcopy(state['services'][service]),
            'metric_change_definition': state.get('signed_change_definition', 'Existing before-window scaled signed change.'),
            'trace': copy.deepcopy(packet['trace_context']['services'].get(service)),
            'window_seconds': copy.deepcopy(packet['trace_changes']['window_seconds']),
            'condition': 'Observed service during a supplied incident interval. Missing values are unknown. This task does not infer a cause or service health.'}


def additions(observation):
    context = {'services': {observation['service']: observation['trace']} if observation['trace'] is not None else {}}
    delta = changes(context, observation['window_seconds']['before'], observation['window_seconds']['after'])
    return {'trace_change_columns': delta['service_columns'],
            'trace_changes': delta['services'].get(observation['service']),
            'definitions': delta['definitions']}


def questions(metrics):
    eligibility = ('A metric is eligible only when signed_change is numeric and both before_missing_fraction '
                   'and after_missing_fraction are numeric and between 0 and 0.20 inclusive. Other metrics are ineligible. ')
    trace = ('Use only duration_median_us, duration_p90_us, uncovered_duration_median_us and uncovered_duration_p90_us. '
             'A duration is eligible only with at least 5 spans in EACH window, numeric before and after duration, '
             'and before duration >0. Relative change is (after-before)/before. ')
    intro = 'Classify this service using the stated numerical rule, not an injected-fault guess. Missing measurements are unknown. '
    return {
        'metric_change': {'type': 'choice', 'instructions': intro+eligibility+
            'Is any eligible metric changed by at least 3.0 in absolute signed_change units? Negative changes count. '
            'Select material if ANY eligible metric has abs(signed_change)>=3.0; otherwise select quiet if at least one metric is eligible; select unknown if none are eligible.',
            'criteria': {'material': 'At least one eligible metric reaches the inclusive 3.0 magnitude boundary.',
                         'quiet': 'Eligible metrics exist, and every eligible magnitude is below 3.0.',
                         'unknown': 'No metric meets the measurement eligibility conditions.'}},
        'trace_change': {'type': 'choice', 'instructions': intro+trace+
            'Select material if ANY eligible duration has abs(relative change)>=0.25, quiet if eligible durations exist but all magnitudes are below 0.25, or unknown if none are eligible. Ignore span-rate changes and status codes for this question.',
            'criteria': {'material': 'At least one eligible duration reaches the inclusive 25% change boundary.',
                         'quiet': 'Eligible durations exist, and all absolute relative changes are below 25%.',
                         'unknown': 'No eligible duration, including absent traces, insufficient samples or missing/nonpositive starting durations.'}},
        'trace_coverage': {'type': 'choice', 'instructions': intro+
            'Classify recorded span counts only. Select absent if trace is null or there are zero spans in BOTH windows. '
            'Select adequate if there are at least 5 spans in EACH window. Select limited otherwise. Adequate is a count flag, not complete instrumentation or statistical significance.',
            'criteria': {'adequate': 'At least 5 recorded spans before and at least 5 after.',
                         'limited': 'Some spans exist, but a window has fewer than 5.',
                         'absent': 'No recorded spans in either window, or trace is null.'}},
        'metric_channel': {'type': 'choice', 'instructions': intro+eligibility+
            'Which eligible metric has the greatest absolute signed_change? Consider increases and decreases. '
            'Choose any tied maximum. Select no_eligible_metric if none are eligible. This question applies even when the maximum is below 3.0.',
            'criteria': {**{name: 'This eligible metric has maximal absolute signed_change.' for name in metrics},
                         'no_eligible_metric': 'No metric is eligible.'}},
    }


def request(observation, arm):
    if arm not in ARMS:
        raise ValueError('Unknown evidence arm.')
    state = copy.deepcopy(observation)
    if arm == 'calculated':
        state['calculated_changes'] = additions(observation)
    return {'model': MODEL, 'state': json.dumps(state, sort_keys=True, separators=(',', ':'), allow_nan=False),
            'questions': questions(observation['metrics'])}


def compose(choices):
    """Code composes answers; parallel questions cannot see one another's replies."""
    if any(choices.get(field) not in {'material', 'quiet', 'unknown'} for field in ('metric_change','trace_change')):
        return 'unavailable'
    if 'material' in (choices['metric_change'], choices['trace_change']):
        return 'change_supported'
    if 'unknown' in (choices['metric_change'], choices['trace_change']):
        return 'evidence_limited'
    return 'no_material_change'
