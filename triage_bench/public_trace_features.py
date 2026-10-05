"""Trace observations only: source IDs/operations/answers never enter summaries."""
import copy,json
from collections import Counter,defaultdict
from io import BytesIO
from .public_data import percentile,sha

FIELDS=('traceID','spanID','parentSpanID','serviceName','startTime','startTimeMillis','duration','statusCode')
CACHE={}

def uncovered(start,duration,children):
    """Subtract the union of observed immediate child intervals, clipped to the parent."""
    end=start+duration;intervals=sorted((max(start,s),min(end,s+d)) for s,d in children if min(end,s+d)>max(start,s))
    covered=0;left=right=None
    for a,b in intervals:
        if left is None:left,right=a,b
        elif a>right:covered+=right-left;left,right=a,b
        else:right=max(right,b)
    if left is not None:covered+=right-left
    return duration-covered

def summarize_rows(rows,boundary,start,end,candidates):
    records={};children=defaultdict(list)
    for source in rows:
        r={key:source.get(key) for key in FIELDS};key=(r['traceID'],r['spanID'])
        if not all(isinstance(r[k],str) and r[k] for k in ('traceID','spanID','serviceName')) or r['parentSpanID'] is not None and not isinstance(r['parentSpanID'],str):raise ValueError('Invalid trace identifiers.')
        if any(isinstance(r[k],bool) or not isinstance(r[k],int) for k in ('startTime','startTimeMillis','duration')) or r['duration']<0 or r['startTime']//1000!=r['startTimeMillis']:raise ValueError('Invalid trace time/duration schema.')
        if r['statusCode'] is not None and (isinstance(r['statusCode'],bool) or not isinstance(r['statusCode'],int)):raise ValueError('Invalid source status code.')
        if key in records:raise ValueError('Duplicate trace/span identity; do not choose a row silently.')
        records[key]=r
    for key,r in records.items():
        if r['parentSpanID']:
            parent=(r['traceID'],r['parentSpanID'])
            if parent==key:raise ValueError('Self-parent span.')
            if parent in records:children[parent].append((r['startTime'],r['duration']))
    # A cyclic parent graph is invalid even if timestamps happen to overlap.
    done=set()
    for key in records:
        chain=set();current=key
        while current in records and current not in done:
            if current in chain:raise ValueError('Cyclic parent graph.')
            chain.add(current);r=records[current];current=(r['traceID'],r['parentSpanID']) if r['parentSpanID'] else None
        done.update(chain)
    grouped=defaultdict(list);edges=defaultdict(lambda:[0,0]);coverage={w:Counter() for w in ('before','after')};unmapped=Counter();outside=0
    for key,r in records.items():
        t=r['startTime']
        if not start*1_000_000<=t<(end+1)*1_000_000:outside+=1;continue
        window='before' if t<boundary*1_000_000 else 'after';slot=0 if window=='before' else 1;c=coverage[window];c['spans']+=1
        matched=r['serviceName'] in candidates
        if matched:c['mapped_spans']+=1
        else:unmapped[r['serviceName']]+=1
        parent=records.get((r['traceID'],r['parentSpanID'])) if r['parentSpanID'] else None
        if not r['parentSpanID']:c['root_spans']+=1
        elif parent is None:c['unresolved_parent_spans']+=1
        else:
            c['linked_parent_spans']+=1
            if matched and parent['serviceName'] in candidates and parent['serviceName']!=r['serviceName']:
                edges[(parent['serviceName'],r['serviceName'])][slot]+=1
        if t+r['duration']>(boundary if window=='before' else end+1)*1_000_000:c['spans_crossing_window_end']+=1
        if matched:grouped[(r['serviceName'],window)].append((r,uncovered(t,r['duration'],children[key])))
    services={}
    for service in sorted(candidates):
        observations={}
        for window in ('before','after'):
            values=grouped[(service,window)];durations=[r['duration'] for r,u in values];residuals=[u for r,u in values];codes=Counter(str(r['statusCode']) for r,u in values if r['statusCode'] is not None)
            def rounded(v):return None if v is None else float(format(v,'.8g'))
            observations[window]={'spans':len(values),'distinct_traces':len({r['traceID'] for r,u in values}),
                'duration_median_us':rounded(percentile(durations,.5)),'duration_p90_us':rounded(percentile(durations,.9)),
                'uncovered_duration_median_us':rounded(percentile(residuals,.5)),'uncovered_duration_p90_us':rounded(percentile(residuals,.9)),
                'status_code_counts':dict(sorted(codes.items())),'status_missing_fraction':sum(r['statusCode'] is None for r,u in values)/len(values) if values else None}
        if any(observations[w]['spans'] for w in ('before','after')):services[service]=observations
    return {'condition':'Observed trace context from the same supplied metric interval. Exact service-name matches only; all metric candidates stay unchanged.',
       'definitions':{'span':'Recorded work interval, not necessarily an incoming request or a complete transaction. Counts may change with traffic or trace sampling.',
        'duration_units':'startTime and duration use Jaeger microseconds. startTime//1000 must equal startTimeMillis.',
        'windows':'Classify by span start. Before: metric start <= start < boundary. After: boundary <= start < last metric second + 1. Counts include spans crossing a window end; durations describe complete recorded spans.',
        'uncovered_duration':'Span duration minus the union of observed immediate child intervals, clipped to the parent. It includes unrecorded work or children and is not CPU time or proof of local cause.',
        'dependency':'Parent service to child service for resolved cross-service span links. A recorded link allows propagation; it does not prove causal fault origin or a complete synchronous call graph.',
        'status_codes':'Uninterpreted source statusCode counts. Source semantics can differ. Null means unavailable, not success. No universal success/error classification is imposed.',
        'coverage':'A service absent from these summaries has no mapped recorded span, not evidence of health. Missing parents and uninstrumented candidates are unknown, not absent dependencies.'},
       'coverage':{w:{k:coverage[w][k] for k in ('spans','mapped_spans','root_spans','linked_parent_spans','unresolved_parent_spans','spans_crossing_window_end')} for w in ('before','after')},
       'outside_interval_spans':outside,'unmapped_trace_services':dict(sorted(unmapped.items())),
       'candidates_without_spans':[s for s in sorted(candidates) if s not in services],'services':services,
       'dependency_columns':['parent_service','child_service','before_links','after_links'],
       'dependencies':[[a,b,*counts] for (a,b),counts in sorted(edges.items())]}

