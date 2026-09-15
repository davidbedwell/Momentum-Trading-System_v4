# MTS v4 Cross-Sectional Backend Completion Handoff — 2026-09-14

## Branch and tested code state

Branch:

`mts-v4-cross-sectional-backend-completion-20260914`

Deterministic code/test head validated by GitHub Actions:

`67685557fbec9a687d2671f1736d8390fdd83fd5`

GitHub Actions run:

`34916763944` / MTS v4 core run 215

Every gate completed successfully:

- install project/test dependencies — PASS;
- compile `MTS_V4` and `scripts` — PASS;
- unittest compatibility gate — PASS;
- complete `pytest Tests/mts_v4` gate — PASS;
- CSV adapter regression — PASS;
- wheel/sdist build — PASS;
- installed-package import verification outside checkout — PASS.

Draft PR #10 targets `mts-v4-cross-sectional-derived-market-store-20260914`. Do not merge merely because CI passes; live-data/integration acceptance remains separate.

## Implemented deterministic backend

### Durable Nexus-derived market layer

The parent branch already introduced the Nexus-owned Parquet derived market store, feature/universe versioning, append-only update batches, high-water marks, query slicing, scope contracts, universe evidence materialization, cross-sectional ranking, and participation-method production wiring.

This completion branch adds the rest of the deterministic foundation needed before live data/Sol calibration.

### Point-in-time membership and stable identity

`MTS_V4/universe_membership.py`

- explicit stable `security_id` separate from ticker;
- dated membership/identity intervals;
- optional dated sector/industry attributes;
- overlap validation;
- explicit CSV loader;
- no current-members-projected-backward fallback.

An authoritative historical S&P membership dataset is still required before a real build. The code intentionally refuses to fabricate it.

### Reusable market feature factory

`MTS_V4/derived_feature_factory.py`

Standard predictor/context feature set includes:

- trailing returns: 1/3/5/10/20/63/126/252 sessions;
- SMA20/50/200 and close-to-SMA state;
- SMA20 slope;
- ATR14/20 and normalized ATR;
- realized volatility 20/63;
- relative volume 20;
- point-in-time turnover and relative turnover when historical shares are supplied;
- RSI14;
- gap/intraday/candle-range/close-location measurements;
- range position 20/50/252;
- 252-session drawdown;
- universe return/relative-volume/volatility percentiles;
- sector-relative 252-return percentile when dated sector is supplied;
- breadth above SMA200 and positive 20-session return.

The 1/3/5/10/20 human risk horizons are not the discovery boundary; 63/126/252 and arbitrary Analysis transformations remain available.

Historical future outcomes are a **separate feature set**. This prevents a rolling predictor stream from needing to mutate prior rows when future outcomes mature. Outcome high-water intentionally lags predictor high-water.

### Incremental maintenance

`MTS_V4/derived_market_updater.py`

- only unpublished dates plus maximum required lookback are reacquired;
- raw OHLCV remains process-local/reacquirable and is not persisted in Nexus;
- point-in-time membership and stable identity are attached before feature construction;
- observed cross-sections fail closed when an eligible member is missing;
- duplicate security/date rows fail closed;
- empty required acquisition fails without advancing high-water;
- immutable universe/feature definitions are checked before maintenance;
- update IDs are sanitized;
- predictors and matured outcomes advance independently.

`scripts/update_derived_market_store.py`

- deterministic maintenance CLI;
- dry-run performs zero market downloads and zero Sol calls;
- process-level exclusive maintenance writer lock;
- normal publication remains Parquet-first/manifest-second from the store implementation.

`scripts/rebuild_derived_market_store_copy_on_write.py`

- explicit correction/rebuild path creates a new store generation;
- never silently mutates published historical rows;
- emits a rebuild audit record;
- does not change the published Nexus pointer automatically.

### Predictor/outcome leakage boundary

`MTS_V4/derived_market_evidence.py`

- OUTCOME-classified columns are denied by default;
- historical EXPLORATION must explicitly authorize them;
- evidence provenance records that authorization;
- validation/live callers can remain mechanically predictor-only.

### Universe runner

`scripts/run_sol_batched_universe.py`

