# Discrimination iteration3 — FAIL

Completed 48/48 paired portfolio replays in 380.7s. Tests passed before replays; see tests.log. No GA or production modifications.

Frozen train signals 0–77; independent calibration 80–121; embargo; holdout 126–249. Calibration never changes point estimates. Holdout never changes estimates, uncertainty, or posterior. Matured holdout contrast blocks feed only a permanent safety veto. These exact synthetic tapes were already viewed in iteration2: this is a regression experiment, not new confirmatory evidence.

Fit uses clipped cell date means, neighboring-cell partial pooling and five-date block standard errors. Calibration adds independent residual bias and sampling uncertainty. Economic boundaries remain −0.6%, −0.2%, +0.2%, +0.6%; the entire interval must fit a band and Gaussian conditional-mean posterior must exceed .95. UNKNOWN remains explicit. Gaussian block approximations assume independent/stable blocks; coverage is not distribution-free or certified with eight calibration blocks.

| Scenario | Evaluator | Coverage | Accuracy | False GREAT / TERRIBLE | Monotone seeds |
|---|---|---:|---:|---:|---:|
| learnable | iteration3 | 35.2% | 97.2% | 0/2375 | 0/4 |
| learnable | iteration2_repaired | 22.2% | 96.7% | 0/2375 | 1/4 |
| misleading | iteration3 | 35.2% | 97.2% | 0/2375 | 0/4 |
| misleading | iteration2_repaired | 22.2% | 96.7% | 0/2375 | 1/4 |
| null | iteration3 | 0.0% | n/a | 0/2375 | 0/4 |
| null | iteration2_repaired | 0.0% | n/a | 0/2375 | 0/4 |
| reversal | iteration3 | 2.1% | 0.0% | 102/2375 | 0/4 |
| reversal | iteration2_repaired | 18.8% | 93.8% | 23/2375 | 1/4 |

GOOD/AVERAGE/POOR support, every class precision/recall and realized net means are in tier_aggregate.csv and report.json. Full 5×5 matrices plus UNKNOWN are in confusion_aggregate_*_{ev,realized}.csv. Portfolio CAGR/MDD/exposure/costs and paired differences are in portfolio_runs.csv, portfolio_aggregate.csv and paired*.csv. Exact per-seed results remain in report.json.

Reversal lags: [7, 7, 7, 7]; iteration2: [17, 5, 7, 15]. Alarm counts are in summary.csv. A latch cannot anticipate inversion; it never relearns from holdout.

Stable synthetic sensor contains predictive information by construction; failure to certify middle bands with 78/42 dates and block uncertainty is finite-information limitation, not proof of no signal. Null lacks PIT association by construction. Reversal has no observable advance warning: before matured outcomes no causal detector can distinguish it. Real PIT predictive information remains untested; no real-market edge inferred.

Iteration2 diagnosis: short rolling windows and sparse per-cell independent dates inflate error; calibration pooled into mean invalidates independence; rolling residual vetoes and unadjusted repeated cell scans suppress coverage and produce nuisance alarms. Iteration3 separates those mechanisms but cannot manufacture missing information. Full shrinkage displacement and independent calibration uncertainty are retained instead of shrinking intervals merely to populate bins.

Robust all-seed pass gates are frozen in preregister.json. Portfolio returns cannot override discriminator failure. No real-market edge claim. Modeled candidate risk <=2%, T+1 and cash/cost contracts tested; realized losses are not guaranteed capped. No terminal liquidation; one-session outcome label does not certify multi-session portfolio EV.

Reproduce from repository root (requires original MTS checkout and sibling dependencies):
```bash
python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration3/experiment.py > /tmp/iteration3_execution.log 2>&1
```
Runner stops at test failure. It overwrites artifacts; archive first. finalize.py only aggregates saved results. Original native manager delegates quality to conditional_ev; the causal ledger enforces availability rather than estimating quality. Dependencies and source hashes are retained. Ledger archives contain all eligible opportunities, including unselected entries; scoring truth is added only by evaluator after forecasts.

Limitations:
- Synthetic regression tapes previously evaluated in iteration2: untouched means no fit/update with holdout outcomes in iteration3, not fresh confirmatory data.
- Five-date block independence and approximately Gaussian date-block means assumed; finite sample robust coverage is not guaranteed.
- Posterior is over conditional mean bands, not individual latent class; no oracle labels in fit.
- A shock before matured outcomes cannot be predicted by a safety alarm.
- Calibration uncertainty may honestly preclude middle tiers; no thresholds relaxed.
- Synthetic sensor information is injected; no real-market alpha claim.
- One-session net labels differ from multi-session portfolio holdings; no terminal liquidation.

Detailed saved-result audit and paired enrichment follow.

Stable synthetic sensor contains predictive information by construction; failure to certify middle bands with 78/42 dates and block uncertainty is finite-information limitation, not proof of no signal. Null lacks PIT association by construction. Reversal has no observable advance warning: before matured outcomes no causal detector can distinguish it. Real PIT predictive information remains untested; no real-market edge inferred. Stable middle radii .00236..00508 exceed .002 half-band: all middle support remains zero, so five-way monotonicity fails on every seed. Stable coverage rises by 13.03 percentage points through extreme classes only. Stable nuisance alarms decline from 15 to 1 across four seeds, but permanent latching sacrifices adaptation. At reversal, stronger frozen extreme assignments cause 102 false GREAT before the seven-session alarm versus23 online comparator; pre-alarm wrong assignments explain zero reversal conditional accuracy. This separates stationary finite-information limits from unavoidable delayed regime evidence; it does not establish that predictive information is universally absent.

| Scenario | Policy | Return | CAGR | MDD | Exposure | Fees | Other execution costs |
|---|---|---:|---:|---:|---:|---:|---:|
| learnable | iteration3 | 57.70% | 159.80% | 0.08% | 26.59% | 3596.26 | 7192.54 |
| learnable | iteration2_repaired | 29.45% | 71.06% | 0.11% | 15.47% | 1808.20 | 3616.43 |
| learnable | existing_ev10 | 65.81% | 174.98% | 0.19% | 45.22% | 4427.96 | 8855.90 |
| misleading | iteration3 | 57.70% | 159.80% | 0.08% | 26.59% | 3596.26 | 7192.54 |
| misleading | iteration2_repaired | 29.45% | 71.06% | 0.11% | 15.47% | 1808.20 | 3616.43 |
| misleading | existing_ev10 | -10.71% | -20.04% | 11.57% | 69.53% | 1813.23 | 3626.40 |
| null | iteration3 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00 | 0.00 |
| null | iteration2_repaired | 0.00% | 0.00% | 0.00% | 0.00% | 0.00 | 0.00 |
| null | existing_ev10 | 25.03% | 56.47% | 1.32% | 71.38% | 2019.14 | 4038.21 |
| reversal | iteration3 | -1.79% | -3.55% | 1.79% | 1.56% | 164.33 | 328.66 |
| reversal | iteration2_repaired | 24.90% | 57.07% | 0.68% | 14.74% | 1662.28 | 3324.58 |
| reversal | existing_ev10 | 73.51% | 201.06% | 0.50% | 72.26% | 2330.75 | 4661.45 |

All16 focused tests passed. Artifact audit verified96,000 identical ledger rows,16 identical iteration2 score records,48 replay archives,9,155 BUY fills, unchanged production sources, source hashes and comparator portfolio identity. CAGR annualizes126 sessions and is descriptive. No robust improvement claim.

After reproduction, run `audit_artifacts.py`, then `summarize.py`, then `audit_artifacts.py` in this directory to recreate reporting enrichment and final manifest. Neither script fits or replays.
