"""Freeze and run only the subject-robustness diagnostic."""
import argparse
import json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env, profiles
from triage_bench.subject_robustness_trial import plan, freeze, run, score, RESULT, prepare


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','plan','freeze','run','score'));p.add_argument('--env-file',default=str(ROOT/'.env'));args=p.parse_args()
    if args.action in ('plan','run'):load_env(Path(args.env_file))
    if args.action=='prepare':result=prepare()
    elif args.action=='plan':result=plan(profiles()['jev'])
    elif args.action=='freeze':result=freeze()
    elif args.action=='run':result=run(profiles()['jev'])
    else:
        result=score()
        with RESULT.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('panels','outcomes','audit','files')}))


if __name__=='__main__':main()
