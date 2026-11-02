# Local-file execution attempt, 2026-10-31

Status: BLOCKED_LOCAL_SECTOR_ACCESS. This supersedes the earlier assertion that no local sector cache was found: the user identified exact cache paths, and both were directly opened read-only. Both opens failed with OS PermissionError, errno 13. Their contents, validity, coverage, adjustment treatment and provenance therefore remain unknown. This is an access failure, not invalid-data evidence and not a hypothesis failure.

The directory `/opt/mts/thunder-migration` reports owner nobody, group nogroup, mode drwxr-x---. The executor cannot traverse it. The session disallows permission escalation. No permission changes, alternative identity, network acquisition or source writes were attempted.

The specified SPY parquet was fully read and structurally checked: 5,459 rows from 2005-01-03 through 2026-09-15; 5,283 rows through 2025. Dates are increasing with zero duplicates; adjusted close has zero missing, nonfinite or nonpositive values. Columns include adj_close, close, dividends and stock_splits, but no adjusted open. Filename says YFINANCE; embedded metadata contains pandas/Arrow schema information only, so acquisition URL/time and dividend-adjustment provenance have not been independently verified. No strategy returns were calculated. Reading date/schema integrity is not a holdout outcome evaluation; 2026 was counted for audit only and never admitted to research.

No H1/H2/H3/H4 numerical result is claimed. The sector universe is inaccessible, and the frozen hybrid H4 defensive SGOV history has not been admitted. The requested full study was not implemented or executed after the data access failure. Discovery and validation outcomes remain unevaluated. The preregistration SHA256 remains 23a49749f06cfc44c4c7f5a203e5f18cd04343d5763e7541100c4f977a2f756f. The user's present continuation request authorizes resumption; the original four-hour ceiling has not yet elapsed at this attempt.

Required external change: expose read-only access to the two exact sector parquet files (and provenance sidecars), or place readable copies inside this workspace. This cannot be repaired by analysis code. No claim is made that the source files are absent or invalid.

Evidence: audit.json contains exact paths, errors, SPY SHA256, schema and integrity counts. Reproduce without network from repository root:

```
/opt/mts/.venv/bin/python experiments/sector_etf_20261031/local_evidence/inspect_local.py
```

Only this local_evidence directory was written. No paid data, MTS writes, GitHub push, frozen-design changes, parameter selection or holdout strategy evaluation occurred.
