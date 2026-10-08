# GA4 Machinery Salvage Inventory — 2026-10-08

## Inspection scope and limits
Inspected existing Thunder-connected working checkout `/home/ubuntu/mts-layered-run-20261007` (branch `research/layered-contextual-ga-redesign-20261007`) without switching branches, cleaning files, overwriting local artifacts, or starting compute. This is a **first-pass source inventory**, not a full recovery certification.

## Surviving committed machinery
- `scripts/run_ga_redesign_approved_20261006.py`: `folds`, `dynamic_peer_context`, `execution_returns`, `spread_cost_bps`, `build_arrays`, `random_module`, `random_genome`, `mutate`, `opportunity`, `simulate`, `evaluate`, `evolve_fold`, `calibration`, `main`. **Useful starting implementation.** Its `dominates` function at line 210 compares `cagr` and `mdd`, so GA4 must replace that discovery objective, not reuse it unchanged.
- `Core/conforming_ga/ga_g2.py`: Pareto/dominance, hypervolume, behavioral descriptors, selection, archives, migration, evaluation jobs, and evolutionary controller. Source of reusable mechanics, NOT an authorization to revive G2 scientific design.
- `Core/layered_ga/stage2_nsga2_engine_v3.py`: individual, environmental selection, `evolve`; inspect whether its candidate/evaluation contracts can support a persistent GA4 relationship catalog.
- `Core/layered_ga/stage2_calibration_ga_adapter_v3.py`: matched evaluator.
- `scripts/run_stage2_v3_nsga2_batch_20261007.py`: evolutionary batch orchestration.
- `scripts/run_horizon_free_ga_frozen_architecture_v2_20261005.py` and `scripts/run_horizon_free_ga_final_study_20261005.py`: prior lifecycle and horizon-free work to assess for reuse.
- Multiple defensive GA runners and related tests remain present; keep separate from normal conditional research.

## Working tree protection
At inspection, `git status --porcelain` showed 43 modified/untracked entries, including locally untracked `Core/layered_ga/ga4_*.py`, tests, calibration evidence, feature caches, and the fresh50 frozen membership manifest. **Do not checkout/switch/pull/clean/reset the working directory without first preserving these artifacts.** No destructive operation performed in this inventory.

## Engineering decision
Do NOT rerun G0 pretests or rebuild an evolutionary engine from scratch. Salvage the most complete existing runner and controllers. Change the evaluation and persistence contracts to preserve environment-conditioned 1–4 chromosome interactions, forward horizons 1–63, EV, MAE, uncertainty, and failure conditions. Retain portfolio simulation as downstream analysis rather than global discovery fitness. Test only inexpensive mechanics, data-leakage controls, and reproducibility before substantive DEV80 research.

## Next implementation work (not yet completed)
1. Preserve dirty-tree artifacts and back up the fresh50 membership manifest without opening outcome data.
2. Compare the October 6 runner, G2 mechanics, and Stage2 NSGA-II engine for compatibility and identify exact reusable interfaces.
3. Implement conditional relationship catalog and horizon evidence output, with regression tests.
4. Verify four-fold DEV80/37 isolation and risk-policy integrity before paid compute.
5. Execute DEV80 discovery only when the real scientific prerequisites are satisfied.

## Governance
All future GA4 commits target `research/ga4-conditional-relationships`. Existing historical branches and uncommitted checkout files are not to be overwritten. The approved charter is `Research/Protocols/GA4_CONDITIONAL_RELATIONSHIP_RESEARCH_CHARTER_20261008.md`.
