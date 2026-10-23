"""Niche transition event study; research-only, no production mutation."""
import json,sys
from pathlib import Path
import numpy as np
import pandas as pd
R=Path('/opt/mts')
O=R/'ga6/runs/GA6_NICHE_TRANSITION_STUDY_20261021'
O.mkdir(exist_ok=True)
labels=pd.read_parquet(R/'ga5_redesign/dev79_niche_ga_v1/labels.parquet')
prices=pd.read_parquet(R/'ga5_redesign/exploratory79_ga4_enriched.parquet',columns=['date','ticker','open','close','adj_close','stock_splits'])
prices=prices[(prices.date>='2005-09-14')&(prices.date<'2026-09-15')]
prices=prices.sort_values(['ticker','date'])
labels=labels.sort_values(['ticker','date'])
df=prices.merge(labels[['date','ticker','research_niche']],on=['date','ticker'],how='left',validate='one_to_one')
g=df.groupby('ticker',sort=False)
df['prev_niche']=g.research_niche.shift(1)
df['next_niche']=g.research_niche.shift(-1)
df['onset']=df.research_niche.notna() & df.research_niche.ne(df.prev_niche) & df.prev_niche.notna()
df['persist']=df.research_niche.eq(df.prev_niche) & df.research_niche.notna()
df['exit']=df.research_niche.notna() & df.research_niche.ne(df.next_niche) & df.next_niche.notna()
df['episode']=df.groupby('ticker')['onset'].cumsum()
for h in (2,5,10,15,20):
    # Decision at close t; enter at next open, exit at close t+h; unadjusted prices,
    # skip intervals containing splits to avoid false raw-price jumps.
    nxt=g.open.shift(-1)
    end=g.close.shift(-h)
    split=df.stock_splits.fillna(0).ne(0)
    split_future=split.groupby(df.ticker).transform(lambda s:s.iloc[::-1].rolling(h,min_periods=h).max().iloc[::-1].shift(-1))
    df[f'r{h}']=(end/nxt-1).where((nxt>0)&(end>0)&(~split_future.fillna(True).astype(bool)))
# Event-time offsets measured relative to a retrospectively known onset.
onsets=df.index[df.onset].tolist()
records=[]
by_ticker={t:sub.index.to_numpy() for t,sub in df.groupby('ticker',sort=False)}
loc=np.zeros(len(df),dtype=int)
for ids in by_ticker.values():loc[ids]=np.arange(len(ids))
for idx in onsets:
    row=df.loc[idx]; ids=by_ticker[row.ticker]; pos=loc[idx]
    for off in (-10,-5,-2,-1,0,1,2,5,10):
        j=pos+off
        if j<0 or j>=len(ids):continue
        r=df.loc[ids[j]]
        rec={'ticker':row.ticker,'niche':row.research_niche,'onset_date':str(row.date)[:10],'offset':off,'entry_date':str(r.date)[:10],'entry_niche':r.research_niche,'episode':int(row.episode)}
        for h in (2,5,10,15,20):rec[f'r{h}']=r[f'r{h}']
        records.append(rec)
ev=pd.DataFrame(records)
ev.to_parquet(O/'event_returns.parquet',index=False)
summary=[]
for (n,off),sub in ev.groupby(['niche','offset']):
    rec={'niche':n,'offset':int(off),'onset_events':len(sub)}
    for h in (2,5,10,15,20):
        s=sub[f'r{h}'].dropna()
        rec.update({f'n{h}':len(s),f'mean{h}':float(s.mean()) if len(s) else None,f'median{h}':float(s.median()) if len(s) else None,f'win{h}':float((s>0).mean()) if len(s) else None,f'gt5_{h}':float((s>=.05).mean()) if len(s) else None,f'lt5_{h}':float((s<=-.05).mean()) if len(s) else None})
    summary.append(rec)
pd.DataFrame(summary).to_csv(O/'summary_by_niche_offset.csv',index=False)
meta={'onset_events':int(df.onset.sum()),'niches':13,'offsets':[-10,-5,-2,-1,0,1,2,5,10],'horizons':[2,5,10,15,20],'price_basis':'next-session raw open to horizon close; split-crossing observations excluded; dividends excluded','warnings':['Retrospective event alignment: negative offsets cannot know future onset at decision time','Niche labels are research labels; their point-in-time construction is NOT independently certified','Overlapping returns and ticker dependence; naive counts are not independent statistical samples','No portfolio capacity, fees, earnings embargo, or position-risk execution; not tradable backtest']}
(O/'manifest.json').write_text(json.dumps(meta,indent=2))
for off in (-5,-2,-1,0,1,2,5,10):
    s=ev[ev.offset==off]
    print('OFFSET',off,'events',len(s),'h5_mean',round(s.r5.mean()*100,3),'h5_win',round((s.r5.dropna()>0).mean()*100,2),'h10_mean',round(s.r10.mean()*100,3),'h10_win',round((s.r10.dropna()>0).mean()*100,2),flush=True)
print('SAVED',O,flush=True)
