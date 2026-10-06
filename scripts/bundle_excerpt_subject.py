"""Package the excerpt-subject diagnostic as a new, immutable release asset."""
import argparse
import gzip
import json
import os
import subprocess
import tarfile
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env
from triage_bench.public_data import sha
from scripts.verify_excerpt_subject import verify

PREFIXES = ('runs/excerpt-subject/hosted-2026-10-06-v1',)


def build(output, manifest, env_file=None):
    import pyarrow.parquet as pq
    output, manifest = Path(output), Path(manifest)
    if output.exists() or manifest.exists():
        raise ValueError('Use new archive and manifest paths.')
    verification = verify()
    if verification['human_reviews'] != 0 or verification['independent_reviews'] != 0:
        raise ValueError('Note diagnostic must open no fresh recording.')
    if env_file:
        load_env(Path(env_file))
    key = os.getenv('TYPESAFE_API_KEY', '')
    needle = ''.join(map(chr, [84, 69, 76, 85, 83])).casefold()
    files = sorted(p for prefix in PREFIXES for p in (ROOT / prefix).rglob('*') if p.is_file())
    if not files or any(p.is_symlink() or p.name == '.env' for p in files):
        raise ValueError('Unsafe bundle entry.')
    for path in files:
        raw = path.read_bytes()
        if (key and key.encode() in raw) or needle.encode() in raw.lower():
            raise ValueError('Excluded identity or credential in evidence.')
        if path.suffix == '.parquet':
            table = pq.read_table(path)
            for field in table.schema:
                if str(field.type) in ('string', 'large_string'):
                    for value in table.column(field.name).to_pylist():
                        if value is not None and (needle in value.casefold() or key and key in value):
                            raise ValueError('Excluded text in compressed source telemetry.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as compressed, tarfile.open(fileobj=compressed, mode='w') as archive:
        for path in files:
            info = archive.gettarinfo(str(path), arcname=str(path.relative_to(ROOT)))
            info.uid = info.gid = 0
            info.uname = info.gname = ''
            info.mtime, info.mode = 0, 0o644
            with path.open('rb') as stream:
                archive.addfile(info, stream)
    record = {'schema': 'excerpt-subject-evidence-1', 'archive': output.name,
              'archive_sha256': sha(output.read_bytes()), 'bytes': output.stat().st_size,
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'requires': ['public-study-v1', 'public-diagnostics-v1', 'public-selective-v1', 'public-confirmation-v1', 'public-agreement-v1', 'public-traces-development-v1', 'public-trace-task-v1', 'public-evidence-assessment-v1', 'public-claim-assessment-v1', 'public-claim-language-v1', 'public-report-reading-v1', 'public-claim-binding-v1', 'public-fresh-claims-v1', 'public-note-extraction-v1', 'public-sentence-review-v1', 'public-extraction-contrast-v1', 'public-note-language-v1', 'assistant-review-v1', 'binding-corruption-v1', 'subject-check-v1', 'separate-subject-v1', 'direct-subject-v1','prefix-subject-v1'],
              'dataset_revision': 'afeacb11bcc94dadfd1c8f483ee4377b2b8b614e', 'recorded_hosted_calls': verification['recorded_calls'],
              'files': {str(p.relative_to(ROOT)): {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in files}}
    with manifest.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    return {'archive': output.name, 'files': len(files), 'bytes': record['bytes'], 'sha256': record['archive_sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--manifest', default='evidence/excerpt-subject-v1.json')
    parser.add_argument('--env-file')
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.manifest, args.env_file)))
