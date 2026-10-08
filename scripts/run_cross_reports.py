"""Prepare, freeze or replay the whole-report cross-publisher comparison."""
import argparse,json
from pathlib import Path
from triage_bench.app import load_env,profiles
from triage_bench import cross_report_trial as trial
from triage_bench import cross_report_data as data

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','freeze','check','run','score','verify','verify-public','export'));p.add_argument('--env-file',default=str(data.ROOT/'.env'));a=p.parse_args()
    if a.action=='prepare':r=data.prepare();trial.dump(data.PACK,r)
    elif a.action=='freeze':r=trial.freeze()
    elif a.action=='check':r={'verified':bool(trial.check()),'maximum_calls':162}
    elif a.action=='run':load_env(Path(a.env_file));r=trial.run(profiles()['jev'])
    elif a.action=='score':r=trial.score();trial.dump(trial.RESULT,r)
    elif a.action=='export':r=trial.export()
    else:r=trial.verify(local=a.action!='verify-public')
    print(json.dumps({k:v for k,v in r.items() if k not in ('outcomes','panels','paired','gates','files','fixtures','inventory','claims','references')}))
if __name__=='__main__':main()
