"""Frozen 53 DEV87 survivor trade-level hypothesis study, no GA6 evaluator edits.
Purged chronological folds and clustered uncertainty; no claims of independent validation.
"""
import json,pathlib
import numpy as np,pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score,average_precision_score
P=pathlib.Path('/opt/mts/ga6/runs/post_v3_comparison_20261022');D=pathlib.Path('/opt/mts/thunder-migration/mts-certification-20261011/dev87')
t=pd.read_csv(P/'dev87_entry_extension_volatility_trade_classification.csv');t['entry_date']=pd.to_datetime(t.entry_date);t['exit_date']=pd.to_datetime(t.exit_date)
f=pd.read_parquet(D/'dev87_ga6_enriched.parquet');f['date']=pd.to_datetime(f.date);f=f.sort_values(['ticker','date']);f['next_date']=f.groupby('ticker').date.shift(-1)
features=['ga4_return_20__v1','ga4_return_63__v1','ga4_return_126__v1','ga4_return_252__v1','ga4_close_to_sma_50__v1','ga4_close_to_sma_200__v1','ga4_natr_14__v1','ga4_natr_20__v1','ga4_realized_vol_20__v1','ga4_realized_vol_63__v1','ga4_range_position_20__v1','ga4_range_position_50__v1','ga4_range_position_252__v1','ga4_sector_vs_universe_return_63__v1','ga4_relative_strength_change_20__v1','ga4_volatility_ratio_20_63__v1','ga4_sma200_slope_20__v1','ga4_breadth_above_sma_200__v1','trend','breadth','relative_strength']
assert set(features).issubset(f.columns)
d=t.drop(columns=['ga4_return_126__v1','ga4_close_to_sma_200__v1','ga4_natr_14__v1']).merge(f[['ticker','next_date',*features]],left_on=['ticker','entry_date'],right_on=['ticker','next_date'],how='left',validate='many_to_one');assert len(d)==8218
# Remove direct future information: all features are from prior trading session.
d['extension']=d.ga4_return_126__v1.ge(.30)&d.ga4_close_to_sma_200__v1.ge(.10)&d.ga4_natr_14__v1.ge(.04)
d['win']=d.trade_return>0;d['severe_loss']=d.trade_return<=-.10
# Strict chronology: 2025 first half -> 2025 second half -> 2026; purge 40 sessions at each fold boundary.
folds=[('2025H2','2025-01-01','2025-06-30','2025-09-01','2025-12-31'),('2026H1','2025-01-01','2025-12-31','2026-03-02','2026-06-30'),('2026Q3','2025-01-01','2026-06-30','2026-08-17','2026-09-14')]
results=[];pred=[]
for label,train_start,train_end,test_start,test_end in folds:
 train=d.extension&d.entry_date.between(train_start,train_end)&(d.exit_date<pd.Timestamp(test_start))
 test=d.extension&d.entry_date.between(test_start,test_end)
 a=d[train];b=d[test]
 if len(a)<100 or len(b)<25:continue
 for target in ['win','severe_loss']:
  model=make_pipeline(SimpleImputer(strategy='median',add_indicator=False),StandardScaler(),LogisticRegression(max_iter=1000,C=0.25))
  model.fit(a[features],a[target].astype(int));p=model.predict_proba(b[features])[:,1];y=b[target].astype(int)
  results.append({'fold':label,'target':target,'train_n':len(a),'test_n':len(b),'positive_pct':100*y.mean(),'roc_auc':float(roc_auc_score(y,p)) if y.nunique()>1 else None,'average_precision':float(average_precision_score(y,p))})
  for idx,score in zip(b.index,p):pred.append({'fold':label,'target':target,'chromosome':d.loc[idx,'chromosome'],'ticker':d.loc[idx,'ticker'],'entry_date':str(d.loc[idx,'entry_date'].date()),'exit_date':str(d.loc[idx,'exit_date'].date()),'actual':int(d.loc[idx,target]),'predicted_probability':float(score),'trade_return':float(d.loc[idx,'trade_return'])})
pred=pd.DataFrame(pred);pred.to_csv(P/'dev87_extended_entry_walkforward_predictions.csv',index=False)
# The two key questions: can a model separate winners, and can it identify high-loss tails?
report={'status':'EXPLORATORY_NOT_CERTIFIED','folds':results,'feature_names':features,'n_extended_volatile':int(d.extension.sum()),'limitations':['All folds use DEV87, which was previously used to select 53 chromosomes; chronological split cannot remove that selection bias','Overlapping trades across chromosomes make events dependent','Only completed trades; open positions censored','Chronological training/test split uses purge of at least 40 sessions between latest training entry and earliest test entry; training positions additionally must have exited','Model predictions are not a tested executable trading strategy','This study does not change position sizing or simulate portfolio NAV']}
# Threshold-free feature diagnostics, compare winner and loser distributions within extension group.
e=d[d.extension].copy();diag=[]
for feature in features:
 w=e.loc[e.win,feature].dropna();l=e.loc[~e.win,feature].dropna()
 if len(w)<100 or len(l)<100:continue
 pooled=np.sqrt((w.var()+l.var())/2)
 diag.append({'feature':feature,'winner_median':float(w.median()),'loser_median':float(l.median()),'standardized_mean_diff':float((w.mean()-l.mean())/pooled) if pooled>0 else 0,'n_win':len(w),'n_loss':len(l)})
report['feature_differences_winner_vs_loser']=sorted(diag,key=lambda x:abs(x['standardized_mean_diff']),reverse=True)
# Simple size reduction scenarios: exposure-weighted mean return and downside proxy, not portfolio CAGR/MDD.
scenarios=[]
for reduction in [0.25,0.50,0.75,1.0]:
 weights=np.where(d.extension,1-reduction,1.0)
 scenarios.append({'position_reduction_fraction':reduction,'exposure_weighted_mean_trade_return_pct':float(100*np.average(d.trade_return,weights=weights)),'exposure_weighted_severe_loss_fraction_pct':float(100*np.average(d.severe_loss,weights=weights)),'relative_gross_exposure':float(weights.sum()/len(weights)),'estimated_mean_trade_pnl_per_original_position_pct':float(100*np.mean(weights*d.trade_return)),'not_portfolio_simulation':True})
report['sizing_proxies']=scenarios
(P/'dev87_extended_entry_discrimination_study.json').write_text(json.dumps(report,indent=2));print(json.dumps({'folds':results,'top_feature_differences':report['feature_differences_winner_vs_loser'][:10],'sizing_proxies':scenarios},indent=2))
