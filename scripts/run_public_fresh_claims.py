"""Prepare and execute only the new, nine-recording confirmation protocol."""
import argparse
import json
from pathlib import Path
from triage_bench.paths import ROOT
from triage_bench.app import load_env, profiles
from triage_bench.public_fresh_claim_data import prepare, validate
from triage_bench.public_fresh_claim_trial import plan, freeze, run, score, RESULT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'prepare', 'validate', 'freeze', 'run', 'score'))
    parser.add_argument('--env-file', default=str(ROOT / '.env'))
    args = parser.parse_args()
    if args.action in ('plan', 'run'):
        load_env(Path(args.env_file))
    if args.action == 'plan':
        result = plan(profiles()['jev'])
    elif args.action == 'prepare':
        result = prepare()
    elif args.action == 'validate':
        result = validate()
    elif args.action == 'freeze':
        result = freeze()
    elif args.action == 'run':
        result = run(profiles()['jev'])
    else:
        result = score()
        with RESULT.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in {'datasets', 'files', 'requests', 'downloads'}}))


if __name__ == '__main__':
    main()
