"""Loopback-only public study app. GET requests never invoke a model."""
import argparse
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from .public_rca_service import PublicRCAStudy
from .public_format_service import PublicFormatStudy
from .study_page import DOCUMENTS,render_study
from .public_repeat_service import PublicRepeatStudy
from .public_temporal_service import PublicTemporalStudy
from .public_selective_service import PublicSelectiveStudy
from .public_agreement_service import PublicAgreementStudy
from .public_trace_service import PublicTraceStudy
from .public_trace_task_service import PublicTraceTaskStudy
from .public_evidence_service import PublicEvidenceStudy
from .public_claim_service import PublicClaimStudy
from .public_claim_language_service import PublicClaimLanguageStudy
from .public_report_service import PublicReportStudy
from .public_binding_service import PublicBindingStudy
from .public_fresh_claim_service import PublicFreshClaimStudy
from .public_note_service import PublicNoteStudy
from .public_sentence_service import PublicSentenceStudy
from .public_contrast_service import PublicContrastStudy
from .public_note_language_service import PublicNoteLanguageStudy
from .claim_review_service import ClaimReviewStudy
from .assistant_review_service import AssistantReviewStudy
from .binding_corruption_service import BindingCorruptionStudy
from .subject_check_service import SubjectCheckStudy
from .separate_subject_service import SeparateSubjectStudy
from .direct_subject_service import DirectSubjectStudy
from .prefix_subject_service import PrefixSubjectStudy
from .excerpt_subject_service import ExcerptSubjectStudy
from .subject_robustness_service import SubjectRobustnessStudy
from .full_workflow_service import FullWorkflowStudy

import os
from .paths import ROOT

def load_env(path):
    if not path.exists():return
    for line in path.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        key,sep,value=line.partition('=')
        if not sep or not key.replace('_','').isalnum():raise ValueError('Invalid .env line.')
        value=value.strip()
        if len(value)>=2 and value[0]==value[-1] and value[0] in "\"'":value=value[1:-1]
        os.environ.setdefault(key,value)

def profiles():
    return {'jev':{'model':os.getenv('JEV_MODEL','jev-1.13.0'),'endpoint':os.getenv('JEV_ENDPOINT','https://api.typesafe.ai/v1/systemone'),
        'context_tokens':int(os.getenv('JEV_CONTEXT_TOKENS','32768')),'api_key':os.getenv('TYPESAFE_API_KEY',''),'deployment':'Hosted Jev API'}}

class App:
    def __init__(self,root=ROOT):
        self.root=Path(root)
        self.rca=PublicRCAStudy(root);self.presentation=PublicFormatStudy(root);self.replay=PublicRepeatStudy(root);self.temporal=PublicTemporalStudy(root);self.selective=PublicSelectiveStudy(root);self.agreement=PublicAgreementStudy(root);self.traces=PublicTraceStudy(root);self.trace_task=PublicTraceTaskStudy(root);self.evidence=PublicEvidenceStudy(root);self.claims=PublicClaimStudy(root);self.claim_language=PublicClaimLanguageStudy(root);self.reports=PublicReportStudy(root);self.binding=PublicBindingStudy(root);self.fresh_claims=PublicFreshClaimStudy(root);self.note_extraction=PublicNoteStudy(root);self.sentence_review=PublicSentenceStudy(root);self.note_language=PublicNoteLanguageStudy(root); self.extraction_contrast=PublicContrastStudy(root); self.claim_review=ClaimReviewStudy(self.note_language); self.assistant_review=AssistantReviewStudy(self.root); self.binding_corruption=BindingCorruptionStudy(self.root); self.subject_check=SubjectCheckStudy(self.root); self.separate_subject=SeparateSubjectStudy(self.root); self.direct_subject=DirectSubjectStudy(self.root); self.prefix_subject=PrefixSubjectStudy(self.root);self.excerpt_subject=ExcerptSubjectStudy(self.root);self.subject_robustness=SubjectRobustnessStudy(self.root);self.full_workflow=FullWorkflowStudy(self.root)


