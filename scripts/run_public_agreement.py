"""Freeze, prepare, execute or verify fresh-collection disagreement routing."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench.public_agreement_data import prepare,validate
from triage_bench.public_agreement_trial import freeze_plan,freeze_stage,run,score

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','prepare','validate','freeze','run','score'));p.add_argument('--env-file',default=str(ROOT/'.env'));p.add_argument('--assessment');args=p.parse_args()
    if args.action in ('plan','run'):load_env(Path(args.env_file))
    if args.action=='plan':r=freeze_plan(profiles()['jev'])
    elif args.action=='prepare':r=prepare('evaluation')
    elif args.action=='validate':r=validate('evaluation')
    elif args.action=='freeze':r=freeze_stage()
    elif args.action=='run':r=run('evaluation',profiles()['jev'])
    else:
        r=score()
        if args.assessment:
            with Path(args.assessment).open('x') as stream:stream.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in {'datasets','files','downloads'}}))
if __name__=='__main__':main()
