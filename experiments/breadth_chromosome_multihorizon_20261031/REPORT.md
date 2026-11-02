# DEV79 multihorizon breadth and chromosome entries

Executed 2026-11-01. This follow-up compares all five MA horizons; SMA50 is one hypothesis among 35 fixed feature specifications. No trading code or original experiment file was changed.

**Result:** 8 of 210 identity-sample comparisons pass pooled BH q≤0.05; 1 pass Bonferroni. These are exploratory associations conditional on the archived sample, not validated entry filters. Identity-sample BH discoveries by outcome: return 0, win rate 0, close-path MAE proxy 8. Winner diagnostics have 11 BH discoveries among 315 comparisons. The global adjustment covers 525 finite tests across both sets, systems, features and outcomes.

## Sample and missing records

271,606 closed trades were assembled; 271,606 have all 35 features. All 817 GA6/GA7 selected ledgers are present. Original common cohort: 400 GA6 and 12,431 GA7 identities. The bounded identity sample includes all GA6 and the original identity-ordered GA7 sample; extra retrospectively top-ranked identities retain their own overlapping label. Unexamined cohort members are not zero-trade records. The audit records 68 GA6 and 16 GA7 ledgers with zero completed trades, distinctly from absent ledgers. These identities cannot contribute within-trade slopes. No survivorship correction can be inferred from this sample.

| system | n | eligible |
| --- | --- | --- |
| GA6 | 130256 | 130256 |
| GA7 | 139853 | 139853 |
| GA8 | 1497 | 1497 |

GA8 uses 1,497 reconstructed closed trades from three selected annual production models (2023–2025). The original report records pre-year training cutoffs; these models were not chosen here for their forward returns. The shared `retrospective_top` bucket is a selected-model diagnostic label for GA8, not a claim of forward-performance selection. Eleven open positions were excluded by the upstream reconstruction. Each model appears in only one year, so model and year effects cannot be separated; this is not repeated-chromosome replication. Family attribution follows the entry gene even for positions subsequently added/reduced. These are selected-model diagnostics, not an identity sample.

## Definitions and inference

Breadth is the eligible cross-sectional fraction strictly above SMA10/20/50/100/200. Full trailing observations and at least 20 constituents are required. Features are lagged to the prior SPY session close; no price filling. Changes and finite-difference acceleration use 5/10/21 sessions. Velocity equals change divided by horizon and is exported but excluded from duplicate testing. All horizons use the same complete-feature sample. There is no threshold search. Some specifications are algebraically related (for example five-session acceleration combines five- and ten-session changes); they are correlated tests, not independent signals.

Trade-weighted estimates can be dominated by active chromosomes. Each feature is evaluated separately after demeaning both predictor and outcome within chromosome × entry year. The coefficient is per one within-cell standard deviation. Year and chromosome level differences are removed, but unobserved time-varying confounding remains. Calendar-month clustered t intervals preserve contemporaneous cross-sectional duplication; dependence across months and long overlapping holdings may remain. Intervals are marginal month-cluster intervals. Daily influence-score Bartlett HAC at 63 and 126 sessions supplies overlap sensitivity, including zero-trade sessions. Discovery p is conservatively the maximum of the monthly, HAC63 and HAC126 p-values; q and Bonferroni apply globally to these conjunction p-values. HAC SEs and p-values are exported. BH dependence assumptions are not proven here; Bonferroni supplies the stricter safeguard across correlated specifications. No coefficient is an online fitted prediction or an independent causal effect of that horizon.

GA6/GA7 return outcome `r` is the archive’s risk-unit multiple, not percentage trade return. Risk denominators differ across policies and extreme multiples can influence mean slopes; no outlier-robust return claim is made. GA8 `r` is reconstructed net return on total invested capital, so coefficients must not be pooled across systems. Win is positive net P&L. **Fill-level MAE is absent.** We evaluate `close_mae_proxy`: minimum adjusted-close return from entry close through exit close, including zero at entry, with complete positive observed prices. This omits intraday lows/stops and scale-weighted exposure; same-day episodes have zero proxy despite possible losses. It is not actual trade MAE. Positive coefficients mean less adverse close-path excursion. Missing proxy observations are excluded explicitly; the count is in run_metadata.json. True MAE requires entry fills, intratrade price paths and a documented treatment of additions, exits and stops.

## Strongest identity-sample associations (including nonsignificant rows)

