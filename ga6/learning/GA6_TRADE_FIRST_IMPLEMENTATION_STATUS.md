# GA6 trade-first adaptive learning — implementation status

## Frozen objectives
- **Primary**: learn feasible entry, decline, size, scale, hold and exit decisions using matured, time-t-valid evidence; optimize net trading expectancy, capital efficiency, tail risk and reliability without collapsing trade discovery into CAGR.
- **Secondary**: test whether those decisions improve *one* actual shared-capital portfolio's net growth, CAGR, MDD and Calmar relative to a fixed-selector control.
- Next-open execution, 40-session cap, earnings/membership/defense/risk vetoes, fees, settlement and chromosome ownership must remain binding.

## Implemented in this change
- Historical shadow scoring supports annual cash-yield-adjusted *trade-level* excess returns and retains strict earlier-than-decision label maturity.
- Trial rating removes the algebraically redundant gross-purchases efficiency metric and renames descriptive gaps to avoid suggesting causal regret.
- Independent NAV assessment function computes portfolio growth, CAGR, MDD, Calmar and optional same-period baseline deltas from **supplied real NAV observations**. It does not invent shared fills.
- Unit checks cover label timing, holding-period opportunity cost, NAV drawdown and chronological inputs.

## Still required BEFORE running a valid adaptive portfolio comparison
1. Capture **all** feasible time-t actions and constraint outcomes, including deliberate WAIT/DECLINE vs blocked entry; preserve frozen evaluator via an auditable wrapper or separate replay, never silently patch it.
2. Implement next-open **shared settled-cash** event replay, concurrent opportunity allocation, fixed owner per open position, earnings/defense/risk vetoes, fees and corporate-action handling.
3. Establish single-genome event/fill/NAV parity against frozen reference; fail closed on mismatches.
4. Implement paired trade counterfactuals for scale-in/out and hold/exit with exact lot accounting and no hindsight action selection.
5. Connect matured trade fitness to the actual chronological selector, with a fixed-selector baseline, and feed **real** daily NAV into portfolio assessment.
6. Run DEV first; preserve held-out validation until design frozen. Include dependence-aware uncertainty and promotion gates.

**Do not run or describe the current independent-shadow comparison as a validated adaptive shared-capital CAGR experiment.**

## Shared-capital replay increment
- `shared_capital_replay.py`: one real SettledLedger for all chromosome proposals; next-open execution, actual available settled cash, fees, immutable per-symbol owner, capacity, membership, earnings and execution-day defense checks, mandatory 40-session/defense liquidation, and actual daily NAV.
- `verify_reference_parity`: fail-closed, every-fill and every-session NAV comparison with frozen-evaluator capture.
- `test_shared_capital_replay.py`: synthetic tests for competing cash demands, unsettled proceeds, ownership, execution-day defense, and intentional fill/NAV parity corruption.
- **NOT DONE**: real frozen-evaluator single-genome integration parity; actual decision capture and constraints mapping; live chronological adaptive proposals; scaling/exit counterfactuals; full study rerun. Synthetic parity tests do not establish frozen-evaluator parity.
- A shared replay can legitimately differ from independent reference portfolios when chromosomes compete for capital. The strict single-genome reference parity test must use the same orders, risk policy and settlement configuration.
