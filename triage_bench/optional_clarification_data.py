"""New controlled wording and hand-declared optional-question references."""
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load
from .public_rca_data import dump
from .clarification_data import contexts
from .optional_clarification_features import request,PRIORITY

PLAN=ROOT/'checkpoints/optional-clarification-plan-2026-10-06.json'
BASE=ROOT/'runs/optional-clarification'
DATA=BASE/'development-data-2026-10-06-v1'
FAMILIES=[
 ('explicit_magnitude',(),[
  'The CPU comparison for {s} covers the incident windows, before versus after. I assert that the absolute scaled difference reaches 3.0 or more.',
  'Using the before-incident and after-incident windows, does {s} have material scaled processor-utilization change?']),
 ('explicit_direction',(),[
  'Compare CPU for {s} after the incident against its before-incident observations. The signed scaled difference exceeds zero.',
  'For {s}, check whether processor utilization has positive signed scaled change from before this incident to after it.']),
 ('single_antecedent',(),[
  'The note concerns {s}. Its CPU crosses the material scaled-change threshold between the before-incident and after-incident windows.',
  'Only {s} is in this claim. Does its signed CPU change exceed zero when the after-incident observations are compared with the before-incident ones?']),
 ('explicit_negation',(),[
  'Between the before-incident and after-incident windows, the absolute scaled CPU difference for {s} stays below 3.0.',
  'Compare {s} before with after this incident: its signed processor-utilization change is zero or negative.']),
 ('final_correction',(),[
  'For {s}, I initially requested a material CPU comparison. Replace that request with a positive signed CPU-change check across the before-incident and after-incident windows.',
  'The earlier CPU note for {s} denied material scaled change. Disregard that note: my final assertion is material scaled change, using the before/after incident comparison.']),
 ('incidental_background',(),[
  'A separate note mentions {t}. The subject of this claim is {s}, whose CPU has material scaled change from before the incident to after it.',
  '{t} belongs to another ticket. This check names {s}: does its signed processor-utilization change exceed zero between the before/after incident windows?']),
 ('omitted_service',('service',),[
  'The before-incident versus after-incident CPU comparison shows an absolute scaled difference of at least 3.0.',
  'Check whether processor utilization has positive signed scaled change across the before/after incident windows. I have not named a service.']),
 ('competing_antecedents',('service',),[
  '{s} and {t} both appear in this note. Its CPU has material scaled change between the before-incident and after-incident windows.',
  'The two candidates are {s} and {t}. Is its signed CPU change positive across the before/after incident comparison?']),
 ('undeclared_service_alias',('service',),[
  'Across the before/after incident comparison, the front-door handler has material scaled CPU change.',
  'Check positive signed processor-utilization change for the primary backend, comparing the before-incident and after-incident observations.']),
 ('omitted_channel',('channel',),[
  'I assert material scaled change for {s} between the before/after incident windows, but have not selected a metric channel.',
  'For {s}, does the signed scaled difference exceed zero from before this incident to after it? The metric name is omitted.']),
 ('channel_choices',('channel',),[
  '{s} has a material scaled change in either CPU or memory across the before/after incident comparison.',
  'Compare {s} before versus after the incident. Either processor utilization or mem has positive signed scaled change; the channel is undecided.']),
 ('vague_comparison',('kind',),[
  'CPU for {s} deteriorated from the before-incident window to the after-incident window.',
  'Across the supplied before/after incident comparison, processor utilization for {s} looks worse.']),
 ('comparison_choices',('kind','polarity'),[
  'For {s}, choose between a material-magnitude test and a positive-direction test on CPU, using the before/after incident windows.',
  'Should the before-incident versus after-incident processor-utilization check for {s} concern absolute magnitude or positive signed direction?']),
 ('contradictory_assertion',('polarity',),[
  'Compare {s} CPU before versus after this incident. I assert material scaled change and also deny that same material scaled change.',
  'For {s}, the absolute scaled CPU difference between the before/after incident windows is both at least 3.0 and below 3.0.']),
 ('omitted_window',('window',),[
  'I assert that the absolute scaled CPU difference for {s} reaches at least 3.0. No time comparison is specified.',
  'For {s}, does processor utilization show positive signed scaled change? I have not chosen the observation windows.']),
 ('different_window',('window',),[
  'CPU for {s} has material scaled change when compared with the previous week.',
  'For {s}, the signed processor-utilization change is positive relative to the earlier maintenance period.']),
 ('several_omissions',('service','kind','polarity','window'),[
  'CPU is the metric I want to check; everything else still needs to be specified.',
  'Please help me set up a processor-utilization check.']),
 ('cause_request',None,[
  'Determine whether {s} explains the incident as its root cause.',
  'Is {s} responsible for causing this incident?']),
 ('health_request',None,[
  'Can you establish that {s} is healthy?',
  'Assess whether {s} remains unhealthy following the incident.']),
 ('unavailable_channel',('channel',),[
  'For {s}, packet-loss rate has material scaled change between the before/after incident windows.',
  'Compare {s} before versus after this incident. Does packet-loss rate have positive signed scaled change?']),
 ('subject_and_channel_missing',('service','channel'),[
  'A metric has material scaled change between the before/after incident windows. Neither the service nor channel is specified.',
  'The signed scaled change is positive across the before/after incident comparison; the subject and metric are still undecided.']),
 ('bare_assertion_topic',('polarity',),[
  'Comparison topic only: {s}, CPU, material scaled magnitude, before-incident versus after-incident observations. No condition is asserted or denied.',
  'For {s}, the selected channel is cpu, comparison is positive signed direction, and windows are before versus after the incident. I have not stated whether that condition holds.']),
 ('repair_request',None,[
  'Choose a repair for {s} to restore service.',
  'Should I reboot {s} to repair the incident?'])
]

