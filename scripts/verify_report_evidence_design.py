"""Verify preparation only; never invoke a model or retrieve telemetry."""
import json
from triage_bench.report_evidence_service import ReportEvidenceStudy

def verify():
    result=ReportEvidenceStudy().overview()
    p=result['design']
    if p['stage']!='source_audit_complete_design_frozen_not_an_inference_protocol':
        raise ValueError('Unexpected study stage.')
    if (p['planned_unique_claims'],p['rounds'],p['max_development_provider_calls'],p['max_evaluation_provider_calls'],p['max_total_provider_calls'],p['retries'])!=(48,3,72,72,144,0):
        raise ValueError('Planned denominator or budget changed.')
    if p['profile']['display_probability']!=0.70 or p['candidate']!='rules_with_jev_assistance':
        raise ValueError('Candidate or fixed display policy changed.')
    for allocation in ('development','evaluation'):
        selected=[s for s in result['sources'] if s['primary'] and s['allocation']==allocation]
        if len(selected)!=4 or len({s['incident_group'] for s in selected})!=4:
            raise ValueError('Primary allocation changed.')
    return {'status':'verified_preparation_only','retained_sources':10,'failed_sources':2,'primary_reports':8,'planned_unique_claims':48,'max_new_provider_calls':144,'actual_new_provider_calls':0,'new_telemetry_recordings':0,'inference_protocol_exists':False}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
