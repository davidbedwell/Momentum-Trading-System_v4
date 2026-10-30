# GA9 bounded engineering session — 2026-10-30

Stopped after three repair cycles: no valid end-to-end economic proof. NO_TRADE; no GA, forward selection, promotion, or GA8 process intervention.

## Changes and hypotheses

1. Replace capital-times-constant risk proxy with sum(value * max(0,1-stop/mark)); admission uses remaining 2% NAV risk budget divided by actual candidate stop distance plus entry costs. Separate position cap, capital exposure, cash reserve, stop risk and realized drawdown. Remove 8% research rejection; retain reference. Remove first-16 and full-period-completeness universe filters; reuse causal multi-horizon daily screen.
2. Build frozen top-ten momentum diagnostic over all 125 non-quarantined archive symbols, using only 2022-2024 exposed development data; QQQ fixed before replay. Resolve isolated-copy partition dependency by read-only Research symlink. Initial baseline: CAGR 8.80%, MDD 14.75%, Calmar .597, excess CAGR -29.80 percentage points, mean exposure 50.65%. Audit discovered fixed-entry stop risk grew to 8.07% as unrealized profits accumulated. This result fails the planned-risk requirement.
3. Ratchet protective stop daily to at least close*(1-gene.stop_distance), execute breached stops next open. Add regression for gains not inflating planned loss-at-risk and replace obsolete hard-8% tests. Same baseline rerun: CAGR 16.06%, MDD 20.01%, Calmar .802, excess CAGR -22.55 percentage points, exposure 60.72%, maximum close planned risk 1.6124%. CAGR improved but drawdown worsened; neither result dominates on both objectives. No policy was selected for forward deployment.

## Verification

27 tests passed: ga9.test_engineering, ga9.test_execution, ga9.test_screening, ga9.test_objective. This includes future-prefix invariance, late listing eligibility, 40% capital at 5% stop = 2% planned risk, risk cap rejection above 2%, explicit gap fill, realistic deployment, dividends/settlement, abstention, objective, and accounting. Final max reconciliation error 7.28e-11, minimum settled cash $9,232.46. No full repository suite run.

Reproduce from this directory using /opt/mts/.venv/bin/python -m unittest ga9.test_engineering ga9.test_execution ga9.test_screening ga9.test_objective -q and /opt/mts/.venv/bin/python -m ga9.engineering_baseline NEW_OUTPUT.

Ranking diagnostic: average top-five versus bottom-five net 20-session returns among positive-momentum eligible names: 2022 +1.882% versus -1.794%; 2023-24 +2.938% versus +1.591%, spread +1.347pp. Overlapping labels are not independent; these are exposed development diagnostics, not forward evidence or a fitted net-edge forecast. Absolute positive return does not establish QQQ-relative edge.

## Limits and remaining work

Archive membership is not verified PIT membership. Daily eligibility uses currently observed valid bars and trailing history, never future completeness. Full historical eligible universe, delisting outcomes, dividend/adjustment parity, and full-universe equal-weight secondary benchmark remain unproven/unimplemented in this runner. No sealed 2025/2026 outcomes used for selection. Replay missing held marks raises an error instead of silently filling. Sector metadata unknown; sector constraints disabled for the diagnostic, all stocks appear UNKNOWN. Individual weights can drift above entry cap before next-open exits.

2% is planned stop loss-at-risk, not guaranteed realized loss or maximum drawdown. Daily ratcheting stops and admission sizing enforce the model's defined risk; execution gaps/slippage and intra-session moves can exceed it. Realized 20.01% MDD is allowed in research and is not confused with the 2% planned risk constraint. Costs are fixed 5bp slippage +1bp fee each side, conservative T+2. QQQ NAV includes entry cost but the generic benchmark metrics report zero fills/costs; do not interpret those metadata as a free fill. Both paths mark residual holdings without terminal liquidation. Distributions and corporate actions are unverified price-return assumptions.

GA defaults/mutation search and old supervisor entrypoints are not approved by this repair: some retain legacy benchmark policies and manager weights. Only engineering_baseline is the bounded reviewed entrypoint; no long GA until those paths are migrated and net-edge proof exists.

Next scoped session: isolate ranking, turnover and stop-exit drag versus QQQ on development data; add total-return benchmark parity and secondary full-universe benchmark; migrate remaining GA configuration only after baseline proof. Estimated 1-2 hours engineering plus data availability, not a success ETA. Stop here per no-proof/three-cycle limit.
