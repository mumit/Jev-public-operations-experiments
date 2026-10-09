"""Publish answer evidence only; exclude full reports and full-text requests."""
import argparse,gzip,json,os,subprocess,tarfile
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env
from triage_bench.report_source_audit import digest
from scripts.verify_review_budget import verify

def build(output,manifest,env_file=None):
    output,manifest=Path(output),Path(manifest)
    if output.exists() or manifest.exists():raise ValueError('Preserve immutable archive and manifest.')
    verify()
    if env_file:load_env(Path(env_file))
    key=os.getenv('TYPESAFE_API_KEY','');needle=bytes([84,69,76,85,83]).lower()
    folder=ROOT/'runs/review-budget/public-evidence-v1'
    files=[folder/name for name in ('responses.jsonl','summary.json')]
    if {p for p in folder.rglob('*') if p.is_file()}!=set(files):raise ValueError('Unexpected public evidence, possibly full text.')
    for path in files:
        raw=path.read_bytes()
        if path.is_symlink() or needle in raw.lower() or key and key.encode() in raw:raise ValueError('Unsafe publication entry.')
        if path.name=='responses.jsonl':
            for line in raw.decode().splitlines():
                row=json.loads(line);reply=row['raw_response']
                if set(reply)!={'model','answers','usage'} or set(reply['answers'])!={'verdict'} or set(reply['answers']['verdict'])-{'type','choice','probabilities','confidence'}:raise ValueError('Unexpected response text.')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w') as archive:
        for path in files:
            info=archive.gettarinfo(str(path),arcname=str(path.relative_to(ROOT)));info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0;info.mode=0o644
            with path.open('rb') as stream:archive.addfile(info,stream)
    record={'schema':'review-budget-evidence-1','archive':output.name,'archive_sha256':digest(output.read_bytes()),'bytes':output.stat().st_size,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'requires':['publisher-reports-v1','incident-scope-v1','literal-claim-v1','selective-reports-v1','cross-reports-v1','report-knowledge-v1'],'recorded_hosted_calls':162,'full_source_reports':0,'full_text_requests':0,'verification_boundary':'Original provider payloads and method/gate replay using precommitted rule projections. Full request and rule reconstruction require local source snapshots.','files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in files}}
    with manifest.open('x') as stream:stream.write(json.dumps(record,indent=2)+'\n')
    return {'archive':output.name,'files':len(files),'actual_calls':162,'bytes':record['bytes'],'sha256':record['archive_sha256']}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--manifest',default='evidence/review-budget-v1.json');p.add_argument('--env-file');a=p.parse_args();print(json.dumps(build(a.output,a.manifest,a.env_file)))
