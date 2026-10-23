"""Non-mutating GA6-H derived daily bars, forward outcomes, and row-level quality flags."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path('/opt/mts/ga6_h')
AUDIT=pd.read_parquet(ROOT/'audits/price_coverage.parquet')
OUT=ROOT/'derived_v1'
OUT.mkdir(exist_ok=True)
summary={'files':0,'rows':0,'eligible_signal_rows':0,'invalid_price_rows':0,'invalid_ohlc_rows':0,'zero_volume_rows':0,'short_history_symbols':0}
for rec in AUDIT.itertuples(index=False):
    d=pd.read_parquet(ROOT/'data/prices'/f'{rec.symbol}.parquet').sort_values('date').reset_index(drop=True)
    for c in ('Open','High','Low','Close','Adj Close','Volume'): d[c]=pd.to_numeric(d[c],errors='coerce')
    px=d[['Open','High','Low','Close']]
    valid=(px.gt(0).all(axis=1)&np.isfinite(px).all(axis=1)&d['Volume'].ge(0)&np.isfinite(d['Volume']))
    consistent=(d['High']>=d[['Open','Low','Close']].max(axis=1))&(d['Low']<=d[['Open','High','Close']].min(axis=1))
    d['valid_bar']=valid&consistent
    d['tradable_bar']=d.valid_bar&d.Volume.gt(0)
    d['history_sessions']=np.arange(len(d))+1
    d['eligible_signal']=d.tradable_bar&d.history_sessions.ge(60)
    # Strictly causal: features use close and earlier. Next-open fills are separate.
    close=d['Adj Close'].where(d['Adj Close'].gt(0))
    for n in (5,10,20,40,60,120,252):
        d[f'return_{n}']=close/close.shift(n)-1
    for n in (10,20,40,60):
        d[f'volatility_{n}']=close.pct_change(fill_method=None).rolling(n,min_periods=n).std()
        d[f'volume_ratio_{n}']=d.Volume/d.Volume.rolling(n,min_periods=n).mean().replace(0,np.nan)
    for n in (1,5,10,20,40):
        d[f'forward_adj_return_{n}']=close.shift(-n)/close-1
    keep=['date','symbol','Open','High','Low','Close','Adj Close','Volume','Dividends','Stock Splits','valid_bar','tradable_bar','eligible_signal','history_sessions']+[c for c in d if c.startswith(('return_','volatility_','volume_ratio_','forward_adj_return_'))]
    d[keep].to_parquet(OUT/f'{rec.symbol}.parquet',index=False)
    summary['files']+=1;summary['rows']+=len(d)
    summary['eligible_signal_rows']+=int(d.eligible_signal.sum())
    summary['invalid_price_rows']+=int((~valid).sum())
    summary['invalid_ohlc_rows']+=int((~consistent).sum())
    summary['zero_volume_rows']+=int(d.Volume.eq(0).sum())
    summary['short_history_symbols']+=int(len(d)<252)
(ROOT/'audits/research_layer_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2),flush=True)
