"""Prepare and run the separate, bounded report-reading diagnostic."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench.public_report_data import prepare,validate
from triage_bench.public_report_trial import plan,freeze,run,score,RESULT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','prepare','validate','freeze','run','score'));p.add_argument('--env-file',default=str(ROOT/'.env'));a=p.parse_args()
    if a.action in ('plan','run'):load_env(Path(a.env_file))
    if a.action=='plan':r=plan(profiles()['jev'])
    elif a.action=='prepare':r=prepare()
    elif a.action=='validate':r=validate()
    elif a.action=='freeze':r=freeze()
    elif a.action=='run':r=run(profiles()['jev'])
    else:
        r=score()
        with RESULT.open('x') as stream:stream.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in {'datasets','files','requests'}}))
if __name__=='__main__':main()
