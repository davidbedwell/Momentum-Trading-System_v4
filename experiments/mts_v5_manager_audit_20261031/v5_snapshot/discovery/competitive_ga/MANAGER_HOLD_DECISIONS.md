# MTS manager — approved HOLD and horizon decisions (2026-10-27)

These decisions are authoritative and supersede conflicting exploratory defaults.

1. No manager-imposed 40-session maximum or other universal holding horizon. A chromosome may recommend a time exit; the manager makes the portfolio decision. A stock may remain held beyond the originating chromosome's horizon when current risk-adjusted net expectancy justifies it. Portfolio risk controls and crash defense remain authoritative.
2. HOLD is an active investment decision, not merely absence of EXIT. At every close compare HOLD, ENTER, INCREASE, REDUCE, EXIT, and CASH on marginal expected NET portfolio contribution for comparable capital and forward horizon.
3. Re-estimate remaining upside, probabilities, downside/tail exposure, additional holding time, costs, uncertainty, controlling niche, and alternative chromosomes using only currently observable information and matured historical outcomes. The entry chromosome does not permanently control position management.
4. Compare incremental allocation blocks. The manager may HOLD a core allocation and REDUCE excess exposure to the same stock. No forced all-or-nothing decision.
5. Replace an incumbent only if the expected incremental advantage exceeds actual trading/settlement costs, changed portfolio risk, and an evidence-based uncertainty margin. No arbitrary fixed replacement threshold.
6. Keep cash as an active competing allocation; consider correlation and concentration. Preserve 10% per-symbol cap during learning, 1–2% portfolio-equity risk per trade, next-open fills, settlement, and crash defense.
7. Evaluate all potentially positive chromosomes in parallel; niche-first selection with GA4/Horizons fallback. The chromosome recommends; the manager decides.

IMPORTANT: Existing native GA6 research evaluator MAX_SWING_SESSIONS=40 is not a manager policy. Do not inherit this cap into manager integration. This document and MANAGER_GOVERNING_CONTRACT.md must be consulted before modifying allocation code.
