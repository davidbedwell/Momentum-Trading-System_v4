# Follow-up SPY R-1 combination study

Executed 2026-10-31. Exploratory historical evidence, not an untouched validation or a deployable trading result. All CSV returns/drawdowns/effects are decimal fractions; 0.01 = one percentage point.

## Main result
Rolling annual selection chose **weak&stabilization** in all 14 evaluation years (2012–2025). Its mean 21-session SPY return was **3.51%**, versus 1.26% unconditional, 2.94% for weak breadth alone and 0.97% for positive SPY 63-session momentum. Uplift versus unconditional was 2.25% (marginal 95% HAC CI [0.71%, 3.80%], BH q=0.0297, Bonferroni p=1.0000). Versus momentum, uplift was 2.54%, CI [0.87%, 4.22%], q=0.0225.

**The combination does not establish incremental value over weak breadth alone:** 21-session uplift 0.57%, CI [-0.74%, 1.87%], q=0.6351. Its return difference-in-differences interaction was 0.93%, CI [-0.83%, 2.68%], q=0.7211. Thus the apparent combination advantage is consistent with the already-inspected weak-breadth rebound association. No robust additional predictive contribution is established.

The selected state had 133 signal dates, 46 runs and only 25 greedily spaced 21-session windows. These are dependence diagnostics, not certified independent events. Mean 21-session forward maximum drawdown was -4.55% versus -3.55% unconditional (effect -1.00%, CI [-2.09%, 0.10%]). A larger expected rebound does not establish reduced path risk.

## Source findings and new hypotheses
Read [SOURCES.md](SOURCES.md) for the inspected files and provenance distinctions. The requested historical `MTS_V4/recovery.py` actually handles checkpoint evidence continuity, not market R-1. Frozen recovery protocols are descriptive morphology research, explicitly disallowing trough-based operational signals and threshold fitting at that stage. Surviving reconciled findings report variable ordering of destruction, impulse, breadth conversion, persistence, failed-rebound improvement, trend repair and stress normalization. Original named comparison result artifacts were not located; their reconciled numerical findings were not independently reproduced here.

Historical descriptor construction was found in a separate script (read only; never executed). It supplies breadth velocity/acceleration/persistence and damage/impulse proxies, not a unique Boolean market R-1 implementation. **R1_proxy in this experiment is a newly defined, incomplete hypothesis**, not a reproduced historical R-1 strategy. It combines recent damage, positive impulse, breadth conversion and persistence, and EMA20 repair. It omits actual failed rebounds and external VIX/VVIX/OFR stress. Its thresholds and same-date conjunction are simplifications that can miss the variable ordering described by the sources.

Local Claude-labeled six-signal and pair/triple studies were found and inspected; these are monthly DEV79 stock-selection studies, not SPY market-state studies. A Grok chromosome audit was found and inspected; it is a software/design critique, not SPY evidence. No original Claude/Grok SPY prediction study was located in the bounded local search. No attributed SPY result is invented.

## Causal design and chronology
Exact definitions and selection are in [PROTOCOL.md](PROTOCOL.md); feature and signal series are exported. Weak breadth: <40% of eligible DEV79 stocks above trailing SMA50. Improving: +10 percentage points over 21 sessions. Persistence: SPY above EMA20 on at least four of five sessions with positive five-session return. Stabilization: RV20 no greater than five sessions earlier. Momentum: positive trailing 63-session return. All use close t and earlier only, with full required observations and >=20 eligible stocks; no filling. R1_proxy uses a trailing 252-session drawdown reaching -15% in the last 63 sessions, not knowledge of a future trough.

Expanding training starts in 2006, selects the largest positive 21-session combination uplift subject to >=100 dates and >=15 runs using only outcomes completed before each evaluation year, then holds the rule fixed for that year. Evaluation covers 2012–2025. Outcomes crossing every year boundary are purged at each horizon, including the pooled fixed-rule analysis. 2026 is excluded. Because earlier research inspected 2017–2025 and old recovery episodes, chronological ordering does **not** remove human selection contamination. These are rolling historical evaluations, not untouched OOS. All rolling choices happened to agree, so their signal equals the fixed weak/stabilization combination.

