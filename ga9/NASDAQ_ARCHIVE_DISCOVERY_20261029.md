# Prior Nasdaq PIT archive discovery

Status: **BLOCKED_SOURCE_ACCESS_NOT_PIT_CERTIFIED**. Inspection on 2026-10-29
returned `PermissionError: [Errno 13] Permission denied` for
`/opt/mts/thunder-migration/mts-certification-20261011/nasdaq_pit_20261012`.
The readiness filename, 216 eligible tickers, 112 snapshots, historical Yahoo/EODHD
bars and constituent crosscheck are user-reported discoveries, not independently
verified counts. Preserve and reuse this project before considering acquisition.
The earlier milestone's search did not cover this unreadable archive; its missing
membership/QQQ statements do not establish absence from this project.

| Year | Dated membership | Stock bars / identity gaps | SPY observed sessions |
| --- | --- | --- | ---: |
| 2022 | Unknown: source unreadable | Unknown: source unreadable | 251 |
| 2023 | Unknown: source unreadable | Unknown: source unreadable | 250 |
| 2024 | Unknown: source unreadable | Unknown: source unreadable | 252 |
| 2025 | Unknown: source unreadable | Unknown: source unreadable | 250 |

SPY is the existing local comparator at
`/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet`.
GA9 `load_primary` passed OHLC, duplicate, null, dividend and split-jump checks.
SHA-256: `b182402afd15c074ee4cc596149bf0a821e6cbd00fa5329d84eef269636f6381`.
These are observed counts, not independent calendar completeness certification.
No exchange-calendar package is installed. QQQ availability inside the archive is
unknown. The user authorizes SPY if QQQ is unavailable; freeze that choice before
any replay. Existing `BenchmarkPolicy('nasdaq')` still requires QQQ: it does not
implement this exception. Do not relabel the Nasdaq universe as broad US to bypass
it. No benchmark policy or study runner was changed here.

## Mapping required once readable

1. Inventory and hash the readiness JSON, dated snapshots/change evidence,
   crosscheck, identity tables and existing vendor bars. Record source paths and
   audit failures rather than treating a readiness label as certification.
2. Map membership into GA9's `ticker,effective_from,effective_to,known_at`
   half-open intervals, retaining source provenance and stable security identity
   in a companion table. Require an evidenced starting roster, intervening changes,
   removals/reentries and publication availability. Snapshot capture dates alone
   do not prove historical knowledge dates or uninterrupted membership. Never
   backfill the union of 216 names into every date or extend the last snapshot
   through an unknown interval.
3. Resolve ticker changes, reused symbols, share classes, listing/delisting and
   corporate actions against the crosscheck and vendor identities. Keep unresolved
   cases explicit. Do not stitch ticker histories without identity evidence.
4. Normalize existing bars to GA9's date/ticker/OHLC/adjusted-close/volume/
   dividends/splits schema with vendor lineage. Reconcile Yahoo/EODHD overlaps and
   adjustment conventions; missing actions cannot silently become zero. Retain
   removed securities and marks needed for next-open exits. Audit warmup history
   for the 120-session screen without treating pre-membership prices as eligibility.
5. For each year 2022–2025, report expected and observed eligible security-sessions,
   missing/duplicate/invalid bars, missing exit marks, unresolved identity rows,
   unknown membership intervals and action conflicts, with exact symbol/date lists.
   Use an independent exchange calendar and evidenced listing/suspension exceptions;
   a peer-session union cannot prove completeness. Do not silently prune gaps.
6. Fail closed on any unresolved membership, availability, identity or required bar/
   action/session coverage. GA9's existing interval parser checks structure and
   known_at ordering, but missing `--membership` admits a fixed research cohort;
   it is not an archive certification gate. A strict archive entrypoint must require
   the validated manifest and hashes before calling the runner. Freeze benchmark,
   universe and membership before chronological folds, with the existing 8% risk gate.

Exactly what is currently missing is **read access and the resulting verification**:
the actual readiness findings, file schemas/hashes, dated interval chain, security
identity exceptions, per-year stock/session coverage, action reconciliation and
independent calendar comparison. Which underlying records need repair or acquisition
cannot be determined from an inaccessible archive. No claim that the raw data is
missing is warranted. Integration and replay remain pending; no long GA, download,
GA8 source/artifact/process change or blind rebuild occurred.

Machine-readable observations: [discovery JSON](NASDAQ_ARCHIVE_DISCOVERY_20261029.json).
