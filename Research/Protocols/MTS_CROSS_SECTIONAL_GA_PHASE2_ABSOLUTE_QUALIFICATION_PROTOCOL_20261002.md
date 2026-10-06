# MTS Cross-Sectional GA Phase 2 — Absolute Qualification Protocol — 2026-10-02

## Status
FROZEN DESIGN / PRE-LAUNCH

## Phase-1 finding carried forward
Scarce-slot selection showed meaningful but regime-dependent signal. Phase 1 mostly kept 95–97% of capital in equities, so its 3% safe asset did not function as a genuine competitor for marginal capital. No Phase-1 chromosome advances as deployable.

## Central hypothesis
A candidate must independently qualify to take capital away from the 3% safe asset before it may compete with other equities or incumbents. Ranking alone is insufficient because a relative winner can still be an absolutely poor investment.

## Decision sequence
QUALIFY AGAINST SAFE ASSET → RANK QUALIFIERS → COMPARE WITH INCUMBENT → ALLOCATE OR KEEP SAFE.

## Frozen evidence boundary
- GA fitness/search: already-consumed 67-stock Discovery population only.
- Architecture holdout: already-consumed 50-stock/four-era cohort, opened only after candidates are frozen.
- Remaining 186 Discovery stocks: sealed.
- Untouched Verification: sealed.
- Opportunity layer: existing 396 portable genomes fixed; no new predictive-gene discovery.

## Absolute qualification
For every candidate on every causal decision date, estimate from completed 67-stock historical outcomes only:
- expected forward return;
- probability of positive return;
- downside p10 magnitude;
- evidence count / uncertainty;
- expected return advantage over the 3% safe asset for the remaining holding horizon;
- transaction friction and robustness margin.

A candidate that fails any active qualification requirement cannot consume equity capital, regardless of relative rank.

## GA qualification genes
The GA may evolve:
- minimum excess expected return over safe asset;
- minimum probability of positive return;
- maximum p10 downside magnitude;
- minimum causal evidence count;
- uncertainty/confidence penalty;
- safe-asset robustness margin;
- confirmation delay.

These are absolute gates. Failure means SAFE, not “rank lower.”

## Competition genes after qualification
Among qualifiers only, evolve:
- slot ceiling;
- ranking score;
- challenger advantage required to displace incumbent;
- minimum hold;
- cooldown;
- family duplication penalty.

The slot count is a ceiling, never a target. Zero qualifiers means 100% safe asset. Two qualifiers with a five-slot ceiling means only two equity positions; the rest remains safe.

## Capital rule
Maximum equity exposure = 100%. Leverage prohibited. Unallocated capital earns 3% annualized. Each marginal equity allocation must independently pass qualification; no forced slot filling.

## Costs
Evaluate cost-matched baseline and controller at 0/10/25/50 bps. Phase-2 GA fitness begins at 10 bps; frozen candidates receive sensitivity afterward.

## Pareto governance
Pareto controls advancement. Controlling objectives remain nonredundant:
- maximize terminal wealth;
- maximize positive-return capture;
- improve max drawdown;
- improve CVaR5;
- minimize negative-return capture;
- minimize turnover.

CAGR, worst day, switch frequency, safe-asset fraction, filled-slot fraction, minimum-era CAGR and net value/switch are robustness diagnostics, not independent rescue dimensions.

## Mandatory diagnostics
For every chromosome report:
- candidate signals seen;
- qualification pass rate;
- rejection counts by EV, probability, downside, evidence and uncertainty gate;
- number of qualified candidates per session;
- safe-asset fraction;
- filled-slot fraction;
- accepted and rejected incumbent switches;
- turnover and costs;
- performance by four eras;
- performance when 0, 1–2, 3–5, and >5 candidates qualify.

## Anti-cheating controls
- No candidate's own eventual return may enter its qualification or rank.
- No heldout50 outcome may update any score or threshold.
- Qualification statistics use only outcomes completed strictly before the decision date.
- No forced minimum equity exposure.
- No leverage.
- No opening remaining Discovery or Verification for tuning.

## Launch sequence
1. Freeze machine-readable Phase-2 chromosome schema.
2. Implement qualification diagnostics and tests.
3. Verify canonical identity and explicit all-safe / all-qualify controls.
4. Commit implementation before fitness search.
5. Run GA on 67 only.
6. Freeze a small Pareto-diverse candidate set.
7. Replay once on the already-consumed 50-stock/four-era holdout.
8. Do not access untouched Verification unless a later explicit gate authorizes it.