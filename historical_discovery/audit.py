"""Presence-only local audit. Does not open datasets, reports or credential files."""
import json
import os
from pathlib import Path
from .pipeline import write_new

CREDENTIAL_NAMES = ('POLYGON_API_KEY','MASSIVE_API_KEY','ALPACA_API_KEY','ALPACA_API_SECRET',
                    'APCA_API_KEY_ID','APCA_API_SECRET_KEY','NASDAQ_DATA_LINK_API_KEY',
                    'QUANDL_API_KEY','WRDS_USERNAME','WRDS_PASSWORD','TIINGO_API_KEY',
                    'FMP_API_KEY','EODHD_API_KEY')


def audit(roots):
    result = {'method':'Filesystem metadata only; no data payload opened',
              'inventory':{},'holdout_labels_accessed':False,
              'credentials':{k:bool(os.environ.get(k)) for k in CREDENTIAL_NAMES},
              'credential_files':{p:Path(p).exists() for p in ('.env','.aws/credentials',str(Path.home()/'.aws/credentials'))},
              'coverage':'Unverified; metadata cannot establish historical membership, adjustment policy or PIT availability.'}
    for value in roots:
        root=Path(value)
        extensions={};size=0;count=0
        for base,dirs,files in os.walk(root,followlinks=False):
            dirs[:]=sorted(d for d in dirs if d not in {'.git','__pycache__'})
            for name in sorted(files):
                p=Path(base)/name
                if p.is_symlink():continue
                size+=p.stat().st_size
                ext=p.suffix or '<none>'
                extensions[ext]=extensions.get(ext,0)+1
                count+=1
        result['inventory'][str(root)]={'files':count,'bytes':size,'extensions':extensions,
                                        'contents_read':False,'symlink_root':root.is_symlink(),'exists':root.exists()}
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('roots',nargs='+')
    args=parser.parse_args()
    write_new(args.out,audit(args.roots))
    print('Wrote presence-only audit; no dataset or credential payload read')
