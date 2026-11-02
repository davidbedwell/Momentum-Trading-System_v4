# Daily PIT screening delivery — 2026-10-29

Controlling source: `/opt/mts/ga9/GA9_CODEX_DIRECTIVE.md`, final daily-screen and
GA8 handoff updates. Work was restricted to GA9; existing GA8 edits were preserved.
No GA8 process was signaled, suspended, restarted or modified. No long GA ran.
Git metadata is read-only in this environment; no commit was attempted.

Implemented full eligible-universe daily momentum/trend shortlist, followed by
learned ETF-relative net-edge candidate ranking in the existing shared-capital
allocator. Decisions include screen membership and momentum score. Own historical
prices may precede membership; peer ranks/breadth exclude ineligible stocks.
Historical membership CSV supports dated additions, removals and re-entry, with
known-at validation. Raw prices remain available for held-position accounting.
Removal triggers next-open exit; a queued buy fails if membership has ended.
Shortlist disappearance alone does not force sale: native management, edge and
opportunity-cost forecasts still govern positions.

Primary SPY/QQQ choice, input hashes, screen policy and membership hash are frozen
before each forward fold. Stock and membership hashes are checked before forward.
The complete-universe buy-and-hold diagnostic stays independent of the shortlist.
Chronological expanding folds and hard absolute 8% acceptance remain unchanged.

Validation command:

```
/opt/mts/.venv/bin/python -m unittest ga9.test_screening ga9.test_benchmarks ga9.test_objective ga9.test_execution
```

31 tests passed. Coverage includes daily shortlist changes, truncated-prefix and
future-mutation invariance, historical peer exclusion, membership exit, next-open
fills, positive-edge deployment/abstention, matured-label chronology, frozen ETF
identity across both profiles, full-universe secondary, cash/dividend accounting,
exact 8% boundary and rejection/retention of breached candidates.

Bounded synthetic pilot command:

```
/opt/mts/.venv/bin/python -m ga9.synthetic_pilot --output ga9/artifacts/daily_screen_synthetic_20261029_v2
```

One generation, four candidates, five-second search limit per fold, seed 90079,
horizons 5/20/60. Completed in 2.63 seconds. STOP file and cooperative SIGTERM
apply to the GA9 runner only. Ledger/freeze/benchmark/risk verification passed.

| Forward year | Net CAGR | SPY excess pp | Absolute MDD | Fills | Distinct shortlists |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2023 | 6.12% | +1.03 | 0.0096% | 37 | 5 |
| 2024 | 3.20% | -1.89 | 0.0956% | 41 | 6 |
| 2025 | 5.83% | +0.74 | 0.0055% | 38 | 4 |

All forward risk gates passed; the overall study failed because 2024 had negative
ETF excess. These are engineered synthetic prices, not investment evidence or a
claim of real-market profitability. Independent historical membership provenance,
verified sectors, SGOV execution prices and dividend payment dates remain missing.
Without a membership CSV, the fixed supplied cohort is explicitly unverified for
historical survivorship. Missing held/delisting marks fail rather than inventing a
terminal payout. Benchmark sleeves retain holdings after membership removal under
the declared buy-and-hold policy; no retrospective sleeve redistribution occurs.

Artifacts: `ga9/artifacts/daily_screen_synthetic_20261029_v2/run/` contains manifests,
frozen models, selection/rejection logs, daily ledgers, fills, daily rankings,
controls, ablations, discrimination, ETF and complete-universe diagnostics.
The first attempt at `daily_screen_synthetic_20261029/` is retained: it failed
serializing an unavailable control screen score. The logger now records null for
unavailable scores; the second attempt completed. No outcome-based tuning occurred.
