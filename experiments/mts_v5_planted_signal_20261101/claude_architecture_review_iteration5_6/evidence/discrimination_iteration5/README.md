# Iteration5: FAIL — bounded engineering experiment

Nine unit/integration tests passed twice. Total62 portfolio replays:6 test probes,52 planned runs,4 post-freeze control corrections. Measured compute 30.05s, below720s. No GA or production edits; every new file is in this directory. Existing unrelated workspace changes were left alone.

The gate repair restores stable coverage; it does not certify the bundle. Original bands remain ±0.2%/±0.6%. All three middle radii are below0.002 on4/4 learnable seeds, yet only2/4 seeds support every tier. Radius alone is insufficient when a fitted center approaches a boundary. No widened bands or forced classes were used.

Stable learnable coverage ranges 79.8%–100.0%; conditional individual-latent tier accuracy 95.2%–96.6%. Stable false GREAT/TERRIBLE count0. Conditional cell-mean interval coverage20/20 learnable cells, and20/20 outer-noise cells; this small synthetic sample establishes no nominal coverage guarantee.

Reversal: 442 true-TERRIBLE opportunities labeled GREAT before the22-session return-drift latch on every seed. Mean candidate reversal return -10.31%. Zero stable alarms across12 seed/scenario units, but only4 independent seeds; even0/4 gives a52.7% one-sided95% upper bound on seed alarm probability. Reported0/12 upper bound is descriptive and assumes independence that paired scenarios do not have.

## Measured portfolio results

Arithmetic means of per-seed metrics. Dollar costs on initial$100,000; all entry/exit costs paid, one-session horizon, T+1 sale proceeds, terminal liquidation. These large injected-signal returns are not real alpha.

| Scenario / policy | Return | CAGR | MDD | Costs |
|---|---:|---:|---:|---:|
| learnable / candidate | 86.66% | 248.45% | 0.23% | $26,159 |
| learnable / iteration2 | 32.23% | 77.05% | 0.09% | $8,373 |
| learnable / scaled | 90.99% | 264.90% | 0.38% | $26,425 |
| null / candidate | 0.00% | 0.00% | 0.00% | $0 |
| null / iteration2 | 0.00% | 0.00% | 0.00% | $0 |
| reversal / candidate | -10.31% | -19.55% | 10.31% | $3,104 |
| reversal / iteration2 | 20.81% | 47.43% | 1.58% | $6,706 |
| outer_noise / candidate | 84.28% | 239.67% | 0.36% | $23,521 |
| outer_noise / iteration2 | 27.15% | 64.11% | 0.13% | $6,749 |
| learnable / corrected equal universe | 0.34% | 0.72% | 2.53% | $18,969 |

Original benchmark rows are INVALID independent controls: purchase ranking used forecasts under cash scarcity. The corrected equal-notional control accepts prices only and checks equal entries across all24 names. It ran on four already viewed learnable tapes, consuming four spare replay slots; other scenarios remain incomplete. Corrected comparisons are descriptive after evaluation. Cash control is0 return/CAGR/MDD/cost; real SGOV comparison is unavailable.

Maximum measured per-trade modeled risk 1.9970%; no gap-loss exceedances in the primary replays. An explicit50% gap test demonstrates realized losses can exceed modeled risk. Funded candidate/baseline ledger net reconciliation error 4.4e-16; no horizon mismatch. Tier metrics cover all opportunities, including unfunded and abstentions; these sums are not attainable portfolio returns.

## Method and evidence

Read the full external review and original experiment code; all original reports were parsed. 734 synthetic sessions,24 assets, random class/sensor draws with original sensor noise and original noise law. Outer variant increases return noise25%. Fit signals0–399, calibration403–602, test606–731. Outcomes are usable at signal+3; fit/cal/test execution intervals are disjoint. Each date-cell mean counts once; under this iid-date DGP dates are independent. Cross-cell dependence remains and is covered by union bounds. More complex serial dependence is not validated.

Sensor-cell date means and full-model lag-price slopes fit only training data. The99th percentile disagreement threshold and identifiability filter use training only. Independent calibration widens uncertainty through bias and SE, never changes coefficients. Approximate cell intervals use2.576SE with no individual-class guarantee. The monitor uses a conservative0.018 subGaussian envelope for the prescribed synthetic law, five cells and at most26 looks, with total alpha0.05. This envelope is not a learned real-market guarantee.

