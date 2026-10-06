"""Expand explicitly read note mappings; never read references or measurements."""
import json
from pathlib import Path
from triage_bench.claim_review import fingerprint, proposal, SCHEMA, validate
from triage_bench.public_note_language_data import DATA
from triage_bench.public_data import sha
# Note-specific choices made from the complete prose shown in this conversation.
# M: magnitude/duration/cause block first; D: direction/count/health block first.
# Every note ID and block order is explicit, not inferred by a parser.
assignments = [
 ('NWL-6a1a2c127a1d','D','ts-config-service','socket','negative','duration_median_us','negative','ts-preserve-other-mongo','mem','positive'),
 ('NWL-41460bbdf301','M','ts-config-service','socket','negative','duration_median_us','negative','ts-preserve-other-mongo','mem','positive'),
 ('NWL-a059c4e9b227','M','ts-config-service','socket','negative','duration_median_us','negative','ts-preserve-other-mongo','mem','positive'),
 ('NWL-ebebeada049f','M','ts-admin-travel-service','socket','negative','duration_median_us','negative','ts-ticket-office-mongo','mem','positive'),
 ('NWL-7432a7ac9d8b','D','ts-admin-travel-service','socket','negative','duration_median_us','negative','ts-ticket-office-mongo','mem','positive'),
 ('NWL-9a3498667b9c','M','ts-admin-travel-service','socket','negative','duration_median_us','negative','ts-ticket-office-mongo','mem','positive'),
 ('NWL-db3d395ffc58','D','ts-config-service','socket','negative','duration_p90_us','negative','ts-travel-mongo','cpu','negative'),
 ('NWL-82c22b90a8fb','M','ts-config-service','socket','negative','duration_p90_us','negative','ts-travel-mongo','cpu','negative'),
 ('NWL-c8311dd5cb61','M','ts-config-service','socket','negative','duration_p90_us','negative','ts-travel-mongo','cpu','negative'),
 ('NWL-a87649ebaa1a','M','cartservice','mem','negative','uncovered_duration_median_us','negative','redis','cpu','positive'),
 ('NWL-fe6c9911a37a','D','cartservice','mem','negative','uncovered_duration_median_us','negative','redis','cpu','positive'),
 ('NWL-eafa3a940729','D','cartservice','mem','negative','uncovered_duration_median_us','negative','redis','cpu','positive'),
 ('NWL-039d6ebdd81f','D','recommendationservice','latency-50','negative','duration_median_us','negative','adservice','latency-90','positive'),
 ('NWL-f49033838aa3','M','recommendationservice','latency-50','negative','duration_median_us','negative','adservice','latency-90','positive'),
 ('NWL-0f527b766ed7','M','recommendationservice','latency-50','negative','duration_median_us','negative','adservice','latency-90','positive'),
 ('NWL-b3fb5e096258','D','emailservice','cpu','positive','duration_p90_us','positive','frontend-external','error','positive'),
 ('NWL-aa6833fe95e5','M','emailservice','cpu','positive','duration_p90_us','positive','frontend-external','error','positive'),
 ('NWL-b71d39d22677','D','emailservice','cpu','positive','duration_p90_us','positive','frontend-external','error','positive'),
 ('NWL-7e13ecc55427','D','recommendationservice','workload','negative','duration_median_us','positive','shippingservice','mem','positive'),
 ('NWL-212a9d0deac9','D','recommendationservice','workload','negative','duration_median_us','positive','shippingservice','mem','positive'),
 ('NWL-ee7105dd992e','D','recommendationservice','workload','negative','duration_median_us','positive','shippingservice','mem','positive'),
 ('NWL-1aaf4aca9f84','M','productcatalogservice','latency-50','positive','uncovered_duration_median_us','negative','redis','cpu','positive'),
 ('NWL-4f51f156ed8b','D','productcatalogservice','latency-50','positive','uncovered_duration_median_us','negative','redis','cpu','positive'),
 ('NWL-9dc6904d0134','D','productcatalogservice','latency-50','positive','uncovered_duration_median_us','negative','redis','cpu','positive'),
 ('NWL-85a3178b8cec','M','recommendationservice','latency-90','negative','duration_median_us','negative','redis','cpu','positive'),
 ('NWL-42acf5afe858','M','recommendationservice','latency-90','negative','duration_median_us','negative','redis','cpu','positive'),
 ('NWL-59bca7262cdd','M','recommendationservice','latency-90','negative','duration_median_us','negative','redis','cpu','positive'),
]
# Only public text/candidate fields are read for the review artifact. Measurements
# and original annotation files are neither selected nor used to make decisions.
notes={p['id']:{k:p[k] for k in ('id','dataset','wording','note','candidates')} for p in json.loads((DATA/'inputs.json').read_text())}
records=[]
for identifier,order,a,channel,mp,measure,dp,b,direction,sp in assignments:
 p=notes[identifier]; original=proposal(identifier)
 positions={'m':(2,3,4),'d':(6,7,8)} if order=='M' else {'m':(6,7,8),'d':(3,4,5)}
 decisions={f's{i:02d}':{'decision':'withhold','reason':'non_assertion'} for i in (1,9,10,5 if order=='M' else 2)}
 decisions.update(s11={'decision':'withhold','reason':'multiple_assertions'},s12={'decision':'withhold','reason':'unresolved'})
 claims=[(*positions['m'][:1],a,'metric_material',channel,'none_or_unclear',mp),
 (positions['m'][1],a,'duration_material','none_or_unclear',measure,dp),
 (positions['m'][2],a,'causality','none_or_unclear','none_or_unclear','positive'),
 (positions['d'][0],b,'metric_direction',direction,'none_or_unclear',sp),
 (positions['d'][1],b,'span_adequacy','none_or_unclear','none_or_unclear','positive'),
 (positions['d'][2],b,'health','none_or_unclear','none_or_unclear','positive')]
 for i,service,kind,ch,ms,polarity in claims:
  decisions[f's{i:02d}']={'decision':'confirm','values':dict(role='assertion',service=service,kind=kind,channel=ch,measure=ms,polarity=polarity)}
 payload={'schema':SCHEMA,'workflow_sha256':fingerprint(),'note_id':identifier,'proposal':original,'reviews':decisions}
 validate(payload)
 records.append({'note_id':identifier,'dataset':p['dataset'],'wording':p['wording'],'note_sha256':sha(p['note'].encode()),
   'sentences':[{'id':c['id'],'text':c['text'],'decision':decisions[c['id']]} for c in p['candidates']], 'export':payload})
