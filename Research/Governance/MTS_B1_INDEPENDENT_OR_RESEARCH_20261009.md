# B1 independently ORed slow-bear detector

User-approved research designation: **B1**. Market crash-entry logic: **A OR B OR B1 OR C**. R-1 alone releases Defensive; simultaneous crash evidence dominates R-1. A, B, C and R-1 are unchanged. B1 is a separate, additional trigger, not a replacement for B or a condition that all detectors must satisfy.

B1 internal conjunctive rule: SPY closing below its trailing 200-session simple moving average for 10 consecutive sessions AND market-wide, causally lagged OFR funding-stress percentile >= 0.70 on the signal day. Funding percentiles must be computed with strictly historical observations and the frozen two-business-day OFR lag. Missing funding means B1 false, not automatic entry. This is an **exploratory candidate**, not a scientifically certified live detector.

Historical exploratory A OR B OR B1 OR C result: 2008 first Defensive entry 2008-05-14 (baseline 2008-10-10); 2020 2020-03-09 unchanged; 2022 2022-01-07 unchanged. Defensive time 34.49% (baseline 29.0%). Hypothetical SPY/cash wealth multiple 4.814 (baseline 3.419); maximum drawdown 19.51% (baseline 53.60%). These metrics use unadjusted SPY close, zero cash yield, no costs, dividends or fills; the same history was used to explore candidates, so they are **not independent validation**.

Source implementation: Core/layered_ga/b1_slow_bear.py; daily replay optional B1 field default false to preserve legacy tapes. Market-wide funding feature must be supplied by a separately verified causal data pipeline; no new data-feed certification or live brokerage wiring is claimed. Preserve protected ticker partitions.
