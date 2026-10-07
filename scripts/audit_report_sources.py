"""Audit publisher reports or verify preserved local sources without inference."""
import argparse
import json
from triage_bench.report_source_audit import audit,verify
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('audit','verify','verify-catalog'))
    args=parser.parse_args()
    print(json.dumps(audit() if args.action=='audit' else verify(local=args.action!='verify-catalog'),indent=2))
