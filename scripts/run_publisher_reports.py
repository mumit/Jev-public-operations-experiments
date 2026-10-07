"""Freeze, execute once or replay the publisher-report interpretation study."""
import argparse,json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env,profiles
from triage_bench import publisher_report_trial as t

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('freeze','check','run','score','verify','verify-public','export'));parser.add_argument('--phase',choices=('development','evaluation'),default='development');parser.add_argument('--env-file',default=str(ROOT/'.env'));a=parser.parse_args()
    if a.action=='run':load_env(Path(a.env_file));result=t.run(a.phase,profiles()['jev'])
    elif a.action=='freeze':result=t.freeze()
    elif a.action=='check':result={'status':'exact_protocol_verified','maximum_calls':t.check()['maximum_calls']}
    elif a.action=='score':result=t.score(a.phase);t.dump(t.result_path(a.phase),result)
    elif a.action=='export':result=t.export(a.phase)
    else:result=t.verify(a.phase,local=a.action!='verify-public')
    print(json.dumps({k:v for k,v in result.items() if k not in ('outcomes','panels','gates','paired','files')}))
if __name__=='__main__':main()
