# Generation 1 Pareto Parent Ranking — Frozen 2026-10-08

Status: USER APPROVED; FROZEN. Supplements GEN1_HORIZON_REFINEMENT_AND_RATING_FREEZE_20261008.md. Do not silently alter.

## Approved model
- Use MULTIDIMENSIONAL PARETO ranking, not a single weighted composite or EV/MAE quotient, to evaluate eligible candidates for subsequent parent selection.
- Parent selection dimensions at this stage: absolute net expected value (EV_net), statistical confidence/reliability (accounting for overlapping observations and multiple comparisons), holding-horizon consistency, and genetic/behavioral diversity. Preserve meaningful tradeoffs and non-dominated candidates; do not force a fixed number of survivors.
- Compare economic performance across appropriately matched horizons, execution assumptions, direction, and costs. Report matched passive EV and excess EV separately as diagnostics only; do not make passive excess an eligibility or selection gate without later approval.
- MAE (mean, worst-5% tail) and EV/MAE are measured and reported in a separate risk-quality diagnostic, but NOT used for parent eligibility, Pareto dominance, ranking, filtering, elimination, or breeding-parent selection in this generation. MAE-dependent exits are a separate later research and validation question.
- Maintain original candidates and complete results in an immutable research archive; keep protected banks DEV37, DEV50, BLIND17 untouched.
- A planning target around 128 breeding parents is NOT a hard cutoff or a frozen quota; actual number depends on credible evidence and diversity.

## Pending definitions / non-authorization
- This freezes the Pareto MODEL and allowed dimensions, not numerical screening thresholds, precise objective transformations, statistical tests, dominance tie handling, or parent-count algorithm. These must be specified and frozen BEFORE applying selection to results.
- Do not use this approval to start Generation 2, alter the running Phase A evaluation, or bypass Phases B–D / scientific certification.
