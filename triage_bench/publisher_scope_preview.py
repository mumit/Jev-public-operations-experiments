"""Unscored preview of explicit incident selection; never invoke a model."""
import re
from . import publisher_report_data as data

HEADER=re.compile(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s+\d{2}:\d{2}\s+UTC\s+\(lasting ')

def sections(source):
    data.audit.verify(local=True)
    article=data.load(data.audit.CACHE/(source+'.json'))
    n=data.audit.input_prefix(article['blocks'])['included_blocks'];blocks=article['blocks'][:n]
    headings=[i for i,b in enumerate(blocks) if HEADER.match(b['text'])]
    return blocks,[{'id':str(i),'label':blocks[i]['text'],'start':i,'end':headings[j+1] if j+1<len(headings) else n} for j,i in enumerate(headings)]

def preview(source,section=None):
    blocks,choices=sections(source)
    if section is None:return {'sections':choices,'provider_calls':0,'scored':False}
    chosen=next(s for s in choices if s['id']==section)
    intro=blocks[:choices[0]['start']];selected=[*intro,*blocks[chosen['start']:chosen['end']]]
    text='\n\n'.join(b['text'] for b in selected)
    return {'section':chosen,'report_excerpt':text,'full_bytes':len(data.audit.input_prefix(blocks)['text'].encode()),'scoped_bytes':len(text.encode()),'retained_blocks':[*(range(choices[0]['start'])),*range(chosen['start'],chosen['end'])],'provider_calls':0,'scored':False,'note':'Proposed explicit incident selection. Keep the original claim. This changes the supplied evidence and has no model result; a new frozen protocol must precede testing.'}
