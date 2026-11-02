# Historical discovery pipeline

Standalone research implementation of `GA9_CODEX_CHARTER.md`. Standard-library Python 3.11+; no GA imports, trading integration, downloads, training generations or external writes. Tests use `unittest`.

```bash
python3 -m unittest discover -s historical_discovery/tests -v
python3 -m historical_discovery fixture --out /tmp/discovery-fixture-new
python3 -m historical_discovery.audit --out /tmp/discovery-audit-new.json source results results_final Research
```

Output directories must be new. Exclusive writes prevent silent replacement of frozen predictions. A failed run can leave partial artifacts; audit the failure and use a new directory after fixing it. Do not overwrite prior runs.

## Stages and lock

1. Presence-only audit inventories extensions, byte counts and credential existence without reading data, prior results or credential payloads. It does not establish data coverage or account entitlements. It traverses the explicitly supplied Research symlink root but does not follow nested symlinks.
2. `freeze --out DIR` records code/test hashes, fixed feature definitions, thresholds, tuning choices, candidates, arms, metrics and locked years. `run` verifies this freeze before loading data. There is deliberately no holdout unlock or evaluation command. All year-taking entry points reject years outside 2005–2009; adapter rejection happens before opening the manifest.
3. `run --out DIR --manifest 2005=PATH [--manifest 2006=PATH ...]` accepts contiguous discovery years starting in 2005. 2005 is warmup. Each later fold fits only on earlier complete-year outcomes. Current predictions, fitted parameters, training years, provenance and hashes are persisted before current-year label computation. No candidate selection on a current year's outcomes; both predeclared candidates are reported.
4. Report annual opportunity rankings and binary winner metrics. The three arms use exactly the same stock/date intersection. Broad chart-only results and missing-fundamental IDs are separate. Empty intersections and insufficient training produce absent model results, not fabricated scores. Momentum, liquidity and constant-score baselines use the intersection. Ties sort by permanent ID deterministically; constant ranking has undefined correlation.

No 2010/2011 labels were accessed in this implementation session. Prior exposure elsewhere is unknown; do not describe any later historical evaluation as pristine without an exposure audit. Development years are explicitly known-winner research. Correlations and synthetic tests establish neither causation nor investment performance.

## Fixed research definition

One June 30 end-of-day snapshot per development year, for next-session research use. Chart features: year-to-date adjusted close / first eligible adjusted open minus one, log(1 + mean adjusted dollar volume), and year-to-date market return. Fundamentals: growth between latest two usable original annual revenue reports whose period ends are 300–430 days apart. Nonpositive prior revenue or insufficient reports yields missing, never zero. Versions other than original version 1 are excluded. No sector features or ticker-name predictors.

Reports become usable at the later of public availability and original vendor-version availability (`recorded_at`). Timestamp precision requires timezone. Date-only public availability is delayed until midnight after that date plus two full days. The version timestamp must represent original historical availability, not today's export ingestion timestamp. No financial period ending after the snapshot is usable. Market cap is optional, sourced with its own as-of timestamp, and never a filter or model feature.

Labels are (a) annual first eligible adjusted open to final adjusted close or terminal delisting recovery, and (b) maximum adjusted high / an earlier session's adjusted low minus one. Same-session extrema are not sequenced speculatively. IPOs get explicitly partial-year returns. Winner = calendar return >= 50% OR chronological advance >= 100%. Both continuous labels, start and peak dates, mean dollar liquidity and available starting market cap are retained, including nonwinners and total failures. The regression rank target is max of the two returns. No hard liquidity, capitalization or trade-risk gates.

