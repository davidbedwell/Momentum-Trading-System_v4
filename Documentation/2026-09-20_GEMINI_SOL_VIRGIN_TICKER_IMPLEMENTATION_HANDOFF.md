# Gemini–Sol Virgin-Ticker Equivalence — Implementation Handoff

Date: 2026-09-20
Branch: `mts-v4-gemini-sol-virgin-equivalence-20260920`
Base: `3347c4a8c71487ed37a4311d9928a32fdb3e428d`

## Frozen governance

`Documentation/2026-09-20_GEMINI_SOL_VIRGIN_TICKER_EQUIVALENCE_PROTOCOL.md` is authoritative for this experiment. Do not weaken MTS scientific standards or modify the successful Direct-Sol workflow to accommodate Gemini.

## Implemented

- `MTS_V4/virgin_equivalence.py`
  - fail-closed protocol error;
  - machine-eligible virgin candidate contract;
  - deterministic exactly-three selector;
  - eligible-set and selection freeze hashes;
  - immutable starting-package hashing and arm identity verification;
  - arm completion manifests with required scientific artifacts and usage telemetry;
  - full-record bounded Gemini→Sol appeal context;
  - blinded comparison packaging that strips arm identity and cost;
  - final exactly-three qualification gate;
  - automatic failure for any material Direct-Sol finding missed by hybrid;
  - 35% aggregate savings threshold;
  - no-overwrite frozen JSON writer.
- `Tests/test_virgin_equivalence.py` covers the central frozen invariants.
- `scripts/run_gemini_sol_virgin_equivalence.py` can consume a machine-derived candidate manifest and freeze deterministic selection. It intentionally blocks paid arm execution until repository-specific adapters are proven.

## Deliberate paid-run blocker

Do not hand-author the candidate manifest. The next implementation step must derive it from the repository's authoritative scientific partition, prior-Sol exposure state, prior campaign/artifact state, and starting-data availability. If any source cannot prove virginity, fail closed.

After candidate derivation is tested, bind two adapters without changing scientific behavior:

1. DIRECT_SOL adapter to the frozen successful direct-Sol workflow.
2. GEMINI_SOL_HYBRID adapter using Gemini as RD with identical starting evidence/methods, followed by a bounded Sol appeal receiving the complete Gemini work product and every hybrid Analysis result.

Both adapters must consume the same frozen starting-package SHA for each ticker and write only to separate arm roots.

## Required before first paid call

- run the full existing test suite plus `Tests/test_virgin_equivalence.py` locally/Thunder as appropriate;
- prove candidate-manifest derivation against authoritative partition/exposure stores;
- prove arm-start hash equality;
- prove no cross-arm artifact/context path exists;
- prove hybrid appeal sees full evidence/results/work product;
- prove appeal cannot restart unrestricted Direct Sol;
- prove provider usage telemetry is mandatory and actual cost is aggregated;
- prove blinded comparator cannot see arm identity or cost before scientific freeze.

No API/GPU spend has been authorized or initiated by these commits.
