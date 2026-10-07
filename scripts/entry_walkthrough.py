"""Prepare the frozen walkthrough or assess a private export without inference."""
import argparse,json
from pathlib import Path
from triage_bench import entry_walkthrough as t

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('plan','prepare','freeze','verify','assess'));p.add_argument('--export');p.add_argument('--allow-preview',action='store_true');a=p.parse_args()
    if a.action=='assess':
        if not a.export:p.error('--export is required for assess')
        r=t.validate_export(json.loads(Path(a.export).read_text()),a.allow_preview)
    else:r=getattr(t,a.action)()
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
