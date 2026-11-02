Latest readable archive evidence: [Nasdaq archive audit](NASDAQ_ARCHIVE_AUDIT_20261029.md). Access is resolved; membership, identity and action gates block replay.

# Latest daily screening implementation

Daily close screening now covers the complete supplied stock universe. Fixed
20/60/120-session total-return momentum and 50-session trend are percentile-ranked
against eligible peers; all four must be positive. The top 20 (configurable with
`--screen-top-k`) feed the learned net-edge ranking and competitive allocator.
Incumbents retain native lifecycle management. Screening settings and historical
membership hashes are frozen before each external forward year. Subset `--symbols`
is rejected by the daily runner; it requires matching complete data/universe cohorts.

`--membership history.csv` accepts `ticker,effective_from,effective_to,known_at`.
Intervals are half-open, may include removal and re-entry, must not overlap, and
must have evidence known by their start. Every supplied symbol needs history.
Eligibility constrains ranks, breadth, new fills and close decisions; removal
schedules an incumbent exit at the next open. Raw marks remain available for exits.
Missing held marks fail. The complete-universe secondary uses fixed initial cash
sleeves, enters after its first eligible decision close and holds thereafter without
rebalancing; removals do not retrospectively change sleeves. Missing history is an
explicit fixed-cohort research limitation, not historical survivorship certification.
A CSV supports PIT evidence but does not itself establish independent provenance.

Bounded synthetic replay (one generation, four candidates, five seconds per fold):

```bash
/opt/mts/.venv/bin/python -m ga9.synthetic_pilot --output ga9/artifacts/new_synthetic_pilot
/opt/mts/.venv/bin/python -m unittest ga9.test_screening ga9.test_benchmarks ga9.test_objective ga9.test_execution
```

See [daily screen evidence](DAILY_SCREEN_REPORT.md). The remaining text describes
prior prototype behavior; subset CLI examples below are superseded by this section.

# GA9 portfolio excess-return prototype

Standalone research package. It snapshots GA8 PIT features, chromosome grammar and
execution accounting; it never imports GA8 or writes GA8 source, outputs or checkpoints.

Primary investment benchmark is **QQQ for a predeclared Nasdaq-focused universe**
or **SPY for broad US stocks**. The profile, ETF symbol and input hash are frozen
before training/forward; outcomes cannot switch the benchmark. Primary net excess
return drives matched-window labels, opportunity costs, selection and forward
success. Equal-weight buy-and-hold of the **complete PIT research universe** is a
secondary diagnostic, independent of selected stocks or `--symbols`.

Portfolio feasibility remains **absolute MDD <=8.00%**. Positive primary net excess
CAGR is additionally required for forward success. Calmar/drawdown only break ties
after the economic objective and risk gate. Rejected breaches never count as passing.

From the repository root:

```bash
/opt/mts/.venv/bin/python -m unittest -v ga9.test_benchmarks ga9.test_objective ga9.test_execution
/opt/mts/.venv/bin/python -m ga9.run --output ga9/artifacts/my_pilot --universe-profile broad_us --generations 2 --population 4 --budget 20 --seed 90079
/opt/mts/.venv/bin/python -m ga9.verify ga9/artifacts/my_pilot
```

Outputs must be new directories under this package or `/tmp`. They are never
overwritten. Dependencies are in `requirements.txt`; the existing MTS virtualenv
was used. `--symbols ACN,COST,GEV` selects the exact sample **before** ranks, breadth
and niche calculations. The secondary always uses the complete `--universe-data`
(default `--data`) stock cohort, never the selected subset. `--symbols` must be
contained in that cohort. GEV's secondary sleeve stays cash until 2024-04-02.
Default is the fixed 79-stock source cohort, not a verified historical survivor-free
universe. No future-observed endpoint is used to prune sample membership.

`--universe-profile broad_us` defaults to SPY; `--universe-profile nasdaq` selects
QQQ. `--benchmark-data` accepts a parquet with explicit ticker, date, OHLC, adj_close,
volume, dividends and stock_splits. A single-symbol file may omit ticker only when
its filename identifies the required ETF (e.g. SPY_YFINANCE_2005_2026.parquet).
SPY defaults to the discovered local GA6 backup comparator, read only; its exact
source and SHA-256 are logged. QQQ requires a supplied file: no verified local QQQ
series was found. A missing/wrong ETF, missing session or changed source hash fails
the run without substituting cash, equal weight or the other ETF. ETF data is kept
outside stock features/ranks/niches. Synthetic tests exercise both profiles; they
are not real-market QQQ results. Direct training APIs also require an attached
primary ETF; equal-weight-only label fixtures must be explicitly marked synthetic. The profile is a predeclared research design, not
an exchange classification inferred from subsequent performance.

