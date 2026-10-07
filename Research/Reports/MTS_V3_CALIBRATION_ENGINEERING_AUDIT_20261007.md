# V3 calibration engineering audit — initial verified findings (2026-10-07)

Status: OPEN — static code audit; no full run certified. Source branch: research/layered-contextual-ga-redesign-20261007, evidence commit 66ef099.

## Confirmed blocking defects
1. `scripts/run_stage2_v3_evolutionary_calibration_20261007.py` computes fitness as `effect * count(valid & target) / count(valid)`. This accesses the known synthetic injection mask and magnitude directly, instead of evaluating observed planted-vs-null net returns with the frozen full-horizon curve evaluator. It is an oracle-assisted target-overlap search, not a blind recovery calibration.
2. Its evaluator selects only `day=points[1]`, so it does not evaluate days 1–63 or stable temporal plateaus, contrary to `MTS_STAGE2_V3_FAIR_CALIBRATION_FREEZE_20261007.md`.
3. `ev.best` includes the explicitly evaluated planted target baseline before the GA starts; consequently `best_ga >= baseline` cannot demonstrate evolutionary improvement. The reported `target_visited` is not sufficient evidence of scientific recovery.
4. Zero-effect nulls receive exactly zero fitness for all eligible genomes, making target-specific false discovery impossible by construction. No matched statistical null-recovery comparison is implemented.
5. The script ends unconditionally at `STOPPED_ENGINEERING_FULL_BUDGET_AND_STATISTICAL_GATE_PENDING`. No statistical certification/handoff can occur from this executable.
6. `run_stage2_v3_calibration_20261007.py` tests only injected incremental response on target rows, not actual net EV or confidence intervals. Its `shape` function uses repeated interpolation x coordinates for FAST (`[1,1,3,7,12,63]`), requiring explicit boundary/shape tests.
7. Recorded `failure.json` reports injection-alignment mismatch `4.601199179887772e-06` against `1e-7` for MOMENTUM FAST 0.0025. The committed code alone does not establish whether this was a prior revision or a currently reproducible defect. Preserve as historical evidence; do not silently raise the tolerance.
8. `Core/layered_ga/stage2_evaluator_v3.py` already implements 1–63 curve statistics and long/short costs, but the evolutionary calibration does not use it. Its current LCB uses equal-weighted security-year cluster means for SE and row-weighted EV; assess this mismatch and temporal dependence before claiming calibrated coverage.

## Required repairs (do not change frozen scientific thresholds)
- Build a deterministic outcome-only plant/null evaluator calling the real `evaluate_curve` for both sides across all 63 horizons, without giving GA access to target identity, effect size, or injected shape.
- Evaluate target baseline independently of evolutionary best; report best only from actual GA ledger.
- Add explicit null false-positive checks, independent-N and LCB95 requirements, and planted plateau overlap using pre-frozen criteria.
- Verify calibration shapes, alignment, finite masks, clustering and causal costs with executable unit/property tests.
- Add finite budgets, checkpoints, auditable completion and fail-closed supervisor handoff.
- Do not open protected stock banks, alter search families, tune scientific gates to observed results, or launch paid compute until local tests and preflight pass.

## Evidence
- `Research/Runs/layered/stage2-opportunity-v3-20261007/calibration/{failure,status,plant_integrity_results,evolutionary_results,target_manifest}.json`
- `scripts/run_stage2_v3_calibration_20261007.py`
- `scripts/run_stage2_v3_evolutionary_calibration_20261007.py`
- `Core/layered_ga/stage2_evaluator_v3.py`
- `Research/Design/MTS_STAGE2_V3_FAIR_CALIBRATION_FREEZE_20261007.md`

This is an initial audit record, not certification that engineering corrections have been implemented or tested.
