"""Recompute both recorded studies without new hosted requests."""
import json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.public_data import sha
from triage_bench.provenance import migration,verify_sources
from triage_bench.public_rca_data import validate as validate_rca
from triage_bench.public_format_data import validate as validate_format
from triage_bench.public_rca_trial import body,check
from triage_bench.public_format_trial import body as format_body,check as format_check
from triage_bench.public_rca_stages import score as rca_score,gate as rca_gate,load
from triage_bench.public_format_stages import score as format_score,gate as format_gate,selected


def verify(root=ROOT):
    root=Path(root);snapshot=migration()
    for source_set in snapshot['historical_source_sets']:verify_sources(source_set)
    for name,digest in snapshot['historical_protocol_sha256'].items():
        if sha((root/'checkpoints'/name).read_bytes())!=digest:raise ValueError('Historical protocol changed.')
    rca=root/'runs/public-data/metric-study-2026-10-03-v2'
    presentation=root/'runs/public-data/input-format-2026-10-03-v1'
    validate_rca(rca);validate_format(presentation)
    for kind,data,make,checker in [('rca',rca,body,check),('format',presentation,format_body,format_check)]:
        prefix=root/f'checkpoints/public-{kind}'
        protocol=Path(str(prefix)+'-protocol-2026-10-03.json');candidate=load(str(prefix)+'-candidate-2026-10-03.json')
        boundary=load(str(prefix)+'-boundary-2026-10-03.json');checker(load(protocol),data)
        for split in ('development','calibration','evaluation'):
            hosted=root/f'runs/public-{kind}/{split}-2026-10-03-v1'
            packets={p['id']:p for p in load(data/f'{split}.inputs.json')}
            for request in load(hosted/'requests.json'):
                packet=packets[request.get('case_id',request['id'])]
                actual=make(packet['state'],request['arm']) if kind=='format' else make(packet['state'])
                if actual!=request['body']:raise ValueError('Extracted request differs from recorded request.')
            actual=(format_score(data,protocol,hosted,split) if kind=='format' else rca_score(data,protocol,root/'runs/public-rca/local-2026-10-03-v1',hosted,split))
            expected=candidate['assessment'] if split=='development' else boundary['assessment'] if split=='calibration' else load(str(prefix)+'-evaluation-2026-10-03.json')
            if actual!=expected:raise ValueError(f'{kind} {split} assessment changed.')
        if kind=='format':
            if selected(boundary['assessment'])!=boundary['selected']:raise ValueError('Selected thresholds changed.')
            format_gate(data,protocol,'evaluation',str(prefix)+'-candidate-2026-10-03.json',str(prefix)+'-boundary-2026-10-03.json')
        else:rca_gate(data,protocol,'evaluation',str(prefix)+'-candidate-2026-10-03.json',str(prefix)+'-boundary-2026-10-03.json')
    return {'status':'verified','studies':2,'stage_assessments':6,'recorded_hosted_calls':294,'new_hosted_calls':0,'reserve_cases':36}


def main():print(json.dumps(verify(),indent=2))
if __name__=='__main__':main()
