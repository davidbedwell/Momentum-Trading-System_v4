# MTS v4 — General Winner Capital Rule — Verification A3 — 2026-10-02

## Frozen conclusion
**MIXED. Do not automatically consume more Verification-A evidence.**

The candidate was frozen before A3 as causal historical expectancy / p10 downside, scale 3.154602090106647, bounded 0.75x–1.50x. A3 used exactly five mechanically assigned names: DASH, DGX, DLR, DTE, DVA.

## Breadth
All five names had positive capital-normalized sizing contribution:
- DASH: +5.5770 across 2,535 trades
- DGX: +39.4911 across 45,881 trades
- DLR: +53.3281 across 22,101 trades
- DTE: +25.4786 across 45,397 trades
- DVA: +45.7894 across 37,917 trades

Mean trade sizing contribution was +0.00110293. Breadth was 5/5 positive.

## Portfolio replay
Equal sizing: terminal wealth 10.135613x; CAGR 11.6604%; max drawdown -32.7678%; CVaR5 -2.52705%.
Frozen sizing: terminal wealth 9.612528x; CAGR 11.3790%; max drawdown -33.9175%; CVaR5 -2.51053%.
Exposure-matched equal baseline: terminal wealth 10.003694x.

Thus sized terminal wealth was 5.16% below ordinary equal sizing and 3.91% below the exposure-matched equal baseline. Max drawdown worsened by 1.1496 percentage points; CVaR5 improved by 0.0165 percentage points.

## Frozen protocol interpretation
The pre-result protocol defined 5/5 as STRONG_CONFIRMATION only if aggregate mean sizing contribution was positive, terminal wealth exceeded equal sizing, and max drawdown plus CVaR5 were not both worse. A3 achieved 5/5 breadth and positive mean contribution, and did not worsen both tail metrics, but failed the terminal-wealth requirement. Therefore the protocol-mandated conclusion is **MIXED**, not STRONG_CONFIRMATION.

The inherited evaluator printed CONTRADICTION because it retained stricter A2 composite criteria. That printed label is not authoritative for A3; the prospectively frozen A3 protocol is authoritative. No scientific values were changed after result exposure.

## Scientific implication
The cross-sectional relationship replicated extraordinarily well: 5/5 new tickers show positive trade-level sizing contribution. However, that did not translate into better compounded portfolio wealth. The discrepancy implies that trade-level contribution breadth alone is insufficient; overlap, timing, exposure allocation, cash competition, and compounding path can dominate the sum of isolated trade-return deltas.

This is a mechanism question for new Discovery work. It must not be resolved by drawing additional A names until the portfolio-level discrepancy is understood and a new hypothesis is frozen.

## Integrity
Exactly five A3 names accessed in the research decision process. Remaining 55 A names stay MACHINE-ACCESSED / RESEARCHER-BLINDED and sequestered. Verification B remains sealed. No search or retuning occurred inside A3.
