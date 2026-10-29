# MTS Phase 3 — Hierarchical Evidence / Specificity Protocol
Frozen: 2026-10-02, before Phase-3 results.

## Question
Can MTS preserve the value of genome-specific evidence while allowing causally available family/global evidence to support immature genomes, without treating broad evidence as equally trustworthy?

## Evidence boundary
Search/fitness uses only the already-consumed 67-stock Discovery development lab and the same four fixed eras. No remaining 186 Discovery or Verification banks are opened. No Phase-3 result may alter an era boundary or opportunity genome.

## Evidence model
For every signal, retain genome, family, and global completed-outcome histories separately. Only outcomes whose exit date is strictly before signal date are available.
A chromosome chooses a specificity policy rather than a single destructive fallback bucket.

Candidate policies:
- SPECIFIC_ONLY: genome evidence only; if insufficient, reject.
- HARD_FALLBACK: genome -> family -> global, each must meet required n.
- SHRINKAGE: combine available genome estimate with broader prior using causal empirical shrinkage.
- PENALIZED_FALLBACK: fallback is allowed, but family/global estimates receive explicit uncertainty/margin penalties.

## New genes
- evidence_policy: SPECIFIC_ONLY, HARD_FALLBACK, SHRINKAGE, PENALIZED_FALLBACK
- genome_min_n: 100, 150, 250, 400, 750
- family_min_n: 250, 400, 750, 1250
- global_min_n: 750, 1250, 2500
- family_borrow_penalty_bps: 0, 25, 50, 100, 200
- global_borrow_penalty_bps: 25, 50, 100, 200, 400
- shrinkage_prior_strength: 50, 100, 250, 500
Existing qualification/competition genes remain available.

## Controls
The tournament must include the corrected Phase-2 frozen four plus old EQUAL/FIXED3/BROAD/RISK15/RELATIVE6 controls. Phase-3 candidates are compared at identical 0/10/25/50 bps costs.

## Selection governance
Pareto controls advancement; search is not limited to the current frontier. Controlling objectives remain terminal wealth, max drawdown, CVaR5, positive capture, negative capture, and turnover. Four-era positivity is a robustness gate. Safe fraction, minimum-era CAGR, slot utilization, evidence source mix, and qualification reasons are diagnostics.

## Interpretation
No candidate is deployable from this development lab. Broad evidence is not assumed equivalent to specific evidence. A result is scientifically interesting only if it identifies how specificity, uncertainty, and qualification interact; simply increasing trade count is not success.

## Frozen limitation
This is a post-diagnostic hypothesis generated after observing Phase-2/tournament behavior. It therefore cannot be described as independent validation. Prospective validation requires a still-sealed bank after the mechanism and candidate are frozen.
