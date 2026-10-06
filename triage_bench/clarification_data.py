"""Controlled language contrasts, manually declared reference decisions, no new telemetry."""
import json
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load
from .public_rca_data import dump
from .explicit_claim_data import OLD_DATA
from .clarification_features import FIELDS,compose,request

PLAN=ROOT/'checkpoints/clarification-plan-2026-10-06.json'
BASE=ROOT/'runs/clarification'
DATA=BASE/'development-data-2026-10-06-v1'
ORIGIN=OLD_DATA/'inputs.json'

# Reference labels follow the declared task contract, not a parser or Jev reply.
# A family is one authored ambiguity pattern; variants/applications are correlated.
FAMILIES=[
 ('ready_literal',(),[
  'For {s}, CPU has a material scaled change between the before and after incident windows.',
  'Check whether the absolute scaled CPU change for {s} is at least 3.0, comparing before with after this incident.']),
 ('ready_direction',(),[
  'For {s}, CPU has a positive signed scaled change between the before and after incident windows.',
  'Is the signed CPU change for {s} greater than zero in the after-incident window relative to the before-incident window?']),
 ('ready_pronoun',(),[
  '{s} restarted. Its CPU has a material scaled change between the before and after incident windows.',
  'The affected service is {s}; does its processor utilization show material scaled change across the supplied before/after incident comparison?']),
 ('ready_negative',(),[
  'For {s}, CPU does not have a material scaled change between the before and after incident windows.',
  'For {s}, the absolute scaled CPU change is less than 3.0 when comparing the before-incident window with the after-incident window.']),
 ('ready_correction',(),[
  'For {s}, check material CPU change. Correction: I mean positive signed CPU change, between the before and after incident windows.',
  'I first said the CPU change for {s} was not material. My final claim is that it is material, comparing the after-incident window with the before-incident window.']),
 ('ready_background',(),[
  '{t} is processing a separate ticket. For {s}, CPU has a material scaled change between the before and after incident windows.',
  'Although {t} appears in the background notes, this claim concerns {s}: its CPU change is positive across the before/after incident comparison.']),
 ('service_missing',('service',),[
  'CPU has a material scaled change between the before and after incident windows.',
  'Is the absolute scaled processor utilization change at least 3.0 across the supplied before/after incident comparison?']),
 ('service_pronoun_pair',('service',),[
  '{s} called {t}. Its CPU has a material scaled change between the before and after incident windows.',
  'Both {s} and {t} restarted; its signed CPU change is positive across the before/after incident comparison.']),
 ('service_alias',('service',),[
  'The main handler has a material scaled CPU change between the before and after incident windows.',
  'The usual backend has a positive signed processor utilization change across the supplied before/after incident comparison.']),
 ('channel_missing',('channel',),[
  'For {s}, one metric has a material scaled change between the before and after incident windows.',
  'The signed change for {s} is positive across the supplied before/after incident comparison; I have not selected the metric.']),
 ('channel_alternative',('channel',),[
  'For {s}, CPU or memory has a material scaled change between the before and after incident windows.',
  'For {s}, either processor utilization or mem has a positive signed change across the supplied before/after incident comparison.']),
 ('kind_vague',('kind',),[
  'For {s}, CPU looks worse between the before and after incident windows.',
  'Processor utilization for {s} deteriorated across the supplied before/after incident comparison.']),
 ('kind_alternative',('kind','polarity'),[
  'For {s}, should I check material magnitude or positive direction of CPU change between the before and after incident windows?',
  'For {s}, choose whether this is a magnitude check or a direction check on processor utilization across the before/after incident comparison.']),
 ('polarity_conflict',('polarity',),[
  'For {s}, CPU both has and does not have a material scaled change between the before and after incident windows.',
  'For {s}, the absolute scaled CPU change is at least 3.0, yet it is also less than 3.0 across the supplied before/after incident comparison.']),
 ('window_missing',('window',),[
  'For {s}, CPU has a material scaled change.',
  'Is the signed processor utilization change for {s} positive?']),
 ('window_other',('window',),[
  'For {s}, CPU has a material scaled change compared with last month.',
  'The signed CPU change for {s} is positive compared with the last deployment, rather than this incident comparison.']),
 ('several_missing',('service','kind','polarity','window'),[
  'Check CPU.',
  'I want a check on processor utilization.']),
 ('outside_cause',None,[
  'Did {s} cause the incident?',
  'Identify whether {s} is the root cause, using the supplied before/after incident comparison.']),
 ('outside_health',None,[
  'Is {s} healthy?',
  'Confirm that {s} is not unhealthy after the incident.'])
]

def contexts():
    source=sorted(load(ORIGIN),key=lambda p:p['id']);result=[]
    for dataset in ('Train Ticket','Online Boutique'):
        p=next(p for p in source if p['dataset']==dataset);inventory={o['service']:sorted(o['metrics']) for o in p['observations']}
        if len(inventory)!=2 or any(not {'cpu','mem'}<=set(v) for v in inventory.values()):raise ValueError('Observed inventory contract changed.')
        result.append({'dataset':dataset,'source_packet':p['id'],'inventory':inventory})
    return result

def reconstruct():
    packets=[];refs=[]
    for c in contexts():
        s,t=list(c['inventory'])
        for family,needed,texts in FAMILIES:
            labels={'scope':'outside_scope' if needed is None else 'metric_check',**{k:'not_applicable' if needed is None else 'clarify' if k in needed else 'clear' for k in FIELDS if k!='scope'}}
            for variant,text in enumerate(texts,1):
                identifier='CLR-'+sha((c['dataset']+'/'+family+'/'+str(variant)).encode())[:12]
                packets.append({'id':identifier,'dataset':c['dataset'],'family':family,'variant':variant,'text':text.format(s=s,t=t),'inventory':c['inventory']})
                refs.append({'id':identifier,'labels':labels.copy(),'decision':compose(labels),'reference_origin':'Manually declared authored ambiguity pattern under the frozen contract.'})
    if len(packets)!=76 or len({p['id'] for p in packets})!=76:raise ValueError('Frozen language budget changed.')
    return packets,refs

def prepare(check_plan):
    check_plan()
    if DATA.exists():raise ValueError('Never overwrite a language pack.')
    packets,refs=reconstruct();DATA.mkdir(parents=True);dump(DATA/'inputs.json',packets);dump(DATA/'references.json',refs)
    m={'schema':'clarification-data-1','claims':76,'families':19,'variants':2,'applications':2,'new_recordings':0,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}}
    dump(DATA/'manifest.json',m);validate(check_plan);return m

def validate(check_plan):
    check_plan();m=load(DATA/'manifest.json')
    if m['schema']!='clarification-data-1' or m['claims']!=76 or m['plan_sha256']!=sha(PLAN.read_bytes()) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Language pack identity changed.')
    for n,digest in m['files'].items():
        if sha((DATA/n).read_bytes())!=digest:raise ValueError('Language pack bytes changed.')
    packets,refs=reconstruct()
    if packets!=load(DATA/'inputs.json') or refs!=load(DATA/'references.json'):raise ValueError('Language reconstruction changed.')
    for p in packets:
        wire=json.dumps(request(p))
        if any(x in wire for x in ('source_packet','root_cause','reference',p['id'],p['family'])):raise ValueError('Reference metadata leaked into a model request.')
    return m
