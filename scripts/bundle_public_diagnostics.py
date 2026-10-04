"""Build a separate versioned evidence asset; never overwrite a released bundle."""
import argparse,gzip,hashlib,json,os,subprocess,tarfile
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env
from triage_bench.public_data import sha
from scripts.verify_public_diagnostics import verify

PREFIXES=('runs/public-repeat/diagnostic-2026-10-03-v1','runs/public-repeat/execution',
          'runs/public-temporal/development-2026-10-04-v1','runs/public-temporal/context-probe-2026-10-04-v1',
          'runs/public-temporal/comparison-development-2026-10-04-v1')


def build(output,manifest,env_file=None):
    output=Path(output);manifest=Path(manifest)
    if output.exists() or manifest.exists():raise ValueError('Use new archive and manifest paths.')
    verify()
    if env_file:load_env(Path(env_file))
    key=os.getenv('TYPESAFE_API_KEY','');needle=''.join(map(chr,[84,69,76,85,83])).casefold()
    files=sorted(p for prefix in PREFIXES for p in (ROOT/prefix).rglob('*') if p.is_file())
    if not files or any(p.is_symlink() or p.name=='.env' for p in files):raise ValueError('Unsafe bundle entry.')
    for p in files:
        data=p.read_bytes()
        if (key and key.encode() in data) or needle.encode() in data.lower():raise ValueError('Excluded identity or credential found in evidence.')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w') as archive:
        for p in files:
            info=archive.gettarinfo(str(p),arcname=str(p.relative_to(ROOT)));info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0;info.mode=0o644
            with p.open('rb') as stream:archive.addfile(info,stream)
    record={'schema':'public-diagnostics-evidence-1','archive':output.name,'archive_sha256':sha(output.read_bytes()),'bytes':output.stat().st_size,
        'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'requires':'public-study-v1','dataset_revision':'afeacb11bcc94dadfd1c8f483ee4377b2b8b614e',
        'recorded_hosted_calls':289,'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files}}
    with manifest.open('x') as stream:stream.write(json.dumps(record,indent=2)+'\n')
    return {'archive':output.name,'files':len(files),'bytes':record['bytes'],'sha256':record['archive_sha256']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);parser.add_argument('--manifest',default='evidence/public-diagnostics-v1.json');parser.add_argument('--env-file');args=parser.parse_args()
    print(json.dumps(build(args.output,args.manifest,args.env_file)))
if __name__=='__main__':main()