def handler_for(app):
    assets={name:('text/javascript' if name.endswith('.js') else 'text/css' if name.endswith('.css') else 'text/html; charset=utf-8') for name in (
        'subject-robustness.html','subject-robustness.js','full-workflow.html','full-workflow.js','diagnostic.css','excerpt-subject.html','excerpt-subject.js','excerpt-subject.css','prefix-subject.html','prefix-subject.js','prefix-subject.css','direct-subject.html','direct-subject.js','separate-subject.html','separate-subject.js','subject-check.html','subject-check.js','binding-corruption.html','binding-corruption.js','assistant-review.html','assistant-review.js','claim-review.html','claim-review.js','claim-review.css','public-note-language.html','public-note-language.js','public-note-language.css','public-extraction-contrast.html','public-extraction-contrast.js','public-extraction-contrast.css','public-sentence-review.html','public-sentence-review.js','public-sentence-review.css','public-note-extraction.html','public-note-extraction.js','public-note-extraction.css','public-fresh-claims.html','public-fresh-claims.js','public-claim-binding.html','public-claim-binding.js','public-report-reading.html','public-report-reading.js','public-report-reading.css','public-claim-language.html','public-claim-language.js','public-claims.html','public-claims.js','public-evidence.html','public-evidence.js','public-trace-task.html','public-trace-task.js','public-traces.html','public-traces.js','public-agreement.html','public-agreement.js','index.html','public-rca.html','public-format.html','public-rca.js','public-format.js','study.js',
        'public-selective.html','public-selective.js','public-temporal.html','public-temporal.js','public-repeat.html','public-repeat.js','public-repeat.css','public-rca.css','explorer.css','experiment3.css','report-language.css','study.css')}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def trusted(self):
            hosts={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
            return self.headers.get('Host') in hosts and self.headers.get('Origin') in {None,*('http://'+h for h in hosts)}
        def send(self,status,body,mime='application/json'):
            raw=body if isinstance(body,bytes) else json.dumps(body).encode()
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if not self.trusted():return self.send(403,{'error':'Local origin required.'})
            p=urlparse(self.path);q={k:v[0] for k,v in parse_qs(p.query).items()}
            try:
                if p.path=='/api/subject-robustness':return self.send(200,app.subject_robustness.overview())
                if p.path=='/api/subject-robustness/card':return self.send(200,app.subject_robustness.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/full-workflow':return self.send(200,app.full_workflow.overview())
                if p.path=='/api/full-workflow/card':return self.send(200,app.full_workflow.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/excerpt-subject':return self.send(200,app.excerpt_subject.overview())
                if p.path=='/api/excerpt-subject/card':return self.send(200,app.excerpt_subject.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/prefix-subject':return self.send(200,app.prefix_subject.overview())
                if p.path=='/api/prefix-subject/card':return self.send(200,app.prefix_subject.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/direct-subject':return self.send(200,app.direct_subject.overview())
                if p.path=='/api/direct-subject/card':return self.send(200,app.direct_subject.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/separate-subject':return self.send(200,app.separate_subject.overview())
                if p.path=='/api/separate-subject/card':return self.send(200,app.separate_subject.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/subject-check':return self.send(200,app.subject_check.overview())
                if p.path=='/api/subject-check/card':return self.send(200,app.subject_check.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/binding-corruption':return self.send(200,app.binding_corruption.overview())
                if p.path=='/api/binding-corruption/card':return self.send(200,app.binding_corruption.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/assistant-review':return self.send(200,app.assistant_review.overview())
                if p.path=='/api/assistant-review/card':return self.send(200,app.assistant_review.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/claim-review':return self.send(200,app.claim_review.overview())
                if p.path=='/api/claim-review/card':return self.send(200,app.claim_review.card(q.get('card')))
                if p.path=='/api/public-note-language':return self.send(200,app.note_language.overview())
                if p.path=='/api/public-note-language/card':return self.send(200,app.note_language.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-extraction-contrast':return self.send(200,app.extraction_contrast.overview())
                if p.path=='/api/public-extraction-contrast/card':return self.send(200,app.extraction_contrast.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-sentence-review':return self.send(200,app.sentence_review.overview())
                if p.path=='/api/public-sentence-review/card':return self.send(200,app.sentence_review.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-note-extraction':return self.send(200,app.note_extraction.overview())
                if p.path=='/api/public-note-extraction/card':return self.send(200,app.note_extraction.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-fresh-claims':return self.send(200,app.fresh_claims.overview())
                if p.path=='/api/public-fresh-claims/card':return self.send(200,app.fresh_claims.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-binding':return self.send(200,app.binding.overview())
                if p.path=='/api/public-binding/card':return self.send(200,app.binding.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-reports':return self.send(200,app.reports.overview())
                if p.path=='/api/public-reports/card':return self.send(200,app.reports.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-claim-language':return self.send(200,app.claim_language.overview())
                if p.path=='/api/public-claim-language/card':return self.send(200,app.claim_language.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-claims':return self.send(200,app.claims.overview())
                if p.path=='/api/public-claims/card':return self.send(200,app.claims.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-evidence':return self.send(200,app.evidence.overview())
                if p.path=='/api/public-evidence/card':return self.send(200,app.evidence.card(q.get('card'),q.get('reference')=='1'))
                if p.path=='/api/public-trace-task':return self.send(200,app.trace_task.overview())
                if p.path=='/api/public-trace-task/case':return self.send(200,app.trace_task.case(q.get('split','development'),q.get('dataset','Train Ticket'),q.get('case'),q.get('reference')=='1'))
                if p.path=='/api/public-traces':return self.send(200,app.traces.overview())
                if p.path=='/api/public-traces/case':return self.send(200,app.traces.case(q.get('dataset','Train Ticket'),q.get('case'),q.get('reference')=='1'))
                if p.path=='/api/public-agreement':return self.send(200,app.agreement.overview())
                if p.path=='/api/public-agreement/case':return self.send(200,app.agreement.case(q.get('dataset','Train Ticket'),q.get('case'),q.get('reference')=='1'))
                if p.path=='/api/public-selective':return self.send(200,app.selective.overview())
                if p.path=='/api/public-selective/case':return self.send(200,app.selective.case(q.get('split','evaluation'),q.get('case'),q.get('reference')=='1'))
                if p.path=='/api/public-temporal':return self.send(200,app.temporal.overview())
                if p.path=='/api/public-temporal/case':return self.send(200,app.temporal.case(q.get('case'),q.get('arm','named'),q.get('reference')=='1'))
                if p.path=='/api/public-repeat':return self.send(200,app.replay.overview())
                if p.path=='/api/public-repeat/case':return self.send(200,app.replay.case(q.get('case'),q.get('arm','named'),q.get('reference')=='1'))
                if p.path=='/api/public-rca':return self.send(200,app.rca.overview())
                if p.path=='/api/public-format':return self.send(200,app.presentation.overview())
                if p.path=='/api/public-rca/case':return self.send(200,app.rca.case(q.get('split','development'),q.get('case'),q.get('reference')=='1'))
                if p.path=='/api/public-format/case':return self.send(200,app.presentation.case(q.get('split','development'),q.get('case'),q.get('arm','compact'),q.get('reference')=='1'))
                if p.path=='/study':return self.send(200,render_study(app,q),'text/html; charset=utf-8')
                if p.path=='/study.md':
                    doc=q.get('doc','public-format')
                    if doc not in DOCUMENTS:raise ValueError('Unknown study document.')
                    return self.send(200,(app.root/DOCUMENTS[doc]).read_bytes(),'text/markdown; charset=utf-8')
                name={'/':'index.html','/public-rca':'public-rca.html','/public-format':'public-format.html','/repeatability':'public-repeat.html','/temporal':'public-temporal.html','/selective':'public-selective.html','/agreement':'public-agreement.html','/traces':'public-traces.html','/trace-task':'public-trace-task.html','/evidence-assessment':'public-evidence.html','/claim-assessment':'public-claims.html','/claim-language':'public-claim-language.html','/report-reading':'public-report-reading.html','/subject-robustness':'subject-robustness.html','/full-workflow':'full-workflow.html','/excerpt-subject':'excerpt-subject.html','/prefix-subject':'prefix-subject.html','/direct-subject':'direct-subject.html','/separate-subject':'separate-subject.html','/subject-check':'subject-check.html','/binding-corruption':'binding-corruption.html','/assistant-review':'assistant-review.html','/claim-review':'claim-review.html','/note-language':'public-note-language.html','/extraction-contrast':'public-extraction-contrast.html','/sentence-review':'public-sentence-review.html','/note-extraction':'public-note-extraction.html','/fresh-claims':'public-fresh-claims.html','/claim-binding':'public-claim-binding.html'}.get(p.path,p.path.lstrip('/'))
                if name in assets:return self.send(200,(Path(__file__).parent/'web'/name).read_bytes(),assets[name])
                return self.send(404,{'error':'Page not found.'})
            except (ValueError,KeyError,StopIteration):return self.send(400,{'error':'The requested evidence is invalid or unavailable.'})
            except OSError:return self.send(404,{'error':'The requested local evidence is unavailable.'})
        def do_POST(self):return self.send(405,{'error':'This inspection app is read-only.'})
    return Handler


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8769);args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Invalid port.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler_for(App()))
    print(f'Public operations lab: http://127.0.0.1:{args.port}/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
