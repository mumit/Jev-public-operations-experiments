"""Keep selected source state fixed and define judgment of the claim as written."""
import copy
from .incident_scope_features import request as selected_request

ARMS=('legacy','literal')
CRITERIA={
    'supported':'The excerpt establishes the exact proposition in claim, including its subject, time, quantifiers and certainty.',
    'contradicted':'The excerpt establishes an incompatible proposition about the same subject, time and scope. An explicit statement that investigation is ongoing contradicts a claim that this report confirms its cause.',
    'not_established':'The excerpt neither establishes nor contradicts the exact proposition. Missing information alone is not a contradiction. Judge the claim as written rather than a substituted question about its underlying event.'}

def request(packet,arm):
    if arm not in ARMS:raise ValueError('Unknown literal-claim input arm.')
    body=selected_request(packet,'selected_section')
    if arm=='literal':
        body=copy.deepcopy(body);q=body['questions']['verdict'];q['criteria']=CRITERIA
        q['instructions']+=' Judge the complete claim as written. Do not replace it with a weaker proposition or a question about the underlying event. An assertion about what this report confirms is different from an assertion about whether its cause is known. Preserve the claim\'s quantifiers, temporal scope and certainty.'
    return body
