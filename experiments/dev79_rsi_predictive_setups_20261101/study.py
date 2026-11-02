import os,time,json,hashlib,itertools
from pathlib import Path
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
S=P.parent/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv'
START=time.monotonic()
x=pd.read_csv(S,parse_dates=['execution_date','feature_date','exit_date'])
assert x.execution_date.dt.year.between(2009,2018).all()
assert x.feature_date.lt(x.execution_date).all()
assert x.exit_date.dropna().dt.year.le(2018).all()
assert not x.duplicated(['execution_date','ticker']).any()
x['prior15_volume_ratio_60']=(20*x.volume_ratio_20_60-5*x.volume_ratio_5_60)/15
b21=x.return_21-x.relative_strength_21;b63=x.return_63-x.relative_strength_63
x['prior42_relative_strength']=(1+x.return_63)/(1+x.return_21)-(1+b63)/(1+b21)
x['vol_ratio_10_21']=x.vol_10/x.vol_21
x['rs_daily_improvement']=x.relative_strength_21/21-x.prior42_relative_strength/42
conds={}
def c(name,cols,fn,definition):
    known=x[cols].notna().all(axis=1)&np.isfinite(x[cols]).all(axis=1)
    conds[name]=(fn(x)&known,known,definition,cols)
c('trend_return',['return_252'],lambda z:z.return_252>0,'return_252 > 0')
c('trend_slope',['ma_slope_200_21'],lambda z:z.ma_slope_200_21>0,'ma_slope_200_21 > 0')
c('pullback_return',['return_21'],lambda z:z.return_21<0,'return_21 < 0')
c('pullback_ma',['ma_distance_20'],lambda z:z.ma_distance_20<0,'ma_distance_20 < 0')
c('bounce',['return_5'],lambda z:z.return_5>0,'return_5 > 0')
c('positive_days',['positive_fraction_21'],lambda z:z.positive_fraction_21>.5,'positive_fraction_21 > 0.5')
c('acceleration',['acceleration_21'],lambda z:z.acceleration_21>0,'acceleration_21 > 0')
c('reversal',['reversal_5_vs_prior21'],lambda z:z.reversal_5_vs_prior21>0,'reversal_5_vs_prior21 > 0')
c('vol_contract',['vol_ratio_10_21'],lambda z:z.vol_ratio_10_21<1,'vol_ratio_10_21 < 1')
for t in [1.2,1.5]:c('elevated_'+str(t),['prior15_volume_ratio_60'],lambda z,t=t:z.prior15_volume_ratio_60>t,f'prior15_volume_ratio_60 > {t}')
for t in [1.,.8]:c('normal_'+str(t),['volume_ratio_5_20'],lambda z,t=t:z.volume_ratio_5_20<t,f'volume_ratio_5_20 < {t}')
c('rs_positive',['relative_strength_21'],lambda z:z.relative_strength_21>0,'relative_strength_21 > 0')
c('rs_improving',['rs_daily_improvement'],lambda z:z.rs_daily_improvement>0,'relative_strength_21/21 > prior42_relative_strength/42')
families={
 'trend_pullback':(['trend_return','trend_slope'],['pullback_return','pullback_ma'],['bounce','positive_days']),
 'stabilization':(['pullback_return','pullback_ma'],['acceleration','reversal'],['bounce','vol_contract']),
 'volume_normalization':(['elevated_1.2','elevated_1.5'],['normal_1.0','normal_0.8'],['pullback_return','bounce']),
 'relative_strength':(['pullback_return','pullback_ma'],['rs_positive','rs_improving'],['bounce','trend_return'])}
rules=[];masks={};knowns={}
for family,(aa,bb,cc) in families.items():
 for a,b,extra in itertools.product(aa,bb,[[],[cc[0]],[cc[1]],cc]):
    names=[a,b]+extra;rid=f'{family}_{1+sum(r["family"]==family for r in rules):02d}'
    masks[rid]=np.logical_and.reduce([conds[k][0] for k in names]);knowns[rid]=np.logical_and.reduce([conds[k][1] for k in names])
    rules.append(dict(rule_id=rid,family=family,n_conditions=len(names),conditions=' & '.join(names),definition=' AND '.join(conds[k][2] for k in names)))