Iteration2 predict is imported unchanged on the last126 warmup+126 test sessions of the same fresh tapes. Bar conversion preserves exact net returns under its inherited multiplicative costs. Its calibration pooling violation is retained and explicitly uncertified. Candidate has a longer fit, so this is a paired engineering comparison, not a pure gate-only ablation. The full-model ungated ablation isolates the gate on the candidate fit. Scaled15% allocations are learnable-only; see paired.csv for incremental returns/MDD/costs.

Confusion matrices for individual latent and realized tiers, all-opportunity recalls, GREAT→TERRIBLE and TERRIBLE→GREAT, per-cell diagnostics, conditional mean interval coverage, drift reasons/lags, and seed-level metrics are in report.json. tier_metrics.csv holds support and net returns; ledger_audit.csv includes daily rank IC and realized loss sums for false GREAT. opportunities.jsonl.gz includes every test opportunity, actual funded flags/debits and open-to-exit outcomes; replays.jsonl.gz contains funded trades and daily cash/NAV.

preregister.json and core Python SHA256 hashes were committed locally before seeds.json was drawn from OS entropy. No trusted external/public timestamp or hardware RNG attestation exists. Fresh-seed tapes were untouched at generation; they are now viewed. The inherited DGP and developer choices were informed by earlier work. No untouched test remains, and the benchmark correction is explicitly post-freeze. Original core hashes still match commitment.json. No outcome-based tuning or reruns of the candidate occurred.

PIT readiness: local policy/manifest and provisional CSV headers show no complete release/revision/vintage provenance. No real rows were admitted or fabricated. pit_schema.json and validate_pit provide a strict row adapter, not source authenticity or statistical certification. Real OOS IC>0.1 cannot be assessed.

## Recommendations implemented versus blocked

- **P1_gate:** IMPLEMENTED sensor/full disagreement; no price-only veto, train-only threshold; stable coverage recovers.
- **P2_independent_dates:** IMPLEMENTED 734 sessions,400 fit/200 cal dates, original bands. Radii pass but per-seed five-tier support fails.
- **P3_outer_holdout:** PARTIAL four OS entropy seeds after local hash commitment, separate noise variant; trusted public timestamp unavailable. All evaluated tapes now viewed.
- **P4_disjoint_calibration:** IMPLEMENTED embargoed chronological disjoint ranges; mutation tests show calibration cannot alter point coefficients. Statistical correlation need not literally be zero in finite samples.
- **P5_sequential_monitor:** IMPLEMENTED cell/look union bound with stated DGP subGaussian envelope; stable0/12 but only4 independent seeds. Reversal22-session lag is unsafe.
- **P6_horizon_ledger:** IMPLEMENTED all-opportunity one-session open-to-exit ledger, matched funded horizons, costs/cash/final liquidation/risk/gap audits. Original variable holding manager not replayed; synthetic one-session harness only.
- **P7_real_PIT:** ADAPTER/AUDIT ONLY; no accepted real rows or real OOS IC. Local provisional artifacts lack complete revision/release provenance. NO alpha claim.

## Run and inspect

```bash
PYTHONPATH=/opt/Momentum-Trading-System_v5-alpha python3 -m unittest discover -s experiments/mts_v5_planted_signal_20261101/discrimination_iteration5 -p "test_*.py" -v
```

Tests are rerunnable but execute three synthetic portfolio probes per invocation. The archived accounting includes exactly two test invocations; no more runs are scheduled. experiment.py refuses holdout reuse while commitment.json exists. Its archived frozen runner preserves the original benchmark bug for audit; use corrected_benchmark.replay_equal for a valid price-only equal-universe control. A future full experiment needs a new directory/protocol/commitment and its own replay budget; do not delete this commitment to claim a fresh test. finalize.py analyzes archived results without running portfolios. checksums.json covers artifacts; raw_report.json preserves the pre-correction machine output.

**Engineering blocker:** FAIL: five-tier support missing on2/4 stable seeds; reversal442 false GREAT before22-session latch and negative net return. Real PIT information and trusted timestamp absent; corrected independent benchmark coverage incomplete.

**Next decision:** Do not promote or optimize this bundle. Retain as gate-repair evidence; first specify acceptable reversal exposure and acquire provenance-complete real PIT predictors. Use a new externally committed protocol for any future validation.
