# Stage 2 machine-semantic search audit — 2026-10-08

Status: **FAIL / NOT SCIENTIFICALLY CERTIFIED**. Read-only review, no paid GA or protected-bank access.

- Eight available families: MOMENTUM, BREAKOUT, TREND, MEAN_REVERSION, VOLATILITY, VOLUME_LIQUIDITY, RELATIVE_CROSS_SECTIONAL, MARKET_REGIME_STRUCTURE. Their nominal single-family search products range from 528 to 13,824; product counts are not unique executable phenotypes because inactive genes and equivalent predicates can collide.
- Genetics: 1–4 chromosome combinations, random initialization, gene mutation, family injection, crossover, uniqueness checks. No Stage 1 five-state label requirement found in these modules.
- **Blocking defect:** `scripts/run_ga4_parallel_dev80.py` calls `evaluate_conditional_candidate` without `side`, defaulting to LONG. Independent SHORT discovery is absent from the active runner, despite evaluator SHORT support.
- **Blocking uncertainty:** `CausalSignalCompiler.qthreshold` uses only prior-date observations, but quantile history pools all previously observed stock rows, not necessarily a frozen PIT market universe. Verify eligibility, contemporaneous universe composition and feature timestamps.
- **Blocking uncertainty:** Stage 2 cost/path code uses T+1 adjusted open paths and prospective costs, but source-adjustment PIT fidelity, short borrow/locate assumptions, market-shock-dependent uncertainty and full end-to-end leakage tests remain unverified.
- **Known statistical limitation:** `stage2_evaluator_v3` clusters by security-year, not independent crash/market episodes; its LCB is not certified for shared market shocks.
- **Predicate check:** ABOVE, BELOW, HIGH, LOW, LEADER, LAGGARD, POSITIVE and NEGATIVE all return 3 matches on a 5-row [-2,-1,0,1,2] toy vector at zero. No LOW/LAGGARD defect.
- The optional Stage 1 integration test passed with and without human context (399,691 DEV80 rows); this is not scientific certification.

Required before paid GA: implement and test independent LONG/SHORT discovery with side-specific identities/evidence; prove PIT feature and universe causality; test selection and outcome leakage; certify cost assumptions and market-episode dependence; benchmark throughput only after these repairs. Preserve original checkpoints and protected partitions. New run ID and source hashes mandatory.
