"""Risk proxies, annual contrasts and corrected matched/HAC estimates."""
import numpy as np
import pandas as pd
from study import ROOT,analyze,contrast,bh

def main():
 t=pd.read_csv(ROOT/'trades.csv.gz',parse_dates=['entry_date','exit_date','feature_date'])
 analyze(t)
 # Close-based stock path proxies, not actual fill MAE or portfolio MDD.
 d=pd.read_parquet('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet',columns=['date','ticker','adj_close']);d['date']=pd.to_datetime(d.date)
 panel=d.pivot(index='date',columns='ticker',values='adj_close').sort_index()
 unique=t[['ticker','entry_date','exit_date']].drop_duplicates();risk=[]
 for r in unique.itertuples():
  x=panel.loc[r.entry_date:r.exit_date,r.ticker].dropna().to_numpy()
  risk.append((min(x/x[0]-1),min(x/np.maximum.accumulate(x)-1)) if len(x) else (np.nan,np.nan))
 unique['close_mae_proxy']=[x[0] for x in risk];unique['close_mdd_proxy']=[x[1] for x in risk]
 u=t.merge(unique,on=['ticker','entry_date','exit_date'],validate='many_to_one')
 u[u.identity_sample].groupby(['system','year','regime']).agg(n=('r','size'),mean_mae_proxy=('close_mae_proxy','mean'),mean_mdd_proxy=('close_mdd_proxy','mean')).to_csv(ROOT/'risk_proxies.csv')
 rows=[]
 for keys,g in t[t.identity_sample].groupby(['system','year']):
  z=contrast(g,g.regime.eq('weak'),g.regime.eq('strong'))
  if z:rows.append(dict(system=keys[0],year=keys[1],**z))
 z=pd.DataFrame(rows);z['q_bh']=bh(z.p);z.to_csv(ROOT/'annual_contrasts.csv',index=False)
 # Number of identities with both regimes and direction, without treating them as independent.
 rows=[]
 for keys,g in t[t.identity_sample].groupby(['system','chromosome_id']):
  a=g[g.regime.eq('weak')];b=g[g.regime.eq('strong')]
  rows.append(dict(system=keys[0],chromosome_id=keys[1],n_weak=len(a),n_strong=len(b),delta_r=a.r.mean()-b.r.mean()))
 pd.DataFrame(rows).to_csv(ROOT/'chromosome_contrasts.csv',index=False)
 print('refined',len(t),len(unique))
if __name__=='__main__':main()
