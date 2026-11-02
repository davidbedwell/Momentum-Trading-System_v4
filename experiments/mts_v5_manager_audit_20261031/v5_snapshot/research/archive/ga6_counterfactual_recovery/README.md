# GA6 Counterfactual Recovery — 2026-10-27

## Status
Recovered research modules from /opt/mts/ga6 into this directory without modifying the GA6 originals. Original tests copied to ../../tests. Baseline pytest result: 3 passed.

## Recovered modules
- counterfactuals.py: per-entry hold versus exit/reentry comparisons, including fee and cash-gap effects.
- portfolio_counterfactuals.py: basic shared-cash chronological entry/exit competition; **not** full portfolio counterfactual replay.
- selector_learning_fourfold_20261025.py: shadow outcome schema, maturity gating, train/proof folds, persistent chromosome/niche memory.
- selector_fold_trainer_20261025.py: causal training fold orchestration; references original ga6 package and absolute /opt/mts/ga6 output location.
- shared_selector_engine_contract_20261025.py: proposal validation, entry ranking and position ownership; references original ga6 package.
- shared_selector_competition_20261025.py: research allocator with shared cash.

## Important limitations / integration gates
1. These are unmodified recovery snapshots, not import-ready independent v5 components. The trainer and selector contract import from ga6; the learning module has an absolute GA6 output path. Do not execute the trainer in v5 until these dependencies and output paths are isolated.
2. The portfolio research comparison does not simulate full daily NAV, drawdown, settlement, realistic mark-to-market, competing full-horizon counterfactual branches, or live broker parity.
3. The shadow ledger schema supports feasibility and matured outcomes, but no complete execution-equivalent rejected-trade outcome producer is yet connected.
4. Existing tests demonstrate narrow behavior only; do not infer historical or production certification.
5. Preserve GA6 originals and historical research artifacts; integrate via adapters with versioned contracts, and create v5-specific tests before training.
6. No live orders authorized.

## Next engineering step
Build an isolated v5 package with stable opportunity schema, single shared bankroll simulator, realistic chronological execution, and replay of feasible alternatives. Connect mature shadow outcomes to selector learning, then run walk-forward portfolio baselines and proof evaluation.
