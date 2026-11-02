"""Local research entry point; stage authorization precedes opening the bundle."""
import argparse
import json
from .adapters import ROOT
from .executor import execute


def main():
    parser = argparse.ArgumentParser(description='Controlling v2 local executor')
    sub = parser.add_subparsers(dest='command',required=True)
    run = sub.add_parser('execute')
    run.add_argument('--bundle',required=True)
    run.add_argument('--stage',type=int,choices=(1,2),required=True)
    # Retain old command fail-closed, including before any path access.
    legacy = sub.add_parser('run')
    legacy.add_argument('--prices'); legacy.add_argument('--members')
    legacy.add_argument('--years'); legacy.add_argument('--out')
    args = parser.parse_args()
    try:
        if args.command != 'execute':
            raise ValueError('Stage2 SEALED: use stage-specific verified bundle executor')
        manifest = json.loads((ROOT/'manifest.json').read_text())
        result = execute(args.bundle,args.stage,manifest)
        print(json.dumps(dict(valid=result['valid'],passers=result['passers'])))
    except (ValueError,KeyError,FileExistsError,OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
