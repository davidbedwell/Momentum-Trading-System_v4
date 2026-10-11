# Corrected Normal-regime evolutionary experiment — preflight specification

Status: PREPARATION ONLY. NO GA AUTHORIZED OR LAUNCHED.

Predecessor: G4 mixed-regime evolution, halted at generation 91. Its checkpoint and all child evidence must remain immutable. Do not use its mixed-regime fitness rankings as Normal certification.

## Required before new compute
1. Obtain point-in-time Parquet inputs and independently computed A, B, B1, C and six-element R-1 signals. Freeze hashes and provenance. Fail closed on missing dates or signals.
2. Replay controller with A/B/B1/C precedence over R-1 on simultaneous triggers. Verify daily state continuity and no lookahead.
3. For Normal-only evaluation: permit entries only after Normal close-state decisions; fill at next executable open; cancel pending Normal entries and liquidate all Normal positions at next executable open after Defensive declaration, with realistic costs, suspended symbols and cash accounting.
4. Preserve both original mixed-regime scores and corrected scores for the same archived genomes. Quantify rank changes, outlier sensitivity, and crash-boundary effects. Reranking alone does not restore eliminated evolutionary branches.
5. Test with deterministic fixtures for same-day conflict, missing signals, holidays, halt/unfilled orders, next-open execution, costs, and R-1 release. Verify all test assertions and immutable input checksums.
6. Require a preflight scientific certification and explicit user approval before launching a new GA. No DEV50 or BLIND17 access during design.

Do not substitute calendar crash exclusion for the causal controller in final fitness. Calendar exclusions may be separately reported as a sensitivity diagnostic only.