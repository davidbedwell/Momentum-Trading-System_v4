# Implemented v5 Counterfactual and Selector Modules

## Native v5 modules (initial integration)
- engines/counterfactual_learning/counterfactuals.py — trade-level hold vs exit/reentry research
- engines/counterfactual_learning/portfolio_counterfactuals.py — preliminary chronological shared-capital opportunity accounting
- engines/counterfactual_learning/selector_learning_fourfold_20261025.py — matured shadow ledger, chronological folds and retained selector memory
- engines/counterfactual_learning/selector_fold_trainer_20261025.py — chronological fold trainer
- engines/portfolio_selector/shared_selector_engine_contract_20261025.py — candidate decision contract and position ownership
- engines/portfolio_selector/shared_selector_competition_20261025.py — preliminary shared-cash proposal allocator

These are importable from the v5 project root with PYTHONPATH=. . GA6 imports have been replaced with v5 module imports. Training artifacts are directed to v5/runtime/selector_learning_fourfold. GA6 source files remain unchanged and are archived under research/archive/ga6_counterfactual_recovery.

## Verification
- Shared selector contract self-test: PASS
- Shared capital competition self-test: PASS
- V5 module imports, trade/portfolio smoke assertions, output path isolation: PASS
- Original GA6 baseline tests: 3 passed (run against original GA6 implementation, not a v5 certification)

## Not yet production complete
- The recovered allocator does not yet enforce all approved symbol/sector/correlation/risk caps and realistic execution constraints.
- The portfolio counterfactual comparison is not a complete marked-to-market alternative-portfolio replay.
- Shadow ledger needs a certified signal/outcome producer, market data and actual portfolio fills.
- No validated end-to-end strategy-to-execution integration or live trading authorization.

## Module policy
Put code in its owning engine, not in root or miscellaneous research. Keep frozen source snapshots in research/archive. All new modules must declare inputs/outputs and receive tests before integration. Placeholder directories do not imply implemented engines.