def reconstruct():
    packets=[];refs=[]
    for c in contexts():
        s,t=list(c['inventory'])
        for family,needed,texts in FAMILIES:
            for variant,text in enumerate(texts,1):
                identifier='OPT-'+sha((c['dataset']+'/'+family+'/'+str(variant)).encode())[:12]
                packets.append({'id':identifier,'dataset':c['dataset'],'family':family,'variant':variant,'text':text.format(s=s,t=t),'inventory':c['inventory']})
                required=[] if needed is None else [k for k in PRIORITY if k in needed]
                choice='outside_scope' if needed is None else required[0] if required else 'no_question'
                refs.append({'id':identifier,'needed':required,'choice':choice,'scope':'outside_task' if needed is None else 'needs_question' if required else 'complete_wording','reference_origin':'Manually declared controlled wording under the frozen metric-entry contract; same assistant, no independent review.'})
    if len(packets)!=92 or len({p['id'] for p in packets})!=92:raise ValueError('Optional wording budget changed.')
    return packets,refs

def prepare(check_plan):
    check_plan()
    if DATA.exists():raise ValueError('Never overwrite optional question evidence.')
    packets,refs=reconstruct();DATA.mkdir(parents=True);dump(DATA/'inputs.json',packets);dump(DATA/'references.json',refs)
    m={'schema':'optional-clarification-data-1','claims':92,'families':23,'variants':2,'applications':2,'new_recordings':0,'human_reviews':0,'independent_reviews':0,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    dump(DATA/'manifest.json',m);validate(check_plan);return {'claims':92,'families':23,'new_recordings':0}

def validate(check_plan):
    check_plan();m=load(DATA/'manifest.json')
    if m['schema']!='optional-clarification-data-1' or m['claims']!=92 or m['plan_sha256']!=sha(PLAN.read_bytes()) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Optional pack identity changed.')
    for name,digest in m['files'].items():
        if sha((DATA/name).read_bytes())!=digest:raise ValueError('Optional pack bytes changed.')
    packets,refs=reconstruct()
    if packets!=load(DATA/'inputs.json') or refs!=load(DATA/'references.json'):raise ValueError('Optional pack reconstruction changed.')
    for p in packets:
        for arm in ('direct','checklist'):
            wire=str(request(p,arm))
            if any(x in wire for x in ('source_packet','reference',p['id'],p['family'])):raise ValueError('Optional request leaked reference metadata.')
    return m
