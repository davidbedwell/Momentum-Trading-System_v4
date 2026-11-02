# Eligibility protocol

This phase audits existing evidence before any optimization. This document is retrospective screening, not preregistration. A search is permitted only if every condition holds:

- A validated chronological, cash-constrained baseline and counterfactual portfolio supports net performance, marked MDD and actual exposure objectives.
- At least 20 separated market events support a candidate relationship; correlated genomes and overlapping trades do not count independently. Use merged holding intervals with a 63-business-day gap as a conservative support proxy, without asserting independence.
- At least two materially active later chronological folds support repeatability. Four trades do not make a materially active fold.
- Incremental net economic benefit repeats across later folds and uncertainty supports that benefit, including skipped profitable trades and original costs. Raw per-trade mean improvement is insufficient.

Failing any condition stops the phase with NO-GA warranted. The newly calculated fixed diagnostic cannot reopen the stop. No optimizer implementation is necessary when the gate fails. Budget: 60 seconds for local audit excluding human review, no remote data, no live code mutation. Do not use a forced search to manufacture a positive result.

If a later separately authorized study meets eligibility, fit a small gate/sizer on earlier folds only, using MA in {10,20,50,100,200}, level and slope, with strict complexity bounds and a fixed evaluation budget. Freeze before later-fold scoring. Select on validated net portfolio performance/MDD and exposure, compare fixed breadth and baseline, retain original exits and execution costs, and stop on null evidence. Already inspected periods cannot become pristine OOS through a new split.
