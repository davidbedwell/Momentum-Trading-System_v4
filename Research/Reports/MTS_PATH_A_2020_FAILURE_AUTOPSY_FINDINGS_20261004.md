# Path A 2020 Failure Autopsy — Exploratory Findings — 2026-10-04

## Status
**NEW_RESEARCH_POST_RECOVERY — exploratory; no detector promoted or frozen.**

The original detector implementation and original derived feature tape were lost when Thunder was intentionally deleted after ChatGPT incorrectly stated backup completeness. The predictor-v2 panel used here is reconstructed from surviving specifications/raw market history. VIX/VVIX and OFR raw inputs are original recovered artifacts.

Protected portfolio evidence was not accessed. Portfolio CAGR/wealth/DD were not used to choose detector rules.

## 2020 causal sequence
The reconstructed daily tape shows distinct phases rather than one continuously simultaneous signal.

- 2020-02-24: VIX causal 252-session percentile = 100%; VVIX about 99.2%; median 5-day shock about 99.2nd bad-tail percentile.
- 2020-02-25: median breadth-positive-20 falls to about 26.4%.
- 2020-02-27: breadth-positive-20 about 7.6%; median-stock 252-day drawdown about 15.8%; VIX/VVIX extreme.
- 2020-02-28: breadth-positive-20 about 4.4%; median-stock drawdown about 16.8%.
- Funding/credit stress then accelerates. By 2020-03-03, lagged Funding 20-session change and acceleration are both at the top of their causal rolling distributions.
- 2020-03-06: lagged Funding CHANGE_20 = +0.501 and short acceleration = +0.1117; VIX/VVIX remain extreme and breadth remains severely damaged.

Interpretation: fast market shock/breadth damage appeared first; systemic funding confirmation followed.

## Experiment 1 — shock memory plus broad systemic confirmation
Short shock-memory and confirmation variants moved 2020 earlier, including Feb-27/28 and Mar-3, but were too noisy. The least-noisy tested variant still generated 21 outside-window alert episodes.

**Finding:** do not promote this mechanism. Simply adding memory or reducing confirmation is not justified.

## Experiment 2 — strict four-dimensional concurrence
Reconstructed the mechanism represented by the surviving successful heldout-2020 classifier using four dimensions: causal Funding stress percentile, market drawdown percentile, VVIX percentile, and breadth-positive-20 damage percentile.

A notable exploratory candidate is 95th-percentile threshold, 4-of-4 concurrence, 3-session confirmation.

Observed declarations:
- 2008: 2008-10-08 — too late for the GFC; not a substitute for B.
- 2020: **2020-03-05** — materially earlier than the surviving 2020-03-12 benchmark.
- 2022: 2022-01-27 — close to B/C's 2022-01-25 declaration.
- 2015 designated control: no declaration.

Nominal outside-positive starts: four.

## Inspection of nominal outside-positive starts
1. 2007-08-13 — median-stock drawdown about 10.8%, later about 14.5%; before the protocol's Oct-9 GFC peak anchor.
2. 2011-08-12 — severe 2011 correction; median-stock drawdown about 18.1%, later about 23.2%.
3. 2011-08-22 — continuation/retrigger within the same 2011 stress episode.
4. 2020-03-24 — immediately after the protocol's Mar-23 COVID reference trough; persistence of the same crash state.

Raw false-start count therefore overstates ordinary nuisance behavior. This does not validate the candidate; it means episode-aware auditing is required.

## Scientific interpretation
Current evidence favors the following:
- 2020 contained strong causal information before March 12.
- The failed FAST-A formulation was too narrow/morphologically brittle.
- Relaxing it indiscriminately creates many nuisance alerts.
- Strong concurrence across distinct market mechanisms is more specific and may move detection toward March 5 without portfolio fitting.
- A need not catch 2008 early because A/B/C operate as Boolean OR and B is the slow-deterioration path.

## Next required work
1. Audit strict-candidate alerts across the full evaluable history as contiguous stress episodes.
2. Compare 1/2/3/5-session confirmation around the strict high-concurrence family for stability, not earliest 2020 date.
3. Re-run leave-crisis-out logic where scientifically possible from reconstructed causal data.
4. Freeze at most a small defensible A candidate set before portfolio testing.
5. Only after freeze evaluate MTS DD, CAGR, terminal wealth, tail loss and turnover/cost.

A reduction in DD while holding or increasing CAGR is a win. Portfolio performance may judge the frozen detector but may not choose its rule.

## Current decision
**Do not freeze A yet. Continue the autopsy.** The March-5 strict-concurrence result is promising enough to investigate but has not earned promotion.
