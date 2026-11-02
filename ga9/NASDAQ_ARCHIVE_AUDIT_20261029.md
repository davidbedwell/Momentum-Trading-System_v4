# Readable Nasdaq archive audit — 2026-10-29

**BLOCKED_NOT_PIT_CERTIFIED.** Read access is resolved. This supersedes the access
block in NASDAQ_ARCHIVE_DISCOVERY_20261029.md. No real-data forward smoke or GA
was executed because the underlying evidence gates fail. GA8 was neither edited
nor executed; its pre-existing working-tree modifications were left intact.

Read-only recursive inventory: **358 files, 49,597,668 bytes**, including nested
source repositories (rather than the reported 223 files). All files are hashed in
[the inventory](artifacts/nasdaq_archive_audit_final_20261029/inventory.json).
The four hashes declared in SOURCE_AND_FILE_CHECKSUMS.json match. This verifies
local byte consistency, not historical accuracy or vendor provenance.

There are **112 snapshots, 216 distinct eligible tickers, 130 Yahoo parquet files
and 56 EODHD JSON files**. No symbol has overlapping vendor files. The eligible
rosters exclude the frozen protected partition; these are not full Nasdaq-100
rosters. Missing protected stocks must not be added to fill index-size differences.

| Year | Snapshots | Peer sessions | Projected symbols | Projected security-sessions | Observed | Missing | Raw rows | Unknown action rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 6 | 251 | 80 | 17,905 | 16,014 | 1,891 | 33,582 | 2,930 |
| 2023 | 5 | 250 | 77 | 17,124 | 15,875 | 1,249 | 33,575 | 2,500 |
| 2024 | 5 | 252 | 73 | 16,884 | 15,775 | 1,109 | 33,860 | 2,360 |
| 2025 | 6 | 250 | 75 | 16,755 | 15,498 | 1,257 | 32,838 | 1,508 |

These denominators are **diagnostic projections**, assuming each snapshot roster
until the next snapshot. They are not certified expected PIT sessions. Peer
sessions are the observed vendor union, not an independent exchange calendar.
Certified PIT security-sessions remain **zero**. Raw-row/action counts cover all
stored symbols in each year, not just projected eligible rows. Basic checks found
zero duplicate or invalid OHLCV rows in these years; identity and adjustment
correctness cannot be inferred from that result.

Projected symbols with no raw file (also unresolved identity candidates):

- 2022: ATVI, BKNG, FB, FISV, GOOGL, SPLK, TSLA, WBA, XLNX.
- 2023: ATVI, BKNG, FISV, GOOGL, SPLK, TSLA, WBA.
- 2024: APP, ARM, BKNG, GOOGL, SPLK, TSLA, WBA.
- 2025: APP, ARM, BKNG, GOOGL, TSLA, WDC.

The archive's 30 identity exceptions comprise 24 deferred and six unresolved 404
symbols. Every candidate has allow_in_backtest=false. Its quarantine identifies
FB→META and GOOGL→GOOG protected relationships and prohibits testing. Candidate
ISIN matches are not historical identity certification; no aliases were stitched.

The event ledger contains 449 asserted dated events from third-party YAML. The
407 snapshot-difference events explicitly have SNAPSHOT_INTERVAL precision.
The official crosscheck covers only four announcement dates (eight action groups):
2020-12-21, 2023-12-18, 2025-12-22, 2026-06-22. Eight exact matches do not certify
all 2022–2025 transitions or the starting roster. Publication knowledge dates and
stable security IDs remain absent from the projected mapping.

EODHD files lack dividends and splits; the adapter preserves nulls. Yahoo action
columns exist, but raw/adjusted accounting and historical split conventions remain
unreconciled. An independent calendar is unavailable in the current environment.
The warmup/interval-end diagnostic lists missing preceding 120 peer-session bars
and next peer-session marks after **each projected interval end**. These ends
include unchanged snapshot transitions, so they are not counts of actual required
portfolio exits. No exit or warmup completeness certification is claimed.
No QQQ series exists in the archive. The earlier SPY exception still needs explicit
benchmark-policy implementation and freezing if the other gates are later repaired.

## Adapter and reproducibility

[Adapter](nasdaq_archive.py) maps local-session dates, OHLC, adjusted close, volume,
and explicit actions with file path/SHA-256 lineage. It neither downloads nor fills
records, trims away missing symbols, extends the final snapshot, nor writes a
runnable stock panel. The unverified half-open membership CSV deliberately has
null known_at/security_id; GA9 membership_mask rejects it. require_replay_inputs
always fails closed, including when presented a forged passing manifest. This is
an audited diagnostic adapter, not a completed certification/replay integration.

```bash
/opt/mts/.venv/bin/python -m ga9.nasdaq_archive \
  --archive /tmp/ga9_nasdaq_archive \
  --output ga9/artifacts/NEW_ARCHIVE_AUDIT
```

The output directory must be new. Exit code **2** means the audit completed with
blocked replay gates. Final evidence is in
[coverage.json](artifacts/nasdaq_archive_audit_final_20261029/coverage.json),
[raw audit](artifacts/nasdaq_archive_audit_final_20261029/raw_bar_audit.csv),
[exact missing bars](artifacts/nasdaq_archive_audit_final_20261029/missing_projected_bars.csv),
[identity exceptions](artifacts/nasdaq_archive_audit_final_20261029/identity_exceptions.csv),
and [warmup/interval-end diagnostics](artifacts/nasdaq_archive_audit_final_20261029/warmup_exit_UNVERIFIED.csv).
Earlier diagnostic directories without the `final` name are intermediate audits,
not strategy runs.

Validation: 37 unittest tests passed across test_nasdaq_archive, test_screening,
test_benchmarks, test_objective and test_execution. After adding final diagnostic
fields, all six adapter tests passed again. Tests cover unknown actions, session
dates, lineage, duplicate/invalid bars, removal/reentry, no terminal extension,
rejection of unknown availability, and rejection of forged replay authorization.

## Alpaca repair follow-up

See [bounded Alpaca repair audit](ALPACA_REPAIR_AUDIT_20261029.md). Actual SIP
access probes failed before HTTP with DNS `gaierror` (-3); zero of 5,506 gaps
were recovered, and no records entered replay. Secondary membership comparisons
found an ANSS interval discrepancy and an official-notice conflict for the
SGEN/TTWO transition. All existing replay and quarantine gates remain closed.
