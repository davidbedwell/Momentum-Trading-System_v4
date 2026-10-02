# MTS v4 — Causal Wealth Growth Frontier Extension — Development Result — 2026-10-02

## Finding
The causal wealth-growth response continued upward through the prospectively frozen 4.00x boundary, but the portfolio simulator is now visibly close to its cash/gross-exposure ceiling. The upper-bound result therefore cannot be interpreted as an unconstrained economic optimum.

Equal baseline: 15.822560x terminal wealth, max drawdown -45.7329%, CVaR5 -3.26747%, average gross exposure 0.8582.

At same-day top-50% / 4.00x: terminal wealth 21.5076x (+35.93%), average gross exposure 0.9596, peak gross exposure 0.9989, minimum cash 0.00108, max drawdown -45.551% (about 0.182pp better than equal), CVaR5 about 0.052pp worse than equal, and +2.34% terminal wealth versus exposure-matched equal.

At same-day top-25% / 4.00x: terminal wealth 21.4631x (+35.65%), average gross exposure 0.9576, peak gross exposure 0.9981, minimum cash 0.00185, max drawdown -45.508% (about 0.224pp better), CVaR5 about 0.040pp worse, and +2.91% versus exposure-matched equal.

All extension candidates retained the broad evidence gate. Three were nondominated within the extension: top-50%/4.00x, top-25%/4.00x, and boost-all/4.00x.

## Interpretation
The evidence supports the user's original principle: allowing exposure to grow with causal opportunity quality can materially increase terminal wealth, and the effect is not accompanied by a comparable increase in max drawdown in this Development sample.

However, the simulator is nearly fully invested at the upper frontier. Continuing to raise per-trade caps inside the same long-only cash-constrained simulator would increasingly test allocation under a binding capital ceiling rather than genuine additional exposure. The next scientific question is therefore not simply 5x, 6x, 8x. It is whether the system should permit leverage/portfolio heat above 1.0 gross exposure, and under what causal conditions.

Before any such leveraged experiment, leverage mechanics, financing/carry costs, margin/portfolio constraints, and catastrophic-risk limits must be explicitly modeled. The unlevered 4.00x frontier can be frozen as a candidate architecture without claiming 4.00x is optimal.

No Discovery Holdout, additional Verification A, or Verification B evidence was accessed.
