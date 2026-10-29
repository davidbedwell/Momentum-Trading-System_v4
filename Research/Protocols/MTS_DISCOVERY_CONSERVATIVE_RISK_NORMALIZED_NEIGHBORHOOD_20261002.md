# MTS v4 — Conservative Risk-Normalized Ranking Neighborhood — 2026-10-02

## Purpose
Determine whether the clean Development pass at fixed-budget same-day EV/p10 ranking is part of a broad conservative plateau rather than an isolated parameter point.

## Evidence boundary
Discovery Development only. Discovery Holdout remains closed. No Verification A/B access.

## Frozen neighborhood
Same-day top-50% EV/p10 fixed-budget redistribution only.
- caps: 1.10x, 1.20x, 1.25x
- total portfolio risk scales: 85%, 90%, 95% of ordinary equal-sizing base trade fraction
No intermediate values, optimization, or outcome-dependent expansion.

## Gate
Unchanged from the prior risk-normalized protocol: candidate wealth must exceed ordinary equal sizing at 100% risk and equal sizing at the same risk scale; max drawdown and CVaR5 must each be no worse than ordinary equal100; trade-level breadth/CI/concentration gates remain unchanged.

## Plateau criterion
A family is considered structurally supported only if at least four of the nine frozen neighborhood combinations pass, spanning at least two caps and two risk scales. Prefer a representative near the middle of the passing region, not the highest-return point.

## Integrity
No Holdout or Verification evidence. No relaxation of risk criteria.