| system | feature | outcome | n | effect | lo | hi | q_bh | p_bonferroni |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GA7 | b50 | close_mae_proxy | 101708 | -0.00087257 | -0.0012809 | -0.00046426 | 0.0069466 | 0.027786 |
| GA6 | a200_21 | close_mae_proxy | 130256 | -0.0058513 | -0.0087414 | -0.0029612 | 0.014743 | 0.13268 |
| GA7 | d200_21 | close_mae_proxy | 101708 | -0.00076279 | -0.0011753 | -0.00035023 | 0.019389 | 0.21328 |
| GA6 | d50_21 | close_mae_proxy | 130256 | -0.005693 | -0.0086701 | -0.0027158 | 0.019653 | 0.25549 |
| GA7 | b100 | close_mae_proxy | 101708 | -0.00079188 | -0.0012245 | -0.00035924 | 0.019653 | 0.24169 |
| GA6 | d200_21 | close_mae_proxy | 130256 | -0.0060802 | -0.0089558 | -0.0032046 | 0.030802 | 0.4953 |
| GA6 | d200_5 | close_mae_proxy | 130256 | -0.0042445 | -0.0066663 | -0.0018226 | 0.030802 | 0.52363 |
| GA6 | d100_21 | close_mae_proxy | 130256 | -0.0052962 | -0.0083021 | -0.0022903 | 0.034232 | 0.65041 |
| GA7 | b20 | close_mae_proxy | 101708 | -0.00062988 | -0.0010399 | -0.00021991 | 0.071232 | 1 |
| GA6 | d200_10 | close_mae_proxy | 130256 | -0.0042969 | -0.0066668 | -0.001927 | 0.098214 | 1 |
| GA6 | b20 | close_mae_proxy | 130256 | -0.0046732 | -0.0074545 | -0.0018919 | 0.1057 | 1 |
| GA7 | b200 | close_mae_proxy | 101708 | -0.00071946 | -0.0011999 | -0.00023905 | 0.11531 | 1 |
| GA7 | d100_21 | close_mae_proxy | 101708 | -0.00068548 | -0.0011765 | -0.00019442 | 0.11806 | 1 |
| GA6 | d20_21 | close_mae_proxy | 130256 | -0.0038899 | -0.0064905 | -0.0012892 | 0.1214 | 1 |
| GA7 | d50_21 | close_mae_proxy | 101708 | -0.00066651 | -0.0011082 | -0.00022484 | 0.1214 | 1 |

## Cross-year and family robustness

All annual, family and chromosome coefficients are exported in heterogeneity.csv; within_year_detail.csv additionally reports each chromosome-year and family-year slope (descriptive; no discovery p-values). They retain chromosome-year controls and require 30 trades. Sign shares count groups equally and can be unstable for sparse groups. Leave-one-year-out results refit the same fixed specification and restandardize in each retained sample. They test sensitivity, not untouched holdout performance.

| system | feature | outcome | year_groups | year_same_sign_share | family_same_sign_share | chromosome_same_sign_share | loyo_min | loyo_max | loyo_sign_stable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GA7 | b50 | close_mae_proxy | 10 | 1 | 1 | 0.7574 | -0.00095652 | -0.00079896 | True |
| GA6 | a200_21 | close_mae_proxy | 10 | 0.8 | 1 | 0.87261 | -0.0063015 | -0.0046345 | True |
| GA7 | d200_21 | close_mae_proxy | 10 | 0.9 | 0.92857 | 0.73373 | -0.00083302 | -0.00060058 | True |
| GA6 | d50_21 | close_mae_proxy | 10 | 1 | 1 | 0.90764 | -0.0066782 | -0.0050554 | True |
| GA7 | b100 | close_mae_proxy | 10 | 0.9 | 0.92857 | 0.75148 | -0.0008952 | -0.00068659 | True |
| GA6 | d200_21 | close_mae_proxy | 10 | 1 | 0.92308 | 0.88217 | -0.0066139 | -0.0051303 | True |
| GA6 | d200_5 | close_mae_proxy | 10 | 0.9 | 0.92308 | 0.85987 | -0.0046577 | -0.0038013 | True |
| GA6 | d100_21 | close_mae_proxy | 10 | 0.9 | 1 | 0.88854 | -0.0062448 | -0.0047822 | True |
| GA7 | b20 | close_mae_proxy | 10 | 1 | 0.85714 | 0.73373 | -0.00069537 | -0.00051233 | True |
| GA6 | d200_10 | close_mae_proxy | 10 | 1 | 0.92308 | 0.88217 | -0.0045953 | -0.0040692 | True |
| GA6 | b20 | close_mae_proxy | 10 | 0.9 | 1 | 0.86943 | -0.0056083 | -0.0037132 | True |
| GA7 | b200 | close_mae_proxy | 10 | 0.9 | 0.85714 | 0.71006 | -0.00091084 | -0.00063003 | True |
| GA7 | d100_21 | close_mae_proxy | 10 | 0.8 | 0.92857 | 0.75148 | -0.00079857 | -0.0005288 | True |
| GA6 | d20_21 | close_mae_proxy | 10 | 0.8 | 0.92308 | 0.83439 | -0.004648 | -0.0032409 | True |
| GA7 | d50_21 | close_mae_proxy | 10 | 0.8 | 0.85714 | 0.73373 | -0.00084093 | -0.00049144 | True |

## Interpretation of the risk-proxy findings

