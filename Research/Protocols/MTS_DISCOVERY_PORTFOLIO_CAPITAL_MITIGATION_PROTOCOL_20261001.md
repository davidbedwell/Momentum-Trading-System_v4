# MTS Discovery Portfolio-Capital Mitigation Protocol — 2026-10-01

**Status:** FROZEN BEFORE OUTCOME SEARCH  
**Scope:** Discovery only. Verification A remainder and all Verification B remain sealed.  
**Parent evidence:** Dynamic adverse-path stop study concluded DISCOVERY NULL across 1,980 prespecified binary stop policies; fixed stop families previously reduced aggregate expectancy.

## Scientific question
Can ex-ante risk-conditioned sizing, graduated capital commitment, and causal partial de-risking improve compounded portfolio wealth and reduce drawdown versus equal-sized full-entry MTS trades while preserving the positive-skew winners that make baseline MTS profitable?

The unit of optimization is portfolio capital, not win rate. A mitigation policy is valuable only if it improves the wealth/risk tradeoff without depending on future information or sealed Verification evidence.

## Population and partitions
Use the exact corrected 67-ticker / 125,002-trade Discovery population and causal reconstructed paths used by the parent studies. Preserve chronological split date 2021-09-13: Development for policy selection; Discovery Holdout for one unchanged replay after nomination. Verification A remainder and all Verification B are inaccessible.

Use the canonical immutable Discovery research cache when its format, population, split, and source-checkpoint hashes verify. Cache use must not alter scientific inputs.

## Baseline
Equal capital weight at original MTS entry; original frozen MTS exit; no post-entry resizing. Portfolio simulations must report both trade-level capital-normalized results and a chronological overlapping-position portfolio model with explicit capital/exposure assumptions.

## Stage 1 — simple ex-ante sizing controls
Test separately before combinations:
1. Equal weight baseline.
2. Inverse ATR/price volatility sizing using causal entry-time ATR20/price.
3. Realized-volatility sizing where causal pre-entry returns are available; otherwise mark unavailable rather than proxy silently.
4. Downside-risk sizing using Development-only pooled historical downside estimates available strictly before each trade in the simulation. No terminal outcome of the current/future trade may enter its size.

Sizing multipliers are normalized to equal average gross exposure and bounded by prespecified caps/floors so apparent improvement cannot come merely from lower total exposure. Test conservative bounded multiplier grids: floor 0.25/0.50; cap 1.25/1.50/2.00. No leverage above the selected cap.

## Stage 2 — genome/family-conditioned sizing
Estimate risk only where sample support is adequate. Hierarchy: exact genome if support >=100 prior Development observations; otherwise progressively pooled genome family; otherwise global causal risk estimate. Never use a future observation to estimate a prior trade's risk. Candidate risk statistics: downside deviation, p10/p05 loss, MAE distribution, and volatility. Compare raw expectancy with downside risk; do not assume high volatility deserves less capital unless return fails to compensate for risk.

## Stage 3 — graduated entry
Preserve original signal and original exit. Test initial allocations 25%, 50%, 75%, 100% of the policy target. Remaining target exposure may be earned in causal increments when prespecified favorable evidence occurs: cessation of lower lows, recovery efficiency thresholds, recent-low preservation/reclaim, and/or attack/reclaim of recent highs. Never backfill an add at an earlier price. Each add fills at the first price available after the decision.

## Stage 4 — graduated de-risking
Do not force binary exit. On prespecified adverse evidence, reduce current exposure by 25%, 50%, or 75%; retain the remainder until original MTS exit unless later causal policy action changes it. Candidate evidence comes only from previously discovered causal variables: lower-low persistence, recovery efficiency, sustained failure/reclaim of prior 5/10/20-day lows or confirmed causal swing low. No new indicator search in this stage. Record capital saved on losers and upside surrendered on eventual winners.

## Stage 5 — combinations
Only after Stages 1–4 are evaluated independently may Development nominate combinations of ex-ante sizing + graduated entry + partial de-risking. Combination search must be small and constructed from independently useful components; no unrestricted combinatorial optimization.

## Catastrophic protection
Evaluate a separate distant disaster layer (not an ordinary optimized stop): 8/10/12 ATR and 25/30/40% adverse move. Report results with and without it. Gap-through fills at first available observed price, never at an unavailable threshold price.

## Portfolio simulation
Sort decisions causally by timestamp. Explicitly model overlapping positions and available capital. No policy may deploy capital not available at the decision time. Report gross exposure, peak exposure, number of concurrent positions, and unused cash. Where multiple same-time signals compete for insufficient capital, use a deterministic outcome-independent allocation rule frozen in code before result inspection.

Run at least two capital conventions: (A) non-levered 100% capital budget; (B) normalized risk-budget comparison where average gross exposure is held comparable across policies. Do not credit idle cash with a return unless a prespecified cash return series is available to every policy equally.

## Primary outcomes
Primary: compounded terminal wealth / CAGR-equivalent over common elapsed period, maximum drawdown, drawdown duration/recovery time, downside tail (p05 and CVaR/expected shortfall), and return-to-drawdown ratio. Secondary: volatility, Sharpe-like return/volatility diagnostic, total/gross exposure, turnover, original trade expectancy/PF, average winner/loser, win rate, and concentration by ticker/year/family/genome.

A lower raw trade expectancy may still be economically superior only if portfolio compounding/risk improves under comparable exposure. Conversely, simply reducing exposure is not success.

## Development nomination
A component/policy may be nominated only if, versus its exposure-matched baseline: terminal compounded wealth is higher OR statistically indistinguishable with materially lower max drawdown; max drawdown does not worsen; CVaR does not worsen; improvement is not dominated by one ticker/year/genome; and benefit appears across >=20 tickers, >=5 years, and >=4 signal families where applicable. Report bootstrap/ticker-cluster uncertainty. Nominate at most three: growth-oriented, balanced, drawdown-oriented. Do not inspect Holdout during selection.

## Discovery Holdout survival
Replay frozen nominees unchanged. A nominee survives only if its intended property generalizes: growth nominee does not reduce compounded wealth while worsening drawdown; drawdown nominee materially improves drawdown without a disproportionate loss of terminal wealth; balanced nominee improves the prespecified return/drawdown tradeoff. Report Development→Holdout degradation. No retuning after Holdout.

## Falsification / anti-overfit controls
Compare against equal-size baseline, simple volatility sizing, simple constant fractional exposure, and original exit. Report whether gains arise merely from lower exposure. Test concentration, chronological stability, gap assumptions, turnover sensitivity, and capital scarcity. Preserve null outcomes. Do not search Verification evidence, promote to paper/live trading, or change thresholds after viewing Holdout.

## Required outputs
JSON + Markdown with protocol SHA, code/provenance hashes, cache manifest/hash, population audit, Verification access flags, portfolio assumptions, baseline, complete candidate manifest, independent Stage 1–4 results, small Stage 5 combination manifest, Development frontier/nominees, unchanged Holdout replay, catastrophic-layer sensitivity, exposure-normalized comparisons, wealth/drawdown paths and metrics, breadth/stability, ticker-cluster uncertainty, falsification checks, and conclusion: DISCOVERY CANDIDATE / DISCOVERY NULL / IMPLEMENTATION FAILURE.
