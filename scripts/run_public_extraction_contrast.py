"""Freeze, run and assess only the new extraction-definition diagnostic."""
import argparse
import json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env, profiles
from triage_bench.public_note_v2_data import validate
from triage_bench.public_contrast_trial import plan, freeze, run, score, RESULT


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('plan', 'validate', 'freeze', 'run', 'score'))
    p.add_argument('--phase', choices=('extraction', 'verdict'), default='extraction')
    p.add_argument('--env-file', default=str(ROOT / '.env'))
    args = p.parse_args()
    if args.action in ('plan', 'run'):
        load_env(Path(args.env_file))
    if args.action == 'plan': result = plan(profiles()['jev'])
    elif args.action == 'validate': result = validate()
    elif args.action == 'freeze': result = freeze(args.phase)
    elif args.action == 'run': result = run(args.phase, profiles()['jev'])
    else:
        result = score()
        with RESULT.open('x') as f: f.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('datasets', 'files', 'requests', 'bindings', 'costs')}))


if __name__ == '__main__': main()
