# MTS v4 — Major Drawdown Ex-Ante Separability Test

**Date:** 2026-10-03
**Parent gate:** MTS_RISK_RETURN_TENABILITY_GATE_20261003.md
**Purpose:** Determine whether the current MTS architecture has an identifiable, causal risk-management solution or an inverted/structurally unacceptable risk-return profile.

## 1. Primary falsifiable hypothesis

H1: Before major MTS losses, information already observable to the system contains enough structure to distinguish dangerous equity exposure from the exposure that produces major portfolio gains.

H0 / failure condition: Dangerous exposure is not meaningfully separable ex ante from wealth-producing exposure, or exploiting any apparent separation removes a disproportionate share of wealth creation.

Failure of this test makes the current architecture untenable for the stated MTS objective. Mechanical de-risking is not a pass.

## 2. Evidence boundary

Use only already-consumed 67-stock Discovery development evidence and frozen Phase-3 architecture information. Remaining Discovery stocks, Verification A, and Verification B remain sealed.

No crisis dates, drawdown dates, or future returns may enter any predictor.

## 3. Portfolio bases

Evaluate three frozen Phase-3 portfolio regions to prevent conclusions from depending on one risk appetite:
- aggressive / wealth-oriented base: frozen index 0;
- intermediate ~35% drawdown region: frozen index 35;
- ~30% drawdown knee: frozen index 226.

Primary transaction cost: 10 bps.
Sensitivity: 0/5/10/15/20 bps.

Every era starts independently at $100,000. No capital path crosses an era boundary. Causal evidence history may use only outcomes completed before the decision date.

## 4. Major drawdown definition

For each base and era, construct the daily close-to-close equity curve.

A major drawdown episode is mechanically identified as either:
A. peak-to-trough loss >= 10%, or
B. one of the three deepest non-overlapping peak-to-trough episodes in that era if fewer than three reach 10%.

For each episode record:
- prior peak date/value;
- onset date;
- trough date/value;
- recovery date if present;
- depth;
- duration;
- five worst contributing sessions;
- fraction of total episode loss occurring in first 1/3/5/10 sessions.

Episode definitions are outcome labels only and cannot be used as predictors.

## 5. Prediction horizons and labels

At every eligible session t, freeze information available no later than t close and evaluate future portfolio outcomes over:
- next 1 session;
- next 3 sessions;
- next 5 sessions;
- next 10 sessions;
- next 20 sessions.

Danger labels:
- forward loss <= -2.5%;
- forward loss <= -5%;
- forward loss <= -7.5%;
- forward loss <= -10%;
- membership in the damaging portion of a mechanically defined major drawdown.

Wealth labels:
- forward gain >= +2.5%;
- >= +5%;
- >= +7.5%;
- >= +10%;
- membership in the strongest wealth-producing windows matched by horizon.

Threshold sensitivity must be reported; no single cutoff may determine the conclusion.

## 6. Ex-ante state vector

Only causal values available by t:

### Market state
- trailing portfolio return 1/3/5/10/20/60 sessions;
- SPY/current broad-market proxy trailing 1/5/20/60 return where already available causally;
- trend relative to 20/50/200-session moving averages where already available;
- recent acceleration/deceleration.

### Volatility
- trailing portfolio realized vol 5/20/60;
- vol ratios 5/20 and 20/60;
- change in realized vol;
- fraction of positions with expanding idiosyncratic vol where available.

### Correlation / dispersion
- mean pairwise trailing return correlation among live positions;
- median and upper-quartile pairwise correlation;
- cross-sectional dispersion;
- fraction of live positions negative on prior 1/3/5 sessions;
- fraction moving in same direction.

### Exposure / concentration
- gross equity exposure;
- safe-asset fraction;
- number of live positions / filled slots;
- largest position weight;
- top-3 position weight;
- effective number of positions / HHI;
- ticker concentration.

### Signal intensity
- new MTS signals 1/3/5 sessions;
- signal count relative to trailing 20/60-session history;
- percentile / z-score of opportunity density;
- simultaneous qualifying candidate count.

### Family / sector
- family weights;
- family HHI / largest-family share;
- sector weights and sector HHI only if sector membership is available from a source already admitted to the development dataset; otherwise explicitly mark unavailable and do not backfill using future/current classifications.

### Position age
- mean/median live-position age;
- youngest/oldest;
- fraction age <=5, <=10, <=20;
- capital-weighted age;
- fraction of exposure in newly entered positions.

### Interactions required a priori
- signal intensity x volatility expansion;
- equity exposure x correlation;
- equity exposure x negative-position fraction;
- concentration x correlation;
- new-position fraction x volatility expansion;
- family concentration x volatility expansion;
- signal intensity x negative acceleration;
- extreme signal intensity x explosive volatility.

