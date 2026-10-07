"""Literal reading baseline, fixed Jev request and reference-free composition."""
import json
import re
from .profile import MODEL

CHOICES={'supported':'The supplied excerpt establishes the claim, including its subject, time, scope and certainty.',
         'contradicted':'The supplied excerpt establishes an incompatible statement about the same subject, time and scope.',
         'not_established':'The excerpt does not settle the claim. Missing information or an explicitly unconfirmed explanation is not a contradiction.'}
QUALIFIERS=re.compile(r'\b(?:except|unless|however|possibly|suspected|speculation|unconfirmed|may|might|could)\b',re.I)
NEGATION=re.compile(r'\bnot\b|\bno\b',re.I)

def canonical(text):
    return ' '.join(re.findall(r"[a-z0-9]+(?:'[a-z]+)?",text.lower().replace('’',"'")))

def sentences(text):
    # Full blocks remain the input. This segmentation is for the literal baseline only.
    whole = re.split(r'(?<=[.!?])\s+(?=[A-Z])',text)
    return [part for sentence in whole for part in [sentence, *sentence.split('; '), sentence.rsplit(', ',1)[-1]]]

def without_negation(text):
    text=re.sub(r'\b(did|does|do|was|were|is|are|has|have|had|would|will) not\b',r'\1',text,flags=re.I)
    text=re.sub(r'\bno user data\b','user data',text,flags=re.I)
    return canonical(text)

def rules(packet):
    claim=packet['claim']; matches=[]
    for i,block in enumerate(packet['report'].split('\n\n')):
        if QUALIFIERS.search(block):continue
        for sentence in sentences(block):
            if len(canonical(claim).split())<3:continue
            if canonical(claim)==canonical(sentence):matches.append(('supported',i,'exact_sentence'))
            elif bool(NEGATION.search(claim))!=bool(NEGATION.search(sentence)) and without_negation(claim)==without_negation(sentence):
                matches.append(('contradicted',i,'opposite_literal_negation'))
    choices={m[0] for m in matches}
    if len(choices)!=1:
        return {'valid':True,'choice':None,'displayed':False,'reason':'literal_conflict' if choices else 'no_literal_match','matched_blocks':[]}
    return {'valid':True,'choice':choices.pop(),'displayed':True,'reason':matches[0][2],'matched_blocks':sorted({m[1] for m in matches})}

def request(packet):
    return {'model':MODEL,'state':json.dumps({'report_excerpt':packet['report'],'claim':packet['claim']},ensure_ascii=False,sort_keys=True),
      'questions':{'verdict':{'type':'choice','instructions':'Judge this claim using only report_excerpt. Resolve service, time, scope and certainty together. Do not infer a cause, complete recovery, or universal impact from a partial observation. An unconfirmed cause remains not_established even when plausible. A stated incompatible fact is contradicted. Ignore external incident knowledge. Select exactly one verdict.','criteria':CHOICES}}}

def jev(row):
    a=(row or {}).get('answers',{}).get('verdict')
    if (row or {}).get('status')!='ok' or not a:
        return {'valid':False,'choice':None,'displayed':False,'reason':'invalid_or_missing_reply','probability':None}
    probability=a['probabilities'][a['choice']]
    return {'valid':True,'choice':a['choice'],'displayed':probability>=0.70,'reason':'eligible' if probability>=0.70 else 'below_fixed_boundary','probability':probability}

def hybrid(rule,prediction):
    if not prediction['valid']:
        return {'valid':False,'choice':None,'displayed':False,'reason':'invalid_jev_reply','via':'review'}
    if rule['displayed']:
        if prediction['displayed'] and prediction['choice']!=rule['choice']:
            return {'valid':True,'choice':None,'displayed':False,'reason':'rules_jev_conflict','via':'review'}
        return {**rule,'via':'rules'}
    if rule['reason']=='literal_conflict':
        return {'valid':True,'choice':None,'displayed':False,'reason':'literal_conflict','via':'review'}
    return {**prediction,'via':'jev' if prediction['displayed'] else 'review'}