## Returns and forward drawdown by horizon
Forward return is adjusted close t+h / close t - 1. Drawdown is worst close peak-to-trough over t..t+h, including interim peaks. Intraday risk is omitted. A close-t predictor is not assumed executable at that same close; delay-one sensitivity is reported. No portfolio profitability or cost claim is made.
| horizon | metric | n | onsets | nonoverlap_n | mean | baseline_mean | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|---|---|
| 5.00000 | return | 135.00000 | 47.00000 | 50.00000 | 0.00892 | 0.00304 | 0.00589 | -0.00255 | 0.01432 | 0.36507 |
| 5.00000 | drawdown | 135.00000 | 47.00000 | 50.00000 | -0.02116 | -0.01367 | -0.00749 | -0.01276 | -0.00222 | 0.03481 |
| 10.00000 | return | 135.00000 | 47.00000 | 34.00000 | 0.01685 | 0.00594 | 0.01090 | 0.00087 | 0.02093 | 0.13282 |
| 10.00000 | drawdown | 135.00000 | 47.00000 | 34.00000 | -0.03250 | -0.02246 | -0.01004 | -0.01691 | -0.00318 | 0.02950 |
| 21.00000 | return | 133.00000 | 46.00000 | 25.00000 | 0.03511 | 0.01258 | 0.02253 | 0.00709 | 0.03797 | 0.02968 |
| 21.00000 | drawdown | 133.00000 | 46.00000 | 25.00000 | -0.04548 | -0.03551 | -0.00997 | -0.02094 | 0.00100 | 0.22527 |
| 63.00000 | return | 98.00000 | 35.00000 | 16.00000 | 0.06692 | 0.03622 | 0.03070 | -0.01441 | 0.07581 | 0.37766 |
| 63.00000 | drawdown | 98.00000 | 35.00000 | 16.00000 | -0.07902 | -0.06454 | -0.01448 | -0.04091 | 0.01195 | 0.51097 |

## Component and momentum comparisons
Each of 22 combinations is compared with each of its own component rules, unconditional SPY and SPY momentum on common feature eligibility. All six components are also reported. This is a difference in conditional outcome means, not an exposure-matched portfolio alpha.
| comparator | metric | mean | baseline_mean | effect | ci_low | ci_high | q | bonferroni |
|---|---|---|---|---|---|---|---|---|
| unconditional | return | 0.03511 | 0.01258 | 0.02253 | 0.00709 | 0.03797 | 0.02968 | 1.00000 |
| unconditional | drawdown | -0.04548 | -0.03551 | -0.00997 | -0.02094 | 0.00100 | 0.22527 | 1.00000 |
| unconditional | downside | 0.21805 | 0.30440 | -0.08636 | -0.20774 | 0.03502 | 0.35326 | 1.00000 |
| momentum | return | 0.03511 | 0.00966 | 0.02545 | 0.00865 | 0.04225 | 0.02254 | 1.00000 |
| momentum | drawdown | -0.04548 | -0.03147 | -0.01401 | -0.02563 | -0.00239 | 0.08438 | 1.00000 |
| momentum | downside | 0.21805 | 0.31490 | -0.09686 | -0.22938 | 0.03566 | 0.33567 | 1.00000 |
| weak | return | 0.03511 | 0.02943 | 0.00568 | -0.00738 | 0.01873 | 0.63512 | 1.00000 |
| weak | drawdown | -0.04548 | -0.04869 | 0.00320 | -0.01025 | 0.01666 | 0.83587 | 1.00000 |
| weak | downside | 0.21805 | 0.24000 | -0.02195 | -0.11558 | 0.07167 | 0.83727 | 1.00000 |
| stabilization | return | 0.03511 | 0.01070 | 0.02441 | 0.00998 | 0.03884 | 0.00907 | 0.98879 |
| stabilization | drawdown | -0.04548 | -0.03384 | -0.01165 | -0.02202 | -0.00127 | 0.11756 | 1.00000 |
| stabilization | downside | 0.21805 | 0.31693 | -0.09888 | -0.21786 | 0.02009 | 0.26557 | 1.00000 |

