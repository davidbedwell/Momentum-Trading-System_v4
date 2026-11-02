# Current GA9 delivery

Latest override implemented: QQQ primary for Nasdaq, SPY primary for broad US;
complete-universe equal weight is secondary. Policy, ETF source hash and universe
are fixed before test. Absolute MDD <=8% is unchanged. Missing/mismatched benchmark
data fails rather than switching or substituting a selected-stock benchmark.

29 tests pass, including both profiles through all three synthetic chronological
folds and verification. The real SPY pilot (one generation, four candidates, 20s
search budget per fold) completed in 31.5s and verified. All three forward folds
failed excess-return success. The 2024/2025 refits additionally failed the 8% risk
gate (14.50%/14.68%); these are retained as rejected research diagnostics.

Real QQQ evaluation is blocked by missing verified local OHLC/dividend bars. Its
explicit failure is logged in artifacts/nasdaq_primary_missing_data/failure.json.
Current reports are PILOT_REPORT.md and pilot_summary.json. Superseded reports are
archived in history/; historical runtime outputs and frozen models were preserved.

Inspected GA8 hashes are unchanged; no GA8 files, checkpoints or processes were
modified. Work remains uncommitted because .git is read-only: the prior staging
attempt failed creating .git/index.lock. No long search was launched.
