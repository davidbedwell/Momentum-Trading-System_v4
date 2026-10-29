# MTS v4 — A3 Paradox Mechanism Audit — 2026-10-02

## Question
Why can causal EV/p10 sizing show broad positive trade-level/ticker contribution yet fail to improve compounded portfolio wealth?

## Evidence boundary
Discovery Development only for mechanism discrimination and architecture work. A3 may be referenced only as the motivating observation already opened; A3 outcomes MUST NOT be used to fit, rank, threshold, or select alternatives. Discovery Holdout remains closed during mechanism work. Remaining 55 Verification-A names remain researcher-blinded/sequestered. Verification B remains sealed.

## Deterministic calculations
Using the frozen Discovery Development population and causal EV/p10 score, decompose: (1) trade arithmetic contribution, (2) chronological portfolio compounding, (3) average/peak exposure and cash, (4) same-day opportunity overlap, (5) score rank versus absolute score, and (6) concentration of added capital through time. Compare absolute clipped sizing with budget-aware relative same-day allocation.

## Hypotheses formulated before this audit
H1: absolute per-trade weights change total exposure/cash through time, so positive arithmetic trade contribution need not imply superior compounded portfolio wealth.
H2: EV/p10 is more useful as a relative opportunity-ranking signal than as an absolute independent multiplier.
H3: when many opportunities overlap, unrestricted independent boosts crowd capital and can make chronology dominate arithmetic expectancy.
H4: a portfolio-budget-aware rule that prioritizes higher-ranked simultaneous opportunities should translate the signal into wealth more reliably than fixed absolute weights.

## Decision rule
Mechanism evidence may motivate a new Discovery experiment. Do not choose a Holdout nominee from this audit alone. Any candidate architecture must first demonstrate broad Development behavior and stable neighboring parameterizations; only then freeze representative nominee(s) before opening Discovery Holdout.
