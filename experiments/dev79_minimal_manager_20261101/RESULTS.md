# Actual historical replay results

Exploratory fixed DEV79 survivor universe; price returns only. No alpha, transferability, or PIT certification claim.

2009-01-02 through 2026-09-14; 4,451 sessions; $100,000 initial NAV per arm.

| Strategy | Final NAV | CAGR | Max drawdown | Fills | Fees | Adverse slippage | Mean exposure |
|---|---:|---:|---:|---:|---:|---:|---:|
| manager | $95,981.99 | -0.23% | 23.86% | 18,944 | $36,601.42 | $36,601.43 | 46.33% |
| buy_hold | $1,364,456.02 | 15.95% | 33.98% | 79 | $49.98 | $49.95 | 96.59% |
| momentum | $1,042,251.32 | 14.19% | 22.87% | 2,086 | $28,725.86 | $28,725.95 | 66.46% |

The manager underperformed both baselines. No parameters were tuned to improve these results. Fees and daily turnover materially eroded performance. Drawdown throttling is a sizing control and did not guarantee a drawdown ceiling.

All three ledgers independently reconstruct cash, unsettled proceeds, shares, and NAV. Maximum internal PnL reconciliation error: $9.31e-10. No stale valuation rows occurred in this run.

Manager decision counts: `{"abstain": 302126, "add": 2537, "enter": 7284, "exit": 7127, "hold": 30239, "reduce": 2316}`.

## Commands actually used

From `/opt/mts/sector-leadership-independent`:

```bash
/opt/mts/.venv/bin/python experiments/dev79_minimal_manager_20261101/audit_inputs.py > experiments/dev79_minimal_manager_20261101/input_audit.log 2>&1
/usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M cpu=%P' -o experiments/dev79_minimal_manager_20261101/runtime.txt /opt/mts/.venv/bin/python experiments/dev79_minimal_manager_20261101/manager.py > experiments/dev79_minimal_manager_20261101/run.log 2>&1
/opt/mts/.venv/bin/python -m unittest discover -s experiments/dev79_minimal_manager_20261101 -p 'test_manager.py' -v > experiments/dev79_minimal_manager_20261101/tests.log 2>&1
/opt/mts/.venv/bin/python experiments/dev79_minimal_manager_20261101/summarize.py
```

Repeat the whole pipeline with `bash experiments/dev79_minimal_manager_20261101/run.sh`. The replay pins itself to one allowed CPU before numerical imports.

## Runtime and tests

```
elapsed_seconds=26.47 peak_rss_kb=628768 cpu=99%
test_cash_clip_and_no_double_split (test_manager.Tests.test_cash_clip_and_no_double_split) ... ok
test_historical_artifacts_independent_reconstruction (test_manager.Tests.test_historical_artifacts_independent_reconstruction) ... ok
test_historical_fills_match_archived_next_session_open (test_manager.Tests.test_historical_fills_match_archived_next_session_open) ... ok
test_missing_window_blocks_eligibility (test_manager.Tests.test_missing_window_blocks_eligibility) ... ok
test_next_open_and_missing_next_open_cancellation (test_manager.Tests.test_next_open_and_missing_next_open_cancellation) ... ok
test_partial_sale_cost_fees_and_settlement (test_manager.Tests.test_partial_sale_cost_fees_and_settlement) ... ok
test_prefix_invariance_and_future_mutation (test_manager.Tests.test_prefix_invariance_and_future_mutation) ... ok

----------------------------------------------------------------------
Ran 7 tests in 8.342s

OK
```
