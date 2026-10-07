"""Inspect recorded publisher-report decisions; browsing never invokes Jev."""
import json
from pathlib import Path
from .paths import ROOT
from . import publisher_report_trial as trial
from . import publisher_report_data as data
from .report_evidence_service import ReportEvidenceStudy
from .hosted import encoded
from .report_source_audit import digest

class PublisherReportStudy:
    def __init__(self,root=ROOT):self.root=Path(root)
    def overview(self):
        if self.root.resolve()!=ROOT.resolve():raise ValueError('Evidence belongs to this checkout.')
        d,claims,refs=data.metadata();source_audit=ReportEvidenceStudy().overview();source={s['id']:s for s in source_audit['sources']};results={}
        for phase in ('development','evaluation'):
            if trial.result_path(phase).exists():results[phase]=trial.verify(phase,local=False)
        if 'evaluation' in results and not results['development']['candidate_passes']:raise ValueError('Evaluation preceded passing development.')
        return {'phases':list(results),'results':{phase:{k:v for k,v in r.items() if k!='outcomes'} for phase,r in results.items()},
          'claims':[{**c,'source_title':source[c['source_id']]['display_title'],'publisher':source[c['source_id']]['publisher'],'source_url':source[c['source_id']]['url']} for c in claims if c['allocation'] in results],
          'actual_calls':sum(r['actual_calls'] for r in results.values()),'new_telemetry_recordings':0,'human_reviews':0,'independent_reference_reviews':0,'source_cache_available':data.audit.CACHE.exists()}
    def claim(self,phase,identifier,n=1,reveal=False,include_input=False):
        if phase not in ('development','evaluation') or n not in (1,2,3):raise ValueError('Unknown selection.')
        r=trial.verify(phase,local=False);d,claims,refs=data.metadata();c=next(c for c in claims if c['id']==identifier and c['allocation']==phase)
        recorded,summary=trial.rows(phase,local=False);row=next((x for x in recorded if x['claim_id']==identifier and x['round']==n),None)
        outcomes={o['method']:{'prediction':o['prediction'],**({k:o[k] for k in ('correct_choice','correct_display','wrong_display','withheld')} if reveal else {})} for o in r['outcomes'] if o['id']==identifier and o['round']==n}
        reference=next(x for x in refs if x['id']==identifier) if reveal else None
        request=None
        if include_input:
            path=trial.destination(phase)/'requests.json'
            if path.exists():
                job=next(x for x in data.load(path) if x['claim_id']==identifier and x['round']==n)
                if digest(encoded(job['body']))!=job['request_sha256']:raise ValueError('Exact local request changed.')
                request=job['body']
        return {'claim':c,'round':n,'outcomes':outcomes,'reference':reference,'row':row,'request':request,'request_sha256':row['request_sha256'] if row else None,'exact_input_available':(trial.destination(phase)/'requests.json').exists(),'input_note':'Complete publisher text stays in local snapshots and full-text requests. The public bundle preserves choices, probabilities, usage, hashes and replayable method composition.'}