record={'schema':'assistant-review-decisions-1','reviewer':'Codex assistant, same author as controlled notes and annotations',
 'human_review':False,'independent_review':False,'blinded':False,'reference_access_this_review':'Decisions written from complete prose, before reopening frozen references in this continuation. Earlier annotation authorship and exposure remain known.',
 'method':'Explicit per-note service, channel, measure, polarity and block-order decisions. A mechanical expansion writes the twelve sentence records; no telemetry verdict or gold annotation supplies a decision.',
 'scope':'27 controlled notes, nine inspected recordings. No authentic report, specialist validation, human equivalence or effort claim.',
 'rationale':{'metric_material':'Compare absolute scaled change to 3.0; below/not reach/fall short are negative; at least/not below/meet are positive.',
 'duration_material':'Compare absolute relative duration change to 25%; less than/below/fall short are negative; no less than/not below/meet are positive.',
 'metric_direction':'Positive/not zero or negative/above zero are positive; nonpositive/not greater than zero/at or below zero are negative.',
 'span_adequacy':'Each window at least five, neither window fewer than five, and both meeting the minimum express the same positive count property.',
 'health_causality':'Endorsed single health/cause assertions are in scope; deciding their truth is a later evidence task.',
 'withholding':'Heading, request/question and explicitly unendorsed allegation are non-assertions; the compound has two assertions; the final either/or subject is unresolved.',
 'pronouns':'The intact preceding service block supplies the unique local antecedent; requested checks establish a subject without themselves asserting a telemetry fact.'},
 'records':records}
path=Path('checkpoints/assistant-review-decisions-2026-10-05.json')
with path.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
print({'notes':len(records),'decisions':sum(len(r['sentences']) for r in records),'human_reviews':0})
