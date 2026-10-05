"""Two evidence representations for independent written-claim judgments."""
import copy,json,math
from .profile import MODEL
ARMS=('observations','ledger')
FIELDS=('statement_a','statement_b','statement_c')
CLASSES=('supported','contradicted','unanswerable')
POLICY={'metric_magnitude':3.,'maximum_missing_fraction':.2,'minimum_spans_per_window':5,'duration_relative_change':.25,'display_probability':.7}
DURATIONS=('duration_median_us','duration_p90_us','uncovered_duration_median_us','uncovered_duration_p90_us')

def numeric(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)

def ledger(observation):
    metrics=[]
    for name,v in observation['metrics'].items():
        eligible=numeric(v.get('signed_change')) and all(numeric(v.get(k)) and 0<=v[k]<=.2 for k in ('before_missing_fraction','after_missing_fraction'))
        metrics.append({'channel':name,**copy.deepcopy(v),'eligible_for_change_policy':eligible,'absolute_scaled_change':abs(v['signed_change']) if numeric(v.get('signed_change')) else None})
    trace=observation['trace'];durations=[]
    b=None if trace is None else trace['before']['spans'];a=None if trace is None else trace['after']['spans']
    for name in DURATIONS:
        bv=None if trace is None else trace['before'][name];av=None if trace is None else trace['after'][name]
        eligible=numeric(b) and numeric(a) and b>=5 and a>=5 and numeric(bv) and numeric(av) and bv>0
        durations.append({'measure':name,'before_us':bv,'after_us':av,'eligible_for_change_policy':eligible,'relative_change':(av-bv)/bv if eligible else None})
    return {'service':observation['service'],'window_seconds':copy.deepcopy(observation['window_seconds']),
        'metric_change_definition':observation['metric_change_definition'],'condition':observation['condition'],
        'metric_facts':metrics,'trace_observations':copy.deepcopy(trace),'recorded_span_counts':{'before':b,'after':a},'duration_facts':durations,
        'limits':'Missing observations remain unknown. Recorded changes do not establish health, success of all requests, or incident causality.'}

def request(observation,statements,arm):
    if arm not in ARMS or set(statements)!=set(FIELDS):raise ValueError('Claim request identity.')
    state=copy.deepcopy(observation) if arm=='observations' else ledger(observation)
    instructions=('Judge the single written statement against only the supplied service observations. '
        'Use supported when the evidence establishes the statement; contradicted when eligible evidence establishes its opposite; '
        'unanswerable when neither follows. Missing data is unknown, not proof of health, success or failure. '
        'A metric is eligible for the change policy only when signed_change is numeric and BOTH missing fractions are numeric in [0,0.20]. '
        'Material metric change means abs(signed_change)>=3.0; decreases count. '
        'Duration change eligibility requires at least 5 recorded spans in EACH window, numeric before and after, and before>0. '
        'Material duration change means abs((after-before)/before)>=0.25. '
        'Counts describe recorded samples only, not complete instrumentation. A numerical change alone does not establish a cause. '
        'For a threshold or direction claim about an ineligible metric/duration, select unanswerable. '
        'Do not use outside knowledge or guess an injected fault. Statement: ')
    return {'model':MODEL,'state':json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False),
        'questions':{field:{'type':'choice','instructions':instructions+statements[field],
            'criteria':{'supported':'The supplied eligible evidence establishes the written statement.',
                        'contradicted':'The supplied eligible evidence establishes the opposite of the written statement.',
                        'unanswerable':'The supplied observations cannot establish either the statement or its opposite.'}} for field in FIELDS}}
