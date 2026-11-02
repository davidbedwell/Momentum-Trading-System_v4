# Breadth at chromosome trade entry: archival study

Weak DEV79 breadth does **not establish a reliable profitable-entry predictor** in the available records. Small aggregate advantages coexist with changing year effects, weak matching support, broad uncertainty and retrospective chromosome selection. This is exploratory historical association, not a validated trading filter. No GA/MTS code or data were changed; no network or paid data were used.

## Inventory and what can be reproduced

`file_inventory.csv` inventories 31,522 structured artifacts (GA6 1,697; GA7 28,334; GA8 1,491), including nested repository copies. Counts are files, not unique experiments. CSV/Parquet schemas, JSON top-level fields, errors and sizes are retained. `sqlite_inventory.csv` and `sqlite_copy_inventory.csv` contain actual table schemas/counts. SQLite files requiring writable sidecars were inspected on disposable copies with their WAL, without opening source files for writing. Copies are best-effort point-in-time reads, not transactional backups of actively changing databases. The managed environment status tool was unavailable; all work stayed local.

- **GA6:** numerous incompatible native/structural/defensive runs and evaluation caches exist. The source for the common replay is `/opt/mts/ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json`: 400 saved structural candidates. All 400 common-replay ledgers were analyzed. Native daily equity, 31,019 fills and 8,218 entry feature records for 53 identities also exist under `runs/independent_review`, spanning a different 2025–2026 evaluation; they were not mixed into the common engine results. Forty-session baseline trades and selector portfolio logs are different strategies, not additional observations of these chromosomes.
- **GA7:** `/opt/mts/ga7-deploy/ga7_audit_v2/validation/handoff/frozen_cohort.json` contains 12,431 recoverable identities across 14 groups. The common replay summary has all 12,431 GA7 plus 400 GA6, status OK, each over 2,516 sessions in 2009–2018. These are saved simulations, not live executions. To bound work, analyze the first 20 sorted identities per group (280), chosen without consulting returns. Identity order need not be representative. Also analyze the saved GA7 top-ten-per-group list (140 identities) and GA6 top ten by common-replay CAGR, explicitly as retrospective descriptions. `selection.csv` records every inclusion. Total union: 817 identities, 270,109 completed trades. Entries in the union run from 2009-04-21 through 2018-03-23; nominal replay coverage is longer. No missing trades were invented.
- **GA8:** the production catalogue has 261,878 chromosome rows, 266,165 evaluations, 555 forward evidence rows and 270 replay-trade-evidence summaries. These tables contain aggregate metrics/statistics, not reconstructable dated trades. The separate GEV-PIT run has 993 chromosome rows, 1,000 evaluations and zero forward evidence; it is not interchangeable with production. The forward-all catalogue is another snapshot (202,354 identities), not a fresh replication. `forward_2023/2024/2025.jsonl` are aggregate evaluations. However, production `fold_2023.json`, `fold_2024.json`, `fold_2025.json` retain full dated fills for three saved winners. Their checkpoint records training cutoffs 2023-01-01, 2024-01-01, 2025-01-01 and next-year tests. These yield **133, 809, 555** completed position episodes; **0, 1, 10** open positions are excluded, not assumed losses or profits. Different winners each year prevent same-chromosome multi-year validation. No forward winner was selected for this study.

The chromosome pools themselves were discovered retrospectively; even the identity sample does not remove discovery/survivorship bias. GA6/GA7 top-list results are never evidence of prospective predictive power. Historical native evaluation metrics, common execution metrics and GA8 returns are kept separate.

## Definitions and controls

Reuse `spy_state_predictor_20261031/study.py:features` and its exact local SPY and DEV79 sources (hashes in `source_hashes.json`). Breadth is the fraction of available DEV79 adjusted closes strictly above their trailing 50-observation SMA, requiring 50 nonmissing observations and **at least 20** eligible stocks that day. Eligibility here means sufficient observed price history; historical membership vintages and tradability are not independently proven. DEV79 is a retrospectively chosen universe. No unavailable DEV87 data were used.

All breadth, slopes, momentum and volatility are shifted one complete SPY session: an entry uses the previous close. Weak <40%, medium 40–60% inclusive, strong >60%. Improvement means positive five-session breadth change. A crossing is from <40% to >=40%; age 0–5 and 6–21 sessions uses only the last already observed crossing. “Before the next crossing” is deliberately not assigned using future crossing dates. SPY 5/21/63-session outcomes start at entry close; SPY21 in tables is descriptive, not an entry feature.

Common execution: original 10bp fee per side, zero cash yield, 10% acquisition cap, original genome capacities/sector/risk constraints, and optimistic OHLC stop ordering. Original P&L and R are preserved. R denominators differ across evolved risk/scale policies and can produce extreme values; median R, currency P&L and win rates accompany means. P&L sums across hypothetical chromosomes are not an investable combined portfolio.

