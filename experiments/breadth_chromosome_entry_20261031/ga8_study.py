from pathlib import Path
import json
import numpy as np
import pandas as pd
from study import ROOT,load_features,sha

def reconstruct(fills,dividends=None):
 active={};closed=[]
 for f in fills:
  key=f['ticker'];q=f['quantity'];value=q*f['price'];cost=value*.0001;act=f['action']
  if key in active and dividends is not None:
   a=active[key];amount=dividends.loc[(dividends.index>a['last_date'])&(dividends.index<=f['date']),key].sum()*a['qty'];a['proceeds']+=amount;a['dividends']+=amount;a['last_date']=f['date']
  if act=='ENTRY':
   assert key not in active
   active[key]=dict(ticker=key,entry_date=f['date'],gene=f['gene'],last_date=f['date'],dividends=0.,qty=q,bought=value+cost,proceeds=0.,costs=cost)
  elif act=='ADD':
   a=active[key];a['qty']+=q;a['bought']+=value+cost;a['costs']+=cost
  elif act in ['REDUCE','EXIT','REPLACE']:
   a=active[key];a['qty']-=q;a['proceeds']+=value-cost;a['costs']+=cost
   assert a['qty']>=-1e-6
   if act in ['EXIT','REPLACE']:
    assert abs(a['qty'])<1e-6
    a['exit_date']=f['date'];a['pnl']=a['proceeds']-a['bought'];a['net_return']=a['pnl']/a['bought'];closed.append(a);del active[key]
  else:raise ValueError(act)
 return closed,active

def main():
 f,sectors=load_features();rows=[];meta=[]
 d=pd.read_parquet('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet',columns=['date','ticker','dividends']);d['date']=pd.to_datetime(d.date);dividends=d.pivot(index='date',columns='ticker',values='dividends').fillna(0)
 for year in [2023,2024,2025]:
  p=Path('/opt/mts/ga8/production_500_20261029')/f'fold_{year}.json';d=json.loads(p.read_text());closed,opened=reconstruct(d['result']['fills'],dividends)
  for x in closed:
   x.update(year=year,chromosome_id=d['model']['id'],family=d['model']['genes'][x['gene']]['family']);rows.append(x)
  meta.append(dict(year=year,chromosome_id=d['model']['id'],path=str(p),sha256=sha(p),closed=len(closed),open_excluded=len(opened),**d['result']['metrics']))
 pd.DataFrame(meta).to_csv(ROOT/'ga8_inventory.csv',index=False)
 t=pd.DataFrame(rows);t['entry_date']=pd.to_datetime(t.entry_date);t['exit_date']=pd.to_datetime(t.exit_date);t=t.join(f,on='entry_date');t['win']=t.pnl.gt(0);t.to_csv(ROOT/'ga8_trades.csv',index=False)
 parts=[]
 for dims in [['year','chromosome_id','regime'],['year','chromosome_id','timing'],['family','regime']]:
  z=t.groupby(dims).agg(n=('pnl','size'),entry_dates=('entry_date','nunique'),mean_net_return=('net_return','mean'),win_rate=('win','mean'),pnl=('pnl','sum'),spy21=('spy_forward21','mean'));parts.append(z.reset_index())
 pd.concat(parts).to_csv(ROOT/'ga8_results.csv',index=False)
 print(pd.concat(parts).to_string(index=False))
 from study import contrast,bh
 tests=[]
 t['r']=t.net_return
 for year,g in t.groupby('year'):
  for name,a,b in [('weak_vs_strong',g.regime.eq('weak'),g.regime.eq('strong')),('improving_vs_other_weak',g.timing.eq('weak_improving'),g.timing.eq('weak_not_improving')),('cross_0_5_vs_weak',g.timing.eq('crossed_0_5'),g.regime.eq('weak'))]:
   z=contrast(g,a,b)
   if z:tests.append(dict(year=year,test=name,**z))
 z=pd.DataFrame(tests);z['q_bh']=bh(z.p);z.to_csv(ROOT/'ga8_contrasts.csv',index=False)
if __name__=='__main__':main()
