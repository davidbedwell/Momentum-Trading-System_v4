# MTS v4 — Queued Cross-Sectional Selective-Switch Hypothesis — 2026-10-02

## Status
QUEUED ONLY. Do not execute until the active controller incremental-cost / lower-turnover study is completed and closed with findings and Pareto status.

## Motivation
MTS currently treats qualifying stock signals largely as independent capital requests. A separate architectural hypothesis is that capital allocation may improve if qualifying opportunities compete cross-sectionally against one another and against incumbent holdings, with residual capital parked in the safe asset.

## Research question
Does a causal rank -> incumbent/challenger comparison -> selective switch -> safe-asset residual architecture preserve MTS's portable opportunity signal while reducing turnover, weak entries, and portfolio tail risk?

## Candidate genome architecture to explore later
1. eligibility/universe filters;
2. MTS opportunity/genome score;
3. cross-sectional relative rank;
4. incumbent rank/persistence;
5. challenger improvement threshold before replacement;
6. minimum holding / switch hysteresis;
7. portfolio slot count and fixed/limited position sizing;
8. residual capital to 3% safe-asset proxy;
9. optional correlation/dispersion diversification constraint;
10. existing causal market-state controller as a separate portfolio-level layer, not baked in without testing.

## Governance
This hypothesis is inspired by a general portfolio-selection architecture and by MTS's observed turnover problem. It does not assume knowledge of any proprietary third-party rule, threshold, genome, or implementation. Freeze a full protocol and evidence boundary before any experiment. Do not consume untouched Verification evidence merely to explore it.