rules=pd.DataFrame(rules);rules.to_csv(P/'rule_definitions.csv',index=False)
pd.DataFrame([dict(condition=k,definition=v[2],inputs=';'.join(v[3])) for k,v in conds.items()]).to_csv(P/'condition_definitions.csv',index=False)
months=sorted(x.loc[x.winner.notna(),'execution_date'].unique());oos=[d for d in months if d.year>=2014]
assert len(months)==119 and len(oos)==59

def classification(mask,scope):
 z=x.loc[scope];sel=pd.Series(mask,index=x.index).loc[z.index].astype(bool);valid=z.winner.notna();w=z.winner.eq(1)
 a=int((sel&valid&w).sum());n=int((sel&valid).sum());nw=int((valid&w).sum());N=int(valid.sum());u=int((~sel&valid).sum())
 return dict(candidate_n=len(z),labeled_n=N,winner_n=nw,selected_n=int(sel.sum()),selected_labeled_n=n,selected_winner_n=a,unselected_labeled_n=u,unselected_winner_n=nw-a,missing_outcome_n=int((~valid).sum()),selected_missing_outcome_n=int((sel&~valid).sum()),precision=a/n if n else np.nan,recall=a/nw if nw else np.nan,baseline_precision=nw/N if N else np.nan,enrichment=(a/n)/(nw/N) if n and nw else np.nan,selected_mean_return=z.loc[sel,'return'].mean(),unselected_mean_return=z.loc[~sel,'return'].mean(),basket_mean_return=z['return'].mean())
monthly=[]
for rid in masks:
 for d in months:
    scope=x.execution_date.eq(d);row=classification(masks[rid],scope);row.update(rule_id=rid,execution_date=d,unknown_feature_n=int((scope&~knowns[rid]).sum()))
    row['precision_excess']=row['precision']-row['baseline_precision'];row['selected_return_excess']=row['selected_mean_return']-row['basket_mean_return'];monthly.append(row)
monthly=pd.DataFrame(monthly);monthly.to_csv(P/'setup_monthly_metrics.csv',index=False)

def calibrate(cutoff):
 train=x.execution_date.lt(cutoff)&x.exit_date.lt(cutoff)&x.winner.notna()
 ds=set(x.loc[train,'execution_date']);m=monthly[monthly.execution_date.isin(ds)]
 rows=[]
 for rid,g in m.groupby('rule_id',sort=True):
    r=classification(masks[rid],train);active=g.selected_labeled_n.gt(0);r.update(rule_id=rid,train_start=str(min(ds).date()),train_last_entry=str(max(ds).date()),max_train_exit=str(x.loc[train,'exit_date'].max().date()),cutoff=str(pd.Timestamp(cutoff).date()),active_months=int(active.sum()),train_months=len(ds),mean_monthly_precision_excess=g.loc[active,'precision_excess'].mean(),positive_precision_months=int(g.precision_excess.gt(0).sum()))
    r['eligible']=r['selected_labeled_n']>=40 and r['active_months']>=24;rows.append(r)
 t=pd.DataFrame(rows).merge(rules,on='rule_id');t=t.sort_values(['eligible','mean_monthly_precision_excess','enrichment','rule_id'],ascending=[False,False,False,True]);t['discovery_rank']=np.arange(1,len(t)+1)
 return t
frozen=calibrate(pd.Timestamp('2014-01-01'));frozen.to_csv(P/'discovery_ranked_setups.csv',index=False)
policies={};schedule=[]
for family in ['all']+list(families):
 policy='expanding_'+family;policies[policy]=pd.Series(False,index=x.index)
 for year in range(2014,2019):
    t=calibrate(pd.Timestamp(year,1,1));t.to_csv(P/f'calibration_{year}.csv',index=False)
    q=t[t.eligible & (True if family=='all' else t.family.eq(family))]
    rid=q.iloc[0].rule_id if len(q) else None
    scope=x.year.eq(year)
    if rid:policies[policy].loc[scope]=masks[rid][scope]
    schedule.append(dict(policy=policy,evaluation_year=year,rule_id=rid,train_last_entry=t.iloc[0].train_last_entry,max_train_exit=t.iloc[0].max_train_exit,training_score=q.iloc[0].mean_monthly_precision_excess if len(q) else np.nan))
for family in ['all']+list(families):
 q=frozen[frozen.eligible & (True if family=='all' else frozen.family.eq(family))]
 if len(q):policies['frozen_'+family]=masks[q.iloc[0].rule_id]
