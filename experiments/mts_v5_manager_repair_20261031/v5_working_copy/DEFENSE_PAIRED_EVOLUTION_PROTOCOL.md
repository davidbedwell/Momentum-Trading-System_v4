# Paired defense-on/off portfolio evolution

Every frozen manager/chromosome configuration must be evaluated with defense disabled and enabled against identical synthetic sessions, candidate library, costs, and initial capital. In NORMAL state, before the first defense trigger, ON and OFF executions must be identical. A/B/B1/C trigger defensive portfolio behavior; R-1 governs recovery. The defense-enabled path must never receive future trigger or recovery knowledge.

Evaluate both paths as complete shared-capital portfolios, not as independent per-chromosome hypothetical MDD. Report portfolio CAGR, maximum drawdown, Calmar, after-cost net return, defense transaction costs, missed gains during defense, recovery timing, and synthetic SPY benchmark advantage. Compare the paired difference and allow the GA to retain either defense mode; never assume defense ON wins. Preserve existing risk gates and no-trade choice.

During Year 1 development, train on Year 1 only. Freeze both paths and compare in Year 2. Then learn from Year 2 failures and repeat frozen forward evaluations for Years 3, 4 and 5. Neither path may see forward-year results until that year's frozen evaluation completes. If the defensive controller is unimplemented or unavailable, mark defense comparison blocked rather than simulating an invented defense.
