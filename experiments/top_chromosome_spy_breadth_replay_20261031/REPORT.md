# Top-chromosome entry breadth: chronological archival replay

The available evidence does **not establish a stable positive or negative relationship or a useful breadth decision rule**. GA6 MA50 correlations are weakly negative; GA8 is near zero; GA7 has negative Pearson but near-zero Spearman correlation, suggesting sensitivity to return magnitudes rather than a stable monotonic effect. This is insufficient evidence of a reliable relationship, not proof that the true relationship is zero. All returns below are decimal fractions.

## Scope and selection

Read the prior archival REPORT, its selection/ledger inventories and fills, and the existing multihorizon code/PROTOCOL and partial outputs. The multihorizon directory had no REPORT or final pooled results at inspection; it was not silently treated as a completed study. Its causal feature builder is reused. The prior 270,109-trade GA6/7 union is **not** labeled prospectively selected winners.

Use the fixed identity sample: 400 GA6 and 280 GA7 (first 20 sorted IDs per archived GA7 group), **680 candidates**, excluding retrospective top-list additions. These are the strongest by the specified training metric within this bounded sample, not all 12,431 GA7 genomes. For each family, select three by training NAV CAGR / max(training NAV drawdown, 1%), requiring >=30 closed training trades, with chromosome ID tie-break. Training begins 2009-01-01 and ends strictly before 2012, 2014, or 2016. Test windows are [2012,2014), [2014,2016), [2016,2018). Training NAV includes only marks already observed before the cutoff. No future return, activity, or breadth association is used to select or replace a chromosome. Five of 18 selected family/fold slots have no closed test trades; these stay in fold_audit.csv rather than being replaced after seeing inactivity.

| fold | system | chromosome_id | training_closed_trades | cagr | mdd | score |
|---|---|---|---|---|---|---|
| F2 | GA6 | 36f53f73e2b6 | 179.00000 | 0.08713 | 0.04514 | 1.92995 |
| F3 | GA6 | 36f53f73e2b6 | 227.00000 | 0.06229 | 0.04514 | 1.37973 |
| F1 | GA6 | 42a5f1a5fb34 | 97.00000 | 0.17437 | 0.06918 | 2.52073 |
| F2 | GA6 | 42a5f1a5fb34 | 179.00000 | 0.12938 | 0.06918 | 1.87029 |
| F3 | GA6 | 42a5f1a5fb34 | 230.00000 | 0.09685 | 0.07402 | 1.30842 |
| F2 | GA6 | 79b45b1fd15c | 156.00000 | 0.22110 | 0.10897 | 2.02900 |
| F3 | GA6 | 79b45b1fd15c | 202.00000 | 0.16014 | 0.10897 | 1.46961 |
| F1 | GA6 | dc024e6a4adf | 97.00000 | 0.17437 | 0.06918 | 2.52073 |
| F1 | GA6 | f087e59a0bfc | 107.00000 | 0.08111 | 0.03624 | 2.23793 |
| F1 | GA7 | 0042a3d812ac | 49.00000 | 0.03803 | 0.01079 | 3.52383 |
| F2 | GA7 | 0042a3d812ac | 49.00000 | 0.02260 | 0.01079 | 2.09385 |
| F3 | GA7 | 0042a3d812ac | 56.00000 | 0.01538 | 0.01915 | 0.80320 |
| F1 | GA7 | 02ef8253dc78 | 59.00000 | 0.01659 | 0.00990 | 1.65881 |
| F3 | GA7 | 02ef8253dc78 | 61.00000 | 0.00787 | 0.00990 | 0.78688 |
| F2 | GA7 | 0a6ec0b12161 | 390.00000 | 0.02450 | 0.01997 | 1.22675 |
| F2 | GA7 | 0ca35a5e4065 | 302.00000 | 0.04221 | 0.03147 | 1.34144 |
| F1 | GA7 | 0fe1feebc33d | 59.00000 | 0.01615 | 0.00962 | 1.61514 |
| F3 | GA7 | 0fe1feebc33d | 61.00000 | 0.00766 | 0.00962 | 0.76616 |

