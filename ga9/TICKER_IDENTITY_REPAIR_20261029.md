# FB/META and XLNX/AMD repair

Implemented `ticker_lineage.py` and bounded host CLI `repair_ticker_identities.py`.
No GA8 files/processes or existing admission/quarantine rules were changed. No
replay or evolution ran. Protected FB acquisition here is explicitly requested
identity diagnostics only: `accepted_raw.json` is always empty.

Nasdaq primary evidence:

- [ECA2022-125](https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2022-125): June 3 notice; FB becomes META effective June 9, 2022; Class A CUSIP 30303M102. The issuer announcement referenced by Nasdaq is May 31, distinct from notice publication. Exact notice time is unavailable. The ledger uses June 4 00:00 New York (04:00 UTC) as a conservative knowledge bound, explicitly labeled rather than an invented publication timestamp.
- [ECA2022-23](https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2022-23): XLNX CUSIP 983919101; last trade February 11; merger closed before February 14 open; halted February 14 and suspended February 15; consideration 1.7234 AMD shares per XLNX share. AMD is a different security, never a historical XLNX bar alias. This page is labeled February 10 but updated after closing; update knowledge time remains null. Closing is never represented as known on February 10.
- [Alpaca bars](https://docs.alpaca.markets/us/reference/stockbars): `asof` identifies the entity at that symbol/date; historical bars are labeled with the requested symbol. Unknown symbols can fall back to literal lookup. Requests therefore use FB/asof=2022-06-08 and XLNX/asof=2022-02-11; raw SIP only. `asof` does not prove historical availability or trading eligibility.

Events are frozen dataclasses with canonical SHA-256 identities. Merger lineage
references the last-trade event digest; corrections produce new digests. Each run
writes an exclusive new output directory containing its immutable fact snapshot,
observation timestamp, knowledge/effectiveness fields and source URLs. Historical
identity resolution is explicitly retrospective; `visible()` gates event knowledge
and rejects missing time zones. Unknown knowledge timestamps never pass. This is
application-level immutability/content addressing, not filesystem WORM storage.

Original gaps contained 109 FB and 34 XLNX dates. SHA-verified original SIP/raw
responses from the two prior stock recovery runs account for 29 XLNX dates.
Remaining: **109 FB and 5 XLNX**. XLNX February 14–18 are all after last trade:
`POST_LAST_TRADE_NO_XLNX_BAR_EXPECTED`. These remain visible as diagnosed coverage
errors; the script does not silently remove them, fill forward, or substitute AMD.
The independent sessions/membership projection still needs correction before any
replay admission. Unexpected vendor XLNX bars on these dates are rejected.

Final live attempt: two authenticated requests, one for each symbol, both failed
with URLError / gaierror / errno -3. No HTTP response; credentials or SIP
entitlement cannot be diagnosed from DNS failure. **Exactly 0 new raw recovered,
0 certified, 0 admitted**. FB retains 109 recoverable-but-unretrieved dates; five
XLNX dates need no XLNX bar. See
`artifacts/ticker_identity_repair_both_20261029/report.json`. Earlier attempts are
retained separately; they also recovered zero.

Host invocation (use a fresh output directory):

```bash
/opt/mts/.venv/bin/python -m ga9.repair_ticker_identities \
  --gaps ga9/artifacts/nasdaq_archive_audit_final_20261029/missing_projected_bars.csv \
  --previous ga9/artifacts/alpaca_stock_recovery_batch_20261029 \
  --previous ga9/artifacts/alpaca_stock_recovery_second_20261029 \
  --output ga9/artifacts/NEW_IDENTITY_RETRIEVAL --max-requests 8
```

Bounds: only FB/XLNX, only 2022, at most 150 remaining dates, default eight/max
sixteen HTTP requests, max four pages per symbol, 20 seconds per HTTP call, no
retries. Stops on authentication/entitlement/rate limit failures; allows one
independent attempt per symbol after DNS failure. Existing response byte/hash and
OHLCV/window/pagination validation is reused. Source files are never overwritten;
only requested, unique, valid pre-delisting dates count toward raw recovery.
Exit 2 always indicates no replay authorization, even if retrieval succeeds.

Validation: 55 tests passed across ticker lineage, Alpaca repair, archive adapter,
screening, benchmarks, objective and execution. Six new tests cover immutable
lineage, separate knowledge/effectiveness, absent update timestamps, same-CUSIP
rename, merger non-aliasing, zero admission after identity repair, exact recovery
counts, rejecting post-last-trade bars, request asof values, prior source hashes,
exclusive outputs, and bounds.
