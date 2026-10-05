"""Lossless trace table encoding for the second, pre-inference sizing protocol."""
import copy

COLUMNS = ('spans', 'distinct_traces', 'duration_median_us', 'duration_p90_us',
           'uncovered_duration_median_us', 'uncovered_duration_p90_us',
           'status_code_counts', 'status_missing_fraction')


def compact(context):
    result = copy.deepcopy(context)
    result['service_columns'] = list(COLUMNS)
    result['services'] = {name: {window: [values[key] for key in COLUMNS]
                                for window, values in observations.items()}
                          for name, observations in context['services'].items()}
    return result


def expand(context):
    result = copy.deepcopy(context)
    columns = result.pop('service_columns')
    if columns != list(COLUMNS):
        raise ValueError('Trace columns changed.')
    result['services'] = {name: {window: dict(zip(columns, values, strict=True))
                                for window, values in observations.items()}
                          for name, observations in context['services'].items()}
    return result
