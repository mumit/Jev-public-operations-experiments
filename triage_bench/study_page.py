"""Formatted public-study articles with safe return links."""
from html import escape
import math
from pathlib import Path
import re
from string import Template
from urllib.parse import urlencode,urlparse
from markdown_it import MarkdownIt

DOCUMENTS={'binding-corruption':'docs/binding-corruption.md','assistant-review':'docs/assistant-review.md','claim-review':'docs/claim-review.md', 'public-note-language':'docs/public-note-language.md','public-extraction-contrast':'docs/public-extraction-contrast.md','public-sentence-review':'docs/public-sentence-review.md','public-note-extraction':'docs/public-note-extraction.md','public-fresh-claims':'docs/public-fresh-claims.md','public-binding':'docs/public-claim-binding.md','public-reports':'docs/public-report-reading.md','public-claim-language':'docs/public-claim-language.md','public-claims':'docs/public-claim-assessment.md','public-evidence':'docs/public-evidence-assessment.md','public-trace-task':'docs/public-trace-task.md','public-traces':'docs/public-traces.md','public-agreement':'docs/public-agreement.md','public-confirmation':'docs/public-confirmation.md','public-selective':'docs/public-selective.md','public-temporal':'docs/public-temporal-next.md','public-repeat':'docs/public-repeatability.md','public-rca':'docs/public-rca-experiment.md','public-format':'docs/public-input-format.md',
           'public-data':'docs/public-data-assessment.md','handoff':'HANDOFF.md','evidence':'docs/evidence.md','migration':'docs/migration.md'}

def return_path(value):
    value=value or '/public-format';p=urlparse(value)
    if p.scheme or p.netloc or p.path not in {'/','/public-rca','/public-format','/repeatability','/temporal','/selective','/agreement','/traces','/trace-task','/binding-corruption','/assistant-review','/claim-review','/note-language','/extraction-contrast','/sentence-review','/note-extraction','/fresh-claims','/claim-binding','/report-reading','/claim-language','/claim-assessment','/evidence-assessment'} or '\\' in value or len(value)>4096:return '/public-format'
    if p.fragment and p.fragment not in {'overview','evidence','input','decision','inspect','wire'}:return '/public-format'
    return value


def slug(text):
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',text.casefold())).strip('-') or 'section'


