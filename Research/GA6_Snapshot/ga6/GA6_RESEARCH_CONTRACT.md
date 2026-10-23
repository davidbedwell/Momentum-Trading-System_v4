# GA6 research contract — 2026-10-21

GA6 is a distinct experiment. Never overwrite or resume GA5 checkpoints under GA6 identity.

## Evolution
- Permit crossover across all 13 niches, preserving immutable chromosome genetic identity.
- Evaluate each candidate independently within every niche for which evidence exists.
- Rank and retain elites **within each niche**. A chromosome may rank in multiple niches.
- Separate genetic provenance from evaluated niche and preserve both in every record.

## Trade-level eligibility
- Model next-open execution and explicit costs. Do not treat shadow fills as portfolio fills.
- Positive net arithmetic EV and positive mean log(1+return) are necessary, not sufficient.
- Report payoff ratio, profit factor, worst-tail mean, trade count, and capital efficiency.
- Win rate is diagnostic only; never the principal objective.
- Estimate uncertainty using time-blocked or episode-aware resampling; avoid pretending correlated trades are independent.
- Require adequate observations and independent episodes; retain inconclusive candidates in a research pool.

## Decisions
- Entry: compare entering against cash/no-entry.
- Hold: compare hold against sell-now under the same future path.
- Exit: compare sell-now, hold, and exit/reentry; include costs, cash yield, time out of market and available replacement trades.
- Counterfactual outcomes may train research fitness but may not enter live signal features.
- Fixed stops are optional baselines, not mandatory chromosome behavior.

## Portfolio gate
- Chronological next-open portfolio replay with PIT membership, earnings restrictions, realistic capacity, settlement, cash, corporate actions and fees.
- Report CAGR, signed MDD magnitude, Calmar, turnover, exposure, costs, tradeability, and robustness.
- Research screen: CAGR >15%, MDD >4% and <20%, preferred Calmar >2. Flag very low MDD for validation rather than asserting it is impossible.
- No certification without independent untouched evaluation. Preserve DEV80/DEV87/DEV50 and sealed blind governance.

## Required implementation gates before launch
1. Frozen GA5 manifest with code/data/checkpoint hashes.
2. GA6 runner and niche-specific breeder implemented and unit-tested.
3. Entry/hold/exit counterfactual evaluator implemented and causality-tested.
4. Portfolio replay parity, fee, settlement and corporate-action tests.
5. Smoke run on permitted development data, then explicit production launch.