Example for a Nasdaq study with supplied QQQ bars:

```bash
/opt/mts/.venv/bin/python -m ga9.run --universe-profile nasdaq --benchmark-data /path/to/QQQ.parquet --universe-data /path/to/full_universe.parquet --data /path/to/full_universe.parquet --output ga9/artifacts/nasdaq_pilot --generations 1
```

Three expanding chronological folds train through 2022/2023/2024 and test the next
year. Search uses a chronological half-year internal validation segment of each
training period; those validation results are selection-used. The selected genome
is refit through year-end, written to `frozen.json` and hashed before external forward
rows are loaded. The next fold may legitimately train on the preceding year after
it has ended. No previous fold's forward score drives search or parameter choices.
Training-refit results are explicitly in-sample; forward is protected from selection,
not globally unseen after GA8 research and disclosed GA9 engineering runs.

The three scientific measurements remain separate:

1. Fixed score-bin conditional expectations of matched-window future **net** relative
   returns; only outcomes whose next-open exit has matured before the training cutoff
   are labels. Frozen features map to expectations without accessing future outcomes.
   Post-freeze discrimination reports rank correlation and selected relative returns.
2. Shared-capital realized contribution: funded per-gene removal ablations include
   fees, cash reserves, settlement delays, turnover, correlation, sector capacity,
   incumbent positions, and opportunity costs. Entry forecasts pay both trading sides;
   holding forecasts treat entry costs as sunk. Missing holding forecasts preserve
   native lifecycle rules. These ablations are diagnostic and never forward selection.
3. Complete next-year portfolio excess CAGR and dollar NAV versus predeclared QQQ/SPY,
   plus separately reported complete-universe equal-weight excess, with absolute portfolio risk acceptance and full daily ledgers.

Horizon sessions default to `5,20,60,120`; mixture weights evolve only on training
validation. Each new position gets an expiry sampled reproducibly from its frozen
mixture using a date/symbol/genome hash. Native loss, trailing, hold/add/reduce/exit
and replacement policies remain active and may close sooner. An explicit swing
experiment is available as `--horizons 5,20,40 --swing-max-sessions 40`; the cap is
recorded and all requested horizons must respect it. No forward horizon selection.

The competitive manager retains NO_TRADE and cash, next-open execution, 5bp slippage,
1bp fees, conservative T+2 proceeds and nonspendable ex-date dividend receivables.
Benchmarks use identical entry costs, uninvested listing sleeves and no invented
terminal liquidation; holdings are marked at the final close. Both accounts wait
through their first decision close before the earliest fill. The secondary never
rebalances its initial equal-dollar sleeves. Every label starts a matched-window
primary ETF buy-and-hold account. Complete-universe secondary sleeves remain cash
until listing, without future-endpoint survivor filtering.

Unknown sectors share one conservative `UNKNOWN` bucket; GA9 caps aggregate entry
allocations to it instead of inventing sector diversification. Market drift can
exceed entry caps. Verified PIT sector classifications, SGOV prices and dividend
payment dates remain missing evidence. SGOV is disabled; cash remains available.
The GA8 seed and momentum controls preserve native GA8 management and do not inherit
GA9's added conservative sector cap. The GA8 control is the inspected source seed
portfolio, not a running champion or a matched search-budget claim.

`status.json` reports stage, elapsed time and search ETA. The pilot has hard CLI
bounds: 1–3 generations, 4–8 candidates, 1–120 search seconds per fold. Budget checks
occur between candidates; refits and diagnostic reports finish atomically. Create
`<output>/STOP` or send SIGTERM to **the GA9 run's** PID for a cooperative stop. No
long search driver exists. Each fold starts an independent $100,000 account; these
are not continuous, stitched trading returns. MDD uses daily close NAV including
initial capital; gaps can breach the limit and are rejected, never clipped.

The delivered pilot's exact command, elapsed time, failure results and artifact
locations are in `PILOT_REPORT.md` and `pilot_summary.json`. Frozen models, daily CSV
ledgers, fills, decision rankings, contribution, discrimination and risk rejections
are in the referenced local artifact directories. Engineering reruns are disclosed
in their manifests. Source/data hashes permit checking the evaluated implementation.

Latest real-data availability audit, bounded smoke and training-only participation
experiment: [2026-10-29 milestone](MILESTONE_20261029.md). Historical Nasdaq
membership and QQQ remain explicitly blocked; real fixed-cohort SPY smoke verified,
all forward excess gates failed, and widening the shortlist was not promoted.
