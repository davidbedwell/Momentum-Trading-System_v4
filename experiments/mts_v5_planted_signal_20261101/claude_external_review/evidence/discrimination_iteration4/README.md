# Discrimination iteration 4

Independent experiment; iteration3 calibration is rejected as deployment baseline. Iteration2's unchanged predictor and corrected local replay kernel are the comparator. No production edits or GA.

Run from repository root:
```
python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration4/experiment.py > experiments/mts_v5_planted_signal_20261101/discrimination_iteration4/execution.log 2>&1
python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration4/summarize.py
```
Requires the existing sibling MTS dependencies used by iteration2. Runner executes contract tests before replays and stops on failure. Reproduction overwrites artifacts; archive first.

Preregistration freezes fresh seeds 841729/926183 before tape generation, chronological train20..77/cal80..121/holdout126..249, fixed economic boundaries, model penalty, gate thresholds and 32 replay budget. No selection among ablations. Original iteration2 generator is unchanged: all policies receive identical price tapes, noisy sensors and costs. Full candidate, ungated full candidate, sensor-only and price-only models receive classification evaluation; iteration2, gated base, ungated base and gated scaled allocation receive paired portfolio evaluation. Scaling uses the existing additional realized-evidence requirements and 15% target, with cost-inclusive entire-position risk <=2%.

PIT predictors use only closes through the decision date: 20-session mean return minus fixed six-symbol synthetic sector proxy; mean minus market mean; mean divided by realized volatility; volatility. Sector membership is a fixed modeling proxy, not claimed real industry metadata. Economic hypotheses are relative strength persistence, idiosyncratic trend persistence and risk normalization. Their noise is the observed noisy return history; no fabricated signal or latent class access is added. Existing synthetic class sensor has injected Gaussian sd .30/.50 class units and retains its original inverse-variance fusion. Full ridge model adds price features; sensor-only and price-only ablations expose their contribution. Volume confirmation and revisions are unavailable and explicitly null in ledgers. No real fundamentals are inferred.

Forecast fit uses matured outcomes available by126 and never updates on holdout. Independent calibration provides date-block residual bias and uncertainty. The pooled interval is a diagnostic approximation, not a valid conditional or simultaneous coverage certificate: it does not model coefficient uncertainty, conditional heteroskedasticity or arbitrary serial dependence. Thresholds are not adjusted to populate tiers. UNKNOWN maps to NO_TRADE/exit through existing callbacks. Calibration does not fit point estimates.

Reliability is a separate policy function. It vetoes when the three models disagree by >.004, recent six-date matured forecast residual mean exceeds .004 in magnitude (minimum three dates), or price features depart >4 training SD. Deterioration/drift latch permanently; disagreement is per opportunity. The same gated state supplies GREAT confirmation and scaling. Gate outcomes never narrow intervals or force classes. Unannounced inversion has no advance observable marker; a matured-residual detector necessarily lags. Tests include a controlled reversal timing fixture; actual observed tape alarm lags are reported separately.

The original synthetic classes are independent across dates, so technical history has no designed predictive association with the next class. This is an intentional information test, not an attempt to inject a stronger oracle. Learnable and misleading scenarios have identical sensor/truth relationships; misleading refers to the legacy raw forecast. Null removes sensor association. Reversal inverts sensors at126 without a warning flag. No holdout outcomes are used to choose a model, threshold or seed.

Portfolio CAGR annualizes126 sessions; costs, T+1, cash and MDD behavior come from the unchanged corrected local kernel. One-session forward labels differ from multi-session holdings and positions are not terminally liquidated. Modeled 2% loss is not a realized-loss cap. Results are synthetic diagnostics only.

Noise/observability detail: the unchanged DGP adds .008 idiosyncratic and .003 date-common Gaussian net-return noise. Technical features inherit that noise and overlapping-window dependence; their three transformations are correlated and are not independent observations. Prices contain the cost gross-up in the original generator. Fixed six-symbol groups proxy sectors solely for this synthetic diagnostic. A missing price is mapped to zero return in the feature extractor (not proof of flat price); future-price truncation is tested for PIT causality, while missing-data robustness is not certified. The original injected sensor is observed at the decision index and has no actual market release record. It is retained only as a clearly named synthetic benchmark.




## Frozen holdout result: FAIL

FAIL: gate abstains on every holdout opportunity; zero false GREAT provides no evidence of useful discrimination. Full and sensor-only stable coverage differ by <.04 percentage points; price features add no demonstrated predictive value. Reversal latch lags 11/15 are deterioration/feature-drift alarms, not validated timely reversal detection. Global residual averaging can cancel opposing class errors; disagreement with an uninformative price-only model suppresses useful extreme forecasts. Scaling unexercised: zero incremental value is not evidence that active scaling is safe.

Completed 32 replays in 503.9s; pre-replay contract tests passed. No post-holdout tuning.

| Scenario | Model | Coverage | Accuracy | False GREAT / TERRIBLE |
|---|---|---:|---:|---:|
| learnable | iteration4 | 0.0% | n/a | 0/1176 |
| learnable | iteration2_repaired | 23.8% | 97.5% | 0/1176 |
| learnable | ungated | 39.6% | 97.8% | 0/1176 |
| learnable | sensor_only | 39.7% | 97.8% | 0/1176 |
| learnable | price_only | 0.0% | n/a | 0/1176 |
| misleading | iteration4 | 0.0% | n/a | 0/1176 |
| misleading | iteration2_repaired | 23.8% | 97.5% | 0/1176 |
| misleading | ungated | 39.6% | 97.8% | 0/1176 |
| misleading | sensor_only | 39.7% | 97.8% | 0/1176 |
| misleading | price_only | 0.0% | n/a | 0/1176 |
| null | iteration4 | 0.0% | n/a | 0/1176 |
| null | iteration2_repaired | 0.0% | n/a | 0/1176 |
| null | ungated | 0.0% | n/a | 0/1176 |
| null | sensor_only | 0.0% | n/a | 0/1176 |
| null | price_only | 0.0% | n/a | 0/1176 |
| reversal | iteration4 | 0.0% | n/a | 0/1176 |
| reversal | iteration2_repaired | 14.5% | 89.9% | 29/1176 |
| reversal | ungated | 39.6% | 0.0% | 1138/1176 |
| reversal | sensor_only | 39.7% | 0.0% | 1138/1176 |
| reversal | price_only | 0.0% | n/a | 0/1176 |

Five-tier support, precision/recall and realized forward net means: tier_aggregate.csv. Complete latent/realized confusion matrices include UNKNOWN. Actual alarm lags (null means no latch) are in summary.csv; these are not guaranteed inversion detection. Gate reason counters describe instantaneous checks; an existing permanent latch can keep a decision UNKNOWN after those checks clear. Portfolio CAGR/MDD/costs: portfolio_aggregate.csv; per-seed matched allocation deltas: paired.csv (scaled comparator delta is base minus scaled).

The candidate fails robust discrimination requirements; low false-GREAT counts achieved through abstention do not establish useful classification. Price-only and ungated ablations show the information and safety tradeoff; portfolio returns do not override failed discrimination.

Next engineering blocker: Acquire release-timestamped real PIT candidate features with measured conditional predictive information and independent regime episodes; validate conditional uncertainty and pre-entry change indicators before scaling. OHLC history cannot forecast iid synthetic future classes; sensor/price agreement is insufficient certification.