Full identities, scores and all candidate ranks are in selection.csv and candidate_rankings.csv; candidate_pool.csv retains original ledger hashes. Eighteen selected slots represent 10 distinct GA6/7 identities. Crucial limitation: checkpoints and genomes were discovered in 2026. Earlier-period ranking prevents **additional** test-period ranking leakage, but cannot make these historical folds prospective or undo genetic search, survivor, universe or prior experiment selection bias. Training scores can select dormant models and behavioral duplicates; correlated trades are not independent confirmations.

## Replay and accounting

Reuse the immutable original common-v1 replay fills and daily NAV, preserving its original genome rules and continuous portfolio state; this is a chronological **cached-fill replay**, not a new native GA6/7 strategy implementation. Acquisition expenditure sums every BUY including 10bp per-side entry fees; original net PnL includes partial reductions, exits, dividends and fees. Net return = net PnL / all acquisition expenditure; **R is not used as a net return**. Completed fill cycles reconcile original PnL to <0.01 currency unit. All calculations are hypothetical account currency amounts, not live profits.

The archived contract uses next-open decisions, zero cash yield, 10% symbol acquisition cap, genome capacities, sector/risk constraints and optimistic OHLC stop ordering, on split-adjusted prices. Native GA6/GA7 implementations differ; common-v1 results must not be relabeled native backtests. Test rows must both enter and exit within their fold. 71 entries still open at a fold cutoff are excluded, introducing completed-trade censoring; pre-cutoff positions carried into a fold are also excluded. The underlying portfolio state is continuous and no independent cash-reset test is claimed.

A deterministic fresh replay of one latest-fold candidate per family was attempted with the original driver (verify_replay.py). It failed at import: ga4_registry requires `/opt/mts/thunder-migration/mts-layered-run-20261007/Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet`, which is permission denied. No engine inputs were replaced and no exact fresh-rerun equivalence is claimed. replay_verification.log preserves the failure. The accessible historical ledgers remain usable.

GA6/7 MAE uses original fills, share exposure, partial realized proceeds, dividends and low-price liquidation marks while shares remain open; all costs use the same engine assumptions. It is an **OHLC model proxy**, not verified intraday-path MAE. GA8 MAE is a separate adjusted-close path adverse-excursion proxy beginning at entry close; it omits fill prices, scaling and intraday losses, and is not comparable fill-level MAE. One-day GA8 episodes may show zero proxy MAE despite actual losses. Ledger fields include mae_method so these are never silently pooled as identical measures.

GA8 retains only the three archived winners' 2023/2024/2025 completed episodes (133/809/555), each selected with a recorded earlier training cutoff. Selection was inherited, not reranked on forward outcomes. Eleven open episodes (0/1/10) remain excluded. Net returns use original episode acquisition accounting, including adds, execution-price slippage, commissions and dividend entitlement; no slippage is subtracted twice. There are three **different** chromosomes, so no same-chromosome multi-year GA8 validation, cross-candidate training ranking, or GA8 filter improvement claim is possible.

## Breadth at entry

SPY is one ETF. The measured series is **DEV79 market-wide breadth proxy**, not literal SPY breadth or S&P 500 constituent breadth. Among the inspected local inputs no validated point-in-time S&P 500 membership-plus-price breadth panel was available; existing membership reconstruction is insufficient, so no constituent series is fabricated or substituted. DEV79 is retrospective and eligibility is observed price availability, not independently validated historical tradability/membership.

For MA 10/20/50/100/200, take the fraction of DEV79 adjusted closes strictly above their trailing MA, requiring the full window of nonmissing observations and >=20 eligible stocks. Reindex to the SPY session calendar; every feature is shifted one session. feature_date is strictly before entry_date. n10/n20/n50/n100/n200 expose denominators. Secondary velocity = five-session breadth difference / 5; acceleration = (b[t]-2b[t-5]+b[t-10])/25, using prior-close data. No forward SPY return is an entry control.

