"""Once-only prospective report audit; no claims, labels or model calls."""
import json
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse
from .paths import ROOT
from .report_source_audit import extract,digest
from .publisher_scope_preview import HEADER
from .public_rca_stages import committed

PLAN=ROOT/'checkpoints/publisher-selective-confirmation-plan-2026-10-07.json'
AUDIT=ROOT/'checkpoints/publisher-selective-source-audit-2026-10-07.json'
CACHE=ROOT/'runs/selective-report/source-audit-2026-10-07-v1'

def inventory(blocks):
    indices=[i for i,b in enumerate(blocks) if HEADER.match(b['text'])]
    return [{'id':str(i),'label':blocks[i]['text'],'start':i,'end':indices[n+1] if n+1<len(indices) else len(blocks)} for n,i in enumerate(indices)]

def audit():
    committed(PLAN)
    if AUDIT.exists() or CACHE.exists():raise ValueError('Preserve the once-only audit and all failures.')
    plan=json.loads(PLAN.read_text());CACHE.mkdir(parents=True);sources=[]
    for source in plan['sources']:
        record=dict(source)
        try:
            request=urllib.request.Request(source['url'],headers={'User-Agent':'Northstar-public-source-audit/1.0'})
            with urllib.request.urlopen(request,timeout=30) as response:
                if urlparse(response.url).hostname!='github.blog':raise ValueError('Publisher redirect left its official domain.')
                raw=response.read(8000001)
            if len(raw)>8000000:raise ValueError('Source snapshot exceeds audit limit.')
            (CACHE/(source['id']+'.html')).write_bytes(raw);record['html_sha256']=digest(raw)
            article=extract(raw,'GitHub');serialized=(json.dumps(article,ensure_ascii=False,indent=2)+'\n').encode()
            (CACHE/(source['id']+'.json')).write_bytes(serialized)
            title=(article['title'] or '').lower()
            if source['month'].lower() not in title or str(source['year']) not in title or 'availability report' not in title:
                raise ValueError('Source title does not match the frozen month.')
            sections=inventory(article['blocks'])
            record.update(status='available',title=article['title'],article_sha256=digest(serialized),blocks=len(article['blocks']),
                incident_sections=len(sections),sections=sections,preparation_eligible=len(sections)>=3)
        except urllib.error.HTTPError as error:
            record.update(status='failed',reason='source_http_'+str(error.code));error.close()
        except (OSError,ValueError) as error:
            record.update(status='failed',reason=type(error).__name__+': '+str(error))
        sources.append(record)
    result={'schema':'publisher-selective-source-audit-1','plan_sha256':digest(PLAN.read_bytes()),
        'producer_sha256':digest(Path(__file__).read_bytes()),'sources':sources,'preparation_eligible':all(s.get('preparation_eligible',False) for s in sources),
        'new_provider_calls':0,'new_telemetry_recordings':0,'human_reviews':0,'independent_reference_reviews':0,
        'full_source_publication':False,'boundary':'Publisher snapshots only. Claims, references and exact model requests are not yet prepared.'}
    with AUDIT.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    return result

def verify(local=True):
    committed(PLAN);result=json.loads(AUDIT.read_text())
    if digest(PLAN.read_bytes())!=result['plan_sha256'] or digest(Path(__file__).read_bytes())!=result['producer_sha256']:
        raise ValueError('Prospective source plan or audit changed.')
    if local:
        for source in result['sources']:
            if source['status']!='available':continue
            raw=(CACHE/(source['id']+'.html')).read_bytes();saved=(CACHE/(source['id']+'.json')).read_bytes()
            article=extract(raw,'GitHub')
            if digest(raw)!=source['html_sha256'] or digest(saved)!=source['article_sha256'] or json.loads(saved)!=article or inventory(article['blocks'])!=source['sections']:
                raise ValueError('Source snapshot or section inventory changed.')
    return result
