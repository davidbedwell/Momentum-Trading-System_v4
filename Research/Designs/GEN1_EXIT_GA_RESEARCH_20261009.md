# Gen1 Path-Conditional Exit GA

Research objective: Discover causal sequential exit rules from known DEV80 trade paths of 4,360 Gen1 chromosomes, then test frozen policies on unseen chronological DEV80 trades.

Governance: DEV80 only. Do not touch DEV37, DEV50 or BLIND17. Preserve original chromosome entries, directions, and train-only assigned horizons. Unsupported horizons remain ineligible.

Discovery: Evaluate every eligible daily decision. Inputs include observable return trajectory, MFE, MAE, reversals, volatility, breadth, sector conditions, chromosome context, and remaining horizon. GA discovers combinations and thresholds rather than imposing arbitrary checkpoints.

Execution: Replay trades sequentially with one entry and at most one exit. Execute at the next feasible price, with gaps and costs. Historical post-exit counterfactuals measure false signals but are never policy inputs.

Validation: Compare realized net return, drawdown, tail loss, profit capture, false exits, missed recoveries and turnover against original horizon exits, fixed ATR, trailing ATR and time exits. Use chronological purges, episode-aware inference and multiplicity controls.

Engineering gates: PIT lineage and fills; complete trade-path reconciliation; sequential simulator tests; small budget-capped DEV80 pilot; freeze before unseen evaluation; scale only if unseen economic and risk gates pass.

Status: DESIGN ONLY; NOT CERTIFIED; NO GA LAUNCHED.
