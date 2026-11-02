# Stock repair fix

The host run was a selection failure, not an Alpaca access failure or exhausted
request budget. Its 25 successful requests were one QQQ probe plus four years
of five bar variants and one corporate-action query each. All 5,506 stock gaps
were filtered out because the runner conflated `allow_in_backtest=false` with
protected acquisition quarantine.

The raw repair runner now excludes the protected partition and known protected
aliases (including FB and GOOGL), leaving 4,394 eligible diagnostic stock gaps.
Unresolved identities stay blocked from `accepted_raw.json`, the existing
admission adapter, certification, and replay. Their vendor bars are saved only
in `recovered_raw.json`, with original response bytes, hashes, and a request
ledger. No alias stitching or identity inference is performed. Existing PIT and
quarantine admission functions are unchanged.

Stock symbols are ranked by missing date count with deterministic ticker ties.
Each request covers a bounded batch of missing dates within one stock/year;
only requested gap dates count as recovery. Year is derived from date rather
than trusting a supplied year column. The runner needs one request to start,
without a QQQ probe, adjusted variants, or corporate-action work. It stops at
the request bound and on DNS/authentication/rate-limit failures. Pagination
and OHLCV validation still fail closed. QQQ is never scheduled by this runner;
`--reuse-qqq` verifies hashes and references the existing raw QQQ evidence.
Use the prior runner's saved responses for further certification diagnostics.

Validation: 18 focused unit tests passed (`ga9.test_alpaca_repair` and
`ga9.test_nasdaq_archive`). New checks cover a one-request stock repair,
quarantine exclusion, deduplicated gap counts, separate raw/certified reporting,
identity-deferred storage, budget stopping, cached QQQ hashes and unique dates.
The sandbox smoke attempted BKNG January 3–5, 2022 and failed with URLError /
gaierror / errno -3. It verified reuse of 1,003 QQQ dates, made zero QQQ requests,
and recovered **0 raw / 0 certified**. This is not a successful live stock test.
Evidence: `artifacts/alpaca_stock_smoke_fix_20261029/report.json`.

Run on the host with working Alpaca access:

```bash
cd /opt/mts/ga8/Momentum-Trading-System_v4-ga8
./ga9/repair_stock_smoke.sh
```

This executable uses the existing credential-file default without printing keys,
a fresh timestamped output directory, at most two HTTP requests, one stock and
three missing dates per batch. It checks nonzero raw recovery, zero certified
recovery, 1,003 reused QQQ sessions and no QQQ HTTP requests. Default first work
is BKNG January 3–5, 2022. Expected maximum recovery is six missing dates if both
single-page requests succeed; actual vendor results determine the count. CLI
exit 2 means PIT remains blocked; the script handles that expected exit and
returns failure if stock recovery did not occur. Recovered rows do not overwrite
the archive. No GA8 files were edited by this fix.
