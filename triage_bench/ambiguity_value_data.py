"""Forty-eight new authored statements, paired references, no telemetry access."""
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load
from .public_rca_data import dump
from .clarification_data import contexts
from .clarification_features import PRIORITY
from .ambiguity_value_features import request

PLAN=ROOT/'checkpoints/ambiguity-value-plan-2026-10-06.json'
DATA=ROOT/'runs/ambiguity-value/development-data-2026-10-06-v1'
# Each tuple declares two reference masks independently of the rule/model output.
PATTERNS=[
 ('service_omission_pair',('complete','omission'),((),('service',)),(
  'For {s}, CPU has material scaled magnitude between before and after this incident.',
  'For the unnamed component, CPU has material scaled magnitude between before and after this incident.')),
 ('metric_omission_pair',('complete','omission'),((),('channel',)),(
  'For {s}, memory has positive signed scaled change between before and after this incident.',
  'For {s}, the unselected metric has positive signed scaled change between before and after this incident.')),
 ('window_omission_pair',('complete','omission'),((),('window',)),(
  'For {s}, CPU does not have material scaled magnitude between before and after this incident.',
  'For {s}, CPU does not have material scaled magnitude. The time comparison remains unspecified.')),
 ('assertion_topic_pair',('complete','omission'),((),('polarity',)),(
  'For {s}, CPU has material scaled magnitude between before and after this incident.',
  'Topic only, no assertion: for {s}, CPU, material scaled magnitude, before and after this incident.')),
 ('vague_meaning_pair',('complete','subtle'),((),('kind',)),(
  'For {s}, CPU has material scaled magnitude between before and after this incident.',
  'For {s}, CPU shifted unfavorably between before and after this incident.')),
 ('antecedent_pair',('complete','subtle'),((),('service',)),(
  '{s} is the component in this note. Its memory has positive signed scaled change between before and after this incident.',
  '{s} and {t} are the components in this note. Its memory has positive signed scaled change between before and after this incident.')),
 ('incidental_subject_pair',('complete','subtle'),((),()),(
  'For {s}, processor utilization has material scaled magnitude between before and after this incident.',
  '{s} and {t} appear in that order in this note. The latter belongs to a separate ticket. The former is the subject of this claim: processor utilization has material scaled magnitude between before and after this incident.')),
 ('metric_alternatives_pair',('complete','subtle'),((),('channel',)),(
  'For {s}, CPU has positive signed scaled change between before and after this incident.',
  'For {s}, CPU or memory has positive signed scaled change between before and after this incident; the metric choice is unresolved.')),
 ('correction_pair',('subtle','subtle'),((),('channel',)),(
  'For {s}, CPU has material scaled magnitude between before and after this incident. Discard that entire draft. The replacement claim concerns {t}: memory has material scaled magnitude between before and after this incident.',
  'For {s}, CPU has material scaled magnitude between before and after this incident. Discard that entire draft. The replacement claim concerns {t}: an unselected metric has material scaled magnitude between before and after this incident.')),
 ('polarity_conflict_pair',('complete','subtle'),((),('polarity',)),(
  'For {s}, I deny material scaled CPU magnitude between before and after this incident.',
  'For {s}, I assert material scaled CPU magnitude and deny that same magnitude between before and after this incident.')),
 ('other_window_pair',('complete','subtle'),((),('window',)),(
  'For {s}, CPU has positive signed scaled change between before and after this incident.',
  'For {s}, CPU has positive signed scaled change between yesterday and today.')),
 ('numeric_wording_pair',('complete','complete'),((),()),(
  'For {s}, CPU has material scaled magnitude between before and after this incident.',
  'For {s}, the absolute scaled CPU difference reaches three or more between before and after this incident.'))]


def reconstruct():
    packets=[];refs=[]
    for c in contexts():
        s,t=list(c['inventory'])
        for family,categories,masks,texts in PATTERNS:
            pair='AVP-'+sha((c['dataset']+family).encode())[:12]
            for i,text in enumerate(texts):
                identifier='AV-'+sha((c['dataset']+family+str(i)).encode())[:12]
                packets.append({'id':identifier,'dataset':c['dataset'],'family':family,'pair':pair,'variant':i+1,'category':categories[i],'text':text.format(s=s,t=t),'inventory':c['inventory']})
                needed=[k for k in PRIORITY if k in masks[i]]
                refs.append({'id':identifier,'needed':needed,'choice':needed[0] if needed else 'no_question','scope':'needs_question' if needed else 'complete_wording','origin':'Assistant-declared masks before inference; no independent reviewer or authentic report.'})
    if len(packets)!=48 or len({p['id'] for p in packets})!=48:raise ValueError('Fresh wording allocation changed.')
    return packets,refs


def prepare(check_plan):
    check_plan();packets,refs=reconstruct();DATA.mkdir(parents=True)
    dump(DATA/'inputs.json',packets);dump(DATA/'references.json',refs)
    dump(DATA/'manifest.json',{'schema':'ambiguity-value-data-1','claims':48,'pairs':24,'new_recordings':0,'plan_sha256':sha(PLAN.read_bytes()),'files':{n:sha((DATA/n).read_bytes()) for n in ('inputs.json','references.json')}})
    return validate(check_plan)


def validate(check_plan):
    check_plan();m=load(DATA/'manifest.json')
    if m['schema']!='ambiguity-value-data-1' or m['claims']!=48 or m['plan_sha256']!=sha(PLAN.read_bytes()) or set(m['files'])!={'inputs.json','references.json'}:raise ValueError('Fresh pack identity changed.')
    for n,d in m['files'].items():
        if sha((DATA/n).read_bytes())!=d:raise ValueError('Fresh pack bytes changed.')
    if reconstruct()!=(load(DATA/'inputs.json'),load(DATA/'references.json')):raise ValueError('Fresh text/reference reconstruction changed.')
    for p in load(DATA/'inputs.json'):
        wire=str(request(p))
        if any(k in wire for k in (p['id'],p['family'],p['pair'],'reference_origin')):raise ValueError('Reference metadata leaked.')
    return m
