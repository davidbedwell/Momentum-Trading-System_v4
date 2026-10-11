# Superseding execution clarification — 13-window Normal GA

This supersedes the prior interpretation that any trade overlapping the retrospective peak+10 through trough+10 crash window should simply be discarded.

- The historical crash window is inclusive, from peak + 10 trading sessions through trough + 10 trading sessions, using the frozen episode calendar. It is an oracle research boundary, not a substitute for causal A/B/B1/C.
- A Normal position opened before the boundary is liquidated at the first executable open at the start of the crash exclusion, with realized pre-liquidation P&L, costs, and turnover preserved. It is **not** retroactively removed from the trade record.
- No new Normal purchases within the crash exclusion. The resulting uninvested allocation receives the historical cash/T-bill return while held.
- After the exclusion interval ends, Normal purchases remain blocked until the causal R-1 controller declares NORMAL. R-1 decisions are end-of-session; orders may execute at the next open. If R-1 is already satisfied at the boundary, resumption is eligible at the next valid open; never assume automatic resumption merely because the calendar interval ends.
- Defensive opportunity trades, if modeled, belong to the separate GA Crash study, not Normal GA fitness.
- Execution simulation must implement forced liquidation, cash carry, next-open timing, controller state, transaction costs, and non-stitching across the interval. A horizon eligibility mask alone does not satisfy this protocol.
- Protected heldouts remain untouched. Certification and end-to-end execution tests must pass before launch.
