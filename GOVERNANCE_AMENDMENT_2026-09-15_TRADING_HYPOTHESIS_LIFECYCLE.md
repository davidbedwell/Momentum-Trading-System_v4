# MTS v4 Human-Approved Governance Amendment — Trading-Hypothesis Lifecycle

Date: 2026-09-15
Status: Approved by the human owner

This amendment supplements `ChatGPT.md` and supersedes the fixed cumulative
`success_rate >= 0.60` rule in
`Architecture/ADR/ADR-20260910-PREDICTIVE-HYPOTHESIS-BLIND-VALIDATION.md` as the
criterion for predictive-hypothesis verification or advancement. Historical
records produced under the former rule remain historical evidence and must not
be rewritten.

## 1. Three distinct stages

MTS shall distinguish:

1. trading-hypothesis candidacy;
2. scientific validation; and
3. candidacy for trading promotion.

Success at one stage does not establish success at a later stage.

## 2. Trading-hypothesis candidacy

The AI Research Director may designate a relationship as a candidate trading
hypothesis only when exploratory evidence supports a specific, non-duplicative,
and falsifiable relationship between information observable at time `T` and
subsequent market behavior, and a proposed human-executable trade policy has
positive estimated net expected value.

The proposed policy must specify enough mechanics to evaluate an achievable
trade, including:

- observable entry conditions, direction, instrument, and prediction point;
- expected favorable outcome;
- maximum permitted adverse movement or initial risk unit;
- stop, invalidation, favorable-exit, and maximum-holding-period rules;
- treatment of gaps, executable fills, and permitted position management;
- estimated commissions, spread, slippage, and market impact; and
- applicable population or market regime.

Exploratory outcomes must apply the proposed policy chronologically. A favorable
movement occurring after the policy would have stopped, invalidated, expired,
or otherwise exited does not count. No later recovery may be credited after the
position would no longer exist.

Exploratory net expectancy is:

```math
EV_{net,exploratory}=\frac{1}{N}\sum_{i=1}^{N}(X_i-C_i)
```

where `X_i` is the realized outcome of applying the policy to observation `i`
and `C_i` is its estimated all-in cost. Positive exploratory net expectancy is
required for trading-hypothesis candidacy. No single universal success-rate or
favorable-movement threshold governs candidacy because profitable hypotheses
may have materially different payoff distributions.

A predictive relationship without positive exploratory trading expectancy may
remain a scientific observation or supporting finding. It is not a candidate
trading hypothesis unless an executable structure with positive estimated net
expectancy is established.

Historical look-ahead remains permitted during exploration. Its use, examined
evidence, and parameters selected from that evidence must be recorded. Candidate
status is exploratory only; it is neither scientific validation nor trading
eligibility.

## 3. Scientific validation

Before untouched validation begins, the candidate hypothesis and executable
policy must be frozen. The frozen specification must include its signal,
population, regime, prediction point, direction, normalization, entry and exit
rules, risk limit, favorable and adverse outcomes, path-order rules, horizon,
gap/fill handling, cost assumptions, success definition, position-management
rules, and planned analyses.

Validation must use evidence unavailable during hypothesis formation,
exploratory evaluation, and parameter selection. The policy must be applied
chronologically without retrospective alteration. Movement after a policy exit
must never contribute to its result.

The AI Research Director determines whether untouched evidence validates,
qualifies, rejects, or leaves the predictive relationship unresolved.
Scientific interpretation must consider effect direction and magnitude, sample
adequacy and uncertainty, dependence, selection and multiple-testing effects,
stability across securities, periods and regimes, adverse path, and
reproducibility.

Deterministic code may enforce frozen specifications, untouched-sample
separation, temporal integrity, lineage, arithmetic, and execution contracts.
It may not substitute deterministic scientific judgment for the Research
Director's interpretation.

Scientific validation establishes whether a predictive relationship is
supported. It does not establish sufficient economic materiality for trading.
A scientifically validated but economically insufficient relationship may
remain durable knowledge or contribute to a later combined hypothesis.

For a candidate trading hypothesis to pass scientific validation as having
positive expectancy, the lower bound of its predeclared uncertainty assessment
for path-executable net expectancy must remain greater than zero on untouched
evidence. The uncertainty method must be scientifically appropriate to the
evidence and account for material dependence such as overlapping signals,
shared securities, and common market regimes. RD selects and predeclares the
method; deterministic code verifies faithful execution rather than inventing
the scientific method.