- supports a primary predictor/context feature set plus an optional separate historical outcome feature set;
- outcome evidence requires explicit `--allow-historical-outcomes`;
- retains the governed batch RD loop/spend guard;
- raw universe rows remain in campaign cache, not AI transport;
- run summary records deterministic analysis-cache state.

### Cross-sectional statistical tools

`MTS_V4/cross_sectional_statistics.py`

`analysis.cross_sectional.cohort_effect` reports:

- selected/control row descriptives;
- equal-date paired differences;
- Newey-West/HAC uncertainty across dates;
- year stability;
- an explicit warning that row count is not independent-trial count.

RD chooses cohort, threshold, direction, outcome and HAC lag.

`MTS_V4/multiple_testing.py`

`analysis.statistics.benjamini_hochberg` provides deterministic BH adjustment for an RD-defined coherent family of tests. It does not choose the family or interpret significance.

### Exact deterministic result reuse

`MTS_V4/cached_analysis.py`

Campaign-local Analysis cache hashes exact subject/method/evidence/parameters/analysis-input lineage. Only exact matches are reused. Cache hits receive fresh request/result lineage and are marked in execution metadata. No fuzzy scientific substitution occurs.

### Earnings/event substrate for PEAD controls

`MTS_V4/earnings_event_features.py`

- versioned earnings event feature-set definition;
- timezone-aware event timestamps required;
- event is aligned to the first supplied actual market close after it became known;
- no holiday/calendar inference is fabricated;
- EPS estimate/reported EPS/surprise are retained as point-in-time event measurements.

A real historical event-source integration/coverage audit is still required before PEAD calibration.

### Blinded scientific acceptance controls

`MTS_V4/acceptance_controls.py`

Blinded prompts are defined for:

1. cross-sectional medium-term momentum;
2. medium-term trend persistence;
3. short-horizon continuation/reversal;
4. post-earnings behavior;
5. deterministic negative control.

The prompts do not tell Sol the expected answer/direction.

`analysis.controls.deterministic_null` creates an identity/date hash control unrelated to market measurements for the negative-control experiment.

### Sol-before-Qwen gate

`scripts/build_sol_qwen_shadow_corpus.py`

Builds a read-only historical Sol decision/report corpus for later Qwen replay/shadow evaluation. It explicitly labels the corpus `SUPERVISED_REPLAY_SHADOW_ONLY_NOT_AUTONOMOUS_AUTHORITY`.

Qwen autonomy remains prohibited until:

1. real derived data is built and validated;
2. Sol runs the blinded controls and establishes the benchmark;
3. selected Sol historical research traces are preserved;
4. Qwen is brought online against those traces in replay/shadow mode;
5. Qwen demonstrates contract competence and useful scientific behavior.

## What is deliberately not claimed complete

These require real data, source selection, or AI/GPU integration and therefore are not satisfied by deterministic CI:

- authoritative point-in-time historical S&P 500 membership acquisition;
- empirical initial 20-year market-store build;
- live weekly yfinance maintenance performance/coverage testing;
- historical point-in-time shares-outstanding source integration;
- empirical earnings-history completeness/timestamp audit;
- actual Sol execution of the five scientific controls;
- actual Qwen launch/replay/shadow evaluation;
- any claim that a market relationship has been validated.

Also review feature-definition arithmetic against the canonical deterministic computation library before the first authoritative store build; if any formula semantics are changed, bump feature/version rather than silently rewriting v1.

## Next live-data session

1. Pull this branch and verify the code head descended from tested commit `67685557fbec9a687d2671f1736d8390fdd83fd5`.
2. Select/validate authoritative point-in-time membership source.
3. Run updater `--dry-run` first; confirm MARKET_DOWNLOADS=0 and SOL_CALLS=0.
4. Build a small dated fixture/real subset and inspect feature arithmetic, completeness, Parquet size and query latency.
5. Build the initial historical universe substrate only after those checks.
6. Run universe runner `--dry-run`; confirm SOL_CALLS=0 and predictor/outcome access policy.
7. Run Sol blinded acceptance controls with a deliberately small spend authorization.
8. Preserve Sol traces and build Qwen shadow corpus.
9. Only then bring Qwen online in replay/shadow mode.
