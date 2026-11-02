# Discrimination iteration2 — FAIL

Completed 48/48 paired full replays in 408.0s, after all12 unit tests passed. No GA or production changes. No thresholds changed after evaluation.

No overall improvement or reliable five-way claim. Synthetic injected sensor bundle is more informative by construction; it is not measured real alpha. Primary online estimator pools recent calibration observations into its mean, so it does not meet independent calibration certification. The separately reported static ablation uses disjoint chronological train0–77/cal80–121/holdout126–249, with no holdout refitting.

Decision boundary bands are TERRIBLE <−0.6%, POOR [−0.6%,−0.2%), AVERAGE [−0.2%,0.2%), GOOD [0.2%,0.6%), GREAT ≥0.6%. UNKNOWN remains explicit. Conditional mean bands do not guarantee the individual hidden latent class.

| Scenario | Evaluator | Coverage | Accuracy | False GREAT / true TERRIBLE | Monotone seeds |
|---|---|---:|---:|---:|---:|
| learnable | iteration2 | 22.2% | 96.7% | 0/2375 | 1/4 |
| learnable | previous_repaired | 14.7% | 86.3% | 37/2375 | 0/4 |
| misleading | iteration2 | 22.2% | 96.7% | 0/2375 | 1/4 |
| misleading | previous_repaired | 14.7% | 86.3% | 37/2375 | 0/4 |
| null | iteration2 | 0.0% | n/a | 0/2375 | 0/4 |
| null | previous_repaired | 0.0% | n/a | 0/2375 | 0/4 |
| reversal | iteration2 | 18.8% | 93.8% | 23/2375 | 1/4 |
| reversal | previous_repaired | 8.9% | 83.3% | 39/2375 | 0/4 |

Reversal lag (first post126 alarm minus126): [17, 5, 7, 15]; previous repaired: [8, 9, 7, 11]. Repeated/nuisance alarm counts are in summary.csv. Stronger measurements can increase damage before an unannounced reversal is observed; inspect false-GREAT protection separately from stable coverage.

Prior diagnosis: no tier-dispatch bug or overlapping thresholds. The prior80% coarse sensor mixes states; the narrow0.4-percentage-point middle bands, at most21 recent independent date clusters, and train/calibration discrepancy produce intervals crossing boundaries. Global gates further suppress coverage. Exact counts and descriptive realized cell means are in report.json diagnosis; these are overlapping diagnostics, not causal ablation estimates.

| Scenario | Policy | Mean return | Mean MDD | Worst MDD |
|---|---|---:|---:|---:|
| learnable | iteration2 | 29.45% | 0.11% | 0.15% |
| learnable | previous_repaired | 26.85% | 0.21% | 0.37% |
| learnable | existing_ev10 | 65.81% | 0.19% | 0.26% |
| misleading | iteration2 | 29.45% | 0.11% | 0.15% |
| misleading | previous_repaired | 26.85% | 0.21% | 0.37% |
| misleading | existing_ev10 | -10.71% | 11.57% | 18.34% |
| null | iteration2 | 0.00% | 0.00% | 0.00% |
| null | previous_repaired | 0.00% | 0.00% | 0.00% |
| null | existing_ev10 | 25.03% | 1.32% | 1.46% |
| reversal | iteration2 | 24.90% | 0.68% | 2.46% |
| reversal | previous_repaired | 16.51% | 0.48% | 1.03% |
| reversal | existing_ev10 | 73.51% | 0.50% | 0.59% |

Independent full post-BUY risk reconstruction: 8830 BUYs, maximum modeled entire-candidate loss 0.02000000 <=0.02. T+1 tested. No scale-up or terminal liquidation. Risk is modeled, not a realized-loss guarantee.

