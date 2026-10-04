"""Verify archived source and standalone extraction without rewriting history."""
import json
from pathlib import Path
from .public_data import sha
from .paths import ROOT


def migration():
    return json.loads((ROOT/'provenance/migration.json').read_text())


def verify_sources(expected):
    manifest=migration()
    historical=expected in manifest['historical_source_sets']
    base=ROOT/'provenance/source' if historical else ROOT
    for name,digest in expected.items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe source path.')
        if sha((base/path).read_bytes())!=digest:raise ValueError('Frozen source drift: '+name)
    if historical:
        for name,digest in manifest['active_source_sha256'].items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Standalone baseline drift: '+name)


def reject_historical_inference(protocol):
    if sha(Path(protocol).read_bytes()) in migration()['historical_protocol_sha256'].values():
        raise ValueError('This completed historical protocol is read-only. Freeze a separate protocol for new calls.')
