import argparse
from pathlib import Path
from .core import Config, development_year
from .pipeline import freeze, run
from .fixture import FixtureAdapter
from .adapters import JsonAdapter


def main():
    p=argparse.ArgumentParser(description='Discovery-only research pipeline; evaluation years locked')
    sub=p.add_subparsers(dest='command',required=True)
    demo=sub.add_parser('fixture',help='Run invented 2005–2009 functionality demonstration')
    demo.add_argument('--out',required=True,type=Path)
    fr=sub.add_parser('freeze',help='Freeze code, definitions, candidates, metrics and tests')
    fr.add_argument('--out',required=True,type=Path)
    real=sub.add_parser('run',help='Read explicit single-year, attested discovery manifests')
    real.add_argument('--out',required=True,type=Path)
    real.add_argument('--manifest',action='append',required=True,help='YEAR=PATH; contiguous years from 2005')
    args=p.parse_args()
    cfg=Config()
    if args.command=='freeze':freeze(args.out,cfg)
    elif args.command=='fixture':
        freeze(args.out,cfg)
        run({y:FixtureAdapter(y) for y in range(2005,2010)},args.out,cfg)
    else:
        adapters={}
        for spec in args.manifest:
            year,path=spec.split('=',1)
            year=int(year)
            development_year(year)
            if year in adapters:p.error('Duplicate year')
            adapters[year]=JsonAdapter(path)
        run(adapters,args.out,cfg)
    print(f'Artifacts: {args.out}; 2010/2011 remain locked')


if __name__=='__main__':main()
