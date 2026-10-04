"""Freeze, prepare, execute or verify fixed-boundary reserve confirmation."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench.public_confirmation_data import prepare,validate
from triage_bench.public_confirmation_trial import freeze_plan,freeze_stage,run,score

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','prepare','validate','freeze','run','score'));p.add_argument('--env-file',default=str(ROOT/'.env'));p.add_argument('--assessment');args=p.parse_args()
    if args.action in ('plan','run'):load_env(Path(args.env_file))
    if args.action=='plan':r=freeze_plan(profiles()['jev'])
    elif args.action=='prepare':r=prepare('confirmation')
    elif args.action=='validate':r=validate('confirmation')
    elif args.action=='freeze':r=freeze_stage()
    elif args.action=='run':r=run('confirmation',profiles()['jev'])
    else:
        r=score()
        if args.assessment:
            with Path(args.assessment).open('x') as stream:stream.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in {'datasets','files','downloads'}}))
if __name__=='__main__':main()
