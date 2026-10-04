"""Prepare and evaluate the separate public metric root-cause study."""
import argparse
import json
from triage_bench.public_rca_data import build, validate

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('build','validate','freeze','local','jev','candidate','boundary','score'))
    parser.add_argument('--data',default='runs/public-data/metric-study-2026-10-03-v2')
    parser.add_argument('--index',default='runs/public-data/preflight-2026-10-03-v1/cases.parquet')
    parser.add_argument('--protocol',default='checkpoints/public-rca-protocol-2026-10-03.json')
    parser.add_argument('--candidate',default='checkpoints/public-rca-candidate-2026-10-03.json')
    parser.add_argument('--boundary',default='checkpoints/public-rca-boundary-2026-10-03.json')
    parser.add_argument('--split',choices=('development','calibration','evaluation'),default='development')
    parser.add_argument('--local',default='runs/public-rca/local-2026-10-03-v1')
    parser.add_argument('--hosted')
    parser.add_argument('--output')
    args=parser.parse_args()
    hosted=args.hosted or f'runs/public-rca/{args.split}-2026-10-03-v1'
    if args.action=='build':result=build(args.data,args.index)
    elif args.action=='validate':result=validate(args.data)
    elif args.action in ('freeze','jev'):
        from triage_bench.app import load_env,profiles
        from triage_bench.dataset import ROOT
        from triage_bench.public_rca_trial import freeze,run
        load_env(ROOT/'.env');profile=profiles()['jev']
        result=freeze(args.data,args.protocol,profile) if args.action=='freeze' else run(args.data,args.protocol,hosted,profile,args.split,args.candidate,args.boundary)
    elif args.action=='local':
        from triage_bench.public_rca_models import run_local
        result=run_local(args.data,args.local)
    else:
        from triage_bench.public_rca_stages import freeze_candidate,freeze_boundary,score
        if args.action=='candidate':result=freeze_candidate(args.data,args.protocol,args.local,hosted,args.candidate)
        elif args.action=='boundary':result=freeze_boundary(args.data,args.protocol,args.candidate,hosted,args.boundary)
        else:
            result=score(args.data,args.protocol,args.local,hosted,args.split)
            if args.output:
                from pathlib import Path
                from triage_bench.public_rca_data import dump
                if Path(args.output).exists():raise ValueError('Assessment already exists.')
                dump(args.output,result)
    print(json.dumps({k:result[k] for k in ('schema','counts','status','split','metrics','selected') if k in result}))

if __name__=='__main__':main()
