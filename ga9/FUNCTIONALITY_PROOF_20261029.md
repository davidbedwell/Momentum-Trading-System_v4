# SYNTHETIC functionality proof — not historical performance

Executed 8 deterministic sessions through `ga9.execution.replay`, without evolution.
Two controlling niches (0/1) and two specialized chromosomes beat a higher-scoring
generalist at routing. They share one $100,000 account with 91% cash reserve: the
first specialist receives about $6,000 and the next only the remaining budget.
Fallback activates when eligible specialist scores fail threshold. Both paths use
membership, screen, threshold, correlation, slot, cash, sector and risk gates.
Routing is opt-in (`niche_first=True`); existing runner behavior is unchanged.

Run:

```
/opt/mts/.venv/bin/python -m ga9.functionality_fixture --output /tmp/ga9-proof-new
/opt/mts/.venv/bin/python -m unittest ga9.test_functionality_fixture ga9.test_execution ga9.test_first_replay ga9.test_benchmarks -v
```

26 tests passed. Tests verify prefix invariance under future mutations, execution-time
admission revocation, specialist and fallback gates, correlation rejection, next-session
open fills, 5 bp slippage plus 1 bp fees each side, nonnegative settled cash, unsettled
sale proceeds, accounting conservation, and an explicit exception on >8% drawdown.
The generalist-only counterfactual is separately executed with identical capital and
gates, never used to choose the realized policy after observing returns.

Artifacts: `artifacts/functionality_synthetic_verified_20261029/` contains inputs,
per-day decisions/orders/fills/NAV in `ledger.json`, full replay, full counterfactual,
QQQ source/hash audit, test output and SHA256 manifest.

Observed: 11 fills including ENTRY, REDUCE and EXIT; NO_TRADE decisions; final NAV
$99,952.072403; costs $17.978311; maximum drawdown 0.0479276%. Synthetic predeclared
benchmark final NAV $100,641.713443; excess NAV -$689.641040. Benchmark buys at the
first executable open, pays entry costs, and marks remaining shares without a
fictitious terminal liquidation. Two residual strategy positions remain marked.
Annualized metrics in raw engine output are engineering outputs only.

## QQQ correction

`artifacts/alpaca_repair_live_batch_20261029/accepted_raw.json` and its hashed
`response_*.json` sources contain 1,003 unique QQQ dates from 2022-01-03 through
2025-12-31. Existing `reuse_benchmark` verified source hashes (five responses,
including overlapping probe coverage). No network request was needed.

The previous `first_replay.run` did not search for a benchmark: it hard-coded
“No local QQQ…” while its ingestion function only consumed requested stock gaps.
That was an incorrect absence claim. The script now checks the existing raw cache
and reports raw availability separately from benchmark certification. The previous
artifact is retained as an audit record. Raw bars lack reconciled explicit
splits/distributions and historical availability certification; they are not yet an
admitted total-return benchmark. Real PIT admission remains unchanged.

## Remaining blockers

The architecture cannot guarantee a realized 8% ceiling across arbitrary overnight
gaps while filling at the next open. `enforce_drawdown=True` explicitly fails a
breached replay rather than clipping NAV or inventing a fill. This proves a hard
acceptance ceiling, not gap-proof loss prevention. If gap-proof prevention is a
required interpretation, the architecture fails that requirement.

Hand-authored signals and synthetic eligibility prove execution/routing mechanics,
not model calibration, feature estimation, chromosome profitability, historical PIT
membership, corporate-action reconciliation or real-data trading readiness. No real
symbol was newly admitted. GA8 was not edited and no long GA9 evolution ran.
