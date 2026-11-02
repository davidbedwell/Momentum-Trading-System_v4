# Independent SPY state prediction study

Executed 2026-10-31. All returns, effects, probabilities and drawdowns below are decimal fractions; 0.01 = 1 percentage point.

## Result
Discovery selected **DEV79_breadth50_weak**, direction +1, 21-session discovery uplift 1.0892%. Validation 21-session uplift 1.5673%, 95% HAC CI [0.6968%, 2.4378%], p=0.0004171, BH q=0.025108. Frozen validation criterion **PASSES** under BH; more conservative Bonferroni p=0.085089. This is one chronological historical holdout, not evidence of future profitability.

## Interpretation
The selected state is fewer than 40% of eligible DEV79 stocks above their trailing 50-session average. It occurred on 392 validation signal dates, in 61 runs, with only 38 greedily spaced 21-session windows. Its 21-session negative-return probability was 28.06% versus 29.81%; the difference is not significant. Mean maximum forward drawdown was worse: −5.60% versus −3.89% (effect −1.71 percentage points; BH q=0.0439). This is a rebound-return association with greater path risk. Versus positive 63-session momentum, return uplift was +1.74 points but BH q=0.0841, so adjusted evidence for improvement over momentum is insufficient. The lag-126 sensitivity interval for return uplift is [+0.84, +2.30] points. Discovery itself was noisy (21-session return BH q=0.433); selection did not require discovery significance.

Yearly uplift was positive in all eight validation years with signals; 2017 had no weak-breadth signals. That is descriptive and uses overlapping labels. The downtrend subgroup had a positive marginal interval; the uptrend and volatility-expansion subgroup intervals included zero. At 10 bps one way the secondary state-only strategy earned 4.34% CAGR versus 8.53% for simple momentum and 15.04% for buy-and-hold; exposure was only 17.3%. No deployable trading advantage is established.

## Data and scope
{
  "SPY": {
    "path": "/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet",
    "sha256": "b182402afd15c074ee4cc596149bf0a821e6cbd00fa5329d84eef269636f6381",
    "rows": 5459,
    "start": "2005-01-03 00:00:00",
    "end": "2026-09-15 00:00:00"
  },
  "DEV79": {
    "path": "/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet",
    "sha256": "7eb869d0059dd976705c9673c5098d611b38c4970645168a28882fe15c055e0a",
    "rows": 394795,
    "start": "2004-09-01 00:00:00",
    "end": "2026-09-14 00:00:00",
    "tickers": 79
  },
  "DEV87": {
    "path": "/opt/mts/thunder-migration/mts-certification-20261011/dev87/dev87_raw.parquet",
    "unavailable": "[Errno 13] Permission denied: '/opt/mts/thunder-migration/mts-certification-20261011/dev87/dev87_raw.parquet'"
  }
}

DEV79 is the requested dev80_raw_no_smci panel (file label differs from universe name). DEV87 source read and requested copy fallback both failed with permission denied. It was not fabricated or substituted. Cross-universe robustness therefore remains untested. Original Claude/Grok transcripts were unavailable; the fixed rules operationalize the hypotheses enumerated by the user.

**DEV universes are retrospective and survivorship-biased.** Current-vintage adjusted histories and retrospective security selection prevent a point-in-time universe claim. Adjustment revisions can affect historical features; no historical-vintage correction is available. Breadth uses eligible current/complete trailing observations only, with minimum 20 stocks; no filling. Prices are asserted positive and keys unique. data_quality.csv records missingness and large daily moves without filtering them. Daily vendor data are not independently certified.

## Design and inference
See PROTOCOL.md and study.py for exact rules. Discovery 2006–2016; validation 2017–2025. Outcomes are purged at each split end; 2026 never enters analysis. 2005 supplies warmup, so 200-session breadth may start later. No validation tuning. All rule results, including failures, are in results.csv. Daily signal counts, onsets and greedy nonoverlap counts are reported; neither onsets nor nonoverlap counts guarantee independent samples. No causal interpretation.

17 fixed states; 204 tests per split/comparator. BH q-values adjust across all states × four horizons × three outcomes separately per split/comparator. Bonferroni adjusted p-values are also in results.csv as a conservative dependence-robust comparison. Only finite p-values enter BH (actual family sizes in run_metadata.json); zero-variance identical comparator contrasts have undefined p-values. Dependence may limit BH FDR guarantees. HAC influence-function normal CIs use Bartlett lag max(63,2h), preserving calendar gaps; they are marginal and approximate, especially for rare states. Lag-126 sensitivity appears in sensitivity_lag126.csv. Selection on discovery is optimistic; validation is not used to change selection. Comparator-specific eligibility makes unconditional baselines potentially differ by rule.

