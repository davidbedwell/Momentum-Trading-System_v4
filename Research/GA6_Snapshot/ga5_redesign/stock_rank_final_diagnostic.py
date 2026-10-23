import pandas as pd,numpy as np,json
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingRegressor
r=Path('/opt/mts/ga5_redesign');o=r/'stock_rank_final_diagnostic';o.mkdir(exist_ok=True)
p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet').sort_values(['ticker','date']).copy();p.date=pd.to_datetime(p.date)
# Purely stock-local features: avoid unverified historical cross-sectional percentiles.
fs=['ga4_return_5__v1','ga4_return_20__v1','ga4_return_63__v1','ga4_return_126__v1','ga4_return_252__v1','ga4_return_252_skip_20__v1','ga4_close_to_sma_20__v1','ga4_close_to_sma_50__v1','ga4_close_to_sma_200__v1','ga4_sma50_slope_10__v1','ga4_pullback_from_high_20__v1','ga4_range_position_252__v1','ga4_natr_20__v1','ga4_rsi_14__v1','ga4_relative_volume_20__v1','ga4_realized_vol_20__v1','ga4_volatility_ratio_20_63__v1']
# Forward adjusted close returns, then execute next-open via shifted adjusted open.
p['aopen']=p.open*p.adj_close/p.close
for h in (5,20,63):p[f'y{h}']=p.groupby('ticker').aopen.shift(-(h+1))/p.groupby('ticker').aopen.shift(-1)-1
p=p.replace([np.inf,-np.inf],np.nan);p=p.dropna(subset=fs+['aopen']);p=p[p.date.between('2006-01-01','2026-09-14')];p['year']=p.date.dt.year
results=[];trades=[]
# Rolling training ending at least horizon + 2 sessions before prediction year.
for h in (5,20,63):
 for year in range(2017,2027):
  start=pd.Timestamp(f'{year}-01-01');train=p[(p.date<start-pd.Timedelta(days=int(h*2.0+10)))&(p.date>=start-pd.Timedelta(days=365*10))].dropna(subset=[f'y{h}']);test=p[p.year==year].copy()
  if len(train)<1500 or len(test)<100:continue
  model=HistGradientBoostingRegressor(max_iter=85,max_leaf_nodes=9,l2_regularization=20,min_samples_leaf=90,learning_rate=.045,random_state=37)
  model.fit(train[fs].to_numpy(),train[f'y{h}'].clip(-.7,1.5).to_numpy());test['score']=model.predict(test[fs].to_numpy())
  test['rank']=test.groupby('date').score.rank(pct=True);test['actual']=test[f'y{h}'];test['bucket']=pd.cut(test['rank'],[0,.2,.8,1.0001],labels=['bottom','middle','top'],include_lowest=True)
  # Fixed nonoverlapping calendar dates every h market sessions; evaluate top 20% vs cross-sectional universe.
  dates=sorted(test.date.unique());anchors=set(dates[::h]);v=test[test.date.isin(anchors)].dropna(subset=['actual']);top=v[v['bucket']=='top'];bottom=v[v['bucket']=='bottom'];base=v
  results.append(dict(horizon=h,year=year,anchors=len(anchors),top_n=len(top),mean_top=float(top.actual.mean()),mean_universe=float(base.actual.mean()),mean_bottom=float(bottom.actual.mean()),top_edge=float(top.actual.mean()-base.actual.mean()),top_minus_bottom=float(top.actual.mean()-bottom.actual.mean()),top_net_20bps=float(top.actual.mean()-.002)))
  trades.append(v[['date','ticker','score','rank','bucket','actual']].assign(horizon=h,year=year))
  print('YEAR',h,year,'TOP_EDGE',round(results[-1]['top_edge'],5),flush=True)
a=pd.DataFrame(results);a.to_csv(o/'yearly_rank_results.csv',index=False);pd.concat(trades).to_csv(o/'nonoverlap_predictions.csv',index=False)
summary=[]
for h,g in a.groupby('horizon'):
 summary.append(dict(horizon=int(h),years=len(g),positive_years=int((g.top_edge>0).sum()),mean_yearly_top_edge=float(g.top_edge.mean()),median_yearly_top_edge=float(g.top_edge.median()),mean_top_net_20bps=float(g.top_net_20bps.mean()),mean_top_minus_bottom=float(g.top_minus_bottom.mean())))
report={'status':'WALK_FORWARD_STOCK_RANKING_DIAGNOSTIC','summary':summary,'features':fs,'limitations':['79-stock exploratory selection may be survivorship-biased and not NAS100 historical membership','Feature point-in-time provenance not independently audited','Nonoverlap dates per year, but cross-stock dependence remains','Top bucket 20% and horizons chosen before evaluation; repeated research exposure to later years','No portfolio, liquidity, earnings embargo or defensive gate','Adjusted next-open price approximation; costs only deducted from average return']};(o/'report.json').write_text(json.dumps(report,indent=2));print('FINAL',json.dumps(report,indent=2),flush=True)
