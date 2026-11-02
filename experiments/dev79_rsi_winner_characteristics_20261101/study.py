import os,time,json,itertools,hashlib
os.environ.update({k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']})
import numpy as np
import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet')
H=ROOT.parent/'dev79_monthly_indicator_20261101/adjusted/discovery/rsi14_oversold/holdings.csv'
def wilson(a,n):
 if not n:return (np.nan,np.nan)
 z=1.95996398454;p=a/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;rad=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return mid-rad,mid+rad
def main():
 start=time.monotonic(); h=pd.read_csv(H,parse_dates=['execution_date']);h=h[h.execution_date.between('2009-01-01','2018-12-31')].copy()
 d=pd.read_parquet(SOURCE,filters=[('date','<',pd.Timestamp('2019-01-01'))]);d.date=pd.to_datetime(d.date)
 assert not d.duplicated(['date','ticker']).any()
 def wide(k):return d.pivot(index='date',columns='ticker',values=k).sort_index()
 c=wide('adj_close');raw=wide('close');factor=c/raw;o=wide('open')*factor;hi=wide('high')*factor;lo=wide('low')*factor;v=wide('volume');r=c.pct_change(fill_method=None)
 # Universe: every non-SMCI ticker in supplied DEV79 file, with available daily returns.
 ew=r.mean(axis=1);bench=(1+ew.fillna(0)).cumprod();f={}
 delta=c.diff();gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean();loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
 f['rsi14']=100-100/(1+gain/loss)
 for n in [5,10,21,63,126,252]:f[f'return_{n}']=c/c.shift(n)-1
 for n in [10,21,60]:f[f'vol_{n}']=r.rolling(n).std()*np.sqrt(252)
 for n in [20,50,100,200]:
  ma=c.rolling(n).mean();f[f'ma_distance_{n}']=c/ma-1;f[f'ma_slope_{n}_21']=ma/ma.shift(21)-1
 f['distance_high_252']=c/c.rolling(252).max()-1
 for a,b in [(5,20),(5,60),(20,60)]:f[f'volume_ratio_{a}_{b}']=v.rolling(a).mean()/v.rolling(b).mean()
 f['reversal_5_vs_prior21']=f['return_5']-(c.shift(5)/c.shift(26)-1)
 f['acceleration_21']=f['return_21']-(c.shift(21)/c.shift(42)-1)
 tr=np.maximum(hi-lo,np.maximum((hi-c.shift()).abs(),(lo-c.shift()).abs()));f['atr14_pct']=tr.rolling(14).mean()/c
 for n in [21,63]:
  f[f'positive_fraction_{n}']=(r.gt(0).astype(float).where(r.notna())).rolling(n).mean()
  f[f'drawdown_{n}']=c/c.rolling(n).max()-1
 for n in [21,63,126]:f[f'relative_strength_{n}']=f[f'return_{n}'].sub(bench/bench.shift(n)-1,axis=0)
 records=[];dates=c.index
 for row in h.itertuples():
  t=row.execution_date;j=dates.get_loc(t);prior=dates[j-1];nxt=(t.to_period('M')+1).to_timestamp();future=dates[(dates>=nxt)&(dates<nxt+pd.offsets.MonthBegin(1))]
  exitdate=future[0] if len(future) else pd.NaT
  rec=dict(execution_date=t,ticker=row.ticker,feature_date=prior,exit_date=exitdate,source_signal=row.signal,entry_open=o.at[t,row.ticker],exit_open=o.at[exitdate,row.ticker] if pd.notna(exitdate) else np.nan)
  rec.update({k:x.at[prior,row.ticker] for k,x in f.items()});records.append(rec)
 x=pd.DataFrame(records);x['return']=x.exit_open/x.entry_open-1;x['year']=x.execution_date.dt.year;x['winner']=np.nan;x['rank']=np.nan
 for t,g in x.groupby('execution_date'):
  valid=g[g['return'].notna()].sort_values(['return','ticker'],ascending=[False,True]);n=len(valid)
  if n:
   x.loc[valid.index,'rank']=np.arange(1,n+1);x.loc[valid.index,'winner']=0;x.loc[valid.index[:int(np.ceil(n/4))],'winner']=1
 # Thresholds fixed before outcome inspection; candidate-local median uses all selected candidates, even unlabeled.
 flags={};defs=[]
 for k in f:
  med=x.groupby('execution_date')[k].transform('median')
  flags[k+'__above_month_median']=x[k].gt(med).where(x[k].notna());defs.append((k+'__above_month_median',k,'> candidate monthly median'))
  if k.startswith('vol_') or k=='atr14_pct':
   flags[k+'__below_month_median']=x[k].lt(med).where(x[k].notna());defs.append((k+'__below_month_median',k,'< candidate monthly median'))
  threshold=.30 if k.startswith('vol_') else .03 if k=='atr14_pct' else -.10 if k.startswith('drawdown_') else 30 if k=='rsi14' else 1.2 if k.startswith('volume_ratio') else .5 if k.startswith('positive_fraction') else -.1 if k=='distance_high_252' else 0
  name=k+'__gt_'+str(threshold);flags[name]=x[k].gt(threshold).where(x[k].notna());defs.append((name,k,f'> {threshold}'))
 flags=pd.DataFrame(flags,index=x.index);pd.DataFrame(defs,columns=['characteristic','feature','rule']).to_csv(ROOT/'thresholds.csv',index=False)
 x.to_csv(ROOT/'stock_month_features.csv',index=False);pd.concat([x[['execution_date','ticker','winner']],flags],axis=1).to_csv(ROOT/'characteristic_flags.csv',index=False)
 usable=x.winner.notna();w=x.winner.eq(1);out=[]
 flag_known=flags.notna().to_numpy();flag_yes=flags.fillna(False).astype(bool).to_numpy();flag_pos={k:i for i,k in enumerate(flags)};winner_array=w.to_numpy();usable_array=usable.to_numpy()
 def summarize(mask,cols,label,scope,kind):
  ii=[flag_pos[k] for k in cols];known=flag_known[:,ii].all(axis=1)&np.asarray(mask)&usable_array;yes=flag_yes[:,ii].all(axis=1);nw=int((known&winner_array).sum());nn=int((known&~winner_array).sum());a=int((known&winner_array&yes).sum());b=int((known&~winner_array&yes).sum());pw=a/nw if nw else np.nan;pn=b/nn if nn else np.nan
  wl,wu=wilson(a,nw);nl,nu=wilson(b,nn)
  return dict(scope=scope,kind=kind,characteristic=label,winner_numerator=a,winner_denominator=nw,winner_prevalence=pw,winner_ci95_low=wl,winner_ci95_high=wu,nonwinner_numerator=b,nonwinner_denominator=nn,nonwinner_prevalence=pn,nonwinner_ci95_low=nl,nonwinner_ci95_high=nu,lift=pw/pn if pn else np.nan,difference=pw-pn)
 for scope,mask in [('pooled',usable)]+[(str(y),x.year.eq(y)) for y in range(2009,2019)]+[(str(t.date()),x.execution_date.eq(t)) for t in sorted(x.execution_date.unique())]:
  for k in flags:out.append(summarize(mask,[k],k,scope,'single'))
 singles=pd.DataFrame(out);singles['prevalence_rank']=singles.groupby('scope').winner_prevalence.rank(method='min',ascending=False);singles.to_csv(ROOT/'single_commonality.csv',index=False)
 # Exhaustive combinations of one fixed interpretable rule per family; no outcome-selected shortlist.
 base=[k for k in flags if '__gt_' in k and not k.startswith(('ma_slope_100','ma_slope_200'))]
 combos=[]
 for size in [2,3]:
  for cols in itertools.combinations(base,size):
   rec=summarize(usable,list(cols),' & '.join(cols),'pooled',f'{size}-way')
   if rec['winner_numerator']>=20 and rec['nonwinner_numerator']>=20:combos.append((cols,rec))
 co=pd.DataFrame([rec for cols,rec in combos]);co=co.sort_values('winner_prevalence',ascending=False);co.to_csv(ROOT/'cooccurrence_pooled.csv',index=False)
 # Year consistency for every retained combination.
 cy=[]
 for cols,rec in combos:
  for y in range(2009,2019):cy.append(summarize(x.year.eq(y),list(cols),rec['characteristic'],str(y),rec['kind']))
 pd.DataFrame(cy).to_csv(ROOT/'cooccurrence_yearly.csv',index=False)
 yearly=singles[singles.scope.isin([str(y) for y in range(2009,2019)])];cons=yearly.groupby('characteristic').agg(years_positive_difference=('difference',lambda a:int((a>0).sum())),years_evaluable=('difference','count'),min_year_difference=('difference','min'),max_year_difference=('difference','max'));cons.to_csv(ROOT/'year_consistency.csv')
 monthly=x.groupby('execution_date').agg(selected=('ticker','size'),labeled=('return','count'),winners=('winner','sum'),mean_return=('return','mean'));monthly.to_csv(ROOT/'monthly_summary.csv')
 audit=dict(rows=len(x),months=len(monthly),labeled=int(usable.sum()),winners=int(w.sum()),tickers=len(c.columns),date_min=str(d.date.min()),date_max=str(d.date.max()),features=len(f),characteristics=len(flags.columns),pairs_triples_retained=len(co),source_signal_max_abs_rsi_error=float((x.source_signal+x.rsi14).abs().max()),missing_features={k:int(x[k].isna().sum()) for k in f},cpu_affinity=list(os.sched_getaffinity(0)),seconds=time.monotonic()-start,holdings_sha256=hashlib.sha256(H.read_bytes()).hexdigest())
 assert len(monthly)==120 and x.feature_date.lt(x.execution_date).all() and d.date.max()<pd.Timestamp('2019-01-01')
 assert x[usable].groupby('execution_date').winner.sum().eq(np.ceil(x[usable].groupby('execution_date').size()/4)).all()
 (ROOT/'audit.json').write_text(json.dumps(audit,indent=2))
 def table(df,n=12):
  lines=['|Characteristic|Winners n/N (%)|Nonwinners n/N (%)|Lift|','|---|---:|---:|---:|']
  for z in df.head(n).itertuples():lines.append(f'|{z.characteristic}|{z.winner_numerator}/{z.winner_denominator} ({100*z.winner_prevalence:.1f}%)|{z.nonwinner_numerator}/{z.nonwinner_denominator} ({100*z.nonwinner_prevalence:.1f}%)|{z.lift:.2f}|')
  return '\n'.join(lines)
 pooled=singles[singles.scope.eq('pooled')].sort_values(['winner_prevalence','characteristic'],ascending=[False,True])
 report=f'''# DEV79 RSI winner characteristics, 2009–2018

Executed historical descriptive study: {len(x)} selected stock-months, {usable.sum()} labeled, {w.sum()} winners across 119 outcome months. {len(f)} continuous features and {len(flags.columns)} threshold characteristics. No production changes, optimization, GA, or 2019+ observations.

## Method and boundary

Holdings are taken verbatim from `{H.relative_to(ROOT.parent.parent)}`. Daily file: `{SOURCE}`. Features use the immediately preceding global trading session, with no forward fill. Adjusted OHLC = raw OHLC × adj_close/close, matching the source experiment; volume is vendor volume without split adjustment. Vendor historical adjustment factors are not independently point-in-time certified. Source split audit favors already split-adjusted prices, but is a heuristic. RSI uses Wilder-style EWM alpha 1/14, matching source initialization; maximum source signal discrepancy = {audit['source_signal_max_abs_rsi_error']:.8g}.

Outcome is adjusted next calendar-month first observed session open / entry open − 1, no fees. Rank descending return with ticker ascending for exact ties; winners are exactly ceil(n/4) among observed outcomes each month (thus potentially above 25%). Missing outcomes are excluded from labels, never imputed. December 2018 is censored because its next open is in 2019; features and selected candidates remain exported. No 2019+ rows are loaded. Warmup uses available pre-2009 data.

All medians are contemporaneous within the selected RSI candidate month, without outcome information; strict inequalities exclude equal-to-threshold values. Fixed thresholds and definitions are in thresholds.csv. Returns use trading-session lags; volatility is sample daily standard deviation annualized sqrt(252); slopes are MA/MA 21 sessions earlier−1; drawdown is close/trailing maximum−1; ATR is simple 14-session mean true range / close. Reversal compares last 5-session return with preceding 21-session return (unequal horizons); acceleration compares consecutive 21-session returns. Relative strength subtracts compounded daily equal-weight available-return DEV79 universe performance; universe has {len(c.columns)} tickers and reflects the supplied fixed historical universe, with survivorship/availability bias. Ratios of rolling vendor volume may be split-sensitive.

## Source coverage discrepancy

The requested DEV79 label does not imply 79 observed price series here: the supplied file contains {len(c.columns)} tickers before 2019. Selected holdings range from {int(monthly.selected.min())} to {int(monthly.selected.max())} per month. The study preserves the supplied holdings rather than rebuilding a different universe or selection. Missing feature counts are disclosed in audit.json.

## Pooled prevalence ranking

{table(pooled)}

## Year-by-year consistency

Positive winner-minus-nonwinner prevalence years among the leading pooled characteristics (out of evaluable years):

{chr(10).join('- '+str(k)+': '+str(int(cons.loc[k, 'years_positive_difference']))+'/'+str(int(cons.loc[k, 'years_evaluable'])) for k in pooled.characteristic.head(12))}

## Co-occurring characteristics

Exhaustive pairs/triples of the fixed-rule family (excluding two redundant long-MA slopes), requiring at least 20 matching winners AND 20 matching nonwinners. Ranked by winner prevalence, not conditional win rate. All retained combinations are exported with yearly comparisons.

{table(co)}

## Uncertainty and interpretation

CSV tables include numerator/denominator, winner and nonwinner prevalence, lift, prevalence difference, and marginal 95% Wilson intervals. These intervals assume independent stock-months and can understate uncertainty because months, tickers and characteristics are dependent; they are not simultaneous or cluster-adjusted. All comparisons and rankings are EXPLORATORY, with no significance claims or multiplicity-adjusted discovery claims. No predictive edge is validated. Many high-prevalence features are equally prevalent among nonwinners. Full year consistency reports positive-difference years out of evaluable years, plus the annual range; missing values use characteristic-specific denominators. Combinations are dependent and their sample-size filter is descriptive.

## Monthly iteration and verification

single_commonality.csv contains the full characteristic ranking separately for every one of the 120 months, every year, and pooled; monthly_summary.csv lists every month, including censored December 2018. stock_month_features.csv contains ranks, labels, return endpoints and every feature. characteristic_flags.csv permits reproduction of every comparison. cooccurrence_pooled.csv and cooccurrence_yearly.csv contain full retained pair/triple tables. year_consistency.csv summarizes annual single-feature consistency. audit.json records missingness, coverage and execution bounds. Assertions verify 120 months, pre-entry dates, rank counts, and no 2019+ data. Run with run.sh; validation uses verify.py.
'''
 (ROOT/'REPORT.md').write_text(report);print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