| system | trades | chromosomes | entry_dates | mean_return | win_rate |
|---|---|---|---|---|---|
| GA6 | 596.00000 | 5.00000 | 164.00000 | 0.02514 | 0.61409 |
| GA7 | 234.00000 | 3.00000 | 138.00000 | -0.00082 | 0.31197 |
| GA8 | 1497.00000 | 3.00000 | 533.00000 | -0.00172 | 0.43019 |

## Correlations and uncertainty

Pearson and Spearman compare prior-close breadth with **net trade return**, separately for each GA family. Entry-date influence scores sum all stocks/chromosomes sharing a date, with calendar Bartlett HAC(63) and HAC(126) sensitivity. Spearman HAC treats observed marginal ranks as fixed, an approximation. Independent-trade standard errors are not used. Sparse comparisons (<30 trades or <20 distinct dates) retain point estimates but have no inferential intervals/p-values. Date counts, not just trade counts, determine support. Within-chromosome/year demeaned versions are sensitivity measures, including globally ranked demeaned Spearman, not separate independent replications.

MA50 pooled results (95% HAC intervals):

| system | method | n | dates | correlation | lo | hi | p | q_bh |
|---|---|---|---|---|---|---|---|---|
| GA6 | pearson | 596.00000 | 164.00000 | -0.05588 | -0.20262 | 0.09086 | 0.45543 | 0.68365 |
| GA6 | spearman | 596.00000 | 164.00000 | -0.07762 | -0.21866 | 0.06342 | 0.28072 | 0.52401 |
| GA7 | pearson | 234.00000 | 138.00000 | -0.15723 | -0.24976 | -0.06471 | 0.00087 | 0.01819 |
| GA7 | spearman | 234.00000 | 138.00000 | -0.02178 | -0.13752 | 0.09395 | 0.71218 | 0.85461 |
| GA8 | pearson | 1497.00000 | 533.00000 | -0.02140 | -0.08771 | 0.04491 | 0.52701 | 0.73782 |
| GA8 | spearman | 1497.00000 | 533.00000 | 0.01286 | -0.04777 | 0.07349 | 0.67757 | 0.84727 |

Three-month moving-block bootstrap resamples all trades in a sampled month together, 400 replicates with seed 20261101; intervals re-estimate marginal ranks. It preserves date clusters and nearby serial dependence but is exploratory with few folds and regime changes:

| system | feature | method | replicates | lo | hi |
|---|---|---|---|---|---|
| GA6 | b50 | pearson | 400.00000 | -0.19895 | 0.08728 |
| GA6 | b50 | spearman | 400.00000 | -0.20815 | 0.06338 |
| GA7 | b50 | pearson | 400.00000 | -0.28051 | -0.09595 |
| GA7 | b50 | spearman | 400.00000 | -0.20716 | 0.06536 |
| GA8 | b50 | pearson | 400.00000 | -0.10180 | 0.04069 |
| GA8 | b50 | spearman | 400.00000 | -0.09420 | 0.06687 |

Spearman across all requested MAs:

| system | feature | correlation | lo | hi | q_bh |
|---|---|---|---|---|---|
| GA6 | b10 | -0.09756 | -0.23124 | 0.03612 | 0.41814 |
| GA6 | b20 | -0.05009 | -0.19982 | 0.09963 | 0.72895 |
| GA6 | b50 | -0.07762 | -0.21866 | 0.06342 | 0.52401 |
| GA6 | b100 | -0.13124 | -0.27586 | 0.01338 | 0.36931 |
| GA6 | b200 | -0.14735 | -0.27732 | -0.01737 | 0.20983 |
| GA7 | b10 | 0.00634 | -0.24629 | 0.25897 | 0.96075 |
| GA7 | b20 | -0.00637 | -0.18951 | 0.17677 | 0.96075 |
| GA7 | b50 | -0.02178 | -0.13752 | 0.09395 | 0.85461 |
| GA7 | b100 | -0.04216 | -0.18644 | 0.10212 | 0.75862 |
| GA7 | b200 | 0.00770 | -0.12590 | 0.14129 | 0.96075 |
| GA8 | b10 | -0.03123 | -0.07751 | 0.01505 | 0.41814 |
| GA8 | b20 | -0.03380 | -0.09272 | 0.02512 | 0.50958 |
| GA8 | b50 | 0.01286 | -0.04777 | 0.07349 | 0.84727 |
| GA8 | b100 | 0.02180 | -0.04102 | 0.08463 | 0.72895 |
| GA8 | b200 | -0.02381 | -0.10379 | 0.05617 | 0.75862 |

