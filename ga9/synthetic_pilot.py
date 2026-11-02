"""Bounded synthetic engineering replay, never real-market performance evidence."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from .test_benchmarks import frame
from .run import main as run
from .verify import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.output.resolve()
    package = Path(__file__).resolve().parent
    if not (root.is_relative_to(package) or root.is_relative_to(Path('/tmp'))):
        parser.error('Output must be under GA9 or /tmp')
    root.mkdir(parents=True, exist_ok=False)
    dates = pd.bdate_range('2022-01-03', '2025-12-31')
    frames = []
    for j, symbol in enumerate(['A', 'B', 'C', 'D']):
        f = frame(symbol, dates, 1.)
        t = np.arange(len(dates))
        growth = .0004 + .002*np.sin(t/65+j*1.6)
        f['close'] = 100*np.exp(np.cumsum(growth))
        f['open'] = np.r_[100, f.close.to_numpy()[:-1]]
        f['high'] = f[['open','close']].max(axis=1)*1.001
        f['low'] = f[['open','close']].min(axis=1)*.999
        f['adj_close'] = f.close
        frames.append(f)
    pd.concat(frames).to_parquet(root/'stocks.parquet')
    frame('SPY', dates, 1.0002).to_parquet(root/'SPY.parquet')
    pd.DataFrame(dict(ticker=['A','B','C','D'],effective_from=['2022-01-01']*3+['2022-08-01'],
                      effective_to=[None,None,'2024-07-01',None],known_at=['2021-12-01']*4)).to_csv(root/'membership.csv',index=False)
    out = run(['--data',str(root/'stocks.parquet'),'--benchmark-data',str(root/'SPY.parquet'),
               '--membership',str(root/'membership.csv'),'--screen-top-k','2','--output',str(root/'run'),
               '--generations','1','--population','4','--budget','5','--horizons','5,20,60'])
    print(verify(out))

if __name__ == '__main__':
    main()
