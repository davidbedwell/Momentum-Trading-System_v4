# GA8 portfolio-first research engine

Independent package for MTS v4. No imports from or modifications to GA6/GA7.
Runtime outputs: `/opt/mts/ga8`. This is a historical funded-capital simulator;
it does not connect to a broker.

From the isolated v4 root:

```bash
/opt/mts/.venv/bin/python -m unittest -v ga8.test_engine
/opt/mts/.venv/bin/python -m ga8.run --generations 3 --budget 180 --seed 80079
/opt/mts/.venv/bin/python -m ga8.verify
```

The local panel path is declared in `run.py`. Required dependencies are pinned
in `requirements.txt`. Each run reads only the 2022–2026 panel. The delivered trial includes an explicit
accounting-correction re-evaluation recorded in `holdout_access.json`; do not
describe its final window as globally untouched. Evaluation inputs
are causal at each decision date; 2026 outcomes are opened only after freezing
the model trained through 2024. Re-running overwrites runtime outputs; use
`--output /tmp/ga8-reproduction` for an independent reproduction. `verify` reads
the default output directory and only replays development, never final validation.

Stop conditions: at most three generations by default, eight portfolio candidates
per generation, and 180 seconds per training fold. Budget checks happen between
candidates; a candidate and its three ablations finish atomically. All native
replays are serial because the full measured trial is about a minute; no worker
pool is kept idle and no parallel duplication increases memory or IO. CLI bounds
are 1–10 generations and 1–900 seconds per fold. 100 stagnant generations remains
a secondary stop, unreachable under this pilot's stricter bounds.

Read `status.json` for stage, command/PID, completed checks, elapsed runtime,
evaluation throughput, ETA and blockers. PID is executor-namespace-local; use the
session job controls to interrupt. Stage ETA is a measured estimate for the
current search, not a deadline for all remaining packaging work.

Evidence: `inventory.json`, `smoke.json`, `shadow.json`, `pilot_lineage.json`,
`pilot_search.json`, `pilot_shadow_bank.json`, `functionality_evidence.json`,
`train_2023_*`, `train_2024_*`, `fold_2023.json`–`fold_2025.json`,
`frozen_model.json`, `final_holdout.json`, `final_shadow.json`, `results.json` and
`pilot_report.md`. Ledgers record native fills, portfolio equity and drawdown,
fees, attribution, parentage, active families, niche coverage and funded ablations.
The shadow bank includes nonselected candidate genes, each with its own native
account. These accounts are never added to funded NAV.

No survivor means the target failed; best infeasible portfolios are retained as
research diagnostics. Calmar >1.5 and MDD <20% must hold across all chronological
tests before promotion. Cash-only has zero return and Calmar zero, hence is not
promoted. Actual trade counts, exposure, turnover and costs accompany every score.
Search ranks funded feasibility/CAGR with marginal contribution as a tie-break;
mutation preferentially replaces the weakest funded contributor and preserves
niche specialists plus an independent novelty challenger. It is a bounded
engineering pilot and does not establish an investment edge.

The fixed DEV79 cohort is not a verified PIT membership universe. Sector genes
and sector limits, earnings, named crash defense and recovery, SGOV, and SPY are
disabled because corresponding verified causal inputs are unavailable. Correlation
diversification remains active. Price features and independent native exits do
not require sector history. Stops evaluate -1% and exit at -2% on next open;
market gaps may exceed those triggers. T+2 settlement throughout is conservative.
Vendor OHLC and dividends are split normalized; no second split multiplier is
applied. Dividends are ex-date receivables that cannot be spent during the replay,
because payment dates are unavailable. Ambiguous split discontinuities stop the run. Corporate-action fidelity
still depends on the copied vendor data, and is explicitly reported as such.
