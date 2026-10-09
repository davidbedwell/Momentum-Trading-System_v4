# Gen1 Path Study Consolidation Decision — 2026-10-09

Decision: RETIRE the matched-checkpoint terminal-loss classifier as an active research method. REPLACE it with the Gen1 Path-Conditional Exit GA defined in Research/Designs/GEN1_EXIT_GA_RESEARCH_20261009.md. Preserve historical outputs and failures as immutable evidence; do not delete them.

Salvage: original 4,360 chromosomes, train-only horizon assignments, DEV80 entry signals, original execution arrays, PIT feature tables, path reconstructions, evaluation utilities, provenance and tests. Each asset must pass an independent causal/executable audit before reuse. Do not claim old checkpoint outputs prove an exit policy.

Active scope: Exit GA only for the path/stop research stream. Other ongoing MTS projects remain preserved and paused, not canceled. No new parent promotions. No changes to the 168 parent allocation.

Protected partitions: DEV37 heldout, DEV50 preserved-not-pristine, BLIND17 final blind; do not inspect or use without separate authorization. DEV80 discovery and unseen chronological DEV80 validation only.

Engineering order: (1) inventory and audit salvage, (2) implement deterministic sequential one-exit trade replay with causal next-session fills, (3) test forced horizon exits and counterfactual false signals, (4) small bounded discovery pilot, (5) evaluate untouched later DEV80 trades against simple stop baselines, (6) expand only after predefined economic/risk gates pass.

No GA production launch until replay, PIT, costs, and benchmark gates are demonstrably passing. Retain negative results. This document consolidates the research scope; it does not certify the new method.
