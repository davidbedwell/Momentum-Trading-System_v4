# G3 scientific classification — frozen correction (2026-10-10)

**Experiment:** `Research/Runs/gen3-v2-eta-pilot-20261010`

**Correct designation:** **G3 — MIXED-REGIME EVOLUTION (NORMAL + CRASH EXPOSURE)**.

**Do not call this run "Normal-market evolution", "Normal-only GA", or "Normal-certified".** Its candidate selection and fitness evaluations include crash intervals and therefore do not represent the actual Normal-only deployment opportunity set under A/B/C–R-1.

## Scientific consequences
- False rejection: Normal-profitable chromosomes can be removed because they suffer during periods when the production controller would liquidate Normal holdings.
- False promotion: crash winners can dominate the fitness ranking even though the Normal strategy would be in cash.
- Post-hoc masking/reranking cannot recover unexplored descendants of previously eliminated chromosomes.
- Retain every genome, parentage record, signal and evaluation as exploratory evidence; mark all current results **MIXED_REGIME_UNCERTIFIED_FOR_NORMAL**.
- Historical calendar crash masks may be used only for a separately labeled sensitivity analysis; production and definitive Normal fitness must use causal A/B/C and R-1 declarations and next-executable-open exits.

## Compute governance
- Do not start another GA, restart this run, or schedule a new full rerun without explicit authorization.
- Existing G3 process was running when this classification was recorded. This document **does not authorize stopping it**.
- Preserve current run artifacts and checkpoints; analyze already paid-for evaluations first.
- Separate prospective Normal-only and Defensive research, and reserve full mixed-market evaluation for end-to-end controller validation.