"""Independent saved-trade dollar ledger and training-selection verification."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from ga10 import SOURCE,ROOT,fitness
raw=pd.read_parquet(SOURCE)
raw.date=pd.to_datetime(raw.date)
raw=raw[raw.date.between('2008-12-01','2018-12-31')]
raw['fill']=raw.open*raw.adj_close/raw.close
p=raw.set_index(['date','ticker'])
opens=p['fill'].to_dict();closes=p['adj_close'].to_dict()
checked=0
for folder in ['smoke','bounded']:
    root=ROOT/folder
    search=pd.read_csv(root/'search.csv')
    best=max(search.to_dict('records'),key=fitness)
    np.testing.assert_allclose(json.loads(best['genome']),json.loads((root/'genome.json').read_text()),rtol=0,atol=0)
    for file in root.glob('*_daily.csv'):
        daily=pd.read_csv(file,parse_dates=['date']);trades=pd.read_csv(str(file).replace('_daily.csv','_trades.csv'),parse_dates=['date','signal_date'])
        cash=1.;shares={}
        for row in daily.itertuples(index=False):
            fills=trades[trades.date==row.date]
            for trade in fills.itertuples(index=False):
                assert trade.signal_date<trade.date
                assert abs(trade.fee-.001*abs(trade.notional))<1e-12
                if trade.action=='entry' and ('ga10' in file.name or 'rsi_setup' in file.name): assert trade.in_screen
                price=opens[(row.date,trade.ticker)]
                shares[trade.ticker]=shares.get(trade.ticker,0.)+trade.notional/price
                cash-=trade.notional+trade.fee
            close_nav=cash+sum(q*closes[(row.date,t)] for t,q in shares.items() if abs(q)>1e-10)
            open_nav=cash+sum(q*opens[(row.date,t)] for t,q in shares.items() if abs(q)>1e-10)
            np.testing.assert_allclose([close_nav,open_nav],[row.nav,row.open_nav],atol=2e-9,rtol=1e-9)
            assert cash>=-1e-8
        checked+=1
(ROOT/'verification.json').write_text(json.dumps({'saved_paths_reconciled':checked,'training_winners_match_exported_fitness':True,'ledger':'PASS; independent dollar fills, fees, cash, open and close marks'},indent=2))
print(f'PASS: independently reconciled {checked} saved portfolio paths and both training winners')