Some conditional historical associations survive the broader correction and should not be hidden by the inconclusive MA50 rank results. In particular, GA6's within-chromosome/year MA200 demeaned-rank association is -0.2355 (95% HAC interval -0.3344 to -0.1366; global BH q≈0.00036). Its raw MA200 Spearman is -0.1473, with 84-test-family q≈0.210. The conditional result therefore depends on the adjustment/estimand and does not validate an executable threshold. GA7 MA50/100 Pearson and GA8's small within-year MA200 Pearson effects also survive global BH. These are evidence of selected historical negative associations, with discovery and regime limitations, rather than universal uncorrelated outcomes. All globally BH-significant pooled correlations are shown here:

| system | feature | method | within_chromosome_year | correlation | lo | hi | q_global | p_global_bonferroni |
|---|---|---|---|---|---|---|---|---|
| GA6 | b200 | spearman | True | -0.23552 | -0.33443 | -0.13661 | 0.00036 | 0.00036 |
| GA7 | b50 | pearson | False | -0.15723 | -0.24976 | -0.06471 | 0.02061 | 0.10306 |
| GA7 | b50 | pearson | True | -0.16008 | -0.24430 | -0.07585 | 0.00774 | 0.02323 |
| GA7 | b100 | pearson | True | -0.18262 | -0.28903 | -0.07620 | 0.02061 | 0.09160 |
| GA8 | b200 | pearson | True | -0.08882 | -0.14518 | -0.03247 | 0.03413 | 0.23892 |

Secondary MA50 five-session velocity and acceleration (raw pooled estimates):

| system | feature | method | correlation | lo | hi | q_bh |
|---|---|---|---|---|---|---|
| GA6 | v50_5 | pearson | -0.07102 | -0.21825 | 0.07621 | 0.55927 |
| GA6 | v50_5 | spearman | -0.07435 | -0.22561 | 0.07690 | 0.55927 |
| GA6 | a50_5 | pearson | -0.08967 | -0.22447 | 0.04514 | 0.41814 |
| GA6 | a50_5 | spearman | -0.08958 | -0.21620 | 0.03703 | 0.41814 |
| GA7 | v50_5 | pearson | -0.13677 | -0.31588 | 0.04233 | 0.41814 |
| GA7 | v50_5 | spearman | -0.00796 | -0.22310 | 0.20717 | 0.96075 |
| GA7 | a50_5 | pearson | -0.12892 | -0.26747 | 0.00963 | 0.35795 |
| GA7 | a50_5 | spearman | -0.05497 | -0.25242 | 0.14248 | 0.76819 |
| GA8 | v50_5 | pearson | -0.04960 | -0.12035 | 0.02116 | 0.41814 |
| GA8 | v50_5 | spearman | -0.04074 | -0.09693 | 0.01545 | 0.41814 |
| GA8 | a50_5 | pearson | -0.00174 | -0.06751 | 0.06402 | 0.96075 |
| GA8 | a50_5 | spearman | 0.00209 | -0.07062 | 0.07481 | 0.96075 |

No secondary derivative test survives the 84-test correction. These are secondary to levels and no lag search was performed.

correlations.csv contains 84 tests (5 levels plus MA50 velocity/acceleration × Pearson/Spearman × raw/within × 3 GA families), BH q and Bonferroni. Fold/year/matched/filter files have their own BH families. all_tests.csv additionally adjusts **all 119 finite tests together**, both BH and Bonferroni; missing/sparse tests are not counted. These corrections cannot undo genome optimization, inherited winner selection, all earlier research or post hoc analysis design. No discovery here is a preregistered validated signal.