def summarize(raw,boundary,start,end,candidates):
    import pyarrow.parquet as pq
    key=(sha(raw),boundary,start,end,tuple(sorted(candidates)))
    if key not in CACHE:
        rows=pq.read_table(BytesIO(raw),columns=list(FIELDS)).to_pylist();value=summarize_rows(rows,boundary,start,end,candidates)
        if len(CACHE)>=32:CACHE.clear()
        CACHE[key]=value
    return copy.deepcopy(CACHE[key])

def augment(state,context):
    result=copy.deepcopy(state);result['trace_context']=copy.deepcopy(context);return result

def trace_ranking(context,candidates):
    """A fixed median uncovered-duration ratio, not a fitted causal model."""
    ranking=[]
    for service in candidates:
        row=context['services'].get(service,{});before=row.get('before',{});after=row.get('after',{})
        a=before.get('uncovered_duration_median_us');b=after.get('uncovered_duration_median_us')
        score=max(0.,b-a)/max(a,1.) if a is not None and b is not None and before.get('spans',0)>=5 and after.get('spans',0)>=5 else None
        ranking.append({'service':service,'score':score})
    ranking.sort(key=lambda r:(-(r['score'] if r['score'] is not None else -1),r['service']))
    return {'choice':ranking[0]['service'] if ranking and ranking[0]['score'] is not None and ranking[0]['score']>0 else 'insufficient_evidence','ranking':ranking,'note':'Positive relative increase in median uncovered span duration with at least five spans in both windows. Missing coverage cannot rank as a healthy service.'}
