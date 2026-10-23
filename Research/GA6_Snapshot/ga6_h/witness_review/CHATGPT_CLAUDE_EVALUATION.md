# ChatGPT evaluation of Claude's GA6-H review

Accept: Real historical net EV, discovery-only data enforcement, full chromosome archive, meaningful Pareto improvement and bounded search runtime. Exclude CAGR and MDD from chromosome breeding.

Disagree: Fixed 20-session rank IC or top-minus-bottom returns are not realized net EV from actual 1–40-session entry, exit, stops and 10bps per-side costs. Use close-t signals and next-open execution. A mandatory population reset after 100 stagnant generations is not the agreed stopping policy and could prolong the experiment indefinitely. Fixed epsilon values need empirical noise calibration rather than arbitrary substitution.

Verify before rewriting: The existing breed function already uses nested tree_crossover. Duplicate fitness vectors do not inherently break nondominated sorting; reproduce the alleged bug first. Root crossover edge cases merit focused tests.

Defer: PIT universe reconstruction, lag gene, Sobol threshold refinement, extensive stock-disjoint transport until first genuine discovery evaluator works. Disclose survivorship and earnings timing limitations.

Fast path: Build minimal causal historical EV evaluator on existing data, repair archive/restart fidelity, enforce discovery split, then time-box a small benchmark and scale based on actual evaluations per second. Do not modify the separate running GA6.
