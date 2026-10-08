"""Audit frozen cross-publisher allocation without model inference."""
import argparse,json
from triage_bench import cross_report_audit as a
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('audit','verify','verify-public'));args=p.parse_args()
 r=a.audit() if args.action=='audit' else a.verify(local=args.action!='verify-public')
 print(json.dumps({'preparation_eligible':r['preparation_eligible'],'sources':[{k:s.get(k) for k in ('id','status','blocks','text_bytes','code_blocks','probe_wire_bytes','reason')} for s in r['sources']],'provider_calls':0},indent=2))
