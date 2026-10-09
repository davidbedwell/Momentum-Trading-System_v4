# Gen1 SHORT replay validation — 2026-10-09

Status: FAIL — do not run environment-conditioned analysis from reconstructed signals yet.

Recovered source components:
- Core/layered_ga/stage2_compiler_v3.py VectorSignalCompiler
- Core/layered_ga/stage2_evaluator_v3.py evaluate_curve and cluster_ids_from_frame
- Core/layered_ga/stage2_path_v3.py ExecutionPaths and ProspectiveCosts
- DEV80 predictors and frozen execution matrices under stage2-opportunity-v3-20261007/ga4_dev80_checkpoint.

A smoke replay against archived all_candidates.jsonl produced unequal raw counts and EVs:
- Genome 1 SHORT horizon 1: replay n=66721 vs archived n=68641, EV -0.0108478963 vs -0.0108386381.
- Genome 6 LONG horizon 1: replay n=101005 vs archived n=100797, EV -0.0093796765 vs -0.0093801823.
- The sample differences are not a constant offset and persist when removing the extra eligible mask.
- Thus exact signal-row lineage / threshold semantics / predictor snapshot must be reconciled before conditional environment estimates.

No protected data touched. No new Gen1 selection or reproduction authorized. Do not claim exact replay or environmental findings.