tier_aggregate.csv reports per-tier precision, coverage and forward realized net return. Confusion CSVs provide5×5 plus UNKNOWN, for latent EV and individual realized tiers. paired.csv and paired_aggregate.csv report matched return/MDD deltas against both comparators. Abstention costs are signed forgone net sum, positive realized sum and positive evaluator-EV sum per opportunity; these ex-post quantities ignore cash conflicts and are not attainable portfolio returns.

Reproduce from repository root (requires the original MTS checkout and sibling dependencies):
```bash
python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/experiment.py > /tmp/discrimination_iteration2_execution.log 2>&1
python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/finalize.py
python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/audit_artifacts.py
```
Runner stops on any failed test. It overwrites outputs; archive this directory before reproduction. preregister.json is frozen and its execution hash is in report.json. source_checksums.json covers reviewed/executed sources, local corrected manager/kernel and patch are preserved, all6000 eligible outcome events per tape are in ledger archives, held-out scoring records in opportunities.jsonl.gz, actual executions in replays.jsonl.gz. run.log is the external task transcript; execution.log summarizes the test/replay timing and budget.

Missing data and limitations:
- Real PIT sensor time series with release timestamps, revision history, missingness, and measured noise covariance; injected Gaussian quality has no empirical realism validation.
- Longer independent matured stable-regime dates for narrow middle economic bands; independent calibration episodes and more forward seeds/regimes.
- Observable change predictors available before entry, or more rapid genuinely matured horizon outcomes to protect inversion before alarms.
- A holding-horizon-specific net-return label and causal selection-aware portfolio counterfactual for attainable abstention cost.
- Injected synthetic sensor quality is assumed, not calibrated to any real measurement; no real alpha claim.
- Conditional mean uncertainty is not individual latent-state certainty; neighboring classes overlap even with narrow intervals.
- Diagnostic SE intervals have no formal simultaneous or serial dependence coverage guarantee.
- Unannounced inversion cannot be detected before strictly matured outcomes; pre-alarm false GREAT unavoidable.
- Rolling online holdout ingests only matured realized returns, never evaluator truth; not a static untouched outcome fit.
- Four paired seeds,126 sessions; no statistical robustness claim.
- One-session DGP grosses up costs; multi-session portfolio holdings pay costs less often, null profits are not recognition.
- Abstention opportunity costs are ex-post sums per opportunity, not attainable portfolio returns.
- No terminal liquidation; modeled2% risk is not a realized-loss guarantee.
- Primary pooled estimator uses its recent calibration window in the point estimate. That window is a drift/stability diagnostic, not independent calibration. Independent static train0..77/cal80..121 ablation is reported separately and was reserved before execution.
- Primary initial rolling split is33..92 older,93..123 recent, as explicitly stated before execution; it does not use nominal static ranges.
- Static ablation radius formula is inherited unchanged from primary method, but static ablation has no rolling drift adaptation or residual gate and no portfolio replay; cannot certify the complete online bundle.

Additional artifact interpretation:

- Independent static ablation reaches55.3% stable coverage but fails every seed and causes2336 false GREAT at inversion; static mean confidence cannot certify temporal validity.
- Online stable scenarios emit only5 GOOD predictions each across four seeds; populated aggregate tiers are not reliable five-way identification.
- Stable tapes produce2..6 nuisance alarms per seed; quarantine and post-reset warmup remove large fractions of coverage. Detector scans five cells repeatedly without multiplicity calibration; nominal3SE comparisons do not control a sequential false-alarm rate.
- All online holdout decisions:13920 quarantine,9405 insufficient matured dates,7549 boundary uncertainty,9192 absent signal,32 residual-bias veto,7518 confident. These mutually exclusive prioritized reasons are not causal effect estimates.
- Future work requires independent sequential false-alarm calibration and better time-stamped change predictors. No post-holdout detector tuning was performed.
- Earlier radius attribution is descriptive of the repaired prior estimator:33812 middle-centered UNKNOWN intervals all have radius>=.002. Narrowing economic bands or counting stocks as independent would not be a valid fix.
