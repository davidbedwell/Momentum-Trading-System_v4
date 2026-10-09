# Gen1 Recovery/Failure Path Study — Approved 2026-10-09

Status: USER APPROVED RESEARCH PROTOCOL; NOT AN APPROVAL TO CHANGE GEN1 PARENT SELECTION OR LAUNCH GEN2.

Objective: Independently assess whether learned chronological recovery-versus-failure signatures and executable exits improve Gen1 genome evaluation relative to the frozen EV/reliability/horizon-consistency/diversity rubric.

Population: retain all 4,360 archived Gen1 candidates; preserve original provisional 168 identities, scores, rankings, and archived observations unchanged. Do not screen new-study eligibility using original rankings.

Data governance: DEV80 only for design and chronological out-of-training evaluation. DEV37, DEV50 and BLIND17 protected. Do not use protected banks without a separate approval.

Design: at each causal decision time construct observable path features, define mutually distinguishable recovery/failure/other outcomes and payoff horizons in advance, fit calibrated models on past training periods, and evaluate exit-versus-hold decisions on subsequent periods. Do not prescribe a 60% exit threshold; learn economically justified boundaries and quantify uncertainty. Model fitting and threshold selection must be nested inside chronological training folds; no leakage through overlapping trade paths, feature preprocessing, or outcome labeling.

Compare: baseline net EV and rank versus learned-exit executable EV and rank; Spearman/Pearson correlation with uncertainty; top-168 overlap; long/short, holding-window, regime, and era breakdowns; paired path-managed versus no-learned-exit performance; MAE/tail loss; cost, slippage, and opportunity forgone; portfolio CAGR/MDD when a validated capital-constrained simulator exists. Evaluate selection-bias and multiple-comparison effects.

Compute governance: preflight schema/causality/cost checks and small benchmark first; cache reusable feature paths, report runtime/memory/unique genome counts, checkpoint and resume; no unbounded full-population run until benchmark and scientific protocol checks pass.

Decision: diagnostic research only. Report correlations and disagreements before requesting an explicit amendment to the frozen parent-selection criteria. No Gen2 breeding until original certification gates are satisfied.