## All fixed rules: 21-session return
Do not rank by q-value: rare-state HAC intervals can be severely overconfident. `fragile=True` means fewer than 20 runs or 20 nonoverlap windows. For example, weak/improving/persistence has only one nonoverlap window, and weak/persistence/momentum only three. Their tiny asymptotic p-values are unreliable and do not support conclusions. Weak/improving averages 5.25% but has only 32 dates, 11 runs and nine windows.
| rule | n | onsets | nonoverlap_n | fragile | mean | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|---|
| weak&improving | 32.00000 | 11.00000 | 9.00000 | True | 0.05250 | 0.03993 | 0.01135 | 0.06850 | 0.03846 |
| weak&improving&stabilization | 29.00000 | 9.00000 | 7.00000 | True | 0.04994 | 0.03736 | 0.00623 | 0.06850 | 0.08615 |
| weak&persistence&momentum | 7.00000 | 4.00000 | 3.00000 | True | 0.04620 | 0.03362 | 0.02324 | 0.04400 | 0.00000 |
| weak&stabilization | 133.00000 | 46.00000 | 25.00000 | False | 0.03511 | 0.02253 | 0.00709 | 0.03797 | 0.02968 |
| weak&improving&persistence | 8.00000 | 2.00000 | 1.00000 | True | 0.03223 | 0.01966 | 0.01404 | 0.02527 | 0.00000 |
| weak&persistence | 21.00000 | 9.00000 | 7.00000 | True | 0.03133 | 0.01876 | 0.00537 | 0.03214 | 0.03784 |
| weak&persistence&stabilization | 15.00000 | 6.00000 | 4.00000 | True | 0.03029 | 0.01771 | 0.00102 | 0.03440 | 0.14484 |
| weak | 525.00000 | 86.00000 | 57.00000 | False | 0.02943 | 0.01685 | 0.00959 | 0.02411 | 0.00009 |
| stabilization&R1_proxy | 59.00000 | 24.00000 | 13.00000 | True | 0.02565 | 0.01308 | -0.00175 | 0.02790 | 0.23850 |
| improving&R1_proxy | 53.00000 | 22.00000 | 11.00000 | True | 0.02519 | 0.01262 | -0.00176 | 0.02699 | 0.23914 |
| R1_proxy | 75.00000 | 29.00000 | 14.00000 | True | 0.02518 | 0.01261 | -0.00001 | 0.02522 | 0.17220 |
| R1_proxy&persistence&stabilization | 58.00000 | 24.00000 | 13.00000 | True | 0.02465 | 0.01207 | -0.00371 | 0.02785 | 0.31203 |
| persistence&R1_proxy | 71.00000 | 29.00000 | 14.00000 | True | 0.02340 | 0.01083 | -0.00327 | 0.02492 | 0.30960 |
| weak&momentum | 138.00000 | 61.00000 | 32.00000 | False | 0.02027 | 0.00769 | -0.00657 | 0.02196 | 0.51739 |
| momentum&R1_proxy | 41.00000 | 19.00000 | 10.00000 | True | 0.01413 | 0.00155 | -0.01349 | 0.01659 | 0.93806 |
| improving | 1054.00000 | 152.00000 | 91.00000 | False | 0.01083 | -0.00175 | -0.00671 | 0.00322 | 0.72294 |
| stabilization | 1666.00000 | 238.00000 | 136.00000 | False | 0.01070 | -0.00188 | -0.00474 | 0.00098 | 0.39817 |
| improving&stabilization | 839.00000 | 162.00000 | 84.00000 | False | 0.00991 | -0.00267 | -0.00835 | 0.00302 | 0.60314 |
| momentum | 2496.00000 | 81.00000 | 137.00000 | False | 0.00966 | -0.00292 | -0.00626 | 0.00043 | 0.24168 |
| persistence | 1532.00000 | 241.00000 | 129.00000 | False | 0.00923 | -0.00335 | -0.00607 | -0.00063 | 0.07673 |
| weak&stabilization&momentum | 19.00000 | 13.00000 | 10.00000 | True | 0.00912 | -0.00345 | -0.03641 | 0.02951 | 0.93806 |
| persistence&stabilization | 1058.00000 | 248.00000 | 114.00000 | False | 0.00894 | -0.00364 | -0.00689 | -0.00039 | 0.11780 |
| improving&persistence | 733.00000 | 166.00000 | 82.00000 | False | 0.00849 | -0.00409 | -0.00922 | 0.00104 | 0.28658 |
| persistence&momentum | 1370.00000 | 227.00000 | 120.00000 | False | 0.00766 | -0.00492 | -0.00852 | -0.00132 | 0.04440 |
| stabilization&momentum | 1336.00000 | 210.00000 | 116.00000 | False | 0.00737 | -0.00521 | -0.00879 | -0.00163 | 0.02968 |
| improving&momentum | 792.00000 | 151.00000 | 80.00000 | False | 0.00610 | -0.00648 | -0.01197 | -0.00099 | 0.09311 |
| weak&R1_proxy | 4.00000 | 2.00000 | 1.00000 | True | 0.02021 | NA | NA | NA | NA |
| weak&improving&momentum | 0.00000 | 0.00000 | 0.00000 | True | NA | NA | NA | NA | NA |

