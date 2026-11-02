# Competitive Portfolio GA (GA6 + GA7)

Status: architecture contract only; optimizer not yet implemented or validated.

## Objective
Evolve a causal capital-allocation/position-management policy over immutable GA6 and GA7 candidate signals, maximizing out-of-sample economic value relative to defended SPY (A_v2/B/B1/C + R-1). This is a selector GA, not a new trade-signal discovery GA.

## Genome / policy controls
- Comparable, causal opportunity scoring from entry features and chromosome provenance; never use future realized trade P&L.
- Holding-versus-entry replacement thresholds; trade/hold/reduce/add/exit/cash decisions.
- Position weights, concentration and correlation penalties within hard risk limits.
- Opportunity competition without guaranteed GA-family quotas.
- Regime-conditional decisions; defense state overrides entry and liquidation decisions.
- Costs/turnover and uncertainty penalties, calibrated using discovery training folds only.

## Hard invariants
- One $100,000 shared bankroll, exact same defense controller as defended SPY.
- Signals at close, fills no earlier than next open; no hindsight selection.
- Initially <=10% per symbol; <=2% equity risk per trade; sector/correlation and settlement rules enforced in shared execution kernel, not negotiable GA genes.
- No allocation to losing/no-edge signals required; SGOV/cash permissible.
- Same fill, cash, mark-to-market, corporate action and fee rules for all genomes.
- Training fitness computed by full chronological portfolio replay, not synthetic proxy scores.
- Matured counterfactual outcomes can inform training only after they become observable.
- Selection across training folds and untouched proof separated; freeze before DEV87.

## First implementation gates
1. Normalize and parity-test GA6 and GA7 dated signals against existing research ledgers.
2. Implement common event-driven replay and verify deterministic cash/NAV/defense parity.
3. Implement a simple deterministic competition baseline (no GA) as a control.
4. Evolve portfolio policy genomes with chronological training/validation folds and explicit complexity penalties.
5. Compare GA6-only, GA7-only, combined deterministic, combined Competitive GA and defended SPY; freeze before independent proof.

## Failure/stop rule
If the competitive GA cannot beat defended SPY and the deterministic selector after costs on forward chronological validation, do not promote or expand production engineering. Preserve negative evidence.

## Mandatory regime and niche analysis/discovery
The Competitive GA must ingest causal time-t market regime features (trend, volatility, breadth, momentum, recovery) and per-symbol niche memberships, strengths, and distances. The existing A_v2/B/B1/C + R-1 defense controller is authoritative for defense transitions and overrides competing portfolio policies. Existing GA6/GA7 niches are starting knowledge, not a closed taxonomy. Research must permit discovery of new regimes and overlapping stock niches, including descriptive patterns with no proven trading edge. Niche model construction, centroids/radii, membership ranks, and any learned regime boundaries must be trained only on preceding chronological data and reconstructed point-in-time for each validation fold; recompute cross-sectional ranks after eligible-universe filtering. Distinguish descriptive niche discovery from profit validation, and do not permit future realized returns or hindsight crash labels into time-t features. Candidate genomes may evolve regime/niche-conditioned scoring, allocation, hold/replace and cash behavior, while the defense state machine and hard risk/execution controls remain external. Compare incremental performance against an otherwise identical competitive selector without regime/niche features to quantify their actual contribution.

## Hybrid niche-discovery architecture (approved direction)
Use the existing GA6/GA7 chronological niche discovery and PIT membership reconstruction as the initial, shared feature service; inspect and certify actual source implementation before wiring. Add a separate Competitive GA niche-research extension that discovers novel descriptive patterns or intersections when existing niches fail to discriminate chromosome outcomes. Do not allow each portfolio genome to independently redefine all niches. Version niche definitions, model training cutoff, centroids, radii, memberships, provenance and feature calculation; publish only from prior chronological training data. Each competitive genome may select, weight, combine or ignore available niches, but cannot alter their historical definitions. Newly proposed niches are evaluated on later discovery-validation folds, with ablations against existing-only niches and no-niche baseline. Approved additions become available in subsequent GA iterations, never retroactively within a fold. Existing crash-defense A_v2/B/B1/C + R-1 remains separate and authoritative. Final heldout DEV87 remains untouched until freeze.

## Authoritative flow ordering
Market state at t -> Risk + A_v2/B/B1/C + R-1 defense (hard permissions and overrides) -> GA6/GA7 proposals -> Competitive GA -> next-open execution with final independent risk/defense recheck -> NAV/ledger. Defense exits do not depend on the presence of new proposals.
