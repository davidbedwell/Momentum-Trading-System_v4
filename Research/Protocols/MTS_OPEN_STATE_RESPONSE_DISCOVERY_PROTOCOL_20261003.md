# MTS Open-Ended Market-State / Response Discovery Protocol
Date: 2026-10-03
Status: FROZEN BEFORE OPEN-ENDED SEARCH

## Research question
What contemporaneously measurable market/portfolio state, if any, tells MTS when normal behavior should remain unrestricted, become constrained, or be shut down, and what capital/action response is justified by that state?

The search MUST NOT assume that the answer is binary, three-state, hybrid, or any fixed number of states. Discrete labels are not genome primitives. A useful solution may be continuous, piecewise, clustered, multi-dimensional, or may show no stable state structure.

## Evidence isolation
Use only the already-consumed 67-stock Discovery laboratory plus causal market information available through each timestamp. Heldout50, remaining Discovery, Verification A, and Verification B remain sealed. No event names, future crash dates, future drawdown labels, hindsight news, or LLM judgment may enter the deployable rule.

## Roles
Analysis Engine: deterministic calculation only.
GA: deterministic search over open state representations and response functions.
Sol: scientific interpretation, artifact/overfit challenge, and formulation of follow-up deterministic tests. Sol is not in the live decision path.

## Candidate causal information
Allow market returns/trend over multiple horizons; realized volatility, ratios and acceleration; breadth and breadth change; cross-sectional negative fraction; dispersion/correlation/convergence; drawdown state; MTS signal/opportunity density; live exposure/safe fraction; position count/concentration; new-position fraction; and causal rates/interactions among them.
Do not require any particular feature family.

## Open state representation
A genome may select a sparse subset of causal features and transforms, combine them through weighted continuous scores and/or deterministic nonlinear interactions, and map the resulting state coordinates to response continuously or piecewise.
No fixed state count. No GREEN/YELLOW/RED primitive. No mandatory warning/crash/recovery phases.
Complexity is penalized. Preserve interpretable feature contribution and neighboring-parameter stability.

## Open response
Primary response is a continuous target equity-permission/exposure value bounded [0,1], with residual capital earning the frozen 3% safe return. Do not restrict exposure to a 0/25/50/75/100 ladder.
The search may additionally discover deterministic modifiers to initial position commitment, adding permission, reduction/exit urgency, and re-entry ramp only when supported by evidence. These modifiers are optional, not assumed.
No leverage above 100%.
Normal MTS prospective entries still must justify leaving the frozen 3% safe asset.

## Objective and frontier
Four independent $100,000 resets:
E1 2006-09-15--2011-09-14
E2 2011-09-15--2016-09-14
E3 2016-09-15--2021-09-14
E4 2021-09-15--2026-09-14.
Primary economic objective is pooled compounded terminal wealth/CAGR after costs, jointly evaluated with economically significant drawdown. Preserve the Pareto frontier rather than collapsing the problem to drawdown minimization or return maximization.
Diagnostics: max DD, CVaR5, worst day, time underwater, DD depth/frequency, recovery, safe fraction, turnover/switching, false constraints, missed rebound/upside, and response smoothness.

## Search and validation
Primary costs 10 bps; sensitivity 0/5/15/20 bps.
Use leave-one-era-out: discover/select using three eras, freeze parameters/thresholds/scaling, apply unchanged to fourth; rotate four ways.
Search until frontier and mechanism families saturate, not a fixed genome count.
Preserve mechanism diversity and negative findings.
Challenge top families with feature ablation, neighboring perturbations, simpler controls, era dominance, and accounting/causality audits.
Do not open protected banks until architecture is scientifically frozen.

## Prior constrained run
The prior binary normal/derisk GA is evidence only. Its winning genome must not seed, constrain, or define this search. Its observed feature relationships may be included only as ordinary candidate evidence alongside the full causal feature set.
