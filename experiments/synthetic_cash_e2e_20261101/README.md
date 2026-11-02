# Bounded synthetic cash-constrained simulation

**SYNTHETIC ONLY. These are deterministic scenario results, not historical performance or authentic PIT validation.**

Executed 126 business sessions, ten invented assets, initial NAV $100,000. Existing source was imported directly; it was not edited. The synthetic callbacks exercise the repaired manager contract; they do not reproduce native model alpha. No GA, live orders, historical data, tuning, or further simulation runs.

Entry points: `discovery.competitive_ga.functional_niche_manager.run_slice` and `engines.portfolio_replay.kernel.Replay.day`. Source SHA-256 hashes are in `report.json`.

```bash
PYTHONPATH=/opt/Momentum-Trading-System_v5-alpha python3 experiments/synthetic_cash_e2e_20261101/run.py
```

| Scenario | Final NAV | CAGR | MDD | Calmar | Time-weighted equity | Fills |
|---|---:|---:|---:|---:|---:|---:|
| 70% entry target | $96,581.55 | -6.72% | 5.70% | -1.179 | 62.64% | 120 |
| 100% permitted allocation | $95,183.78 | -9.40% | 8.21% | -1.145 | 90.48% | 120 |
| Equal-weight buy-and-hold | $97,008.67 | -5.89% | 7.93% | -0.743 | 99.21% | 10 |

CAGR uses 252 sessions/year and initial capital before session zero. Exposure is the arithmetic mean of session-close equity/NAV, with equal session weights. Fills count buys and sells separately.

The 70% case requests 7% per asset on entry; the comparison requests 10%. Both permit 100% aggregate allocation subject to cash and risk gates. These are entry targets, not continuous exposure mandates: HOLD positions drift, and 70% reached 70.23% briefly. No portfolio rebalance or exposure governor was added.

Synthetic prices use fixed trigonometric paths with an 8% overnight shock at session 62. Dated synthetic proposals use a declared pre-run model cutoff and only the current date and filled holdings. Explicitly synthetic marginal net EV is a fixed positive hypothetical five-session return after assumed costs/risk, used for global cash priority. No estimate is calibrated to later returns, and no authentic PIT provenance is claimed. All synthetic proposals and EV observations are saved in the audit JSON files.

Costs: 5 bp fee, 10 bp full spread, 3 bp one-way slippage, 2 bp one-way impact. Buys execute at open × 1.001 plus fees; sells at open × 0.999 minus fees. Signals execute next open; sales settle T+1. Cash earns zero. Ordinary position entries cap at 10%; the kernel enforces a 2% modeled loss gate and 20% MDD admission latch. These are modeled controls, not guaranteed realized loss ceilings.

Benchmark: same ten assets, capital, dates, first eligible open, and buy costs; equal dollar allocations followed by holding. All portfolios use terminal marks; the strategy has its scheduled final exit while the buy-and-hold benchmark remains invested. The exposure and turnover differences are intentional, so this is not a risk-matched alpha estimate.

Reconciliation independently rebuilds quantities, settled cash, T+1 receivables, fees, realized and unrealized P&L, and daily NAV from fills. Maximum error: $7.28e-11. Final 70% NAV = $32,148.24 settled cash + $64,433.30 receivable; final 100% NAV = approximately zero settled cash + $95,183.78 receivable. Both have zero final equity. Tiny negative cash (−$5.82e-11) is floating-point residue within the $1e-7 assertion tolerance. Five 70%-case final-close signals remain unexecuted; zero in the 100% case.

Control probes PASS: sale proceeds cannot fund same-open purchases; T+1 release permits next-session purchases; oversized modeled risk is clipped; an opening gap triggers the MDD latch and blocks new risk while allowing exits. Main scenarios did not breach the 20% threshold.

Execution issue: initial `python` command failed (127, executable missing); the direct `python3` command with the requested PYTHONPATH passed (0). No simulation assertion failures. Hard stop after this bounded run.

Artifacts: `run.py`, `runner.patch`, `report.json`, `synthetic_prices.csv`, scenario daily CSVs and audit JSONs, and benchmark daily CSV.
