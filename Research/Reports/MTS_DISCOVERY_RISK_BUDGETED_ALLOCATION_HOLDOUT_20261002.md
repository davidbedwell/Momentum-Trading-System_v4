# MTS v4 — Risk-Budgeted Allocation Discovery Holdout — 2026-10-02

## Conclusion
The frozen top-half same-day EV/p10 redistribution rule with a 1.50x cap and Development-derived p90 gross-exposure ceiling **PASSED all frozen Discovery Holdout gates**.

## Top-half rule
Baseline Holdout terminal wealth: 2.744909x.
Risk-budgeted allocation: 2.812392x, +2.4585% relative.
The rule remained +0.2153% above an exposure-matched equal-sizing control.

Max drawdown improved from -15.9683% to -15.4410%. CVaR5 worsened from -2.11892% to -2.13861%; because max drawdown improved, the frozen rule that both tail metrics may not worsen passed.

Breadth: 62/67 tickers positive, 6/6 Holdout years positive, 6/8 families positive. Ticker-cluster bootstrap 95% CI [0.00644218, 0.00974220]. The gross ceiling bound on 31.79% of Holdout days. All concentration, breadth, uncertainty, wealth, and risk gates passed.

## Structural control
The frozen top-quarter / 1.50x / p90 gross-ceiling control produced 2.819536x (+2.7188% versus equal; +1.6900% versus exposure-matched equal), improved max drawdown and CVaR5, and had 60/67 positive tickers and 6/6 positive years. It nevertheless failed the frozen family-breadth gate at 4/8 positive families. It is therefore not the general nominee despite higher wealth.

## Interpretation
The experiment resolves the earlier portfolio paradox more cleanly than simply boosting trades. EV/p10 contains broad ranking information, but portfolio implementation matters. Redistributing capital among same-day opportunities while enforcing a prospectively defined gross-exposure ceiling preserved broad predictive contribution and converted part of it into incremental compounded wealth without relaxing the existing risk gate.

The top-half architecture is favored by the frozen scientific criteria because it generalizes across more signal families, not because it has the highest terminal wealth.

## Evidence boundary
This remains Discovery evidence. No additional Verification A names and no Verification B names were accessed. The remaining 55 Verification-A names remain machine-accessed/researcher-blinded and sequestered; Verification B remains sealed.