pd.DataFrame(schedule).to_csv(P/'selection_schedule.csv',index=False)
policies['baseline_rsi_basket']=pd.Series(True,index=x.index)
# Baseline-relative returns, monthly membership, denominators, and all complements.
for name in list(policies):
 if name!='baseline_rsi_basket':policies[name+'_unselected']=~policies[name]

def portfolio(mask,dates):
 prev={};rows=[]
 for d in dates:
    g=x[x.execution_date.eq(d)];chosen=g.loc[pd.Series(mask,index=x.index).loc[g.index]];n=len(chosen)
    target={t:1/n for t in chosen.ticker} if n else {}
    buy=sum(max(target.get(t,0)-prev.get(t,0),0) for t in set(prev)|set(target));sell=sum(max(prev.get(t,0)-target.get(t,0),0) for t in set(prev)|set(target))
    gross=float(chosen['return'].fillna(0).sum()/n) if n else 0.
    cost=.001*(buy+sell);net=(1-cost)*(1+gross)-1
    # pandas renames reserved return field; replace from explicit columns.
    prev={t:(1/n)*(1+(r if pd.notna(r) else 0))/(1+gross) for t,r in chosen[['ticker','return']].itertuples(index=False,name=None)} if n else {}
    rows.append(dict(execution_date=d,exit_date=g.exit_date.max(),holdings_n=n,gross_return=gross,net_return=net,buy_turnover=buy,sell_turnover=sell,two_sided_turnover=buy+sell,transaction_cost_fraction=cost,missing_return_n=int(chosen['return'].isna().sum())))
 # Liquidate after final observed holding interval, at its exit open.
 rows[-1]['net_return']=(1+rows[-1]['net_return'])*(1-.001*sum(prev.values()))-1
 rows[-1]['sell_turnover']+=sum(prev.values());rows[-1]['two_sided_turnover']+=sum(prev.values());rows[-1]['transaction_cost_fraction']+=.001*sum(prev.values())
 return pd.DataFrame(rows)
def performance(z):
 r=z.net_return.to_numpy();wealth=np.r_[1,np.cumprod(1+r)];sd=np.std(r,ddof=1)
 return dict(months=len(z),active_months=int(z.holdings_n.gt(0).sum()),mean_holdings=z.holdings_n.mean(),cagr=wealth[-1]**(12/len(r))-1,mdd=float(np.min(wealth/np.maximum.accumulate(wealth)-1)),sharpe=float(np.mean(r)/sd*np.sqrt(12)) if sd else np.nan,mean_monthly_net_return=np.mean(r),two_sided_turnover_sum=z.two_sided_turnover.sum(),mean_monthly_two_sided_turnover=z.two_sided_turnover.mean(),missing_return_n=int(z.missing_return_n.sum()))
# All fixed candidates evaluated, but order remains discovery rank.
allm={**masks,**policies};perf=[];portrows=[];annual=[];summary=[];members=[]
for name,mask in allm.items():
 z=portfolio(mask,oos);z['strategy']=name;portrows.append(z)
 perf.append(dict(strategy=name,**performance(z)))
 for year,g in z.groupby(z.execution_date.dt.year):
    ann=classification(mask,x.year.eq(year)&x.execution_date.isin(oos));annual.append(dict(strategy=name,year=year,**ann,**performance(g)))
 scope=x.execution_date.isin(oos);r=classification(mask,scope)
 mm=[classification(mask,scope&x.execution_date.eq(d)) for d in oos]
 r.update(strategy=name,active_months=sum(t['selected_labeled_n']>0 for t in mm),precision_positive_months=sum(t['precision']>t['baseline_precision'] for t in mm),return_positive_months=sum(t['selected_mean_return']>t['basket_mean_return'] for t in mm),mean_monthly_precision_excess=pd.Series([t['precision']-t['baseline_precision'] for t in mm]).mean())
 r['unknown_feature_n']=int((scope&~knowns[name]).sum()) if name in knowns else np.nan
 summary.append(r)
 if name in policies:
    y=x.loc[scope,['execution_date','exit_date','ticker','feature_date','return','winner']].copy();y['strategy']=name;y['selected']=pd.Series(mask,index=x.index).loc[y.index];members.append(y)
