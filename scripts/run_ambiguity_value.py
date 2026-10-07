"""Prepare, run or replay the frozen ambiguity value comparison."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench import ambiguity_value_trial as t

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','prepare','freeze','run','score','verify'));p.add_argument('--env-file',default=str(ROOT/'.env'));a=p.parse_args()
    if a.action in ('plan','run'):load_env(Path(a.env_file))
    if a.action=='plan':r=t.plan(profiles()['jev'])
    elif a.action=='prepare':r=t.data.prepare(t.check_plan)
    elif a.action=='freeze':r=t.freeze()
    elif a.action=='run':r=t.run('development',profiles()['jev'])
    elif a.action=='verify':r=t.verify()
    else:
        r=t.score()
        with t.result_path().open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ('panels','outcomes','files','paired')}))
if __name__=='__main__':main()
