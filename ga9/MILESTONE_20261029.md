# GA9 real-data milestone — 2026-10-29 UTC

Historical Nasdaq-100 certification and real QQQ replay remain blocked. No synthetic
series was substituted. All work is isolated under ga9; GA8 source hashes before
and after match. No GA8 process or checkpoint was modified. Read-only status shows
production_500_20261029 RUNNING (last update 14:20:50 UTC); the separate GEV PIT run
was already STOPPED. Status is an observation, not independent process liveness.
The existing GA8 files/checkpoints remain in place for restoration.

The independent audit records 13 dated add/remove facts from the
[Nasdaq December 9, 2022 notice](https://www.nasdaq.com/press-release/annual-changes-to-the-nasdaq-100-index-2022-12-09),
effective December 19. The event CSV is deliberately NOT an executable membership
interval file: removals cannot establish original admission dates and additions
cannot establish indefinite continued eligibility. Every source-cohort ticker has
an explicit unverified starting-membership audit row. Full historical eligibility
requires a dated starting roster, all off-cycle changes, security/ticker mappings,
and bars for removed/delisted securities. Current constituent lists or annual
notices alone do not meet that requirement. DEV79 is not a Nasdaq-100 universe.

No QQQ parquet was found in the inspected local research locations. Public Yahoo
chart acquisition for 2022–2025 failed with ConnectionError; only endpoint and
exception class were recorded, without environment values or credential contents.
The cloud status tool and network-policy file were unavailable, so remote source
entitlements could not be established. No new subscription, login, or purchase was
attempted. [Invesco](https://www.invesco.com/qqq-etf/en/performance.html) provides
fund return reference figures, but those are not executable daily OHLC/action bars.
A QQQ replay still needs daily OHLC, adjusted close, distributions and splits,
source identity/hash, complete aligned sessions, split normalization checks and an
independent total-return reconciliation. Adjusted-close returns must not receive a
second dividend credit. Published NAV returns also differ from next-open execution.

A bounded **real-stock/SPY fixed-cohort** smoke completed in 20.1 seconds:

```
/opt/mts/.venv/bin/python -m ga9.run --output ga9/artifacts/real_daily_smoke_20261029 --universe-profile broad_us --generations 1 --population 4 --budget 1 --seed 90079
/opt/mts/.venv/bin/python -m ga9.verify ga9/artifacts/real_daily_smoke_20261029
```

One second is the search check budget per fold, not a total process timeout;
refits/reports finish atomically. Verification passed all three folds. The 31
existing screening/benchmark/objective/execution tests passed. This is an engineering
smoke with minimal search, not optimized evidence or independent unseen history.

| Forward year | GA9 CAGR | SPY excess pp | MDD | Exposure | Fills |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2023 | 0.00% | -25.93 | 0.00% | 0.0% | 0 |
| 2024 | 0.00% | -26.01 | 0.00% | 0.0% | 0 |
| 2025 | 3.45% | -13.93 | 4.56% | 28.3% | 604 |

No fold passes positive excess. Cash selection in the first two years and low
exposure in 2025 explain much of the participation gap; they do not establish
positive stock-selection skill. The conservative shared UNKNOWN sector cap,
positive expected-edge requirement, reserve, trading costs and short native exits
are plausible additional constraints; this run does not isolate their causality.
SPY uses the real local vendor bars with identical first-decision timing, entry
costs, receivables, and final marks. Complete-cohort equal-weight sleeves are a
secondary diagnostic, not a certified PIT Nasdaq benchmark. Daily ledgers, frozen
models, hashes, risk rejections and comparator metrics are in the smoke directory.

One controlled improvement hypothesis was tested only on 2022 training data:
widen top-k from 20 to 40, leaving all momentum/trend positivity rules, native genes,
manager and accounting unchanged. The experiment declaration was written before
replay; forward folds were not used to choose this setting. Entry signals are
screened explicitly; incumbent holding scores remain native. This diagnostic uses
the native control rather than a retrained expected-edge allocator, so it does not
establish how an evolved GA9 portfolio would respond.

| Training metric | Top 20 | Top 40 |
| --- | ---: | ---: |
| Mean shortlist after 120-session warmup | 12.93 | 16.81 |
| Zero shortlist sessions after warmup | 5/131 | 5/131 |
| CAGR | 1.47% | 0.22% |
| SPY excess pp | +20.46 | +19.21 |
| MDD | 8.36% | 8.34% |
| Exposure | 25.09% | 24.84% |
| Fills | 371 | 382 |

Widening increased available names but did not improve funded participation or
returns, and both controls breached 8% MDD. **Do not promote top 40.** Keep top 20;
no forward tuning or long optimization followed. Initial warmup accounts for 120
of the 125 full-period zero-shortlist sessions. Earlier unscreened diagnostic files
are retained as unscreened_control_audit.json and unscreened_repeat_audit.json;
they are excluded from this conclusion.

Reproduce the audit with `python -m ga9.milestone_audit NEW_OUTPUT` after supplying
that new directory's ga8_before.json and acquisition.json evidence records. Outputs
refuse an existing audit.json. Current evidence lives in
`artifacts/milestone_20261029/`: source event CSV, per-ticker eligibility audit,
training-only declaration/results, daily participation/equity and GA8 hashes.
