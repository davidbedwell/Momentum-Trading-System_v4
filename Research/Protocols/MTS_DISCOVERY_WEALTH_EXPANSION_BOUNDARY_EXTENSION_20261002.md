# MTS v4 — Discovery Wealth Expansion Boundary Extension — 2026-10-02

## Reason
The prospectively frozen 1.10x–2.00x Development search showed no wealth-response rollover by the upper 2.00x boundary. Same-day top-25% at 2.00x produced 19.495452x wealth, 56/56 positive tickers, 16/17 positive years, 8/8 positive families, max drawdown approximately equal to baseline, and a positive ticker-cluster CI. Therefore 2.00x is a censored search boundary, not a scientifically established optimum.

## Objective
Using Discovery Development only, extend the coarse per-trade multiplier boundary to identify whether/where terminal wealth rolls over or risk accelerates disproportionately.

## Frozen architecture
No new predictor or architecture generation. Test only the already-supported same-day relative EV/p10 ranking architecture at top fractions 25% and 50%, plus absolute boost as a control.

## Extension grid
Maximum multipliers: 2.25x, 2.50x, 3.00x, 3.50x, 4.00x. This is intentionally coarse. Stop extending once a clear wealth rollover or disproportionate risk escalation is observed across neighboring points. Do not fine-tune around a local maximum.

## Evaluation
Same metrics and breadth/concentration/cluster-CI requirements as the parent causal wealth expansion protocol. Report ordinary equal and exposure-matched controls. Identify the non-dominated wealth/maxDD/CVaR frontier.

## Evidence boundary
Discovery Development only. Do not open Discovery Holdout until representative broad frontier policies are frozen. No additional Verification A. Verification B remains sealed.
