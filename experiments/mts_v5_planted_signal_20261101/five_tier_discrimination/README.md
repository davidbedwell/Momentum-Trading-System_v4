# Five-tier opportunity discrimination — FAIL

Completed 64 full portfolio replays; eight focused tests passed first. Replay experiment took 182.2 seconds. No GA; production source hashes unchanged.

Preregistered before tests/replays: `preregister.json`. Fixed train signals 0–77, calibration 80–121, untouched evaluation 126–249, portfolio sessions 126–251. Forecast k executes k+1 and matures k+2; fit requires maturity strictly before cutoff. No thresholds, features, or policies were chosen using evaluation outcomes. A cell receives a tier only when its full frozen uncertainty interval lies within one absolute net-return band. Otherwise it is UNKNOWN.

Absolute one-session net bands: TERRIBLE <−0.6%; POOR [−0.6%,−0.2%); AVERAGE [−0.2%,0.2%); GOOD [0.2%,0.6%); GREAT ≥0.6%. These are economic bands, not quantiles.

| Scenario | Coverage | Conditional EV-tier accuracy | Unknown | False GREAT / true TERRIBLE | Populated tiers |
|---|---:|---:|---:|---:|---|
| learnable | 24.7% | 83.3% | 8960 | 47/2394 | TERRIBLE, GREAT |
| misleading | 24.7% | 83.3% | 8960 | 47/2394 | TERRIBLE, GREAT |
| null | 0.0% | n/a | 11904 | 0/2433 | none |
| reversal | 25.0% | 4.3% | 8925 | 989/2394 | TERRIBLE, GREAT |

The preregistered robust five-way claim FAILS. See `failure_specifics` and per-seed recall in `report.json`. Missing middle tiers remain unpopulated; null abstention is a useful safety result but provides no five-way identification. Regime reversal tests out-of-distribution failure; no confidence interval trained only before the reversal can guarantee its detection.

Synthetic truth: latent classes set distinct conditional expected executable net returns; their class and mean are evaluator-only. Each realized forward return includes common-date and individual shocks. The learner sees only noisy point-in-time measurements, training outcomes and calibration outcomes; it never receives a known forecast-strength coefficient or true tier. Learnable/misleading measurements are artificially informative, so even success there would not establish native MTS quality recognition. Misleading predicted EV reverses the observable relationship; null forecasts/features have no latent-class information. EV-tier confusion and individual realized-return-tier confusion are reported separately.

Every confusion CSV contains the required 5×5 matrix plus a separate UNKNOWN column. Rows are true tiers; columns are inferred tiers. `opportunities.jsonl.gz` preserves every held-out observation and prediction. Calibration bias, RMSE, regression slope/intercept and rank correlations are in the report, as are per-tier counts, realized net means, monotonicity, GREAT precision and terrible-to-GREAT mistakes. Date grouping reduces cross-sectional pseudo-replication; two-sided 2.58-SE intervals are diagnostic and lack formal serial-dependence or simultaneous coverage guarantees.

Portfolio comparison uses the existing MTS EV admission and ranked cash queue at 10%, plus tier10 and conditional tier15/tier20. Proposals use harmonized positive/negative signal ENTER/HOLD/EXIT logic, not the prior generator’s exact incumbent switching rule. Tier policies admit GOOD/GREAT only and request scaling only for GREAT incumbents. Scaling still requires native funded mature-trade/fold/profitability evidence. All policies use the same tape, costs, 2% entire-candidate modeled risk, T+1, MDD latch and cash reservation. No fabricated scale fills. Each replay has an independent ledger/cash/NAV reconstruction; finalization independently checks every actual BUY’s entire candidate risk. No terminal liquidation; pending positions remain marked.

| Scenario | Policy | Mean total return | Mean MDD | Turnover | Scaled fills (mean) |
|---|---|---:|---:|---:|---:|
| learnable | existing_ev10 | 65.47% | 0.27% | 67.82 | 0.0 |
| learnable | tier10 | 27.43% | 0.10% | 34.42 | 0.0 |
| learnable | tier15 | 27.61% | 0.10% | 34.55 | 4.5 |
| learnable | tier20 | 27.58% | 0.10% | 34.60 | 4.8 |
| misleading | existing_ev10 | -9.42% | 9.84% | 35.02 | 0.0 |
| misleading | tier10 | 27.43% | 0.10% | 34.42 | 0.0 |
| misleading | tier15 | 27.61% | 0.10% | 34.55 | 4.5 |
| misleading | tier20 | 27.58% | 0.10% | 34.60 | 4.8 |
| null | existing_ev10 | 21.95% | 1.57% | 36.28 | 0.0 |
| null | tier10 | 0.00% | 0.00% | 0.00 | 0.0 |
| null | tier15 | 0.00% | 0.00% | 0.00 | 0.0 |
| null | tier20 | 0.00% | 0.00% | 0.00 | 0.0 |
| reversal | existing_ev10 | 66.11% | 0.41% | 37.29 | 0.0 |
| reversal | tier10 | -10.06% | 10.08% | 19.88 | 0.0 |
| reversal | tier15 | -10.06% | 10.08% | 19.88 | 0.0 |
| reversal | tier20 | -10.06% | 10.08% | 19.88 | 0.0 |

Portfolio gains do not establish quality recognition. The DGP grosses up one-session net EV by round-trip costs; holdings spanning multiple signals pay costs less frequently, so even the null EV baseline earns positive drift. This horizon mismatch is a material limitation, not recognition evidence. Returns exploit artificial observable relationships and are separate from the five-way decision criteria. Four seeds and 126 portfolio sessions are insufficient for production robustness. Costs, tail MDD, per-seed paired comparisons against both EV10 and tier10, and actual scaling fills are saved in JSON/CSV.

Minimum engineering change: Add a horizon-specific causal outcome ledger for all eligible opportunities, date-clustered calibrated absolute net-EV intervals and explicit abstention at the manager admission seam; independently validate native PIT features across forward regimes before enabling five-tier claims or tier scaling.

Reproduce from this repository with the original `/opt/Momentum-Trading-System_v5-alpha` checkout available:
```bash
python3 experiments/mts_v5_planted_signal_20261101/five_tier_discrimination/experiment.py
python3 experiments/mts_v5_planted_signal_20261101/five_tier_discrimination/finalize.py
```
The runner always executes focused tests first and stops on any failure. It overwrites this experiment’s outputs. Dependencies and original source paths/hashes are in report.json. `source.patch` is the inherited manager/kernel correction relative to stage2_fix manager and original kernel; corrected copies are included. `experiment.patch` reconstructs the experiment sources. No original production files are patched. `manifest.json` hashes all final artifacts except itself and the still-active harness run.log. Logs preserve test and execution evidence.
