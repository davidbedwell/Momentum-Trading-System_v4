# MTS Discovery Dynamic Adverse-Path Stop Protocol — 2026-10-01

**Status:** FROZEN BEFORE OUTCOME SEARCH
**Scope:** Discovery only; no Verification A or Verification B access
**Parent evidence:** Frozen adverse-path study at commit 4b1d2c6e57e64834164b135dce84443394e0a4fa
**Purpose:** Test whether a causal state-dependent exit can truncate failed trades while preserving right-tail winners better than fixed percent/ATR/time stops.

## 1. Scientific question
Can observable post-entry path deterioration identify economic trade failure early enough to improve the payoff distribution without using terminal outcome, future path information, or Verification evidence?

A candidate stop is valuable only if its avoided loss exceeds profit destroyed in original winners and the effect generalizes across the chronological Discovery holdout and broad ticker/year/family coverage. Win rate alone is not an objective.

## 2. Evidence boundaries
Use exactly the corrected 67-ticker Discovery population and frozen trade/path construction from the parent adverse-path protocol. Preserve the chronological 70/30 Discovery development/holdout split (split date 2021-09-13). Selection/tuning occurs on development only; holdout receives unchanged replay of nominated policies. Verification A remainder and all Verification B remain sealed. No candidate can be promoted by this experiment.

Every exit decision at session t may use only information available through session t. Full-path MAE/MFE and terminal outcome are evaluation labels only and may never qualify a stop.

## 3. Causal structural references
Evaluate separately, never collapsed into an ANY-REFERENCE state:
- prior 5-session low
- prior 10-session low
- prior 20-session low
- most recent confirmed causal swing low (2 preceding and 2 confirming bars)

Reference values must be fixed from information causally available before/at the decision session. Report each reference independently and combined policies explicitly.

## 4. Prespecified deterioration components
For each reference measure close penetration below reference in ATR20 units at thresholds: 0.00, 0.25, 0.50, 0.75, 1.00 ATR.

Reclaim allowance after first qualifying break: 1, 2, 3, or 5 completed sessions. A reclaim is a close back above the broken reference. Persistence variants: one qualifying close, two consecutive closes, or three consecutive closes below the reference/threshold.

Lower-low confirmation: evaluate both required and not-required. When required, after the initial break/reclaim window the path must print a subsequent causal lower low before exit.

Recovery state at the exit decision: <25%, <50%, or <75% recovery from the adverse excursion. Recovery is calculated causally from the running adverse low and entry price; no future low may be used.

## 5. Candidate stop families
A. Structural break only: reference + ATR penetration + persistence.
B. Break + failed reclaim: A plus no reclaim within the prespecified allowance.
C. Break + failed reclaim + subsequent lower low.
D. Break + failed reclaim + weak recovery.
E. Full adverse-path failure: break + failed reclaim + subsequent lower low + weak recovery.

All combinations of the prespecified component grids are evaluated within their family. Duplicate-equivalent policies are canonicalized. No SMA/EMA is added to this search; the parent experiment found recent price lows materially more informative and the purpose here is to test that discovered mechanism rather than expand the search space.

## 6. Catastrophic-risk layer
Evaluate a separate emergency cap, not as the primary economic stop. Prespecified caps: 6, 8, 10, 12 ATR20 adverse excursion and 20%, 25%, 30%, 40% loss from entry. Report results both with no catastrophic cap and with each cap. Do not select a cap merely because it raises win rate. Gap-through execution uses first available observed price and must not assume fill at the threshold.

## 7. Economics and tail-shaping metrics
For every candidate report: N/participation, exits triggered, exit timing, exit return, terminal return under original frozen exit, mean/median return, total return units, profit factor, average winner, average loser, payoff ratio, win rate, p01/p05/p10, worst trade, maximum drawdown in return units, and ticker/year/family/genome breadth.

Directly report: original winners killed, percentage of original winners killed, foregone winner profit total/mean, original losers truncated, percentage of original losers truncated, loss avoided total/mean, and **stop economic value = loss avoided minus foregone winner profit**. Also report change versus original in expectancy, PF, average loser, p05, worst trade, and max drawdown.

## 8. Selection rule on Development only
Do not rank by win rate. A policy is eligible for nomination only if:
1. stop economic value > 0;
2. mean expectancy exceeds original-entry Development baseline after applying the stop;
3. profit factor is not lower than baseline;
4. average loser improves;
5. p05 improves;
6. it has >=20 unique tickers, >=5 calendar years, and >=4 Search families;
7. no single ticker supplies >20% of its total stop economic value.

Among eligible policies, identify the Pareto frontier across expectancy improvement, stop economic value, p05 improvement, max-drawdown improvement, and original-winner preservation. Nominate at most three non-dominated policies representing conservative, balanced, and aggressive tail truncation. This is policy selection, not validation.

## 9. Frozen Discovery holdout replay
Replay nominated Development policies unchanged on the latest 30% Discovery holdout. A candidate survives this internal stress test only if holdout stop economic value remains >0, holdout expectancy is not below the holdout baseline, average loser and p05 improve, and breadth remains >=15 tickers and >=3 years. Report effect-size degradation from Development to holdout. Do not retune failed policies on holdout.

## 10. Baselines and falsification
Compare against original frozen exit, complete parent percent-stop grid, complete ATR-stop grid, and time-stop grid. Explicitly test whether any apparent benefit is merely tail truncation that destroys comparable/more winner profit; concentrated in ticker/year/family/genome; dependent on gap-fill assumptions; driven by overlapping observations; unstable across Development/Holdout; or explainable by position sizing rather than stopping.

The hypothesis is falsified for this Discovery population if no prespecified dynamic policy survives the frozen holdout criteria. A null result is an acceptable result.

## 11. Required outputs
Machine-readable JSON and concise Markdown containing: protocol/provenance hash, population audit, Verification access flags, baseline economics, full candidate manifest/count, Development candidate results, Pareto frontier, nominated policies, unchanged holdout replay, catastrophic-cap sensitivity, fixed-stop comparisons, breadth/stability, ticker-cluster dependence-aware uncertainty for nominated policies, falsification assessment, and explicit conclusion: DISCOVERY CANDIDATE / DISCOVERY NULL / IMPLEMENTATION FAILURE.

## 12. Governance
This experiment may create a candidate exit policy only. It may not promote, paper-trade, or operationalize one. Verification A/B access requires a separately frozen validation protocol and explicit subsequent decision. Analysis Engine/deterministic code performs calculations and contract enforcement only; scientific interpretation and hypothesis formulation remain governed research functions.
