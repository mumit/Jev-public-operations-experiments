"""A fixed question-only diagnostic of report knowledge versus incident facts."""
import copy
from .literal_claim_features import request as literal_request

ARMS=('literal','knowledge')
CRITERIA={
 'supported':'The excerpt supports the complete claim. For an incident-fact claim, the stated fact matches. For a claim about what the report says or establishes, its stated knowledge, uncertainty or confirmation matches that assertion.',
 'contradicted':'The excerpt explicitly conflicts with the complete claim in the same scope. For a report-knowledge claim, an explicit unknown or undetermined fact conflicts with an assertion that the report establishes it or leaves no uncertainty. Judge that assertion about the report, not a substituted question about the unknown event fact.',
 'not_established':'The excerpt neither supports nor explicitly conflicts with the complete claim. Use this for unreported or explicitly unknown underlying event facts. Missing discussion alone does not contradict a claim. Do not use it for a report-knowledge assertion that conflicts with the report explicitly saying the relevant fact is unknown.'}

def request(packet,arm):
 if arm not in ARMS:raise ValueError('Unknown report-knowledge arm.')
 body=literal_request(packet,'literal')
 if arm=='knowledge':
  body=copy.deepcopy(body);q=body['questions']['verdict'];q['criteria']=CRITERIA
  q['instructions']+=' First identify the proposition being asserted: an underlying incident fact, or what this report says, knows, identifies or establishes. For a report-knowledge assertion, evaluate the claimed reporting status itself. Explicit uncertainty can contradict an assertion of established knowledge even though the underlying event fact remains unknown. For an incident-fact assertion, an unknown fact remains not established unless an incompatible fact is stated. Return the verdict for the original complete claim. Do not substitute the underlying fact for a reporting assertion.'
 return body
