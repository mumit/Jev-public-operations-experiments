"""Audit the committed new-report allocation or replay its provenance."""
import argparse,json
from triage_bench import selective_report_audit as a
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('audit','verify','verify-public'));args=p.parse_args()
    r=a.audit() if args.action=='audit' else a.verify(local=args.action!='verify-public')
    print(json.dumps({'preparation_eligible':r['preparation_eligible'],'sources':[{'id':s['id'],'status':s['status'],'incident_sections':s.get('incident_sections'),'reason':s.get('reason')} for s in r['sources']],'provider_calls':0},indent=2))
if __name__=='__main__':main()