A material revision creates a new hypothesis identity and requires new
untouched validation.

## 4. Candidacy for trading promotion

A scientifically validated hypothesis may become a candidate for prospective
paper testing only when its frozen, path-executable validation evidence satisfies
all three requirements:

```math
EV_{conservative}>0
```

```math
EV_{net,point}\geq 0.15R
```

```math
EV_{gross,point}\geq 2C
```

`R` is the frozen adverse-risk unit. `C` is the upper-bound estimate of average
all-in trading costs. Conservative expectancy must use conservative probability
and outcome estimates, observed adverse paths, and upper-bound costs. Net point
expectancy is after costs; gross point expectancy is before costs.

All calculations must use realizable outcomes under the frozen policy:

```math
EV_{net,policy}=\frac{1}{N}\sum_{i=1}^{N}(X_i-C_i)
```

The previously discussed combination of greater-than-60-percent success at a
favorable movement of at least 1.5 ATR remains a strong human-utility reference
example. It is not the exclusive acceptable payoff structure and must not
constrain exploration or scientific validation.

Meeting the minimum requirements establishes eligibility for prospective paper
testing only. It does not establish attractiveness, priority, suitability for
meaningful capital, or live-trading authority. The `0.15R` requirement is a
rejection floor, not a research objective.

Among eligible hypotheses, the Research Director should compare conservative
expectancy, adverse path, opportunity frequency, time in trade, regime
stability, liquidity, capacity, cost sensitivity, and correlation with other
signals and positions. Greater durable risk-adjusted expectancy is preferred.

## 5. Prospective and live authority

Historical probability does not itself trigger an entry. A prospective paper
entry requires the frozen signal to be present, current applicability to remain
valid, conservative net expectancy to remain positive under current upper-bound
costs, and complete recording of signals, decisions, rejections, entries, and
outcomes.

Neither validation nor paper testing authorizes live trading. Live eligibility
requires reproducible prospective performance under frozen rules, realistic
execution and portfolio-risk treatment, complete decision lineage, no
retrospective selection or parameter adjustment, and separate explicit human
authorization.

No standard may be lowered retrospectively because results appear promising.

## 6. Screener eligibility and ranking

The future Stock Screener Engine must distinguish minimum eligibility from
comparative opportunity ranking.

The screener shall identify every current security for which a frozen,
scientifically validated, trading-promotion-eligible signal is present and the
hypothesis remains applicable. Every eligible candidate must be recorded,
including candidates later rejected or not selected by the Trading Engine.

Passing the `0.15R` floor means only that a candidate is eligible for
consideration. It does not mean that capital should ordinarily be assigned when
stronger or more portfolio-compatible opportunities are available.

The screener should rank eligible candidates using the governed evidence
available at the decision point, including conservative net expectancy,
expected return on committed capital, expected holding time, adverse path,
uncertainty, liquidity, cost sensitivity, regime applicability, opportunity
frequency, capacity, and correlation with existing positions and other
candidates. Ranking must not silently alter the frozen underlying hypothesis.

Outcomes must be tracked for both selected and unselected eligible candidates.
This preserves unbiased prospective evidence about the hypothesis separately
from portfolio selection, capital limitations, and Trading Engine constraints.

## 7. Trading Engine selection

The future Trading Engine receives eligible, ranked candidates from the Stock
Screener Engine. It may select, size, defer, or reject candidates according to
available capital and governed portfolio-level risk, including exposure,
concentration, correlation, liquidity, drawdown, and execution constraints.

A candidate that satisfies the minimum hypothesis gate may correctly receive no
trade. Nonselection does not invalidate the hypothesis and must be recorded with
its contemporaneous reason. The Trading Engine may not manufacture a signal,
change a hypothesis, or discard an eligible candidate from prospective
scorekeeping merely because it was not selected for capital.

## 8. Implementation consequence

The existing binary success ledger and deterministic 0.60 classifier cannot by
themselves represent this amendment. Before another paid autonomous Research
Director campaign relies on predictive-hypothesis status, the runtime contract
must preserve the frozen executable policy, path-realized gross and net outcome,
cost, risk-unit normalization, scientific validation assessment, and separate
trading-promotion assessment. Tests must prove that the three stages remain
distinct and that movement after a policy exit is never credited.
