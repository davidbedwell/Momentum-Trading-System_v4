# MTS v4 — Portfolio Allocation Architecture Summary — 2026-10-02

## Starting observation
Verification A3 of the 0.75x–1.50x EV/p10 rule produced 5/5 positive ticker-level sizing contribution but lower compounded portfolio wealth (9.6125x vs 10.1356x equal sizing). This motivated Discovery-only portfolio architecture work without consuming additional Verification evidence.

## Discovery architecture findings
Portfolio-wide boost/rank overlays increased Development wealth substantially, up to 18.7239x vs 15.8226x equal sizing, with broad ticker/year/family contribution. They failed the strict frozen gate because max drawdown and CVaR5 both worsened.

Capacity gates, causal realized-volatility/ATR gates, and prior-close drawdown guards did not eliminate the CVaR deterioration. Coarse static risk normalization produced two clean Development passes, but not enough neighboring passes to satisfy the frozen plateau criterion.

## Within-ticker mechanism
A new structural hypothesis preserved each ticker's same-day scheduled capital budget and used EV/p10 only to redistribute capital among that ticker's competing simultaneous signals.

Development:
- 1.10x cap: 15.95255x, +0.8215% vs equal; 56/56 tickers positive; 16/17 years; 5/8 families; full frozen gate pass.
- 1.25x cap: 16.13240x, +1.958%; full frozen gate pass.
- 1.50x cap: 16.38836x, +3.576%; full frozen gate pass.
All three caps passed, establishing a broad within-ticker Development plateau. Per protocol, the simplest 1.10x cap was frozen before Holdout.

## Frozen Discovery Holdout replay
Candidate: within_ticker_top50_c1.10.
Holdout population: 37,501 trades, 67 tickers.

Equal sizing:
- terminal wealth 2.744909x
- max drawdown -15.9683%
- CVaR5 -2.11892%

Within-ticker candidate:
- terminal wealth 2.749694x (+0.1743%)
- max drawdown -15.9450% (slightly better)
- CVaR5 -2.12282% (slightly worse)
- mean sizing contribution +0.00048472
- ticker breadth 61/67 = 91.0%
- year breadth 6/6 = 100%
- family breadth 4/8 = 50%
- ticker-cluster 95% CI [0.00039387, 0.00057410]

## Frozen conclusion
**DISCOVERY HOLDOUT NOT FULLY REPLICATED.**
Every frozen gate passed except family breadth, which required >=60% and achieved 50%. Do not waive or reinterpret that gate after exposure.

The result still supports a broad ticker-level EV/p10 relationship and suggests that preserving cross-ticker capital budgets materially reduces the portfolio-compounding conflict seen in A3. However, the architecture is not eligible for Verification on this evidence because its frozen Holdout gate failed.

## Evidence stewardship
No additional Verification A names were consumed in this Discovery architecture sequence. The remaining 55 A names stay MACHINE-ACCESSED / RESEARCHER-BLINDED and sequestered. Verification B remains sealed.