Within each chromosome, compare regimes and years (`regime_results.csv`, `chromosome_contrasts.csv`). Exact matched comparisons require the same chromosome, ticker (stronger than sector), year, momentum63 sign, annualized 20-session volatility band (<15%, 15–25%, >25%) and holding bin (0–5, 6–20, 21–40, >40). Each matched cell gets equal weight, with equal weight per arm inside the cell. Realized holding duration is a post-entry control: this is a descriptive sensitivity, not an executable selection rule. Sector names from the prior market panel are static and not claimed historically point-in-time. Ticker matching avoids relying on those names.

Uncertainty aggregates influence scores by entry date across all tickers and chromosomes, then uses Bartlett HAC with 63 business-day lags and 126-lag sensitivity. This preserves shared calendar shocks and overlapping outcomes rather than counting trades as independent. It remains an asymptotic approximation, especially poor in a single year or few crossing episodes. No independent-trade bootstrap is used. BH corrections are provided within contrast families and jointly across all reported contrasts (`all_tests.csv`); they cannot correct original genome search or all prior breadth experiments. Annual tests and top-list results remain exploratory.

## Numerical findings

Identity sample, original R (means are trade-weighted; not cross-system rankings):

| system | regime | n | entry_dates | mean_r | median_r | win_rate | spy21 |
|---|---|---|---|---|---|---|---|
| GA6 | medium | 23461 | 330 | 0.1621 | 0.1247 | 0.6383 | 0.0171 |
| GA6 | strong | 82072 | 1203 | 0.1223 | 0.0629 | 0.5649 | 0.0126 |
| GA6 | weak | 24723 | 175 | 0.1496 | 0.0329 | 0.5281 | 0.0248 |
| GA7 | medium | 21118 | 335 | 0.0894 | -0.9900 | 0.3546 | 0.0145 |
| GA7 | strong | 65148 | 1254 | -0.0222 | -1.0652 | 0.3209 | 0.0114 |
| GA7 | weak | 15442 | 175 | 0.0321 | -1.1004 | 0.3321 | 0.0258 |

Weak minus strong, with 95% overlap-aware intervals:

| system | matched | n_a | n_b | delta_r | lo | hi | q_bh |
|---|---|---|---|---|---|---|---|
| GA6 | False | 24723 | 82072 | 0.0273 | -0.2194 | 0.2739 | 0.8707 |
| GA6 | True | 1781 | 2051 | -0.0766 | -0.3751 | 0.2219 | 0.8707 |
| GA7 | False | 15442 | 65148 | 0.0543 | -0.1729 | 0.2815 | 0.8707 |
| GA7 | True | 2472 | 3670 | 0.2981 | 0.0127 | 0.5835 | 0.3095 |

GA6's raw advantage is +0.0273R but the matched estimate is −0.0766R. GA7's raw advantage is +0.0543R; the matched estimate is +0.2981R (unadjusted p=.0406), which does not survive the contrast-family correction (q=.3095). Matching retains only 3,832 GA6 and 6,142 GA7 weak/strong trades. Among identities with >=10 trades in each regime, only 42.5% of 266 GA6 and 60.7% of 145 GA7 favor weak breadth. These correlated identities are not independent replications.

Year direction is inconsistent: GA6 weak-minus-strong is +0.598R in 2009, −0.304R in 2011 and −0.112R in 2015. GA7 is −0.316R in 2010 and +0.700R in 2015. The 2017 weak-versus-strong comparison lacks support. Annual intervals/corrections are in `annual_contrasts.csv`, not evidence of a stable rule.

Improving versus nonimproving weak breadth is −0.0453R GA6 and −0.1782R GA7 raw; crossing within five sessions versus weak is −0.0279R GA6 and +0.0721R GA7. None survives correction. Strict GA6 improvement matching has only 12 trades per arm. Retrospective top-list weak/strong differences are +0.1201R GA6 and −0.1231R GA7 raw, another warning that selecting winners changes the apparent story.

GA8 completed episodes, execution-price return after commission and dividend entitlement (denominator: all acquisition expenditure, including adds; not capital-time return or R):

| year | regime | n | entry_dates | mean_net_return | win_rate | spy21 |
|---|---|---|---|---|---|---|
| 2023.0000 | medium | 28 | 22 | -0.0125 | 0.2857 | 0.0213 |
| 2023.0000 | strong | 40 | 23 | 0.0045 | 0.3750 | 0.0187 |
| 2023.0000 | weak | 65 | 40 | 0.0072 | 0.5538 | 0.0336 |
| 2024.0000 | medium | 258 | 66 | -0.0035 | 0.3953 | 0.0264 |
| 2024.0000 | strong | 514 | 152 | 0.0004 | 0.4689 | 0.0170 |
| 2024.0000 | weak | 37 | 13 | 0.0019 | 0.5135 | 0.0316 |
| 2025.0000 | medium | 218 | 86 | -0.0094 | 0.3349 | 0.0001 |
| 2025.0000 | strong | 199 | 85 | -0.0024 | 0.4020 | 0.0207 |
| 2025.0000 | weak | 138 | 46 | 0.0023 | 0.5072 | 0.0433 |

GA8 weak-minus-strong uncertainty (returns, not R):

