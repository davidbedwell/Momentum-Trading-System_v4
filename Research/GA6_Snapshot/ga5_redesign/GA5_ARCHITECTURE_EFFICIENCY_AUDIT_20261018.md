# GA5 Architecture and Efficiency Audit — 2026-10-18
Status: AUDITED; PRODUCTION LAUNCH NOT AUTHORIZED. No GA5 evolutionary jobs restarted.
Scope: /opt/mts GA5 modules, parallel runner, redesign and 79-stock OHLCV data.

## Executive decision
FAIL for scientific end-to-end completeness. FAIL for computational deduplication. PASS for current unit/regression tests (56 passed); these tests do not certify trading research.

## Research coverage
- Data: 394,795 rows, 79 tickers, 2004-09-01 through 2026-09-14; no null cells in stored raw columns. Historical universe PIT membership and delistings NOT verified.
- GA4 feature families: eight implemented as prototypes. Sector is NaN when no sector map supplied; any chromosome selecting sector is non-evaluable in current runner. Breadth and relative strength are computed from the restricted 79-stock set, not certified full-market PIT universe.
- Genome: entry, hold, exit, regime, sizing, replacement, stop, trailing stop, hold duration and risk budget represented. Regime-specific cooperative portfolio selection and independent risk policy NOT integrated.
- Niches: seven protected niches in ga5_redesign/optimizer_v3.py, but old parallel runner still imports ga5_evolution_pilot.run, all growth-only. New evolve() explicitly raises NotImplementedError.
- Main evolutionary evaluation: ga5_chromosome_portfolio_pilot.evaluate uses mts_next_open_ledger_v1.Ledger, not corporate action ledger; no T+1 settlement, SGOV cash yield, verified PIT earnings embargo or independent veto.
- Next-open decisions are implemented; 10bps fee is default. Fee alone does not establish full trading friction model.
- Earnings embargo and SGOV rotation exist as separate components and have unit tests, but are not wired into main evolutionary evaluator.
- No walk-forward/OOS, independent market episodes, BLIND17 final blind or promotion certification in the active GA5 runner.
- 35% CAGR is a research target, not an enforced threshold or verified performance.

## Computational inefficiency and duplication
P0: 8 workers read same parquet independently, calculate same feature transforms independently, and start same growth seed on same data. Different RNG seeds are not distinct scientific folds.
P0: ga5_chromosome_portfolio_pilot.evaluate copies and sorts entire prepared frame for EVERY genome and reconstructs daily rows/groupbys, adding high repeated Python overhead. No memoization of identical genome evaluations.
P0: old runner bypasses redesign and can launch incomplete experiment without science preflight.
P1: checkpoints write growing complete history every generation; repeated serialization and disk I/O. Redesign diagnostic has no resume/checkpoint.
P1: no shared work ledger keyed by genome identity, data fingerprint, evaluator version, costs, and validation fold; same genome can be evaluated redundantly.
P1: mutation small local steps and only within niche; no measured novelty/fitness improvement early stop, no adaptive allocation of compute among niches.
P1: 8 parallel workers are CPU-saturating but CPU utilization is not the same as productive throughput.
P1: multiple independent ledger prototypes and replay entrypoints are not unified; inconsistent corporate action/settlement assumptions risk incomparable results.
P2: risk-aware fitness currently a scalar heuristic with no robustness, trade count, statistical confidence, regime diversity, tail-risk or OOS penalty.
P2: current diagnostic runner uses production-size generation targets without workload calibration or fixed scientific test budgets.

## Required corrective sequence (no restart)
1. Freeze requirements and acceptance criteria: PIT universe, no lookahead, fees, settlement, corporate actions, earnings embargo, SGOV, independent veto, folds/blind, niche objectives, promotion criteria.
2. Build ONE canonical execution/evaluation engine, with strict fail-closed validation of mandatory PIT inputs and trading policies. Retire alternative runner entrypoints from production.
3. Precompute market features once per data/fold version; share read-only feature store across workers (memory map / shared file); reuse date index and aligned numeric arrays. Ensure point-in-time sector and breadth.
4. Build global evaluation cache with keys including genome identity, market/fold fingerprint, engine version and policy version; cache results across workers and resumed runs.
5. Implement protected niches with separate objectives, population breadth, elitism, diversity checks, novelty monitoring and measured stagnation policies; support inter-niche portfolio composition without cross-niche genetic contamination.
6. Add chronological walk-forward, crash-episode tests, DEV transport, reserved DEV50 where appropriate, and final untouched BLIND17. Avoid leakage from reusing selection periods.
7. Add atomic checkpoint/restart and append-only compact history; deterministic seeds, manifest hashes, audit logs, baseline benchmarks.
8. Benchmark 1, 2, 4 and 8 worker throughput on identical representative full-history workload; compare evaluations per CPU-hour and duplicated evaluations; run full production only after integration and certification preflight pass.

## Evidence
Modules inspected: ga5_parallel_diagnostic_runner.py, ga5_evolution_pilot.py, ga5_redesign/optimizer_v3.py, ga5_chromosome_contract.py, ga5_feature_families.py, ga5_feature_adapter.py, ga5_chromosome_decisions.py, ga5_chromosome_portfolio_pilot.py, ga5_corporate_action_ledger.py, ga5_sgov_rotation_contract.py, ga5_earnings_entry_embargo.py, ga5_portfolio_replay.py, mts_next_open_ledger_v1.py.
Test log: /opt/mts/ga5_redesign/full_audit_tests.log (56 passed).
No scientific certification is claimed.
