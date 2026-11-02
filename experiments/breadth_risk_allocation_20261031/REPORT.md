# GA6/GA7 fill-risk and allocation feasibility pilot

Executed 2026-11-01. **Historical strategy counterfactual BLOCKED; no GA justified.** Working narrower pilot reconstructs original fill-cycle risk and validates synthetic cash-executor behavior. No historical counterfactual NAV, CAGR, MDD, Calmar, exposure or fixed-rule portfolio uplift is available. No optimization or MTS trading-code change was made.

## Evidence and engine feasibility

Read the three completed predecessor REPORT.md files and their source code, selection and original ledgers. Fresh engine import failed before replay; see engine_probe.log. Exact chain: common cohort replay → StructuralCandidate → ga5_chromosome_contract → ga5_redesign.ga4_registry → pyarrow.read_schema(SOURCE). SOURCE is `/opt/mts/thunder-migration/mts-layered-run-20261007/Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet`; stat returns PermissionError. The runtime environment-status tool is unavailable in this session. No registry substitution, permission bypass or fabricated strategy decisions were used.

The accessible common execution reference was inspected: next-open orders, cash limits, priority competition, one-session sales settlement, dividends, overlapping holdings and modeled stops. test_study.py runs that executor with dynamic **synthetic toy rules**, altered sizing, overlapping A/B holdings and later C purchase after sale proceeds settle. It verifies nonnegative final cash, settlement, changed quantities and future-prefix invariance. This is executable plumbing evidence, not GA6/GA7 validation or evidence of breadth economics. Synthetic scale factors are not historical breadth observations. Reconstructing original decisions and matching unchanged baseline NAV/fills remains mandatory before real breadth-conditioned sizing or freed-capital comparisons.

## Risk reconstruction

All 10 selected unique original ledgers from the prior chronological selection were read; 3,074 closed episodes reconcile to source net PnL within 0.005 currency units, with exact cycle counts. 0 open cycles are explicitly excluded. Full 2009–2018 lifetimes are analyzed once per identity, avoiding duplicated fold rows. This includes earlier training years and already-inspected years, and is a selected-chromosome diagnostic, **not forward-fold evidence**. It does not reproduce the multihorizon identity sample's 270,109 GA6/GA7 trades.

Accounting uses each original BUY cost, SELL net proceeds, quantities, partial additions/reductions and pre-fill held-share dividends; split-adjusted bars follow the archived engine basis. Hypothetical liquidation marks charge the archive's 10-bp sell fee; acquisition costs already contain buy fees. Outcome denominator is total lifetime acquisition cost, including adds, so differs from archive R units. Adds/reductions/stops: GA6 3028/0/7; GA7 30/431/930.

There is **no actual intraday MAE**. `fill_marks` is the minimum fee-adjusted position PnL at recorded fill prices, an incomplete set of observations. `post_fill_low` reproduces daily lows only on shares remaining after daily fills plus fill marks; it can miss exit-day exposure. `exposed_state_low` marks every pre/post-fill held-share state at that session's low as a conservative OHLC scenario envelope. That envelope may put a modeled stopped holding below its assumed stop or put the low before a buy; it is not a certified attainable path or formal bound on actual intraday MAE. Stop prices themselves are archived model assumptions. `close_path` is the entry-close-to-exit-close minimum price-return comparator, without fill weighting. All outcomes include zero at inception. No real market execution certification follows from exact archived PnL reconciliation.

## Controlled association results

Each regression demeans within chromosome × entry year and standardizes the residual breadth predictor. Adjusted regressions include log(1+realized holding sessions), prior-close SPY 20-session annualized volatility and 63-session momentum. Duration is an ex-post explanatory sensitivity, never an online sizing input; it can mediate or induce selection effects. Each breadth horizon is tested separately; controls do not identify causal effects. Daily influence scores include zero-trade business days. Reported intervals use the largest SE from calendar-month clustering, Bartlett HAC63 and HAC126. Long cross-month dependence may remain. All 48 pooled tests (three inherited candidate features per system × four outcomes × adjusted/unadjusted) share BH and Bonferroni adjustment; annual results are descriptive and unadjusted. This is a focused post-selection family, not a correction for all previous research.

| System / feature | Risk measure | N | Effect (pp) | conservative 95% interval (pp) | BH q |
|---|---|---:|---:|---|---:|
| GA6 d50_21 | close_path | 1636 | -0.9910 | [-1.6575, -0.3246] | 0.0269 |
| GA6 d50_21 | fill_marks | 1636 | -0.8382 | [-1.4677, -0.2087] | 0.0395 |
| GA6 d50_21 | post_fill_low | 1636 | -0.7532 | [-1.3695, -0.1368] | 0.0613 |
| GA6 d50_21 | exposed_state_low | 1636 | -0.7853 | [-1.4595, -0.1111] | 0.0769 |
| GA7 b50 | close_path | 1438 | -0.0178 | [-0.1257, 0.0902] | 0.8129 |
| GA7 b50 | fill_marks | 1438 | -0.0564 | [-0.1287, 0.0158] | 0.2155 |
| GA7 b50 | post_fill_low | 1438 | -0.0386 | [-0.0919, 0.0146] | 0.2481 |
| GA7 b50 | exposed_state_low | 1438 | -0.0186 | [-0.1872, 0.1501] | 0.8467 |

Effects are percentage points per within-chromosome/year SD of breadth feature. GA7 b50 adjusted SD is 17.83 breadth points; GA6 d50_21 is 27.03 change points. GA7's negative direction persists descriptively but is uncertain, including for the close-path comparator in this smaller selected sample. GA6 retains negative adjusted direction in every risk definition; fill marks pass BH, but both daily-low measures do not. Thus the pilot does not establish persistence under actual intraday risk, or a robust daily-OHLC discovery. `annual.csv` exports same-year diagnostics; sparse cells and correlated chromosomes limit replication.

## Decision and reproducibility

Stop at NO-GA. Accessible evidence supplies neither a validated cash-constrained strategy counterfactual nor repeatable forward-fold net economic benefit. The original baseline, fixed b50 <= 0.5 gate and breadth-conditioned sizing cannot be compared as portfolios until the original engine dependency is available and unchanged replay reconciles. Deleting historical fills, scaling archived PnL, or using original NAV for filtered portfolios would fail that requirement. No such metrics are emitted.

Run from repository root:

```sh
OPENBLAS_NUM_THREADS=1 /opt/mts/.venv/bin/python experiments/breadth_risk_allocation_20261031/study.py
/opt/mts/.venv/bin/python -m unittest discover -s experiments/breadth_risk_allocation_20261031 -p 'test_*.py' -v
/opt/mts/.venv/bin/python experiments/breadth_risk_allocation_20261031/report.py
```

Four tests pass (tests.log). Full risk outputs: risk_episodes.csv.gz, ledger_audit.csv, associations.csv, annual.csv. metadata.json hashes consumed market data, features, selection, ledgers and study code. Daily breadth is inherited prior-close DEV79 breadth; feature timestamps are asserted strictly before entries. Fixed retrospective membership and current-vintage price revisions, archived winner discovery, selected identities, ten years, overlapping stocks and proxy stop execution limit interpretation. All newly written artifacts stay in this research directory.