## Stability, matched conditions and deciles

| system | fold | method | n | dates | correlation | lo | hi |
|---|---|---|---|---|---|---|---|
| GA6 | F1 | pearson | 253.00000 | 51.00000 | -0.05502 | -0.24854 | 0.13850 |
| GA6 | F1 | spearman | 253.00000 | 51.00000 | -0.05565 | -0.24151 | 0.13021 |
| GA6 | F2 | pearson | 126.00000 | 42.00000 | -0.31238 | -0.47086 | -0.15390 |
| GA6 | F2 | spearman | 126.00000 | 42.00000 | -0.30092 | -0.49859 | -0.10326 |
| GA6 | F3 | pearson | 217.00000 | 71.00000 | 0.06967 | -0.18358 | 0.32291 |
| GA6 | F3 | spearman | 217.00000 | 71.00000 | 0.04004 | -0.22314 | 0.30323 |
| GA7 | F2 | pearson | 230.00000 | 134.00000 | -0.14315 | -0.22972 | -0.05657 |
| GA7 | F2 | spearman | 230.00000 | 134.00000 | -0.00380 | -0.11670 | 0.10910 |
| GA8 | GA8_2023 | pearson | 133.00000 | 85.00000 | -0.04110 | -0.33591 | 0.25370 |
| GA8 | GA8_2023 | spearman | 133.00000 | 85.00000 | -0.15205 | -0.38727 | 0.08316 |
| GA8 | GA8_2024 | pearson | 809.00000 | 231.00000 | 0.03219 | -0.04902 | 0.11340 |
| GA8 | GA8_2024 | spearman | 809.00000 | 231.00000 | 0.02689 | -0.05067 | 0.10445 |
| GA8 | GA8_2025 | pearson | 555.00000 | 217.00000 | -0.07072 | -0.21314 | 0.07171 |
| GA8 | GA8_2025 | spearman | 555.00000 | 217.00000 | -0.04493 | -0.18393 | 0.09407 |

GA6's MA50 Pearson changes from -0.055 in F1 to -0.312 in F2 and +0.070 in F3; Spearman changes from -0.056 to -0.301 to +0.040. The pooled weak negative relationship therefore hides an unstable fold effect. GA7 F1 has zero completed trades and F3 just four: its pooled estimate mainly reflects F2, not repeatability across three active periods.

The same GA6 chromosome 42a5f1a5fb34 across entry years illustrates variation (sparse years are descriptive):

| year | n | dates | correlation |
|---|---|---|---|
| 2012.00000 | 50.00000 | 13.00000 | 0.11570 |
| 2013.00000 | 32.00000 | 10.00000 | -0.09095 |
| 2014.00000 | 40.00000 | 14.00000 | -0.36298 |
| 2016.00000 | 40.00000 | 9.00000 | 0.12849 |
| 2017.00000 | 38.00000 | 9.00000 | -0.12941 |

same_chromosome_years.csv contains every eligible chromosome/year comparison. Distinct genomes sometimes have identical trades, so they are not independent evidence. GA8 year differences conflate market year and selected chromosome.

Matched weak (<0.4) versus strong (>0.6) breadth controls same chromosome, ticker, calendar year, SPY 63-session momentum sign, and annualized 20-session volatility band (<15%, 15–25%, >25%), all known at entry. No realized holding-duration control is used. Each matched cell and arm receives equal weight; uncertainty clusters its weighted influence by date. This is an observational sensitivity, not causal identification:

| system | n | cells | delta | se | lo | hi | se126 | p | q_bh |
|---|---|---|---|---|---|---|---|---|---|
| GA6 | 21.00000 | 10.00000 | -0.13100 | NA | NA | NA | NA | NA | NA |
| GA7 | 4.00000 | 2.00000 | 0.08534 | NA | NA | NA | NA | NA | NA |
| GA8 | 377.00000 | 52.00000 | -0.00621 | 0.00681 | -0.01956 | 0.00715 | 0.00459 | 0.36222 | 0.36222 |

