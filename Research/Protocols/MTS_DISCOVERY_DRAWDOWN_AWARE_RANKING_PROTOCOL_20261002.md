# MTS v4 — Discovery Drawdown-Aware Ranking Protocol — 2026-10-02

## Objective
Test whether the causal EV/p10 ranking edge can retain higher terminal wealth while reducing tail deterioration by scaling only new-entry risk during ongoing portfolio drawdowns.

## Evidence boundary
Discovery Development only for candidate generation. Discovery Holdout remains closed. No additional Verification A and no Verification B access.

## Fixed ranking architecture
Same-day top-50% EV/p10 fixed-budget redistribution. Test caps 1.20x, 1.25x, and 1.50x. The EV/p10 predictor and ranking are unchanged and causal.

## Causal drawdown state
Before each session's new entries, compute portfolio equity from the prior close and compare it with the strategy's own prior equity peak. Only that already-observed drawdown may affect new-entry risk. No same-day or future price information may enter the guard.

## Frozen guard families
1. Mild: drawdown >=5% -> 95% new-entry risk; >=10% -> 90%.
2. Moderate: drawdown >=10% -> 95%; >=20% -> 90%.
3. Strong: drawdown >=5% -> 90%; >=10% -> 80%.
Normal state remains 100% risk.

For each guard, run both ranked sizing and equal sizing under the identical guard.

## Gate
A ranked guarded candidate must:
- exceed ordinary unguarded equal100 terminal wealth;
- exceed equal sizing under the same drawdown guard;
- have max drawdown and CVaR5 each no worse than ordinary unguarded equal100;
- retain the unchanged trade-level EV/p10 breadth/CI/concentration gates.

## Stability
Require at least four passing combinations spanning at least two caps and two guard families before any Holdout replay. Prefer a simple central representative, not the wealth maximum.

## Integrity
No parameter adjustment from Verification evidence. No relaxation of tail-risk requirements.
