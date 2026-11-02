# Trading Engine — Portfolio 3 Implementation Charter
Date: 2026-10-27
Status: Implementation scope frozen for first parity milestone; no performance certification.

## Objective
Maximize defensible incremental economic value of MTS GA6/GA7 with A_v2/B/B1/C + R-1 versus SPY with the SAME defense. Portfolio 1 SPY passive is the ultimate economic baseline. All portfolios begin at $100,000 on identical sessions.

## Existing research contract
/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518/ga6_ga7_matched_evaluation_contract.yaml
Status there: BLOCKED_UNTIL_IMPLEMENTED_AND_PARITY_TESTED. Do not relabel this as certified.

## Portfolio 3 build order
1. **Adapter**: translate GA6 and GA7 native decisions into immutable timestamped signal, desired position, risk, exit, and lineage records. Never infer next-open fills from same-day closing signals.
2. **Execution parity kernel**: one deterministic daily event loop with shared bankroll, fills, fees/slippage, splits/dividends, T+1 settlement, cash/SGOV accrual, mark-to-market NAV and reconciliation. Unit tests must prove identical synthetic signals yield identical fills/NAV for GA6 and GA7 adapters.
3. **Defense**: reuse exact A_v2/B/B1/C + R-1 state machine, next-open liquidations, entry block and recovery. Compare its event calendar against portfolio 2, with no separate approximations.
4. **Selector**: ranked competing opportunities, positions held through time, native exits, scale/add/reduce, cash feasibility, 10% symbol learning cap, 2% risk ceiling, max three per sector, correlation-aware risk; no forced trades.
5. **Ledger**: every candidate accepted/rejected with reason, orders, fills, positions, NAV, exposures, costs, regime, benchmark attribution and counterfactual outcomes.
6. **Discovery-only evaluation**: deduplicate and rank chromosomes, first GA6-only and GA7-only, then combined selector; compare all against SPY and defended SPY on matched DEV79 chronology.
7. **Freeze and proof**: freeze all code, candidates, allocation, defense, data and selection rules before touching DEV87. No heldout peeking or tuning.

## First gate deliverables
- Input/adapter schema audit with real GA6 and GA7 ledger samples.
- Deterministic execution-parity tests with cash/NAV reconciliation and defense transition fixtures.
- Reproducible matched discovery replay with daily NAV and baseline deltas.
- A GO/STOP/RESEARCH verdict grounded in incremental excess wealth, drawdown and transferability, not cherry-picked chromosome CAGR.

## Current blockers
- Existing v5 selector and counterfactual implementations are research-grade and incomplete.
- GA6 and GA7 EV units differ; direct EV ranking is invalid.
- Current GA7 portfolio metrics are not execution-parity certified.
- Actual defense state-machine and its dependencies must be imported/tested without changing semantics.
- DEV87 is reserved until predeclared freeze.

No changes to live GA processes, historical data, or heldout sets are authorized by this charter.

## Competitive GA addition
The selector itself is a GA, separate from GA6/GA7 discovery. It evolves causal portfolio policies over both families of immutable candidate signals, with no guaranteed family quota. Fitness is computed through full shared-bankroll chronological replay under the same A_v2/B/B1/C + R-1 defense as benchmark 2. The execution kernel enforces immutable hard risk limits. Compare GA6-only, GA7-only, deterministic combined selection, evolved combined selection and defended SPY; guard against selector overfitting using chronological folds and untouched DEV87. Design contract: discovery/competitive_ga/README.md.

## Implementation checkpoint 2026-10-27
Created engines/portfolio_replay/kernel.py: deterministic first-pass event loop with next-open pending signals, common GA6/GA7 signal interface, fee accounting, 10% symbol cap, conservative non-reuse of same-day sale proceeds, cash/dividend/split hooks, daily NAV, and externally supplied defense state. Created tests/test_portfolio_replay_kernel.py: four initial tests pass. NOT certified: no actual GA6/GA7 adapters, no A_v2/B/B1/C/R-1 integration, no complete T+1 release ledger, no real price/earnings/PIT inputs, no sector/correlation/risk engine, no evolved selector, no SPY benchmark run. Do not infer a trading edge from this checkpoint.

## Iterative research governance
Competitive GA is a repeated discovery/review/revision/replay program, not a single run. Each iteration includes diagnostics, adversarial Claude/Grok review when available, versioned hypothesis-led modifications and comparable rerun. Keep discovery folds distinct from untouched DEV87. Protocol: discovery/competitive_ga/ITERATIVE_RESEARCH_PROTOCOL.md.

## Causal counterfactual ledger checkpoint — 2026-10-27
Added engines/counterfactual_learning/causal_ledger.py and tests/test_causal_ledger.py. Immutable decision records carry decision date, selected/rejected status, chromosome/family, feature snapshot hash, niche/regime model versions, defense state and reason. Alternative outcome records carry observed-through date, maturity date, scenario, replay manifest hash and incremental net value. Learning API filters out outcomes not yet matured and logs policy hash and exactly which outcome IDs were accessible. Four new ledger tests pass; 15 relevant tests pass overall. This is a standalone provenance/temporal-gating ledger, NOT a full portfolio counterfactual replay or integrated Competitive GA learning loop. Next: connect to shared execution events, ensure immutable persisted state and real alternative replay with proper cash, defense and risk parity.
