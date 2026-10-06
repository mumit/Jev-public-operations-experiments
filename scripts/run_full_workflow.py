"""Freeze and execute the separately budgeted complete-note workflow."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench import full_workflow_trial as t

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','freeze','run','score'));p.add_argument('--phase',choices=('initial','verdict'));p.add_argument('--env-file',default=str(ROOT/'.env'));a=p.parse_args()
 if a.action in ('plan','run'):load_env(Path(a.env_file))
 if a.action=='plan':r=t.plan(profiles()['jev'])
 elif a.action=='freeze':r=t.freeze(a.phase)
 elif a.action=='run':r=t.run(a.phase,profiles()['jev'])
 else:
  r=t.score()
  with t.RESULT.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k not in ('panels','outcomes','files')}))
if __name__=='__main__':main()