No return or win-rate comparison survives BH correction. The clearest identity-sample risk-proxy association is GA7 SMA50 breadth: one within-cell SD (18.18 breadth percentage points) corresponds to 0.0873 percentage points more negative close-path excursion (effect −0.000873, BH q=0.00695, Bonferroni p=0.0278). Its direction is negative in all ten years and all 14 families, in 75.7% of 169 chromosomes with sufficient descriptive support, and in every leave-one-year-out fit. This is the only identity-sample result surviving Bonferroni. Higher breadth here accompanies slightly worse close-path excursion, not improved profitability.

GA6 21-session SMA50 breadth change also has a negative proxy slope (−0.569 percentage points per 25.77-point change SD), with the same sign in all ten years and 13 families, BH q=0.0197 but Bonferroni p=0.255. Other BH findings involve SMA100/200 levels, changes and acceleration. None supports treating SMA50 as the sole signal. All significant identity-sample proxy effects are negative. Correlated chromosomes do not constitute independent replications. Proxy associations may reflect holding duration, stock selection, stop/exit policy and market recovery exposure; realized holding duration is not controlled here. They warrant fresh validation using fill-level MAE and historically valid universes, not deployment.

## Selected-model diagnostics

| system | feature | outcome | n | effect | lo | hi | q_bh |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GA7 | b50 | close_mae_proxy | 39475 | -0.0010364 | -0.0014554 | -0.0006175 | 0.00208 |
| GA7 | b100 | close_mae_proxy | 39475 | -0.00099213 | -0.0014206 | -0.00056368 | 0.0036088 |
| GA6 | a200_21 | close_mae_proxy | 5258 | -0.0066656 | -0.009538 | -0.0037932 | 0.0063426 |
| GA6 | d50_21 | close_mae_proxy | 5258 | -0.0069674 | -0.010211 | -0.0037236 | 0.0074712 |
| GA6 | d100_21 | close_mae_proxy | 5258 | -0.0071494 | -0.010372 | -0.0039263 | 0.0074712 |
| GA6 | d200_21 | close_mae_proxy | 5258 | -0.0070578 | -0.010064 | -0.0040516 | 0.0087917 |
| GA7 | d200_21 | close_mae_proxy | 39475 | -0.00081988 | -0.0012463 | -0.00039341 | 0.014743 |
| GA7 | b20 | close_mae_proxy | 39475 | -0.0007743 | -0.0011857 | -0.00036287 | 0.017041 |
| GA7 | b200 | close_mae_proxy | 39475 | -0.0011991 | -0.0018522 | -0.00054597 | 0.019968 |
| GA6 | a100_21 | close_mae_proxy | 5258 | -0.0061423 | -0.0096212 | -0.0026633 | 0.030802 |

## Limits and reproducibility

**Temporal causality is enforced, but certified point-in-time DEV79 membership and historical adjustment vintages are unavailable.** This is a fixed retrospective universe with current-vintage adjusted closes, subject to survivorship/revision bias. No broad-market or deployable claim follows. Correlated horizons, repeated trades across chromosomes, retrospective selection, only ten GA6/GA7 entry years and three GA8 years limit evidence. A significant pooled association alone is insufficient to call a robust relationship; examine the year/family/chromosome and leave-one-year-out tables before forming a fresh validation hypothesis.

Run from repository root:
```sh
OPENBLAS_NUM_THREADS=1 /opt/mts/.venv/bin/python experiments/breadth_chromosome_multihorizon_20261031/study.py
OPENBLAS_NUM_THREADS=1 /opt/mts/.venv/bin/python experiments/breadth_chromosome_multihorizon_20261031/supplement.py
OPENBLAS_NUM_THREADS=1 /opt/mts/.venv/bin/python experiments/breadth_chromosome_multihorizon_20261031/within_year_detail.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_multihorizon_20261031/check_features.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_multihorizon_20261031/report.py
/opt/mts/.venv/bin/python experiments/breadth_chromosome_multihorizon_20261031/validate_results.py
```

Inputs and code hashes/package versions are in run_metadata.json; per-ledger hashes are in ledger_audit.csv. selection_snapshot.csv preserves the original selection. entry_features.csv exports breadth, eligibility denominators and all derivative features; trades_with_features.csv.gz is the reproducible joined ledger. cohort_coverage.csv distinguishes the 12,014 unexamined GA7 identities from missing/observed ledgers; coverage.csv reports exclusions, pooled_results.csv all tests, and robustness_summary.csv all sign/leave-year summaries. Feature checks verify prior-close alignment, prefix invariance under future price changes, missing-window eligibility and exact velocity rescaling. The protocol was fixed before outcome estimation; GA8 was added when its extracted ledger became available before estimation. FOLLOWUP_NOTE.md documents the later addition of close-path proxy analysis and synchronization with the finalized original GA8 accounting before follow-up outcome inspection. The original REPORT.md is hashed and its sample limitations carry forward.
