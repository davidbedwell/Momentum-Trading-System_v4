# MTS v4 — Discovery Capacity-Aware Allocation Protocol — 2026-10-02

## Objective
Preserve the broad causal EV/p10 ranking edge while preventing the tail-risk deterioration observed when extra capital is allocated during crowded portfolio states.

## Evidence boundary
Discovery Development only for candidate generation. No additional Verification A and no Verification B access. Existing Discovery Holdout stays closed until representative nominees are frozen.

## Fixed signal-quality predictor
Historical expected return / historical p10 downside; only completed prior outcomes; minimum N=100; genome -> family -> global -> neutral backoff. Frozen scale remains 3.154602090106647. Do not search alternative predictors.

## Causal portfolio-state variable
At each entry session, use only the number of positions already open immediately before that session's new entries, plus the number of same-session new entries. This is known prospectively and contains no forward outcome information.

## Candidate families
1. Same-day top-50% EV/p10 boost with caps 1.25x and 1.50x, active only when pre-entry open-position count is at or below the Development median concurrency.
2. Same rule active at or below the Development 75th-percentile concurrency.
3. Same-day fixed-budget top-50% redistribution with caps 1.25x and 1.50x under the same median and 75th-percentile capacity gates.
4. Headroom-scaled boost: uplift attenuates monotonically as current open positions approach the structural concurrency ceiling; caps 1.25x and 1.50x.

Concurrency thresholds are structural exposure statistics, not return-optimized thresholds.

## Required metrics and gate
Use the prior allocation-architecture reporting and frozen gate unchanged: positive mean contribution; >=60% ticker/year/family breadth; ticker-cluster CI lower bound >0; <=15% ticker/genome positive-contribution concentration; terminal wealth > equal sizing; and max drawdown/CVaR5 may not both worsen. Also report exposure-matched equal sizing.

## Selection
Prefer the simplest broad family that passes across neighboring caps/capacity gates. Do not pick an isolated peak. Freeze at most two structurally distinct representatives before any Discovery Holdout replay.

## Integrity
No A3 outcome values may enter parameter choice. A3 motivates only the portfolio-capacity mechanism. No search or retuning on Verification evidence.