Candidates: standardized equal feature weights and diagonal feature/target covariance weights. Scaling and covariance fit exclusively on earlier years. No hyperparameter search. Metrics: recall@2 and precision@2 for threshold winners, average-tie Spearman against continuous opportunity ranking, plus each selected security's calendar days from snapshot to annual advance peak and maximum strictly post-snapshot high / snapshot close minus one. Negative lead time explicitly indicates that the annual peak preceded prediction. Remaining upside is retrospective descriptive opportunity, not executable profit. Combined-minus-chart and combined-minus-fundamentals deltas use the same intersection. The annual label can include an advance that occurred before the snapshot; these metrics must not be interpreted as forecasting only new future winners.

## Provider adapter / schema v1

`Adapter.load(year) -> dict` and `Adapter.provenance() -> dict`. `JsonAdapter` accepts one trusted, attested single-year partition, validating manifest scope **before opening the payload**. A mislabeled or dishonest payload cannot be guaranteed unread by a JSON parser: a data custodian must segregate discovery from evaluation before delivery. Never point this implementation at a mixed-year legacy dataset. Actual transport/vendor integration remains future work.

A manifest has these required fields:

```json
{
  "schema_version": 1,
  "years": [2005],
  "payload": "discovery_2005.json",
  "source": "licensed supplier and dataset/version identifiers",
  "release_date": "YYYY-MM-DD",
  "revision_policy": "original_as_reported",
  "coverage": "exchanges, sessions, financial coverage and documented exclusions",
  "adjustment_policy": "documented PIT split/dividend OHLCV and terminal-value basis",
  "historical_listing_membership": true,
  "includes_delistings": true,
  "corporate_actions_reconciled": true,
  "pit_financial_availability": true,
  "asof_adjusted_ohlcv": true,
  "complete_exchange_sessions": true
}
```

Payload is a JSON object of table arrays. Every row requires nonempty `source`. Dates are ISO dates, timestamps are ISO with timezones, monetary fields must share a documented currency and basis. Every price row has permanent `id`, `date`, positive `open/high/low/close`, nonnegative `volume`. All price/market/session rows belong to the declared year. Tables:

| Table | Additional required columns and meaning |
| --- | --- |
| `listings` | `id, ticker, start, end, exchange, kind, end_reason`; nonoverlapping inclusive listing/ticker intervals; NYSE/NASDAQ `common` admitted, other kinds excluded and reported. `end_reason=delisting` requires terminal recovery. Partition-boundary end dates are not delistings. |
| `sessions` | `exchange, date`; complete actual exchange calendar for the year, including holidays correctly. |
| `prices` | Adjusted OHLCV above; exact price coverage for every session during every eligible listing interval. Unexplained holes fail closed. Supplier must resolve suspensions/missing sessions explicitly; no automatic filling. |
| `market` | `date, close`; historically valid adjusted benchmark levels; no current constituent reconstruction. |
| `financials` | `id, period_end, period_type=annual, available_at, recorded_at, revenue, version, revision_policy=original_as_reported`; omit absent records; no null-to-zero replacement. |
| `market_caps` | `id, date, available_at, value`; optional rows, unknown remains null. |
| `actions` | `id, date, kind, adjustment_reference`; split/dividend/merger/spinoff reconciliation evidence. |
| `delistings` | `id, date, terminal_adjusted_value`; full terminal recovery on the same basis as prices, including zero recoveries. |

Empty `actions`, `financials`, `market_caps` or `delistings` arrays are legal when accurate. Listing sessions and prices may not be silently dropped to manufacture coverage. Adjustment computation is the supplier adapter's responsibility; the JSON reader cannot infer missing splits, dividends or terminal recoveries from prices. As-of-adjusted volume and prices must use a consistent basis. Tests validate the contract, not a real supplier's data quality. Raw data and all provenance are hashed in each prediction artifact; caller-provided attestations are not independent verification.

`FixtureAdapter` invents eight securities per year, weekday sessions (not a real exchange calendar), a midyear IPO, delisting to zero, an ETF exclusion, missing financials, positive and negative returns. No real symbols or winner lists are encoded. Its direct synthetic provenance is marked throughout the output. Full generated examples are reproducible with `fixture`; none is evidence that real historical coverage exists.
