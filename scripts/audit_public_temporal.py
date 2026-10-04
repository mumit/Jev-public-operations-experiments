"""Save a separate exploratory timing audit without hosted calls."""
import argparse,json
from pathlib import Path
from triage_bench.public_temporal_audit import audit

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',default='checkpoints/public-temporal-audit-2026-10-03.json');args=parser.parse_args()
    result=audit()
    with Path(args.output).open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':'exploratory_audit','cases':len(result['cases']),'hosted_calls':0,'reserve_consumed':0}))
if __name__=='__main__':main()