Forward return is adjusted close t+h / close t − 1. Downside is return <0. Maximum forward drawdown is worst peak-to-trough across t..t+h, including interim peaks; daily closes omit intraday losses. adverse in outcomes.csv separately records worst close relative to entry. Features use close t and earlier only. Predictive close-t labels assume no ability to trade after seeing that same close.

## Selected rule: untouched validation vs unconditional
| horizon | metric | n | onsets | nonoverlap_n | mean | baseline_mean | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|---|---|
| 5.00000 | return | 392.00000 | 61.00000 | 105.00000 | 0.00744 | 0.00307 | 0.00437 | 0.00010 | 0.00864 | 0.20510 |
| 5.00000 | downside | 392.00000 | 61.00000 | 105.00000 | 0.33929 | 0.37439 | -0.03511 | -0.10109 | 0.03088 | 0.57205 |
| 5.00000 | drawdown | 392.00000 | 61.00000 | 105.00000 | -0.02569 | -0.01491 | -0.01077 | -0.01780 | -0.00375 | 0.04388 |
| 10.00000 | return | 392.00000 | 61.00000 | 63.00000 | 0.01278 | 0.00611 | 0.00667 | 0.00007 | 0.01327 | 0.21113 |
| 10.00000 | downside | 392.00000 | 61.00000 | 63.00000 | 0.31633 | 0.33037 | -0.01405 | -0.08774 | 0.05965 | 0.88637 |
| 10.00000 | drawdown | 392.00000 | 61.00000 | 63.00000 | -0.03972 | -0.02443 | -0.01530 | -0.02596 | -0.00464 | 0.04960 |
| 21.00000 | return | 392.00000 | 61.00000 | 38.00000 | 0.02854 | 0.01286 | 0.01567 | 0.00697 | 0.02438 | 0.02511 |
| 21.00000 | downside | 392.00000 | 61.00000 | 38.00000 | 0.28061 | 0.29808 | -0.01747 | -0.10309 | 0.06815 | 0.88483 |
| 21.00000 | drawdown | 392.00000 | 61.00000 | 38.00000 | -0.05603 | -0.03893 | -0.01710 | -0.02838 | -0.00583 | 0.04388 |
| 63.00000 | return | 385.00000 | 57.00000 | 18.00000 | 0.06764 | 0.03787 | 0.02976 | 0.00264 | 0.05689 | 0.16540 |
| 63.00000 | downside | 385.00000 | 57.00000 | 18.00000 | 0.21818 | 0.23147 | -0.01329 | -0.12499 | 0.09841 | 0.91567 |
| 63.00000 | drawdown | 385.00000 | 57.00000 | 18.00000 | -0.09020 | -0.07338 | -0.01682 | -0.03214 | -0.00151 | 0.16540 |

## Selected rule: validation vs simple positive 63-session momentum
| horizon | metric | n | baseline_n | mean | baseline_mean | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|---|
| 5.00000 | return | 392.00000 | 1748.00000 | 0.00744 | 0.00277 | 0.00467 | -0.00006 | 0.00940 | 0.31964 |
| 5.00000 | downside | 392.00000 | 1748.00000 | 0.33929 | 0.36442 | -0.02513 | -0.09755 | 0.04729 | 0.85913 |
| 5.00000 | drawdown | 392.00000 | 1748.00000 | -0.02569 | -0.01181 | -0.01388 | -0.02236 | -0.00541 | 0.04241 |
| 10.00000 | return | 392.00000 | 1743.00000 | 0.01278 | 0.00554 | 0.00724 | -0.00028 | 0.01476 | 0.31964 |
| 10.00000 | downside | 392.00000 | 1743.00000 | 0.31633 | 0.31784 | -0.00152 | -0.08962 | 0.08659 | 0.98615 |
| 10.00000 | drawdown | 392.00000 | 1743.00000 | -0.03972 | -0.01986 | -0.01986 | -0.03256 | -0.00717 | 0.05516 |
| 21.00000 | return | 392.00000 | 1732.00000 | 0.02854 | 0.01113 | 0.01740 | 0.00543 | 0.02937 | 0.08411 |
| 21.00000 | downside | 392.00000 | 1732.00000 | 0.28061 | 0.28233 | -0.00172 | -0.10777 | 0.10433 | 0.98615 |
| 21.00000 | drawdown | 392.00000 | 1732.00000 | -0.05603 | -0.03292 | -0.02311 | -0.03657 | -0.00965 | 0.02934 |
| 63.00000 | return | 385.00000 | 1690.00000 | 0.06764 | 0.03186 | 0.03578 | -0.00292 | 0.07447 | 0.33572 |
| 63.00000 | downside | 385.00000 | 1690.00000 | 0.21818 | 0.22189 | -0.00371 | -0.16070 | 0.15328 | 0.98615 |
| 63.00000 | drawdown | 385.00000 | 1690.00000 | -0.09020 | -0.06768 | -0.02253 | -0.04395 | -0.00111 | 0.26009 |