## 7. Stage A — Descriptive decomposition

For every major drawdown:
- show state vector at peak, onset, and 1/3/5 sessions before the major damaging segment;
- identify which variables changed before loss rather than after it;
- quantify contribution by live position, family, and sector if available;
- compare against all ordinary sessions and matched wealth-producing sessions.

This stage is descriptive and cannot establish a rule.

## 8. Stage B — Matched separability test

For every danger observation, construct controls from the same base and preferably same era matched on:
- gross exposure;
- number of live positions;
- approximate calendar regime/year where sample permits;
- recent trailing portfolio return;
- opportunity/signal count.

Compare the ex-ante state vector between danger and matched wealth/ordinary controls.

Report standardized effect size, distribution overlap, conditional danger probability, and bootstrap uncertainty.

The core question is not whether variables are statistically different. It is whether distributions separate enough to support a useful causal decision rule.

## 9. Stage C — Causal rule discovery without hindsight leakage

Use leave-one-era-out development.

For each held-out era:
1. Use the other three eras only to choose thresholds/rules.
2. Freeze the selected rule.
3. Apply it unchanged to the held-out era.
4. Repeat until each era has served as held-out once.

Allowed rule class is deliberately small and interpretable:
- single thresholds;
- two-variable AND interactions;
- at most one confirmation duration;
- at most one hysteresis duration;
- exposure responses of 100%, 75%, 50%, 25%, or 0%.

No unrestricted optimizer, tree ensemble, neural model, or high-dimensional search.

## 10. Counterfactual portfolio test

A risk rule acts only on exposure. It does not alter signal generation, rankings, or original exits.

When active, equity exposure is scaled to the frozen response and residual capital earns the 3% safe return. Re-entry follows the frozen rule/hysteresis. No leverage.

For each held-out era and cost:
- CAGR;
- ending wealth;
- max drawdown;
- CVaR5;
- worst day;
- positive/upside capture;
- negative/downside capture;
- turnover;
- fraction of time de-risked;
- avoided drawdown dollars;
- foregone wealth-producing dollars.

## 11. Mandatory comparison: loss avoided vs wealth sacrificed

For every rule calculate:
- % of baseline drawdown loss avoided;
- % of baseline positive-return wealth removed;
- drawdown reduction per 1% CAGR sacrificed;
- CVaR improvement per 1% CAGR sacrificed;
- downside capture reduction;
- upside capture retained.

Also show every major drawdown individually. A rule that solves one famous crash while worsening the remainder does not pass.

## 12. Pre-frozen pass/fail logic

### Strong evidence of separability
All of the following:
1. Rule is selected without using the evaluated era.
2. Improves max drawdown or CVaR materially in at least 3 of 4 held-out eras and does not materially worsen both in the fourth.
3. Retains at least 80% of baseline CAGR in every held-out era OR at least 85% pooled geometric wealth growth with no era losing more than 25% of its baseline CAGR.
4. Retains at least 80% of upside capture.
5. Reduces downside capture by at least 15% or reduces major-drawdown depth by at least 20% in aggregate.
6. Improvement is not produced principally by persistent safe-asset allocation: de-risked time must be <=35% unless the opportunity-cost test still satisfies criteria 3 and 4.
7. Direction remains coherent at 5/10/15/20 bps.

### Partial / unresolved
There is reproducible ex-ante separation, but it misses one or more economic thresholds above. Architecture remains researchable but has not passed the tenability gate.

### Failure / inverted risk-return
Any of:
- no stable ex-ante state distinction survives leave-one-era-out testing;
- protective rules remove wealth at roughly the same or greater rate than they remove damaging exposure;
- achieving meaningful DD/CVaR improvement requires chronic safe allocation and violates return-retention criteria;
- apparent success depends on hindsight-specific dates/thresholds or one era;
- direction collapses under modest cost sensitivity.

A failure result renders the current architecture untenable under the parent gate.

## 13. Anti-overfitting controls

- thresholds learned only from training eras;
- report number of candidate rules searched;
- retain all attempted rules, not only winners;
- identical search space for each held-out fold;
- no manual threshold changes after seeing held-out results;
- no use of untouched banks;
- no weakening of pass criteria after results.

## 14. Required outputs

1. machine-readable JSON;
2. drawdown episode table;
3. ex-ante feature comparison table;
4. matched danger-vs-wealth analysis;
5. leave-one-era-out selected rules;
6. held-out counterfactual metrics by base/era/cost;
7. loss-avoided vs wealth-sacrificed table;
8. explicit verdict: PASS / UNRESOLVED / FAIL under the frozen criteria;
9. limitations and data unavailable.

This protocol tests the current architecture. It is not permission to redesign MTS after observing the result.