GA6 has only 21 matched trades and GA7 four: no usable matched inference. GA8's matched weak-minus-strong estimate changes sign relative to some raw summaries and includes zero. Sparse overlap prevents a strong incremental market-condition claim.

quantile_deciles.csv reports within-family empirical breadth deciles separately for each MA, retaining ties and dropping duplicate quantile boundaries. These bins are descriptive and learned on the evaluated sample, not executable entry thresholds. breadth_deciles.csv provides the complementary **fixed 10-percentage-point breadth bands**, despite its legacy filename. Counts/dates, win rates and mean returns accompany each; bands are not equal-population quantiles. MA50 quantile details:

| system | quantile_decile | n | dates | mean_return | win_rate |
|---|---|---|---|---|---|
| GA6 | (0.173, 0.419] | 63.00000 | 21.00000 | 0.03338 | 0.53968 |
| GA6 | (0.419, 0.486] | 57.00000 | 16.00000 | 0.05006 | 0.77193 |
| GA6 | (0.486, 0.558] | 60.00000 | 14.00000 | 0.03195 | 0.71667 |
| GA6 | (0.558, 0.614] | 66.00000 | 16.00000 | 0.02694 | 0.60606 |
| GA6 | (0.614, 0.694] | 53.00000 | 20.00000 | 0.03085 | 0.62264 |
| GA6 | (0.694, 0.74] | 63.00000 | 20.00000 | 0.00945 | 0.57143 |
| GA6 | (0.74, 0.797] | 58.00000 | 17.00000 | 0.01425 | 0.62069 |
| GA6 | (0.797, 0.824] | 58.00000 | 12.00000 | 0.02034 | 0.55172 |
| GA6 | (0.824, 0.863] | 68.00000 | 14.00000 | -0.00131 | 0.51471 |
| GA6 | (0.863, 0.96] | 50.00000 | 14.00000 | 0.04366 | 0.66000 |
| GA7 | (0.146, 0.288] | 31.00000 | 11.00000 | 0.00740 | 0.45161 |
| GA7 | (0.288, 0.366] | 16.00000 | 7.00000 | 0.00167 | 0.37500 |
| GA7 | (0.366, 0.438] | 23.00000 | 11.00000 | 0.01029 | 0.34783 |
| GA7 | (0.438, 0.486] | 25.00000 | 14.00000 | -0.00331 | 0.24000 |
| GA7 | (0.486, 0.542] | 27.00000 | 14.00000 | 0.00719 | 0.48148 |
| GA7 | (0.542, 0.622] | 20.00000 | 14.00000 | -0.00891 | 0.20000 |
| GA7 | (0.622, 0.681] | 22.00000 | 18.00000 | -0.01416 | 0.09091 |
| GA7 | (0.681, 0.736] | 28.00000 | 18.00000 | -0.00925 | 0.21429 |
| GA7 | (0.736, 0.809] | 18.00000 | 15.00000 | 0.00120 | 0.33333 |
| GA7 | (0.809, 0.944] | 24.00000 | 16.00000 | -0.00288 | 0.33333 |
| GA8 | (0.062299999999999994, 0.333] | 156.00000 | 63.00000 | 0.00965 | 0.57692 |
| GA8 | (0.333, 0.443] | 149.00000 | 67.00000 | -0.00854 | 0.42282 |
| GA8 | (0.443, 0.506] | 171.00000 | 53.00000 | -0.00749 | 0.35088 |
| GA8 | (0.506, 0.57] | 141.00000 | 55.00000 | -0.00595 | 0.36879 |
| GA8 | (0.57, 0.603] | 133.00000 | 37.00000 | -0.00463 | 0.33835 |
| GA8 | (0.603, 0.646] | 168.00000 | 55.00000 | -0.00061 | 0.44048 |
| GA8 | (0.646, 0.684] | 134.00000 | 40.00000 | -0.00532 | 0.42537 |
| GA8 | (0.684, 0.734] | 146.00000 | 52.00000 | 0.00314 | 0.45890 |
| GA8 | (0.734, 0.785] | 167.00000 | 55.00000 | 0.00180 | 0.47305 |
| GA8 | (0.785, 0.936] | 132.00000 | 56.00000 | -0.00012 | 0.43182 |