## Discovery ranking (21-session return; selection-eligible)
| rule | n | onsets | mean | baseline_mean | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|
| DEV79_breadth50_weak | 547.00000 | 78.00000 | 0.01806 | 0.00717 | 0.01089 | -0.00236 | 0.02414 | 0.43253 |
| negative_momentum_expansion | 261.00000 | 41.00000 | -0.00074 | 0.00717 | -0.00791 | -0.03764 | 0.02182 | 0.98372 |
| vol_contraction | 721.00000 | 65.00000 | 0.00188 | 0.00717 | -0.00529 | -0.01553 | 0.00495 | 0.81234 |
| DEV79_fragile_trend | 183.00000 | 46.00000 | 0.01071 | 0.00717 | 0.00354 | -0.01312 | 0.02020 | 0.98372 |
| DEV79_breadth200_weak | 402.00000 | 25.00000 | 0.00432 | 0.00717 | -0.00285 | -0.02983 | 0.02413 | 0.98372 |
| DEV79_healthy_trend | 1177.00000 | 116.00000 | 0.00499 | 0.00717 | -0.00218 | -0.00920 | 0.00484 | 0.98372 |
| vol_expansion | 562.00000 | 63.00000 | 0.00543 | 0.00717 | -0.00175 | -0.01569 | 0.01220 | 0.98372 |
| DEV79_breadth50_strong | 1590.00000 | 133.00000 | 0.00557 | 0.00717 | -0.00161 | -0.00649 | 0.00328 | 0.98372 |
| acceleration_positive | 1244.00000 | 186.00000 | 0.00876 | 0.00717 | 0.00159 | -0.00399 | 0.00716 | 0.98372 |
| DEV79_recovery | 262.00000 | 58.00000 | 0.00875 | 0.00717 | 0.00158 | -0.01405 | 0.01722 | 0.98372 |

## All states: validation 21-session return
| rule | n | onsets | mean | baseline_mean | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|
| momentum63_positive | 1732.00000 | 39.00000 | 0.01113 | 0.01286 | -0.00173 | -0.00620 | 0.00275 | 0.71372 |
| momentum21_positive | 1574.00000 | 82.00000 | 0.00970 | 0.01286 | -0.00317 | -0.00590 | -0.00044 | 0.13256 |
| acceleration_positive | 1065.00000 | 135.00000 | 0.01187 | 0.01286 | -0.00100 | -0.00625 | 0.00426 | 0.88637 |
| vol_expansion | 416.00000 | 35.00000 | 0.01036 | 0.01286 | -0.00250 | -0.01975 | 0.01474 | 0.90078 |
| vol_contraction | 624.00000 | 51.00000 | 0.01401 | 0.01286 | 0.00114 | -0.00654 | 0.00883 | 0.90078 |
| momentum_acceleration | 823.00000 | 124.00000 | 0.00926 | 0.01286 | -0.00361 | -0.00989 | 0.00267 | 0.54677 |
| negative_momentum_expansion | 142.00000 | 19.00000 | 0.02801 | 0.01286 | 0.01514 | -0.01260 | 0.04288 | 0.57102 |
| DEV79_breadth50_strong | 1288.00000 | 103.00000 | 0.00954 | 0.01286 | -0.00332 | -0.00770 | 0.00105 | 0.40256 |
| DEV79_breadth50_weak | 392.00000 | 61.00000 | 0.02854 | 0.01286 | 0.01567 | 0.00697 | 0.02438 | 0.02511 |
| DEV79_breadth200_strong | 1608.00000 | 55.00000 | 0.00978 | 0.01286 | -0.00309 | -0.00783 | 0.00166 | 0.49342 |
| DEV79_breadth200_weak | 217.00000 | 21.00000 | 0.04735 | 0.01286 | 0.03449 | 0.00891 | 0.06007 | 0.07000 |
| DEV79_breadth_improving | 728.00000 | 102.00000 | 0.00880 | 0.01286 | -0.00407 | -0.01052 | 0.00239 | 0.50736 |
| DEV79_breadth_deteriorating | 785.00000 | 103.00000 | 0.01790 | 0.01286 | 0.00504 | -0.00002 | 0.01010 | 0.21230 |
| DEV79_divergence | 272.00000 | 82.00000 | 0.01576 | 0.01286 | 0.00290 | -0.00551 | 0.01130 | 0.75464 |
| DEV79_recovery | 160.00000 | 26.00000 | 0.01742 | 0.01286 | 0.00455 | -0.02101 | 0.03011 | 0.89330 |
| DEV79_healthy_trend | 972.00000 | 95.00000 | 0.01138 | 0.01286 | -0.00148 | -0.00811 | 0.00515 | 0.86498 |
| DEV79_fragile_trend | 151.00000 | 34.00000 | 0.00506 | 0.01286 | -0.00781 | -0.02880 | 0.01319 | 0.72588 |

