import pandas as pd,numpy as np,json,hashlib
from pathlib import Path
p=Path('/opt/mts/ga6_h/audits');d=pd.read_csv(p/'GA6v3_four_way_transport_rankings.csv');coh=['DEV79','DEV87','DEV50b']
# Three disjoint stock cohorts for transport; combined portfolio is diagnostic only.
for m in ['net_ev','ev_lcb','cagr','mdd','trades','win_rate']:
 a=d[[c+'__'+m for c in coh]]
 d['independent_min_'+m]=a.min(axis=1,skipna=False)
 d['independent_median_'+m]=a.median(axis=1,skipna=False)
d['independent_max_abs_mdd']=d[[c+'__mdd' for c in coh]].abs().max(axis=1)
d['cagr_range']=d[[c+'__cagr' for c in coh]].max(axis=1)-d[[c+'__cagr' for c in coh]].min(axis=1)
d['min_trades']=d[[c+'__trades' for c in coh]].min(axis=1)
d['transport_eligible']=np.logical_and.reduce([(d[c+'__trades']>0)&(d[c+'__ev_lcb']>0) for c in coh])
# Full trade-entry and exit fingerprint across disjoint cohorts, insensitive to JSON object key order.
fingerprints={}
for c in coh:
 t=pd.read_csv(p/f'GA6v3_400_{c}_trade_ledger_2019_2024.csv',usecols=['identity','trade_ledger'])
 for ident,ledger in zip(t.identity,t.trade_ledger):
  rows=json.loads(ledger); key=tuple(sorted((str(r.get('symbol')),str(r.get('entry_date')),str(r.get('exit_date'))) for r in rows))
  fingerprints.setdefault(ident,[]).append(key)
d['trade_signature']=[hashlib.sha256(repr(fingerprints[i]).encode()).hexdigest() for i in d.identity]
d['duplicate_group_size']=d.groupby('trade_signature').trade_signature.transform('size')
d['duplicate_representative']=~d.duplicated('trade_signature')
# Pareto maximize conservative profit, growth, activity; minimize drawdown and degradation.
objectives=['independent_min_net_ev','independent_min_ev_lcb','independent_min_cagr','min_trades','independent_max_abs_mdd','cagr_range'];sign=np.array([1,1,1,1,-1,-1]);valid=d[d.transport_eligible & d.duplicate_representative].copy();v=valid[objectives].to_numpy(dtype=float)*sign;assert np.isfinite(v).all()
front=np.zeros(len(v),dtype=int);remaining=np.arange(len(v));level=1
while len(remaining):
 x=v[remaining];dom=np.zeros(len(x),dtype=bool)
 for j in range(len(x)):
  dom[j]=np.any(np.all(x>=x[j],axis=1)&np.any(x>x[j],axis=1))
 chosen=remaining[~dom];front[chosen]=level;remaining=remaining[dom];level+=1
valid['pareto_front']=front
d=d.merge(valid[['identity','pareto_front']],on='identity',how='left')
d=d.sort_values(['pareto_front','independent_min_ev_lcb','independent_min_cagr'],ascending=[True,False,False],na_position='last')
d.to_csv(p/'GA6v3_global_chromosome_pareto_leaderboard.csv',index=False)
valid.sort_values(['pareto_front','independent_min_ev_lcb'],ascending=[True,False]).to_csv(p/'GA6v3_global_pareto_eligible_unique.csv',index=False)
print('total',len(d),'eligible',int(d.transport_eligible.sum()),'unique signatures',d.trade_signature.nunique(),'eligible unique',len(valid),'front1',int((valid.pareto_front==1).sum()))
print('top first-front by conservative LCB:')
print(valid[valid.pareto_front==1].sort_values('independent_min_ev_lcb',ascending=False)[['index','niche','independent_min_ev_lcb','independent_min_net_ev','independent_min_cagr','independent_max_abs_mdd','cagr_range','min_trades','duplicate_group_size']].head(15).to_string(index=False,float_format=lambda x:f'{x:.4f}'))
print('front counts',valid.pareto_front.value_counts().sort_index().head(10).to_dict())
