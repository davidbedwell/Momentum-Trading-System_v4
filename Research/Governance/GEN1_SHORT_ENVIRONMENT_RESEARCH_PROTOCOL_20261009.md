# Gen1 SHORT Effectiveness by Market Environment — Research Protocol (2026-10-09)

Status: User approved investigation; **protocol proposal**, not frozen numerical definitions or authorization to tune on protected data.

## Research question
Across all 2,180 SHORT genomes (not only the 12 preliminary positive-EV genomes), which *ex-ante observable* market environments and holding durations predict reliable positive net EV? Test competing hypotheses: fast shock / crash; persistent declining bear; grinding internal weakness; rebound / trend repair; ordinary rising market; sideways / mixed.

## Controls
- Use only authorized research/DEV data. DEV37, DEV50, BLIND17 remain untouched. Do not select regimes retrospectively using future returns, realized troughs, or outcomes of candidate trades.
- Use existing A/B/C defensive detectors and R-1 recovery components as candidate **point-in-time features**, not pre-declared truth labels. Also analyze continuous shock velocity, breadth, realized volatility, trend slope, funding stress, and recovery strength where genuinely available at entry.
- Record environment **at entry** and time-varying environment during each position. Distinguish entry conditioning from duration/exit interactions.
- Measure all 23 currently evaluated horizons (1,2,3,4,5,6,7,8,9,10,12,15,18,20,25,30,35,40,45,50,55,60,63), and longer 64–126 only after Phase B produces legitimate observations.
- For each genome × horizon × environment, report number of trades, effective independent samples, EV_net, uncertainty bounds, positive-EV fraction, drawdown/MAE diagnostics, and matched LONG/passive comparators under identical dates and costs.
- Correct for repeated overlapping observations, correlated market episodes, selection over horizons/genomes/environment labels, and sparse episodes; report uncertainty and effective independent crash episodes, not only thousands of trade rows.
- Compare short duration against long duration **within the same genome and same entry environments** before inferring short duration superiority. Evaluate adverse rebound and sustained-bear hypotheses.
- Make no changes to the 168 provisional allocation, Pareto rubric, MAE zero-selection-influence, SHORT candidate preservation, or Gen2 gates based on this protocol alone.

## Engineering prerequisites
1. Audit whether existing Gen1 outputs retain trade-level entry dates, returns, and time-varying market features; aggregated horizon summaries alone cannot establish environment effectiveness.
2. Verify PIT regime-feature lineage, A/B/C and R-1 timestamps, and eligible data partitions.
3. Predeclare environment definitions, multiple-testing corrections, episode clustering, and minimum sample sufficiency **before running conditional selection**.
4. Generate reproducible environment × horizon tables, charts, and a failure-analysis report; no retroactive relabeling to make results attractive.

Do not claim environmental findings before these prerequisites are complete.