## Interaction tests
Pair conjunctions do not by themselves demonstrate interaction. `interactions.csv` reports E[Y|11]-E[Y|10]-E[Y|01]+E[Y|00] with a paired calendar HAC influence calculation, cell counts and a separate multiplicity family. No causal interpretation follows from this observational contrast.
| horizon | metric | cell_counts | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|
| 5.00000 | return | [135, 410, 1647, 1258] | 0.00233 | -0.00939 | 0.01406 | 0.82677 |
| 5.00000 | drawdown | [135, 410, 1647, 1258] | 0.00134 | -0.00833 | 0.01102 | 0.89217 |
| 5.00000 | downside | [135, 410, 1647, 1258] | 0.03426 | -0.09741 | 0.16593 | 0.82568 |
| 10.00000 | return | [135, 398, 1620, 1227] | 0.00610 | -0.00789 | 0.02009 | 0.73835 |
| 10.00000 | drawdown | [135, 398, 1620, 1227] | 0.00346 | -0.00984 | 0.01676 | 0.82568 |
| 10.00000 | downside | [135, 398, 1620, 1227] | -0.01487 | -0.17868 | 0.14894 | 0.91494 |
| 21.00000 | return | [133, 392, 1533, 1168] | 0.00928 | -0.00826 | 0.02681 | 0.72107 |
| 21.00000 | drawdown | [133, 392, 1533, 1168] | 0.00400 | -0.01321 | 0.02120 | 0.82677 |
| 21.00000 | downside | [133, 392, 1533, 1168] | -0.04926 | -0.17935 | 0.08083 | 0.74989 |
| 63.00000 | return | [98, 310, 1272, 958] | -0.00205 | -0.03468 | 0.03058 | 0.93667 |
| 63.00000 | drawdown | [98, 310, 1272, 958] | -0.00284 | -0.02625 | 0.02057 | 0.89217 |
| 63.00000 | downside | [98, 310, 1272, 958] | 0.05005 | -0.13204 | 0.23214 | 0.82568 |

## Robustness
For years with signals, 21-session unconditional uplift was positive in 9 of 12 years. This descriptive sign count uses conditional sample means even when fewer than five observations prevent inference, ignores overlap and is not a sign-test p-value. Leave-one-year-out 21-session uplift versus weak breadth ranged [0.02%, 0.85%]; inspect all intervals in robustness.csv. Crisis exclusion removes 2020 and 2022 from the evaluation sample. Breadth .35/.45 are fixed sensitivities, not a tuned winner.
| variant | comparator | n | onsets | nonoverlap_n | effect | ci_low | ci_high |
|---|---|---|---|---|---|---|---|
| lag126 | unconditional | 133.00000 | 46.00000 | 25.00000 | 0.02253 | 0.00677 | 0.03829 |
| lag126 | weak | 133.00000 | 46.00000 | 25.00000 | 0.00568 | -0.00778 | 0.01914 |
| delay1 | unconditional | 133.00000 | 46.00000 | 25.00000 | 0.02442 | 0.01019 | 0.03866 |
| delay1 | weak | 133.00000 | 46.00000 | 25.00000 | 0.00743 | -0.00383 | 0.01870 |
| weak35 | unconditional | 102.00000 | 36.00000 | 19.00000 | 0.03063 | 0.01650 | 0.04475 |
| weak35 | weak | 102.00000 | 36.00000 | 19.00000 | 0.00969 | -0.00376 | 0.02313 |
| weak45 | unconditional | 189.00000 | 67.00000 | 34.00000 | 0.01421 | -0.00046 | 0.02888 |
| weak45 | weak | 189.00000 | 67.00000 | 34.00000 | 0.00146 | -0.01036 | 0.01328 |
| exclude_crisis | unconditional | 80.00000 | 31.00000 | 18.00000 | 0.01140 | -0.00825 | 0.03105 |
| exclude_crisis | weak | 80.00000 | 31.00000 | 18.00000 | -0.00379 | -0.02100 | 0.01342 |

