"""Once-only whole-report transfer audit, with retained code blocks and failures."""
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse
from .paths import ROOT
from .report_source_audit import Tree,BLOCKS,digest
from .report_knowledge_features import request
from .hosted import encoded
from .public_rca_stages import committed

PLAN=ROOT/'checkpoints/publisher-review-budget-plan-2026-10-08.json'
AUDIT=ROOT/'checkpoints/publisher-review-budget-source-audit-2026-10-08.json'
CACHE=ROOT/'runs/review-budget/source-audit-2026-10-08-v1'

def extract(raw):
    tree=Tree();tree.feed(raw.decode('utf-8'));nodes=list(tree.root.walk())
    roots=[n for n in nodes if 'article-content' in n.attrs.get('class','').split()]
    if len(roots)!=1:raise ValueError('Expected one Cloudflare article container.')
    blocks=[]
    def collect(n):
        if n.tag in {'script','style','nav','footer','aside','noscript'}:return
        if n.tag in BLOCKS|{'pre'}:
            value=re.sub(r'\s+',' ',n.text()).strip()
            if value:blocks.append({'tag':n.tag,'text':value})
            return
        for child in n.children:
            if hasattr(child,'tag'):collect(child)
    collect(roots[0]);titles=[n for n in nodes if n.tag=='h1']
    if not blocks or sum(len(b['text']) for b in blocks)<100 or not titles:raise ValueError('Unusable article text or title.')
    return {'title':re.sub(r'\s+',' ',titles[0].text()).strip(),'blocks':blocks,
        'representation':'All extracted prose/list/table/code blocks in source order; whitespace normalized; images excluded.'}

def text(article):return '\n\n'.join(b['text'] for b in article['blocks'])

def audit():
    committed(PLAN)
    if AUDIT.exists() or CACHE.exists():raise ValueError('Preserve the once-only source audit.')
    plan=json.loads(PLAN.read_text());CACHE.mkdir(parents=True);sources=[]
    for source in plan['sources']:
        record=dict(source)
        try:
            req=urllib.request.Request(source['url'],headers={'User-Agent':'Northstar-public-source-audit/1.0'})
            with urllib.request.urlopen(req,timeout=30) as response:
                if urlparse(response.url).hostname!='blog.cloudflare.com':raise ValueError('Redirect left the official publisher.')
                raw=response.read(8000001)
            if len(raw)>8000000:raise ValueError('Source snapshot exceeds audit cap.')
            (CACHE/(source['id']+'.html')).write_bytes(raw);record['html_sha256']=digest(raw)
            article=extract(raw);saved=(json.dumps(article,ensure_ascii=False,indent=2)+'\n').encode()
            (CACHE/(source['id']+'.json')).write_bytes(saved)
            if article['title']!=source['expected_title']:raise ValueError('Source title differs from allocation.')
            full=text(article);packet={'report':full,'scoped_report':full,'claim':'Preparation size probe.','selected_incident':article['title']}
            size=max(len(encoded(request(packet,a))) for a in plan['arms'])
            record.update(status='available',title=article['title'],article_sha256=digest(saved),blocks=len(article['blocks']),
                text_sha256=digest(full.encode()),text_bytes=len(full.encode()),probe_wire_bytes=size,
                code_blocks=sum(b['tag']=='pre' for b in article['blocks']),preparation_eligible=size<=plan['maximum_request_bytes'])
        except urllib.error.HTTPError as error:
            record.update(status='failed',reason='source_http_'+str(error.code));error.close()
        except (OSError,ValueError) as error:record.update(status='failed',reason=type(error).__name__+': '+str(error))
        sources.append(record)
    result={'schema':'publisher-review-budget-source-audit-1','plan_sha256':digest(PLAN.read_bytes()),
        'producer_sha256':digest(Path(__file__).read_bytes()),'sources':sources,
        'preparation_eligible':all(s.get('preparation_eligible',False) for s in sources),
        'new_provider_calls':0,'new_telemetry_recordings':0,'human_reviews':0,'independent_reference_reviews':0}
    with AUDIT.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    return result

def verify(local=True):
    committed(PLAN);result=json.loads(AUDIT.read_text())
    if digest(PLAN.read_bytes())!=result['plan_sha256'] or digest(Path(__file__).read_bytes())!=result['producer_sha256']:
        raise ValueError('Frozen source plan or audit producer changed.')
    if local:
        for source in result['sources']:
            if source['status']!='available':continue
            raw=(CACHE/(source['id']+'.html')).read_bytes();saved=(CACHE/(source['id']+'.json')).read_bytes();article=extract(raw)
            if digest(raw)!=source['html_sha256'] or digest(saved)!=source['article_sha256'] or json.loads(saved)!=article or digest(text(article).encode())!=source['text_sha256']:
                raise ValueError('Retained source snapshot changed.')
    return result
