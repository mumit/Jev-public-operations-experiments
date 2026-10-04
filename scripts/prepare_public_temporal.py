"""Freeze or prepare fresh development only; never call a model."""
import argparse,json
from pathlib import Path
from triage_bench.public_temporal_data import freeze_preparation,prepare,validate
from triage_bench.paths import ROOT

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('freeze','prepare','validate'))
    parser.add_argument('--index',default=str(ROOT/'runs/public-data/preflight-2026-10-03-v1/cases.parquet'))
    parser.add_argument('--plan',default='checkpoints/public-temporal-preparation-2026-10-04.json');parser.add_argument('--folder',default='runs/public-temporal/development-2026-10-04-v1');args=parser.parse_args()
    r=freeze_preparation(args.index,args.plan) if args.action=='freeze' else prepare(args.plan,args.index,args.folder) if args.action=='prepare' else validate(args.plan,args.folder)
    print(json.dumps({k:v for k,v in r.items() if k in ('schema','counts','maximum_cases','downloaded_cases','hosted_calls','fits_context','sealed_cases')}))
if __name__=='__main__':main()
