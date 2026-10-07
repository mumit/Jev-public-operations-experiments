"""Read-only provenance for a planned publisher-report comparison."""
import json
from pathlib import Path
from . import report_source_audit as audit
from .paths import ROOT

DESIGN = 'checkpoints/report-evidence-design-2026-10-07.json'
NOTES = 'checkpoints/report-source-audit-notes-2026-10-07.json'

class ReportEvidenceStudy:
    def __init__(self, root=ROOT):
        self.root = Path(root)

    def overview(self):
        if self.root.resolve() != ROOT.resolve():
            raise ValueError('Source provenance belongs to this checkout.')
        verified = audit.verify(local=False)
        record = json.loads(audit.AUDIT.read_text())
        design = json.loads((self.root/DESIGN).read_text())
        if design['audit_sha256'] != audit.digest(audit.AUDIT.read_bytes()) or design['catalog_sha256'] != audit.digest(audit.CATALOG.read_bytes()):
            raise ValueError('Design no longer matches the source audit.')
        notes = json.loads((self.root/NOTES).read_text())
        if design['audit_notes_sha256'] != audit.digest((self.root/NOTES).read_bytes()):
            raise ValueError('Failed-source provenance changed.')
        primary = set(design['primary_sources'])
        if len(primary) != 8 or not primary <= {s['id'] for s in record['sources'] if s['status']=='available'}:
            raise ValueError('Primary reports are unavailable or changed.')
        for source in record['sources']:
            failure = next((s for s in notes['failed_retrieved_sources'] if s['id'] == source['id']), None)
            if failure:
                source.update(failure)
                cached = audit.CACHE/(source['id']+'.html')
                if cached.exists() and audit.digest(cached.read_bytes()) != failure['raw_sha256']:
                    raise ValueError('Failed source snapshot changed.')
            source['display_title'] = source.get('title_observed') or notes['display_titles'].get(source['id']) or source['id']
        return {'verification':verified, 'stage':design['stage'], 'audit_date':record['audit_date'],
                'sources':[{**s,'primary':s['id'] in primary} for s in record['sources']],
                'design':design, 'local_cache_available':audit.CACHE.exists(),
                'new_provider_calls':0, 'new_telemetry_recordings':0,
                'human_reviews':0, 'independent_reference_reviews':0}
