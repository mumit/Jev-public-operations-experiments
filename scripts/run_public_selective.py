"""Freeze, prepare, run and verify selective advisory policies, stage by stage."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench.public_selective_data import prepare,validate
from triage_bench.public_selective_trial import freeze_plan,freeze_stage,run,score,freeze_boundary

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','prepare','validate','freeze','run','score','boundary'));p.add_argument('--split',choices=('calibration','evaluation'),default='calibration');p.add_argument('--env-file',default=str(ROOT/'.env'));p.add_argument('--assessment');args=p.parse_args()
    if args.action in ('plan','run'):load_env(Path(args.env_file))
    if args.action=='plan':r=freeze_plan(profiles()['jev'])
    elif args.action=='prepare':r=prepare(args.split)
    elif args.action=='validate':r=validate(args.split)
    elif args.action=='freeze':r=freeze_stage(args.split)
    elif args.action=='run':r=run(args.split,profiles()['jev'])
    elif args.action=='boundary':r=freeze_boundary()
    else:
        r=score(args.split)
        if args.assessment:
            with Path(args.assessment).open('x') as stream:stream.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in {'outcomes','comparators','curves','files','downloads','selective','assessment'}}))
if __name__=='__main__':main()
