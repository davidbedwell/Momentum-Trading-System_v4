# Opportunity evaluator fix — FAIL

Execution COMPLETE: 64/64 portfolio replays, 14 tests passed first; 212.0 seconds. No production changes or GA.

The causal all-opportunity ledger and rolling calibration are implemented. The robust five-way claim fails unless every preregistered scenario/seed passes; abstention is retained. No quality gates were relaxed after evaluation.

Parameters were frozen in preregister.json before tests/replays. Predictions use only PIT measurement cells and outcomes strictly matured before each decision. All 250 × 24 eligible opportunities per tape are logged, including untraded opportunities; pending final outcomes are explicit. No oracle regimes or true EV enters inference. Evaluation truth appears only in discrimination scoring.

Calibration: older 40 and up to 21 recent signal dates in a rolling 61-date matured window (inclusive source boundaries), diagnostic 2.58-SE intervals plus window bias. Recent 9 versus older 30+ dates monitors cell drift; alarms quarantine all tiers for 20 clocks. No identifiable cross-cell signal yields UNKNOWN, not AVERAGE. Outcome fifth-percentile risk gates and absolute bands are frozen in preregister.json. No formal confidence-coverage guarantee under dependence.

Protocol metadata discrepancy: the inherited static-fit fields in preregister.json were superseded by its version 2 rolling method. Nominal window counts say 40/20/8, while the frozen inclusive code implements 40/21/9. No parameters or code were changed after evaluation. This documentation discrepancy also prevents a clean preregistration PASS.

Absolute one-session net bands: TERRIBLE < -0.6%; POOR [-0.6%,-0.2%); AVERAGE [-0.2%,0.2%); GOOD [0.2%,0.6%); GREAT >=0.6%. The full uncertainty interval must fit one band.

| Scenario | Old coverage | New coverage | New accuracy | Old false GREAT | New false GREAT | Detection delays |
|---|---:|---:|---:|---:|---:|---|
| learnable | 24.7% | 11.7% | 82.8% | 47 | 21 | [None, None, None, None] |
| misleading | 24.7% | 11.7% | 82.8% | 47 | 21 | [None, None, None, None] |
| null | 0.0% | 0.0% | n/a | 0 | 0 | [None, None, None, None] |
| reversal | 25.0% | 7.6% | 78.9% | 989 | 22 | [20, 7, 8, 7] |

Drift delay is first post-126 alarm minus 126, in sessions, scored externally using the known reversal onset. Other scenarios have no true change, so alarm counts measure nuisance alarms. Alarm events and counts are in report.json.

Ledger and rolling estimator implemented locally; reliable five-way inference still requires stronger PIT features distinguishing neighboring EV bands, more independent matured dates within stable regimes, and timely observable regime-change predictors. Null has no identifying signal by design.

| Scenario | Policy | Mean return | Mean MDD | Worst MDD |
|---|---|---:|---:|---:|
| learnable | existing_ev10 | 65.47% | 0.27% | 0.35% |
| learnable | tier10 | 8.20% | 0.09% | 0.14% |
| learnable | tier15 | 8.27% | 0.09% | 0.14% |
| learnable | tier20 | 8.27% | 0.09% | 0.14% |
| misleading | existing_ev10 | -9.42% | 9.84% | 12.14% |
| misleading | tier10 | 8.20% | 0.09% | 0.14% |
| misleading | tier15 | 8.27% | 0.09% | 0.14% |
| misleading | tier20 | 8.27% | 0.09% | 0.14% |
| null | existing_ev10 | 21.95% | 1.57% | 2.36% |
| null | tier10 | 0.00% | 0.00% | 0.00% |
| null | tier15 | 0.00% | 0.00% | 0.00% |
| null | tier20 | 0.00% | 0.00% | 0.00% |
| reversal | existing_ev10 | 66.11% | 0.41% | 0.47% |
| reversal | tier10 | 5.01% | 0.49% | 1.77% |
| reversal | tier15 | 5.04% | 0.49% | 1.77% |
| reversal | tier20 | 5.04% | 0.49% | 1.77% |

Same paired seeds, tapes, horizons, baseline and native manager/kernel as the prior five-tier run. Tier10/15/20 admit GOOD/GREAT; above-10% adds still need actual funded native evidence. Independent entire-candidate risk <=2%, costs, T+1, cash reservations, exits and MDD latch are preserved and checked. No terminal liquidation.

The synthetic one-session outcome grosses up transaction costs. Multi-session holdings pay less frequent costs, so null portfolio profits do not imply recognition. Four seeds and 126 portfolio sessions cannot establish statistical tail robustness. Portfolio comparisons and costs are in portfolio_runs.csv, portfolio_aggregate.csv, paired.csv and portfolio_previous.csv. Both latent-EV and realized-return confusion matrices include UNKNOWN separately.

Reproduce from repository root with the original MTS checkout and sibling experiment dependencies available:
```bash
python3 experiments/mts_v5_planted_signal_20261101/opportunity_evaluator_fix/experiment.py
python3 experiments/mts_v5_planted_signal_20261101/opportunity_evaluator_fix/finalize.py
```
The runner always runs tests first and stops on failures. It overwrites its outputs; parameters and method remain fixed. All eligible PIT records, costs, context, timestamps, missingness and outcomes are in opportunities.jsonl.gz; execution ledgers are in replays.jsonl.gz. Source checksums and inherited manager/kernel copies are saved. manifest.json excludes itself and active run.log/finalize.log.
