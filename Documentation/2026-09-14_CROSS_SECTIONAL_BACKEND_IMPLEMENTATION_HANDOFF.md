# MTS v4 Cross-Sectional Backend Implementation Handoff — 2026-09-14

## Status

Backend implementation has been pushed to branch:

`mts-v4-cross-sectional-derived-market-store-20260914`

Current branch head at handoff creation should be read from Git before testing. The implementation is **not yet server-tested**. No pytest PASS claim is authorized until the branch is pulled onto a working server and the targeted/full gates complete.

The branch was created from:

`mts-v4-future-cohort-waiting-lifecycle-20260914`

at:

`ef685136d581ae82f543d715e7f9a0e85da4ee1c`

so the previously implemented future-cohort waiting lifecycle remains in its ancestry.

## Human-approved architecture

Read before modifying:

- `GOVERNANCE_AMENDMENT_2026-09-14.md`
- `Documentation/2026-09-14_MTS_V4_CROSS_SECTIONAL_DERIVED_MARKET_STORE_DESIGN.md`
- root `ChatGPT.md`

The 2026-09-14 governance amendment explicitly changes the former Nexus boundary only for reproducible **derived point-in-time market state**. Raw/reacquirable source data such as OHLCV remains temporary cache data.

## Implemented backend components

### Nexus-owned derived market store

`MTS_V4/derived_market_store.py`

Provides:

- immutable `UniverseDefinition`;
- versioned `DerivedFeatureDefinition`;
- immutable `DerivedFeatureSetDefinition`;
- `DerivedMarketQuery`;
- append-only `DerivedMarketUpdateRecord`;
- per-universe/feature-set high-water state;
- incremental lookback planning;
- in-memory test implementation;
- Parquet-backed durable implementation;
- atomic publication ordering: immutable Parquet update file first, manifest advance second;
- query slicing by date/security/features/eligibility.

Normal updates cannot overlap the published high-water mark. Historical correction/rebuild is intentionally a separate future path rather than silent mutation.

### Nexus integration

`MTS_V4/nexus.py`

`ResearchNexus` now exposes `derived_market_store`. The in-memory Nexus owns an in-memory derived store.

`MTS_V4/nexus_json.py`

`JsonResearchNexus` owns a `ParquetDerivedMarketStore` and accepts `derived_market_root` so many campaign-local Nexus JSON documents can share one durable derived market substrate.

### Explicit research scopes

`MTS_V4/research_scope.py`

Adds `SUBJECT`, `UNIVERSE`, `COHORT`, and `EVENT_COHORT` scope definitions while preserving the existing `subject_id` lineage key. For backward compatibility, a universe/cohort scope is represented as the active durable owner and row-level `security_id` values identify the participating securities.

This is an additive bridge rather than an invasive rewrite of every Analysis contract.

### Derived market evidence materialization

`MTS_V4/derived_market_evidence.py`

Materializes only the AI-requested derived market slice from durable Nexus store into normal temporary campaign evidence/cache. Bulk row payload is not placed in the AI prompt by default.

### Generic cross-sectional Analysis

`MTS_V4/cross_sectional_analysis.py`

Adds:

`analysis.cross_sectional.rank`

The RD chooses the value column, grouping columns, output column, and ranking direction. Deterministic code performs only exact within-group percentile ranking and exposes a reusable derived dataset.

### Production bootstrap wiring

`MTS_V4/bootstrap.py`

Now registers:

- `analysis.cross_sectional.rank`;
- the previously existing but unwired `analysis.measurements.participation_context`.

`build_runtime` and `build_batch_runtime` now optionally accept `derived_market_root` for shared Nexus-derived state.

### Universe Sol runner

`scripts/run_sol_batched_universe.py`

Adds an explicit batched universe research runner. It accepts a universe, feature-set version, date range, optional security IDs and feature columns; materializes a compact requested slice; then uses the existing governed Sol batch research loop and spend guard.

`--dry-run` must be tested before any Sol call.

### Tests added

- `Tests/mts_v4/test_derived_market_store.py`
- `Tests/mts_v4/test_cross_sectional_analysis.py`

These are committed but have not yet been executed on a server.

## Required first server session

Do not authorize Sol spend first.

1. Pull/checkout this branch.
2. Confirm exact HEAD and clean worktree.
3. Run syntax/import checks.
4. Run targeted tests:
   - `Tests/mts_v4/test_derived_market_store.py`
   - `Tests/mts_v4/test_cross_sectional_analysis.py`
   - bootstrap tests;
   - participation-analysis tests;
   - future-cohort waiting tests inherited from parent branch.
5. Run full pytest gate.
6. Patch only evidence-backed defects.
7. Run `scripts/run_sol_batched_universe.py --dry-run` against a small fixture-derived store. Confirm `SOL_CALLS=0`.
8. Audit resume/reconstruction/continuation runners for assumptions that `subject_id` always means one equity ticker.
9. Only after deterministic/backend acceptance should live data acquisition and Sol calibration begin.

## Known items to verify/repair during test pass

These are not claimed defects until reproduced, but deserve explicit attention:

- manifest-loaded JSON lists versus dataclass tuples during idempotent universe/feature-set re-registration;
- sanitization of update IDs used as Parquet file names;
- multi-process writer locking if maintenance/research could write concurrently;
- correction/rebuild transaction semantics;
- outcome/future-information feature access policy at derived-store materialization during VALIDATION/live prediction;
- semantics/naming of the `ascending` argument in `analysis.cross_sectional.rank`;
- whether `load_subject_scientific_context` and continuation/reconstruction code make ticker-specific assumptions for `universe:*` scopes;
- positional-constructor compatibility of inherited `BatchResearchLoopOutcome` waiting-state field changes.

## Point-in-time S&P history remains intentionally unresolved

No current-S&P-members-projected-backward dataset has been fabricated. The durable store supports a point-in-time universe definition, but the authoritative membership source and historical build procedure must be selected and tested on the server before the initial S&P historical substrate is produced.

## Scientific acceptance gate before expensive autonomous discovery

The repaired assembled system should be challenged with known-effect controls without telling the AI the expected answer/direction:

1. cross-sectional momentum;
2. medium-term trend persistence;
3. short-horizon reversal;
4. post-earnings announcement drift;
5. a negative control;
6. universe request/lineage/cache lifecycle control.

## Qwen gate

Do not release Qwen as autonomous Research Director yet.

Sequence:

1. deterministic backend passes;
2. Sol establishes the benchmark on controls and selected historical research;
3. preserve Sol Research Packages, Analysis choices, successful paths, rejected paths, findings, negative results, and continuation decisions;
4. bring Qwen up in supervised replay/shadow mode against those Sol historical traces;
5. compare Qwen behavior to the Sol benchmark;
6. authorize Qwen autonomy only after it demonstrates contract competence and useful scientific behavior.
