# MTS v4 — Momentum Transition / Exhaustion Audit — 2026-10-03

## Question
Does the transition of momentum—acceleration, deceleration, exhaustion, or reversal—contain useful causal information for MTS entry, hold, or exit decisions beyond momentum level itself?

## Evidence boundary
Use only the already-consumed 67-stock Discovery development population and existing frozen trade/bar cache. Do not access remaining Discovery, Verification A, or Verification B.

## Governance
Analysis Engine performs calculations only. No prospective/deployable claim. Freeze protocol before results. Do not optimize on sealed evidence.

## States
At entry and at +5/+10/+20 sessions while the original frozen trade remains alive, calculate causally:
- 5/10/20/60-session returns
- 5-vs-prior-15 and 10-vs-prior-20 acceleration
- change in 5-day momentum over prior 5 sessions
- change in 10-day momentum over prior 10 sessions
- SMA20 and SMA50 slope and change in slope
- distance from 20/60-day high and change in distance
- drawdown from post-entry running high
- recent reversal: positive medium-term momentum with negative short-term momentum
- renewed acceleration: positive medium-term momentum and improving short-term momentum
- exhaustion: high medium-term momentum/proximity-to-high combined with decelerating short-term momentum

Thresholds for high/low states use pooled development quantiles reported explicitly; continuous relationships are also reported so conclusions do not depend on a single cut.

## Outcomes
Entry: original frozen trade return, win probability, tail loss, >=1.5 ATR success where available.
Hold checkpoints: remaining return to frozen exit, forward 5/10-session return, adverse/favorable excursion where available.
Exit experiment: for each prespecified transition state at each checkpoint, compare causal liquidation at checkpoint with original frozen exit. Report mean/median delta, fraction improved, winner truncation, loser avoided, tail effect, and breadth by year/family/ticker.

## Required controls
Compare transition variables against their underlying momentum level. Report year, family, and ticker directional breadth. Do not interpret pooled averages alone. Explicitly test whether an exit rule improves losers by sacrificing disproportionate future winner return.

## Interpretation
Classify evidence separately as entry-selection, hold-confirmation, exit-warning, interaction-only, or unsupported. Momentum level and momentum transition must not be conflated.
