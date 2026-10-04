"""Freeze, run or recompute the three-round fresh development comparison."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench.public_temporal_trial import freeze,run,score

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('freeze','run','score'));parser.add_argument('--env-file',default=str(ROOT/'.env'));parser.add_argument('--assessment');args=parser.parse_args()
    if args.action=='score':
        r=score()
        if args.assessment:
            with Path(args.assessment).open('x') as stream:stream.write(json.dumps(r,indent=2)+'\n')
        print(json.dumps({k:v for k,v in r.items() if k not in {'cases'}}))
    else:
        load_env(Path(args.env_file));p=profiles()['jev'];print(json.dumps(freeze(p) if args.action=='freeze' else run(p)))
if __name__=='__main__':main()