## Regime diagnostics
Causal trend is SPY relative to trailing 200-session average; volatility expansion is trailing 20/60 realized volatility >1.2. Regimes are descriptive, not independent tests or selection inputs. Calendar years are in regimes.csv.
| rule | regime | n | baseline_n | mean | effect | ci_low | ci_high |
|---|---|---|---|---|---|---|---|
| DEV79_breadth50_weak | validation_uptrend | 173.00000 | 1852.00000 | 0.02135 | 0.01026 | -0.00084 | 0.02137 |
| DEV79_breadth50_weak | validation_downtrend | 219.00000 | 389.00000 | 0.03422 | 0.01289 | 0.00070 | 0.02509 |
| DEV79_breadth50_weak | validation_vol_expansion | 155.00000 | 416.00000 | 0.02879 | 0.01843 | -0.00081 | 0.03767 |
| DEV79_breadth50_weak | validation_no_expansion | 237.00000 | 1825.00000 | 0.02837 | 0.01494 | 0.00521 | 0.02467 |
| momentum63_positive | validation_uptrend | 1683.00000 | 1852.00000 | 0.01193 | 0.00084 | -0.00129 | 0.00297 |
| momentum63_positive | validation_downtrend | 49.00000 | 389.00000 | -0.01607 | -0.03739 | -0.10166 | 0.02687 |
| momentum63_positive | validation_vol_expansion | 274.00000 | 416.00000 | 0.00122 | -0.00914 | -0.02637 | 0.00808 |
| momentum63_positive | validation_no_expansion | 1458.00000 | 1825.00000 | 0.01300 | -0.00044 | -0.00416 | 0.00329 |

## Secondary cost-aware strategy
Long/cash only. State at close t executes close t+1; earliest earned return is t+1 to t+2. Bearish selected state means cash inside state and long outside. Missing signals remain cash; inspect daily exposure. No leverage; cash return zero, no tax, market impact or borrowing. Costs are 5/10/25 bps one way including entry and liquidation. Sharpe uses zero cash benchmark. Strategy summaries are descriptive, not additional confirmatory evidence.
| rule | one_way_bps | exposure | turnover | cagr | annual_vol | sharpe | max_drawdown |
|---|---|---|---|---|---|---|---|
| buy_hold | 5.00000 | 1.00000 | 2.00000 | 0.15051 | 0.18481 | 0.85151 | -0.33717 |
| buy_hold | 10.00000 | 1.00000 | 2.00000 | 0.15039 | 0.18481 | 0.85090 | -0.33717 |
| buy_hold | 25.00000 | 1.00000 | 2.00000 | 0.15000 | 0.18482 | 0.84907 | -0.33717 |
| momentum63_positive | 5.00000 | 0.77498 | 78.00000 | 0.08999 | 0.11521 | 0.80592 | -0.30059 |
| momentum63_positive | 10.00000 | 0.77498 | 78.00000 | 0.08526 | 0.11526 | 0.76790 | -0.30550 |
| momentum63_positive | 25.00000 | 0.77498 | 78.00000 | 0.07118 | 0.11551 | 0.65340 | -0.32004 |
| DEV79_breadth50_weak | 5.00000 | 0.17330 | 122.00000 | 0.05049 | 0.13643 | 0.42941 | -0.28352 |
| DEV79_breadth50_weak | 10.00000 | 0.17330 | 122.00000 | 0.04337 | 0.13649 | 0.37943 | -0.28854 |
| DEV79_breadth50_weak | 25.00000 | 0.17330 | 122.00000 | 0.02227 | 0.13681 | 0.22952 | -0.30548 |

## Reproduce
Run `/opt/mts/.venv/bin/python experiments/spy_state_predictor_20261031/study.py`, then `/opt/mts/.venv/bin/python -m pytest -q experiments/spy_state_predictor_20261031/test_study.py`. Inputs remain external; SHA256 and coverage are in run_metadata.json. No MTS code changed, no GA, no paid data, no push. Tests and execution log are stored alongside outputs.