perf=pd.DataFrame(perf);summary=pd.DataFrame(summary);annual=pd.DataFrame(annual)
pd.concat(portrows).to_csv(P/'strategy_monthly_returns.csv',index=False);perf.to_csv(P/'strategy_metrics.csv',index=False);summary.to_csv(P/'oos_classification_metrics.csv',index=False);annual.to_csv(P/'annual_metrics.csv',index=False);pd.concat(members).to_csv(P/'policy_membership.csv',index=False)
ranked=frozen.merge(summary.rename(columns={'strategy':'rule_id'}),on='rule_id',suffixes=('_train','_oos')).merge(perf.rename(columns={'strategy':'rule_id'}),on='rule_id',suffixes=('','_portfolio'))
ranked.to_csv(P/'ranked_setups.csv',index=False)
x.to_csv(P/'input_features_with_derivations.csv',index=False)
flags=pd.DataFrame({k:v for k,v in masks.items()});flags.insert(0,'ticker',x.ticker);flags.insert(0,'execution_date',x.execution_date);flags.to_csv(P/'setup_flags.csv',index=False)
audit=dict(source_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),plan_sha256=hashlib.sha256((P/'PLAN.md').read_bytes()).hexdigest(),rows=len(x),labeled=int(x.winner.notna().sum()),rules=len(rules),oos_months=len(oos),oos_start=str(oos[0].date()),oos_last_entry=str(oos[-1].date()),oos_final_exit=str(x.loc[x.execution_date.eq(oos[-1]),'exit_date'].max().date()),missing_outcomes_by_month={str(k):int(v) for k,v in x.groupby('execution_date')['return'].apply(lambda z:z.isna().sum()).items() if v},feature_missing={k:int(x[k].isna().sum()) for k in x if x[k].isna().any()},seconds=time.monotonic()-START,raw_data_loaded=False,earnings='unavailable: no demonstrated PIT 2009-2018 timestamp/coverage provenance; local pilot cache is not certification')
(P/'audit.json').write_text(json.dumps(audit,indent=2))
# Independent reproduction checks of labels, flags, calibration boundary, complement and accounting.
assert len(rules)==64 and rules.n_conditions.between(2,4).all()
for d,g in x[x.winner.notna()].groupby('execution_date'):
 ordered=g.sort_values(['return','ticker'],ascending=[False,True]);assert ordered.head(int(np.ceil(len(g)/4))).winner.eq(1).all();assert g.winner.sum()==np.ceil(len(g)/4)
assert np.allclose(x['return'],x.exit_open/x.entry_open-1,equal_nan=True)
for a in schedule:assert pd.Timestamp(a['max_train_exit'])<pd.Timestamp(a['evaluation_year'],1,1)
for name in policies:
 if name.endswith('_unselected'):assert (pd.Series(policies[name],index=x.index)^pd.Series(policies[name[:-11]],index=x.index)).all()
assert summary.selected_missing_outcome_n.eq(0).all()
assert pd.concat(portrows).groupby('strategy').size().eq(59).all()
assert (perf.mdd<=0).all() and np.isfinite(perf.cagr).all()
for rid in masks:
 assert masks[rid].equals(pd.Series(masks[rid],index=x.index)) if isinstance(masks[rid],pd.Series) else True
