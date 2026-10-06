"""Validate an analyst export and reconstruct its preview without inference."""
import argparse
import json
from triage_bench.claim_review import read_export, validate
from scripts.verify_public_note_language import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('export'); parser.add_argument('--preview-output')
    args = parser.parse_args()
    verify()
    result = validate(read_export(args.export))
    if args.preview_output:
        with open(args.preview_output, 'x') as f: f.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'request'}, indent=2))


if __name__ == '__main__': main()
