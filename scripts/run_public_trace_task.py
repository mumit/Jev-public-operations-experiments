"""Freeze, prepare, execute, score or promote a trace-aware task study."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench.public_trace_task_data import prepare,validate
from triage_bench.public_trace_task_trial import freeze_plan,freeze_stage,run,score,promote

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','prepare','validate','freeze','run','score','promote'));p.add_argument('--split',choices=('development','evaluation'),default='development');p.add_argument('--env-file',default=str(ROOT/'.env'));p.add_argument('--assessment');a=p.parse_args()
    if a.action in ('plan','run'):load_env(Path(a.env_file))
    if a.action=='plan':r=freeze_plan(profiles()['jev'])
    elif a.action=='prepare':r=prepare(a.split)
    elif a.action=='validate':r=validate(a.split)
    elif a.action=='freeze':r=freeze_stage(a.split)
    elif a.action=='run':r=run(a.split,profiles()['jev'])
    elif a.action=='promote':r=promote()
    else:
        r=score(a.split)
        if a.assessment:
            with Path(a.assessment).open('x') as stream:stream.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in {'datasets','files','downloads'}}))
if __name__=='__main__':main()