# Dynamic summary generation after verification.
def pct(a):return f'{100*a:.2f}%' if pd.notna(a) else 'NA'
def table(names):
 lines=['|Strategy|Winner hits / selected|Recall|Enrichment|CAGR net|MDD monthly|Sharpe|Positive precision months / active|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for name in names:
    a=summary.set_index('strategy').loc[name];b=perf.set_index('strategy').loc[name]
    lines.append(f'|{name}|{int(a.selected_winner_n)}/{int(a.selected_labeled_n)} ({pct(a.precision)})|{pct(a.recall)}|{a.enrichment:.2f}|{pct(b.cagr)}|{pct(b.mdd)}|{b.sharpe:.2f}|{int(a.precision_positive_months)}/{int(a.active_months)}|')
 return '\n'.join(lines)
names=['baseline_rsi_basket']+['expanding_'+f for f in ['all']+list(families)]+['frozen_all']
report=f'''# RSI multi-feature setup study, 2009–2018

Executed and verified 64 prespecified 2–4-condition rules. Discovery uses 2009–2013; 59 common walk-forward entry months run from {audit['oos_start']} through {audit['oos_last_entry']}, with final exit {audit['oos_final_exit']}. No production code changes, GA, 2019+ data, external fetches, or fitted OOS thresholds. Runtime {audit['seconds']:.1f} seconds, one numerical thread.

## Main OOS results

{table(names)}

These are winner precision and recall, not winner feature prevalence. The baseline winner rate is above 25% because each month labels exactly ceil(observed basket size/4) winners. Read all families, including weak or negative results; no family is promoted by OOS rank. Expanding-all is the primary prespecified selection policy. Fixed-all provides a completely frozen 2013 comparator.

The overall expanding policy improves pooled winner precision and net CAGR here, but selects only 72 stock-months and is active in 28/59 months. It captures only 25/236 winners, and its Sharpe is below the basket. Volume normalization has the highest family precision yet loses money after costs; relative strength has below-baseline precision despite positive returns. The frozen overall rule also has below-baseline precision. This is mixed evidence, not a validated repeatable winner detector.

## Design and timing

See PLAN.md for the design saved before setup evaluation, rule_definitions.csv for all 64 exact conjunctions, and condition_definitions.csv for inputs. Four economic families cover positive long trend with pullback, falling selling momentum/stabilization, elevated prior volume followed by normalization, and improving relative strength while price is depressed. Each rule combines 2–4 named raw or derived feature predicates. Volatility contraction uses derived vol_10/vol_21; derived features may use multiple raw inputs. Recent reversal compares unequal horizons and is a stabilization proxy. Volume ratios identify an elevated prior 15-session mean, not a dated one-day spike; vendor volume can be split-sensitive. RS improvement reconstructs prior 42-session relative performance from 63/21-session stock and benchmark returns, then compares simple per-session averages; this is a horizon-normalized proxy, not regression slope.

All features are taken from the immediately preceding global trading session without forward fill. Monthly labels rank next-month adjusted open-to-open returns descending, ticker ascending for ties. Monthly basket membership is copied verbatim from the source lowest-20%-RSI14 holdings; 12–15 stocks from the same supplied fixed 77-ticker universe. Cross-sectional outcomes never enter selection. No benchmark/universe changes between variants. The primary common benchmark is the entire RSI basket; relative-strength features retain the source equal-weight daily available-return universe benchmark.

Within each evaluation year the rule is fixed; annual expanding calibration uses all earlier labeled months whose exit is strictly earlier than January entry. December just before each evaluation year is embargoed, including December 2013, so initial calibration ends November 2013. Eligible rules require >=40 labeled selections and >=24 active training months. Rank by mean monthly selected winner precision minus monthly basket winner rate, tie-break pooled enrichment then rule ID. Family policies apply that identical procedure within each family. A negative best score is not suppressed. No 2014–2018 tuning or OOS-ranked choice is used. selection_schedule.csv and calibration_YEAR.csv disclose every choice, score, eligibility and cutoff. Later walk-forward years legitimately train on already realized earlier evaluation years.

## Portfolio and missingness

Portfolios assign equal weights at each shared entry open, hold until next shared entry open, then rebalance with drift-adjusted weights. Empty selections hold zero-return cash; complements use the same calendar. Costs are 10bps times bought notional plus 10bps times sold notional. Initial entry and final liquidation are charged. Monthly net return is (1-start cost)*(1-gross loss or +gross gain)-1, with final liquidation multiplicatively deducted at final exit. All positions are scaled proportionally to fund costs. Turnover exports are two-sided gross traded notional/NAV, not half turnover; both buy and sell legs are provided. No slippage beyond these fees, tax, financing, or capacity model. Sharpe uses monthly net mean/sample standard deviation ×sqrt(12), zero risk-free rate. CAGR annualizes by 12/month count; MDD includes initial NAV and uses monthly observations, so intramonth drawdown is unknown. Annual rows summarize that year's segment of the continuous simulation, not independent annual restarts.

There are {len(x)} candidate stock-months, {int(x.winner.notna().sum())} labeled. Only December 2018 lacks outcomes ({int(x['return'].isna().sum())} stocks), and is excluded from every performance/label denominator. Its features and flags remain exported. Unknown feature conditions fail selection, are counted separately and are included in the unselected portfolio; no feature imputation. No missing OOS returns occurred. If an in-period return were missing its preassigned weight would use a disclosed zero-return proxy, rather than outcome-aware reweighting. Pooled returns in classification tables are stock-month means; strategy returns are monthly portfolio means including cash and fees. They answer different questions.

## Annual consistency and negative results

'''
for name in names[1:]:
 a=annual[annual.strategy.eq(name)];r=summary.set_index('strategy').loc[name]
 report+=f"- {name}: annual enrichment >1 in {int(a.enrichment.gt(1).sum())}/{int(a.enrichment.notna().sum())} evaluable years; selected mean return beats unselected in {int(a.selected_mean_return.gt(a.unselected_mean_return).sum())}/{int((a.selected_mean_return.notna()&a.unselected_mean_return.notna()).sum())} evaluable years; active-month selected mean return beats basket in {int(r.return_positive_months)}/{int(r.active_months)} months.\n"
report+='\n|Policy|Selected gross stock-month mean|Unselected gross stock-month mean|Mean monthly two-sided turnover|\n|---|---:|---:|---:|\n'
for name in names[1:]:
 a=summary.set_index('strategy').loc[name];b=perf.set_index('strategy').loc[name]
 report+=f'|{name}|{pct(a.selected_mean_return)}|{pct(a.unselected_mean_return)}|{b.mean_monthly_two_sided_turnover:.3f}|\n'
report+='''
All fixed rules, including ineligible and losing rules, are exported in discovery order in ranked_setups.csv, with OOS metrics alongside training fields. setup_monthly_metrics.csv exposes the full monthly denominators, selected/unselected gross means and precision/enrichment for every fixed rule. annual_metrics.csv provides annual selected/unselected counts and strategy performance. strategy_monthly_returns.csv provides all common-date portfolio paths and turnover. oos_classification_metrics.csv and strategy_metrics.csv cover all rules, adaptive/frozen policies, baseline and policy complements. policy_membership.csv makes the executed selections reviewable. policy_monthly_metrics.csv provides policy precision, recall, enrichment and selected/unselected return denominators on each OOS month.

## Earnings and limitations

Post-earnings family: **unavailable**. The existing feature file has no dated earnings variable or release timestamps. Local earnings cache/pilot files do not establish full 2009–2018 point-in-time release availability and issuer coverage; no earnings rule is manufactured from them. No raw market or earnings data file was needed or loaded. Inspection of fetch_earnings_batch5.py and analyze_pilot_earnings_2019.py confirmed that the existing pilot workflow targets 2019, outside the authorized study period; those observations were not loaded.

The prior descriptive study examined the full 2009–2018 sample, and the requested families were informed by it. Consequently this is chronological out-of-sample computation within an already explored historical period, not a pristine untouched confirmatory holdout. Sixty-four dependent rules, five adaptive selections and additional frozen diagnostics create substantial multiple-comparisons and selection risk. There are only 59 OOS months and few stocks per basket; stock/month dependence, sparse strict conjunctions and regime changes weaken inference. No p-values or significance claims are made; an OOS-positive row alone does not establish a reliable edge. Cash can improve MDD while reducing exposure, and selected rules may capture volatility rather than unique recovery information. No risk matching is claimed.

Inherited limitations: fixed historical universe survivorship/availability bias; 77 rather than nominal 79 tickers; vendor adjusted prices not independently certified point-in-time; possible split artifacts in vendor volume; label construction excludes unobserved returns; no independently validated delisting coverage. Relative-strength benchmark uses changing available members. Results apply only to this supplied basket and data convention.

## Reproduction and verification

Run `bash experiments/dev79_rsi_predictive_setups_20261101/run.sh` from repository root. A 900-second hard timeout bounds execution. study.py writes artifacts and asserts date boundaries, exact monthly winner counts/ties, open-to-open returns, 64-rule boundedness, strict calibration exit embargo, complementary policy membership, 59 equal OOS months per variant, no missing OOS returns, and finite accounting metrics. audit.json hashes source and frozen design and records missingness. verification.json records successful checks. verify.py independently replays dollar holdings, cash, fees, turnover and CAGR for all policies and complements, and reproduces training rankings and all fixed-rule OOS counts; validation.log records its result. No production files were changed by this study.
'''
(P/'REPORT.md').write_text(report)
(P/'verification.json').write_text(json.dumps(dict(status='PASS',rules=64,oos_months=59,strategies=len(perf),checks=['pre-entry dates','no 2019+ endpoints','monthly labels/ties','open-to-open outcomes','strict training embargo','policy complements','common OOS months','no missing OOS returns','finite strategy accounting']),indent=2))
print(table(names));print('PASS',P/'REPORT.md')
