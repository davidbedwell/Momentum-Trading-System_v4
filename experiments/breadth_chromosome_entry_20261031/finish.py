import json
import numpy as np
import pandas as pd
from study import ROOT,contrast,bh,sha

def main():
 t=pd.read_csv(ROOT/'ga8_trades.csv',parse_dates=['entry_date','exit_date']);t['r']=t.net_return
 t['holding_sessions']=[len(pd.bdate_range(a,b))-1 for a,b in zip(t.entry_date,t.exit_date)]
 # Use actual observed market sessions, not business-day holiday approximation.
 raw=pd.read_parquet('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet');raw['date']=pd.to_datetime(raw.date);panel=raw.pivot(index='date',columns='ticker',values='adj_close').sort_index();dates=panel.index
 t['holding_sessions']=[dates.searchsorted(b)-dates.searchsorted(a) for a,b in zip(t.entry_date,t.exit_date)]
 risk=[]
 for x in t.itertuples():
  p=panel.loc[x.entry_date:x.exit_date,x.ticker].dropna().to_numpy();risk.append((min(p/p[0]-1),min(p/np.maximum.accumulate(p)-1)))
 t['close_mae_proxy']=[x[0] for x in risk];t['close_mdd_proxy']=[x[1] for x in risk]
 t.groupby(['year','regime']).agg(n=('r','size'),mean_mae_proxy=('close_mae_proxy','mean'),mean_mdd_proxy=('close_mdd_proxy','mean')).to_csv(ROOT/'ga8_risk_proxies.csv')
 t['hold_bin']=pd.cut(t.holding_sessions,[-1,5,20,40,10000],labels=False);t['momentum_bin']=t.m63.gt(0);t['vol_bin']=pd.cut(t.rv20,[0,.15,.25,np.inf],labels=False)
 tests=[];support=[]
 for year,u in t.groupby('year'):
  for name,a,b in [('weak_vs_strong',u.regime.eq('weak'),u.regime.eq('strong')),('improving_vs_other_weak',u.timing.eq('weak_improving'),u.timing.eq('weak_not_improving')),('cross_0_5_vs_weak',u.timing.eq('crossed_0_5'),u.regime.eq('weak'))]:
   v=u[a|b].copy();v['arm']=a[a|b].astype(int);keys=['chromosome_id','ticker','hold_bin','momentum_bin','vol_bin'];v=v[v.groupby(keys,observed=True).arm.transform('nunique')==2].copy()
   if len(v):v['weight']=1/v.groupby(keys+['arm'],observed=True).r.transform('size')
   support.append(dict(year=year,test=name,n=len(v)))
   z=contrast(v,v.arm.eq(1),v.arm.eq(0)) if len(v) else None
   if z:tests.append(dict(year=year,test=name,matched=True,**z))
 pd.DataFrame(support).to_csv(ROOT/'ga8_match_support.csv',index=False)
 z=pd.read_csv(ROOT/'ga8_contrasts.csv');z=z[z['matched'].eq(False)] if 'matched' in z else z;z['matched']=False;z=pd.concat([z,pd.DataFrame(tests)]);z['q_bh']=bh(z.p);z.to_csv(ROOT/'ga8_contrasts.csv',index=False)
 alltests=[]
 for name in ['contrasts','annual_contrasts','ga8_contrasts','native_ga6_contrasts']:
  z=pd.read_csv(ROOT/(name+'.csv'));z['test_family']=name;alltests.append(z)
 z=pd.concat(alltests);z['q_all_exploratory']=bh(z.p);z.to_csv(ROOT/'all_tests.csv',index=False)
 m=json.loads((ROOT/'run_metadata.json').read_text());m['final_code_hashes']={p.name:sha(p) for p in ROOT.glob('*.py')};m['tests_total']=len(z);(ROOT/'run_metadata.json').write_text(json.dumps(m,indent=2))
 print('tests',len(z))
if __name__=='__main__':main()
