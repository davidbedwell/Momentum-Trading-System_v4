# MTS Defensive Strategy-Bank Generalization Autopsy — Findings
Date: 2026-10-05

## Status
Diagnostic autopsy completed under the frozen protocol. No remaining Discovery, Verification A, or Verification B evidence was accessed. No finalist, threshold, or strategy was repaired from replay evidence.

## Executive finding
The large DEV50-to-50+17 performance divergence is real, but it is not well explained by a different broad signal-family mix or by disappearance of candidate opportunities. The dominant evidence is consistent with **development-specific conditional overfit amplified by highly correlated bear-market observations**.

The label “50 development stocks” materially overstates the independent information available to GA. Only 42 DEV50 names generated signals inside the six frozen Defensive windows (the other eight had no signals in those windows, not missing files), and within each bear episode the cross-stock candidate returns were strongly correlated. Median pairwise correlations ranged from 0.236 to 0.640. Under a simple equal-correlation effective-N approximation, 28–42 participating stocks behaved like only about 1.54–3.84 independent cross-sectional units per episode.

## Q1 — Effective independence
DEV50 Defensive-window candidate rows: 19,302.
Unique Defensive-window dates: 836.
GA's merged ticker/date source events: 10,159.
Contributing DEV50 tickers: 42.

Median pairwise cross-stock candidate-return correlation and correlation-implied effective ticker count:
- GFC: r=0.441; 28 tickers; effective N ≈2.17
- 2011: r=0.496; 30 tickers; effective N ≈1.95
- 2015–16: r=0.236; 31 tickers; effective N ≈3.84
- 2018: r=0.408; 38 tickers; effective N ≈2.36
- COVID: r=0.640; 40 tickers; effective N ≈1.54
- 2022: r=0.317; 42 tickers; effective N ≈3.00

The replay population shows the same broad correlation structure (effective N ≈1.66–3.37 per episode). Therefore the result is not that DEV50 alone was unusually correlated; bear-regime cross sections themselves provide far fewer independent observations than the ticker count suggests.

## Q2 — Episode transport
All five Pareto finalists degraded materially on replay:
- PF1 CAGR 47.64% -> 12.81%; max DD -8.94% -> -15.64%; 5/6 replay episodes positive.
- PF2 29.22% -> -0.68%; max DD -7.46% -> -12.08%.
- PF3 26.78% -> -2.09%; max DD -6.62% -> -12.63%.
- PF4 17.16% -> 3.21%; max DD -4.22% -> -3.98%.
- PF5 8.17% -> -4.73%; max DD -2.25% -> -8.39%.

PF1 did not fail uniformly: GFC +21.74%, 2011 +8.31%, 2018 +5.65%, COVID +7.58%, 2022 +7.70%, but 2015–16 -7.58%. Its drawdown deterioration is therefore both generalization loss and episode-sensitive.

## Q3/Q4 — Stock and family transport
Broad candidate-family composition is highly similar between DEV50 and combined replay. Total-variation distance across the eight family shares is only 2.26 percentage points. This does not support a simple family-mix explanation.

Candidate-layer economics weakened, but modestly relative to finalist collapse:
- DEV50 all Defensive-window candidate rows: mean forward return +2.82%, win rate 58.00%.
- Replay: mean +2.13%, win rate 57.11%.

Every major family remained positive on average in replay. Thus the second bank did not simply lack candidate opportunities.

## Q5 — Candidate preselection and GA conditional overfit
The strongest evidence is the collapse **after GA filtering**.

Frozen finalist selected-event economics before portfolio capacity:
- PF1: DEV 502 events, +2.97% mean, 71.3% winners -> replay 1,173 events, +0.40%, 55.9% winners.
- PF2: DEV 120, +5.60%, 79.2% -> replay 302, +0.29%, 57.3%.
- PF3: DEV 106, +5.76%, 78.3% -> replay 293, +0.25%, 56.3%.
- PF4: DEV 99, +3.02%, 75.8% -> replay 262, +0.38%, 56.1%.
- PF5: DEV 113, +1.30%, 65.5% -> replay 274, -0.26%, 47.8%.

The finalists actually activate on **more** replay events, so failure is not due to scarcity. The conditional relationships GA selected on DEV50 lost most of their discriminatory power on new stocks.

The upstream ticker-by-ticker candidate search is itself an optimization layer, so it remains a structural source of selection pressure. However, the broad candidate baseline transported much better than the downstream GA filters. The current evidence therefore points more strongly to the **second-stage GA conditional selection** than to complete failure of the candidate generator.

## Q6 — PF1 portability
PF1 is qualitatively different from PF2–PF5. It uses 5/10-session candidates from Momentum, Breakout, Volume/Liquidity, and Market-Regime/Structure, with a permissive 1-of-4 immediate entry gate and 1-of-2 exit gate. Its development selected-event edge fell from +2.97% / 71.3% winners to +0.40% / 55.9%, but the larger number of opportunities allowed the exact-MTM portfolio to retain +12.81% CAGR.

PF1 should not be promoted as validated: its max DD worsened to -15.64% and 2015–16 lost -7.58%. Its survival is evidence of partial portability, not proof of a stable production mechanism.

## Determination
Primary: **GA conditional overfit / effective-sample-size problem.**
Contributing: **high within-episode cross-stock dependence and two-stage selection pressure.**
Not supported as primary: **broad signal-family distribution shift or absence of candidate opportunities in replay.**

## Scientific implication
Do not repair PF1–PF5 against 50+17. Before another protected reveal, the discovery architecture should be changed so that selection pressure is evaluated across genuinely independent units—e.g. stock-group and/or episode-held-out internal folds—rather than treating thousands of correlated ticker/date events as independent evidence. Any such redesign must be specified and frozen before untouched Discovery is accessed.