Additional paired circular moving-block bootstrap checks (1,000 replicates per contrast, deterministic seed; 63/126-session blocks) are descriptive marginal percentile intervals, not selection-adjusted inference. They resample paired outcomes and signals and preserve dependence within blocks; rare-state bootstrap remains imperfect.
| comparator | metric | block | replicates | ci_low | ci_high |
|---|---|---|---|---|---|
| unconditional | return | 63.00000 | 1000.00000 | 0.00478 | 0.03723 |
| unconditional | return | 126.00000 | 1000.00000 | 0.00376 | 0.03661 |
| unconditional | drawdown | 63.00000 | 1000.00000 | -0.02241 | 0.00104 |
| unconditional | drawdown | 126.00000 | 1000.00000 | -0.02419 | 0.00011 |
| weak | return | 63.00000 | 1000.00000 | -0.01082 | 0.01795 |
| weak | return | 126.00000 | 1000.00000 | -0.01270 | 0.01696 |
| weak | drawdown | 63.00000 | 1000.00000 | -0.01048 | 0.01647 |
| weak | drawdown | 126.00000 | 1000.00000 | -0.01126 | 0.01608 |
| momentum | return | 63.00000 | 1000.00000 | 0.00713 | 0.04162 |
| momentum | return | 126.00000 | 1000.00000 | 0.00606 | 0.04138 |
| momentum | drawdown | 63.00000 | 1000.00000 | -0.02867 | -0.00268 |
| momentum | drawdown | 126.00000 | 1000.00000 | -0.02809 | -0.00310 |

## Inference and limits
Pooled fixed-rule tests use one BH/Bonferroni family across all rules, comparators, four horizons and three outcomes: 1080 finite contrasts. Annual results form a separate family of 7278 finite contrasts; interactions and rolling-policy contrasts each form separate families. Sensitivity tests are separately adjusted across the full sensitivity table; the displayed sensitivity intervals are marginal, not simultaneous. BH under dependent tests has limited FDR guarantees; Bonferroni is more conservative. Undefined or <5-date contrasts retain NA, not zero p-values. HAC lag max(63,2h), lag126 sensitivity and calendar-aligned influence scores address overlap approximately, not rare-event asymptotics or selection bias. Rolling-policy inference does not model model-selection uncertainty.

**DEV79 historical survivorship limitation:** a fixed retrospective universe and current-vintage adjusted prices cannot establish point-in-time broad-market breadth. Constituent selection and adjustment revisions can contaminate historical generalization even though the feature functions are temporally causal. This study is conditional on that panel. DEV87 was attempted at the prior source path and is unavailable with permission denied; cross-universe robustness remains untested. No independent price certification was attempted. Source hashes, coverage and data-quality statistics are exported.

## Reproduction and artifacts
Run from the workspace:
```sh
/opt/mts/.venv/bin/python experiments/spy_r1_combinations_20261031/study.py
/opt/mts/.venv/bin/python experiments/spy_r1_combinations_20261031/bootstrap.py
/opt/mts/.venv/bin/python -m pytest -q experiments/spy_r1_combinations_20261031/test_study.py
/opt/mts/.venv/bin/python experiments/spy_r1_combinations_20261031/report.py
```
Tests cover future-data perturbation, prefix invariance, missing-input propagation, conjunction construction, outcome drawdown arithmetic, annual purging and paired inference. See tests.log. CSVs: results, annual_results, rolling_selections, rolling_results, interactions, robustness, bootstrap, features, signals, outcomes and data_quality. run_metadata.json and source_hashes.json preserve provenance. No GA, MTS modifications, external model calls, paid data, commits or publication.
