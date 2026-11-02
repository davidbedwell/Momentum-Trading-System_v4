# Frozen design, saved before this experiment's outcome computation
Entire 2009–2018 is exploratory in-sample; prior studies already examined these years. No tuning or confirmatory claim.

Control: verbatim original monthly bottom-20%-RSI holdings and prior-session eligibility, equal weight. Never rerank RSI. Secondary predicates are conjunctions; missing/nonfinite features fail. Strict fixed thresholds, no fitted quantiles. Exhaust all 9 choose 1,2,3 = 9+36+84=129 combinations, including redundant/sparse/empty rules. Rank only after all calculations by net CAGR descending, ID tie break.

Panel (one numerical feature per predicate), directions and hypotheses:
- return_252 > 0: positive long trend supports recovery.
- ma_distance_20 < 0: depressed short-term price offers recovery potential.
- return_5 > 0: early bounce signals stabilization.
- acceleration_21 > 0: recent momentum improves versus prior 21 sessions.
- reversal_5_vs_prior21 > 0: recent selling decelerates (unequal-horizon proxy).
- positive_fraction_21 > 0.5: positive-session breadth signals stabilization.
- vol_ratio_10_21 < 1: volatility contracts; existing predictive derived feature vol_10/vol_21.
- volume_ratio_5_20 < 1: recent vendor volume normalizes.
- relative_strength_21 > 0: relative resilience supports recovery.

Definitions inherited unchanged from winner-characteristics study.py and predictive-setups study.py: adjusted close returns at trading-session lags; MA20 simple mean; acceleration consecutive 21-session returns; reversal last 5 minus preceding 21-session return; positive fraction strictly positive daily returns over 21 sessions; volatility sample daily SD annualized sqrt(252); vendor volume rolling means; RS21 subtracts existing compounded equal-weight available-universe 21-session benchmark. Pre-entry feature date is previous global session. Warmup before 2009 allowed; no 2019+ data.

Accounting exactly original indicator_experiment.py: adjusted OHLC; self-financing commission fixed point at 10bps each bought/sold dollar; drifted weights; empty portfolio cash return zero except transition sale cost. Monthly opening rebalance and next-month open endpoints; final December marked at last 2018 close, no liquidation fee. This explicit terminal exception is necessary to reproduce original 23.15–23.19% rather than use forbidden January 2019 data. CAGR original 252/trading-session exponent; Sharpe monthly sample SD, zero risk-free; daily-close/endpoint and monthly MDD, positive loss magnitude.

For each combo simulate exposure-matched control: full original RSI basket on exactly combo's active months, cash otherwise, same actual costs. Binary capital exposure is identical (full investment whenever nonempty); this is not volatility matching. Also compare selected and control net returns on common active months, and gross return differences, without calling active-month compounded returns a calendar CAGR. Export monthly counts, membership, exposure, annual continuous-path segments and slices 2009,2011,2015–16,2018 for every combo. All ranks, no support filters. Fixed universe survivorship, multiple testing, dependent predicates and vendor adjustment/volume limitations apply.
