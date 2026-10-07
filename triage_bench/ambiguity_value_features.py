"""Fixed literal rules and an unchanged Jev request for fresh-wording comparison."""
import re
from .clarification_features import PRIORITY
from .optional_clarification_features import request as old_request,action
from .optional_question_policy import decision


def request(packet):
    # Same focused six-field request, model, choices and state representation.
    return old_request(packet,'checklist')


def rules(packet):
    text=packet['text'].lower()
    # A declared final correction supersedes earlier wording, rather than voting.
    if 'final correction:' in text:text=text.rsplit('final correction:',1)[1]
    if re.search(r'\b(?:healthy|unhealthy|root cause|repair|reboot|trace duration)\b',text):
        return {'valid':True,'choice':'outside_scope','displayed':True,'labels':None,**action('outside_scope')}
    names=[s for s in packet['inventory'] if re.search(r'(?<![a-z0-9-])'+re.escape(s.lower())+r'(?![a-z0-9-])',text)]
    subjects=[s for s in names if re.search(r'(?:\bfor |\bon |claim concerns |subject is |check names |only |note concerns )'+re.escape(s.lower())+r'(?![a-z0-9-])',text)]
    selected=subjects if subjects else names
    available=set(packet['inventory'][selected[0]]) if len(selected)==1 else set.union(*(set(v) for v in packet['inventory'].values()))
    aliases={'cpu':r'\bcpu\b|\bprocessor utilization\b','mem':r'\bmem\b|\bmemory\b'}
    channels={name for name,pattern in aliases.items() if re.search(pattern,text)}
    for values in packet['inventory'].values():
        channels.update(c for c in values if c not in aliases and re.search(r'(?<![a-z0-9-])'+re.escape(c)+r'(?![a-z0-9-])',text))
    magnitude=bool(re.search(r'\bmaterial\b|\bmagnitude\b|absolute scaled(?: (?:cpu|memory|processor utilization))? (?:change|difference).{0,45}(?:3\.0|three)',text))
    direction=bool(re.search(r'positive (?:signed |scaled )*|signed scaled (?:change|difference).{0,30}(?:exceeds zero|greater than zero|zero or negative)',text))
    conflict=bool(re.search(r'\bassert\b.{0,80}\bdeny\b|\bboth\b.{0,60}at least 3\.0.{0,30}below 3\.0',text))
    topic=bool(re.search(r'\btopic only\b|no assertion|not asserted|no condition (?:is )?asserted',text))
    labels={'service':'clear' if len(selected)==1 else 'clarify',
            'channel':'clear' if len(channels)==1 and channels<=available else 'clarify',
            'kind':'clear' if magnitude!=direction else 'clarify',
            'polarity':'clarify' if conflict or topic else 'clear',
            'window':'clear' if all(re.search(r'\b'+w+r'\b',text) for w in ('before','after','incident')) else 'clarify'}
    choice=next((f for f in PRIORITY if labels[f]=='clarify'),'no_question')
    return {'valid':True,'choice':choice,'displayed':True,'labels':labels,**action(choice)}


def jev(row):return decision(row,'first_question')