| year | n_a | n_b | delta_r | lo | hi | q_bh |
|---|---|---|---|---|---|---|
| 2023 | 65 | 40 | 0.0027 | -0.0204 | 0.0257 | 0.8836 |
| 2024 | 37 | 514 | 0.0015 | -0.0086 | 0.0116 | 0.8836 |
| 2025 | 138 | 199 | 0.0048 | -0.0102 | 0.0197 | 0.8298 |

The weak advantage is +0.267, +0.150 and +0.476 percentage points in 2023/2024/2025; every interval includes zero. Weak-entry counts are 65, 37 and 138, covering only 40, 13 and 46 distinct entry dates. The 2023 post-crossing versus weak contrast is −1.978 percentage points (18 versus 65 episodes; GA8-family q=.0331; joint correction also remains below .05), but it is a small single-year exploratory result, with no consistent cross-year significance. The full exploratory correction is in `all_tests.csv`. Three different selected models do not prove repeatability within one chromosome.

GA8 reconstruction groups ENTRY/ADD/REDUCE/EXIT/REPLACE into full position episodes, checks quantities, includes dividends due to overnight quantity and charges 1bp commission. Fill execution prices already contain 5bp slippage, so total reported `cost` is **not** subtracted again. Partial exits are not invented independent entries. Full portfolio CAGR/MDD in `ga8_inventory.csv` includes open positions and therefore differs from completed-episode summaries.

## Separate native GA6 sensitivity

The 53-chromosome native audit has 8,218 saved entry/exit episodes from 2025-01-03 through 2026-09-09, with fills through 2026-09-14. `native_ga6_results.csv` joins the same lagged breadth to those records, preserving the saved `trade_return` and saved `mae` instead of substituting common-engine R. Selection provenance and scale/fee accounting of these derived return records are not established here; these are a separate sensitivity, not additional independent confirmation. 2026 is incomplete and is not a reserved holdout. Weak-minus-strong saved return is +2.02 percentage points in 2025 (95% HAC interval −3.63 to +7.66), and +8.26 points in 2026 (+4.73 to +11.79; unadjusted p=.00000463). The latter is a positive association in these selected records, not grounds to dismiss every breadth relationship. But 2026 weak entries cover only 14 distinct dates (367 trades); subsequent SPY21 return is 10.23% versus −1.41% for strong-entry dates. A recovery episode and retrospective selection can drive this difference. Saved MAE averages are −6.56% weak versus −7.17% strong in 2025, and −6.71% versus −9.60% in 2026. These saved MAE definitions were not independently reconstructed.

## Risk, interpretation and gaps

`risk_proxies.csv` and `ga8_risk_proxies.csv` report stock adjusted-close path adverse excursion and peak-to-trough drawdown over each observed entry/exit interval. These start at entry **close**, omit intraday stops and scale-weighted exposure, and are not fill-level MAE or portfolio MDD. One-day episodes have zero close-path excursion despite possible stop losses. Full-replay NAV MDD is retained per chromosome in `ledger_inventory.csv`; it cannot be assigned to an entry regime without inventing a portfolio allocation experiment. Costs are the saved models' assumptions, not verified realized spreads.

Weak entries also coincide with stronger subsequent SPY21 returns (e.g. GA6 2.48% versus 1.26%, GA7 2.58% versus 1.14%). This could reflect market recovery exposure; these trade-weighted SPY observations are correlated and do not establish incremental chromosome timing value. Matching on momentum/volatility reduces some confounding but does not establish causality. No association here distinguishes “start of a profitable spell” from ordinary completed-trade profitability: no spell onset was defined or inferred after seeing results.

Missing requirements for a predictive claim: a chromosome frozen before the studied years, dated native trades across multiple independent years for that same chromosome, historically vintage membership/sector/earnings eligibility, comparable cost/risk accounting, and adequate matched crossing episodes. Broad GA8 catalogue summaries cannot supply these missing trades. Additional runs or a new GA/MTS replay would go beyond this focused archival study. The defensible conclusion is insufficient evidence for a weak-breadth entry rule; neither improvement nor crossing consistently dominates.

## Reproduce and tests

Use Python 3.12 with numpy, pandas, scipy and pyarrow (available in `/opt/mts/.venv`). From repository root:

```sh
/opt/mts/.venv/bin/python experiments/breadth_chromosome_entry_20261031/study.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_entry_20261031/inventory_detail.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_entry_20261031/ga8_study.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_entry_20261031/refine.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_entry_20261031/native_ga6.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_entry_20261031/finish.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_entry_20261031/report.py
/opt/mts/.venv/bin/python -m unittest discover -s experiments/breadth_chromosome_entry_20261031 -p test_study.py -v
```

Four tests passed: exact regime boundaries; feature prefix invariance and >=20 eligibility; scaled/partial fill accounting with dividends and no doubled slippage; archived count reconciliation and strict prior-session feature dating. `tests.log` retains execution output. Source hashes cover price inputs, analyzed ledgers and GA8 folds; inventory lists discovery artifacts without pretending every historical evaluation is reproducible from aggregate metrics. Original databases may be live and counts can change on rerun. No certification or deployment claim is made.
