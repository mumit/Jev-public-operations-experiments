"""Verify and restore the public release without overwriting evidence."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import tarfile
from triage_bench.paths import ROOT


def digest(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def restore(archive,root=ROOT,manifest=None):
    archive=Path(archive);root=Path(root).resolve()
    manifest=manifest or json.loads((root/'evidence/public-study-v1.json').read_text())
    if digest(archive)!=manifest['archive_sha256']:raise ValueError('Archive checksum mismatch.')
    expected=manifest['files']
    with tarfile.open(archive,'r:gz') as bundle:
        members=bundle.getmembers();names=[m.name for m in members]
        if len(names)!=len(set(names)) or set(names)!=set(expected):raise ValueError('Archive contents differ from manifest.')
        for member in members:
            path=PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='runs' or not member.isfile():raise ValueError('Unsafe archive entry.')
            destination=root/str(path)
            if not destination.resolve().is_relative_to(root):raise ValueError('Unsafe destination.')
            if any(parent.is_symlink() for parent in [destination,*destination.parents] if parent!=root and parent.is_relative_to(root)):raise ValueError('Symlink destination.')
            if destination.exists():raise ValueError('Existing evidence will not be overwritten.')
            info=expected[member.name]
            if member.size!=info['bytes']:raise ValueError('Unexpected file size.')
            with bundle.extractfile(member) as stream:
                if hashlib.sha256(stream.read()).hexdigest()!=info['sha256']:raise ValueError('Evidence checksum mismatch.')
        # Validate the complete archive before any extraction. Destination parents
        # are checked above, and data filtering rejects links and special files.
        bundle.extractall(root,filter='data')
    return {'status':'restored','files':len(expected)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive');args=parser.parse_args()
    print(json.dumps(restore(args.archive)))
if __name__=='__main__':main()
