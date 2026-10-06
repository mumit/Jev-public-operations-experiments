"""Reference-free review packets; verifies the completed evidence first."""
from .claim_review import DATA, SCHEMA, fingerprint, load, options, packet, proposal, request_template


class ClaimReviewStudy:
    def __init__(self, evidence):
        self.evidence = evidence

    def overview(self):
        try:
            self.evidence.verified(); digest = fingerprint()
            return {'available': True, 'workflow_sha256': digest, 'schema': SCHEMA,
                'notes': [{'id': p['id'], 'dataset': p['dataset'], 'wording': p['wording']} for p in load(DATA / 'inputs.json')]}
        except (OSError, ValueError, KeyError):
            return {'available': False, 'error': 'Restore verified public evidence and the matching review workflow.'}

    def card(self, identifier):
        self.evidence.verified(); digest = fingerprint(); p = packet(identifier)
        return {'schema': SCHEMA, 'workflow_sha256': digest, 'id': p['id'], 'dataset': p['dataset'], 'wording': p['wording'],
            'note': p['note'], 'candidates': p['candidates'], 'options': options(p), 'proposal': proposal(identifier),
            'template': request_template(p)}