def render_study(study,params):
    document=params.get('doc','public-format')
    if document not in DOCUMENTS:raise ValueError('Unknown study document.')
    source=(study.root/DOCUMENTS[document]).read_text()
    back=return_path(params.get('return','/binding-corruption' if document=='binding-corruption' else '/assistant-review' if document=='assistant-review' else '/claim-review' if document=='claim-review' else '/note-language' if document=='public-note-language' else '/extraction-contrast' if document=='public-extraction-contrast' else '/sentence-review' if document=='public-sentence-review' else '/note-extraction' if document=='public-note-extraction' else '/fresh-claims' if document=='public-fresh-claims' else '/claim-binding' if document=='public-binding' else '/report-reading' if document=='public-reports' else '/claim-language' if document=='public-claim-language' else '/claim-assessment' if document=='public-claims' else '/evidence-assessment' if document=='public-evidence' else '/trace-task' if document=='public-trace-task' else '/traces' if document=='public-traces' else '/agreement' if document=='public-agreement' else '/selective' if document in {'public-selective','public-confirmation'} else '/temporal' if document=='public-temporal' else '/repeatability' if document=='public-repeat' else '/public-rca' if document in {'public-rca','public-data'} else '/public-format'))
    def reader_link(href):
        p=urlparse(href)
        if not p.scheme and not p.netloc:
            if href.startswith('#'):return '#section-'+p.fragment.removeprefix('section-')
            for key,path in DOCUMENTS.items():
                if p.path in {path,Path(path).name,'../'+path,'../'+Path(path).name}:
                    return '/study?'+urlencode({'doc':key,'return':back})+('#section-'+p.fragment if p.fragment else '')
        if p.hostname in {'localhost','127.0.0.1'} and p.path in {'/','/public-rca','/public-format','/repeatability','/temporal','/selective','/agreement','/traces','/trace-task','/evidence-assessment','/claim-assessment','/claim-language','/report-reading','/binding-corruption','/assistant-review','/claim-review','/note-language','/extraction-contrast','/sentence-review','/note-extraction','/fresh-claims','/claim-binding','/study'}:
            return p.path+('?' +p.query if p.query else '')+('#'+p.fragment if p.fragment else '')
        return href
    md = MarkdownIt('js-default')
    tokens = md.parse(source)
    headings, used = [], set()
    title = 'Study overview'
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            label = tokens[i + 1].content
            anchor = 'section-' + slug(label)
            candidate, suffix = anchor, 2
            while anchor in used:
                anchor = candidate + '-' + str(suffix)
                suffix += 1
            used.add(anchor)
            token.attrSet('id', anchor)
            if token.tag == 'h1':
                title = label.removeprefix('Northstar Telecom: ')
                title = title[:1].upper() + title[1:]
            elif token.tag in {'h2', 'h3'}:
                headings.append((token.tag, label, anchor))
        for child in token.children or []:
            if child.type == 'link_open':
                href = reader_link(child.attrGet('href') or '')
                child.attrSet('href', href)
                if href.startswith(('https://', 'http://')):
                    child.attrSet('target', '_blank')
                    child.attrSet('rel', 'noopener noreferrer')

    def inline_code(renderer, row, index, options, env):
        content = row[index].content
        code = '<code>' + escape(content) + '</code>'
        return code

    def fence(renderer, row, index, options, env):
        token = row[index]
        language = token.info.split()[0] if token.info else 'text'
        count = len(token.content.splitlines())
        label = 'JSON input' if language == 'json' else 'Code example'
        return (f'<details class="code-example" {"open" if count <= 24 else ""}>'
                f'<summary><span>{label}</span><span class="code-meta">{escape(language.upper())} · {count} lines</span></summary>'
                '<div class="code-actions"><button type="button" data-copy-code>Copy code</button></div>'
                f'<pre tabindex="0"><code class="language-{escape(language, quote=True)}">{escape(token.content)}</code></pre></details>\n')

    md.add_render_rule('code_inline', inline_code)
    md.add_render_rule('fence', fence)
    # The first heading is displayed as the article's hero, with its original anchor retained.
    start = 3 if tokens and tokens[0].type == 'heading_open' and tokens[0].tag == 'h1' else 0
    article = md.renderer.render(tokens[start:], md.options, {})
    # Table rendering stays under the Markdown parser; wrappers add local scrolling and inspection.
    article = article.replace('<table>', '<div class="reading-table"><div class="table-actions"><span class="scroll-hint" hidden>Scroll sideways to read all columns</span><button type="button" data-expand-table>Expand table</button></div><div class="table-scroll" tabindex="0" role="region" aria-label="Study comparison table"><table>')
    article = article.replace('</table>', '</table></div></div>')
    toc = ''.join(f'<a class="toc-{tag}" href="#{anchor}">{escape(label)}</a>' for tag, label, anchor in headings)
    sections = ''.join(f'<option value="{anchor}">{"  " if tag == "h3" else ""}{escape(label)}</option>' for tag, label, anchor in headings)
    minutes = max(1, math.ceil(len(re.findall(r'\b\w+\b', source)) / 220))
    download = '/study.md' if False else '/study.md?doc=' + document
    hero_anchor = tokens[0].attrGet('id') if start else 'section-study'
    return Template((Path(__file__).parent / 'web/study.html').read_text()).substitute(
        title=escape(title), back=escape(back, quote=True), article=article,
        toc=toc, sections=sections, minutes=minutes, hero_anchor=hero_anchor,
        download=escape(download, quote=True), filename=Path(DOCUMENTS[document]).name,
        kind='Study reference',
        evidence_label='Public injected faults' if document in {'public-rca','public-format'} else 'Public dataset assessment' if document=='public-data' else 'Public research study',
        decision_label='Analyst review required' if document in {'public-rca','public-format'} else 'Input preparation' if document=='public-data' else 'Diagnostic decisions only',
    ).encode()
