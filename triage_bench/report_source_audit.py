"""Audit publisher-written reports without inference or telemetry access."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import urllib.request
from .paths import ROOT

CATALOG = ROOT / 'checkpoints/report-source-catalog-2026-10-07.json'
AUDIT = ROOT / 'checkpoints/report-source-audit-2026-10-07.json'
CACHE = ROOT / 'runs/report-evidence/source-audit-2026-10-07-v1'
BLOCKS = {'p', 'h1', 'h2', 'h3', 'h4', 'li', 'tr'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
HOSTS = {'Cloudflare':'blog.cloudflare.com', 'GitHub':'github.blog', 'AWS':'aws.amazon.com', 'Fastly':'www.fastly.com'}

def digest(value):
    return hashlib.sha256(value).hexdigest()

class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []
    def text(self):
        if self.tag in {'script','style','nav','footer','aside','noscript'}:
            return ''
        value = ''.join(c.text() if isinstance(c, Node) else c for c in self.children)
        return ' ' + value + ' ' if self.tag in {'br', 'td', 'th', 'p', 'li'} else value
    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.walk()

class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break
    def handle_data(self, value):
        self.stack[-1].children.append(value)


def extract(raw, publisher):
    tree = Tree()
    tree.feed(raw.decode('utf-8'))
    nodes = list(tree.root.walk())
    roots = [n for n in nodes if (
        publisher == 'Cloudflare' and 'article-content' in n.attrs.get('class','').split()
        or publisher == 'GitHub' and 'post__content' in n.attrs.get('class','').split()
        or publisher == 'Fastly' and any('rich-text-article-content' in c for c in n.attrs.get('class','').split())
        or publisher == 'AWS' and n.tag == 'main'
    )]
    if len(roots) != 1:
        raise ValueError('Expected one publisher article container.')
    out = []
    def collect(n):
        if n.tag in {'script','style','nav','footer','aside','noscript'}:
            return
        if n.tag in BLOCKS:
            text = re.sub(r'\s+', ' ', n.text()).strip()
            if text:
                out.append({'tag':n.tag, 'text':text})
            return  # No nested paragraph/list duplicates.
        for child in n.children:
            if isinstance(child, Node):
                collect(child)
    collect(roots[0])
    if not out or sum(len(x['text']) for x in out) < 100:
        raise ValueError('No usable article text.')
    title_nodes = [n for n in nodes if n.tag == 'h1']
    title = re.sub(r'\s+', ' ', title_nodes[0].text()).strip() if title_nodes else None
    dates = [n.attrs['content'] for n in nodes if n.tag == 'meta' and n.attrs.get('property') == 'article:published_time' and n.attrs.get('content')]
    return {'title':title, 'publisher_date_metadata':dates[0] if dates else None, 'blocks':out}


def input_prefix(blocks, budget=14000):
    selected=[]
    for block in blocks:
        proposed='\n\n'.join([*selected, block['text']])
        if len(proposed.encode('utf-8')) > budget:
            break
        selected.append(block['text'])
    text='\n\n'.join(selected)
    if not text:
        raise ValueError('No complete block fits input budget.')
    return {'text':text, 'included_blocks':len(selected), 'omitted_blocks':len(blocks)-len(selected), 'bytes':len(text.encode('utf-8')), 'sha256':digest(text.encode('utf-8'))}


def load_catalog():
    c=json.loads(CATALOG.read_text())
    if c['schema'] != 'publisher-report-catalog-1' or len(c['sources']) != 12:
        raise ValueError('Source catalog schema or count changed.')
    ids=[s['id'] for s in c['sources']]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate source.')
    groups={}
    for s in c['sources']:
        u=urlparse(s['url'])
        if u.scheme != 'https' or u.hostname != HOSTS.get(s['publisher']) or u.query or u.fragment:
            raise ValueError('Unapproved publisher URL.')
        if s['allocation'] not in {'development','evaluation','audit_only'}:
            raise ValueError('Unknown source allocation.')
        groups.setdefault(s['incident_group'],set()).add(s['allocation'])
    if any(len(v) != 1 for v in groups.values()):
        raise ValueError('One incident crosses allocations.')
    if {a:sum(v=={a} for v in groups.values()) for a in ('development','evaluation','audit_only')} != {'development':4,'evaluation':4,'audit_only':2}:
        raise ValueError('Whole-incident allocation changed.')
    return c


def audit():
    c=load_catalog()
    if AUDIT.exists() or CACHE.exists():
        raise ValueError('Preserve existing audit and use a separately versioned attempt.')
    CACHE.mkdir(parents=True)
    records=[]
    for s in c['sources']:
        entry={**s,'status':'unavailable'}
        try:
            request=urllib.request.Request(s['url'],headers={'User-Agent':'Northstar-public-source-audit/1.0'})
            with urllib.request.urlopen(request,timeout=30) as response:
                final=response.geturl()
                if urlparse(final).scheme != 'https' or urlparse(final).hostname != HOSTS[s['publisher']]:
                    raise ValueError('Unexpected publisher redirect.')
                raw=response.read(8000001)
            if len(raw)>8000000:
                raise ValueError('Oversized publisher document.')
            (CACHE/(s['id']+'.html')).write_bytes(raw)
            article=extract(raw,s['publisher'])
            if not all(term.casefold() in '\n'.join(b['text'] for b in article['blocks']).casefold() for term in s['content_checks']):
                raise ValueError('Article identity checks failed.')
            prefix=input_prefix(article['blocks'])
            normalized=(json.dumps(article,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
            (CACHE/(s['id']+'.json')).write_bytes(normalized)
            entry.update(status='available',final_url=final,title_observed=article['title'],publisher_date_metadata=article['publisher_date_metadata'],raw_bytes=len(raw),raw_sha256=digest(raw),normalized_sha256=digest(normalized),blocks=len(article['blocks']),article_words=sum(len(b['text'].split()) for b in article['blocks']),input_prefix={k:v for k,v in prefix.items() if k!='text'})
        except (OSError,ValueError,UnicodeError) as error:
            entry.update(error_type=type(error).__name__)
        records.append(entry)
        print(s['id']+': '+entry['status'],flush=True)
    record={'schema':'publisher-report-audit-1','audit_date':'2026-10-07','catalog_sha256':digest(CATALOG.read_bytes()),'producer_sha256':digest(Path(__file__).read_bytes()),'sources':records,'available_sources':sum(s['status']=='available' for s in records),'new_provider_calls':0,'new_telemetry_recordings':0,'human_reviews':0,'independent_reference_reviews':0,'source_authorship':'Publisher-written operational reports; questions and reference annotations are a separate assistant-reviewed task.','cache_policy':'Full HTML and article text remain in ignored local runs. Publish URLs, hashes, extraction provenance and research annotations; do not include full reports or full-text requests in release assets.'}
    AUDIT.write_text(json.dumps(record,indent=2)+'\n')
    return {'available_sources':record['available_sources'],'sources':len(records),'provider_calls':0}


def verify(local=True):
    c=load_catalog()
    r=json.loads(AUDIT.read_text())
    if r['catalog_sha256']!=digest(CATALOG.read_bytes()) or r['producer_sha256']!=digest(Path(__file__).read_bytes()) or [{k:s[k] for k in c['sources'][0]} for s in r['sources']] != c['sources']:
        raise ValueError('Catalog, producer or audit identity changed.')
    if r['schema'] != 'publisher-report-audit-1' or r['human_reviews'] or r['independent_reference_reviews']:
        raise ValueError('Audit schema or review attribution changed.')
    if r['available_sources']!=sum(s['status']=='available' for s in r['sources']) or r['new_provider_calls'] or r['new_telemetry_recordings']:
        raise ValueError('Audit counts changed.')
    if local:
        for s in r['sources']:
            if s['status']!='available':
                continue
            raw=(CACHE/(s['id']+'.html')).read_bytes()
            saved=(CACHE/(s['id']+'.json')).read_bytes()
            a=extract(raw,s['publisher'])
            canonical=(json.dumps(a,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
            prefix=input_prefix(a['blocks'])
            if digest(raw)!=s['raw_sha256'] or digest(saved)!=s['normalized_sha256'] or saved!=canonical or {k:v for k,v in prefix.items() if k!='text'}!=s['input_prefix']:
                raise ValueError('Cached source or deterministic extraction changed.')
    return {'status':'verified','sources':len(r['sources']),'incident_groups':len({s['incident_group'] for s in r['sources']}),'available_sources':r['available_sources'],'source_cache_checked':local,'new_provider_calls':0,'new_telemetry_recordings':0}
