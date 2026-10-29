# MTS v4 — 117-Stock Portfolio Risk Mechanism Protocol — 2026-10-02

## Objective
Identify causal portfolio-level controls that materially reduce synchronized downside while preserving the portable signal engine's upside. The objective is not minimum drawdown at any cost; it is improved downside efficiency with retained terminal wealth and market alpha.

## Evidence boundary
Research laboratory = already-consumed 67-stock Discovery population plus already-consumed held-out 50. No remaining Discovery, Verification A remainder, or Verification B may be accessed. Develop mechanisms on the 67; replay frozen representatives unchanged on the 50 across the four independent eras.

## Diagnostic finding motivating the protocol
Across both populations independently, worst-5% aggregate signal days show approximately 93–94% simultaneous losers, elevated active-position concurrency, elevated new-entry flow, and elevated cross-sectional dispersion. Stress clusters recur in 2008/09, 2011, 2020, and 2022. This motivates portfolio-crowding/systemic-state controls rather than another individual-trade stop search.

## Causal information rule
Every control for session t may use only information known through the prior close, plus already-scheduled entries known before execution. No same-session close/high/low and no future outcome may set risk. Expanding/rolling thresholds must be computed from prior observations only.

## Mechanism families
1. Concurrency throttle: scale new-entry capital when prior-close active gross/concurrency is above its trailing/expanding 75th, 90th, or 95th percentile.
2. Entry-flow throttle: scale the day's scheduled entry budget when scheduled-entry count is above the prior expanding 75th, 90th, or 95th percentile.
3. Market-stress throttle: use prior-close S&P 500 state only — price relative to 200-session SMA and 20-session realized volatility relative to its prior expanding 75th/90th percentile.
4. Correlation/crowding throttle: trailing 20-session portfolio breadth/correlation proxy using only completed daily cross-sectional returns through the prior close; suppress new risk when downside breadth/correlation is unusually high.
5. Sector/ticker concentration cap where sector metadata exists: prevent same-direction capital from becoming excessively concentrated in one ticker/sector without reducing total budget when safe redistribution is available.

## Control strengths
For each active state test new-entry multipliers 0.75, 0.50, and 0.25. Also test a no-new-entry state only for the most extreme prespecified threshold (95th percentile concurrency/flow or combined severe market stress). Existing positions retain frozen exits; this experiment does not add discretionary liquidation.

## Baselines
Equal sizing and fixed-budget top-25% 3x allocator. Same $100,000 finite-capital simulator, same next-session entry, frozen horizon exits, and same zero-cost convention as the consumed 50-stock experiment. S&P 500 Total Return remains the external opportunity-cost benchmark.

## Development selection — 67 only
Report terminal wealth, CAGR, max drawdown, CVaR5, p05 daily return, gross exposure, trade participation, and upside capture. A representative is eligible only if: (a) max drawdown improves by at least 10% in magnitude OR CVaR5 improves by at least 10%; (b) the other tail metric does not worsen; (c) terminal wealth retains at least 90% of matched baseline; (d) CAGR remains above the contemporaneous S&P 500 total-return CAGR over the comparable full interval when available; and (e) improvement is not concentrated in a single year. Prefer Pareto-stable neighborhoods, not the best isolated cell.

## Frozen replay — 50 only
Freeze at most three structurally distinct representatives before replay. Replay unchanged in each of the four $100,000 eras. A mechanism is considered replicated only if it improves max drawdown in at least 3/4 eras, does not reduce terminal wealth below 90% of baseline in any era, and preserves or improves S&P-relative terminal wealth in at least 3/4 eras. Report all failures without retuning.

## Combination rule
Do not combine failed components. A combination may be tested only after at least two component families independently satisfy the 67-stock Development eligibility rule. Freeze combination logic before 50-stock replay.

## Governance
This is consumed-evidence research only. It cannot promote a live rule. Untouched evidence remains sealed. Deterministic calculations may measure and enforce the protocol; scientific interpretation remains separate.
