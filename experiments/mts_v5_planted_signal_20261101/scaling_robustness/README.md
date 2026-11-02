# Scaling robustness — completed

Completed all 72 primary comparisons: weak and confidently miscalibrated null signals, 10/15/20% caps, seeds 1101–1112, 252 sessions. Also completed 22 hypothetical reliability-gate controls on seeds 1101–1111. Synthetic diagnostic only; no historical-alpha or production calibration claim.

All 10 tests passed before portfolio execution. `test_reliability.py` is now beside the runner; its resolved path and import were checked. `run_tests.py` resolves paths from its own location, so it works from any working directory. Tests cover standalone cost-inclusive loss clipping, other holdings not consuming the candidate budget, cash reservation/release, T+1, MDD exits, reliability warmup and exclusion of current/future outcomes. See `resume_tests.log`.

Budget: 28 prior attempts conservatively counted (26 saved, one result-assembly failure, up to one interrupted run), 68 new attempts, 96 total upper bound. Reused 26 records; no additional attempts are available. Portfolio resume elapsed 42.2 seconds. No GA or production changes.

| Signal | Gate | Cap | Seeds | Mean CAGR | Mean MDD | Mean Calmar | Exposure | Turnover | Above-10% adds | Full target fills | Worst CAGR | Worst MDD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| misnull | existing | 10% | 12 | 6.13% | 7.75% | 1.411 | 78.07% | 34.03 | 0 | 0 | -6.33% | 13.43% |
| misnull | existing | 15% | 12 | 7.50% | 8.61% | 1.670 | 81.45% | 33.85 | 625 | 457 | -10.25% | 16.57% |
| misnull | existing | 20% | 12 | 8.68% | 8.57% | 1.889 | 81.64% | 33.88 | 632 | 108 | -9.14% | 16.95% |
| misnull | hypothetical | 15% | 11 | 7.03% | 7.24% | 1.565 | 78.26% | 33.73 | 0 | 0 | -6.33% | 10.96% |
| misnull | hypothetical | 20% | 11 | 7.03% | 7.24% | 1.565 | 78.26% | 33.73 | 0 | 0 | -6.33% | 10.96% |
| weak | existing | 10% | 12 | 20.98% | 3.93% | 6.171 | 58.19% | 8.32 | 0 | 0 | 5.74% | 7.08% |
| weak | existing | 15% | 12 | 21.45% | 4.02% | 6.238 | 59.24% | 8.49 | 46 | 44 | 5.81% | 7.71% |
| weak | existing | 20% | 12 | 21.45% | 4.02% | 6.238 | 59.24% | 8.49 | 46 | 0 | 5.81% | 7.71% |

Turnover is total traded notional divided by daily NAV, summed over the 252-session run. Fill counts are sums across seeds; performance columns are seed means. Full target counts apply to incumbent scaling adds only; 10% entry fills are not counted as scaling.

| Signal | Gate | Comparison | Mean CAGR delta (pp) | Mean MDD delta (pp) | Mean Calmar delta | CAGR wins | CAGR delta range (pp) |
|---|---|---|---:|---:|---:|---:|---:|
| misnull | existing | 15% vs 10% | 1.370 | 0.854 | 0.260 | 8/12 | -8.308 to 7.230 |
| misnull | existing | 20% vs 10% | 2.549 | 0.813 | 0.478 | 8/12 | -8.308 to 11.927 |
| misnull | hypothetical | 15% vs 10% | 0.000 | 0.000 | 0.000 | 0/11 | 0.000 to 0.000 |
| misnull | hypothetical | 20% vs 10% | 0.000 | 0.000 | 0.000 | 0/11 | 0.000 to 0.000 |
| weak | existing | 15% vs 10% | 0.475 | 0.085 | 0.066 | 8/12 | -0.471 to 1.758 |
| weak | existing | 20% vs 10% | 0.474 | 0.085 | 0.066 | 8/12 | -0.471 to 1.758 |
| weak | existing | 20% vs 15% | -0.000 | 0.000 | -0.000 | 0/12 | -0.002 to 0.000 |
| misnull | existing | 20% vs 15% | 1.180 | -0.041 | 0.219 | 8/12 | -3.556 to 6.645 |

Every comparison uses the same verified tape, costs, callback logic, T+1 rules, exits and 20% MDD admission latch. Existing evidence pools funded exits; its realized inputs depend on portfolio fills, so identical causal evidence logic does not imply identical realized evidence across caps. There is no independent predictive calibration claim.

The hypothetical gate additionally requires 30 matured forecast dates, positive average observed net return, and nonnegative mean forecast error plus two standard errors. Forecast k executes k+1 and matures k+2; only outcomes strictly before the current close are read. Date averages avoid counting correlated stocks as independent. The two-SE margin is an unvalidated diagnostic under serial dependence. These controls are separately labeled and use 11 seeds, compared with their same-seed existing 10% baselines.

Each actual BUY independently satisfies full post-add candidate weight × (max(2% stop, candidate gap) + round-trip cost) ≤2%. Other holdings do not consume this trade budget. Maximum checked candidate loss: 0.02000000; maximum NAV/cash/quantity reconciliation error: 2.91e-10. Risk/cap/cash rejection flags overlap: `runs` stores unique rejection unions and exact overlap counts, so marginal counts must not be added.

Actual above-10% adds require an incumbent BUY with resulting opening weight above 10.001%; passive drift is excluded. Full targets require opening weight at least requested target minus 1e-9. `report.json` contains every run, paired per-seed changes, rejection counts, tails, latch seeds and fill counts.

The prior archive SHA-256 and generating runner, manager, kernel and patch hashes matched `prior_manifest.json`. Its gzip trailer was truncated at interruption. Only 26 complete JSON records were recovered; their individual hashes and run identities are in `replay_verification`. All were revalidated through 252-session ledger/cost/T+1/NAV/risk and scaling-fill reconstruction. Incomplete trailing content was discarded. `completed_replays.jsonl.gz` is a complete, readable 94-record archive. Pending orders were absent from the old archive and are omitted from comparison metrics.

`source.patch` reconstructs both corrected experiment modules byte-for-byte from the Stage2_fix manager and original production kernel (`reconstruction.log`). Source paths and SHA-256 values are recorded and rechecked in `report.json`. The patch is incremental to Stage2_fix; its prior manager fixes are required. No original production source was changed.

Artifacts: `experiment.py` retains the checksummed prior generating source; `resume_experiment.py` performs the bounded resume and persists its attempt ledger before each run; `finalize_report.py` adds report-only summaries; `prior_report.json` and prior error logs preserve the failure history. `manifest.json` hashes final artifacts.
