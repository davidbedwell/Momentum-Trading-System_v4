# MTS v4 — Discovery Causal Wealth Growth Frontier Extension — 2026-10-02

## Trigger
The prospectively frozen 1.10x–2.00x Development grid showed terminal wealth still rising at the 2.00x boundary. This protocol is frozen before testing any cap above 2.00x.

## Objective
Locate the broad region where additional causal EV/p10-directed exposure ceases to improve the wealth/risk tradeoff. Do not optimize a single historical maximum.

## Evidence
Discovery Development only. No Discovery Holdout, additional Verification A, or Verification B access.

## Fixed information and architectures
Keep causal EV/p10 estimator, N=100 backoff, base trade fraction, simulator, and architecture definitions unchanged. Extend only the capital cap dimension.

Test caps 2.25x, 2.50x, 3.00x, 3.50x, and 4.00x for:
- boost-all;
- same-day top 25%;
- same-day top 50%.

Retain the prior 1.10x–2.00x results as the lower frontier. Do not insert intermediate caps after seeing results in this extension.

## Reporting
Same metrics and broad-evidence screen as the parent wealth-growth protocol. Additionally report marginal terminal-wealth gain, CAGR gain, maxDD change, CVaR5 change, average/peak exposure, and minimum cash versus the immediately lower tested cap in the same family.

Identify saturation/reversal when a higher cap fails to improve terminal wealth, or when wealth gains become dominated by another lower-cap candidate on terminal wealth/maxDD/CVaR. A binding cash/exposure ceiling must be reported explicitly rather than interpreted as an economic optimum.

## Next boundary
After this extension, freeze representative conservative/intermediate/aggressive frontier points before any Discovery Holdout replay. Do not choose solely by maximum terminal wealth.

## Integrity
No A3 outcome-driven numerical tuning beyond the broad cap extension triggered by the Development boundary. Remaining 55 Verification-A names stay sequestered/researcher-blinded. Verification B stays sealed.
