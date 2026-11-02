# Competitive GA iterative research protocol
Status: APPROVED RESEARCH WORKFLOW, NOT AN AUTOMATED RUNNER

## Repeatable cycle
1. Freeze and hash the current engine, input data, chromosome pool, controller version, experiment config and train/validation fold boundaries.
2. Run a budgeted Competitive GA evolution on chronological discovery-training folds using actual common-kernel portfolio NAV fitness. Save every genome, ancestry, random seed, fitness component and checkpoint.
3. Independently replay finalists on later discovery-validation folds. Compare defended SPY, GA6-only, GA7-only, deterministic combined selector and Competitive GA under identical defense, fills, capital and fees.
4. Generate diagnostic packet: terminal wealth, CAGR, MDD, Calmar, net excess wealth vs defended SPY, regime/year splits, trade count, hold period, EV, turnover, slippage, cash drag, concentration, sector/correlation, GA6/GA7 attribution, capacity/replacement reasons, drawdown episodes, fold stability, leakage and parity audit.
5. Assistant proposes causal hypotheses for failures and strengths, with expected benefits, cost and overfit risk; do not cherry-pick solely on best CAGR.
6. Send design, metrics, ledgers, diagnostics and critiques to Claude and/or Grok if available and authorized; ask for adversarial review. Record raw reviews, contradictions and disposition. External reviews do not substitute for evidence.
7. Prioritize at most a small number of testable changes per iteration; pre-register hypotheses and acceptance gates; change versioned code/config, not historical results.
8. Rerun under comparable discovery conditions; report both improvement and regression, compute burden and sensitivity. Keep prior champion unchanged until challenger clears gates.
9. Stop/redirect when improvements plateau, tests expose leakage, complexity dominates incremental gain, or forward discovery validation fails to beat deterministic baseline and defended SPY.
10. Only after research-cycle selection: freeze all policies, data definitions and code; use untouched DEV87 once as independent confirmation. Failed proof is reported, not tuned away.

## Controls
- Keep discovery-training, discovery-validation and final untouched proof separate.
- Never allow future-realized trade outcomes in time-t selection; shadow feedback becomes available only when realized.
- Evaluate the full joint portfolio with A_v2/B/B1/C + R-1, not isolated chromosome profits.
- Archive complete run artifacts and reviewer critiques; avoid silent revisions.
- Optimize scientific return per compute-hour: staged fidelity, deterministic baselines, early elimination of broken/invalid genomes, checkpoint and resume; never weaken final fidelity.
- Do not automatically launch costly cloud runs or external model calls without confirming availability, cost and scope.
