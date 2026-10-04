"""Freeze, run or inspect a separate exact-request diagnostic."""
import argparse
import json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench.public_repeat_trial import freeze,run
from triage_bench.public_repeat_results import score


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('freeze','run','score'))
    parser.add_argument('--protocol',default='checkpoints/public-repeat-protocol-2026-10-03.json')
    parser.add_argument('--output',default='runs/public-repeat/diagnostic-2026-10-03-v1');parser.add_argument('--assessment')
    parser.add_argument('--env-file',default=str(ROOT/'.env'));args=parser.parse_args()
    if args.action=='score':
        result=score(args.protocol,args.output)
        if args.assessment:
            with Path(args.assessment).open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:result[k] for k in ('distinct_cases','response_slots','failed_or_missing','metrics','research_gate')},indent=2))
    else:
        load_env(Path(args.env_file));profile=profiles()['jev']
        result=freeze(args.protocol,profile) if args.action=='freeze' else run(args.protocol,args.output,profile)
        print(json.dumps({k:v for k,v in result.items() if k in ('schema','distinct_cases','maximum_calls','attempted','failed','status','stopped_reason')}))
if __name__=='__main__':main()
