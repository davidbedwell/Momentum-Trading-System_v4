# MTS v4 — Momentum Confirmation vs Add-On Allocation Protocol — 2026-10-03

## Question
Does the previously observed low-accumulated-momentum + renewed-acceleration state improve MTS when used as:
A) a hold/let-run confirmation, or
B) a causal add-on allocation trigger?

## Evidence boundary
Use only the already-consumed 67-stock Discovery development population and frozen bar/trade cache. Do not access remaining Discovery, Verification A, or Verification B.

## Frozen trigger
At +5, +10, or +20 sessions after entry while the original trade remains alive:
- medium-term momentum = 20-session return in bottom development quintile,
- renewed acceleration = change in 5-session momentum in top development quintile.
Thresholds are estimated from the consumed development population only and reported explicitly.
No lookahead.

## Arm A — Hold confirmation
For trades meeting the trigger:
- Compare original frozen exit with prespecified extensions of +5 and +10 sessions beyond the original exit, subject to bar availability.
- Also test a narrower rule: suppress any earlier momentum-based exit candidate while trigger remains active.
- Report incremental return, winner truncation/extension, loser worsening, tail behavior, and breadth by era/year/family/ticker.
- Do not assume extension is beneficial merely because remaining return from checkpoint was positive.

## Arm B — Add-on allocation
At trigger checkpoint, add a prespecified fraction of the original position:
- +25% of original position
- +50%
- +100%
No leverage above 100% gross portfolio exposure. If insufficient portfolio cash/capacity, scale add-on pro rata or skip; report frequency.
Add-on exits at the same frozen original exit first. A separate extension variant may only be evaluated after the same-exit result is reported.

## Portfolio evaluation
Reconstruct portfolio-level capital path using the frozen MTS opportunity set and independent era resets.
Costs: 0/5/10/15/20 bps on incremental transactions.
Metrics: terminal wealth, CAGR, max drawdown, CVaR5, worst day, turnover, safe/cash fraction, trades/add-ons, incremental value per add-on.
All four development eras must be reported separately.

## Controls
- frozen base MTS portfolio without confirmation/add-ons
- random add-on timing matched on trade age and approximate frequency where feasible
- high-momentum + renewed-acceleration trigger as a mechanistic contrast
- low-momentum without renewed acceleration as a contrast

## Interpretation
Hold-confirmation and add-on allocation are separate hypotheses. A positive per-trade association is not sufficient for portfolio promotion. Advancement requires economically meaningful portfolio improvement without disproportionate deterioration in max drawdown/CVaR and with reasonably consistent era behavior.

Development only. No deployable/prospective claim.
