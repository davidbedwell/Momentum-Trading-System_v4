# Gen1 hierarchical path study — prospective design freeze (2026-10-09)

Status: DESIGN FROZEN, IMPLEMENTATION PENDING. The 12-genome single-checkpoint smoke test is engineering-only, not inferential evidence.

## Scope and governance
- All 4,360 archived Gen1 genomes remain eligible. Original 168 provisional parents, ranks, scores and allocations remain untouched.
- DEV80 only for engineering, fitting, tuning and internal chronological tests. DEV37, DEV50 and BLIND17 are prohibited without separate approval.
- No Gen2 launch or change to parent selection from this study alone.
- Study primary question: does causally learned, economically chosen exit management add out-of-training executable value, and how does the resulting genome ordering relate to the frozen Gen1 rubric?

## Dataset and efficient representation
- Cache once the PIT date/security aligned OHLC-based trade checkpoints, T+1 entry prices, execution prices, market/sector context and past-only state features.
- Store a canonical event key (security, entry date, side, decision checkpoint, horizon) and a separate sparse mapping from each genome to its qualifying events. Deduplicate identical events for model fitting, NOT for genome performance counting.
- Measure peak memory, event count, event reuse, feature-build time, compile time, fitting time and inference time. Use immutable content hashes and checkpoints.
- Validate causality with executable perturbation tests: changing future data cannot alter past features or decisions; no post-exit outcome used in features.

## Targets and policies
- Predeclare actionable continuation horizons and terminal/competing outcomes: economically meaningful recovery, economically meaningful deterioration and neither, with explicit censoring. A past excursion is a feature only if known at the checkpoint.
- Model conditional recovery/failure/other probabilities and future net payoff distributions; calibration is mandatory. Do not assume recovery and failure are complementary.
- Fit a regularized pooled model, a partially pooled genome-aware model with shrinkage, and one bounded nonlinear challenger. Compare against no learned exits and fixed simple-stop baselines.
- Exit/hold is chosen by out-of-training estimated conditional value and downside constraints versus liquidation/redeployment after realistic execution costs. No arbitrary 0.6 probability threshold.
- Train all preprocessing, hyperparameters, calibration and decision policies within historical folds; never choose based on test outcomes. Account for dependent paths and overlapping forward labels.

## Validation and comparison
- Expanding walk-forward train/calibration/test with a horizon-based purge and embargo; minimum fold support and number of independent episodes must be declared before results are used to promote.
- Evaluate calibration (Brier, reliability, class frequencies), conditional payoff estimation, executable trade net EV, adverse tails, exit fraction and opportunity costs; evaluate CAGR/MDD only with an auditable capital-constrained portfolio simulator.
- Compare original and new genome ranks with Spearman and Kendall, Pearson for numerical measures, top-168 overlap, and discordant examples; stratify by side, horizon, sector, era and market episode.
- Cluster/episode-block uncertainty, sensitivity to episode removal, multiple-comparison adjustment across genome candidates, and selection-corrected portfolio replay required before parent-selection recommendations.
- Report unsupported genomes as insufficient evidence, not zeros or failures; separate exploration from confirmation.

## Staged execution gates
1. Inspect smoke-test results and validate path data/cost alignment and true checkpoint observability.
2. Benchmark shared event-store build and a representative stratified set (LONG/SHORT, horizon windows, entry frequencies), measure memory/time and extrapolate with uncertainty.
3. Validate walk-forward pipeline, leakage tests, calibration, and paired no-exit baseline on development data; stop on failed controls.
4. Scale all 4,360 with resumable partitions and cache; do not use original rank to exclude candidates.
5. Produce correlation, uncertainty, disagreement and portfolio analyses; no changes to frozen Gen1 selections without explicit approval.

## Fail-closed rules
- No statistical-certification claim from the 12-genome pilot.
- No claims of independent evidence from duplicated same-day or same-crash stock trades.
- No leakage through future extrema, label windows, calibration, model selection, overlapping folds, or genome-level re-use.
- No retroactive changes to the frozen Gen1 criteria; no protected heldout access.

## Approved addition: matched distressed-winner versus loser analysis (2026-10-09)
- At each failed trade's warning checkpoint, retrieve comparable states from successful trades of the same genome at ANY historical checkpoint, then from strategy-family and pooled trades where same-genome support is inadequate.
- Match on the then-observable trajectory, adverse excursion, elapsed time or explicitly analyze elapsed time as a differentiator, volatility, and regime; report match quality, common support and sample size. Do not match on ultimate outcomes or future path features.
- Quantify how frequently failure signatures also occur in eventual winners (false-exit risk), and which additional contemporaneously observable factors distinguish subsequent recovery from continued deterioration.
- Measure sensitivity, specificity, precision, calibration, lead time before deterioration, missed recovery payoff, and realized incremental net EV under causal replay; report uncertainty by independent episode and leave-episode-out sensitivity.
- In hindsight autopsy future paths may be inspected freely to form outcome labels and hypotheses. In walk-forward validation, matching libraries, fitted discriminators and exit rules must be trained exclusively on prior periods; evaluate on withheld future episodes.
- If no reliable differentiator exists, report ambiguity and abstention rather than force an exit; preserve original parent rankings until a separately approved governance change.
