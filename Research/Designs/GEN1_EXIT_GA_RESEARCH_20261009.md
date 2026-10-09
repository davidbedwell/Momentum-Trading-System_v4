# Gen1 Path-Conditional Exit GA

Research objective: Discover causal sequential exit rules from known DEV80 trade paths of 4,360 Gen1 chromosomes, then test frozen policies on unseen chronological DEV80 trades.

Governance: DEV80 only. Do not touch DEV37, DEV50 or BLIND17. Preserve all 4,360 original chromosome entry rules and directions. Do not impose the later train-only preferred-horizon assignments: all 4,360 have evaluations for the original nine horizons (1,2,3,5,7,10,15,20,63). Treat those nine results as reference benchmarks, not nine separate independently discovered chromosomes. Use up to 63 sessions of path observation, subject to complete data and execution support. Do not claim a single original assigned horizon without provenance.

Discovery: Evaluate every eligible daily decision. Inputs include observable return trajectory, MFE, MAE, reversals, volatility, breadth, sector conditions, chromosome context, and elapsed time/remaining time to the 63-session research cap. GA discovers combinations and thresholds rather than imposing arbitrary checkpoints.

Execution: Replay trades sequentially with one entry and at most one exit. Execute at the next feasible price, with gaps and costs. Historical post-exit counterfactuals measure false signals but are never policy inputs.

Validation: Compare realized net return, drawdown, tail loss, profit capture, false exits, missed recoveries and turnover against all nine original horizon exits, fixed ATR, trailing ATR and time exits. Use chronological purges, episode-aware inference and multiplicity controls.

Engineering gates: PIT lineage and fills; complete trade-path reconciliation; sequential simulator tests; small budget-capped DEV80 pilot; freeze before unseen evaluation; scale only if unseen economic and risk gates pass.

Status: DESIGN ONLY; NOT CERTIFIED; NO GA LAUNCHED.