## Does breadth improve decisions?

For each selected GA6/7 chromosome/fold, choose among five MAs × low/high direction using **training completed trades only**, at that training sample's median breadth. Require >=20 kept training trades, maximize mean net return, then freeze MA, direction and threshold before testing. decision_value.csv records all nonempty test slots. No future thresholds or replacement chromosome are selected. All training choices happened to prefer lower breadth; this is an observed result, not a coded requirement.

| system | n | kept | skipped | base_mean | kept_mean | base_pnl | kept_pnl | delta | se | lo | hi | se126 | p | q_bh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GA6 | 596.00000 | 411.00000 | 185.00000 | 0.02514 | 0.02850 | 135843.92609 | 104670.83217 | 0.01082 | 0.01086 | -0.01046 | 0.03210 | 0.01118 | 0.31907 | 0.42126 |
| GA7 | 234.00000 | 195.00000 | 39.00000 | -0.00082 | -0.00012 | -1150.40196 | 349.85597 | 0.00420 | 0.00522 | -0.00604 | 0.01444 | 0.00436 | 0.42126 | 0.42126 |

The delta/interval compare kept versus skipped trades; base_mean and kept_mean show the change relative to all original trades. GA6 improves average trade return in 7/9 active slots; GA7 has only four active slots, two with <=7 trades. These selected-trade comparisons do **not** replay freed cash, capacity, later order competition, portfolio drawdown or position sizing. kept_pnl is an arithmetic subset of the original hypothetical ledger, not a counterfactual portfolio. No evidence here establishes improved executable risk-adjusted decisions. No filter is recommended for deployment.

## Deliverables, checks and constraints

trades.csv is the auditable CSV, also supplied as trades.csv.gz: chromosome_id, system (GA), ticker, entry/exit dates, fold/year, original pnl, acquisition_cost, net_return, MAE/proxy/method and prior-close breadth/derivatives/denominators. entry_features.csv gives the independent feature calendar. candidate rankings, pool hashes, selection, fold support, correlations, bootstrap, deciles, matched comparisons, per-year results, decision checks and global corrections are machine-readable companions.

Four tests cover causal prefix invariance and prior-close timing, training-score invariance to future NAV mutation, original fill-cycle return/count/fold reconciliation, and scaled partial-exit accounting. tests.log records the result. metadata.json hashes inputs and code, with selected source-ledger hashes and original pool inventory hashes. The earlier source_hashes.json and GA8 inventory provide original fold provenance.

Computation was bounded to a 20-minute budget: main selection/accounting/statistics took 13.6 seconds; supplementary block bootstrap and checks took additional seconds/minutes. The overall work finished within the budget; no full 12,831-genome rerun, new search, remote data acquisition or inaccessible data reconstruction was attempted. The fresh replay attempt is explicitly blocked as above. All created/edited artifacts are under this experiment. No MTS/GA or live-system code, configuration or database was changed.

Reproduce from repository root with `/opt/mts/.venv/bin/python`:

```sh
/opt/mts/.venv/bin/python experiments/top_chromosome_spy_breadth_replay_20261031/study.py
/opt/mts/.venv/bin/python experiments/top_chromosome_spy_breadth_replay_20261031/supplement.py
/opt/mts/.venv/bin/python -m unittest discover -s experiments/top_chromosome_spy_breadth_replay_20261031 -p test_study.py -v
/opt/mts/.venv/bin/python experiments/top_chromosome_spy_breadth_replay_20261031/report.py
```

verify_replay.py is optional and currently fails on the inaccessible upstream import; it is not part of the passing test command. No predictive or production certification is made.
