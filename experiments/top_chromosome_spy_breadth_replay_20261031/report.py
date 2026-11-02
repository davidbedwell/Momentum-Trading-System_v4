import study,json
import pandas as pd
import numpy as np
R=study.R

def table(df):
 d=df.copy()
 for c in d.select_dtypes(include='number'):d[c]=d[c].map(lambda x:f'{x:.5f}' if pd.notna(x) else 'NA')
 return '| '+' | '.join(d.columns)+' |\n|'+'|'.join(['---']*len(d.columns))+'|\n'+'\n'.join('| '+' | '.join(map(str,z))+' |' for z in d.to_numpy())
def main():
 t=pd.read_csv(R/'trades.csv.gz');t.to_csv(R/'trades.csv',index=False);c=pd.read_csv(R/'correlations.csv');s=pd.read_csv(R/'selection.csv');f=pd.read_csv(R/'fold_correlations.csv');d=pd.read_csv(R/'decision_summary.csv');b=pd.read_csv(R/'block_bootstrap.csv');m=pd.read_csv(R/'matched_conditions.csv');y=pd.read_csv(R/'same_chromosome_years.csv');meta=json.loads((R/'metadata.json').read_text())
 alltests=[]
 for name in ['correlations','fold_correlations','same_chromosome_years','matched_conditions','decision_summary']:
  z=pd.read_csv(R/(name+'.csv'));z['test_family']=name;alltests.append(z)
 a=pd.concat(alltests,ignore_index=True);a['q_global']=study.prior.bh(a.p);a['p_global_bonferroni']=(a.p*a.p.notna().sum()).clip(upper=1);a.to_csv(R/'all_tests.csv',index=False)
 pool=pd.read_csv(study.P/'selection.csv');pool=pool[pool.identity_sample].merge(pd.read_csv(study.P/'ledger_inventory.csv'),on=['system','chromosome_id']);pool.to_csv(R/'candidate_pool.csv',index=False)
 for path in [study.P/'ledger_inventory.csv',study.P/'source_hashes.json',R/'supplement.py',R/'test_study.py',R/'report.py',R/'verify_replay.py',R.parent/'breadth_chromosome_multihorizon_20261031/study.py',R.parent/'breadth_chromosome_entry_20261031/ga8_study.py']:
  meta['hashes'][str(path)]=study.sha(path)
 meta['fresh_engine_replay']='BLOCKED: inaccessible ga4_registry SOURCE at import';meta['multiple_tests_total']=int(a.p.notna().sum());meta['supplement_bootstrap_replicates']=400;(R/'metadata.json').write_text(json.dumps(meta,indent=2))
 counts=t.groupby('system').agg(trades=('net_return','size'),chromosomes=('chromosome_id','nunique'),entry_dates=('entry_date','nunique'),mean_return=('net_return','mean'),win_rate=('win','mean')).reset_index()
 main=c[(c.feature=='b50')&~c.within_chromosome_year][['system','method','n','dates','correlation','lo','hi','p','q_bh']]
 levels=c[(c.method=='spearman')&~c.within_chromosome_year&c.feature.str.startswith('b')][['system','feature','correlation','lo','hi','q_bh']]
 sel=s[['fold','system','chromosome_id','training_closed_trades','cagr','mdd','score']].copy();sel.chromosome_id=sel.chromosome_id.str[:12]
 same=y[(y.method=='spearman')&(y.system=='GA6')&(y.chromosome_id.str.startswith('42a5'))][['year','n','dates','correlation']]
 dec=pd.read_csv(R/'quantile_deciles.csv');dec=dec[dec.ma==50][['system','quantile_decile','n','dates','mean_return','win_rate']]
 text=f'''# Top-chromosome entry breadth: chronological archival replay

The available evidence does **not establish a stable positive or negative relationship or a useful breadth decision rule**. GA6 MA50 correlations are weakly negative; GA8 is near zero; GA7 has negative Pearson but near-zero Spearman correlation, suggesting sensitivity to return magnitudes rather than a stable monotonic effect. This is insufficient evidence of a reliable relationship, not proof that the true relationship is zero. All returns below are decimal fractions.

## Scope and selection

Read the prior archival REPORT, its selection/ledger inventories and fills, and the existing multihorizon code/PROTOCOL and partial outputs. The multihorizon directory had no REPORT or final pooled results at inspection; it was not silently treated as a completed study. Its causal feature builder is reused. The prior 270,109-trade GA6/7 union is **not** labeled prospectively selected winners.

Use the fixed identity sample: 400 GA6 and 280 GA7 (first 20 sorted IDs per archived GA7 group), **680 candidates**, excluding retrospective top-list additions. These are the strongest by the specified training metric within this bounded sample, not all 12,431 GA7 genomes. For each family, select three by training NAV CAGR / max(training NAV drawdown, 1%), requiring >=30 closed training trades, with chromosome ID tie-break. Training begins 2009-01-01 and ends strictly before 2012, 2014, or 2016. Test windows are [2012,2014), [2014,2016), [2016,2018). Training NAV includes only marks already observed before the cutoff. No future return, activity, or breadth association is used to select or replace a chromosome. Five of 18 selected family/fold slots have no closed test trades; these stay in fold_audit.csv rather than being replaced after seeing inactivity.

{table(sel)}

Full identities, scores and all candidate ranks are in selection.csv and candidate_rankings.csv; candidate_pool.csv retains original ledger hashes. Eighteen selected slots represent {meta['selected_identities']} distinct GA6/7 identities. Crucial limitation: checkpoints and genomes were discovered in 2026. Earlier-period ranking prevents **additional** test-period ranking leakage, but cannot make these historical folds prospective or undo genetic search, survivor, universe or prior experiment selection bias. Training scores can select dormant models and behavioral duplicates; correlated trades are not independent confirmations.

## Replay and accounting

Reuse the immutable original common-v1 replay fills and daily NAV, preserving its original genome rules and continuous portfolio state; this is a chronological **cached-fill replay**, not a new native GA6/7 strategy implementation. Acquisition expenditure sums every BUY including 10bp per-side entry fees; original net PnL includes partial reductions, exits, dividends and fees. Net return = net PnL / all acquisition expenditure; **R is not used as a net return**. Completed fill cycles reconcile original PnL to <0.01 currency unit. All calculations are hypothetical account currency amounts, not live profits.

The archived contract uses next-open decisions, zero cash yield, 10% symbol acquisition cap, genome capacities, sector/risk constraints and optimistic OHLC stop ordering, on split-adjusted prices. Native GA6/GA7 implementations differ; common-v1 results must not be relabeled native backtests. Test rows must both enter and exit within their fold. {pd.read_csv(R/'fold_audit.csv').boundary_excluded.sum()} entries still open at a fold cutoff are excluded, introducing completed-trade censoring; pre-cutoff positions carried into a fold are also excluded. The underlying portfolio state is continuous and no independent cash-reset test is claimed.

A deterministic fresh replay of one latest-fold candidate per family was attempted with the original driver (verify_replay.py). It failed at import: ga4_registry requires `/opt/mts/thunder-migration/mts-layered-run-20261007/Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet`, which is permission denied. No engine inputs were replaced and no exact fresh-rerun equivalence is claimed. replay_verification.log preserves the failure. The accessible historical ledgers remain usable.

GA6/7 MAE uses original fills, share exposure, partial realized proceeds, dividends and low-price liquidation marks while shares remain open; all costs use the same engine assumptions. It is an **OHLC model proxy**, not verified intraday-path MAE. GA8 MAE is a separate adjusted-close path adverse-excursion proxy beginning at entry close; it omits fill prices, scaling and intraday losses, and is not comparable fill-level MAE. One-day GA8 episodes may show zero proxy MAE despite actual losses. Ledger fields include mae_method so these are never silently pooled as identical measures.

GA8 retains only the three archived winners' 2023/2024/2025 completed episodes (133/809/555), each selected with a recorded earlier training cutoff. Selection was inherited, not reranked on forward outcomes. Eleven open episodes (0/1/10) remain excluded. Net returns use original episode acquisition accounting, including adds, execution-price slippage, commissions and dividend entitlement; no slippage is subtracted twice. There are three **different** chromosomes, so no same-chromosome multi-year GA8 validation, cross-candidate training ranking, or GA8 filter improvement claim is possible.

## Breadth at entry

SPY is one ETF. The measured series is **DEV79 market-wide breadth proxy**, not literal SPY breadth or S&P 500 constituent breadth. Among the inspected local inputs no validated point-in-time S&P 500 membership-plus-price breadth panel was available; existing membership reconstruction is insufficient, so no constituent series is fabricated or substituted. DEV79 is retrospective and eligibility is observed price availability, not independently validated historical tradability/membership.

For MA 10/20/50/100/200, take the fraction of DEV79 adjusted closes strictly above their trailing MA, requiring the full window of nonmissing observations and >=20 eligible stocks. Reindex to the SPY session calendar; every feature is shifted one session. feature_date is strictly before entry_date. n10/n20/n50/n100/n200 expose denominators. Secondary velocity = five-session breadth difference / 5; acceleration = (b[t]-2b[t-5]+b[t-10])/25, using prior-close data. No forward SPY return is an entry control.

{table(counts)}

## Correlations and uncertainty

Pearson and Spearman compare prior-close breadth with **net trade return**, separately for each GA family. Entry-date influence scores sum all stocks/chromosomes sharing a date, with calendar Bartlett HAC(63) and HAC(126) sensitivity. Spearman HAC treats observed marginal ranks as fixed, an approximation. Independent-trade standard errors are not used. Sparse comparisons (<30 trades or <20 distinct dates) retain point estimates but have no inferential intervals/p-values. Date counts, not just trade counts, determine support. Within-chromosome/year demeaned versions are sensitivity measures, including globally ranked demeaned Spearman, not separate independent replications.

MA50 pooled results (95% HAC intervals):

{table(main)}

Three-month moving-block bootstrap resamples all trades in a sampled month together, 400 replicates with seed 20261101; intervals re-estimate marginal ranks. It preserves date clusters and nearby serial dependence but is exploratory with few folds and regime changes:

{table(b)}

Spearman across all requested MAs:

{table(levels)}

Some conditional historical associations survive the broader correction and should not be hidden by the inconclusive MA50 rank results. In particular, GA6's within-chromosome/year MA200 demeaned-rank association is -0.2355 (95% HAC interval -0.3344 to -0.1366; global BH q≈0.00036). Its raw MA200 Spearman is -0.1473, with 84-test-family q≈0.210. The conditional result therefore depends on the adjustment/estimand and does not validate an executable threshold. GA7 MA50/100 Pearson and GA8's small within-year MA200 Pearson effects also survive global BH. These are evidence of selected historical negative associations, with discovery and regime limitations, rather than universal uncorrelated outcomes. All globally BH-significant pooled correlations are shown here:

{table(a[(a.test_family=='correlations')&(a.q_global<.05)][['system','feature','method','within_chromosome_year','correlation','lo','hi','q_global','p_global_bonferroni']])}

Secondary MA50 five-session velocity and acceleration (raw pooled estimates):

{table(c[(~c.within_chromosome_year)&c.feature.isin(['v50_5','a50_5'])][['system','feature','method','correlation','lo','hi','q_bh']])}

No secondary derivative test survives the 84-test correction. These are secondary to levels and no lag search was performed.

correlations.csv contains 84 tests (5 levels plus MA50 velocity/acceleration × Pearson/Spearman × raw/within × 3 GA families), BH q and Bonferroni. Fold/year/matched/filter files have their own BH families. all_tests.csv additionally adjusts **all {int(a.p.notna().sum())} finite tests together**, both BH and Bonferroni; missing/sparse tests are not counted. These corrections cannot undo genome optimization, inherited winner selection, all earlier research or post hoc analysis design. No discovery here is a preregistered validated signal.

## Stability, matched conditions and deciles

{table(f[['system','fold','method','n','dates','correlation','lo','hi']])}

GA6's MA50 Pearson changes from -0.055 in F1 to -0.312 in F2 and +0.070 in F3; Spearman changes from -0.056 to -0.301 to +0.040. The pooled weak negative relationship therefore hides an unstable fold effect. GA7 F1 has zero completed trades and F3 just four: its pooled estimate mainly reflects F2, not repeatability across three active periods.

The same GA6 chromosome 42a5f1a5fb34 across entry years illustrates variation (sparse years are descriptive):

{table(same)}

same_chromosome_years.csv contains every eligible chromosome/year comparison. Distinct genomes sometimes have identical trades, so they are not independent evidence. GA8 year differences conflate market year and selected chromosome.

Matched weak (<0.4) versus strong (>0.6) breadth controls same chromosome, ticker, calendar year, SPY 63-session momentum sign, and annualized 20-session volatility band (<15%, 15–25%, >25%), all known at entry. No realized holding-duration control is used. Each matched cell and arm receives equal weight; uncertainty clusters its weighted influence by date. This is an observational sensitivity, not causal identification:

{table(m)}

GA6 has only 21 matched trades and GA7 four: no usable matched inference. GA8's matched weak-minus-strong estimate changes sign relative to some raw summaries and includes zero. Sparse overlap prevents a strong incremental market-condition claim.

quantile_deciles.csv reports within-family empirical breadth deciles separately for each MA, retaining ties and dropping duplicate quantile boundaries. These bins are descriptive and learned on the evaluated sample, not executable entry thresholds. breadth_deciles.csv provides the complementary **fixed 10-percentage-point breadth bands**, despite its legacy filename. Counts/dates, win rates and mean returns accompany each; bands are not equal-population quantiles. MA50 quantile details:

{table(dec)}

## Does breadth improve decisions?

For each selected GA6/7 chromosome/fold, choose among five MAs × low/high direction using **training completed trades only**, at that training sample's median breadth. Require >=20 kept training trades, maximize mean net return, then freeze MA, direction and threshold before testing. decision_value.csv records all nonempty test slots. No future thresholds or replacement chromosome are selected. All training choices happened to prefer lower breadth; this is an observed result, not a coded requirement.

{table(d)}

The delta/interval compare kept versus skipped trades; base_mean and kept_mean show the change relative to all original trades. GA6 improves average trade return in {int((pd.read_csv(R/'decision_value.csv').query("system == 'GA6'").delta_mean>0).sum())}/9 active slots; GA7 has only four active slots, two with <=7 trades. These selected-trade comparisons do **not** replay freed cash, capacity, later order competition, portfolio drawdown or position sizing. kept_pnl is an arithmetic subset of the original hypothetical ledger, not a counterfactual portfolio. No evidence here establishes improved executable risk-adjusted decisions. No filter is recommended for deployment.

## Deliverables, checks and constraints

trades.csv is the auditable CSV, also supplied as trades.csv.gz: chromosome_id, system (GA), ticker, entry/exit dates, fold/year, original pnl, acquisition_cost, net_return, MAE/proxy/method and prior-close breadth/derivatives/denominators. entry_features.csv gives the independent feature calendar. candidate rankings, pool hashes, selection, fold support, correlations, bootstrap, deciles, matched comparisons, per-year results, decision checks and global corrections are machine-readable companions.

Four tests cover causal prefix invariance and prior-close timing, training-score invariance to future NAV mutation, original fill-cycle return/count/fold reconciliation, and scaled partial-exit accounting. tests.log records the result. metadata.json hashes inputs and code, with selected source-ledger hashes and original pool inventory hashes. The earlier source_hashes.json and GA8 inventory provide original fold provenance.

Computation was bounded to a 20-minute budget: main selection/accounting/statistics took {meta['elapsed_seconds']:.1f} seconds; supplementary block bootstrap and checks took additional seconds/minutes. The overall work finished within the budget; no full 12,831-genome rerun, new search, remote data acquisition or inaccessible data reconstruction was attempted. The fresh replay attempt is explicitly blocked as above. All created/edited artifacts are under this experiment. No MTS/GA or live-system code, configuration or database was changed.

Reproduce from repository root with `/opt/mts/.venv/bin/python`:

```sh
/opt/mts/.venv/bin/python experiments/top_chromosome_spy_breadth_replay_20261031/study.py
/opt/mts/.venv/bin/python experiments/top_chromosome_spy_breadth_replay_20261031/supplement.py
/opt/mts/.venv/bin/python -m unittest discover -s experiments/top_chromosome_spy_breadth_replay_20261031 -p test_study.py -v
/opt/mts/.venv/bin/python experiments/top_chromosome_spy_breadth_replay_20261031/report.py
```

verify_replay.py is optional and currently fails on the inaccessible upstream import; it is not part of the passing test command. No predictive or production certification is made.
'''
 (R/'REPORT.md').write_text(text)
if __name__=='__main__':main()
