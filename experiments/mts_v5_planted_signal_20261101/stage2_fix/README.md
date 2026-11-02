# Stage2 cash reservation fix — stopped: scaling blocked

Local experimental correction only. Actual MTS source was not changed. No GA, historical-alpha claim, or performance recommendation. All planned affected comparisons are complete; no further runs.

## Defect and correction

Stage2 reserved settled cash for native ADD targets before validating scaling evidence. Rejected ADDs crowded out eligible entrants; rejected requests also topped up holdings drifting below 10%. The local manager now validates the evidence cap before reservation, rejects cap-denied scaling without ordinary top-ups, applies the mandatory cost-inclusive 2% modeled risk gate and other-position risk floor, and reserves incremental modeled loss in queue order. Only approved, affordable increments reserve cash including execution friction and fees. Kernel execution-time evidence, cash, settlement, and risk checks remain active.

## Verification and budget

Inspected Stage2 README, report.json, source.patch, runner, original manager, kernel and scaling policy before editing. Two identical regression cases fail against the pre-fix Stage2 manager (15% and 20% requests leave both entrants unfunded) and pass after correction. Five fixed tests cover denied reservation release, actually filled 15% and 20% targets, 2% modeled risk clipping, and independent reconstruction of fees, settlement, cash, shares and NAV. Nonnegative cash and reconstructed NAV ensure no leverage or cash over-allocation. The 2% rule is a modeled loss admission gate, not a guaranteed portfolio loss bound.

108 comparison portfolios: three signal qualities × twelve seeds (1101–1112) × 10/15/20% variants, 252 sessions, same Stage1 generator and Stage2 callbacks. No priority/hysteresis/compatibility search was replayed. All 36 tape hashes match Stage2; each 10% baseline matches its Stage2 CAGR/MDD/exposure/turnover/final NAV to 1e-10. Every comparison independently reconstructs accounting and checks modeled admitted trade loss <=2%.

Total 118 portfolio attempts: 108 comparisons + 2 expected pre-fix failures + 5 passing regression replays + 2 successful sanity portfolios + 1 discarded sanity-probe attempt. Hard limit 120. Comparison/probe runtime 33.59s; full work completed within 15 minutes. Sanity portfolios check T+1 non-reuse of sale proceeds and MDD latch with native exits. The first sanity fixture omitted settlement_sessions=1; its assertion failed before comparisons. Corrected the fixture, retained initial_probe_failure.log, and counted that attempt. No manager change followed the passing regression suite.

## Paired diagnostic outputs

Arithmetic means over the same 12 seeds. CAGR/MDD/exposure in percent; turnover is buys plus sells divided by same-session NAV, in ×. These outputs are descriptive accounting diagnostics: scaling was sparse and never reached 20%; no scaling performance claim is valid.

| Signal | Target | CAGR | MDD | Exposure | Turnover | Cap clipped/rejected | Risk clipped/rejected | Executed >10% ADDs | Full targets |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| strong | 10% | 145.4874 | 1.0063 | 78.9948 | 33.4333 | 0 | 966 | 0 | 0 |
| strong | 15% | 145.4571 | 1.0063 | 78.9992 | 33.4387 | 8628 | 17962 | 1 | 0 |
| strong | 20% | 145.4571 | 1.0063 | 78.9992 | 33.4387 | 13652 | 17962 | 1 | 0 |
| weak | 10% | 20.9766 | 3.9317 | 58.1908 | 8.3161 | 0 | 143 | 0 | 0 |
| weak | 15% | 21.0020 | 3.9317 | 58.2421 | 8.3261 | 1609 | 1823 | 2 | 1 |
| weak | 20% | 21.0020 | 3.9317 | 58.2421 | 8.3261 | 1750 | 1823 | 2 | 0 |
| misnull | 10% | 6.1287 | 7.7534 | 78.0681 | 34.0328 | 0 | 947 | 0 | 0 |
| misnull | 15% | 6.1286 | 7.7534 | 78.0683 | 34.0333 | 13501 | 18249 | 0 | 0 |
| misnull | 20% | 6.1286 | 7.7534 | 78.0683 | 34.0333 | 16089 | 18249 | 0 | 0 |

Counts are close-time funding requests, including partial clips; cap and risk counts may overlap and repeated daily requests count separately. They are not kernel fill rejection counts. Baseline risk clips concern ordinary 10% entries. Raw requested/current/cap/approved values appear in first-seed audits; runs.csv has every seed. Executed scaling requires an actual incumbent BUY whose resulting open-equity weight exceeds 10.001%, not a risk admission or price-drifted close weight. Full-target fills additionally require >=15% or >=20% within numerical tolerance. Each scaling variant executed three above-10% ADDs: strong reached 13.581629% once; weak reached 14.171370% and 15% once each. Only the 15% variant reached its full requested target (one fill); the 20% variant reached no full target. Misnull executed no above-10% ADD. See executed_scaling.csv for all six fills across both variants.

| Signal | Target vs 10% | ΔCAGR (pp) | ΔMDD (pp) | ΔExposure (pp) | ΔTurnover (×) |
|---|---:|---:|---:|---:|---:|
| strong | 15% | -0.030279 | +0.000000 | +0.004408 | +0.005421 |
| strong | 20% | -0.030279 | +0.000000 | +0.004408 | +0.005421 |
| weak | 15% | +0.025415 | +0.000000 | +0.051227 | +0.009994 |
| weak | 20% | +0.025415 | +0.000000 | +0.051227 | +0.009994 |
| misnull | 15% | -0.000072 | +0.000000 | +0.000194 | +0.000489 |
| misnull | 20% | -0.000072 | +0.000000 | +0.000194 | +0.000489 |

Scaling remains largely blocked by endogenous evidence and cost-inclusive other-position risk; no 20% target executed. Correct reservation removes the unfunded-ADD crowd-out, but these tapes do not validate concentration scaling. STOP. No tuning, gate relaxation, extra portfolios, or performance conclusions.

## Exact patch reconstruction

source.patch is a cumulative unified patch against the actual original manager, including the existing Stage2 prototype plus this correction. The runner applied it with patch -p1 in a temporary local tree and asserted exact byte equality with the tested functional_niche_manager.py. It separately reconstructed and verified the original Stage2 patch. The original manager, kernel and progressive_scaling.py hashes match Stage2 before and after. report.json records these hashes, reconstruction results, test accounting, aggregates, paired deltas and artifact hashes. The tested manager SHA-256 is `439a9aceefc9ff606522a43c0c1691f82fafe346141566f1f31079211f7fe41e`.

Reproduction from the workspace root (starts a new bounded run; not executed again here):

```bash
cd experiments/mts_v5_planted_signal_20261101/stage2_fix
PRE_FIX=1 python3 -m unittest test_reservation.Regression.test_denied_15_releases_cash test_reservation.Regression.test_denied_20_releases_cash -v  # expect 2 failures
python3 -m unittest test_reservation -v
python3 run.py
```

The reproduction now uses the corrected sanity fixture: 117 attempts; this recorded session used 118 because of the discarded probe. support.py imports Stage1 data/callback helpers and the installed kernel; only stage2_fix/functional_niche_manager.py is imported as the experimental manager. Do not run support.py as an experiment entrypoint. No patch application to actual MTS is authorized or performed.
