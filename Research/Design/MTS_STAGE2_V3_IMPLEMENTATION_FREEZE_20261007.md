# MTS Stage 2 V3 Implementation Freeze — 2026-10-07
Status: FROZEN BEFORE V3 CALIBRATION/PRODUCTION OUTCOMES

This document implements, and does not replace, `MTS_STAGE2_CORRECTED_PREREGISTRATION_V2_20261007.md` plus its full-path horizon amendment. V2 production never ran; its matched-search calibration is classified `ENGINEERING_CALIBRATION_INVALID` because the target was never visited and a day-20 plant was compared against candidates selecting among unrelated horizons.

## Certified source dependency
V3 vendors the recovered `MTS_V4` Python source package plus the approved cost engine under `Reconstruction/Certified-Stage2-Source-20261007/`. `SHA256SUMS` is controlling. The recovered feature factory, family grammar, signal compiler semantics, and GA mechanics are source-of-truth; V3 optimizations require executable equivalence tests against those sources.

## Causal feature availability
The eight certified families remain: MOMENTUM, BREAKOUT, TREND, MEAN_REVERSION, VOLATILITY, VOLUME_LIQUIDITY, RELATIVE_CROSS_SECTIONAL, MARKET_REGIME_STRUCTURE. EVENT_EARNINGS remains excluded. `forward_horizon` is removed from the genotype and replaced by the full 1..63 path phenotype already frozen.

Three recovered feature values are excluded before search for data-governance reasons, not because of outcomes:
- `turnover__v1` and `turnover_relative_20__v1`: DEV117 lacks point-in-time shares outstanding; coverage is zero.
- `sector_return_252_percentile__v1`: the only stock-to-sector map recovered is static 2026 metadata. Backblaze and repository searches found no point-in-time historical stock-sector map. Static sector identity may be used for reporting/stratification, never as a historical predictive input. Stage 3 requires an explicit PIT-sector solution before sector-conditioned inference.
All other recovered predictor columns have approximately 95-100% DEV117 coverage.

## Feature computation
Stock-local predictors use the recovered `derived_feature_factory.py` exactly. For compute only, stock-local work may run in spawned workers; recovered cross-sectional percentile/breadth/relative-strength semantics are reconstructed after merge. An executable oracle-equivalence test must match the monolithic recovered factory. V3 signal masks use a vectorized compiler with exact recovered threshold/interpolation arithmetic; an executable randomized oracle-equivalence test must match recovered `_compile_signal` bit-for-bit across all eight families.

## Executable outcome path
A decision observation is at close T. Hypothetical execution enters at T+1 open, consistent with the approved execution freeze. Every integer holding interval h=1..63 is measured from adjusted T+1 open to adjusted T+1+h open. Adjusted intraday highs/lows over the held sessions produce running MAE/MFE. This path is an outcome/measurement substrate only; it is not a fixed-hold or lifecycle rule.

Each genome produces all 63 horizon phenotypes. No horizon is a genotype gene. Genome+horizon phenotypes are compared without a weighted EV/MAE exchange rate: maximize net EV and LCB95 and maximize MAE (less-negative adverse excursion). A genome remains competitive if any phenotype is nondominated. Capital-time efficiency and horizon length are descriptors only. Exact exit/lifecycle discovery remains downstream.

## Prospective transaction economics
V3 uses the approved causal cost model: decision-day HLC range spread proxy, 2-bps floor/50-bps cap; trailing-20 observed-session ADV through T; impact `10 bps * sqrt(order_notional/ADV)`; commission zero; historical SEC Section 31 + FINRA TAF on the sale leg; short borrow baseline 0.30%/yr with 1% and 3% sensitivities and actual calendar-day accrual.

The Stage-2 discovery reference notional is $100,000, matching the registered conforming engine and the frozen $100k-account research convention. The decision-date spread/ADV estimate is used prospectively for both hypothetical legs, matching the approved lifecycle-hurdle semantics. LONG and SHORT costs remain separately computed; SHORT is not an inverted LONG result.

## Calibration correction
Single-predicate baselines are exhaustive before combination evolution, so a planted primitive cannot fail merely because random initialization omitted it. Matched-search calibration must test the same recovered genome mutation/crossover mechanics and must verify target visitation explicitly. A planted effect is scored only at its declared planted horizon for recovery-power testing; it is not compared against unrelated horizons. Full-path throughput is benchmarked separately on the production evaluator. Null controls remain required. The V2 prospective budget ladder (0.25%=>8k, 0.50%=>10k, 1%=>15k, 2%=>20k evaluations per population; no recovery=>stop) is retained unless superseded by a separately frozen pre-outcome amendment.

## Protected evidence
DEV117 only for design/calibration/production search. The recurring verification-50 is selected from the repaired untouched Discovery136 only after the DEV117 frontier freezes and cannot repair/tune Stage 2. Fresh-50, Verification A and Verification B remain inaccessible. Static sector labels may be used to make the verification sample sector-proportional without viewing outcomes.

## Historical rate coverage engineering clarification (pre-V3 scientific outcomes)
The certified historical SEC Section 31 schedule starts 2005-12-22, while DEV117 history begins in 2004. Pre-schedule regulatory rates must not be invented or backfilled: leave corresponding prospective cost, and thus cost-dependent net EV, as missing. This preserves early predictor observations without promoting them as economically evaluated trades; report eligible coverage explicitly. Executable test verifies missing costs before schedule.
