"""Instruction-only transformation; keep state, choices and manual references fixed."""
import copy
from .clarification_features import request as original,FIELDS

COMMON=('Assess only the named field, not whether the whole statement is complete or true. '
 'First apply the task scope: explicit health, causality, ownership, repair or trace-duration requests are outside this metric workflow. For those requests, this entry field MUST be not_applicable even if a name, assertion or time is explicit. '
 'Otherwise this is a bounded metric check, possibly incomplete. Return clear or clarify, never not_applicable. Other missing or conflicting fields do not make this field unclear. '
 'Apply any explicit final correction before judging the field. Available catalog entries are possible selections, not the analyst\'s selected values. No measurements are supplied or needed for this language classification. ')
RULES={
 'scope':'Classify the requested TASK only. Material scaled magnitude, positive scaled direction, their negations, and incomplete requests to check a metric are metric_check. Health, cause, ownership, repair or trace-duration tasks are outside_scope. Missing service, channel, comparison, assertion or window does not put a metric request outside scope. Do not decide whether the statement is true.',
 'service':'Field: SERVICE. clear requires one observed name as the claim subject, or its pronoun with one named antecedent. A second service in incidental background is not a second claim subject when the claim explicitly identifies one service. Two possible antecedents for its/it require clarify. A generic handler/backend alias absent from the catalog requires clarify. Ignore missing metrics, comparison, assertion or time for this field.',
 'channel':'Field: METRIC CHANNEL. clear requires one catalog channel or supplied alias. CPU/processor utilization selects cpu; memory selects mem. CPU OR memory requires clarify, as does an unspecified metric. A missing subject does not make an explicit channel ambiguous when that channel exists for the observed candidates. Ignore comparison, assertion and time.',
 'kind':'Field: COMPARISON MEANING. Material, absolute scaled magnitude >=3.0 and its negation identify the magnitude meaning. Positive signed change >0 and its negation identify direction. Vague worsening requires clarify. A choice between magnitude and direction requires clarify. Conflicting positive/negative assertions of the SAME comparison leave this field clear: that conflict belongs to polarity. An unavailable or unspecified time window leaves an explicit comparison meaning clear: that issue belongs to window. Ignore subject/channel incompleteness.',
 'polarity':'Field: ASSERTION. A declarative assertion, its explicit negation or a yes/no check about one condition is clear. Asserted vague worsening still has clear polarity even if kind is unclear. Contradictory assertions of the same condition require clarify. Mentioning only a metric, asking which comparison to choose or asking to select a condition requires clarify. Ignore missing subject/channel/window. A final corrected assertion supersedes earlier conflicting wording.',
 'window':'Field: TIME WINDOW SELECTION. clear requires expressly comparing before-incident with after-incident observations; their order in the sentence does not matter. No time comparison or a comparison against another period requires clarify. Merely making the before/after comparison available in context does not select it. Ignore subject, metric, comparison-kind and assertion issues.'}

def request(packet,arm):
    body=original(packet)
    if arm=='control':return body
    if arm!='focused':raise ValueError('Unknown instruction representation.')
    body=copy.deepcopy(body)
    for field in FIELDS:body['questions']['claim_'+field]['instructions']=RULES[field] if field=='scope' else COMMON+RULES[field]
    return body
