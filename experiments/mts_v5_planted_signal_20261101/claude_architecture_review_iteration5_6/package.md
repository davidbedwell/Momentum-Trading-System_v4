# Iteration5/6 scientific evidence and architectural design request

All data here are SYNTHETIC, from the explicitly supplied DGP; no real alpha, production readiness, or real PIT provenance is established. All final seeds have now been viewed. This is an external DESIGN request, not implementation authorization. Do not merely audit statistics. Provide a SPECIFIC actionable ALTERNATIVE ARCHITECTURE, equations and online pseudocode grounded in the supplied source and evidence. Distinguish measured facts, assumptions, theoretical limits, and proposed hypotheses. Treat the original Claude review as historical advice, not authority.

Answer all requirements:
1. Mathematically identifiable earliest reversal detection using ONLY PIT observables. Define filtration and signal+3 outcome availability, prove or qualify observational equivalence before eligible outcomes; distinguish the hard 3-session limit from statistical accumulation delay. Propose concrete online sequential algorithms (e.g. likelihood ratio/CUSUM/mixture e-process), statistic, windows or horizon-free scheme, numerical thresholds, multiplicity and false-alarm correction across assets/cells/channels/time, false-alarm assumptions, and detection-delay/power calculation under this exact DGP. Address estimated baseline uncertainty and missing extreme-cell dates. Compare against current 2/4/8-window gate. Avoid oracle switch times and latent truth.
2. Eliminate more false GREAT without lowering stable return: distinguish a finite-sample observation from a population guarantee; assess whether both demands are mathematically achievable. Account explicitly for unavoidable 3-session exposure, funding, costs, liquidation and delayed outcomes. Design exposure/risk decision policy, any abstention/recovery logic, and constrained objective. Give a tradeoff frontier and refuse impossible zero-cost guarantees. No synthetic informative indicator may be silently invented.
3. Restore missing AVERAGE without forced labels, widened economic bands, or tuning these held-out tapes. Explain estimand (individual latent vs conditional mean vs realized return), center-to-boundary margin and uncertainty. Give a TRAINING-ONLY identifiable design, independent-date/sample-size calculation, feature/model changes if actually justified, calibration split, uncertainty validity, and conditions under which class support is impossible or uncertifiable. No guarantee of all classes on every random tape unless proved.
4. Provide a concrete ALTERNATIVE ARCHITECTURE with exact available inputs; equations/pseudocode for fitting, calibration, prediction, monitoring, portfolio policy and recovery; explicit training-only choices versus independent calibration; prioritized modifications with source function targets; expected benefits and costs as hypotheses; new external commitment and untouched validation plan with episode/seed denominators, multiple testing correction, stable return noninferiority and false-GREAT/detection-delay metrics. State falsification and stop criteria with numerical candidate thresholds and explain which require stakeholder risk choices. Separate impossible from engineering-fixable. Critique DGP overfitting, reviewed-holdout adaptation and model complexity; no claims of real alpha. Include minimum new data needed for each claim.

Package integrity: complete Python sources, README, preregistration, commitments, tests and archived test output, CSV metrics/confusion/detection/portfolio/audits are transmitted verbatim. Reports use semantic compaction: discrimination rows retain all fields EXCEPT train_dates/cal_dates lists, which are represented by count, endpoints, contiguity, SHA256 of canonical JSON; repetitive daily channel traces retain counts, hash, first four/last two rows and alarm neighborhoods; full reports are archived locally with original SHA256. Representative ledger examples are deterministic samples, NOT full-ledger statistical evidence; exact whole-ledger denominators are supplied. No portfolios or tests are rerun. Original review and original review metadata are included. All hashes are local provenance, not trusted timestamps.

## claude_external_review/review.md

# Scientific Peer Review: Five-Tier Discrimination Experiment Series

## 1. Evidence-Grounded Executive Verdict and Chronological Numerical Comparison

**Overall verdict: FAIL across all five reports. No iteration establishes the preregistered five-way discrimination claim. The series documents a coherent engineering progression but not scientific confirmation.**

### Chronological Numerical Summary

| Report | Seeds | N/seed | Coverage | Cond. Accuracy | False GREAT/TERRIBLE | Middle tiers populated | Reversal false GREAT |
|---|---|---|---|---|---|---|---|
| Iter1 ORIGINAL (learnable) | 2101–2104 | 2976 | 24.7% | 83.3% | 47/2394 | None | 989/2394 |
| Iter1 REPAIRED (learnable) | 2101–2104 | 2976 | 11.7% | 82.8% | 21/2394 | None | 22/2394 |
| Iter2 iteration2 (learnable) | 3101–3104 | 2976 | 22.2% | 96.7% | 0/2375 | 5 GOOD total | 23/2375 |
| Iter3 iteration3 (learnable) | 3101–3104 | 2976 | 35.2% | 97.2% | 0/2375 | None | 102/2375 |
| Iter4 iteration4 (learnable) | 841729, 926183 | 2976 | 0.0% | n/a | 0/1176 | None | 0/1176 |

**Critical observations:**
- The original evaluator's 989 false GREAT (reversal) was a genuine evaluator bug, not a DGP property; the repair reduced this to 22 on the same tapes/seeds.
- Iteration2 uses new seeds (3101–3104) on new tapes; its comparator `previous_repaired` on those same new tapes yields 39 false GREAT (reversal), not 22—these are different tapes and the numbers are not directly comparable.
- Iteration3 reuses seeds 3101–3104 with the same tapes as iteration2; its 102 false GREAT (reversal) versus iteration2's 23 on identical tapes is a valid within-tape comparison showing regression in reversal safety.
- Iteration4 uses two fresh seeds (841729, 926183); its zero false GREAT is achieved through universal abstention (0% coverage), providing no discrimination evidence.
- POOR/AVERAGE/GOOD remain absent in iterations 1 (original and repaired), 3, and 4. Iteration2 produces 5 GOOD observations total across 4 seeds × 2 scenarios—insufficient for any inference.

---

## 2. Fatal Versus Repairable Methodological Issues

### Fatal Issues (block any positive claim)

**F1. Middle-tier structural impossibility with current DGP and estimator.**
The POOR/GOOD bands have half-width 0.002. With 80% faithful coarse sensor, E[net|cell=POOR] ≈ −0.0032, only 0.0012 from the TERRIBLE/POOR boundary. The diagnostic radius formula (max of 2.58×SE_train, |bias| + 2.58×SE_cal) routinely exceeds 0.0012 with ≤21 independent date clusters. This is not a bug—it is a correct reflection of genuine uncertainty. The iteration3 frozen-fit radii for middle cells are 0.00236–0.00508 (seeds 3101–3104, `frozen_fit_diagnostics`), all exceeding the 0.002 half-band. **No amount of estimator refinement can certify middle tiers without either more independent dates, narrower noise, or wider bands—none of which are permitted by the preregistration.**

**F2. Iteration3 reuses iteration2's exact tapes (seeds 3101–3104).**
The preregistration explicitly states "Prior iteration2 holdout already viewed: this is a prespecified synthetic regression comparison, not a novel confirmatory holdout." The 96,000 identical ledger rows are confirmed by `artifact_audit`. Any positive result on these tapes cannot be confirmatory.

**F3. Iteration4 universal abstention.**
Zero coverage (0/5952 opportunities assigned) means the gate provides no discrimination evidence. The 0 false GREAT is achieved by abstaining on every opportunity, not by correct classification. The `gate_reason_counts` show 10,182 FORECAST_DISAGREEMENT vetoes—the disagreement gate between full and price-only models suppresses all useful sensor predictions because the price-only model is uninformative (rank_correlation ≈ 0.02 for price-only vs. realized returns).

**F4. Iteration2 calibration independence violation.**
The primary online estimator pools recent calibration observations into its point estimate. The preregistration and local REVIEW.md both acknowledge: "Primary pooled estimator uses its recent calibration window in the point estimate. That window is a drift/stability diagnostic, not independent calibration." This violates the independent calibration requirement and precludes certification of the complete online bundle.

**F5. Insufficient independent seeds/regimes for any claim.**
Four seeds (iterations 1–3) or two seeds (iteration4) over 126 sessions with 24 cross-sectionally dependent stocks do not provide the statistical power to distinguish signal from noise. The 2.58-SE intervals are explicitly labeled "diagnostic, not formal simultaneous/dependence-robust coverage."

### Repairable Issues

**R1. Original evaluator false GREAT bug (989/2394):** Fixed in the repaired evaluator (22/2394). Confirmed repair.

**R2. Preregistration metadata discrepancy (repaired):** Version 2 method supersedes inherited static fields; window counts 40/21/9 vs. nominal 40/20/8. Acknowledged but not repaired post-evaluation.

**R3. CAGR annualization error in iterations 2–4:** `metric['cagr']=(metric['final_nav']/s.INITIAL)**2-1` uses exponent 2 instead of `252/126=2`. This happens to be numerically identical for 126-session windows but is a formula error. The README tables show CAGR values consistent with the squaring formula (e.g., iteration3 learnable/iteration3: 159.80% = (1.577)²−1 ≈ correct for 126 sessions at 252/year). **This is actually correct for 126 sessions: (NAV/initial)^(252/126) = (NAV/initial)^2.** Not a bug.

**R4. Iteration4 gate design flaw (repairable):** Requiring agreement between full model and uninformative price-only model guarantees suppression of all sensor-based predictions. Removing the price-only model from the disagreement gate would allow the sensor to function. However, this would require a new preregistration.

---

## 3. Leakage and Preregistration Audit

### Chronological PIT Causality
The causal chain k→k+1→k+2 (signal→execution→maturity) is correctly implemented across all iterations. The `observed()` function uses `days[i+2][1][t].open / days[i+1][1][t].open - 1`, and the fit requires `i+2 < cutoff`. The rolling estimator in iterations 2–4 uses `maturity_index = now+2` with `available_index = now+3`, consistent with the stated protocol.

**Iteration2 vs. Iteration3 tape reuse:** Iteration2 can use matured holdout sequentially (prequential). Iteration3 uses a frozen fit at index 126 with safety-only holdout veto—this is causally valid but the tapes are not fresh confirmatory data. The distinction matters: iteration3's holdout outcomes are not used for fitting, but the tape itself was already evaluated in iteration2, so any positive result would be pseudo-confirmatory.

**Iteration4 DGP inheritance:** Seeds 841729/926183 are fresh, but the DGP, sensor design, band boundaries, and estimator architecture were all informed by four prior iterations. This constitutes developer adaptation. The preregistration acknowledges "No holdout outcomes are used to choose a model, threshold or seed" but cannot exclude the broader design adaptation.

### Preregistration Compliance
- **Iteration1 original:** Preregistered before execution; SHA256 verified (`174df2...`). PASS on process.
- **Iteration1 repaired:** Version 2 method supersedes inherited fields; window count discrepancy (40/21/9 vs. 40/20/8) acknowledged. Minor documentation FAIL.
- **Iteration2:** Preregistered before execution; SHA256 verified (`f3d910...`). The static ablation was reserved before execution. PASS on process.
- **Iteration3:** Preregistered before execution; SHA256 verified (`4d2b65...`). Explicitly acknowledges tape reuse. PASS on process, FAIL on confirmatory claim.
- **Iteration4:** Preregistered before execution; SHA256 verified (`578ef7...`). Fresh seeds. PASS on process.

### Leakage Assessment
No direct runtime leakage of evaluation truth into inference is detected across any iteration. The `discrimination()` function receives `truth` only for scoring, not for the estimator. The `causal_predictions()` and `predict()` functions use only matured realized returns, never latent EV labels.

**Developer adaptation leakage (indirect):** Each iteration's design was informed by the previous iteration's results. The gate thresholds (0.004 disagreement, 0.004 residual mean, 4 SD feature drift) in iteration4 were chosen after observing iteration3's behavior. This is not runtime leakage but constitutes design-space exploration that inflates the effective false-positive rate of the overall series.

---

## 4. Uncertainty and Identification Critique

### Distinct Estimands
The series conflates three distinct estimands:

1. **Latent individual class** (TERRIBLE/POOR/AVERAGE/GOOD/GREAT): The generative DGP class z, evaluator-only, never observable.
2. **Conditional mean tier**: The tier of E[net|cell], the cell's expected return. This is what the estimator targets.
3. **Individual realized return tier**: The tier of the actual one-session net return, which includes common-date shock (σ=0.003) and idiosyncratic shock (σ=0.008).

The confusion matrices labeled "latent_ev" use the conditional mean µ(z) as truth, not the individual class z. The "realized_return" matrices use tier(actual_net). These are distinct and the report correctly separates them, but the pass criteria mix them: "conditional exact EV-tier accuracy" tests the conditional mean estimand, while "five realized tier means strictly monotone" tests the realized return estimand. A classifier can satisfy one without the other.

**Accuracy conditional on abstention conceals poor all-opportunity recall.** For iteration2 (learnable, aggregate): conditional accuracy = 96.7%, but recall including abstentions for POOR = 8.5%, AVERAGE = 12.9%, GOOD = 0.17%. The 96.7% figure is computed only over the 22.2% of opportunities that receive a label. The all-opportunity recall for middle tiers is near zero.

### Confusion Matrix Analysis (Iteration2, Learnable, Aggregate, Latent EV)
From `exact_aggregate_matrices` (seeds 3101–3104, learnable, iteration2):
```
True\Pred  TERRIBLE  POOR  AVERAGE  GOOD  GREAT  UNKNOWN
TERRIBLE    1011      4      0       0      0     1360
POOR          25    198     12       0      0     2095
AVERAGE        0      9    307       1      0     2054
GOOD           0      0      9       4     27     2321
GREAT          0      0      0       0   1031     1436
```
- True TERRIBLE: 1011 correct, 4 misclassified as POOR, 0 false GREAT, 1360 UNKNOWN. False GREAT rate = 0/2375 = 0%.
- True GREAT: 1031 correct, 0 misclassified as TERRIBLE, 1436 UNKNOWN. True TERRIBLE misclassified as GREAT = 0.
- POOR support: 198/2330 = 8.5% recall. AVERAGE: 307/2371 = 12.9%. GOOD: 4/2361 = 0.17%.

**The five-class support is severely imbalanced.** GOOD has only 4 correct assignments across 4 seeds × 2976 opportunities = 11,904 total. This is insufficient for any statistical claim about GOOD discrimination.

### Iteration3 Radii and Middle Tier Impossibility
From `frozen_fit_diagnostics` (seed 3101):
- Cell 1 (POOR): mean=−0.00409, radius=0.00376. Interval [−0.00785, −0.00033] spans TERRIBLE/POOR boundary (−0.006) and POOR/AVERAGE boundary (−0.002). → UNKNOWN.
- Cell 2 (AVERAGE): mean=−0.000218, radius=0.00405. Interval [−0.00427, 0.00383] spans three bands. → UNKNOWN.
- Cell 3 (GOOD): mean=0.00323, radius=0.00312. Interval [0.00011, 0.00635] spans AVERAGE/GOOD/GREAT. → UNKNOWN.

All four seeds show the same pattern. The radii (.00236–.00508) systematically exceed the 0.002 half-band for middle cells. This is not a calibration failure—it is an honest reflection of the information content available from 16 training blocks and 8 calibration blocks with date-common noise.

### SE Interval Validity
The 2.58-SE intervals are date-clustered (treating each date's cross-sectional mean as one observation), which correctly accounts for within-date dependence. However:
- Serial dependence across dates is not modeled.
- The ~8 calibration blocks (five-date blocks from 42 calibration dates) provide only 8 effective observations for the calibration SE.
- The Gaussian posterior in iteration3 assumes independent blocks—not guaranteed with overlapping return windows.
- No simultaneous coverage correction is applied across five cells.

---

## 5. Safety and Economic Validity

### False GREAT / True TERRIBLE Trajectory
| Report | Scenario | False GREAT / True TERRIBLE | Rate |
|---|---|---|---|
| Iter1 original | reversal | 989/2394 | 41.3% |
| Iter1 repaired | reversal | 22/2394 | 0.92% |
| Iter2 iteration2 | reversal | 23/2375 | 0.97% |
| Iter3 iteration3 | reversal | 102/2375 | 4.30% |
| Iter4 iteration4 | reversal | 0/1176 | 0% (abstention) |
| Iter4 ungated | reversal | 1138/1176 | 96.8% |

The iteration3 regression (102 vs. 23 on identical tapes) is explained by the frozen fit: the static estimator cannot adapt after the reversal, while iteration2's online estimator detects drift and quarantines. The iteration4 ungated model (1138/1176) confirms that without the gate, the sensor-based model is catastrophically wrong after reversal—the gate's safety function is real, but it achieves safety through universal abstention.

**The reversal false GREAT comparison between iteration4 (0/1176) and iteration2 comparator (29/1176) is on different tapes.** The iteration4 comparator uses seeds 841729/926183 on new tapes; the iteration2 result used seeds 3101–3104. These cannot be directly compared.

### Portfolio Returns
Portfolio returns are not evidence of discrimination. The DGP grosses up one-session EV by round-trip costs; multi-session holdings pay costs less frequently, generating positive drift even under null signals. The null/existing_ev10 portfolio earns 21.95% (iteration1) and 25.03% (iteration2) with zero classification. These are artifacts of the cost-grossup horizon mismatch, not recognition evidence.

The learnable/tier10 portfolio in iteration1 original earns 27.4% mean return, but seeds 2103 and 2104 earn 0% (no fills) due to the estimator producing only TERRIBLE predictions for those seeds. This seed-level heterogeneity (2 of 4 seeds with zero fills) is masked by the mean.

### Modeled vs. Realized Risk
The 2% entire-candidate modeled risk is verified post-BUY (`max_modeled_trade_loss ≤ 0.02` across all iterations). However, this is a modeled loss based on gap assumptions, not a realized loss cap. No terminal liquidation means pending positions remain marked at last price.

### Economic Band Validity
The absolute bands (±0.2%, ±0.6%) are economically motivated but create a structural problem: the DGP's individual noise (σ=0.008 idiosyncratic + σ=0.003 common) means that even a perfectly classified GREAT opportunity (µ=+1.2%) has P(realized < 0.6%) ≈ P(Z < (0.006−0.012)/0.0085) ≈ P(Z < −0.71) ≈ 24%. The realized return tier is not the same as the latent class tier, and the confusion matrices confirm this: for iteration2 learnable, 807 true-GREAT opportunities are realized-UNKNOWN (i.e., realized return in [−0.2%, +0.2%]).

---

## 6. Prioritized Actionable Engineering Changes

### Priority 1 (Blocking): Fix the Iteration4 Gate Design
**Problem:** Requiring agreement between full model and uninformative price-only model (rank_IC ≈ 0.02) guarantees suppression of all sensor-based predictions.
**Change:** Remove price-only from the disagreement gate. Use sensor-only vs. full disagreement, or use a calibrated threshold based on training-period disagreement distribution.
**Acceptance test:** On fresh seeds with learnable scenario, ungated coverage ≥ 30% and gated coverage ≥ 15% with false GREAT/TERRIBLE ≤ 1% on stable tapes.
**Minimum new data:** 2 fresh seeds, same DGP.

### Priority 2 (Blocking): Obtain More Independent Date Clusters for Middle Tiers
**Problem:** 16 training blocks and 8 calibration blocks are insufficient to certify middle bands with half-width 0.002 given the noise structure.
**Change:** Either (a) extend the training window to ≥200 dates (requiring a longer synthetic history), or (b) widen the POOR/GOOD bands to ±0.4% (half-width 0.004), which would require a new preregistration and economic justification.
**Acceptance test:** Middle-tier radii < 0.002 for at least 3 of 4 seeds in stable scenarios.
**Minimum new data:** Synthetic history of ≥300 dates with same DGP, or preregistered band change.
**Note:** Do not narrow bands to populate tiers.

### Priority 3 (Blocking): Establish Genuinely Untouched Outer Evaluation
**Problem:** Iterations 2–4 all use tapes or DGP designs informed by prior results. No iteration provides a truly fresh confirmatory test.
**Change:** Preregister a final evaluation protocol with seeds drawn from a hardware RNG after all design decisions are frozen. Archive the preregistration with a trusted timestamp before any tape generation. Use a completely separate holdout DGP variant (e.g., different noise levels) to test generalization.
**Acceptance test:** Preregistration hash matches a publicly timestamped commitment made before any tape generation.
**Minimum new data:** 4+ fresh seeds on the frozen design.

### Priority 4 (Important): Separate Calibration from Point Estimation
**Problem:** Iteration2's primary estimator pools calibration into the mean, violating independent calibration.
**Change:** Use a strictly disjoint calibration window (e.g., signals 80–121) only for uncertainty estimation, never for point estimate adjustment. The iteration3 approach (frozen fit + independent calibration blocks) is closer to correct but uses only 8 calibration blocks.
**Acceptance test:** Calibration window outcomes have zero correlation with training window outcomes used for point estimation (verify by construction).

### Priority 5 (Important): Sequential False-Alarm Control for Drift Detector
**Problem:** The drift detector scans 5 cells repeatedly without multiplicity correction. Iteration2 reports 2–6 nuisance alarms per seed in stable scenarios.
**Change:** Apply a Bonferroni or Holm correction across the 5 cells at each scan. Use a prespecified maximum number of scans with union-bound correction (as iteration3 does for its 26-look monitor).
**Acceptance test:** Nuisance alarm rate ≤ 5% per stable-scenario seed over 126 holdout sessions.

### Priority 6 (Important): All-Opportunity Outcome Ledger with Horizon-Matched Labels
**Problem:** One-session net labels are used for a portfolio that holds positions for multiple sessions. The DGP cost grossup creates positive drift for multi-session holders.
**Change:** Implement a horizon-matched label: for each entry at session k, record the net return from open(k+1) to the actual exit open, not just open(k+2). Compare this to the one-session label to quantify the horizon mismatch.
**Acceptance test:** Null scenario portfolio return ≤ 2% over 126 sessions with horizon-matched labels.

### Priority 7 (Prerequisite for Production): Real PIT Feature Validation
**Problem:** All iterations use synthetic injected sensors. The price-only features have no designed predictive association with iid synthetic classes (confirmed by rank_IC ≈ 0.02).
**Change:** Acquire release-timestamped real PIT features with documented revision history, missingness patterns, and measured conditional predictive information. Validate on independent regime episodes before any production claim.
**Acceptance test:** Real PIT features show rank_IC > 0.1 on out-of-sample data with documented release timestamps.

---

## 7. Targeted Questions Whose Answers Change the Conclusion

**Q1. What is the actual false-alarm rate of the iteration4 deterioration/feature-drift latch on stable scenarios?**
Seed 841729 learnable triggers a DETERIORATION alarm at index 162; seed 926183 learnable triggers FEATURE_DRIFT at index 141. Both are in the stable (non-reversal) scenario. If these are nuisance alarms, the latch permanently suppresses all subsequent predictions, explaining the 0% coverage. *If the latch is removed and replaced with a per-opportunity gate, does coverage recover to ≥15% with false GREAT ≤ 1%?* This would change the conclusion from "gate is broken" to "latch is too aggressive."

**Q2. Are the iteration4 reversal latch lags (11, 15 sessions) deterioration alarms or genuine reversal detection?**
The report states "11/15 are deterioration/feature-drift alarms, not validated timely reversal detection." If these are feature-drift alarms triggered by the price features responding to the reversal (which changes the price history), they may be detecting the reversal indirectly. *What is the alarm trigger: deterioration of residuals or feature drift?* The per-seed data shows seed 841729 reversal: DETERIORATION at index 137 (lag=11); seed 926183 reversal: FEATURE_DRIFT at index 141 (lag=15). Feature drift at index 141 = 15 sessions after reversal at 126. This is consistent with price history gradually reflecting the reversal. If this is a genuine (if delayed) detection mechanism, it has value—but the 15-session lag means 15 sessions of potential false GREAT exposure.

**Q3. Does removing the price-only model from the disagreement gate restore useful coverage?**
The `gate_reason_counts` show 10,182 FORECAST_DISAGREEMENT vetoes out of 23,808 total holdout decisions (4 scenarios × 2 seeds × 2976 opportunities = 23,808). If the disagreement gate is removed, does the sensor-only model achieve coverage ≥ 15% with false GREAT ≤ 1% on stable scenarios? The ungated model achieves 39.6% coverage with 0 false GREAT on stable scenarios, suggesting the sensor has genuine information. *The answer to this question determines whether iteration4's failure is a gate design flaw or a fundamental information absence.*

**Q4. What is the per-seed paired return delta for iteration2 vs. iteration3 on identical tapes (seeds 3101–3104)?**
From the paired data: iteration3 learnable vs. iteration2_repaired mean return delta = +28.2 percentage points (iteration3 higher). But iteration3 achieves this with 0 middle-tier support and worse reversal safety (102 vs. 23 false GREAT). *Is the return improvement entirely explained by the higher extreme-tier coverage (35.2% vs. 22.2%), and does it persist after accounting for the reversal safety regression?* If yes, this confirms that coverage of extreme tiers drives returns, not middle-tier discrimination.

**Q5. What fraction of the iteration2 FORECAST_DISAGREEMENT vetoes in iteration4 are between sensor-only and full model (vs. full and price-only)?**
The disagreement gate uses `max(preds.values()) - min(preds.values()) > 0.004`. If the price-only model predicts near zero (as expected for iid classes), and the sensor predicts ±0.01, the disagreement will always exceed 0.004. *Is the gate effectively `|sensor_prediction| > 0.004`?* If so, it is suppressing all confident sensor predictions, which is the opposite of the intended safety function.

**Q6. Can the middle tiers be populated with the current DGP by using a finer sensor (σ=0.10 instead of 0.30/0.50)?**
The iteration2 sensor uses σ=0.30/0.50 class units. With σ=0.10, the conditional cell means would be closer to the true class means (E[net|cell] ≈ 0.95×µ_class), potentially centering POOR/GOOD cells further from boundaries. *Would this reduce the radius below 0.002 for middle cells?* This would require a new preregistration and would change the sensor design, but it would test whether the middle-tier absence is a sensor-noise problem or a fundamental date-cluster problem.

**Q7. What is the realized loss distribution for the reversal scenario under iteration2 (23 false GREAT)?**
The 23 false GREAT assignments in iteration2 reversal represent TERRIBLE opportunities labeled GREAT. The realized net for GREAT-labeled opportunities in reversal is +1.14% (from tier_aggregates). But these 23 false GREAT are TERRIBLE opportunities with expected realized net ≈ −1.2%. *What is the actual realized loss for these 23 opportunities?* If the realized loss is small (due to the reversal happening gradually), the safety risk may be lower than the false GREAT count suggests. If the realized loss is large, it confirms the safety concern.

---

## Report/Schema Discrepancies

1. **Iteration4 `paired` field uses `iteration3_return` key** for the candidate return, not `iteration4_return`. This is a schema inconsistency inherited from iteration3's code but does not affect the numerical values.

2. **Iteration2 CAGR formula:** `metric['cagr']=(metric['final_nav']/s.INITIAL)**2-1` is used in iterations 2, 3, and 4. For 126 sessions with 252-session annualization, this is `(NAV/initial)^(252/126) = (NAV/initial)^2`, which is numerically correct. However, the formula is written as a literal `**2` rather than `**(252/len(evdays))`, making it fragile if the session count changes.

3. **Iteration4 `aggregate` field `drift_lags`** is stored as a string `"[null, null]"` rather than a JSON array `[null, null]`. This is a serialization inconsistency.

4. **Iteration3 portfolio `exposure_fields`** is a nested dict `{"exposure": 0.266}` rather than a flat field, unlike iterations 1–2 which have `"exposure": 0.266` directly. This schema change makes cross-iteration comparison harder.

5. **Iteration1 original `mean_rank_ic`** for misleading scenario = +0.532 (same as learnable), but `mean_raw_prediction_rank_ic` = −0.532. This is correct by construction (misleading reverses the raw prediction), but the aggregate table in the README shows identical coverage/accuracy for learnable and misleading, which is expected since the tier assignments use the cell mean (not the raw prediction) and the cell means are identical across scenarios for the same seed.

6. **Iteration4 `per_seed_discrimination` for iteration2_repaired** shows seed 926183 reversal with 0 false GREAT (159 TERRIBLE, 0 GREAT predicted), while the aggregate shows 29/1176. The 29 false GREAT come entirely from seed 841729 (29 confirmed in per-seed data). This is consistent but the aggregate table header "False GREAT / TERRIBLE = 29/1176" uses the total TERRIBLE count (1176 = 2 seeds × 588), not just seed 841729's TERRIBLE count (557). The rate 29/1176 = 2.47% is correct as an aggregate rate.

---

## What Cannot Be Inferred

1. Whether any real PIT features have predictive information for the MTS's actual opportunity universe. All results are synthetic.
2. Whether the 2% modeled risk bound translates to any realized loss protection in live trading.
3. Whether the positive portfolio returns in learnable/misleading scenarios reflect any genuine alpha or are entirely explained by the cost-grossup horizon mismatch.
4. Whether the iteration4 deterioration/feature-drift alarms on stable scenarios represent genuine model instability or are false alarms from the price feature extractor responding to normal return variation.
5. The statistical power of any test in this series: with 4 seeds (or 2), date-clustered observations, and no formal dependence model, no p-value or confidence interval can be computed with known coverage.



## claude_external_review/submission_metadata.json

{
  "timestamp_utc": "2026-11-01T14:13:18.429952+00:00",
  "endpoint": "https://openrouter.ai/api/v1/chat/completions",
  "submitted": true,
  "http_status": 200,
  "model": "anthropic/claude-sonnet-4.6",
  "usage": {
    "prompt_tokens": 227371,
    "completion_tokens": 7498,
    "total_tokens": 234869,
    "cost": 0.794583,
    "is_byok": false,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "cache_write_tokens": 0,
      "audio_tokens": 0,
      "video_tokens": 0
    },
    "cost_details": {
      "upstream_inference_cost": 0.794583,
      "upstream_inference_prompt_cost": 0.682113,
      "upstream_inference_completions_cost": 0.11247
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "image_tokens": 0,
      "audio_tokens": 0
    }
  },
  "provider_response_verified": true,
  "credential_path": "/opt/mts/thunder-migration/.openrouter_api_env",
  "errors": [],
  "models_http_status": 200,
  "offered_claude_models": [
    "anthropic/claude-sonnet-5.5",
    "anthropic/claude-sonnet-5.5:batch",
    "anthropic/claude-opus-5.5",
    "anthropic/claude-opus-5.5:batch",
    "anthropic/claude-opus-5",
    "anthropic/claude-opus-5:batch",
    "anthropic/claude-sonnet-5",
    "anthropic/claude-sonnet-5:batch",
    "anthropic/claude-opus-4.8",
    "anthropic/claude-opus-4.8:batch",
    "anthropic/claude-opus-4.7",
    "anthropic/claude-opus-4.7:batch",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-sonnet-4.6:batch",
    "anthropic/claude-opus-4.6",
    "anthropic/claude-opus-4.6:batch",
    "anthropic/claude-opus-4.5",
    "anthropic/claude-opus-4.5:batch",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-sonnet-4.5:batch",
    "anthropic/claude-opus-4.1",
    "anthropic/claude-opus-4.1:batch"
  ],
  "model_context_length": 1000000,
  "conservative_context_budget": 329262,
  "request_sha256": "027ee53d63113717ef3860bc2449d0ae952496d813e08efba7dad35ad31b0d91",
  "request_bytes": 673945,
  "post_attempted_at_utc": "2026-11-01T14:13:18.527410+00:00",
  "response_model": "anthropic/claude-sonnet-4.6",
  "provider": "Claude Platform on AWS",
  "response_id": "gen-1793542398-jUuNBDqWKmsFwlZNbc3t",
  "finish_reason": "stop",
  "claude_model_identity_verified": true,
  "review_characters": 26934,
  "substantive_review_check": true,
  "completed_at_utc": "2026-11-01T14:16:22.013622+00:00",
  "status": "SUBMITTED_AND_VERIFIED"
}



## discrimination_iteration5/README.md

```
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

```


## discrimination_iteration5/benchmark_correction_commitment.json

```
{
  "source_sha256": "f22cc50c64a942a22ed19a1d23b8d61269df6c9c239a84000f221acd65f8acc1",
  "phase": "post-freeze correction on already viewed learnable tapes",
  "reason": "Original benchmark forecast-ranked cash-limited purchases; invalid independent control.",
  "additional_replays": 4
}
```


## discrimination_iteration5/checksums.json

```
{
  "README.md": "db531c8cae3e47018f8861680f56bce98e51be4604e117df32e426a89bc995b7",
  "benchmark_correction_commitment.json": "da1e1ed1401c36576858d16d3b3536afb1fcb0979af2ee897b5e741c34681078",
  "commitment.json": "7f51d54ee11a8f342021321d5d8f6ad4b788e6c4a52f6c1b387a68ed1baae9a7",
  "corrected_benchmark.py": "f22cc50c64a942a22ed19a1d23b8d61269df6c9c239a84000f221acd65f8acc1",
  "corrected_benchmark_metrics.csv": "3acaaa98b2cea7daa637bb838763784b1d0628daa3f70bcd27c98f2f0fd3845c",
  "corrected_benchmark_paired.csv": "34200da72ecb4851b068d9d8e586a49390d053c9c78e5392e019de0c93a9c9a3",
  "corrected_benchmark_replays.jsonl.gz": "9d273a2bcf85d33781b7e8dad70a0b0d31ee80eb9c3e15edec7278cd137bb3f2",
  "corrected_benchmark_results.json": "9d9d97e30345112dd12c189e090703c5c146ceaa97b0f0045dbcd696e3219a4e",
  "execution.log": "2f60496a87daa3873e1ec7f2c770566330b5f1c0f67b91f2b4f90838d5cc401b",
  "experiment.py": "374e1fda136c50c643cbfce4ab2bd1ed26274b19b433dfc38109ead03a1b50a0",
  "finalize.py": "c6c98d50a7d6532697dc61c0817ad5baf21397ee27b64f018ab384ed120f6014",
  "ledger_audit.csv": "60befbe0ca58e5fc5571dd4b952faf06d49de9c6c22d68f15128bee381b69286",
  "metrics.csv": "7f61882fba2627e740ac51003742861e036fc05e93629bc227220d946e579a8b",
  "opportunities.jsonl.gz": "dd17c242a2bdea1610c6e0eadfff8f975f4324ecf67ba74709f6e653a204e495",
  "paired.csv": "467494525463a05dfe864aa70ae1ec3fd1ba83845b4e088ff8a284021d2eb8e1",
  "pit_schema.json": "0a32482af58c4fab83b220829fc3498c6750757bb6558387da61a7082958c73e",
  "preregister.json": "f6253010529818262e3b4f52511d307ae0cafb3129629c164e4293db06495b0c",
  "raw_report.json": "3b7f4677cb0af3324c1068554780a3b646a39498a0fa4724682cd57f55e1af50",
  "replays.jsonl.gz": "1eae2fd4dc0e24ed2969edb7d71a5e7abde5e57511c8dfc05f9517464b7aca8c",
  "report.json": "feb70078c9f945a1a1dbe13884b6525ad572b40f69c3cce8777e42169250f64f",
  "seeds.json": "c6b9508f47995a779cd4b8d86e285d9ba33727a4d3959d6abb330ade3bf146be",
  "test_experiment.py": "4ae56648ea21e1edb241d2699b08aeb00c3e3401baf9b8c8a4dadff82f6408a9",
  "tests.log": "8432c726eebebf7df9915e81f43bd4e4d1d60b27e1d2de00e9f0461266db660c",
  "tier_metrics.csv": "61be4e90ebb679e759e0abbd54f454d8719fa6334a2d3f27c1e6ef3f1b3f27b1"
}
```


## discrimination_iteration5/commitment.json

```
{
  "utc": "2026-11-01T14:24:04.481259+00:00",
  "sources": {
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration5/experiment.py": "374e1fda136c50c643cbfce4ab2bd1ed26274b19b433dfc38109ead03a1b50a0",
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration5/test_experiment.py": "4ae56648ea21e1edb241d2699b08aeb00c3e3401baf9b8c8a4dadff82f6408a9",
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration5/preregister.json": "f6253010529818262e3b4f52511d307ae0cafb3129629c164e4293db06495b0c"
  },
  "preregister_sha256": "f6253010529818262e3b4f52511d307ae0cafb3129629c164e4293db06495b0c"
}
```


## discrimination_iteration5/corrected_benchmark.py

```
"""Post-freeze engineering correction, evaluated descriptively on four already viewed tapes.
No predictions or signal ranking are accepted. Each entry uses equal notional across 24 names.
"""
import hashlib,json,time
from pathlib import Path
import experiment as e
O=Path(__file__).resolve().parent

def replay_equal(prices):
    cash=100000.;receivable=0.;held=[];peak=100000.;mdd=0.;costs=0.;trades=[];daily=[]
    for i in range(e.START,e.END):
        cash+=receivable;receivable=0.
        for t in held:
            proceeds=t['shares']*prices[i+1][t['j']]*(1-e.COST/2);receivable+=proceeds;costs+=t['shares']*prices[i+1][t['j']]*e.COST/2
            t.update(exit_index=i+1,net=proceeds/t['debit']-1);trades.append(t)
        held=[];opening=cash+receivable
        debit=min(cash/24,opening/24)
        for j in range(24):
            if debit<=1e-8:continue
            shares=debit/(prices[i+1][j]*(1+e.COST/2));risk=shares*prices[i+1][j]/opening*([.03,.06,.12,.24][j%4]+e.COST)
            assert risk<=.02
            held.append(dict(signal=i,j=j,shares=shares,debit=debit,entry_index=i+1,modeled_risk=risk));cash-=debit;costs+=shares*prices[i+1][j]*e.COST/2
        assert cash>=-1e-7
        nav=cash+receivable+sum(t['shares']*prices[i+1][t['j']] for t in held);peak=max(peak,nav);mdd=max(mdd,1-nav/peak);daily.append(dict(index=i,nav=nav,cash=max(0,cash)))
    for t in held:
        proceeds=t['shares']*prices[e.END+1][t['j']]*(1-e.COST/2);cash+=proceeds;costs+=t['shares']*prices[e.END+1][t['j']]*e.COST/2;t.update(exit_index=e.END+1,net=proceeds/t['debit']-1);trades.append(t)
    nav=cash+receivable;peak=max(peak,nav);mdd=max(mdd,1-nav/peak)
    # Integrated invariant checks do not execute additional portfolios.
    bydate={}
    for t in trades:bydate.setdefault(t['signal'],[]).append(t)
    assert all(len(ts)==24 and max(t['debit'] for t in ts)==min(t['debit'] for t in ts) for ts in bydate.values())
    return dict(total_return=nav/100000-1,cagr=(nav/100000)**2-1,mdd=mdd,costs=costs,final_nav=nav,trades=len(trades)),trades,daily

if __name__=='__main__':
    if (O/'corrected_benchmark_results.json').exists():raise SystemExit('No rerun permitted')
    start=time.monotonic();commit=dict(source_sha256=e.sha(__file__),phase='post-freeze correction on already viewed learnable tapes',reason='Original benchmark forecast-ranked cash-limited purchases; invalid independent control.',additional_replays=4)
    (O/'benchmark_correction_commitment.json').write_text(json.dumps(commit,indent=2))
    rows=[]
    import gzip
    with gzip.open(O/'corrected_benchmark_replays.jsonl.gz','wt') as f:
        for seed in json.loads((O/'seeds.json').read_text()):
            p,_,_=e.generate(seed,'learnable');metric,trades,daily=replay_equal(p);rows.append(dict(seed=seed,scenario='learnable',variant='corrected_equal_universe',**metric));f.write(json.dumps(dict(seed=seed,trades=trades,daily=daily))+'\n')
    (O/'corrected_benchmark_results.json').write_text(json.dumps(dict(runs=rows,elapsed_seconds=time.monotonic()-start,**commit),indent=2));e.writecsv('corrected_benchmark_metrics.csv',rows)

```


## discrimination_iteration5/corrected_benchmark_metrics.csv

```
seed,scenario,variant,total_return,cagr,mdd,costs,final_nav,trades
1564008556893530022,learnable,corrected_equal_universe,0.0012100007917366096,0.002421465685389146,0.022706316339030863,19194.585079138906,100121.00007917365,1512
1634635432866334191,learnable,corrected_equal_universe,-0.022751766007440333,-0.04498588915842339,0.03225819886723702,18594.00594861596,97724.82339925597,1512
5015368413594993126,learnable,corrected_equal_universe,0.03000399146943411,0.06090822244296601,0.015172876533262714,19141.388367254258,103000.39914694341,1512
3584306075979195116,learnable,corrected_equal_universe,0.005221912988778055,0.010471094352818566,0.03103160661240656,18944.136993032975,100522.1912988778,1512

```


## discrimination_iteration5/corrected_benchmark_paired.csv

```
seed,scenario,candidate_return,benchmark_return,return_delta,cagr_delta,mdd_delta,cost_delta
1564008556893530022,learnable,0.8565803518951918,0.0012100007917366096,0.8553703511034552,2.444469137357885,-0.02074277086715104,7196.149237344529
1634635432866334191,learnable,0.8532868241113967,-0.022751766007440333,0.876038590118837,2.4796579415833304,-0.028262505296307694,7519.892585078051
5015368413594993126,learnable,0.8611443345975147,0.03000399146943411,0.8311403431280806,2.40295001176146,-0.013123213641742182,6589.674482551403
3584306075979195116,learnable,0.8954416618367764,0.005221912988778055,0.8902197488479984,2.5822279990737425,-0.02970537042494037,7454.591947392932

```


## discrimination_iteration5/corrected_benchmark_results.json

```
{
  "runs": [
    {
      "seed": 1564008556893530022,
      "scenario": "learnable",
      "variant": "corrected_equal_universe",
      "total_return": 0.0012100007917366096,
      "cagr": 0.002421465685389146,
      "mdd": 0.022706316339030863,
      "costs": 19194.585079138906,
      "final_nav": 100121.00007917365,
      "trades": 1512
    },
    {
      "seed": 1634635432866334191,
      "scenario": "learnable",
      "variant": "corrected_equal_universe",
      "total_return": -0.022751766007440333,
      "cagr": -0.04498588915842339,
      "mdd": 0.03225819886723702,
      "costs": 18594.00594861596,
      "final_nav": 97724.82339925597,
      "trades": 1512
    },
    {
      "seed": 5015368413594993126,
      "scenario": "learnable",
      "variant": "corrected_equal_universe",
      "total_return": 0.03000399146943411,
      "cagr": 0.06090822244296601,
      "mdd": 0.015172876533262714,
      "costs": 19141.388367254258,
      "final_nav": 103000.39914694341,
      "trades": 1512
    },
    {
      "seed": 3584306075979195116,
      "scenario": "learnable",
      "variant": "corrected_equal_universe",
      "total_return": 0.005221912988778055,
      "cagr": 0.010471094352818566,
      "mdd": 0.03103160661240656,
      "costs": 18944.136993032975,
      "final_nav": 100522.1912988778,
      "trades": 1512
    }
  ],
  "elapsed_seconds": 0.24051805003546178,
  "source_sha256": "f22cc50c64a942a22ed19a1d23b8d61269df6c9c239a84000f221acd65f8acc1",
  "phase": "post-freeze correction on already viewed learnable tapes",
  "reason": "Original benchmark forecast-ranked cash-limited purchases; invalid independent control.",
  "additional_replays": 4
}
```


## discrimination_iteration5/execution.log

```
1564008556893530022 learnable 4 3.94
1564008556893530022 null 7 5.58
1564008556893530022 reversal 10 7.3
1564008556893530022 outer_noise 13 8.82
1634635432866334191 learnable 17 10.52
1634635432866334191 null 20 11.78
1634635432866334191 reversal 23 13.47
1634635432866334191 outer_noise 26 15.01
5015368413594993126 learnable 30 17.02
5015368413594993126 null 33 18.26
5015368413594993126 reversal 36 19.65
5015368413594993126 outer_noise 39 21.65
3584306075979195116 learnable 43 23.13
3584306075979195116 null 46 24.7
3584306075979195116 reversal 49 26.39
3584306075979195116 outer_noise 52 27.84
FAIL {'four_fresh_seeds': True, 'ungated_coverage': True, 'gated_coverage': True, 'stable_false_great': True, 'middle_radii': True, 'five_tier_support': False, 'stable_false_alarm_observed': True, 'null_return': True, 'trusted_timestamp': False, 'real_pit_ready': False}

```


## discrimination_iteration5/experiment.py

```
#!/usr/bin/env python3
"""Bounded independent diagnostic. No production imports except frozen iteration2 comparator."""
import csv,gzip,hashlib,importlib.util,json,math,random,secrets,statistics as st,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
O=Path(__file__).resolve().parent
TIERS=['TERRIBLE','POOR','AVERAGE','GOOD','GREAT']; EDGES=[-.006,-.002,.002,.006]
MU=[-.012,-.004,0,.004,.012]; COST=.003; START=606; END=732; N=734
FIT=range(0,400); CAL=range(403,603)
def tier(x):return TIERS[sum(x>=e for e in EDGES)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mean(v):return st.mean(v) if v else 0.
def se(v):return st.stdev(v)/math.sqrt(len(v)) if len(v)>1 else 1.
def label(mu,r,n,nc):return tier(mu) if min(n,nc)>=100 and tier(mu-r)==tier(mu+r) else 'UNKNOWN'
def generate(seed,scenario):
    rng=random.Random(seed); sr=random.Random(seed+90000); sensors=[]; net=[]; truth=[]; gross=[]
    for i in range(N):
        common=rng.gauss(0,.003*(1.25 if scenario=='outer_noise' else 1)); fs=[]; ys=[]; ts=[]
        for j in range(24):
            z=rng.randrange(5);rng.random();rng.randrange(5) # fixed unused coarse channel, independent of sensor
            y=MU[z]+common+rng.gauss(0,.008*(1.25 if scenario=='outer_noise' else 1))
            source=sr.randrange(5) if scenario=='null' else z
            x=source+sr.gauss(0,.30);v=source+sr.gauss(0,.50)
            f=max(0,min(4,math.floor((x/.09+v/.25)/(1/.09+1/.25)+.5)))
            if scenario=='reversal' and i>=START:f=4-f
            fs.append(f);ys.append(y);ts.append(MU[z]);
        sensors.append(fs);net.append(ys);truth.append(ts);gross.append([(1+y)*(1+COST/2)/(1-COST/2)-1 for y in ys])
    prices=[[100.+j for j in range(24)] for _ in range(N)]
    for i in range(2,N):prices[i]=[p*(1+g) for p,g in zip(prices[i-1],gross[i-2])]
    # Inference receives prices and sensors only; latent truth stays evaluator-only.
    return prices,sensors,truth

def observed(prices,i,j):return prices[i+2][j]*(1-COST/2)/(prices[i+1][j]*(1+COST/2))-1

def dates(prices,sensors,indices,c):
    return [(i,mean([observed(prices,i,j) for j in range(24) if sensors[i][j]==c])) for i in indices if c in sensors[i]]

def fit(prices,sensors):
    models=[]
    # Full model adds a lag-price slope, centered separately within each sensor cell.
    for c in range(5):
        tr=dates(prices,sensors,FIT,c); ca=dates(prices,sensors,CAL,c); mu=mean([v for _,v in tr])
        rows=[(prices[i][j]/prices[max(0,i-1)][j]-1,observed(prices,i,j)) for i in FIT for j in range(24) if sensors[i][j]==c]
        center=mean([x for x,y in rows]); slope=sum((x-center)*(y-mu) for x,y in rows)/(1+sum((x-center)**2 for x,y in rows))
        # Train-only disagreement distribution; calibration changes uncertainty only.
        disagreements=sorted(abs(slope*(x-center)) for x,y in rows)
        threshold=max(.0005,disagreements[int(.99*(len(disagreements)-1))])
        bias=mean([v-mu for _,v in ca]); radius=max(2.576*se([v for _,v in tr]),abs(bias)+2.576*se([v for _,v in ca]))
        models.append(dict(mean=mu,slope=slope,center=center,threshold=threshold,radius=radius,ntrain=len(tr),ncal=len(ca),cal_bias=bias,train_dates=[i for i,v in tr],cal_dates=[i for i,v in ca]))
    return models

def monitor(prices,sensors,models,now):
    # 25 prespecified looks, 5 cells, two-sided union bound. One latch per tape.
    if now<START+22 or (now-START-22)%4:return []
    alarms=[]
    for c,m in enumerate(models):
        v=dates(prices,sensors,range(now-22,now-2),c)
        if len(v)<15:continue
        # .018 sub-Gaussian envelope exceeds sqrt(.012^2+.01068^2) even for outer noise.
        threshold=.018*math.sqrt(2*math.log(2*5*26/.05)*(1/len(v)+1/m['ntrain']))
        delta=mean([y for i,y in v])-m['mean']
        if abs(delta)>threshold:alarms.append(dict(index=now,cell=c,delta=delta,threshold=threshold,last_signal=now-3,reason='CELL_RETURN_DRIFT'))
    return alarms

def predict(prices,sensors):
    models=fit(prices,sensors);states={v:[] for v in ['candidate','ungated']};alarms=[];latched=False
    identifiable=max(m['mean'] for m in models)-min(m['mean'] for m in models)>.003
    for i in range(START,END):
        if not latched:
            found=monitor(prices,sensors,models,i)
            if found:alarms+=found;latched=True
        for v in states:
            row=[]
            for j,c in enumerate(sensors[i]):
                m=models[c];sensor=m['mean'];full=sensor+m['slope']*(prices[i][j]/prices[i-1][j]-1-m['center']);r=m['radius']+abs(full-sensor)
                lab=label(full,r,m['ntrain'],m['ncal']);reason='INTERVAL'
                if not identifiable:lab='UNKNOWN';reason='NO_IDENTIFIABLE_SIGNAL'
                if v=='candidate' and (latched or abs(full-sensor)>m['threshold']):lab='UNKNOWN';reason='DRIFT_LATCH' if latched else 'SENSOR_FULL_DISAGREEMENT'
                row.append(dict(mean=full,radius=r,label=lab,reason=reason))
            states[v].append(row)
    return states,models,alarms

def baseline(prices,sensors):
    # Unmodified iteration2 inference on the same last 126 pretest +126 test dates.
    spec=importlib.util.spec_from_file_location('i2_original',O.parent/'discrimination_iteration2/experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    offset=START-126
    # Original observed uses its own multiplicative execution costs; adapt bars exactly.
    ratio=(1-mod.s.FRICTION)*(1-mod.s.COSTS['fees'])/((1+mod.s.FRICTION)*(1+mod.s.COSTS['fees']))
    target=(1-COST/2)/(1+COST/2)
    adapted=[[100.+j for j in range(24)] for _ in range(252)]
    for i in range(1,252):adapted[i]=[adapted[i-1][j]*(prices[offset+i][j]/prices[offset+i-1][j])*target/ratio for j in range(24)]
    days=[(str(i),{t:mod.k.Bar(adapted[i][j],adapted[i][j]) for j,t in enumerate(mod.s.TICKERS)}) for i in range(252)]
    states,_,alarms=mod.predict(days,sensors[offset:offset+252])
    return [[states[i][sensors[offset+i][j]] for j in range(24)] for i in range(126,252)],alarms

def replay(prices,states,policy='tier',scale=1.):
    cash=100000.;nav=cash;peak=nav;mdd=0.;costs=0.;risks=[];trades=[];daily=[];gap_exceed=0
    # All trades hold exactly one open-to-open session. Prior sales settle one session later.
    receivable=0.;positions=[]
    for k,i in enumerate(range(START,END)):
        opening=nav;cash+=receivable;receivable=0.;pnl=0.;exit_value=0.
        for t in positions:
            exitp=prices[i+1][t['j']]; proceeds=t['shares']*exitp*(1-COST/2)
            exit_value+=proceeds;costs+=t['shares']*exitp*COST/2
            t.update(exit_index=i+1,exit_open=exitp,net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav'])
            gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        receivable=exit_value;positions=[]
        opening=cash+receivable
        available=cash
        order=sorted(range(24),key=lambda j:states[k][j]['mean'],reverse=True)
        for j in order:
            c=states[k][j]
            if policy=='cash' or (policy=='tier' and c['label'] not in ('GOOD','GREAT')):continue
            gap=[.03,.06,.12,.24][j%4];weight=min(.10*scale,.02/(gap+COST)); debit=min(available,opening*weight)
            if debit<=1e-8:continue
            entry=prices[i+1][j];shares=debit/(entry*(1+COST/2));risk=shares*entry/opening*(gap+COST)
            assert risk<=.02+1e-12
            costs+=shares*entry*COST/2;available-=debit
            positions.append(dict(signal=i,j=j,entry_index=i+1,entry_open=entry,shares=shares,debit=debit,entry_nav=opening,modeled_risk=risk,tier=c['label']))
        cash=available;nav=cash+receivable+sum(t['shares']*prices[i+1][t['j']] for t in positions)
        assert cash>=-1e-8
        peak=max(peak,nav);mdd=max(mdd,1-nav/peak);daily.append(dict(index=i,nav=nav,cash=cash,receivable=receivable,exposure=sum(t['shares']*prices[i+1][t['j']] for t in positions)/nav))
    # Explicit final horizon liquidation; settle for ending NAV.
    for t in positions:
        proceeds=t['shares']*prices[END+1][t['j']]*(1-COST/2);costs+=t['shares']*prices[END+1][t['j']]*COST/2
        t.update(exit_index=END+1,exit_open=prices[END+1][t['j']],net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav']);gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        cash+=proceeds
    nav=cash+receivable;peak=max(peak,nav);mdd=max(mdd,1-nav/peak)
    return dict(total_return=nav/100000-1,cagr=(nav/100000)**(252/126)-1,mdd=mdd,costs=costs,final_nav=nav,max_modeled_risk=max((t['modeled_risk'] for t in trades),default=0),gap_loss_exceedances=gap_exceed,max_realized_trade_loss_nav=max((t['realized_loss_nav'] for t in trades),default=0),trades=len(trades),mean_exposure=mean([d['exposure'] for d in daily])),trades,daily

def validate_pit(rows):
    required=['asset','feature','value','event_time','release_time','available_time','decision_time','revision_id','source_uri','source_sha256','vintage_id']
    for r in rows:
        if any(k not in r or r[k] is None for k in required):raise ValueError('missing provenance')
        times=[datetime.fromisoformat(r[k]) for k in ['release_time','available_time','decision_time']]
        if any(t.tzinfo is None for t in times) or not times[0]<=times[1]<=times[2]:raise ValueError('not PIT')
        if len(r['source_sha256'])!=64 or any(c not in '0123456789abcdef' for c in r['source_sha256']):raise ValueError('hash')
        if not isinstance(r['value'],(float,int)) or not math.isfinite(r['value']):raise ValueError('nonfinite feature')
    return rows

def writecsv(name,rows):
    if not rows:return
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    start=time.monotonic(); plan=json.loads((O/'preregister.json').read_text())
    if (O/'commitment.json').exists():raise SystemExit('Refusing holdout reuse: archive directory and create a new preregistered experiment.')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(O),'-p','test_*.py','-v'],capture_output=True,text=True)
    (O/'tests.log').write_text(tests.stdout+tests.stderr)
    if tests.returncode:raise SystemExit(tests.returncode)
    sources={str(p):sha(p) for p in sorted(O.glob('*.py'))}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and str(path).endswith('.py') and Path(path).is_file() and ('/opt/' in str(path)):
            sources[str(Path(path).resolve())]=sha(path);sources[str(O/'preregister.json')]=sha(O/'preregister.json')
    # Local commitment is written before OS entropy draws and generation; no trusted timestamp claimed.
    commitment=dict(utc=datetime.now(timezone.utc).isoformat(),sources=sources,preregister_sha256=sha(O/'preregister.json'))
    (O/'commitment.json').write_text(json.dumps(commitment,indent=2))
    seeds=[secrets.randbits(63) for _ in range(4)];(O/'seeds.json').write_text(json.dumps(seeds))
    scores=[];metrics=[];tiers=[];attempts=0;completed=[]
    with gzip.open(O/'opportunities.jsonl.gz','wt') as out,gzip.open(O/'replays.jsonl.gz','wt') as rp:
        for seed in seeds:
            for scenario in plan['scenarios']:
                if time.monotonic()-start>690 or attempts+3>58:break
                prices,sensors,truth=generate(seed,scenario);states,models,alarms=predict(prices,sensors)
                old,oldalarms=baseline(prices,sensors);states['iteration2']=old
                funded={}; replay_variants=[('candidate',states['candidate'],'tier',1),('iteration2',old,'tier',1),('benchmark',states['candidate'],'all',1)]
                if scenario=='learnable':replay_variants.append(('scaled',states['candidate'],'tier',1.5))
                for variant,ss,policy,scale in replay_variants:
                    if time.monotonic()-start>710 or attempts>=58:break
                    attempts+=1;metric,trades,daily=replay(prices,ss,policy,scale)
                    funded[variant]={(t['signal'],t['j']):t for t in trades}
                    metrics.append(dict(seed=seed,scenario=scenario,variant=variant,**metric));rp.write(json.dumps(dict(seed=seed,scenario=scenario,variant=variant,trades=trades,daily=daily))+'\n')
                for variant,ss in states.items():
                    confusion=[[0]*6 for _ in range(5)];realconf=[[0]*6 for _ in range(5)];rows=[];covered=0;datecovered=0;datecount=0
                    for k,i in enumerate(range(START,END)):
                        for c in range(5):
                            vals=[observed(prices,i,j) for j in range(24) if sensors[i][j]==c]
                            if vals:
                                m=models[c];datecovered+=abs(mean(vals)-m['mean'])<=m['radius'];datecount+=1
                        for j,c in enumerate(sensors[i]):
                            z=ss[k][j];actual=observed(prices,i,j);ti=TIERS.index(tier(truth[i][j]));pi=TIERS.index(z['label']) if z['label']!='UNKNOWN' else 5
                            confusion[ti][pi]+=1;realconf[TIERS.index(tier(actual))][pi]+=1
                            covered+=abs(truth[i][j]-z['mean'])<=z['radius']
                            row=dict(seed=seed,scenario=scenario,variant=variant,index=i,j=j,execution_index=i+1,exit_index=i+2,available_index=i+3,inferred_tier=z['label'],inferred_net=z['mean'],radius=z['radius'],reason=z.get('reason'),true_ev=truth[i][j],realized_net=actual,one_session_net=actual,horizon_mismatch=0.,cost_fraction=COST,eligible=True,funded=(i,j) in funded.get(variant,{}),funded_debit=funded.get(variant,{}).get((i,j),{}).get('debit',0.))
                            rows.append(row);out.write(json.dumps(row)+'\n')
                    count=len(rows);assigned=sum(sum(r[:5]) for r in confusion);false=confusion[0][4];den=sum(confusion[0])
                    score=dict(seed=seed,scenario=scenario,variant=variant,coverage=assigned/count,conditional_accuracy=sum(confusion[i][i] for i in range(5))/assigned if assigned else None,confusion_latent_individual=confusion,confusion_realized=realconf,all_opportunity_recall=[confusion[i][i]/sum(confusion[i]) for i in range(5)],false_great_on_terrible=false,false_great_rate=false/den,false_terrible_on_great=confusion[4][0],individual_latent_interval_coverage=covered/count,date_mean_predictive_interval_coverage=datecovered/datecount,alarms=alarms if variant=='candidate' else oldalarms if variant=='iteration2' else [],drift_lag=(alarms[0]['index']-START if alarms else None) if scenario=='reversal' else None,models=models if variant=='candidate' else None)
                    scores.append(score)
                    for t in TIERS+['UNKNOWN']:
                        rr=[r for r in rows if r['inferred_tier']==t];tiers.append(dict(seed=seed,scenario=scenario,variant=variant,tier=t,n=len(rr),coverage=len(rr)/count,mean_net=mean([r['realized_net'] for r in rr]) if rr else None))
                completed.append([seed,scenario]);print(seed,scenario,attempts,round(time.monotonic()-start,2),flush=True)
    # Conditional cell EV coverage: independent evaluator Monte Carlo from the known sensor channel.
    # Not used in inference. Fixed analytical integration via Gaussian CDF rounding probabilities.
    sd=1/math.sqrt(1/.09+1/.25);normal=st.NormalDist()
    celltrue=[]
    for c in range(5):
        weights=[normal.cdf((c+.5-z)/sd) if c==0 else 1-normal.cdf((c-.5-z)/sd) if c==4 else normal.cdf((c+.5-z)/sd)-normal.cdf((c-.5-z)/sd) for z in range(5)]
        celltrue.append(sum(w*m for w,m in zip(weights,MU))/sum(weights))
    for s in scores:
        if s['variant']=='candidate':
            target=[0.]*5 if s['scenario']=='null' else list(reversed(celltrue)) if s['scenario']=='reversal' else celltrue
            s['conditional_mean_interval_coverage']=mean([abs(m['mean']-v)<=m['radius'] for m,v in zip(s['models'],target)])
    paired=[]
    for m in metrics:
        if m['variant']!='candidate':continue
        for comparator in ['iteration2','scaled','benchmark']:
            other=next((x for x in metrics if x['seed']==m['seed'] and x['scenario']==m['scenario'] and x['variant']==comparator),None)
            if other:paired.append(dict(seed=m['seed'],scenario=m['scenario'],comparator=comparator,return_delta=m['total_return']-other['total_return'],cagr_delta=m['cagr']-other['cagr'],mdd_delta=m['mdd']-other['mdd'],cost_delta=m['costs']-other['costs']))
    stable=[s for s in scores if s['variant']=='candidate' and s['scenario'] in ['learnable','null','outer_noise']];learn=[s for s in stable if s['scenario']=='learnable'];ung=[s for s in scores if s['variant']=='ungated' and s['scenario']=='learnable']
    stable_alarms=sum(bool(s['alarms']) for s in stable)
    checks=dict(four_fresh_seeds=len(set(s['seed'] for s in learn))>=4,ungated_coverage=all(s['coverage']>=.30 for s in ung),gated_coverage=all(s['coverage']>=.15 for s in learn),stable_false_great=all(s['false_great_rate']<=.01 for s in stable),middle_radii=sum(all(m['radius']<.002 for m in s['models'][1:4]) for s in learn)>=3,five_tier_support=all(all(next(t['n'] for t in tiers if t['seed']==s['seed'] and t['scenario']==s['scenario'] and t['variant']=='candidate' and t['tier']==tiername)>=20 for tiername in TIERS) for s in learn),stable_false_alarm_observed=stable_alarms/max(1,len(stable))<=.05,null_return=all(m['total_return']<=.02 for m in metrics if m['variant']=='candidate' and m['scenario']=='null'),trusted_timestamp=False,real_pit_ready=False)
    report=dict(status='PASS' if all(checks.values()) else 'FAIL',execution_status='COMPLETE' if len(completed)==16 and attempts==52 else 'INCOMPLETE_BUDGET',checks=checks,elapsed_seconds=time.monotonic()-start,portfolio_replays=attempts,total_replays_including_phase_a=attempts+6,seeds=seeds,completed=completed,preregister_sha256=sha(O/'preregister.json'),design_unchanged=all(sha(p)==h for p,h in sources.items()),fresh_test='Fresh OS-entropy seed tapes generated after local source freeze; now evaluated and no longer untouched. DGP adapted from prior work; no trusted public timestamp.',stable_false_alarms=dict(seed_scenario_units=len(stable),alarmed=stable_alarms,observed_rate=stable_alarms/max(1,len(stable)),upper95_if_zero=1-.05**(1/max(1,len(stable))) if not stable_alarms else None,independent_seeds=4,power='Four independent seeds cannot establish <=5% nuisance probability; scenarios within seed are paired.'),discrimination=scores,portfolio_runs=metrics,paired=paired,real_pit_audit=dict(status='BLOCKED',real_rows=0,reason='No release-timestamped real predictor dataset supplied or acquired.',adapter='validate_pit; schema in pit_schema.json',missing=['revision histories','release and availability timestamps','coverage/missingness audit','independent regime OOS rank IC >0.1 evidence']),sgov=dict(status='UNAVAILABLE_REAL_DATA',comparison='Cash zero-yield control has return/CAGR/MDD/costs 0; no fabricated SGOV series'),engineering_blocker='Real PIT information absent; narrow-band support and drift safety require measured validation. No production promotion.',recommended_next_decision='Review failed checks; acquire provenance-complete PIT data and independent regime evaluation before any production or alpha claim. No optimization reruns in this experiment.')
    (O/'report.json').write_text(json.dumps(report,indent=2));writecsv('tier_metrics.csv',tiers);writecsv('metrics.csv',metrics);writecsv('paired.csv',paired)
    (O/'checksums.json').write_text(json.dumps({str(p.relative_to(O)):sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'},indent=2))
    print(report['status'],checks,flush=True)
if __name__=='__main__':main()

```


## discrimination_iteration5/finalize.py

```
"""Read-only-result analysis and documentation. Executes no tapes or portfolio replays."""
import csv,gzip,hashlib,json,statistics as st
from pathlib import Path
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def avg(xs):return st.mean(xs) if xs else None
def ranks(xs):
    order=sorted(range(len(xs)),key=xs.__getitem__);r=[0.]*len(xs);i=0
    while i<len(xs):
        j=i+1
        while j<len(xs) and xs[order[j]]==xs[order[i]]:j+=1
        for k in range(i,j):r[order[k]]=(i+j-1)/2
        i=j
    return r
def corr(x,y):
    x=ranks(x);y=ranks(y);mx=avg(x);my=avg(y);den=(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))**.5
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/den if den else None

def main():
    if (O/'raw_report.json').exists():r=json.loads((O/'raw_report.json').read_text())
    else:
        r=json.loads((O/'report.json').read_text());(O/'raw_report.json').write_text(json.dumps(r,indent=2))
    original=json.loads((O/'commitment.json').read_text());assert all(sha(p)==h for p,h in original['sources'].items())
    correction=json.loads((O/'corrected_benchmark_results.json').read_text());paired=[]
    for b in correction['runs']:
        c=next(x for x in r['portfolio_runs'] if x['seed']==b['seed'] and x['scenario']=='learnable' and x['variant']=='candidate')
        paired.append(dict(seed=b['seed'],scenario='learnable',candidate_return=c['total_return'],benchmark_return=b['total_return'],return_delta=c['total_return']-b['total_return'],cagr_delta=c['cagr']-b['cagr'],mdd_delta=c['mdd']-b['mdd'],cost_delta=c['costs']-b['costs']))
    with (O/'corrected_benchmark_paired.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
    audits={};funded={};tierstats={};daily={}
    with gzip.open(O/'opportunities.jsonl.gz','rt') as f:
        for line in f:
            z=json.loads(line);key=(z['seed'],z['scenario'],z['variant']);a=audits.setdefault(key,dict(n=0,false_great=0,false_great_net_sum=0.,false_great_loss_sum=0.,horizon_mismatch_max=0.,funded=0))
            a['n']+=1;a['funded']+=z['funded'];a['horizon_mismatch_max']=max(a['horizon_mismatch_max'],abs(z['horizon_mismatch']))
            if z['true_ev']==-.012 and z['inferred_tier']=='GREAT':a['false_great']+=1;a['false_great_net_sum']+=z['realized_net'];a['false_great_loss_sum']+=min(0,z['realized_net'])
            if z['funded']:funded[(z['seed'],z['scenario'],z['variant'],z['index'],z['j'])]=z
            tierstats.setdefault((z['scenario'],z['variant'],z['inferred_tier']),[]).append(z['realized_net'])
            daily.setdefault((*key,z['index']),[[],[]]);daily[(*key,z['index'])][0].append(z['inferred_net']);daily[(*key,z['index'])][1].append(z['realized_net'])
    maxerr=0.;cashmin=1e99;riskmax=0.;tradecount=0
    with gzip.open(O/'replays.jsonl.gz','rt') as f:
        for line in f:
            z=json.loads(line);cashmin=min(cashmin,min(d['cash'] for d in z['daily']))
            if z['variant'] not in ['candidate','iteration2']:continue
            for t in z['trades']:
                row=funded[(z['seed'],z['scenario'],z['variant'],t['signal'],t['j'])];assert t['exit_index']==t['entry_index']+1
                maxerr=max(maxerr,abs(t['net']-row['realized_net']));riskmax=max(riskmax,t['modeled_risk']);tradecount+=1
    assert maxerr<1e-12 and cashmin>=-1e-8 and riskmax<=.02
    cells=[]
    for key,a in audits.items():cells.append(dict(seed=key[0],scenario=key[1],variant=key[2],mean_daily_spearman=avg([v for k,xy in daily.items() if k[:3]==key and (v:=corr(*xy)) is not None]),**a))
    with (O/'ledger_audit.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(cells[0]));w.writeheader();w.writerows(cells)
    for score in r['discrimination']:
        if score['variant']=='iteration2':
            score['date_mean_predictive_interval_coverage']=None
            score['date_mean_interval_note']='Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis.'
    r['post_freeze_benchmark_correction']=dict(reason=correction['reason'],additional_replays=4,evaluated_scenarios=['learnable'],incomplete_scenarios=['null','reversal','outer_noise'],untouched_test=False,runs=correction['runs'],paired=paired,invalid_original_rows="All variant=benchmark rows in metrics.csv and corresponding paired comparisons are invalid as independent controls; retained as evidence of ranking confound.")
    r['total_replays_including_phase_a']=62;r['compute_accounting']=dict(initial_phase_a_seconds=1.968,runner_seconds=r['elapsed_seconds'],benchmark_correction_seconds=correction['elapsed_seconds'],total_measured_seconds=1.968+r['elapsed_seconds']+correction['elapsed_seconds'],phase_a_replays=6,phase_b_replays=52,post_freeze_control_correction_replays=4,limit=64,stopped=True)
    r['artifact_audit']=dict(funded_trade_matches=tradecount,max_net_ledger_error=maxerr,min_cash=cashmin,max_modeled_risk=riskmax,frozen_sources_match=True)
    r['recommendation_status']={
      'P1_gate':'IMPLEMENTED sensor/full disagreement; no price-only veto, train-only threshold; stable coverage recovers.',
      'P2_independent_dates':'IMPLEMENTED 734 sessions,400 fit/200 cal dates, original bands. Radii pass but per-seed five-tier support fails.',
      'P3_outer_holdout':'PARTIAL four OS entropy seeds after local hash commitment, separate noise variant; trusted public timestamp unavailable. All evaluated tapes now viewed.',
      'P4_disjoint_calibration':'IMPLEMENTED embargoed chronological disjoint ranges; mutation tests show calibration cannot alter point coefficients. Statistical correlation need not literally be zero in finite samples.',
      'P5_sequential_monitor':'IMPLEMENTED cell/look union bound with stated DGP subGaussian envelope; stable0/12 but only4 independent seeds. Reversal22-session lag is unsafe.',
      'P6_horizon_ledger':'IMPLEMENTED all-opportunity one-session open-to-exit ledger, matched funded horizons, costs/cash/final liquidation/risk/gap audits. Original variable holding manager not replayed; synthetic one-session harness only.',
      'P7_real_PIT':'ADAPTER/AUDIT ONLY; no accepted real rows or real OOS IC. Local provisional artifacts lack complete revision/release provenance. NO alpha claim.'}
    r['real_pit_audit']['local_evidence']=[dict(path=str(p),sha256=sha(p),reason=reason) for p,reason in [(O.parents[2]/'pilot_2019_sample.csv','Annual summarized provisional observations; no release/revision provenance.'),(O.parents[2]/'reports/offline-provisional-2019/observations.csv','Monthly provisional observations; no release/vintage/source-hash fields.'),(O.parents[2]/'manifest.json','Explicit certified=false, PIT coverage unverified;2019/2020 contaminated.')]]
    r['limitations']=['Four seeds do not establish a <=5% stable alarm probability;0/12 paired scenario units is not12 independent seeds.','Conditional mean intervals and latent-individual/realized tier confusion are different estimands. Date_mean_predictive_interval_coverage is a diagnostic hit rate for date means, not nominal prediction coverage.','Sensor/full gate threshold calibrated only on fit distribution; no formal conformal reliability guarantee.','Benchmark control correction is post-freeze, with learnable-only coverage; no independent benchmark evidence for other scenarios.','No real SGOV data, SGOV-relative return unavailable. Cash zero is a synthetic control.','Source freeze manifests cover new core files; imported original dependency hashes were not committed comprehensively before seed generation.','Injected sensors and cost-grossup DGP cannot establish real alpha. Fresh seeds do not make the inherited DGP untouched.','Original baseline estimator unmodified, but its portfolio policy uses new one-session harness and has126-date warmup rather than candidate400 fit/200 cal dates.','CAGR/MDD from synthetic126-session windows and open marks only; no intraday risk or aggregate2% risk guarantee.']
    r['engineering_blocker']='FAIL: five-tier support missing on2/4 stable seeds; reversal442 false GREAT before22-session latch and negative net return. Real PIT information and trusted timestamp absent; corrected independent benchmark coverage incomplete.'
    r['recommended_next_decision']='Do not promote or optimize this bundle. Retain as gate-repair evidence; first specify acceptable reversal exposure and acquire provenance-complete real PIT predictors. Use a new externally committed protocol for any future validation.'
    r['execution_status']='COMPLETE_PLANNED_RUN_WITH_INCOMPLETE_CORRECTED_BENCHMARK_COVERAGE'
    (O/'report.json').write_text(json.dumps(r,indent=2))
    # Human report is assembled below from measured aggregates, not a success claim.
    learn=[s for s in r['discrimination'] if s['variant']=='candidate' and s['scenario']=='learnable'];rev=[s for s in r['discrimination'] if s['variant']=='candidate' and s['scenario']=='reversal']
    lines=['# Iteration5: FAIL — bounded engineering experiment','',f"Nine unit/integration tests passed twice. Total62 portfolio replays:6 test probes,52 planned runs,4 post-freeze control corrections. Measured compute {r['compute_accounting']['total_measured_seconds']:.2f}s, below720s. No GA or production edits; every new file is in this directory. Existing unrelated workspace changes were left alone.",'','The gate repair restores stable coverage; it does not certify the bundle. Original bands remain ±0.2%/±0.6%. All three middle radii are below0.002 on4/4 learnable seeds, yet only2/4 seeds support every tier. Radius alone is insufficient when a fitted center approaches a boundary. No widened bands or forced classes were used.','',f"Stable learnable coverage ranges {min(s['coverage'] for s in learn):.1%}–{max(s['coverage'] for s in learn):.1%}; conditional individual-latent tier accuracy {min(s['conditional_accuracy'] for s in learn):.1%}–{max(s['conditional_accuracy'] for s in learn):.1%}. Stable false GREAT/TERRIBLE count0. Conditional cell-mean interval coverage20/20 learnable cells, and20/20 outer-noise cells; this small synthetic sample establishes no nominal coverage guarantee.",'',f"Reversal: {sum(s['false_great_on_terrible'] for s in rev)} true-TERRIBLE opportunities labeled GREAT before the22-session return-drift latch on every seed. Mean candidate reversal return {avg([m['total_return'] for m in r['portfolio_runs'] if m['variant']=='candidate' and m['scenario']=='reversal']):.2%}. Zero stable alarms across12 seed/scenario units, but only4 independent seeds; even0/4 gives a52.7% one-sided95% upper bound on seed alarm probability. Reported0/12 upper bound is descriptive and assumes independence that paired scenarios do not have.",'','## Measured portfolio results','', 'Arithmetic means of per-seed metrics. Dollar costs on initial$100,000; all entry/exit costs paid, one-session horizon, T+1 sale proceeds, terminal liquidation. These large injected-signal returns are not real alpha.','', '| Scenario / policy | Return | CAGR | MDD | Costs |','|---|---:|---:|---:|---:|']
    for scen in ['learnable','null','reversal','outer_noise']:
        for var in ['candidate','iteration2','scaled']:
            ms=[m for m in r['portfolio_runs'] if m['scenario']==scen and m['variant']==var]
            if ms:lines.append(f"| {scen} / {var} | {avg([m['total_return'] for m in ms]):.2%} | {avg([m['cagr'] for m in ms]):.2%} | {avg([m['mdd'] for m in ms]):.2%} | ${avg([m['costs'] for m in ms]):,.0f} |")
    bs=correction['runs'];lines.append(f"| learnable / corrected equal universe | {avg([m['total_return'] for m in bs]):.2%} | {avg([m['cagr'] for m in bs]):.2%} | {avg([m['mdd'] for m in bs]):.2%} | ${avg([m['costs'] for m in bs]):,.0f} |")
    lines+=['','Original benchmark rows are INVALID independent controls: purchase ranking used forecasts under cash scarcity. The corrected equal-notional control accepts prices only and checks equal entries across all24 names. It ran on four already viewed learnable tapes, consuming four spare replay slots; other scenarios remain incomplete. Corrected comparisons are descriptive after evaluation. Cash control is0 return/CAGR/MDD/cost; real SGOV comparison is unavailable.','',f"Maximum measured per-trade modeled risk {riskmax:.4%}; no gap-loss exceedances in the primary replays. An explicit50% gap test demonstrates realized losses can exceed modeled risk. Funded candidate/baseline ledger net reconciliation error {maxerr:.2g}; no horizon mismatch. Tier metrics cover all opportunities, including unfunded and abstentions; these sums are not attainable portfolio returns.",'','## Method and evidence','', 'Read the full external review and original experiment code; all original reports were parsed. 734 synthetic sessions,24 assets, random class/sensor draws with original sensor noise and original noise law. Outer variant increases return noise25%. Fit signals0–399, calibration403–602, test606–731. Outcomes are usable at signal+3; fit/cal/test execution intervals are disjoint. Each date-cell mean counts once; under this iid-date DGP dates are independent. Cross-cell dependence remains and is covered by union bounds. More complex serial dependence is not validated.','', 'Sensor-cell date means and full-model lag-price slopes fit only training data. The99th percentile disagreement threshold and identifiability filter use training only. Independent calibration widens uncertainty through bias and SE, never changes coefficients. Approximate cell intervals use2.576SE with no individual-class guarantee. The monitor uses a conservative0.018 subGaussian envelope for the prescribed synthetic law, five cells and at most26 looks, with total alpha0.05. This envelope is not a learned real-market guarantee.','', 'Iteration2 predict is imported unchanged on the last126 warmup+126 test sessions of the same fresh tapes. Bar conversion preserves exact net returns under its inherited multiplicative costs. Its calibration pooling violation is retained and explicitly uncertified. Candidate has a longer fit, so this is a paired engineering comparison, not a pure gate-only ablation. The full-model ungated ablation isolates the gate on the candidate fit. Scaled15% allocations are learnable-only; see paired.csv for incremental returns/MDD/costs.','', 'Confusion matrices for individual latent and realized tiers, all-opportunity recalls, GREAT→TERRIBLE and TERRIBLE→GREAT, per-cell diagnostics, conditional mean interval coverage, drift reasons/lags, and seed-level metrics are in report.json. tier_metrics.csv holds support and net returns; ledger_audit.csv includes daily rank IC and realized loss sums for false GREAT. opportunities.jsonl.gz includes every test opportunity, actual funded flags/debits and open-to-exit outcomes; replays.jsonl.gz contains funded trades and daily cash/NAV.','', 'preregister.json and core Python SHA256 hashes were committed locally before seeds.json was drawn from OS entropy. No trusted external/public timestamp or hardware RNG attestation exists. Fresh-seed tapes were untouched at generation; they are now viewed. The inherited DGP and developer choices were informed by earlier work. No untouched test remains, and the benchmark correction is explicitly post-freeze. Original core hashes still match commitment.json. No outcome-based tuning or reruns of the candidate occurred.','', 'PIT readiness: local policy/manifest and provisional CSV headers show no complete release/revision/vintage provenance. No real rows were admitted or fabricated. pit_schema.json and validate_pit provide a strict row adapter, not source authenticity or statistical certification. Real OOS IC>0.1 cannot be assessed.','', '## Recommendations implemented versus blocked','']
    for k,v in r['recommendation_status'].items():lines.append(f'- **{k}:** {v}')
    lines+=['','## Run and inspect','', '```bash','PYTHONPATH=/opt/Momentum-Trading-System_v5-alpha python3 -m unittest discover -s experiments/mts_v5_planted_signal_20261101/discrimination_iteration5 -p "test_*.py" -v','```','', 'Tests are rerunnable but execute three synthetic portfolio probes per invocation. The archived accounting includes exactly two test invocations; no more runs are scheduled. experiment.py refuses holdout reuse while commitment.json exists. Its archived frozen runner preserves the original benchmark bug for audit; use corrected_benchmark.replay_equal for a valid price-only equal-universe control. A future full experiment needs a new directory/protocol/commitment and its own replay budget; do not delete this commitment to claim a fresh test. finalize.py analyzes archived results without running portfolios. checksums.json covers artifacts; raw_report.json preserves the pre-correction machine output.','', '**Engineering blocker:** '+r['engineering_blocker'],'','**Next decision:** '+r['recommended_next_decision']]
    (O/'README.md').write_text('\n'.join(lines)+'\n')
    (O/'checksums.json').write_text(json.dumps({p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'},indent=2))
    print(r['status'],r['artifact_audit'],r['compute_accounting'])
if __name__=='__main__':main()

```


## discrimination_iteration5/ledger_audit.csv

```
seed,scenario,variant,mean_daily_spearman,n,false_great,false_great_net_sum,false_great_loss_sum,horizon_mismatch_max,funded
1564008556893530022,learnable,candidate,0.6552380952380953,3024,0,0.0,0.0,0.0,713
1564008556893530022,learnable,ungated,0.6552380952380953,3024,0,0.0,0.0,0.0,0
1564008556893530022,learnable,iteration2,0.6801134416516426,3024,0,0.0,0.0,0.0,309
1564008556893530022,null,candidate,-0.023409247757073846,3024,0,0.0,0.0,0.0,0
1564008556893530022,null,ungated,-0.023409247757073846,3024,0,0.0,0.0,0.0,0
1564008556893530022,null,iteration2,-0.025703478646004953,3024,0,0.0,0.0,0.0,0
1564008556893530022,reversal,candidate,-0.6604485852311939,3024,108,-1.1163889214882037,-1.1489339551609028,0.0,129
1564008556893530022,reversal,ungated,-0.6604485852311939,3024,611,-7.303081271322431,-7.4970162778261775,0.0,0
1564008556893530022,reversal,iteration2,0.5997741823456091,3024,29,-0.26594524841073086,-0.2710445359871193,0.0,310
1564008556893530022,outer_noise,candidate,0.5748930296756384,3024,0,0.0,0.0,0.0,700
1564008556893530022,outer_noise,ungated,0.5748930296756384,3024,0,0.0,0.0,0.0,0
1564008556893530022,outer_noise,iteration2,0.5956649313113657,3024,0,0.0,0.0,0.0,271
1634635432866334191,learnable,candidate,0.6496894409937888,3024,0,0.0,0.0,0.0,711
1634635432866334191,learnable,ungated,0.6496894409937888,3024,0,0.0,0.0,0.0,0
1634635432866334191,learnable,iteration2,0.6657500339268952,3024,0,0.0,0.0,0.0,276
1634635432866334191,null,candidate,-0.017218771566597655,3024,0,0.0,0.0,0.0,0
1634635432866334191,null,ungated,-0.017218771566597655,3024,0,0.0,0.0,0.0,0
1634635432866334191,null,iteration2,-0.0035352167769280075,3024,0,0.0,0.0,0.0,0
1634635432866334191,reversal,candidate,-0.6406832298136647,3024,120,-1.5431927654262152,-1.582932625404382,0.0,125
1634635432866334191,reversal,ungated,-0.6406832298136647,3024,570,-6.718616722735391,-6.911289023294453,0.0,0
1634635432866334191,reversal,iteration2,0.5123461750436619,3024,0,0.0,0.0,0.0,280
1634635432866334191,outer_noise,candidate,0.5733540372670808,3024,0,0.0,0.0,0.0,706
1634635432866334191,outer_noise,ungated,0.5733540372670808,3024,0,0.0,0.0,0.0,0
1634635432866334191,outer_noise,iteration2,0.5886177893208699,3024,0,0.0,0.0,0.0,138
5015368413594993126,learnable,candidate,0.6463285024154589,3024,0,0.0,0.0,0.0,688
5015368413594993126,learnable,ungated,0.6463285024154589,3024,0,0.0,0.0,0.0,0
5015368413594993126,learnable,iteration2,0.6638560520552114,3024,0,0.0,0.0,0.0,360
5015368413594993126,null,candidate,-0.021228433402346446,3024,0,0.0,0.0,0.0,0
5015368413594993126,null,ungated,-0.021228433402346446,3024,0,0.0,0.0,0.0,0
5015368413594993126,null,iteration2,-0.015125216343812477,3024,0,0.0,0.0,0.0,0
5015368413594993126,reversal,candidate,-0.6415527950310559,3024,105,-1.1914398608938193,-1.2180077745884477,0.0,121
5015368413594993126,reversal,ungated,-0.6415527950310559,3024,612,-6.8535390780227745,-7.081613980097569,0.0,0
5015368413594993126,reversal,iteration2,0.5841207567554222,3024,25,-0.2960333805048765,-0.29924864506245474,0.0,65
5015368413594993126,outer_noise,candidate,0.5584679089026915,3024,0,0.0,0.0,0.0,537
5015368413594993126,outer_noise,ungated,0.5584679089026915,3024,0,0.0,0.0,0.0,0
5015368413594993126,outer_noise,iteration2,0.5725205411521717,3024,0,0.0,0.0,0.0,346
3584306075979195116,learnable,candidate,0.6409799861973775,3024,0,0.0,0.0,0.0,710
3584306075979195116,learnable,ungated,0.6409799861973775,3024,0,0.0,0.0,0.0,0
3584306075979195116,learnable,iteration2,0.6666079574885745,3024,0,0.0,0.0,0.0,75
3584306075979195116,null,candidate,-0.029054520358868186,3024,0,0.0,0.0,0.0,0
3584306075979195116,null,ungated,-0.029054520358868186,3024,0,0.0,0.0,0.0,0
3584306075979195116,null,iteration2,-0.026260530904559293,3024,0,0.0,0.0,0.0,0
3584306075979195116,reversal,candidate,-0.650103519668737,3024,109,-1.2321849536776264,-1.263067703776362,0.0,124
3584306075979195116,reversal,ungated,-0.650103519668737,3024,591,-6.957543008039263,-7.148309329052395,0.0,0
3584306075979195116,reversal,iteration2,0.5808179277050077,3024,9,-0.08996003299597188,-0.09156020780098728,0.0,222
3584306075979195116,outer_noise,candidate,0.5611387163561077,3024,0,0.0,0.0,0.0,560
3584306075979195116,outer_noise,ungated,0.5611387163561077,3024,0,0.0,0.0,0.0,0
3584306075979195116,outer_noise,iteration2,0.580449172036713,3024,0,0.0,0.0,0.0,75

```


## discrimination_iteration5/metrics.csv

```
seed,scenario,variant,total_return,cagr,mdd,costs,final_nav,max_modeled_risk,gap_loss_exceedances,max_realized_trade_loss_nav,trades,mean_exposure
1564008556893530022,learnable,candidate,0.8565803518951918,2.446890603043274,0.001963545471879824,26390.734316483435,185658.03518951917,0.019970044932601103,0,0.0018333001423728027,713,0.49860300716718614
1564008556893530022,learnable,iteration2,0.39237711548683607,0.938714031731442,0.0009689169948781107,10231.393264712864,139237.7115486836,0.019970044932601103,0,0.001338466798717441,309,0.22515157460859517
1564008556893530022,learnable,benchmark,0.5456474145097245,1.3890259299805963,0.005304813657442509,23877.426114519654,154564.74145097245,0.019970044932601103,0,0.0020559366010415568,690,0.5
1564008556893530022,learnable,scaled,0.8947400188097325,2.5900397388791054,0.0056742683080288625,26408.760006435867,189474.00188097326,0.019970044932601103,0,0.0021428887034773483,541,0.4991352816116626
1564008556893530022,null,candidate,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
1564008556893530022,null,iteration2,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
1564008556893530022,null,benchmark,-0.01290983758249431,-0.025653011258582215,0.0453760384892129,19082.702029076776,98709.01624175056,0.019970044932601103,0,0.004165642239230085,692,0.5
1564008556893530022,reversal,candidate,-0.09335387657175176,-0.1779928068725296,0.09335387657175176,3147.85109849186,90664.61234282482,0.019970044932601103,0,0.00328233948439627,129,0.08740442927292283
1564008556893530022,reversal,iteration2,0.2934610056762552,0.6730413732050295,0.02710753263629373,9518.584637368103,129346.10056762552,0.019970044932601107,0,0.002305920459099081,310,0.2244827378252593
1564008556893530022,reversal,benchmark,-0.3582405588908163,-0.5881448197472281,0.35874663143746455,15493.885177912698,64175.944110918375,0.019970044932601103,0,0.004165642239230081,692,0.5
1564008556893530022,outer_noise,candidate,0.8397485025644511,2.38467455268814,0.00567006677947679,26056.05774051141,183974.85025644512,0.019970044932601103,0,0.002591625177966036,700,0.4942277626474625
1564008556893530022,outer_noise,iteration2,0.3464292042015571,0.8128716019268383,0.0010291813614353718,8873.051981066159,134642.92042015571,0.019970044932601103,0,0.001973083498396808,271,0.20006704184456253
1564008556893530022,outer_noise,benchmark,0.5418507955059377,1.3773038756022928,0.007384105546087483,23874.498674003204,154185.07955059377,0.019970044932601103,0,0.002669920751301966,690,0.5
1634635432866334191,learnable,candidate,0.8532868241113967,2.434672052424907,0.003995693570929326,26113.89853369401,185328.68241113966,0.019970044932601103,0,0.0017168536902495927,711,0.49857151938894406
1634635432866334191,learnable,iteration2,0.3192149412476988,0.7403280612111693,0.0006958697755835574,8776.029399967545,131921.49412476987,0.019970044932601103,0,0.0014903225805685998,276,0.19958026076788485
1634635432866334191,learnable,benchmark,0.48105557509876995,1.193525616531148,0.007368431805399589,22990.851335466683,148105.557509877,0.019970044932601103,0,0.0027305899921181436,691,0.5
1634635432866334191,learnable,scaled,0.8635214315554163,2.472712125866348,0.00639667660381904,25879.79063826065,186352.14315554162,0.019970044932601103,0,0.002575280535374393,539,0.4988630045802842
1634635432866334191,null,candidate,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
1634635432866334191,null,iteration2,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
1634635432866334191,null,benchmark,-0.05224318281853413,-0.10175701548605742,0.061156581700016255,18211.529512313893,94775.68171814659,0.019970044932601103,0,0.0033806980629516393,695,0.5
1634635432866334191,reversal,candidate,-0.11608906596128998,-0.21870146068681517,0.11608906596128998,3115.2372166834834,88391.093403871,0.0199700449326011,0,0.0032217073400820483,125,0.0874371708236961
1634635432866334191,reversal,iteration2,0.3277627983841651,0.7629540487729491,0.0006481066970512872,8953.867364098383,132776.27983841652,0.019970044932601103,0,0.001490322580568601,280,0.20275200936874727
1634635432866334191,reversal,benchmark,-0.3677335509493157,-0.6002391374048384,0.3677335509493157,15054.907708128032,63226.64490506843,0.019970044932601103,0,0.003380698062951627,692,0.5
1634635432866334191,outer_noise,candidate,0.8567061080069394,2.447357571510276,0.005598346966235068,25928.747486069988,185670.61080069395,0.019970044932601103,0,0.002246067112811993,706,0.4915491463397735
1634635432866334191,outer_noise,iteration2,0.15613973447898277,0.3366590856411329,0.0010003859442387908,4117.223624134512,115613.97344789827,0.019970044932601103,0,0.0008791720831319065,138,0.10073127024621309
1634635432866334191,outer_noise,benchmark,0.4672185277845873,1.1527302082743716,0.010762430028337766,22841.138351069356,146721.85277845873,0.019970044932601103,0,0.0035132374901476683,691,0.5
5015368413594993126,learnable,candidate,0.8611443345975147,2.4638582342044257,0.0020496628915205317,25731.06284980566,186114.43345975148,0.019970044932601103,0,0.0019394342118703978,688,0.4870375040799655
5015368413594993126,learnable,iteration2,0.4899570339954422,1.2199719631524952,0.000994720088371981,12336.450302365996,148995.70339954423,0.019970044932601103,0,0.0014630736802362623,360,0.2652163828735844
5015368413594993126,learnable,benchmark,0.5741608338490665,1.4779823308243882,0.0017752091754812405,24081.679072921157,157416.08338490664,0.019970044932601103,0,0.002677556047913142,692,0.5
5015368413594993126,learnable,scaled,0.9660857845289041,2.8654933121266364,0.0014977533699451762,27030.699789999755,196608.57845289042,0.019970044932601103,0,0.002909151317805578,531,0.4962504967922432
5015368413594993126,null,candidate,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
5015368413594993126,null,iteration2,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
5015368413594993126,null,benchmark,0.013446916680871723,0.027074652929965692,0.030896027009147176,18881.47104106435,101344.69166808718,0.019970044932601103,0,0.0031560749335864196,691,0.5
5015368413594993126,reversal,candidate,-0.09932318634435422,-0.18878127734311312,0.09932318634435422,3041.6181921266652,90067.68136556458,0.019970044932601103,0,0.0030038860486007236,121,0.0849147521816611
5015368413594993126,reversal,iteration2,0.015109808669263147,0.030447923656548026,0.026284545213899002,1766.579904717346,101510.98086692631,0.019970044932601103,0,0.002317184721766586,65,0.047104875506691894
5015368413594993126,reversal,benchmark,-0.3287406821718124,-0.5494109282288362,0.3287406821718124,15531.624670052439,67125.93178281876,0.019970044932601103,0,0.003408127944546198,690,0.5
5015368413594993126,outer_noise,candidate,0.7992162433793686,2.237179090440167,0.001522190839828963,20479.54793575007,179921.62433793687,0.019970044932601103,0,0.002724292764837972,537,0.39607254635474404
5015368413594993126,outer_noise,iteration2,0.4889905679446782,1.2170929114282152,0.001522190839829185,11852.516870654441,148899.05679446782,0.019970044932601103,0,0.0021288421002953707,346,0.2557156431102246
5015368413594993126,outer_noise,benchmark,0.6018000908631125,1.5657635310890754,0.0035572180682594823,24365.500441176115,160180.00908631124,0.019970044932601103,0,0.0021300965856244627,692,0.5
3584306075979195116,learnable,candidate,0.8954416618367764,2.592699093426561,0.0013262361874661899,26398.728940425906,189544.16618367765,0.019970044932601103,0,0.0017494203512605736,710,0.49456477157997963
3584306075979195116,learnable,iteration2,0.08770191605740218,0.183095458194944,0.0009689169948781107,2149.2696734320807,108770.19160574023,0.019970044932601103,0,0.0007297366295642403,75,0.05444557961260058
3584306075979195116,learnable,benchmark,0.5109318564790837,1.2829150749233302,0.00539072752005243,23661.73148542008,151093.18564790837,0.019970044932601103,0,0.0018248886295925857,692,0.5
3584306075979195116,learnable,scaled,0.9151154109356636,2.667667037203276,0.0016668108299155993,26381.854557174407,191511.54109356637,0.019970044932601103,0,0.0026241305268908575,534,0.4974383645997597
3584306075979195116,null,candidate,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
3584306075979195116,null,iteration2,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0
3584306075979195116,null,benchmark,0.00638376346489844,0.012808279365772668,0.0334943355219397,18789.50833969456,100638.37634648984,0.019970044932601103,0,0.003004547721390877,691,0.5
3584306075979195116,reversal,candidate,-0.10362440974389797,-0.19651080119302466,0.10362440974389797,3112.1634844739756,89637.5590256102,0.019970044932601103,0,0.002923011157214521,124,0.08745282346965874
3584306075979195116,reversal,iteration2,0.1962153471843755,0.43093115683943606,0.009289614086369413,6583.174756888624,119621.53471843754,0.019970044932601103,0,0.0026713974023778427,222,0.15982432498341242
3584306075979195116,reversal,benchmark,-0.3295449775783236,-0.5504900629095494,0.3295449775783236,15375.41778562892,67045.50224216764,0.019970044932601103,0,0.0033777103126367515,691,0.5
3584306075979195116,outer_noise,candidate,0.8755190363051262,2.517571655542909,0.0015761012824380138,21619.948379440422,187551.90363051262,0.019970044932601103,0,0.0024867754390757177,560,0.4076901962653527
3584306075979195116,outer_noise,iteration2,0.0943484538067405,0.1975985383492036,0.0015761012824380138,2152.4201129854046,109434.84538067406,0.019970044932601103,0,0.0011590843672022368,75,0.05442187919443346
3584306075979195116,outer_noise,benchmark,0.5210568954545496,1.3136140792098328,0.007696845614057368,23716.578978991987,152105.68954545495,0.019970044932601103,0,0.002381110786990742,692,0.5

```


## discrimination_iteration5/paired.csv

```
seed,scenario,comparator,return_delta,cagr_delta,mdd_delta,cost_delta
1564008556893530022,learnable,iteration2,0.4642032364083557,1.5081765713118322,0.0009946284770017133,16159.34105177057
1564008556893530022,learnable,scaled,-0.03815966691454076,-0.14314913583583122,-0.0037107228361490385,-18.025689952432003
1564008556893530022,learnable,benchmark,0.31093293738546723,1.057864673062678,-0.0033412681855626847,2513.3082019637804
1564008556893530022,null,iteration2,0.0,0.0,0.0,0.0
1564008556893530022,null,benchmark,0.01290983758249431,0.025653011258582215,-0.0453760384892129,-19082.702029076776
1564008556893530022,reversal,iteration2,-0.386814882248007,-0.8510341800775592,0.06624634393545803,-6370.733538876244
1564008556893530022,reversal,benchmark,0.26488668231906454,0.4101520128746985,-0.2653927548657128,-12346.034079420839
1564008556893530022,outer_noise,iteration2,0.493319298362894,1.5718029507613018,0.004640885418041418,17183.005759445252
1564008556893530022,outer_noise,benchmark,0.2978977070585134,1.0073706770858473,-0.0017140387666106927,2181.5590665082054
1634635432866334191,learnable,iteration2,0.5340718828636979,1.6943439912137377,0.0032998237953457688,17337.869133726464
1634635432866334191,learnable,scaled,-0.010234607444019606,-0.038040073441441,-0.002400983032889714,234.10789543336068
1634635432866334191,learnable,benchmark,0.3722312490126267,1.241146435893759,-0.0033727382344702628,3123.0471982273266
1634635432866334191,null,iteration2,0.0,0.0,0.0,0.0
1634635432866334191,null,benchmark,0.05224318281853413,0.10175701548605742,-0.061156581700016255,-18211.529512313893
1634635432866334191,reversal,iteration2,-0.4438518643454551,-0.9816555094597643,0.1154409592642387,-5838.6301474149
1634635432866334191,reversal,benchmark,0.2516444849880257,0.3815376767180232,-0.2516444849880257,-11939.670491444549
1634635432866334191,outer_noise,iteration2,0.7005663735279566,2.1106984858691433,0.004597961021996277,21811.523861935475
1634635432866334191,outer_noise,benchmark,0.3894875802223521,1.2946273632359047,-0.005164083062102698,3087.609135000632
5015368413594993126,learnable,iteration2,0.3711873006020725,1.2438862710519305,0.0010549428031485508,13394.612547439665
5015368413594993126,learnable,scaled,-0.10494144993138943,-0.40163507792221065,0.0005519095215753556,-1299.6369401940938
5015368413594993126,learnable,benchmark,0.28698350074844825,0.9858759033800375,0.00027445371603929125,1649.3837768845042
5015368413594993126,null,iteration2,0.0,0.0,0.0,0.0
5015368413594993126,null,benchmark,-0.013446916680871723,-0.027074652929965692,-0.030896027009147176,-18881.47104106435
5015368413594993126,reversal,iteration2,-0.11443299501361737,-0.21922920099966114,0.07303864113045522,1275.0382874093193
5015368413594993126,reversal,benchmark,0.22941749582745818,0.3606296508857231,-0.22941749582745818,-12490.006477925774
5015368413594993126,outer_noise,iteration2,0.3102256754346904,1.020086179011952,-2.220446049250313e-16,8627.031065095629
5015368413594993126,outer_noise,benchmark,0.1974161525162561,0.6714155593510918,-0.0020350272284305193,-3885.952505426045
3584306075979195116,learnable,iteration2,0.8077397457793742,2.409603635231617,0.0003573191925880792,24249.459266993825
3584306075979195116,learnable,scaled,-0.019673749098887194,-0.07496794377671501,-0.0003405746424494094,16.87438325149924
3584306075979195116,learnable,benchmark,0.38450980535769275,1.3097840185032306,-0.00406449133258624,2736.997455005825
3584306075979195116,null,iteration2,0.0,0.0,0.0,0.0
3584306075979195116,null,benchmark,-0.00638376346489844,-0.012808279365772668,-0.0334943355219397,-18789.50833969456
3584306075979195116,reversal,iteration2,-0.29983975692827347,-0.6274419580324607,0.09433479565752856,-3471.0112724146484
3584306075979195116,reversal,benchmark,0.2259205678344256,0.3539792617165247,-0.2259205678344256,-12263.254301154946
3584306075979195116,outer_noise,iteration2,0.7811705824983857,2.3199731171937055,0.0,19467.528266455018
3584306075979195116,outer_noise,benchmark,0.3544621408505766,1.2039575763330763,-0.006120744331619354,-2096.630599551565

```


## discrimination_iteration5/pit_schema.json

```
{
  "schema_version": 1,
  "adapter": "experiment.validate_pit(rows)",
  "required_row_fields": ["asset","feature","value","event_time","release_time","available_time","decision_time","revision_id","source_uri","source_sha256","vintage_id"],
  "constraints": ["finite numeric feature","timezone-aware release_time <= available_time <= decision_time","64-character lowercase hex source SHA256","one explicit source vintage and revision ID per row"],
  "dataset_readiness_requirements": ["original release archive and immutable snapshot hashes","revision chain with superseded availability dates","missingness by asset, feature, date and regime including unavailable values","corporate-action and universe membership timing","licensing/access and reproducible retrieval manifest","disjoint fit/calibration/test regime episodes","OOS rank IC with uncertainty and dependence-aware sampling"],
  "current_status": "No accepted real predictor rows. Adapter validation alone does not certify source authenticity or predictive information."
}

```


## discrimination_iteration5/preregister.json

```
{
  "version": 1,
  "scope": "Independent synthetic discrimination engineering experiment. No GA, production changes, optimization or real alpha claims.",
  "history_sessions": 734,
  "fit_signals": [
    0,
    399
  ],
  "calibration_signals": [
    403,
    602
  ],
  "test_signals": [
    606,
    731
  ],
  "outcome_available": "signal + 3; entry open signal+1; exit open signal+2",
  "independence": "iid date-common and individual innovations; cell means count one observation per date, not per stock. Shared dates induce cross-cell dependence accounted for by Bonferroni.",
  "primary_edges": [
    -0.006,
    -0.002,
    0.002,
    0.006
  ],
  "widened_band_ablation": "Not warranted; omitted. No bands changed or forced classes.",
  "point_fit": "400 dates; sensor cell date means plus train-only centered lag-price slope; no calibration point adjustment",
  "uncertainty": "max(2.576 SE_train, abs(cal_bias)+2.576 SE_cal) plus sensor/full displacement. Simultaneous approximate 99% cell mean diagnostic; Gaussian approximation, measured coverage; not individual prediction intervals.",
  "reliability": "Training-only 99th percentile sensor/full disagreement with 5bp floor; minimum 100 dates in each fit/cal cell; identifiable range >30bp. Calibration only widens intervals.",
  "drift": "26 maximum prespecified looks; first test+22 then every4 sessions; trailing 20 matured signals, >=15 cell dates; five cells, two-sided alpha .05 union bound across all looks. SubGaussian envelope .018 for date-cell means, conservative relative to DGP .012 bounded conditional component plus <=.01068 Gaussian innovation. Frozen training baseline uncertainty included. Latch until end, no refit.",
  "seeds": "4 distinct OS entropy 63bit draws after source/preregistration local commitment, no seed filtering or reruns",
  "scenarios": [
    "learnable",
    "null",
    "reversal",
    "outer_noise"
  ],
  "outer_noise": "separate prespecified DGP variant multiplies common and idiosyncratic noise by1.25; sensor unchanged",
  "portfolio": "Three paired replays per seed/scenario: candidate10%, unchanged iteration2 estimator10%, equal-universe daily benchmark. Plus candidate15% allocation ablation on four learnable tapes only:52 phase B replays. All one-session open-to-open, entry/exit15bp each, sales unavailable until following open, nonnegative cash, final liquidation. Per-position modeled risk<=2% with cyclic gap3/6/12/24%. Zero yield cash measured in tests; no invented SGOV.",
  "baseline": "Unmodified original iteration2 predict on last126 pretest+126 test sessions with exact net-cost conversion. This baseline uses pooled rolling calibration and is not certified independently calibrated. Paired outcome tape; baseline has less history by original design.",
  "acceptance": {
    "stable_ungated_coverage": 0.3,
    "stable_gated_coverage": 0.15,
    "stable_false_great_max": 0.01,
    "middle_radii": "all3 <.002 on >=3 of4 learnable seeds",
    "five_tiers": ">=20 assigned per tier per learnable seed",
    "stable_alarm_seed_scenario_rate_max": 0.05,
    "null_candidate_return_max": 0.02
  },
  "limits": {
    "max_compute_seconds": 720,
    "max_portfolio_replays": 64,
    "optimization_runs": 0,
    "phase_a_replays": 6,
    "phase_b_replays": 52,
    "total_replays_planned": 58
  },
  "process_limits": "Local timestamp only, trusted public commitment unavailable. Fresh tapes do not erase prior DGP adaptation. No real PIT dataset provided; audit reports missing evidence, no invented data.",
  "pass": "All acceptance checks plus trusted timestamp and real PIT readiness; unmet prerequisites FAIL. Report engineering subchecks separately. Four seeds insufficient to prove5% false alarm rate. No threshold adaptation after results."
}

```


## discrimination_iteration5/report.json

```json
{"status":"FAIL","execution_status":"COMPLETE_PLANNED_RUN_WITH_INCOMPLETE_CORRECTED_BENCHMARK_COVERAGE","checks":{"four_fresh_seeds":true,"ungated_coverage":true,"gated_coverage":true,"stable_false_great":true,"middle_radii":true,"five_tier_support":false,"stable_false_alarm_observed":true,"null_return":true,"trusted_timestamp":false,"real_pit_ready":false},"elapsed_seconds":27.84563373005949,"portfolio_replays":52,"total_replays_including_phase_a":62,"seeds":[1564008556893530022,1634635432866334191,5015368413594993126,3584306075979195116],"completed":[[1564008556893530022,"learnable"],[1564008556893530022,"null"],[1564008556893530022,"reversal"],[1564008556893530022,"outer_noise"],[1634635432866334191,"learnable"],[1634635432866334191,"null"],[1634635432866334191,"reversal"],[1634635432866334191,"outer_noise"],[5015368413594993126,"learnable"],[5015368413594993126,"null"],[5015368413594993126,"reversal"],[5015368413594993126,"outer_noise"],[3584306075979195116,"learnable"],[3584306075979195116,"null"],[3584306075979195116,"reversal"],[3584306075979195116,"outer_noise"]],"preregister_sha256":"f6253010529818262e3b4f52511d307ae0cafb3129629c164e4293db06495b0c","design_unchanged":true,"fresh_test":"Fresh OS-entropy seed tapes generated after local source freeze; now evaluated and no longer untouched. DGP adapted from prior work; no trusted public timestamp.","stable_false_alarms":{"seed_scenario_units":12,"alarmed":0,"observed_rate":0.0,"upper95_if_zero":0.22092219194555585,"independent_seeds":4,"power":"Four independent seeds cannot establish <=5% nuisance probability; scenarios within seed are paired."},"discrimination":[{"seed":1564008556893530022,"scenario":"learnable","variant":"candidate","coverage":1.0,"conditional_accuracy":0.9520502645502645,"confusion_latent_individual":[[611,11,0,0,0,0],[14,519,19,0,0,0],[0,17,576,23,0,0],[0,0,20,588,23,0],[0,0,0,18,585,0]],"confusion_realized":[[478,223,154,88,17,0],[66,100,107,64,17,0],[46,88,104,116,54,0],[22,71,99,102,69,0],[13,65,151,259,451,0]],"all_opportunity_recall":[0.9823151125401929,0.9402173913043478,0.935064935064935,0.9318541996830428,0.9701492537313433],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9520502645502645,"date_mean_predictive_interval_coverage":0.2746031746031746,"alarms":[],"drift_lag":null,"models":[{"mean":-0.011563538364309667,"slope":0.0015018779149096211,"center":0.0032517029473314515,"threshold":0.0005,"radius":0.0013464137480056564,"ntrain":398,"ncal":199,"cal_bias":-0.00042229498399287886,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"69258a31756109176352d7632ed41ffc972f0149250ff7f825e959c4cc7c3f82"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"9772f09ca6107c7fa3748470e588596f6819e56fffa993ee2161dede3d23336e"}},{"mean":-0.003927869730736104,"slope":0.0025225226011882465,"center":0.0033503486734594327,"threshold":0.0005,"radius":0.0014584072034673394,"ntrain":398,"ncal":197,"cal_bias":0.0005300449649495801,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"94dfba9f1128ac2fceba7873ecfdbfbe758f7223528f1547f9af64a02f0f193b"},"cal_dates":{"count":197,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"379f76b09df6158577914949ed555b28fb1e1e69fa26287bf492ef57f207856c"}},{"mean":7.20851793757841e-05,"slope":0.0010596990473499674,"center":0.0031491960396893936,"threshold":0.0005,"radius":0.0017862091512938104,"ntrain":399,"ncal":200,"cal_bias":0.0007383452206480645,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"dd4869b3f06ba07c038ccf3c970d061d5398c81cfb540d74ae66452242e192a3"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.004028238114238777,"slope":-0.005424727426604572,"center":0.003267190902322784,"threshold":0.0005,"radius":0.0014581517770964315,"ntrain":400,"ncal":199,"cal_bias":0.0005553031589630829,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"982d1db75be8ba35e952681cd11c1ae8326a06224762578eb3dda813fc4194cf"}},{"mean":0.012140241496694104,"slope":0.003613446570092122,"center":0.0028736006684556012,"threshold":0.0005,"radius":0.0015042032645560305,"ntrain":399,"ncal":200,"cal_bias":0.0005662150087593325,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"9afdca40c51e59e4ea64cdcb6afa2f5b7adbe26e9c6da3afeb7ad5910589fff8"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}}],"conditional_mean_interval_coverage":1},{"seed":1564008556893530022,"scenario":"learnable","variant":"ungated","coverage":1.0,"conditional_accuracy":0.9520502645502645,"confusion_latent_individual":[[611,11,0,0,0,0],[14,519,19,0,0,0],[0,17,576,23,0,0],[0,0,20,588,23,0],[0,0,0,18,585,0]],"confusion_realized":[[478,223,154,88,17,0],[66,100,107,64,17,0],[46,88,104,116,54,0],[22,71,99,102,69,0],[13,65,151,259,451,0]],"all_opportunity_recall":[0.9823151125401929,0.9402173913043478,0.935064935064935,0.9318541996830428,0.9701492537313433],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9520502645502645,"date_mean_predictive_interval_coverage":0.2746031746031746,"alarms":[],"drift_lag":null,"models":null},{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration2","coverage":0.24768518518518517,"conditional_accuracy":0.9692923898531375,"confusion_latent_individual":[[319,1,0,0,0,302],[8,60,0,0,0,484],[0,1,5,1,0,609],[0,0,0,43,11,577],[0,0,0,1,299,303]],"confusion_realized":[[254,27,0,6,9,664],[27,13,4,8,7,295],[23,8,0,8,24,345],[13,7,0,7,31,305],[10,7,1,16,239,666]],"all_opportunity_recall":[0.5128617363344051,0.10869565217391304,0.008116883116883116,0.06814580031695722,0.49585406301824214],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.953042328042328,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":50,"cells":[0]},{"index":135,"cells":[1]},{"index":235,"cells":[2]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":1564008556893530022,"scenario":"null","variant":"candidate","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,622],[0,0,0,0,0,552],[0,0,0,0,0,616],[0,0,0,0,0,631],[0,0,0,0,0,603]],"confusion_realized":[[0,0,0,0,0,960],[0,0,0,0,0,354],[0,0,0,0,0,408],[0,0,0,0,0,363],[0,0,0,0,0,939]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.2037037037037037,"date_mean_predictive_interval_coverage":0.1376,"alarms":[],"drift_lag":null,"models":[{"mean":-6.435706638603189e-05,"slope":0.0029098507293619643,"center":0.0038143222752767976,"threshold":0.0005,"radius":0.0013344486898590818,"ntrain":399,"ncal":200,"cal_bias":0.00013414737869056503,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"8ccd9b86375385649d59de84e62c55f4eb5d3b0f7e85ae94e198a6c597544a28"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":-5.0114507568322524e-05,"slope":0.0037042493109960798,"center":0.00278674999692854,"threshold":0.0005,"radius":0.0016856424691744551,"ntrain":399,"ncal":200,"cal_bias":0.0004639999880577436,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"80aa135899b96f51c01e6425a8ec17e8504e116afbe39ee23ba9a2d675380b81"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.00043268547079204807,"slope":-0.0035719426421115964,"center":0.003520577726687814,"threshold":0.0005,"radius":0.0013488360352900452,"ntrain":398,"ncal":199,"cal_bias":0.00011365016814890857,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"de44e0bd590e0445042cc2222a309256d2779ec874fd831277889e387b456ba5"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"906c213e26816ca3b3ff83fa23e7961a40c36dfc0f89c72848179f056ca4f18b"}},{"mean":7.012530809212448e-05,"slope":-0.006790887893414259,"center":0.0028534191386110157,"threshold":0.0005,"radius":0.0012453904047208732,"ntrain":400,"ncal":200,"cal_bias":1.974050365823003e-05,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.00022061399564712994,"slope":-0.0004989690609501361,"center":0.0029267914781345925,"threshold":0.0005,"radius":0.0021813564345846137,"ntrain":397,"ncal":199,"cal_bias":0.001045023052596927,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"7229dfaf74d82cbed0c48b6aa898c8d5b7b160254c6d0d450cf41c024a659941"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"b0869a1c834bfb93f682ed97c3541fab0cfb93fed261afa939c90d7d13194c92"}}],"conditional_mean_interval_coverage":1},{"seed":1564008556893530022,"scenario":"null","variant":"ungated","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,622],[0,0,0,0,0,552],[0,0,0,0,0,616],[0,0,0,0,0,631],[0,0,0,0,0,603]],"confusion_realized":[[0,0,0,0,0,960],[0,0,0,0,0,354],[0,0,0,0,0,408],[0,0,0,0,0,363],[0,0,0,0,0,939]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.2037037037037037,"date_mean_predictive_interval_coverage":0.1376,"alarms":[],"drift_lag":null,"models":null},{"seed":1564008556893530022,"scenario":"null","variant":"iteration2","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,622],[0,0,0,0,0,552],[0,0,0,0,0,616],[0,0,0,0,0,631],[0,0,0,0,0,603]],"confusion_realized":[[0,0,0,0,0,960],[0,0,0,0,0,354],[0,0,0,0,0,408],[0,0,0,0,0,363],[0,0,0,0,0,939]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.3683862433862434,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":46,"cells":[4]},{"index":146,"cells":[4]},{"index":186,"cells":[2]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":1564008556893530022,"scenario":"reversal","variant":"candidate","coverage":0.1746031746031746,"conditional_accuracy":0.20454545454545456,"confusion_latent_individual":[[0,0,0,0,108,514],[0,0,0,94,1,457],[0,4,108,3,0,501],[1,105,2,0,0,523],[98,4,0,0,0,501]],"confusion_realized":[[1,16,24,34,74,811],[3,9,15,18,19,290],[8,15,22,16,10,337],[9,19,21,14,5,295],[78,54,28,15,1,763]],"all_opportunity_recall":[0.0,0.0,0.17532467532467533,0.0,0.0],"false_great_on_terrible":108,"false_great_rate":0.17363344051446947,"false_terrible_on_great":98,"individual_latent_interval_coverage":0.19047619047619047,"date_mean_predictive_interval_coverage":0.07936507936507936,"alarms":[{"index":628,"cell":0,"delta":0.024490399442385492,"threshold":0.01706337763346477,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.022953208316379807,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}],"drift_lag":22,"models":[{"mean":-0.011563538364309667,"slope":0.0015018779149096211,"center":0.0032517029473314515,"threshold":0.0005,"radius":0.0013464137480056564,"ntrain":398,"ncal":199,"cal_bias":-0.00042229498399287886,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"69258a31756109176352d7632ed41ffc972f0149250ff7f825e959c4cc7c3f82"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"9772f09ca6107c7fa3748470e588596f6819e56fffa993ee2161dede3d23336e"}},{"mean":-0.003927869730736104,"slope":0.0025225226011882465,"center":0.0033503486734594327,"threshold":0.0005,"radius":0.0014584072034673394,"ntrain":398,"ncal":197,"cal_bias":0.0005300449649495801,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"94dfba9f1128ac2fceba7873ecfdbfbe758f7223528f1547f9af64a02f0f193b"},"cal_dates":{"count":197,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"379f76b09df6158577914949ed555b28fb1e1e69fa26287bf492ef57f207856c"}},{"mean":7.20851793757841e-05,"slope":0.0010596990473499674,"center":0.0031491960396893936,"threshold":0.0005,"radius":0.0017862091512938104,"ntrain":399,"ncal":200,"cal_bias":0.0007383452206480645,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"dd4869b3f06ba07c038ccf3c970d061d5398c81cfb540d74ae66452242e192a3"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.004028238114238777,"slope":-0.005424727426604572,"center":0.003267190902322784,"threshold":0.0005,"radius":0.0014581517770964315,"ntrain":400,"ncal":199,"cal_bias":0.0005553031589630829,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"982d1db75be8ba35e952681cd11c1ae8326a06224762578eb3dda813fc4194cf"}},{"mean":0.012140241496694104,"slope":0.003613446570092122,"center":0.0028736006684556012,"threshold":0.0005,"radius":0.0015042032645560305,"ntrain":399,"ncal":200,"cal_bias":0.0005662150087593325,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"9afdca40c51e59e4ea64cdcb6afa2f5b7adbe26e9c6da3afeb7ad5910589fff8"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}}],"conditional_mean_interval_coverage":0.2},{"seed":1564008556893530022,"scenario":"reversal","variant":"ungated","coverage":1.0,"conditional_accuracy":0.19047619047619047,"confusion_latent_individual":[[0,0,0,11,611,0],[0,0,19,519,14,0],[0,23,576,17,0,0],[23,588,20,0,0,0],[585,18,0,0,0,0]],"confusion_realized":[[17,88,154,223,478,0],[17,64,107,100,66,0],[54,116,104,88,46,0],[69,102,99,71,22,0],[451,259,151,65,13,0]],"all_opportunity_recall":[0.0,0.0,0.935064935064935,0.0,0.0],"false_great_on_terrible":611,"false_great_rate":0.9823151125401929,"false_terrible_on_great":585,"individual_latent_interval_coverage":0.19047619047619047,"date_mean_predictive_interval_coverage":0.07936507936507936,"alarms":[],"drift_lag":22,"models":null},{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration2","coverage":0.2328042328042328,"conditional_accuracy":0.875,"confusion_latent_individual":[[282,0,0,0,29,311],[8,20,0,17,1,506],[0,0,8,2,0,606],[0,0,0,37,11,583],[20,0,0,0,269,314]],"confusion_realized":[[228,7,0,13,28,684],[22,5,4,9,12,302],[18,2,0,9,29,350],[11,3,1,9,31,308],[31,3,3,16,210,676]],"all_opportunity_recall":[0.4533762057877814,0.036231884057971016,0.012987012987012988,0.058637083993660855,0.4461028192371476],"false_great_on_terrible":29,"false_great_rate":0.04662379421221865,"false_terrible_on_great":20,"individual_latent_interval_coverage":0.8591269841269841,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":50,"cells":[0]},{"index":132,"cells":[4]},{"index":235,"cells":[2]}],"drift_lag":22,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":1564008556893530022,"scenario":"outer_noise","variant":"candidate","coverage":0.6636904761904762,"conditional_accuracy":0.9586447433981067,"confusion_latent_individual":[[611,8,0,0,0,3],[14,384,0,0,0,154],[0,13,0,15,0,588],[0,0,0,344,23,264],[0,0,0,10,585,8]],"confusion_realized":[[451,165,0,66,30,300],[67,64,0,44,35,128],[43,51,0,50,55,147],[38,51,0,48,67,132],[26,74,0,161,421,310]],"all_opportunity_recall":[0.9823151125401929,0.6956521739130435,0.0,0.5451664025356577,0.9701492537313433],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9520502645502645,"date_mean_predictive_interval_coverage":0.2777777777777778,"alarms":[],"drift_lag":null,"models":[{"mean":-0.011502394958258578,"slope":0.0021480943812187416,"center":0.003281094733449208,"threshold":0.0005,"radius":0.0017021024369144554,"ntrain":398,"ncal":199,"cal_bias":-0.0005504638484404875,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"69258a31756109176352d7632ed41ffc972f0149250ff7f825e959c4cc7c3f82"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"9772f09ca6107c7fa3748470e588596f6819e56fffa993ee2161dede3d23336e"}},{"mean":-0.003879373426989068,"slope":0.0034607603757435897,"center":0.0034120644293612955,"threshold":0.0005,"radius":0.0018197464844389678,"ntrain":398,"ncal":197,"cal_bias":0.000664166473022816,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"94dfba9f1128ac2fceba7873ecfdbfbe758f7223528f1547f9af64a02f0f193b"},"cal_dates":{"count":197,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"379f76b09df6158577914949ed555b28fb1e1e69fa26287bf492ef57f207856c"}},{"mean":8.82595951172062e-05,"slope":0.0014697256688351436,"center":0.0031936686649242972,"threshold":0.0005,"radius":0.002240570372259717,"ntrain":399,"ncal":200,"cal_bias":0.0009323182678274712,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"dd4869b3f06ba07c038ccf3c970d061d5398c81cfb540d74ae66452242e192a3"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.004000864111052434,"slope":-0.007277905276538139,"center":0.0033348442764556735,"threshold":0.0005,"radius":0.0018467300724014295,"ntrain":400,"ncal":199,"cal_bias":0.0007228593616814389,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"982d1db75be8ba35e952681cd11c1ae8326a06224762578eb3dda813fc4194cf"}},{"mean":0.01223021295810954,"slope":0.0036228033612487973,"center":0.002832578640221548,"threshold":0.0005,"radius":0.0018710658386050982,"ntrain":399,"ncal":200,"cal_bias":0.0007038418006913671,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"9afdca40c51e59e4ea64cdcb6afa2f5b7adbe26e9c6da3afeb7ad5910589fff8"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}}],"conditional_mean_interval_coverage":1},{"seed":1564008556893530022,"scenario":"outer_noise","variant":"ungated","coverage":0.6636904761904762,"conditional_accuracy":0.9586447433981067,"confusion_latent_individual":[[611,8,0,0,0,3],[14,384,0,0,0,154],[0,13,0,15,0,588],[0,0,0,344,23,264],[0,0,0,10,585,8]],"confusion_realized":[[451,165,0,66,30,300],[67,64,0,44,35,128],[43,51,0,50,55,147],[38,51,0,48,67,132],[26,74,0,161,421,310]],"all_opportunity_recall":[0.9823151125401929,0.6956521739130435,0.0,0.5451664025356577,0.9701492537313433],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9520502645502645,"date_mean_predictive_interval_coverage":0.2777777777777778,"alarms":[],"drift_lag":null,"models":null},{"seed":1564008556893530022,"scenario":"outer_noise","variant":"iteration2","coverage":0.1927910052910053,"conditional_accuracy":0.9691252144082333,"confusion_latent_individual":[[290,0,0,0,0,332],[7,3,0,0,0,542],[0,0,0,0,0,616],[0,0,0,0,11,620],[0,0,0,0,272,331]],"confusion_realized":[[221,2,0,0,15,774],[25,0,0,0,18,295],[17,1,0,0,20,308],[17,0,0,0,30,289],[17,0,0,0,200,775]],"all_opportunity_recall":[0.4662379421221865,0.005434782608695652,0.0,0.0,0.45107794361525705],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9563492063492064,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":50,"cells":[0]},{"index":89,"cells":[3]},{"index":135,"cells":[1]},{"index":235,"cells":[2]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":1634635432866334191,"scenario":"learnable","variant":"candidate","coverage":0.8062169312169312,"conditional_accuracy":0.9593929450369155,"confusion_latent_individual":[[570,0,0,0,0,16],[20,0,9,0,0,563],[0,0,595,15,0,7],[0,0,19,607,24,0],[0,0,0,12,567,0]],"confusion_realized":[[447,0,151,89,12,254],[69,0,98,73,21,86],[42,0,117,108,40,99],[19,0,97,115,89,70],[13,0,160,249,429,77]],"all_opportunity_recall":[0.9726962457337884,0.0,0.9643435980551054,0.9338461538461539,0.9792746113989638],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9596560846560847,"date_mean_predictive_interval_coverage":0.2025518341307815,"alarms":[],"drift_lag":null,"models":[{"mean":-0.011842268408095807,"slope":0.007265912757075921,"center":0.0027877560111765095,"threshold":0.0005,"radius":0.0014451665088908842,"ntrain":399,"ncal":199,"cal_bias":0.00048001403667675854,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"c9a4b63932b91aaa016376da9da4b4f82e2be4f4cfd5ef06e649baaf874697ac"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"822efda3e926b14ad1b60974e3980abdd6f96e1169ff901fee627d1703d5fa3d"}},{"mean":-0.004462572736095863,"slope":0.000948661726295992,"center":0.002858138365833879,"threshold":0.0005,"radius":0.0018279110270090536,"ntrain":398,"ncal":199,"cal_bias":0.0008251191955606222,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"66899c9bf8be32affa1961d4a67efcce85c9b82096c65daf58448f2ecfc980a9"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"284ee412fbaa3bf9ae2cd15e3ecc261c490514f127ed4a1dc69356d7a1429681"}},{"mean":-0.00036861207984510507,"slope":-0.005082479421957443,"center":0.0027713372846730456,"threshold":0.0005,"radius":0.0010399359607285144,"ntrain":397,"ncal":200,"cal_bias":6.955173759666701e-05,"train_dates":{"count":397,"first":1,"last":399,"contiguous":false,"canonical_json_sha256":"6b1f9125a5653353fcfb2ff0f5433df0bd977679290d6d995100620a0e020158"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.0038130101694972365,"slope":0.005240853493102743,"center":0.002797050480622816,"threshold":0.0005,"radius":0.0013914756464946387,"ntrain":396,"ncal":198,"cal_bias":0.0004520191852532839,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"6a4dae04f3b3c12e413a8cacdb88a7c8a4b548140e8a47cf848e2de1359a10ad"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"de0bf1f2848a6aa985add53f0546c9c35b1384bfdc2dcee2bf71814fa4928c52"}},{"mean":0.011822708862789461,"slope":0.009360030832603318,"center":0.002882485000590901,"threshold":0.0005,"radius":0.0012556586937010807,"ntrain":400,"ncal":197,"cal_bias":0.0002543434438663819,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":197,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"cda952cd0e36cf4e5dc80c161eef6bcb209d6e7d39c8e790ac71eb5dd0bcb1d7"}}],"conditional_mean_interval_coverage":1},{"seed":1634635432866334191,"scenario":"learnable","variant":"ungated","coverage":0.8062169312169312,"conditional_accuracy":0.9593929450369155,"confusion_latent_individual":[[570,0,0,0,0,16],[20,0,9,0,0,563],[0,0,595,15,0,7],[0,0,19,607,24,0],[0,0,0,12,567,0]],"confusion_realized":[[447,0,151,89,12,254],[69,0,98,73,21,86],[42,0,117,108,40,99],[19,0,97,115,89,70],[13,0,160,249,429,77]],"all_opportunity_recall":[0.9726962457337884,0.0,0.9643435980551054,0.9338461538461539,0.9792746113989638],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9596560846560847,"date_mean_predictive_interval_coverage":0.2025518341307815,"alarms":[],"drift_lag":null,"models":null},{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration2","coverage":0.2294973544973545,"conditional_accuracy":0.9596541786743515,"confusion_latent_individual":[[262,0,0,0,0,324],[12,74,0,0,0,506],[0,1,3,2,0,611],[0,0,1,61,10,578],[0,0,0,2,266,311]],"confusion_realized":[[206,23,0,9,6,709],[33,17,1,5,8,283],[24,15,3,13,12,339],[3,9,0,12,45,321],[8,11,0,26,205,678]],"all_opportunity_recall":[0.447098976109215,0.125,0.004862236628849271,0.09384615384615384,0.459412780656304],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9616402116402116,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":45,"cells":[1]},{"index":123,"cells":[1]},{"index":149,"cells":[2]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":1634635432866334191,"scenario":"null","variant":"candidate","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,586],[0,0,0,0,0,592],[0,0,0,0,0,617],[0,0,0,0,0,650],[0,0,0,0,0,579]],"confusion_realized":[[0,0,0,0,0,953],[0,0,0,0,0,347],[0,0,0,0,0,406],[0,0,0,0,0,390],[0,0,0,0,0,928]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.20403439153439154,"date_mean_predictive_interval_coverage":0.23763955342902712,"alarms":[],"drift_lag":null,"models":[{"mean":-0.00064611563700878,"slope":0.010705919133239913,"center":0.0032079198277865572,"threshold":0.0005,"radius":0.002061507165004193,"ntrain":399,"ncal":198,"cal_bias":0.0007845576800150658,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"697146e297276eff87a0fb86ba65e72607123f128318a8591c8b7ab0bb8c9771"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"21cea686f2242309115ab582e52e1263cf59b39af5027aed203e5fc4d7af0b76"}},{"mean":-0.00021751063272405695,"slope":0.002327348108169383,"center":0.002334913269348608,"threshold":0.0005,"radius":0.0023085803024501797,"ntrain":399,"ncal":199,"cal_bias":0.0011750490696532056,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5157766669e922efe45bd6035aec766dd759c370562a4f133feeee13e707e4d4"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"5e004aa2104f57ccfe3db46f7e006ccb7c041d4467c0c615ab7fa9409e5bfa4f"}},{"mean":-0.00011297001686326955,"slope":0.00028918686705534845,"center":0.002841184940640555,"threshold":0.0005,"radius":0.0013164750915372321,"ntrain":398,"ncal":199,"cal_bias":-2.8071655136392075e-05,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"436afbacef9f765a82bb675561301c402a354d70f2361f1bbf10b3f33bb5d1d1"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"eb95863d7f2d1eb04b269d7904c355ed0f829e34fe103d1f0e1fee36b6548fe0"}},{"mean":3.311534067140957e-05,"slope":-0.0029083235582362636,"center":0.003115082281693125,"threshold":0.0005,"radius":0.0015816232217224346,"ntrain":397,"ncal":199,"cal_bias":0.00026378794546844727,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"854fd2c49a96d01eaa80dcd5474519a8f43cc24fb38a4eb7c806c338e96f8c82"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"c3c5618081fee34670a7756d967fafbbef8704e537a97a781a8136e4d3dad491"}},{"mean":-0.00012886292860874756,"slope":0.008717372640717475,"center":0.0025937172140255626,"threshold":0.0005,"radius":0.0014217191260975915,"ntrain":400,"ncal":199,"cal_bias":0.00012718866947364972,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"120301ce444ae9debe9019bd3d7115ae4662de809da54df6c0b08b0fe864377d"}}],"conditional_mean_interval_coverage":1},{"seed":1634635432866334191,"scenario":"null","variant":"ungated","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,586],[0,0,0,0,0,592],[0,0,0,0,0,617],[0,0,0,0,0,650],[0,0,0,0,0,579]],"confusion_realized":[[0,0,0,0,0,953],[0,0,0,0,0,347],[0,0,0,0,0,406],[0,0,0,0,0,390],[0,0,0,0,0,928]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.20403439153439154,"date_mean_predictive_interval_coverage":0.23763955342902712,"alarms":[],"drift_lag":null,"models":null},{"seed":1634635432866334191,"scenario":"null","variant":"iteration2","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,586],[0,0,0,0,0,592],[0,0,0,0,0,617],[0,0,0,0,0,650],[0,0,0,0,0,579]],"confusion_realized":[[0,0,0,0,0,953],[0,0,0,0,0,347],[0,0,0,0,0,406],[0,0,0,0,0,390],[0,0,0,0,0,928]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.37466931216931215,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":62,"cells":[0]},{"index":105,"cells":[2]},{"index":132,"cells":[3]},{"index":162,"cells":[0]},{"index":215,"cells":[0]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":1634635432866334191,"scenario":"reversal","variant":"candidate","coverage":0.14186507936507936,"conditional_accuracy":0.2540792540792541,"confusion_latent_individual":[[0,0,0,3,120,463],[0,0,0,78,4,510],[0,0,109,2,0,506],[1,0,6,0,0,643],[106,0,0,0,0,473]],"confusion_realized":[[3,0,23,38,94,795],[2,0,17,15,19,294],[8,0,22,13,6,357],[16,0,16,10,3,345],[78,0,37,7,2,804]],"all_opportunity_recall":[0.0,0.0,0.1766612641815235,0.0,0.0],"false_great_on_terrible":120,"false_great_rate":0.20477815699658702,"false_terrible_on_great":106,"individual_latent_interval_coverage":0.19675925925925927,"date_mean_predictive_interval_coverage":0.05422647527910686,"alarms":[{"index":628,"cell":0,"delta":0.023786640078661186,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.024722636901506195,"threshold":0.01706133643749677,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}],"drift_lag":22,"models":[{"mean":-0.011842268408095807,"slope":0.007265912757075921,"center":0.0027877560111765095,"threshold":0.0005,"radius":0.0014451665088908842,"ntrain":399,"ncal":199,"cal_bias":0.00048001403667675854,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"c9a4b63932b91aaa016376da9da4b4f82e2be4f4cfd5ef06e649baaf874697ac"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"822efda3e926b14ad1b60974e3980abdd6f96e1169ff901fee627d1703d5fa3d"}},{"mean":-0.004462572736095863,"slope":0.000948661726295992,"center":0.002858138365833879,"threshold":0.0005,"radius":0.0018279110270090536,"ntrain":398,"ncal":199,"cal_bias":0.0008251191955606222,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"66899c9bf8be32affa1961d4a67efcce85c9b82096c65daf58448f2ecfc980a9"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"284ee412fbaa3bf9ae2cd15e3ecc261c490514f127ed4a1dc69356d7a1429681"}},{"mean":-0.00036861207984510507,"slope":-0.005082479421957443,"center":0.0027713372846730456,"threshold":0.0005,"radius":0.0010399359607285144,"ntrain":397,"ncal":200,"cal_bias":6.955173759666701e-05,"train_dates":{"count":397,"first":1,"last":399,"contiguous":false,"canonical_json_sha256":"6b1f9125a5653353fcfb2ff0f5433df0bd977679290d6d995100620a0e020158"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.0038130101694972365,"slope":0.005240853493102743,"center":0.002797050480622816,"threshold":0.0005,"radius":0.0013914756464946387,"ntrain":396,"ncal":198,"cal_bias":0.0004520191852532839,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"6a4dae04f3b3c12e413a8cacdb88a7c8a4b548140e8a47cf848e2de1359a10ad"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"de0bf1f2848a6aa985add53f0546c9c35b1384bfdc2dcee2bf71814fa4928c52"}},{"mean":0.011822708862789461,"slope":0.009360030832603318,"center":0.002882485000590901,"threshold":0.0005,"radius":0.0012556586937010807,"ntrain":400,"ncal":197,"cal_bias":0.0002543434438663819,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":197,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"cda952cd0e36cf4e5dc80c161eef6bcb209d6e7d39c8e790ac71eb5dd0bcb1d7"}}],"conditional_mean_interval_coverage":0.2},{"seed":1634635432866334191,"scenario":"reversal","variant":"ungated","coverage":0.7903439153439153,"conditional_accuracy":0.2489539748953975,"confusion_latent_individual":[[0,0,0,16,570,0],[0,0,9,563,20,0],[0,0,595,7,0,15],[24,0,19,0,0,607],[567,0,0,0,0,12]],"confusion_realized":[[12,0,151,254,447,89],[21,0,98,86,69,73],[40,0,117,99,42,108],[89,0,97,70,19,115],[429,0,160,77,13,249]],"all_opportunity_recall":[0.0,0.0,0.9643435980551054,0.0,0.0],"false_great_on_terrible":570,"false_great_rate":0.9726962457337884,"false_terrible_on_great":567,"individual_latent_interval_coverage":0.19675925925925927,"date_mean_predictive_interval_coverage":0.05422647527910686,"alarms":[],"drift_lag":22,"models":null},{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration2","coverage":0.23115079365079366,"conditional_accuracy":0.9599427753934192,"confusion_latent_individual":[[270,0,0,0,0,316],[12,68,0,0,0,512],[0,0,3,2,0,612],[0,0,1,61,11,577],[0,0,0,2,269,308]],"confusion_realized":[[213,23,0,9,6,702],[34,15,1,5,8,284],[24,12,3,13,12,342],[3,8,0,12,46,321],[8,10,0,26,208,676]],"all_opportunity_recall":[0.46075085324232085,0.11486486486486487,0.004862236628849271,0.09384615384615384,0.46459412780656306],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.8386243386243386,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":45,"cells":[1]},{"index":123,"cells":[1]},{"index":148,"cells":[0,4]}],"drift_lag":22,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":1634635432866334191,"scenario":"outer_noise","variant":"candidate","coverage":0.6904761904761905,"conditional_accuracy":0.9592911877394636,"confusion_latent_individual":[[570,0,0,0,0,16],[20,0,9,0,0,563],[0,0,528,8,0,81],[0,0,17,339,24,270],[0,0,0,7,566,6]],"confusion_realized":[[422,0,167,68,26,327],[57,0,71,37,35,113],[51,0,80,55,49,123],[30,0,70,49,74,125],[30,0,166,145,406,248]],"all_opportunity_recall":[0.9726962457337884,0.0,0.8557536466774717,0.5215384615384615,0.9775474956822107],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9596560846560847,"date_mean_predictive_interval_coverage":0.20095693779904306,"alarms":[],"drift_lag":null,"models":[{"mean":-0.011858035016823025,"slope":0.009748888406358416,"center":0.0026979306095721747,"threshold":0.0005,"radius":0.0018154744848653355,"ntrain":399,"ncal":199,"cal_bias":0.0006119650783927218,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"c9a4b63932b91aaa016376da9da4b4f82e2be4f4cfd5ef06e649baaf874697ac"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"822efda3e926b14ad1b60974e3980abdd6f96e1169ff901fee627d1703d5fa3d"}},{"mean":-0.0045444120425345465,"slope":0.0014522167417440803,"center":0.002843731887427132,"threshold":0.0005,"radius":0.00227988260989754,"ntrain":398,"ncal":199,"cal_bias":0.0010315904905593605,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"66899c9bf8be32affa1961d4a67efcce85c9b82096c65daf58448f2ecfc980a9"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"284ee412fbaa3bf9ae2cd15e3ecc261c490514f127ed4a1dc69356d7a1429681"}},{"mean":-0.00045731261889797885,"slope":-0.007143968339337006,"center":0.0026597108246900272,"threshold":0.0005,"radius":0.0013097278831104247,"ntrain":397,"ncal":200,"cal_bias":9.82806615058986e-05,"train_dates":{"count":397,"first":1,"last":399,"contiguous":false,"canonical_json_sha256":"6b1f9125a5653353fcfb2ff0f5433df0bd977679290d6d995100620a0e020158"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.0037398648953221995,"slope":0.0070415081512995225,"center":0.0027087839204674503,"threshold":0.0005,"radius":0.0017278904960280044,"ntrain":396,"ncal":198,"cal_bias":0.000558603536131022,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"6a4dae04f3b3c12e413a8cacdb88a7c8a4b548140e8a47cf848e2de1359a10ad"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"de0bf1f2848a6aa985add53f0546c9c35b1384bfdc2dcee2bf71814fa4928c52"}},{"mean":0.01180971742769318,"slope":0.012379476435993235,"center":0.002853223715492968,"threshold":0.0005,"radius":0.0015842026485738125,"ntrain":400,"ncal":197,"cal_bias":0.0003329443052724777,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":197,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"cda952cd0e36cf4e5dc80c161eef6bcb209d6e7d39c8e790ac71eb5dd0bcb1d7"}}],"conditional_mean_interval_coverage":1},{"seed":1634635432866334191,"scenario":"outer_noise","variant":"ungated","coverage":0.6908068783068783,"conditional_accuracy":0.9593106749640976,"confusion_latent_individual":[[570,0,0,0,0,16],[20,0,9,0,0,563],[0,0,528,8,0,81],[0,0,17,339,24,270],[0,0,0,7,567,5]],"confusion_realized":[[422,0,167,68,26,327],[57,0,71,37,35,113],[51,0,80,55,49,123],[30,0,70,49,74,125],[30,0,166,145,407,247]],"all_opportunity_recall":[0.9726962457337884,0.0,0.8557536466774717,0.5215384615384615,0.9792746113989638],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9596560846560847,"date_mean_predictive_interval_coverage":0.20095693779904306,"alarms":[],"drift_lag":null,"models":null},{"seed":1634635432866334191,"scenario":"outer_noise","variant":"iteration2","coverage":0.10284391534391535,"conditional_accuracy":0.9453376205787781,"confusion_latent_individual":[[138,0,0,0,0,448],[10,0,0,0,0,582],[0,0,0,0,0,617],[0,0,0,0,7,643],[0,0,0,0,156,423]],"confusion_realized":[[107,0,0,0,3,900],[9,0,0,0,12,292],[14,0,0,0,8,336],[12,0,0,0,26,310],[6,0,0,0,114,875]],"all_opportunity_recall":[0.2354948805460751,0.0,0.0,0.0,0.2694300518134715],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9593253968253969,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":45,"cells":[1]},{"index":123,"cells":[1]},{"index":149,"cells":[2]},{"index":225,"cells":[4]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":5015368413594993126,"scenario":"learnable","variant":"candidate","coverage":0.9014550264550265,"conditional_accuracy":0.9658840792369773,"confusion_latent_individual":[[612,11,0,0,0,0],[14,587,10,0,0,1],[0,13,596,4,0,6],[0,0,15,295,18,282],[0,0,0,8,543,9]],"confusion_realized":[[452,228,161,36,13,37],[84,114,104,26,19,43],[49,99,111,49,40,51],[24,79,95,74,67,54],[17,91,150,122,422,113]],"all_opportunity_recall":[0.9823434991974318,0.9591503267973857,0.962843295638126,0.48360655737704916,0.9696428571428571],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9642857142857143,"date_mean_predictive_interval_coverage":0.25636942675159236,"alarms":[],"drift_lag":null,"models":[{"mean":-0.012091818181512611,"slope":-0.005720118737856484,"center":0.0030380163939413085,"threshold":0.0005,"radius":0.0012134640997358646,"ntrain":394,"ncal":198,"cal_bias":0.0003472475598960405,"train_dates":{"count":394,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"1ccb2f2a064da8958a488c8b73c523bcffdab0646c917e8097966a807872f375"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"3f7c6f665ff4a0591a6f3f7d87bb389d64cdbe3e7641981cf74466df47541a99"}},{"mean":-0.00429841859599819,"slope":0.005479673766743133,"center":0.002247483303171499,"threshold":0.0005,"radius":0.0013702036707842072,"ntrain":398,"ncal":199,"cal_bias":0.000461113138344268,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"f842c31e49c48304d865c43ed8690cc674b0e6b9030f84478e7d5fe4173dbad4"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"50a4a68e81a60a9c53bee65d0c55aba40aadb0fe676f191db7e9bfc76005d516"}},{"mean":-0.00020090770035126982,"slope":0.0005493215215826835,"center":0.0024429114218975363,"threshold":0.0005,"radius":0.0016874970501224642,"ntrain":396,"ncal":199,"cal_bias":0.0007418801845069471,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5ffbe92baaf4c4eb0ac476f27cacc21721ba4e910b45deb6408e690b74673a28"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"46e788b67eb128d55293d91ade09a2b1869440ab4c8bfb483bfb6be291d1a092"}},{"mean":0.003793026956267251,"slope":0.00515793301475153,"center":0.002765688261583568,"threshold":0.0005,"radius":0.0017827769545431214,"ntrain":397,"ncal":200,"cal_bias":0.0009071351472978748,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5a36868106764efce0e234314eb76d893d68fa43a8528af44b541c228ace6461"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.011668490808121771,"slope":-0.00022244558689455437,"center":0.002852437304191861,"threshold":0.0005,"radius":0.001879909289927355,"ntrain":400,"ncal":200,"cal_bias":0.0009402460564762858,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}}],"conditional_mean_interval_coverage":1},{"seed":5015368413594993126,"scenario":"learnable","variant":"ungated","coverage":0.9014550264550265,"conditional_accuracy":0.9658840792369773,"confusion_latent_individual":[[612,11,0,0,0,0],[14,587,10,0,0,1],[0,13,596,4,0,6],[0,0,15,295,18,282],[0,0,0,8,543,9]],"confusion_realized":[[452,228,161,36,13,37],[84,114,104,26,19,43],[49,99,111,49,40,51],[24,79,95,74,67,54],[17,91,150,122,422,113]],"all_opportunity_recall":[0.9823434991974318,0.9591503267973857,0.962843295638126,0.48360655737704916,0.9696428571428571],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9642857142857143,"date_mean_predictive_interval_coverage":0.25636942675159236,"alarms":[],"drift_lag":null,"models":null},{"seed":5015368413594993126,"scenario":"learnable","variant":"iteration2","coverage":0.31712962962962965,"conditional_accuracy":0.9739311783107404,"confusion_latent_individual":[[400,2,0,0,0,221],[8,119,0,0,0,485],[0,2,34,0,0,583],[0,0,2,30,10,568],[0,0,0,1,351,208]],"confusion_realized":[[284,44,15,2,5,577],[59,28,6,7,14,276],[36,21,6,2,24,310],[18,14,3,6,37,315],[11,16,6,14,281,587]],"all_opportunity_recall":[0.6420545746388443,0.19444444444444445,0.05492730210016155,0.04918032786885246,0.6267857142857143],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9467592592592593,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":55,"cells":[4]},{"index":200,"cells":[2]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":5015368413594993126,"scenario":"null","variant":"candidate","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,623],[0,0,0,0,0,612],[0,0,0,0,0,619],[0,0,0,0,0,610],[0,0,0,0,0,560]],"confusion_realized":[[0,0,0,0,0,927],[0,0,0,0,0,390],[0,0,0,0,0,399],[0,0,0,0,0,393],[0,0,0,0,0,915]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.2046957671957672,"date_mean_predictive_interval_coverage":0.2727272727272727,"alarms":[],"drift_lag":null,"models":[{"mean":-6.768803599517748e-05,"slope":0.0037394598048865156,"center":0.002684028665330509,"threshold":0.0005,"radius":0.0020842951057610777,"ntrain":399,"ncal":198,"cal_bias":0.0008988614585073687,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"31407c33bf9e2ac8c016adaa4ec06f1e3956614bb8e94b00e31b1ca6d025a3b0"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"71cc6231bbc5f91d35cbb52edee1fec3bef49755200d4c1609fbd1b056310ce5"}},{"mean":-0.0005985358241781962,"slope":0.0014208134579768244,"center":0.0026759023099680807,"threshold":0.0005,"radius":0.002806598763387621,"ntrain":396,"ncal":200,"cal_bias":0.001528042692189921,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5a3def271be518377841c59cfe7cd71bff0b74e8c54cefd51dae2a07e1774411"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":-0.0005509049829110789,"slope":-0.00032875733049288447,"center":0.00292230224822804,"threshold":0.0005,"radius":0.0020851195755670895,"ntrain":399,"ncal":199,"cal_bias":0.0009221287335476913,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"a2148c9d8b8ee20926df9a49616a0608bcad07b4bff9289c404e8de0a42cb93d"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"ce3542f2c12776a3f55ed3e68ab624ff104949e4c4c5021d626376000772f31d"}},{"mean":-0.0003226041589859131,"slope":0.0021872841643741257,"center":0.0023277178996565034,"threshold":0.0005,"radius":0.0017038126627735477,"ntrain":396,"ncal":200,"cal_bias":0.0005358406222629146,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"b4016cd560f8a15d971331821ad3589466f4caf41b8151809a49998bc0579929"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":-0.00029009773956976373,"slope":-0.002186281887481718,"center":0.0027478812597074753,"threshold":0.0005,"radius":0.002323903396831654,"ntrain":398,"ncal":198,"cal_bias":0.0011281155335694454,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"3ccfc546c79c9bb213aab6a1a8e6686b1e40bcc1d7c454957d02812a141520b7"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"4d4b6f8cc525b17c0ce17e4c620815443c67b964faf27fad50b286b93ddde892"}}],"conditional_mean_interval_coverage":1},{"seed":5015368413594993126,"scenario":"null","variant":"ungated","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,623],[0,0,0,0,0,612],[0,0,0,0,0,619],[0,0,0,0,0,610],[0,0,0,0,0,560]],"confusion_realized":[[0,0,0,0,0,927],[0,0,0,0,0,390],[0,0,0,0,0,399],[0,0,0,0,0,393],[0,0,0,0,0,915]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.2046957671957672,"date_mean_predictive_interval_coverage":0.2727272727272727,"alarms":[],"drift_lag":null,"models":null},{"seed":5015368413594993126,"scenario":"null","variant":"iteration2","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,623],[0,0,0,0,0,612],[0,0,0,0,0,619],[0,0,0,0,0,610],[0,0,0,0,0,560]],"confusion_realized":[[0,0,0,0,0,927],[0,0,0,0,0,390],[0,0,0,0,0,399],[0,0,0,0,0,393],[0,0,0,0,0,915]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.34656084656084657,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":50,"cells":[0]},{"index":91,"cells":[3]},{"index":120,"cells":[3]},{"index":172,"cells":[1]},{"index":208,"cells":[0]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":5015368413594993126,"scenario":"reversal","variant":"candidate","coverage":0.15707671957671956,"conditional_accuracy":0.24,"confusion_latent_individual":[[0,0,0,0,105,518],[0,0,1,40,2,569],[0,2,114,1,0,502],[2,104,3,0,0,501],[98,3,0,0,0,459]],"confusion_realized":[[2,16,39,19,76,775],[4,15,18,9,16,328],[7,18,17,8,9,340],[18,20,16,4,4,331],[69,40,28,1,2,775]],"all_opportunity_recall":[0.0,0.0,0.1841680129240711,0.0,0.0],"false_great_on_terrible":105,"false_great_rate":0.16853932584269662,"false_terrible_on_great":98,"individual_latent_interval_coverage":0.1970899470899471,"date_mean_predictive_interval_coverage":0.0875796178343949,"alarms":[{"index":628,"cell":0,"delta":0.02213517899573353,"threshold":0.017067521442752503,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.023413777877967182,"threshold":0.01706133643749677,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}],"drift_lag":22,"models":[{"mean":-0.012091818181512611,"slope":-0.005720118737856484,"center":0.0030380163939413085,"threshold":0.0005,"radius":0.0012134640997358646,"ntrain":394,"ncal":198,"cal_bias":0.0003472475598960405,"train_dates":{"count":394,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"1ccb2f2a064da8958a488c8b73c523bcffdab0646c917e8097966a807872f375"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"3f7c6f665ff4a0591a6f3f7d87bb389d64cdbe3e7641981cf74466df47541a99"}},{"mean":-0.00429841859599819,"slope":0.005479673766743133,"center":0.002247483303171499,"threshold":0.0005,"radius":0.0013702036707842072,"ntrain":398,"ncal":199,"cal_bias":0.000461113138344268,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"f842c31e49c48304d865c43ed8690cc674b0e6b9030f84478e7d5fe4173dbad4"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"50a4a68e81a60a9c53bee65d0c55aba40aadb0fe676f191db7e9bfc76005d516"}},{"mean":-0.00020090770035126982,"slope":0.0005493215215826835,"center":0.0024429114218975363,"threshold":0.0005,"radius":0.0016874970501224642,"ntrain":396,"ncal":199,"cal_bias":0.0007418801845069471,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5ffbe92baaf4c4eb0ac476f27cacc21721ba4e910b45deb6408e690b74673a28"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"46e788b67eb128d55293d91ade09a2b1869440ab4c8bfb483bfb6be291d1a092"}},{"mean":0.003793026956267251,"slope":0.00515793301475153,"center":0.002765688261583568,"threshold":0.0005,"radius":0.0017827769545431214,"ntrain":397,"ncal":200,"cal_bias":0.0009071351472978748,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5a36868106764efce0e234314eb76d893d68fa43a8528af44b541c228ace6461"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.011668490808121771,"slope":-0.00022244558689455437,"center":0.002852437304191861,"threshold":0.0005,"radius":0.001879909289927355,"ntrain":400,"ncal":200,"cal_bias":0.0009402460564762858,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}}],"conditional_mean_interval_coverage":0.2},{"seed":5015368413594993126,"scenario":"reversal","variant":"ungated","coverage":0.9014550264550265,"conditional_accuracy":0.2186353631694791,"confusion_latent_individual":[[0,0,0,4,612,7],[0,0,10,305,14,283],[0,10,596,6,0,7],[18,576,15,0,0,1],[543,17,0,0,0,0]],"confusion_realized":[[13,72,161,109,452,120],[19,69,104,65,84,49],[40,99,111,45,49,55],[67,128,95,47,24,32],[422,235,150,49,17,42]],"all_opportunity_recall":[0.0,0.0,0.962843295638126,0.0,0.0],"false_great_on_terrible":612,"false_great_rate":0.9823434991974318,"false_terrible_on_great":543,"individual_latent_interval_coverage":0.1970899470899471,"date_mean_predictive_interval_coverage":0.0875796178343949,"alarms":[],"drift_lag":22,"models":null},{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration2","coverage":0.05787037037037037,"conditional_accuracy":0.49714285714285716,"confusion_latent_individual":[[43,0,0,0,25,555],[2,0,0,0,1,609],[0,0,0,0,0,619],[1,26,0,0,1,582],[31,1,0,0,44,484]],"confusion_realized":[[31,6,0,0,19,871],[8,4,0,0,6,372],[5,5,0,0,5,384],[11,5,0,0,5,372],[22,7,0,0,36,850]],"all_opportunity_recall":[0.06902086677367576,0.0,0.0,0.0,0.07857142857142857],"false_great_on_terrible":25,"false_great_rate":0.04012841091492777,"false_terrible_on_great":31,"individual_latent_interval_coverage":0.9097222222222222,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":55,"cells":[4]},{"index":132,"cells":[3,4]},{"index":171,"cells":[0]},{"index":199,"cells":[2]}],"drift_lag":22,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":5015368413594993126,"scenario":"outer_noise","variant":"candidate","coverage":0.392526455026455,"conditional_accuracy":0.9730412805391744,"confusion_latent_individual":[[612,0,0,0,0,11],[14,0,0,0,0,598],[0,0,0,0,0,619],[0,0,0,0,18,592],[0,0,0,0,543,17]],"confusion_realized":[[418,0,0,0,31,527],[80,0,0,0,26,256],[58,0,0,0,36,263],[34,0,0,0,69,243],[36,0,0,0,399,548]],"all_opportunity_recall":[0.9823434991974318,0.0,0.0,0.0,0.9696428571428571],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9642857142857143,"date_mean_predictive_interval_coverage":0.25477707006369427,"alarms":[],"drift_lag":null,"models":[{"mean":-0.012164374070273836,"slope":-0.007545394994692252,"center":0.0030057004608315644,"threshold":0.0005,"radius":0.0015201736035586285,"ntrain":394,"ncal":198,"cal_bias":0.0004367672546929192,"train_dates":{"count":394,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"1ccb2f2a064da8958a488c8b73c523bcffdab0646c917e8097966a807872f375"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"3f7c6f665ff4a0591a6f3f7d87bb389d64cdbe3e7641981cf74466df47541a99"}},{"mean":-0.004347491818021588,"slope":0.007344027740709321,"center":0.002193917864972163,"threshold":0.0005,"radius":0.0016912040683745746,"ntrain":398,"ncal":199,"cal_bias":0.0005586908167247109,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"f842c31e49c48304d865c43ed8690cc674b0e6b9030f84478e7d5fe4173dbad4"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"50a4a68e81a60a9c53bee65d0c55aba40aadb0fe676f191db7e9bfc76005d516"}},{"mean":-0.00024981788662235496,"slope":0.0011612558191001516,"center":0.0023012041311460825,"threshold":0.0005,"radius":0.0021112280655952434,"ntrain":396,"ncal":199,"cal_bias":0.0009302809194312245,"train_dates":{"count":396,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5ffbe92baaf4c4eb0ac476f27cacc21721ba4e910b45deb6408e690b74673a28"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"46e788b67eb128d55293d91ade09a2b1869440ab4c8bfb483bfb6be291d1a092"}},{"mean":0.00371631368213987,"slope":0.006121184499917346,"center":0.0027917290626940233,"threshold":0.0005,"radius":0.002207719500122181,"ntrain":397,"ncal":200,"cal_bias":0.0011164028362054366,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"5a36868106764efce0e234314eb76d893d68fa43a8528af44b541c228ace6461"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.011639698827612536,"slope":-0.0010829864662341166,"center":0.0028717143709058113,"threshold":0.0005,"radius":0.0023424764727706998,"ntrain":400,"ncal":200,"cal_bias":0.001172591300754073,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}}],"conditional_mean_interval_coverage":1},{"seed":5015368413594993126,"scenario":"outer_noise","variant":"ungated","coverage":0.392526455026455,"conditional_accuracy":0.9730412805391744,"confusion_latent_individual":[[612,0,0,0,0,11],[14,0,0,0,0,598],[0,0,0,0,0,619],[0,0,0,0,18,592],[0,0,0,0,543,17]],"confusion_realized":[[418,0,0,0,31,527],[80,0,0,0,26,256],[58,0,0,0,36,263],[34,0,0,0,69,243],[36,0,0,0,399,548]],"all_opportunity_recall":[0.9823434991974318,0.0,0.0,0.0,0.9696428571428571],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9642857142857143,"date_mean_predictive_interval_coverage":0.25477707006369427,"alarms":[],"drift_lag":null,"models":null},{"seed":5015368413594993126,"scenario":"outer_noise","variant":"iteration2","coverage":0.26951058201058203,"conditional_accuracy":0.9754601226993865,"confusion_latent_individual":[[400,1,0,0,0,222],[8,41,0,0,0,563],[0,1,3,0,0,615],[0,0,0,0,10,600],[0,0,0,0,351,209]],"confusion_realized":[[260,13,0,0,18,685],[57,12,0,0,16,277],[42,9,1,0,24,281],[25,4,0,0,40,277],[24,5,2,0,263,689]],"all_opportunity_recall":[0.6420545746388443,0.06699346405228758,0.004846526655896607,0.0,0.6267857142857143],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.951058201058201,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":55,"cells":[4]},{"index":200,"cells":[2]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":3584306075979195116,"scenario":"learnable","variant":"candidate","coverage":0.7976190476190477,"conditional_accuracy":0.9626865671641791,"confusion_latent_individual":[[591,19,0,0,0,0],[20,589,0,0,0,20],[0,17,0,9,0,578],[0,0,0,560,16,14],[0,0,0,9,582,0]],"confusion_realized":[[444,235,0,73,12,160],[84,140,0,58,25,87],[44,106,0,88,36,122],[26,63,0,108,82,107],[13,81,0,251,443,136]],"all_opportunity_recall":[0.9688524590163935,0.9364069952305246,0.0,0.9491525423728814,0.9847715736040609],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.958994708994709,"date_mean_predictive_interval_coverage":0.24920127795527156,"alarms":[],"drift_lag":null,"models":[{"mean":-0.012244942608355068,"slope":-5.773020014814312e-05,"center":0.002809856649107693,"threshold":0.0005,"radius":0.0019360950978409295,"ntrain":399,"ncal":199,"cal_bias":0.000980489210908796,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"03d6ee824562c334f61715a9980034730bb331c93db3d1d5b1ef8ffe7ad4bd78"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"5bfe4780c58e407c990415135a0481c55f95f1dc1dc70679d874de38b8d0e5e6"}},{"mean":-0.004285778591872411,"slope":0.0012119185563599043,"center":0.002549853526264447,"threshold":0.0005,"radius":0.0013986903348685007,"ntrain":397,"ncal":198,"cal_bias":0.00041592938928253296,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"0687f018b322d032f90fa4e7020d2eb2d66cfd6e094d4d88e33adf42ea509ada"},"cal_dates":{"count":198,"first":404,"last":602,"contiguous":false,"canonical_json_sha256":"35fbfc1942ec50ce47359fa37eabf58c920b43033c700be65c01671d8a3f6eff"}},{"mean":-0.0006531851754552181,"slope":0.00636848641829911,"center":0.00264224273196401,"threshold":0.0005,"radius":0.0017613436259112276,"ntrain":399,"ncal":200,"cal_bias":0.0007126316378576044,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"165c1a09dca31c6cd59bd3c82777432497ee0d0cb1f7b383f2721ddeb9152973"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.0037702166545051656,"slope":-0.00029220674380858443,"center":0.002663732540780749,"threshold":0.0005,"radius":0.0015239039093269133,"ntrain":399,"ncal":199,"cal_bias":0.0005180239009822667,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"6f2049deead2f82e130ae97a4515b6d2ea5f66eba2ff5501d853cbdb1225128e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"a8079594299497a8a7eb74eddfc07efb98bd96e2607604a2dcb7a32d48c1a344"}},{"mean":0.011730673264840886,"slope":-0.0018483869937013409,"center":0.002871201971875814,"threshold":0.0005,"radius":0.001081057740814655,"ntrain":399,"ncal":199,"cal_bias":0.0002220844139550286,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"b8a655cf13fc73205bf7980f9ebf6978fef6b77595b148f71ad30be40023e7c8"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"5a7aef421c1aa3fcad53639c3f70c0d5c819c5359314eb0fbdca1ffc2a49b2b2"}}],"conditional_mean_interval_coverage":1},{"seed":3584306075979195116,"scenario":"learnable","variant":"ungated","coverage":0.7976190476190477,"conditional_accuracy":0.9626865671641791,"confusion_latent_individual":[[591,19,0,0,0,0],[20,589,0,0,0,20],[0,17,0,9,0,578],[0,0,0,560,16,14],[0,0,0,9,582,0]],"confusion_realized":[[444,235,0,73,12,160],[84,140,0,58,25,87],[44,106,0,88,36,122],[26,63,0,108,82,107],[13,81,0,251,443,136]],"all_opportunity_recall":[0.9688524590163935,0.9364069952305246,0.0,0.9491525423728814,0.9847715736040609],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.958994708994709,"date_mean_predictive_interval_coverage":0.24920127795527156,"alarms":[],"drift_lag":null,"models":null},{"seed":3584306075979195116,"scenario":"learnable","variant":"iteration2","coverage":0.054563492063492064,"conditional_accuracy":0.9696969696969697,"confusion_latent_individual":[[72,0,0,0,0,538],[1,0,0,0,0,628],[0,0,0,0,0,604],[0,0,0,11,4,575],[0,0,0,0,77,514]],"confusion_realized":[[55,0,0,0,1,868],[10,0,0,2,4,378],[6,0,0,4,3,383],[2,0,0,3,12,369],[0,0,0,2,61,861]],"all_opportunity_recall":[0.1180327868852459,0.0,0.0,0.01864406779661017,0.13028764805414553],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9487433862433863,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":87,"cells":[0]},{"index":145,"cells":[4]},{"index":181,"cells":[4]},{"index":220,"cells":[0]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":3584306075979195116,"scenario":"null","variant":"candidate","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,610],[0,0,0,0,0,629],[0,0,0,0,0,604],[0,0,0,0,0,590],[0,0,0,0,0,591]],"confusion_realized":[[0,0,0,0,0,924],[0,0,0,0,0,394],[0,0,0,0,0,396],[0,0,0,0,0,386],[0,0,0,0,0,924]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.19973544973544974,"date_mean_predictive_interval_coverage":0.19745222929936307,"alarms":[],"drift_lag":null,"models":[{"mean":-0.0003599452106636977,"slope":0.00777518546988035,"center":0.0026571915527416547,"threshold":0.0005,"radius":0.0016513855921614215,"ntrain":399,"ncal":200,"cal_bias":0.00048816728316780557,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"eedb454bfd0884bec2022e53f13da53a6c7b85ad56d3808cca56f459cdf3db96"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":2.3951201089293778e-05,"slope":-5.590756842000173e-06,"center":0.0026915713019545623,"threshold":0.0005,"radius":0.0013231332192634188,"ntrain":398,"ncal":198,"cal_bias":-1.1025526185670932e-05,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"ed0a9b39c426f52d2ff87810bd8df1ff479ca889f86bb6921f8a5d489630482e"},"cal_dates":{"count":198,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"7a9b89f082e9b16d0936921487b2ce4b4874fd888da0b58499346fbf684af5c1"}},{"mean":-0.0003494675601653868,"slope":-0.00225558329413451,"center":0.002658407204537766,"threshold":0.0005,"radius":0.0016256644479934906,"ntrain":400,"ncal":199,"cal_bias":0.0005094688567770733,"train_dates":{"count":400,"first":0,"last":399,"contiguous":true,"canonical_json_sha256":"61c7e6234e65fb5cce2355ea19e2867337eab0f6ef7092bc7e646da03f05ab8e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"28a16e8bd50221c5f3ac54fc1f5ee1ac966bd3ef49866be63bd2fbebda1f4678"}},{"mean":-0.0002762055053427672,"slope":-0.001966803046231866,"center":0.0028878276388053614,"threshold":0.0005,"radius":0.0018279826542127711,"ntrain":398,"ncal":199,"cal_bias":0.0006665587513348314,"train_dates":{"count":398,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"323eae0aa09660ac6440b71d5ce9a6fe0a4782cae3be69003b1ceaecca64135a"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"578ec3e4e0b0d9fd0144b53bb3c1d414db219667f85b6273c81731e58b655fa5"}},{"mean":-0.0007887917048225171,"slope":0.003845766226315255,"center":0.0026277008487394947,"threshold":0.0005,"radius":0.0017489709056947374,"ntrain":399,"ncal":200,"cal_bias":0.00047367599965083976,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"df3966434fa07d607409e5b865756fd25bda9c88a0bca9ad6af1345af67765c7"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}}],"conditional_mean_interval_coverage":1},{"seed":3584306075979195116,"scenario":"null","variant":"ungated","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,610],[0,0,0,0,0,629],[0,0,0,0,0,604],[0,0,0,0,0,590],[0,0,0,0,0,591]],"confusion_realized":[[0,0,0,0,0,924],[0,0,0,0,0,394],[0,0,0,0,0,396],[0,0,0,0,0,386],[0,0,0,0,0,924]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.19973544973544974,"date_mean_predictive_interval_coverage":0.19745222929936307,"alarms":[],"drift_lag":null,"models":null},{"seed":3584306075979195116,"scenario":"null","variant":"iteration2","coverage":0.0,"conditional_accuracy":null,"confusion_latent_individual":[[0,0,0,0,0,610],[0,0,0,0,0,629],[0,0,0,0,0,604],[0,0,0,0,0,590],[0,0,0,0,0,591]],"confusion_realized":[[0,0,0,0,0,924],[0,0,0,0,0,394],[0,0,0,0,0,396],[0,0,0,0,0,386],[0,0,0,0,0,924]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.4074074074074074,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":40,"cells":[1]},{"index":134,"cells":[3]},{"index":185,"cells":[4]},{"index":232,"cells":[0]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":3584306075979195116,"scenario":"reversal","variant":"candidate","coverage":0.14285714285714285,"conditional_accuracy":0.0,"confusion_latent_individual":[[0,0,0,4,109,497],[0,0,0,103,3,523],[0,3,0,3,0,598],[4,93,0,0,0,493],[108,2,0,0,0,481]],"confusion_realized":[[1,10,0,35,83,795],[6,7,0,24,14,343],[4,20,0,25,9,338],[17,24,0,10,4,331],[84,37,0,16,2,785]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":109,"false_great_rate":0.17868852459016393,"false_terrible_on_great":108,"individual_latent_interval_coverage":0.19113756613756613,"date_mean_predictive_interval_coverage":0.08306709265175719,"alarms":[{"index":628,"cell":0,"delta":0.025065602999812024,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.022543543419335565,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}],"drift_lag":22,"models":[{"mean":-0.012244942608355068,"slope":-5.773020014814312e-05,"center":0.002809856649107693,"threshold":0.0005,"radius":0.0019360950978409295,"ntrain":399,"ncal":199,"cal_bias":0.000980489210908796,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"03d6ee824562c334f61715a9980034730bb331c93db3d1d5b1ef8ffe7ad4bd78"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"5bfe4780c58e407c990415135a0481c55f95f1dc1dc70679d874de38b8d0e5e6"}},{"mean":-0.004285778591872411,"slope":0.0012119185563599043,"center":0.002549853526264447,"threshold":0.0005,"radius":0.0013986903348685007,"ntrain":397,"ncal":198,"cal_bias":0.00041592938928253296,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"0687f018b322d032f90fa4e7020d2eb2d66cfd6e094d4d88e33adf42ea509ada"},"cal_dates":{"count":198,"first":404,"last":602,"contiguous":false,"canonical_json_sha256":"35fbfc1942ec50ce47359fa37eabf58c920b43033c700be65c01671d8a3f6eff"}},{"mean":-0.0006531851754552181,"slope":0.00636848641829911,"center":0.00264224273196401,"threshold":0.0005,"radius":0.0017613436259112276,"ntrain":399,"ncal":200,"cal_bias":0.0007126316378576044,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"165c1a09dca31c6cd59bd3c82777432497ee0d0cb1f7b383f2721ddeb9152973"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.0037702166545051656,"slope":-0.00029220674380858443,"center":0.002663732540780749,"threshold":0.0005,"radius":0.0015239039093269133,"ntrain":399,"ncal":199,"cal_bias":0.0005180239009822667,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"6f2049deead2f82e130ae97a4515b6d2ea5f66eba2ff5501d853cbdb1225128e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"a8079594299497a8a7eb74eddfc07efb98bd96e2607604a2dcb7a32d48c1a344"}},{"mean":0.011730673264840886,"slope":-0.0018483869937013409,"center":0.002871201971875814,"threshold":0.0005,"radius":0.001081057740814655,"ntrain":399,"ncal":199,"cal_bias":0.0002220844139550286,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"b8a655cf13fc73205bf7980f9ebf6978fef6b77595b148f71ad30be40023e7c8"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"5a7aef421c1aa3fcad53639c3f70c0d5c819c5359314eb0fbdca1ffc2a49b2b2"}}],"conditional_mean_interval_coverage":0.2},{"seed":3584306075979195116,"scenario":"reversal","variant":"ungated","coverage":0.7976190476190477,"conditional_accuracy":0.0,"confusion_latent_individual":[[0,0,0,19,591,0],[0,0,0,589,20,20],[0,9,0,17,0,578],[16,560,0,0,0,14],[582,9,0,0,0,0]],"confusion_realized":[[12,73,0,235,444,160],[25,58,0,140,84,87],[36,88,0,106,44,122],[82,108,0,63,26,107],[443,251,0,81,13,136]],"all_opportunity_recall":[0.0,0.0,0.0,0.0,0.0],"false_great_on_terrible":591,"false_great_rate":0.9688524590163935,"false_terrible_on_great":582,"individual_latent_interval_coverage":0.19113756613756613,"date_mean_predictive_interval_coverage":0.08306709265175719,"alarms":[],"drift_lag":22,"models":null},{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration2","coverage":0.19246031746031747,"conditional_accuracy":0.9450171821305842,"confusion_latent_individual":[[209,0,0,0,9,392],[10,0,2,0,0,617],[0,0,44,2,0,558],[0,0,1,106,5,478],[0,0,0,3,191,397]],"confusion_realized":[[163,0,18,14,13,716],[29,0,6,11,9,339],[12,0,8,16,18,342],[10,0,7,19,27,323],[5,0,8,51,138,722]],"all_opportunity_recall":[0.34262295081967215,0.0,0.0728476821192053,0.17966101694915254,0.32318104906937395],"false_great_on_terrible":9,"false_great_rate":0.014754098360655738,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9143518518518519,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":87,"cells":[0]},{"index":133,"cells":[3]},{"index":220,"cells":[4]}],"drift_lag":22,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."},{"seed":3584306075979195116,"scenario":"outer_noise","variant":"candidate","coverage":0.3998015873015873,"conditional_accuracy":0.9702233250620348,"confusion_latent_individual":[[591,0,0,0,0,19],[20,0,0,0,0,609],[0,0,0,0,0,604],[0,0,0,0,16,574],[0,0,0,0,582,9]],"confusion_realized":[[421,0,0,0,32,537],[73,0,0,0,24,240],[53,0,0,0,47,265],[32,0,0,0,76,237],[32,0,0,0,419,536]],"all_opportunity_recall":[0.9688524590163935,0.0,0.0,0.0,0.9847715736040609],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.958994708994709,"date_mean_predictive_interval_coverage":0.2476038338658147,"alarms":[],"drift_lag":null,"models":[{"mean":-0.012358135534581562,"slope":0.000697331018018111,"center":0.0027221393373287124,"threshold":0.0005,"radius":0.002423789396749378,"ntrain":399,"ncal":199,"cal_bias":0.0012306512999014484,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"03d6ee824562c334f61715a9980034730bb331c93db3d1d5b1ef8ffe7ad4bd78"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"5bfe4780c58e407c990415135a0481c55f95f1dc1dc70679d874de38b8d0e5e6"}},{"mean":-0.004339249966262714,"slope":0.0018518443546813948,"center":0.002401885430696822,"threshold":0.0005,"radius":0.0017625530134691978,"ntrain":397,"ncal":198,"cal_bias":0.0005410518188053862,"train_dates":{"count":397,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"0687f018b322d032f90fa4e7020d2eb2d66cfd6e094d4d88e33adf42ea509ada"},"cal_dates":{"count":198,"first":404,"last":602,"contiguous":false,"canonical_json_sha256":"35fbfc1942ec50ce47359fa37eabf58c920b43033c700be65c01671d8a3f6eff"}},{"mean":-0.0008252146116987893,"slope":0.008935601002882584,"center":0.0025514152414147424,"threshold":0.0005,"radius":0.0021957805139287225,"ntrain":399,"ncal":200,"cal_bias":0.000887554435733516,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"165c1a09dca31c6cd59bd3c82777432497ee0d0cb1f7b383f2721ddeb9152973"},"cal_dates":{"count":200,"first":403,"last":602,"contiguous":true,"canonical_json_sha256":"b466e02f371653897eeab2cbbb6bac3f333bb6599cfbf059aeeaa7ea1007c8e1"}},{"mean":0.0036877101505895862,"slope":0.0006303895043528584,"center":0.0025469605315299,"threshold":0.0005,"radius":0.0019168475633725476,"ntrain":399,"ncal":199,"cal_bias":0.0006630707224408499,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"6f2049deead2f82e130ae97a4515b6d2ea5f66eba2ff5501d853cbdb1225128e"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"a8079594299497a8a7eb74eddfc07efb98bd96e2607604a2dcb7a32d48c1a344"}},{"mean":0.01170781387289182,"slope":-0.002136348370090328,"center":0.0028239699419671783,"threshold":0.0005,"radius":0.001352390697433938,"ntrain":399,"ncal":199,"cal_bias":0.00028078417878166456,"train_dates":{"count":399,"first":0,"last":399,"contiguous":false,"canonical_json_sha256":"b8a655cf13fc73205bf7980f9ebf6978fef6b77595b148f71ad30be40023e7c8"},"cal_dates":{"count":199,"first":403,"last":602,"contiguous":false,"canonical_json_sha256":"5a7aef421c1aa3fcad53639c3f70c0d5c819c5359314eb0fbdca1ffc2a49b2b2"}}],"conditional_mean_interval_coverage":1},{"seed":3584306075979195116,"scenario":"outer_noise","variant":"ungated","coverage":0.3998015873015873,"conditional_accuracy":0.9702233250620348,"confusion_latent_individual":[[591,0,0,0,0,19],[20,0,0,0,0,609],[0,0,0,0,0,604],[0,0,0,0,16,574],[0,0,0,0,582,9]],"confusion_realized":[[421,0,0,0,32,537],[73,0,0,0,24,240],[53,0,0,0,47,265],[32,0,0,0,76,237],[32,0,0,0,419,536]],"all_opportunity_recall":[0.9688524590163935,0.0,0.0,0.0,0.9847715736040609],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.958994708994709,"date_mean_predictive_interval_coverage":0.2476038338658147,"alarms":[],"drift_lag":null,"models":null},{"seed":3584306075979195116,"scenario":"outer_noise","variant":"iteration2","coverage":0.05092592592592592,"conditional_accuracy":0.9675324675324676,"confusion_latent_individual":[[72,0,0,0,0,538],[1,0,0,0,0,628],[0,0,0,0,0,604],[0,0,0,0,4,586],[0,0,0,0,77,514]],"confusion_realized":[[52,0,0,0,4,934],[9,0,0,0,3,325],[7,0,0,0,7,351],[4,0,0,0,9,332],[1,0,0,0,58,928]],"all_opportunity_recall":[0.1180327868852459,0.0,0.0,0.0,0.13028764805414553],"false_great_on_terrible":0,"false_great_rate":0.0,"false_terrible_on_great":0,"individual_latent_interval_coverage":0.9553571428571429,"date_mean_predictive_interval_coverage":null,"alarms":[{"index":87,"cells":[0]},{"index":145,"cells":[4]},{"index":181,"cells":[4]},{"index":220,"cells":[0]}],"drift_lag":null,"models":null,"date_mean_interval_note":"Not measured for baseline: frozen runner computed candidate-model date diagnostic in this field; invalid baseline value removed in analysis."}],"portfolio_runs":[{"seed":1564008556893530022,"scenario":"learnable","variant":"candidate","total_return":0.8565803518951918,"cagr":2.446890603043274,"mdd":0.001963545471879824,"costs":26390.734316483435,"final_nav":185658.03518951917,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0018333001423728027,"trades":713,"mean_exposure":0.49860300716718614},{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration2","total_return":0.39237711548683607,"cagr":0.938714031731442,"mdd":0.0009689169948781107,"costs":10231.393264712864,"final_nav":139237.7115486836,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.001338466798717441,"trades":309,"mean_exposure":0.22515157460859517},{"seed":1564008556893530022,"scenario":"learnable","variant":"benchmark","total_return":0.5456474145097245,"cagr":1.3890259299805963,"mdd":0.005304813657442509,"costs":23877.426114519654,"final_nav":154564.74145097245,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0020559366010415568,"trades":690,"mean_exposure":0.5},{"seed":1564008556893530022,"scenario":"learnable","variant":"scaled","total_return":0.8947400188097325,"cagr":2.5900397388791054,"mdd":0.0056742683080288625,"costs":26408.760006435867,"final_nav":189474.00188097326,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0021428887034773483,"trades":541,"mean_exposure":0.4991352816116626},{"seed":1564008556893530022,"scenario":"null","variant":"candidate","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":1564008556893530022,"scenario":"null","variant":"iteration2","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":1564008556893530022,"scenario":"null","variant":"benchmark","total_return":-0.01290983758249431,"cagr":-0.025653011258582215,"mdd":0.0453760384892129,"costs":19082.702029076776,"final_nav":98709.01624175056,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.004165642239230085,"trades":692,"mean_exposure":0.5},{"seed":1564008556893530022,"scenario":"reversal","variant":"candidate","total_return":-0.09335387657175176,"cagr":-0.1779928068725296,"mdd":0.09335387657175176,"costs":3147.85109849186,"final_nav":90664.61234282482,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.00328233948439627,"trades":129,"mean_exposure":0.08740442927292283},{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration2","total_return":0.2934610056762552,"cagr":0.6730413732050295,"mdd":0.02710753263629373,"costs":9518.584637368103,"final_nav":129346.10056762552,"max_modeled_risk":0.019970044932601107,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002305920459099081,"trades":310,"mean_exposure":0.2244827378252593},{"seed":1564008556893530022,"scenario":"reversal","variant":"benchmark","total_return":-0.3582405588908163,"cagr":-0.5881448197472281,"mdd":0.35874663143746455,"costs":15493.885177912698,"final_nav":64175.944110918375,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.004165642239230081,"trades":692,"mean_exposure":0.5},{"seed":1564008556893530022,"scenario":"outer_noise","variant":"candidate","total_return":0.8397485025644511,"cagr":2.38467455268814,"mdd":0.00567006677947679,"costs":26056.05774051141,"final_nav":183974.85025644512,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002591625177966036,"trades":700,"mean_exposure":0.4942277626474625},{"seed":1564008556893530022,"scenario":"outer_noise","variant":"iteration2","total_return":0.3464292042015571,"cagr":0.8128716019268383,"mdd":0.0010291813614353718,"costs":8873.051981066159,"final_nav":134642.92042015571,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.001973083498396808,"trades":271,"mean_exposure":0.20006704184456253},{"seed":1564008556893530022,"scenario":"outer_noise","variant":"benchmark","total_return":0.5418507955059377,"cagr":1.3773038756022928,"mdd":0.007384105546087483,"costs":23874.498674003204,"final_nav":154185.07955059377,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002669920751301966,"trades":690,"mean_exposure":0.5},{"seed":1634635432866334191,"scenario":"learnable","variant":"candidate","total_return":0.8532868241113967,"cagr":2.434672052424907,"mdd":0.003995693570929326,"costs":26113.89853369401,"final_nav":185328.68241113966,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0017168536902495927,"trades":711,"mean_exposure":0.49857151938894406},{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration2","total_return":0.3192149412476988,"cagr":0.7403280612111693,"mdd":0.0006958697755835574,"costs":8776.029399967545,"final_nav":131921.49412476987,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0014903225805685998,"trades":276,"mean_exposure":0.19958026076788485},{"seed":1634635432866334191,"scenario":"learnable","variant":"benchmark","total_return":0.48105557509876995,"cagr":1.193525616531148,"mdd":0.007368431805399589,"costs":22990.851335466683,"final_nav":148105.557509877,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0027305899921181436,"trades":691,"mean_exposure":0.5},{"seed":1634635432866334191,"scenario":"learnable","variant":"scaled","total_return":0.8635214315554163,"cagr":2.472712125866348,"mdd":0.00639667660381904,"costs":25879.79063826065,"final_nav":186352.14315554162,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002575280535374393,"trades":539,"mean_exposure":0.4988630045802842},{"seed":1634635432866334191,"scenario":"null","variant":"candidate","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":1634635432866334191,"scenario":"null","variant":"iteration2","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":1634635432866334191,"scenario":"null","variant":"benchmark","total_return":-0.05224318281853413,"cagr":-0.10175701548605742,"mdd":0.061156581700016255,"costs":18211.529512313893,"final_nav":94775.68171814659,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0033806980629516393,"trades":695,"mean_exposure":0.5},{"seed":1634635432866334191,"scenario":"reversal","variant":"candidate","total_return":-0.11608906596128998,"cagr":-0.21870146068681517,"mdd":0.11608906596128998,"costs":3115.2372166834834,"final_nav":88391.093403871,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0032217073400820483,"trades":125,"mean_exposure":0.0874371708236961},{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration2","total_return":0.3277627983841651,"cagr":0.7629540487729491,"mdd":0.0006481066970512872,"costs":8953.867364098383,"final_nav":132776.27983841652,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.001490322580568601,"trades":280,"mean_exposure":0.20275200936874727},{"seed":1634635432866334191,"scenario":"reversal","variant":"benchmark","total_return":-0.3677335509493157,"cagr":-0.6002391374048384,"mdd":0.3677335509493157,"costs":15054.907708128032,"final_nav":63226.64490506843,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.003380698062951627,"trades":692,"mean_exposure":0.5},{"seed":1634635432866334191,"scenario":"outer_noise","variant":"candidate","total_return":0.8567061080069394,"cagr":2.447357571510276,"mdd":0.005598346966235068,"costs":25928.747486069988,"final_nav":185670.61080069395,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002246067112811993,"trades":706,"mean_exposure":0.4915491463397735},{"seed":1634635432866334191,"scenario":"outer_noise","variant":"iteration2","total_return":0.15613973447898277,"cagr":0.3366590856411329,"mdd":0.0010003859442387908,"costs":4117.223624134512,"final_nav":115613.97344789827,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0008791720831319065,"trades":138,"mean_exposure":0.10073127024621309},{"seed":1634635432866334191,"scenario":"outer_noise","variant":"benchmark","total_return":0.4672185277845873,"cagr":1.1527302082743716,"mdd":0.010762430028337766,"costs":22841.138351069356,"final_nav":146721.85277845873,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0035132374901476683,"trades":691,"mean_exposure":0.5},{"seed":5015368413594993126,"scenario":"learnable","variant":"candidate","total_return":0.8611443345975147,"cagr":2.4638582342044257,"mdd":0.0020496628915205317,"costs":25731.06284980566,"final_nav":186114.43345975148,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0019394342118703978,"trades":688,"mean_exposure":0.4870375040799655},{"seed":5015368413594993126,"scenario":"learnable","variant":"iteration2","total_return":0.4899570339954422,"cagr":1.2199719631524952,"mdd":0.000994720088371981,"costs":12336.450302365996,"final_nav":148995.70339954423,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0014630736802362623,"trades":360,"mean_exposure":0.2652163828735844},{"seed":5015368413594993126,"scenario":"learnable","variant":"benchmark","total_return":0.5741608338490665,"cagr":1.4779823308243882,"mdd":0.0017752091754812405,"costs":24081.679072921157,"final_nav":157416.08338490664,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002677556047913142,"trades":692,"mean_exposure":0.5},{"seed":5015368413594993126,"scenario":"learnable","variant":"scaled","total_return":0.9660857845289041,"cagr":2.8654933121266364,"mdd":0.0014977533699451762,"costs":27030.699789999755,"final_nav":196608.57845289042,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002909151317805578,"trades":531,"mean_exposure":0.4962504967922432},{"seed":5015368413594993126,"scenario":"null","variant":"candidate","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":5015368413594993126,"scenario":"null","variant":"iteration2","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":5015368413594993126,"scenario":"null","variant":"benchmark","total_return":0.013446916680871723,"cagr":0.027074652929965692,"mdd":0.030896027009147176,"costs":18881.47104106435,"final_nav":101344.69166808718,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0031560749335864196,"trades":691,"mean_exposure":0.5},{"seed":5015368413594993126,"scenario":"reversal","variant":"candidate","total_return":-0.09932318634435422,"cagr":-0.18878127734311312,"mdd":0.09932318634435422,"costs":3041.6181921266652,"final_nav":90067.68136556458,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0030038860486007236,"trades":121,"mean_exposure":0.0849147521816611},{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration2","total_return":0.015109808669263147,"cagr":0.030447923656548026,"mdd":0.026284545213899002,"costs":1766.579904717346,"final_nav":101510.98086692631,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002317184721766586,"trades":65,"mean_exposure":0.047104875506691894},{"seed":5015368413594993126,"scenario":"reversal","variant":"benchmark","total_return":-0.3287406821718124,"cagr":-0.5494109282288362,"mdd":0.3287406821718124,"costs":15531.624670052439,"final_nav":67125.93178281876,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.003408127944546198,"trades":690,"mean_exposure":0.5},{"seed":5015368413594993126,"scenario":"outer_noise","variant":"candidate","total_return":0.7992162433793686,"cagr":2.237179090440167,"mdd":0.001522190839828963,"costs":20479.54793575007,"final_nav":179921.62433793687,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002724292764837972,"trades":537,"mean_exposure":0.39607254635474404},{"seed":5015368413594993126,"scenario":"outer_noise","variant":"iteration2","total_return":0.4889905679446782,"cagr":1.2170929114282152,"mdd":0.001522190839829185,"costs":11852.516870654441,"final_nav":148899.05679446782,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0021288421002953707,"trades":346,"mean_exposure":0.2557156431102246},{"seed":5015368413594993126,"scenario":"outer_noise","variant":"benchmark","total_return":0.6018000908631125,"cagr":1.5657635310890754,"mdd":0.0035572180682594823,"costs":24365.500441176115,"final_nav":160180.00908631124,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0021300965856244627,"trades":692,"mean_exposure":0.5},{"seed":3584306075979195116,"scenario":"learnable","variant":"candidate","total_return":0.8954416618367764,"cagr":2.592699093426561,"mdd":0.0013262361874661899,"costs":26398.728940425906,"final_nav":189544.16618367765,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0017494203512605736,"trades":710,"mean_exposure":0.49456477157997963},{"seed":3584306075979195116,"scenario":"learnable","variant":"iteration2","total_return":0.08770191605740218,"cagr":0.183095458194944,"mdd":0.0009689169948781107,"costs":2149.2696734320807,"final_nav":108770.19160574023,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0007297366295642403,"trades":75,"mean_exposure":0.05444557961260058},{"seed":3584306075979195116,"scenario":"learnable","variant":"benchmark","total_return":0.5109318564790837,"cagr":1.2829150749233302,"mdd":0.00539072752005243,"costs":23661.73148542008,"final_nav":151093.18564790837,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0018248886295925857,"trades":692,"mean_exposure":0.5},{"seed":3584306075979195116,"scenario":"learnable","variant":"scaled","total_return":0.9151154109356636,"cagr":2.667667037203276,"mdd":0.0016668108299155993,"costs":26381.854557174407,"final_nav":191511.54109356637,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0026241305268908575,"trades":534,"mean_exposure":0.4974383645997597},{"seed":3584306075979195116,"scenario":"null","variant":"candidate","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":3584306075979195116,"scenario":"null","variant":"iteration2","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0},{"seed":3584306075979195116,"scenario":"null","variant":"benchmark","total_return":0.00638376346489844,"cagr":0.012808279365772668,"mdd":0.0334943355219397,"costs":18789.50833969456,"final_nav":100638.37634648984,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.003004547721390877,"trades":691,"mean_exposure":0.5},{"seed":3584306075979195116,"scenario":"reversal","variant":"candidate","total_return":-0.10362440974389797,"cagr":-0.19651080119302466,"mdd":0.10362440974389797,"costs":3112.1634844739756,"final_nav":89637.5590256102,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002923011157214521,"trades":124,"mean_exposure":0.08745282346965874},{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration2","total_return":0.1962153471843755,"cagr":0.43093115683943606,"mdd":0.009289614086369413,"costs":6583.174756888624,"final_nav":119621.53471843754,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0026713974023778427,"trades":222,"mean_exposure":0.15982432498341242},{"seed":3584306075979195116,"scenario":"reversal","variant":"benchmark","total_return":-0.3295449775783236,"cagr":-0.5504900629095494,"mdd":0.3295449775783236,"costs":15375.41778562892,"final_nav":67045.50224216764,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0033777103126367515,"trades":691,"mean_exposure":0.5},{"seed":3584306075979195116,"scenario":"outer_noise","variant":"candidate","total_return":0.8755190363051262,"cagr":2.517571655542909,"mdd":0.0015761012824380138,"costs":21619.948379440422,"final_nav":187551.90363051262,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0024867754390757177,"trades":560,"mean_exposure":0.4076901962653527},{"seed":3584306075979195116,"scenario":"outer_noise","variant":"iteration2","total_return":0.0943484538067405,"cagr":0.1975985383492036,"mdd":0.0015761012824380138,"costs":2152.4201129854046,"final_nav":109434.84538067406,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0011590843672022368,"trades":75,"mean_exposure":0.05442187919443346},{"seed":3584306075979195116,"scenario":"outer_noise","variant":"benchmark","total_return":0.5210568954545496,"cagr":1.3136140792098328,"mdd":0.007696845614057368,"costs":23716.578978991987,"final_nav":152105.68954545495,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002381110786990742,"trades":692,"mean_exposure":0.5}],"paired":[{"seed":1564008556893530022,"scenario":"learnable","comparator":"iteration2","return_delta":0.4642032364083557,"cagr_delta":1.5081765713118322,"mdd_delta":0.0009946284770017133,"cost_delta":16159.34105177057},{"seed":1564008556893530022,"scenario":"learnable","comparator":"scaled","return_delta":-0.03815966691454076,"cagr_delta":-0.14314913583583122,"mdd_delta":-0.0037107228361490385,"cost_delta":-18.025689952432003},{"seed":1564008556893530022,"scenario":"learnable","comparator":"benchmark","return_delta":0.31093293738546723,"cagr_delta":1.057864673062678,"mdd_delta":-0.0033412681855626847,"cost_delta":2513.3082019637804},{"seed":1564008556893530022,"scenario":"null","comparator":"iteration2","return_delta":0.0,"cagr_delta":0.0,"mdd_delta":0.0,"cost_delta":0.0},{"seed":1564008556893530022,"scenario":"null","comparator":"benchmark","return_delta":0.01290983758249431,"cagr_delta":0.025653011258582215,"mdd_delta":-0.0453760384892129,"cost_delta":-19082.702029076776},{"seed":1564008556893530022,"scenario":"reversal","comparator":"iteration2","return_delta":-0.386814882248007,"cagr_delta":-0.8510341800775592,"mdd_delta":0.06624634393545803,"cost_delta":-6370.733538876244},{"seed":1564008556893530022,"scenario":"reversal","comparator":"benchmark","return_delta":0.26488668231906454,"cagr_delta":0.4101520128746985,"mdd_delta":-0.2653927548657128,"cost_delta":-12346.034079420839},{"seed":1564008556893530022,"scenario":"outer_noise","comparator":"iteration2","return_delta":0.493319298362894,"cagr_delta":1.5718029507613018,"mdd_delta":0.004640885418041418,"cost_delta":17183.005759445252},{"seed":1564008556893530022,"scenario":"outer_noise","comparator":"benchmark","return_delta":0.2978977070585134,"cagr_delta":1.0073706770858473,"mdd_delta":-0.0017140387666106927,"cost_delta":2181.5590665082054},{"seed":1634635432866334191,"scenario":"learnable","comparator":"iteration2","return_delta":0.5340718828636979,"cagr_delta":1.6943439912137377,"mdd_delta":0.0032998237953457688,"cost_delta":17337.869133726464},{"seed":1634635432866334191,"scenario":"learnable","comparator":"scaled","return_delta":-0.010234607444019606,"cagr_delta":-0.038040073441441,"mdd_delta":-0.002400983032889714,"cost_delta":234.10789543336068},{"seed":1634635432866334191,"scenario":"learnable","comparator":"benchmark","return_delta":0.3722312490126267,"cagr_delta":1.241146435893759,"mdd_delta":-0.0033727382344702628,"cost_delta":3123.0471982273266},{"seed":1634635432866334191,"scenario":"null","comparator":"iteration2","return_delta":0.0,"cagr_delta":0.0,"mdd_delta":0.0,"cost_delta":0.0},{"seed":1634635432866334191,"scenario":"null","comparator":"benchmark","return_delta":0.05224318281853413,"cagr_delta":0.10175701548605742,"mdd_delta":-0.061156581700016255,"cost_delta":-18211.529512313893},{"seed":1634635432866334191,"scenario":"reversal","comparator":"iteration2","return_delta":-0.4438518643454551,"cagr_delta":-0.9816555094597643,"mdd_delta":0.1154409592642387,"cost_delta":-5838.6301474149},{"seed":1634635432866334191,"scenario":"reversal","comparator":"benchmark","return_delta":0.2516444849880257,"cagr_delta":0.3815376767180232,"mdd_delta":-0.2516444849880257,"cost_delta":-11939.670491444549},{"seed":1634635432866334191,"scenario":"outer_noise","comparator":"iteration2","return_delta":0.7005663735279566,"cagr_delta":2.1106984858691433,"mdd_delta":0.004597961021996277,"cost_delta":21811.523861935475},{"seed":1634635432866334191,"scenario":"outer_noise","comparator":"benchmark","return_delta":0.3894875802223521,"cagr_delta":1.2946273632359047,"mdd_delta":-0.005164083062102698,"cost_delta":3087.609135000632},{"seed":5015368413594993126,"scenario":"learnable","comparator":"iteration2","return_delta":0.3711873006020725,"cagr_delta":1.2438862710519305,"mdd_delta":0.0010549428031485508,"cost_delta":13394.612547439665},{"seed":5015368413594993126,"scenario":"learnable","comparator":"scaled","return_delta":-0.10494144993138943,"cagr_delta":-0.40163507792221065,"mdd_delta":0.0005519095215753556,"cost_delta":-1299.6369401940938},{"seed":5015368413594993126,"scenario":"learnable","comparator":"benchmark","return_delta":0.28698350074844825,"cagr_delta":0.9858759033800375,"mdd_delta":0.00027445371603929125,"cost_delta":1649.3837768845042},{"seed":5015368413594993126,"scenario":"null","comparator":"iteration2","return_delta":0.0,"cagr_delta":0.0,"mdd_delta":0.0,"cost_delta":0.0},{"seed":5015368413594993126,"scenario":"null","comparator":"benchmark","return_delta":-0.013446916680871723,"cagr_delta":-0.027074652929965692,"mdd_delta":-0.030896027009147176,"cost_delta":-18881.47104106435},{"seed":5015368413594993126,"scenario":"reversal","comparator":"iteration2","return_delta":-0.11443299501361737,"cagr_delta":-0.21922920099966114,"mdd_delta":0.07303864113045522,"cost_delta":1275.0382874093193},{"seed":5015368413594993126,"scenario":"reversal","comparator":"benchmark","return_delta":0.22941749582745818,"cagr_delta":0.3606296508857231,"mdd_delta":-0.22941749582745818,"cost_delta":-12490.006477925774},{"seed":5015368413594993126,"scenario":"outer_noise","comparator":"iteration2","return_delta":0.3102256754346904,"cagr_delta":1.020086179011952,"mdd_delta":-2.220446049250313e-16,"cost_delta":8627.031065095629},{"seed":5015368413594993126,"scenario":"outer_noise","comparator":"benchmark","return_delta":0.1974161525162561,"cagr_delta":0.6714155593510918,"mdd_delta":-0.0020350272284305193,"cost_delta":-3885.952505426045},{"seed":3584306075979195116,"scenario":"learnable","comparator":"iteration2","return_delta":0.8077397457793742,"cagr_delta":2.409603635231617,"mdd_delta":0.0003573191925880792,"cost_delta":24249.459266993825},{"seed":3584306075979195116,"scenario":"learnable","comparator":"scaled","return_delta":-0.019673749098887194,"cagr_delta":-0.07496794377671501,"mdd_delta":-0.0003405746424494094,"cost_delta":16.87438325149924},{"seed":3584306075979195116,"scenario":"learnable","comparator":"benchmark","return_delta":0.38450980535769275,"cagr_delta":1.3097840185032306,"mdd_delta":-0.00406449133258624,"cost_delta":2736.997455005825},{"seed":3584306075979195116,"scenario":"null","comparator":"iteration2","return_delta":0.0,"cagr_delta":0.0,"mdd_delta":0.0,"cost_delta":0.0},{"seed":3584306075979195116,"scenario":"null","comparator":"benchmark","return_delta":-0.00638376346489844,"cagr_delta":-0.012808279365772668,"mdd_delta":-0.0334943355219397,"cost_delta":-18789.50833969456},{"seed":3584306075979195116,"scenario":"reversal","comparator":"iteration2","return_delta":-0.29983975692827347,"cagr_delta":-0.6274419580324607,"mdd_delta":0.09433479565752856,"cost_delta":-3471.0112724146484},{"seed":3584306075979195116,"scenario":"reversal","comparator":"benchmark","return_delta":0.2259205678344256,"cagr_delta":0.3539792617165247,"mdd_delta":-0.2259205678344256,"cost_delta":-12263.254301154946},{"seed":3584306075979195116,"scenario":"outer_noise","comparator":"iteration2","return_delta":0.7811705824983857,"cagr_delta":2.3199731171937055,"mdd_delta":0.0,"cost_delta":19467.528266455018},{"seed":3584306075979195116,"scenario":"outer_noise","comparator":"benchmark","return_delta":0.3544621408505766,"cagr_delta":1.2039575763330763,"mdd_delta":-0.006120744331619354,"cost_delta":-2096.630599551565}],"real_pit_audit":{"status":"BLOCKED","real_rows":0,"reason":"No release-timestamped real predictor dataset supplied or acquired.","adapter":"validate_pit; schema in pit_schema.json","missing":["revision histories","release and availability timestamps","coverage/missingness audit","independent regime OOS rank IC >0.1 evidence"],"local_evidence":[{"path":"/opt/mts/sector-leadership-independent/pilot_2019_sample.csv","sha256":"b686917c2f3ceaefcb91c6fec053eb8b98b69af66424858cba6be72c15f6ddcb","reason":"Annual summarized provisional observations; no release/revision provenance."},{"path":"/opt/mts/sector-leadership-independent/reports/offline-provisional-2019/observations.csv","sha256":"9927b45a7faec6acc781a2a1c778859a1a28c351e25f3e7b035e0cdea1a379e8","reason":"Monthly provisional observations; no release/vintage/source-hash fields."},{"path":"/opt/mts/sector-leadership-independent/manifest.json","sha256":"9684e85103b917df05192327d4ab74ba48c4bcf69caff81c2b4ca7ba258e8549","reason":"Explicit certified=false, PIT coverage unverified;2019/2020 contaminated."}]},"sgov":{"status":"UNAVAILABLE_REAL_DATA","comparison":"Cash zero-yield control has return/CAGR/MDD/costs 0; no fabricated SGOV series"},"engineering_blocker":"FAIL: five-tier support missing on2/4 stable seeds; reversal442 false GREAT before22-session latch and negative net return. Real PIT information and trusted timestamp absent; corrected independent benchmark coverage incomplete.","recommended_next_decision":"Do not promote or optimize this bundle. Retain as gate-repair evidence; first specify acceptable reversal exposure and acquire provenance-complete real PIT predictors. Use a new externally committed protocol for any future validation.","post_freeze_benchmark_correction":{"reason":"Original benchmark forecast-ranked cash-limited purchases; invalid independent control.","additional_replays":4,"evaluated_scenarios":["learnable"],"incomplete_scenarios":["null","reversal","outer_noise"],"untouched_test":false,"runs":[{"seed":1564008556893530022,"scenario":"learnable","variant":"corrected_equal_universe","total_return":0.0012100007917366096,"cagr":0.002421465685389146,"mdd":0.022706316339030863,"costs":19194.585079138906,"final_nav":100121.00007917365,"trades":1512},{"seed":1634635432866334191,"scenario":"learnable","variant":"corrected_equal_universe","total_return":-0.022751766007440333,"cagr":-0.04498588915842339,"mdd":0.03225819886723702,"costs":18594.00594861596,"final_nav":97724.82339925597,"trades":1512},{"seed":5015368413594993126,"scenario":"learnable","variant":"corrected_equal_universe","total_return":0.03000399146943411,"cagr":0.06090822244296601,"mdd":0.015172876533262714,"costs":19141.388367254258,"final_nav":103000.39914694341,"trades":1512},{"seed":3584306075979195116,"scenario":"learnable","variant":"corrected_equal_universe","total_return":0.005221912988778055,"cagr":0.010471094352818566,"mdd":0.03103160661240656,"costs":18944.136993032975,"final_nav":100522.1912988778,"trades":1512}],"paired":[{"seed":1564008556893530022,"scenario":"learnable","candidate_return":0.8565803518951918,"benchmark_return":0.0012100007917366096,"return_delta":0.8553703511034552,"cagr_delta":2.444469137357885,"mdd_delta":-0.02074277086715104,"cost_delta":7196.149237344529},{"seed":1634635432866334191,"scenario":"learnable","candidate_return":0.8532868241113967,"benchmark_return":-0.022751766007440333,"return_delta":0.876038590118837,"cagr_delta":2.4796579415833304,"mdd_delta":-0.028262505296307694,"cost_delta":7519.892585078051},{"seed":5015368413594993126,"scenario":"learnable","candidate_return":0.8611443345975147,"benchmark_return":0.03000399146943411,"return_delta":0.8311403431280806,"cagr_delta":2.40295001176146,"mdd_delta":-0.013123213641742182,"cost_delta":6589.674482551403},{"seed":3584306075979195116,"scenario":"learnable","candidate_return":0.8954416618367764,"benchmark_return":0.005221912988778055,"return_delta":0.8902197488479984,"cagr_delta":2.5822279990737425,"mdd_delta":-0.02970537042494037,"cost_delta":7454.591947392932}],"invalid_original_rows":"All variant=benchmark rows in metrics.csv and corresponding paired comparisons are invalid as independent controls; retained as evidence of ranking confound."},"compute_accounting":{"initial_phase_a_seconds":1.968,"runner_seconds":27.84563373005949,"benchmark_correction_seconds":0.24051805003546178,"total_measured_seconds":30.05415178009495,"phase_a_replays":6,"phase_b_replays":52,"post_freeze_control_correction_replays":4,"limit":64,"stopped":true},"artifact_audit":{"funded_trade_matches":8551,"max_net_ledger_error":4.440892098500626e-16,"min_cash":0.0,"max_modeled_risk":0.019970044932601107,"frozen_sources_match":true},"recommendation_status":{"P1_gate":"IMPLEMENTED sensor/full disagreement; no price-only veto, train-only threshold; stable coverage recovers.","P2_independent_dates":"IMPLEMENTED 734 sessions,400 fit/200 cal dates, original bands. Radii pass but per-seed five-tier support fails.","P3_outer_holdout":"PARTIAL four OS entropy seeds after local hash commitment, separate noise variant; trusted public timestamp unavailable. All evaluated tapes now viewed.","P4_disjoint_calibration":"IMPLEMENTED embargoed chronological disjoint ranges; mutation tests show calibration cannot alter point coefficients. Statistical correlation need not literally be zero in finite samples.","P5_sequential_monitor":"IMPLEMENTED cell/look union bound with stated DGP subGaussian envelope; stable0/12 but only4 independent seeds. Reversal22-session lag is unsafe.","P6_horizon_ledger":"IMPLEMENTED all-opportunity one-session open-to-exit ledger, matched funded horizons, costs/cash/final liquidation/risk/gap audits. Original variable holding manager not replayed; synthetic one-session harness only.","P7_real_PIT":"ADAPTER/AUDIT ONLY; no accepted real rows or real OOS IC. Local provisional artifacts lack complete revision/release provenance. NO alpha claim."},"limitations":["Four seeds do not establish a <=5% stable alarm probability;0/12 paired scenario units is not12 independent seeds.","Conditional mean intervals and latent-individual/realized tier confusion are different estimands. Date_mean_predictive_interval_coverage is a diagnostic hit rate for date means, not nominal prediction coverage.","Sensor/full gate threshold calibrated only on fit distribution; no formal conformal reliability guarantee.","Benchmark control correction is post-freeze, with learnable-only coverage; no independent benchmark evidence for other scenarios.","No real SGOV data, SGOV-relative return unavailable. Cash zero is a synthetic control.","Source freeze manifests cover new core files; imported original dependency hashes were not committed comprehensively before seed generation.","Injected sensors and cost-grossup DGP cannot establish real alpha. Fresh seeds do not make the inherited DGP untouched.","Original baseline estimator unmodified, but its portfolio policy uses new one-session harness and has126-date warmup rather than candidate400 fit/200 cal dates.","CAGR/MDD from synthetic126-session windows and open marks only; no intraday risk or aggregate2% risk guarantee."]}
```


## discrimination_iteration5/seeds.json

```
[1564008556893530022, 1634635432866334191, 5015368413594993126, 3584306075979195116]
```


## discrimination_iteration5/test_experiment.py

```
import copy,unittest
import experiment as e
class EngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p,cls.f,cls.truth=e.generate(77,'learnable')
    def test_bands_and_abstain(self):
        for mu,t in zip(e.MU,e.TIERS):self.assertEqual(e.label(mu,.0001,200,200),t)
        self.assertEqual(e.label(.004,.003,400,200),'UNKNOWN')
        self.assertEqual(e.label(.012,.001,99,200),'UNKNOWN')
    def test_disjoint_and_calibration_not_point_fit(self):
        self.assertLess(max(e.FIT)+2,min(e.CAL));self.assertLess(max(e.CAL)+2,e.START)
        m=e.fit(self.p,self.f);p=copy.deepcopy(self.p)
        # All calibration execution prices changed, keeping fit and its price predictors intact.
        for i in range(min(e.CAL)+1,max(e.CAL)+3):p[i]=[x*(1+.0001*(i-min(e.CAL))) for x in p[i]]
        changed=e.fit(p,self.f)
        for a,b in zip(m,changed):
            for key in ['mean','slope','center','threshold']:self.assertEqual(a[key],b[key])
        self.assertTrue(any(a['radius']!=b['radius'] for a,b in zip(m,changed)))
        self.assertTrue(all(len(a['train_dates'])<=400 and len(a['cal_dates'])<=200 for a in m))
    def test_test_outcomes_not_fit_and_future_not_prediction(self):
        states,m,_=e.predict(self.p,self.f);p=copy.deepcopy(self.p)
        for i in range(e.START+12,e.N):p[i]=[x*.9 for x in p[i]]
        ss,mm,_=e.predict(p,self.f)
        self.assertEqual(m,mm);self.assertEqual(states['candidate'][:10],ss['candidate'][:10])
    def test_gate_has_coverage_without_price_only(self):
        ss,m,a=e.predict(self.p,self.f)
        self.assertGreater(sum(z['label']!='UNKNOWN' for row in ss['candidate'] for z in row),0)
    def test_monitor_maturity_and_multiplicity(self):
        m=e.fit(self.p,self.f)
        self.assertEqual(e.monitor(self.p,self.f,m,e.START+21),[])
        p,f,_=e.generate(88,'reversal');_,_,alarms=e.predict(p,f)
        for a in alarms:self.assertLessEqual(a['last_signal']+3,a['index']);self.assertGreater(a['threshold'],.01)
    def test_ledger_cash_risk_horizon_costs(self):
        ss,_,_=e.predict(self.p,self.f);metric,trades,daily=e.replay(self.p,ss['candidate'],scale=1.5)
        self.assertLessEqual(metric['max_modeled_risk'],.02+1e-12)
        self.assertTrue(all(d['cash']>=0 for d in daily));self.assertGreater(metric['costs'],0)
        for t in trades:
            self.assertEqual(t['exit_index'],t['entry_index']+1)
            self.assertAlmostEqual(t['net'],e.observed(self.p,t['signal'],t['j']))
        cash,tt,dd=e.replay(self.p,ss['candidate'],'cash');self.assertEqual(cash['total_return'],0);self.assertEqual(tt,[])
    def test_gap_audit_is_not_realized_cap(self):
        p=copy.deepcopy(self.p)
        for i in range(e.START+2,e.N):p[i]=[x*.5 for x in p[i]]
        ss=[[dict(mean=.012,label='GREAT') for _ in range(24)] for i in range(126)]
        metric,_,_=e.replay(p,ss)
        self.assertGreater(metric['gap_loss_exceedances'],0)
    def test_pit_rejects_missing_future_and_accepts_provenance(self):
        with self.assertRaises(ValueError):e.validate_pit([{}])
        row=dict(asset='X',feature='f',value=1,event_time='2020-01-01T00:00:00+00:00',release_time='2020-01-02T00:00:00+00:00',available_time='2020-01-02T01:00:00+00:00',decision_time='2020-01-03T00:00:00+00:00',revision_id='r0',source_uri='local:fixture',source_sha256='a'*64,vintage_id='v0')
        self.assertEqual(e.validate_pit([row]),[row]);row['available_time']='2021-01-01T00:00:00+00:00'
        with self.assertRaises(ValueError):e.validate_pit([row])
    def test_original_baseline_integration(self):
        ss,alarms=e.baseline(self.p,self.f);self.assertEqual(len(ss),126);self.assertEqual(len(ss[0]),24)
if __name__=='__main__':unittest.main()

```


## discrimination_iteration5/tests.log

```
test_bands_and_abstain (test_experiment.EngineeringTests.test_bands_and_abstain) ... ok
test_disjoint_and_calibration_not_point_fit (test_experiment.EngineeringTests.test_disjoint_and_calibration_not_point_fit) ... ok
test_gap_audit_is_not_realized_cap (test_experiment.EngineeringTests.test_gap_audit_is_not_realized_cap) ... ok
test_gate_has_coverage_without_price_only (test_experiment.EngineeringTests.test_gate_has_coverage_without_price_only) ... ok
test_ledger_cash_risk_horizon_costs (test_experiment.EngineeringTests.test_ledger_cash_risk_horizon_costs) ... ok
test_monitor_maturity_and_multiplicity (test_experiment.EngineeringTests.test_monitor_maturity_and_multiplicity) ... ok
test_original_baseline_integration (test_experiment.EngineeringTests.test_original_baseline_integration) ... ok
test_pit_rejects_missing_future_and_accepts_provenance (test_experiment.EngineeringTests.test_pit_rejects_missing_future_and_accepts_provenance) ... ok
test_test_outcomes_not_fit_and_future_not_prediction (test_experiment.EngineeringTests.test_test_outcomes_not_fit_and_future_not_prediction) ... ok

----------------------------------------------------------------------
Ran 9 tests in 2.017s

OK

```


## discrimination_iteration5/tier_metrics.csv

```
seed,scenario,variant,tier,n,coverage,mean_net
1564008556893530022,learnable,candidate,TERRIBLE,625,0.20667989417989419,-0.011808901656127434
1564008556893530022,learnable,candidate,POOR,547,0.18088624338624337,-0.004187883405108388
1564008556893530022,learnable,candidate,AVERAGE,615,0.20337301587301587,-0.00021324321695498008
1564008556893530022,learnable,candidate,GOOD,629,0.2080026455026455,0.0037893853007694676
1564008556893530022,learnable,candidate,GREAT,608,0.20105820105820105,0.011326047204352674
1564008556893530022,learnable,candidate,UNKNOWN,0,0.0,
1564008556893530022,learnable,ungated,TERRIBLE,625,0.20667989417989419,-0.011808901656127434
1564008556893530022,learnable,ungated,POOR,547,0.18088624338624337,-0.004187883405108388
1564008556893530022,learnable,ungated,AVERAGE,615,0.20337301587301587,-0.00021324321695498008
1564008556893530022,learnable,ungated,GOOD,629,0.2080026455026455,0.0037893853007694676
1564008556893530022,learnable,ungated,GREAT,608,0.20105820105820105,0.011326047204352674
1564008556893530022,learnable,ungated,UNKNOWN,0,0.0,
1564008556893530022,learnable,iteration2,TERRIBLE,327,0.10813492063492064,-0.012014290583248127
1564008556893530022,learnable,iteration2,POOR,62,0.0205026455026455,-0.00457703167078967
1564008556893530022,learnable,iteration2,AVERAGE,5,0.0016534391534391533,-0.002176123182500778
1564008556893530022,learnable,iteration2,GOOD,45,0.01488095238095238,0.0027773344590529764
1564008556893530022,learnable,iteration2,GREAT,310,0.10251322751322751,0.012374994060399417
1564008556893530022,learnable,iteration2,UNKNOWN,2275,0.7523148148148148,-0.00011895335860590224
1564008556893530022,null,candidate,TERRIBLE,0,0.0,
1564008556893530022,null,candidate,POOR,0,0.0,
1564008556893530022,null,candidate,AVERAGE,0,0.0,
1564008556893530022,null,candidate,GOOD,0,0.0,
1564008556893530022,null,candidate,GREAT,0,0.0,
1564008556893530022,null,candidate,UNKNOWN,3024,1.0,-0.00017616411430913532
1564008556893530022,null,ungated,TERRIBLE,0,0.0,
1564008556893530022,null,ungated,POOR,0,0.0,
1564008556893530022,null,ungated,AVERAGE,0,0.0,
1564008556893530022,null,ungated,GOOD,0,0.0,
1564008556893530022,null,ungated,GREAT,0,0.0,
1564008556893530022,null,ungated,UNKNOWN,3024,1.0,-0.00017616411430913532
1564008556893530022,null,iteration2,TERRIBLE,0,0.0,
1564008556893530022,null,iteration2,POOR,0,0.0,
1564008556893530022,null,iteration2,AVERAGE,0,0.0,
1564008556893530022,null,iteration2,GOOD,0,0.0,
1564008556893530022,null,iteration2,GREAT,0,0.0,
1564008556893530022,null,iteration2,UNKNOWN,3024,1.0,-0.00017616411430913532
1564008556893530022,reversal,candidate,TERRIBLE,99,0.03273809523809524,0.01273720636786141
1564008556893530022,reversal,candidate,POOR,113,0.03736772486772487,0.004451808893025798
1564008556893530022,reversal,candidate,AVERAGE,110,0.036375661375661374,0.0005076811626964474
1564008556893530022,reversal,candidate,GOOD,97,0.03207671957671958,-0.0033138382933164514
1564008556893530022,reversal,candidate,GREAT,109,0.036044973544973546,-0.010351595743813884
1564008556893530022,reversal,candidate,UNKNOWN,2496,0.8253968253968254,-0.0003617134592829408
1564008556893530022,reversal,ungated,TERRIBLE,608,0.20105820105820105,0.011326047204352674
1564008556893530022,reversal,ungated,POOR,629,0.2080026455026455,0.0037893853007694676
1564008556893530022,reversal,ungated,AVERAGE,615,0.20337301587301587,-0.00021324321695498008
1564008556893530022,reversal,ungated,GOOD,547,0.18088624338624337,-0.004187883405108388
1564008556893530022,reversal,ungated,GREAT,625,0.20667989417989419,-0.011808901656127434
1564008556893530022,reversal,ungated,UNKNOWN,0,0.0,
1564008556893530022,reversal,iteration2,TERRIBLE,310,0.10251322751322751,-0.010125150572958505
1564008556893530022,reversal,iteration2,POOR,20,0.006613756613756613,-0.0030577359323574692
1564008556893530022,reversal,iteration2,AVERAGE,8,0.0026455026455026454,0.002920681461854313
1564008556893530022,reversal,iteration2,GOOD,56,0.018518518518518517,2.826035150614779e-05
1564008556893530022,reversal,iteration2,GREAT,310,0.10251322751322751,0.009752277322251335
1564008556893530022,reversal,iteration2,UNKNOWN,2320,0.7671957671957672,-0.00016419089943259984
1564008556893530022,outer_noise,candidate,TERRIBLE,625,0.20667989417989419,-0.011805927070159278
1564008556893530022,outer_noise,candidate,POOR,405,0.13392857142857142,-0.0040959873874485755
1564008556893530022,outer_noise,candidate,AVERAGE,0,0.0,
1564008556893530022,outer_noise,candidate,GOOD,369,0.12202380952380952,0.003754973616158615
1564008556893530022,outer_noise,candidate,GREAT,608,0.20105820105820105,0.011233216900177697
1564008556893530022,outer_noise,candidate,UNKNOWN,1017,0.33630952380952384,0.0001320529193777213
1564008556893530022,outer_noise,ungated,TERRIBLE,625,0.20667989417989419,-0.011805927070159278
1564008556893530022,outer_noise,ungated,POOR,405,0.13392857142857142,-0.0040959873874485755
1564008556893530022,outer_noise,ungated,AVERAGE,0,0.0,
1564008556893530022,outer_noise,ungated,GOOD,369,0.12202380952380952,0.003754973616158615
1564008556893530022,outer_noise,ungated,GREAT,608,0.20105820105820105,0.011233216900177697
1564008556893530022,outer_noise,ungated,UNKNOWN,1017,0.33630952380952384,0.0001320529193777213
1564008556893530022,outer_noise,iteration2,TERRIBLE,297,0.09821428571428571,-0.012412427431497872
1564008556893530022,outer_noise,iteration2,POOR,3,0.000992063492063492,-0.013651354588843997
1564008556893530022,outer_noise,iteration2,AVERAGE,0,0.0,
1564008556893530022,outer_noise,iteration2,GOOD,0,0.0,
1564008556893530022,outer_noise,iteration2,GREAT,283,0.09358465608465609,0.011672789687446495
1564008556893530022,outer_noise,iteration2,UNKNOWN,2441,0.8072089947089947,-0.00010809292204607466
1634635432866334191,learnable,candidate,TERRIBLE,590,0.19510582010582012,-0.011604076738985798
1634635432866334191,learnable,candidate,POOR,0,0.0,
1634635432866334191,learnable,candidate,AVERAGE,623,0.20601851851851852,0.00019152115570782787
1634635432866334191,learnable,candidate,GOOD,634,0.20965608465608465,0.003819305918870422
1634635432866334191,learnable,candidate,GREAT,591,0.19543650793650794,0.011613602375653606
1634635432866334191,learnable,candidate,UNKNOWN,586,0.19378306878306878,-0.004073908096419612
1634635432866334191,learnable,ungated,TERRIBLE,590,0.19510582010582012,-0.011604076738985798
1634635432866334191,learnable,ungated,POOR,0,0.0,
1634635432866334191,learnable,ungated,AVERAGE,623,0.20601851851851852,0.00019152115570782787
1634635432866334191,learnable,ungated,GOOD,634,0.20965608465608465,0.003819305918870422
1634635432866334191,learnable,ungated,GREAT,591,0.19543650793650794,0.011613602375653606
1634635432866334191,learnable,ungated,UNKNOWN,586,0.19378306878306878,-0.004073908096419612
1634635432866334191,learnable,iteration2,TERRIBLE,274,0.09060846560846561,-0.011332586247073962
1634635432866334191,learnable,iteration2,POOR,75,0.0248015873015873,-0.002352200519517883
1634635432866334191,learnable,iteration2,AVERAGE,4,0.0013227513227513227,-0.001405489920398989
1634635432866334191,learnable,iteration2,GOOD,65,0.021494708994708994,0.004055006373952751
1634635432866334191,learnable,iteration2,GREAT,276,0.09126984126984126,0.011562645775458059
1634635432866334191,learnable,iteration2,UNKNOWN,2330,0.7705026455026455,1.279484157914857e-06
1634635432866334191,null,candidate,TERRIBLE,0,0.0,
1634635432866334191,null,candidate,POOR,0,0.0,
1634635432866334191,null,candidate,AVERAGE,0,0.0,
1634635432866334191,null,candidate,GOOD,0,0.0,
1634635432866334191,null,candidate,GREAT,0,0.0,
1634635432866334191,null,candidate,UNKNOWN,3024,1.0,5.644220108385968e-05
1634635432866334191,null,ungated,TERRIBLE,0,0.0,
1634635432866334191,null,ungated,POOR,0,0.0,
1634635432866334191,null,ungated,AVERAGE,0,0.0,
1634635432866334191,null,ungated,GOOD,0,0.0,
1634635432866334191,null,ungated,GREAT,0,0.0,
1634635432866334191,null,ungated,UNKNOWN,3024,1.0,5.644220108385968e-05
1634635432866334191,null,iteration2,TERRIBLE,0,0.0,
1634635432866334191,null,iteration2,POOR,0,0.0,
1634635432866334191,null,iteration2,AVERAGE,0,0.0,
1634635432866334191,null,iteration2,GOOD,0,0.0,
1634635432866334191,null,iteration2,GREAT,0,0.0,
1634635432866334191,null,iteration2,UNKNOWN,3024,1.0,5.644220108385968e-05
1634635432866334191,reversal,candidate,TERRIBLE,107,0.035383597883597885,0.011589912814816944
1634635432866334191,reversal,candidate,POOR,0,0.0,
1634635432866334191,reversal,candidate,AVERAGE,115,0.03802910052910053,0.0011677230005208421
1634635432866334191,reversal,candidate,GOOD,83,0.027447089947089946,-0.004944568527376031
1634635432866334191,reversal,candidate,GREAT,124,0.041005291005291,-0.012793778227899046
1634635432866334191,reversal,candidate,UNKNOWN,2595,0.8581349206349206,0.0003056262380978705
1634635432866334191,reversal,ungated,TERRIBLE,591,0.19543650793650794,0.011613602375653606
1634635432866334191,reversal,ungated,POOR,0,0.0,
1634635432866334191,reversal,ungated,AVERAGE,623,0.20601851851851852,0.00019152115570782787
1634635432866334191,reversal,ungated,GOOD,586,0.19378306878306878,-0.004073908096419612
1634635432866334191,reversal,ungated,GREAT,590,0.19510582010582012,-0.011604076738985798
1634635432866334191,reversal,ungated,UNKNOWN,634,0.20965608465608465,0.003819305918870422
1634635432866334191,reversal,iteration2,TERRIBLE,282,0.09325396825396826,-0.011359564658091403
1634635432866334191,reversal,iteration2,POOR,68,0.022486772486772486,-0.0027413768988429703
1634635432866334191,reversal,iteration2,AVERAGE,4,0.0013227513227513227,-0.001405489920398989
1634635432866334191,reversal,iteration2,GOOD,65,0.021494708994708994,0.004055006373952751
1634635432866334191,reversal,iteration2,GREAT,280,0.09259259259259259,0.011628875942058248
1634635432866334191,reversal,iteration2,UNKNOWN,2325,0.7688492063492064,1.9979939947977308e-05
1634635432866334191,outer_noise,candidate,TERRIBLE,590,0.19510582010582012,-0.011572892533901745
1634635432866334191,outer_noise,candidate,POOR,0,0.0,
1634635432866334191,outer_noise,candidate,AVERAGE,554,0.1832010582010582,-0.00011823264221916804
1634635432866334191,outer_noise,candidate,GOOD,354,0.11706349206349206,0.0037708078568672457
1634635432866334191,outer_noise,candidate,GREAT,590,0.19510582010582012,0.01158767630685429
1634635432866334191,outer_noise,candidate,UNKNOWN,936,0.30952380952380953,-0.0011770683797933763
1634635432866334191,outer_noise,ungated,TERRIBLE,590,0.19510582010582012,-0.011572892533901745
1634635432866334191,outer_noise,ungated,POOR,0,0.0,
1634635432866334191,outer_noise,ungated,AVERAGE,554,0.1832010582010582,-0.00011823264221916804
1634635432866334191,outer_noise,ungated,GOOD,354,0.11706349206349206,0.0037708078568672457
1634635432866334191,outer_noise,ungated,GREAT,591,0.19543650793650794,0.011598221243678663
1634635432866334191,outer_noise,ungated,UNKNOWN,935,0.3091931216931217,-0.001197385815461667
1634635432866334191,outer_noise,iteration2,TERRIBLE,148,0.04894179894179894,-0.011227624485746622
1634635432866334191,outer_noise,iteration2,POOR,0,0.0,
1634635432866334191,outer_noise,iteration2,AVERAGE,0,0.0,
1634635432866334191,outer_noise,iteration2,GOOD,0,0.0,
1634635432866334191,outer_noise,iteration2,GREAT,163,0.0539021164021164,0.011557845300118242
1634635432866334191,outer_noise,iteration2,UNKNOWN,2713,0.8971560846560847,-1.6914426808619833e-05
5015368413594993126,learnable,candidate,TERRIBLE,626,0.207010582010582,-0.011005088785009042
5015368413594993126,learnable,candidate,POOR,611,0.20205026455026456,-0.0034620957066898296
5015368413594993126,learnable,candidate,AVERAGE,621,0.20535714285714285,-0.00032482216685101857
5015368413594993126,learnable,candidate,GOOD,307,0.10152116402116403,0.004637057617469859
5015368413594993126,learnable,candidate,GREAT,561,0.18551587301587302,0.011885252458697412
5015368413594993126,learnable,candidate,UNKNOWN,298,0.09854497354497355,0.0034881765171797287
5015368413594993126,learnable,ungated,TERRIBLE,626,0.207010582010582,-0.011005088785009042
5015368413594993126,learnable,ungated,POOR,611,0.20205026455026456,-0.0034620957066898296
5015368413594993126,learnable,ungated,AVERAGE,621,0.20535714285714285,-0.00032482216685101857
5015368413594993126,learnable,ungated,GOOD,307,0.10152116402116403,0.004637057617469859
5015368413594993126,learnable,ungated,GREAT,561,0.18551587301587302,0.011885252458697412
5015368413594993126,learnable,ungated,UNKNOWN,298,0.09854497354497355,0.0034881765171797287
5015368413594993126,learnable,iteration2,TERRIBLE,408,0.1349206349206349,-0.010476138321430324
5015368413594993126,learnable,iteration2,POOR,123,0.040674603174603176,-0.003541291419707649
5015368413594993126,learnable,iteration2,AVERAGE,36,0.011904761904761904,-0.0037198382045604303
5015368413594993126,learnable,iteration2,GOOD,31,0.01025132275132275,0.0056678232668861675
5015368413594993126,learnable,iteration2,GREAT,361,0.11937830687830688,0.012249558834471905
5015368413594993126,learnable,iteration2,UNKNOWN,2065,0.6828703703703703,8.251985123892767e-05
5015368413594993126,null,candidate,TERRIBLE,0,0.0,
5015368413594993126,null,candidate,POOR,0,0.0,
5015368413594993126,null,candidate,AVERAGE,0,0.0,
5015368413594993126,null,candidate,GOOD,0,0.0,
5015368413594993126,null,candidate,GREAT,0,0.0,
5015368413594993126,null,candidate,UNKNOWN,3024,1.0,-2.4987004565335336e-05
5015368413594993126,null,ungated,TERRIBLE,0,0.0,
5015368413594993126,null,ungated,POOR,0,0.0,
5015368413594993126,null,ungated,AVERAGE,0,0.0,
5015368413594993126,null,ungated,GOOD,0,0.0,
5015368413594993126,null,ungated,GREAT,0,0.0,
5015368413594993126,null,ungated,UNKNOWN,3024,1.0,-2.4987004565335336e-05
5015368413594993126,null,iteration2,TERRIBLE,0,0.0,
5015368413594993126,null,iteration2,POOR,0,0.0,
5015368413594993126,null,iteration2,AVERAGE,0,0.0,
5015368413594993126,null,iteration2,GOOD,0,0.0,
5015368413594993126,null,iteration2,GREAT,0,0.0,
5015368413594993126,null,iteration2,UNKNOWN,3024,1.0,-2.4987004565335336e-05
5015368413594993126,reversal,candidate,TERRIBLE,100,0.03306878306878307,0.01063901115541441
5015368413594993126,reversal,candidate,POOR,109,0.036044973544973546,0.0031931952045537847
5015368413594993126,reversal,candidate,AVERAGE,118,0.03902116402116402,-0.0012563031559831616
5015368413594993126,reversal,candidate,GOOD,41,0.013558201058201057,-0.0064979323170623535
5015368413594993126,reversal,candidate,GREAT,107,0.035383597883597885,-0.011100615900011828
5015368413594993126,reversal,candidate,UNKNOWN,2549,0.8429232804232805,4.507838527401235e-05
5015368413594993126,reversal,ungated,TERRIBLE,561,0.18551587301587302,0.011885252458697412
5015368413594993126,reversal,ungated,POOR,603,0.19940476190476192,0.00411656623320124
5015368413594993126,reversal,ungated,AVERAGE,621,0.20535714285714285,-0.00032482216685101857
5015368413594993126,reversal,ungated,GOOD,315,0.10416666666666667,-0.00307326954773798
5015368413594993126,reversal,ungated,GREAT,626,0.207010582010582,-0.011005088785009042
5015368413594993126,reversal,ungated,UNKNOWN,298,0.09854497354497355,-0.003914418514052228
5015368413594993126,reversal,iteration2,TERRIBLE,77,0.02546296296296296,-0.001046078898129242
5015368413594993126,reversal,iteration2,POOR,27,0.008928571428571428,0.001592724624446065
5015368413594993126,reversal,iteration2,AVERAGE,0,0.0,
5015368413594993126,reversal,iteration2,GOOD,0,0.0,
5015368413594993126,reversal,iteration2,GREAT,71,0.023478835978835978,0.003674636599887817
5015368413594993126,reversal,iteration2,UNKNOWN,2849,0.9421296296296297,-0.00010491940684510397
5015368413594993126,outer_noise,candidate,TERRIBLE,626,0.207010582010582,-0.010801089415766105
5015368413594993126,outer_noise,candidate,POOR,0,0.0,
5015368413594993126,outer_noise,candidate,AVERAGE,0,0.0,
5015368413594993126,outer_noise,candidate,GOOD,0,0.0,
5015368413594993126,outer_noise,candidate,GREAT,561,0.18551587301587302,0.011920736696366414
5015368413594993126,outer_noise,candidate,UNKNOWN,1837,0.607473544973545,9.281317928745686e-05
5015368413594993126,outer_noise,ungated,TERRIBLE,626,0.207010582010582,-0.010801089415766105
5015368413594993126,outer_noise,ungated,POOR,0,0.0,
5015368413594993126,outer_noise,ungated,AVERAGE,0,0.0,
5015368413594993126,outer_noise,ungated,GOOD,0,0.0,
5015368413594993126,outer_noise,ungated,GREAT,561,0.18551587301587302,0.011920736696366414
5015368413594993126,outer_noise,ungated,UNKNOWN,1837,0.607473544973545,9.281317928745686e-05
5015368413594993126,outer_noise,iteration2,TERRIBLE,408,0.1349206349206349,-0.010134388588062428
5015368413594993126,outer_noise,iteration2,POOR,43,0.014219576719576719,-0.0045668255884897535
5015368413594993126,outer_noise,iteration2,AVERAGE,3,0.000992063492063492,0.009495167706374522
5015368413594993126,outer_noise,iteration2,GOOD,0,0.0,
5015368413594993126,outer_noise,iteration2,GREAT,361,0.11937830687830688,0.012367350205139738
5015368413594993126,outer_noise,iteration2,UNKNOWN,2209,0.730489417989418,-2.9581602624266637e-05
3584306075979195116,learnable,candidate,TERRIBLE,611,0.20205026455026456,-0.011398275828236196
3584306075979195116,learnable,candidate,POOR,625,0.20667989417989419,-0.004094822937389787
3584306075979195116,learnable,candidate,AVERAGE,0,0.0,
3584306075979195116,learnable,candidate,GOOD,578,0.19113756613756613,0.004560837504971879
3584306075979195116,learnable,candidate,GREAT,598,0.19775132275132276,0.01231028255970228
3584306075979195116,learnable,candidate,UNKNOWN,612,0.20238095238095238,-0.00021324022703956414
3584306075979195116,learnable,ungated,TERRIBLE,611,0.20205026455026456,-0.011398275828236196
3584306075979195116,learnable,ungated,POOR,625,0.20667989417989419,-0.004094822937389787
3584306075979195116,learnable,ungated,AVERAGE,0,0.0,
3584306075979195116,learnable,ungated,GOOD,578,0.19113756613756613,0.004560837504971879
3584306075979195116,learnable,ungated,GREAT,598,0.19775132275132276,0.01231028255970228
3584306075979195116,learnable,ungated,UNKNOWN,612,0.20238095238095238,-0.00021324022703956414
3584306075979195116,learnable,iteration2,TERRIBLE,73,0.02414021164021164,-0.011445871998577986
3584306075979195116,learnable,iteration2,POOR,0,0.0,
3584306075979195116,learnable,iteration2,AVERAGE,0,0.0,
3584306075979195116,learnable,iteration2,GOOD,11,0.0036375661375661374,0.003003833329420477
3584306075979195116,learnable,iteration2,GREAT,81,0.026785714285714284,0.013508064398996529
3584306075979195116,learnable,iteration2,UNKNOWN,2859,0.9454365079365079,1.8171540979507704e-05
3584306075979195116,null,candidate,TERRIBLE,0,0.0,
3584306075979195116,null,candidate,POOR,0,0.0,
3584306075979195116,null,candidate,AVERAGE,0,0.0,
3584306075979195116,null,candidate,GOOD,0,0.0,
3584306075979195116,null,candidate,GREAT,0,0.0,
3584306075979195116,null,candidate,UNKNOWN,3024,1.0,0.00011362406174158851
3584306075979195116,null,ungated,TERRIBLE,0,0.0,
3584306075979195116,null,ungated,POOR,0,0.0,
3584306075979195116,null,ungated,AVERAGE,0,0.0,
3584306075979195116,null,ungated,GOOD,0,0.0,
3584306075979195116,null,ungated,GREAT,0,0.0,
3584306075979195116,null,ungated,UNKNOWN,3024,1.0,0.00011362406174158851
3584306075979195116,null,iteration2,TERRIBLE,0,0.0,
3584306075979195116,null,iteration2,POOR,0,0.0,
3584306075979195116,null,iteration2,AVERAGE,0,0.0,
3584306075979195116,null,iteration2,GOOD,0,0.0,
3584306075979195116,null,iteration2,GREAT,0,0.0,
3584306075979195116,null,iteration2,UNKNOWN,3024,1.0,0.00011362406174158851
3584306075979195116,reversal,candidate,TERRIBLE,112,0.037037037037037035,0.013268175910562832
3584306075979195116,reversal,candidate,POOR,98,0.032407407407407406,0.004194206509773938
3584306075979195116,reversal,candidate,AVERAGE,0,0.0,
3584306075979195116,reversal,candidate,GOOD,110,0.036375661375661374,-0.003223737978314251
3584306075979195116,reversal,candidate,GREAT,112,0.037037037037037035,-0.010986488971418294
3584306075979195116,reversal,candidate,UNKNOWN,2592,0.8571428571428571,1.22026100227998e-05
3584306075979195116,reversal,ungated,TERRIBLE,598,0.19775132275132276,0.01231028255970228
3584306075979195116,reversal,ungated,POOR,578,0.19113756613756613,0.004560837504971879
3584306075979195116,reversal,ungated,AVERAGE,0,0.0,
3584306075979195116,reversal,ungated,GOOD,625,0.20667989417989419,-0.004094822937389787
3584306075979195116,reversal,ungated,GREAT,611,0.20205026455026456,-0.011398275828236196
3584306075979195116,reversal,ungated,UNKNOWN,612,0.20238095238095238,-0.00021324022703956414
3584306075979195116,reversal,iteration2,TERRIBLE,219,0.07242063492063493,-0.011781276453632524
3584306075979195116,reversal,iteration2,POOR,0,0.0,
3584306075979195116,reversal,iteration2,AVERAGE,47,0.015542328042328041,-0.0025258754700738986
3584306075979195116,reversal,iteration2,GOOD,111,0.03670634920634921,0.004649782128162074
3584306075979195116,reversal,iteration2,GREAT,205,0.06779100529100529,0.009660123066693059
3584306075979195116,reversal,iteration2,UNKNOWN,2442,0.8075396825396826,0.00022357240304975127
3584306075979195116,outer_noise,candidate,TERRIBLE,611,0.20205026455026456,-0.011313311233740405
3584306075979195116,outer_noise,candidate,POOR,0,0.0,
3584306075979195116,outer_noise,candidate,AVERAGE,0,0.0,
3584306075979195116,outer_noise,candidate,GOOD,0,0.0,
3584306075979195116,outer_noise,candidate,GREAT,598,0.19775132275132276,0.012441364905313463
3584306075979195116,outer_noise,candidate,UNKNOWN,1815,0.6001984126984127,-1.104185222514289e-06
3584306075979195116,outer_noise,ungated,TERRIBLE,611,0.20205026455026456,-0.011313311233740405
3584306075979195116,outer_noise,ungated,POOR,0,0.0,
3584306075979195116,outer_noise,ungated,AVERAGE,0,0.0,
3584306075979195116,outer_noise,ungated,GOOD,0,0.0,
3584306075979195116,outer_noise,ungated,GREAT,598,0.19775132275132276,0.012441364905313463
3584306075979195116,outer_noise,ungated,UNKNOWN,1815,0.6001984126984127,-1.104185222514289e-06
3584306075979195116,outer_noise,iteration2,TERRIBLE,73,0.02414021164021164,-0.011334737258496392
3584306075979195116,outer_noise,iteration2,POOR,0,0.0,
3584306075979195116,outer_noise,iteration2,AVERAGE,0,0.0,
3584306075979195116,outer_noise,iteration2,GOOD,0,0.0,
3584306075979195116,outer_noise,iteration2,GREAT,81,0.026785714285714284,0.013983845930844436
3584306075979195116,outer_noise,iteration2,UNKNOWN,2870,0.9490740740740741,7.673980935715614e-05

```


## discrimination_iteration5/opportunities.jsonl.gz exact ledger counts and samples
```json
{"group_counts":{"(None, 1564008556893530022, 'learnable', 'candidate')":{"rows":3024,"funded_opportunities":713,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'learnable', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'learnable', 'iteration2')":{"rows":3024,"funded_opportunities":309,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'null', 'candidate')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'null', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'null', 'iteration2')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'reversal', 'candidate')":{"rows":3024,"funded_opportunities":129,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'reversal', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'reversal', 'iteration2')":{"rows":3024,"funded_opportunities":310,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'outer_noise', 'candidate')":{"rows":3024,"funded_opportunities":700,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'outer_noise', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1564008556893530022, 'outer_noise', 'iteration2')":{"rows":3024,"funded_opportunities":271,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'learnable', 'candidate')":{"rows":3024,"funded_opportunities":711,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'learnable', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'learnable', 'iteration2')":{"rows":3024,"funded_opportunities":276,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'null', 'candidate')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'null', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'null', 'iteration2')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'reversal', 'candidate')":{"rows":3024,"funded_opportunities":125,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'reversal', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'reversal', 'iteration2')":{"rows":3024,"funded_opportunities":280,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'outer_noise', 'candidate')":{"rows":3024,"funded_opportunities":706,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'outer_noise', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 1634635432866334191, 'outer_noise', 'iteration2')":{"rows":3024,"funded_opportunities":138,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'learnable', 'candidate')":{"rows":3024,"funded_opportunities":688,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'learnable', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'learnable', 'iteration2')":{"rows":3024,"funded_opportunities":360,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'null', 'candidate')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'null', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'null', 'iteration2')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'reversal', 'candidate')":{"rows":3024,"funded_opportunities":121,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'reversal', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'reversal', 'iteration2')":{"rows":3024,"funded_opportunities":65,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'outer_noise', 'candidate')":{"rows":3024,"funded_opportunities":537,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'outer_noise', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 5015368413594993126, 'outer_noise', 'iteration2')":{"rows":3024,"funded_opportunities":346,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'learnable', 'candidate')":{"rows":3024,"funded_opportunities":710,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'learnable', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'learnable', 'iteration2')":{"rows":3024,"funded_opportunities":75,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'null', 'candidate')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'null', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'null', 'iteration2')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'reversal', 'candidate')":{"rows":3024,"funded_opportunities":124,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'reversal', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'reversal', 'iteration2')":{"rows":3024,"funded_opportunities":222,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'outer_noise', 'candidate')":{"rows":3024,"funded_opportunities":560,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'outer_noise', 'ungated')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"(None, 3584306075979195116, 'outer_noise', 'iteration2')":{"rows":3024,"funded_opportunities":75,"trades":0,"daily_rows":0}},"samples":{"(None, 1564008556893530022, 'learnable', 'candidate')|funded":{"source_line":1,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.00405788501607661,"radius":0.0014877986789342645,"reason":"INTERVAL","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1564008556893530022, 'learnable', 'candidate')|other":{"source_line":5,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"candidate","index":606,"j":4,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.011573821791557295,"radius":0.0013566971752532841,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.01754330334537213,"one_session_net":-0.01754330334537213,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'learnable', 'candidate')|AVERAGE":{"source_line":9,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"candidate","index":606,"j":8,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":8.503373074909002e-05,"radius":0.0017991577026671163,"reason":"INTERVAL","true_ev":0,"realized_net":0.0023916107031118905,"one_session_net":0.0023916107031118905,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'learnable', 'ungated')|other":{"source_line":3025,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.00405788501607661,"radius":0.0014877986789342645,"reason":"INTERVAL","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'learnable', 'ungated')|AVERAGE":{"source_line":3033,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"ungated","index":606,"j":8,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":8.503373074909002e-05,"radius":0.0017991577026671163,"reason":"INTERVAL","true_ev":0,"realized_net":0.0023916107031118905,"one_session_net":0.0023916107031118905,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'learnable', 'iteration2')|other":{"source_line":6049,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.004298144234757758,"radius":0.0017239336438597116,"reason":"BOUNDARY_UNCERTAINTY","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'learnable', 'iteration2')|funded":{"source_line":6050,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration2","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.01260342352596921,"radius":0.0023898301913329255,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.026054962502402912,"one_session_net":0.026054962502402912,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1564008556893530022, 'learnable', 'iteration2')|AVERAGE":{"source_line":8573,"row":{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration2","index":711,"j":4,"execution_index":712,"exit_index":713,"available_index":714,"inferred_tier":"AVERAGE","inferred_net":-0.0004818861597468857,"radius":0.0014519419567915214,"reason":"CONFIDENT","true_ev":0,"realized_net":-0.005919909376148724,"one_session_net":-0.005919909376148724,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'null', 'candidate')|other":{"source_line":9073,"row":{"seed":1564008556893530022,"scenario":"null","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-8.185188237499992e-05,"radius":0.0013519435058480498,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'null', 'ungated')|other":{"source_line":12097,"row":{"seed":1564008556893530022,"scenario":"null","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-8.185188237499992e-05,"radius":0.0013519435058480498,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'null', 'iteration2')|other":{"source_line":15121,"row":{"seed":1564008556893530022,"scenario":"null","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.001678651219138551,"radius":0.0023811463502703377,"reason":"BOUNDARY_UNCERTAINTY","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'reversal', 'candidate')|other":{"source_line":18145,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"POOR","inferred_net":-0.003941865440512114,"radius":0.0014724029132433493,"reason":"INTERVAL","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'reversal', 'candidate')|false_GREAT":{"source_line":18149,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"candidate","index":606,"j":4,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.012116866314005569,"radius":0.0015275784472445657,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.01754330334537213,"one_session_net":-0.01754330334537213,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1564008556893530022, 'reversal', 'candidate')|AVERAGE":{"source_line":18153,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"candidate","index":606,"j":8,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":8.503373074909002e-05,"radius":0.0017991577026671163,"reason":"INTERVAL","true_ev":0,"realized_net":0.0023916107031118905,"one_session_net":0.0023916107031118905,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'reversal', 'candidate')|funded":{"source_line":18154,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"candidate","index":606,"j":9,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.004071071015419479,"radius":0.0015009846782771332,"reason":"INTERVAL","true_ev":-0.004,"realized_net":0.0019088709971941675,"one_session_net":0.0019088709971941675,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1564008556893530022, 'reversal', 'ungated')|other":{"source_line":21169,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"POOR","inferred_net":-0.003941865440512114,"radius":0.0014724029132433493,"reason":"INTERVAL","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'reversal', 'ungated')|false_GREAT":{"source_line":21173,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"ungated","index":606,"j":4,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.012116866314005569,"radius":0.0015275784472445657,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.01754330334537213,"one_session_net":-0.01754330334537213,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'reversal', 'ungated')|AVERAGE":{"source_line":21177,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"ungated","index":606,"j":8,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":8.503373074909002e-05,"radius":0.0017991577026671163,"reason":"INTERVAL","true_ev":0,"realized_net":0.0023916107031118905,"one_session_net":0.0023916107031118905,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'reversal', 'iteration2')|other":{"source_line":24193,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.004323672316591036,"radius":0.0022854037313991306,"reason":"BOUNDARY_UNCERTAINTY","true_ev":0.004,"realized_net":-0.00017168006808920833,"one_session_net":-0.00017168006808920833,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'reversal', 'iteration2')|false_GREAT":{"source_line":24197,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration2","index":606,"j":4,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.01260342352596921,"radius":0.0023898301913329255,"reason":"CONFIDENT","true_ev":-0.012,"realized_net":-0.01754330334537213,"one_session_net":-0.01754330334537213,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1564008556893530022, 'reversal', 'iteration2')|funded":{"source_line":24221,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration2","index":607,"j":4,"execution_index":608,"exit_index":609,"available_index":610,"inferred_tier":"GOOD","inferred_net":0.004308659173096749,"radius":0.0015525995605179782,"reason":"CONFIDENT","true_ev":0,"realized_net":0.0033646745584461346,"one_session_net":0.0033646745584461346,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":9980.114309042092}},"(None, 1564008556893530022, 'reversal', 'iteration2')|AVERAGE":{"source_line":25437,"row":{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration2","index":657,"j":20,"execution_index":658,"exit_index":659,"available_index":660,"inferred_tier":"AVERAGE","inferred_net":0.00019996392527156441,"radius":0.0016253908123619505,"reason":"CONFIDENT","true_ev":0,"realized_net":0.01424998431731428,"one_session_net":0.01424998431731428,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'outer_noise', 'candidate')|funded":{"source_line":27217,"row":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.004043297242308236,"radius":0.0018891632036572314,"reason":"INTERVAL","true_ev":0.004,"realized_net":-0.001214600085111428,"one_session_net":-0.001214600085111428,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1564008556893530022, 'outer_noise', 'candidate')|other":{"source_line":27221,"row":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"candidate","index":606,"j":4,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.01151855592249857,"radius":0.0017182634011544482,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.0189291291817153,"one_session_net":-0.0189291291817153,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'outer_noise', 'ungated')|other":{"source_line":30241,"row":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.004043297242308236,"radius":0.0018891632036572314,"reason":"INTERVAL","true_ev":0.004,"realized_net":-0.001214600085111428,"one_session_net":-0.001214600085111428,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'outer_noise', 'iteration2')|other":{"source_line":33265,"row":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.003986140172319084,"radius":0.002565542556650222,"reason":"INSUFFICIENT_MATURE_DATES","true_ev":0.004,"realized_net":-0.001214600085111428,"one_session_net":-0.001214600085111428,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1564008556893530022, 'outer_noise', 'iteration2')|funded":{"source_line":33415,"row":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"iteration2","index":612,"j":6,"execution_index":613,"exit_index":614,"available_index":615,"inferred_tier":"GREAT","inferred_net":0.013070613603736092,"radius":0.0030305886011871308,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.008092479777317196,"one_session_net":0.008092479777317196,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1634635432866334191, 'learnable', 'candidate')|other":{"source_line":36289,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.004457864092225274,"radius":0.0018326196708796424,"reason":"INTERVAL","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'learnable', 'candidate')|funded":{"source_line":36290,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"candidate","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011725870445423356,"radius":0.001352497111067186,"reason":"INTERVAL","true_ev":0.012,"realized_net":0.015943195952868416,"one_session_net":0.015943195952868416,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1634635432866334191, 'learnable', 'candidate')|AVERAGE":{"source_line":36299,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"candidate","index":606,"j":10,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00028253675829431054,"radius":0.001126011282279309,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008637944296869926,"one_session_net":-0.008637944296869926,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'learnable', 'ungated')|other":{"source_line":39313,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.004457864092225274,"radius":0.0018326196708796424,"reason":"INTERVAL","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'learnable', 'ungated')|AVERAGE":{"source_line":39323,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"ungated","index":606,"j":10,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00028253675829431054,"radius":0.001126011282279309,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008637944296869926,"one_session_net":-0.008637944296869926,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'learnable', 'iteration2')|other":{"source_line":42337,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.002884449521773738,"radius":0.004807405777847566,"reason":"DRIFT_QUARANTINE","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'learnable', 'iteration2')|funded":{"source_line":43923,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration2","index":672,"j":2,"execution_index":673,"exit_index":674,"available_index":675,"inferred_tier":"GREAT","inferred_net":0.012484150257348153,"radius":0.002371730540317189,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.005599991561118234,"one_session_net":0.005599991561118234,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1634635432866334191, 'learnable', 'iteration2')|AVERAGE":{"source_line":45077,"row":{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration2","index":720,"j":4,"execution_index":721,"exit_index":722,"available_index":723,"inferred_tier":"AVERAGE","inferred_net":0.00020903769859933886,"radius":0.0016705514404107868,"reason":"CONFIDENT","true_ev":0,"realized_net":-0.0019168581841191301,"one_session_net":-0.0019168581841191301,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'null', 'candidate')|other":{"source_line":45361,"row":{"seed":1634635432866334191,"scenario":"null","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":1.9427271094386057e-05,"radius":0.0015953112912994582,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'null', 'ungated')|other":{"source_line":48385,"row":{"seed":1634635432866334191,"scenario":"null","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":1.9427271094386057e-05,"radius":0.0015953112912994582,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'null', 'iteration2')|other":{"source_line":51409,"row":{"seed":1634635432866334191,"scenario":"null","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.0009173110531719362,"radius":0.003360037900179991,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'reversal', 'candidate')|funded":{"source_line":54433,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.003839343085178752,"radius":0.0014178085621761542,"reason":"INTERVAL","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1634635432866334191, 'reversal', 'candidate')|other":{"source_line":54434,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"candidate","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.011916752890559809,"radius":0.0015196509913548866,"reason":"INTERVAL","true_ev":0.012,"realized_net":0.015943195952868416,"one_session_net":0.015943195952868416,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'reversal', 'candidate')|false_GREAT":{"source_line":54437,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"candidate","index":606,"j":4,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011827452779554765,"radius":0.0012604026104663848,"reason":"INTERVAL","true_ev":-0.012,"realized_net":0.0011268766553573784,"one_session_net":0.0011268766553573784,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1634635432866334191, 'reversal', 'candidate')|AVERAGE":{"source_line":54443,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"candidate","index":606,"j":10,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00028253675829431054,"radius":0.001126011282279309,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008637944296869926,"one_session_net":-0.008637944296869926,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'reversal', 'ungated')|other":{"source_line":57457,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.003839343085178752,"radius":0.0014178085621761542,"reason":"INTERVAL","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'reversal', 'ungated')|false_GREAT":{"source_line":57461,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"ungated","index":606,"j":4,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011827452779554765,"radius":0.0012604026104663848,"reason":"INTERVAL","true_ev":-0.012,"realized_net":0.0011268766553573784,"one_session_net":0.0011268766553573784,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'reversal', 'ungated')|AVERAGE":{"source_line":57467,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"ungated","index":606,"j":10,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00028253675829431054,"radius":0.001126011282279309,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008637944296869926,"one_session_net":-0.008637944296869926,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'reversal', 'iteration2')|other":{"source_line":60481,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.005567011354341587,"radius":0.003842213879596351,"reason":"DRIFT_QUARANTINE","true_ev":-0.004,"realized_net":0.01210381008565986,"one_session_net":0.01210381008565986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'reversal', 'iteration2')|funded":{"source_line":62041,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration2","index":671,"j":0,"execution_index":672,"exit_index":673,"available_index":674,"inferred_tier":"GREAT","inferred_net":0.012592901105789011,"radius":0.0023525740957186705,"reason":"CONFIDENT","true_ev":0.004,"realized_net":0.005995590011836249,"one_session_net":0.005995590011836249,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1634635432866334191, 'reversal', 'iteration2')|AVERAGE":{"source_line":63221,"row":{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration2","index":720,"j":4,"execution_index":721,"exit_index":722,"available_index":723,"inferred_tier":"AVERAGE","inferred_net":0.00020903769859933886,"radius":0.0016705514404107868,"reason":"CONFIDENT","true_ev":0,"realized_net":-0.0019168581841191301,"one_session_net":-0.0019168581841191301,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'outer_noise', 'candidate')|other":{"source_line":63505,"row":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.00453543423749298,"radius":0.0022888604149391067,"reason":"INTERVAL","true_ev":-0.004,"realized_net":0.01612976260707466,"one_session_net":0.01612976260707466,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'outer_noise', 'candidate')|funded":{"source_line":63506,"row":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"candidate","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011649605209880119,"radius":0.001744314866386874,"reason":"INTERVAL","true_ev":0.012,"realized_net":0.016928994941085573,"one_session_net":0.016928994941085573,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 1634635432866334191, 'outer_noise', 'candidate')|AVERAGE":{"source_line":63515,"row":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"candidate","index":606,"j":10,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.0003064585494696586,"radius":0.001460581952538745,"reason":"INTERVAL","true_ev":0,"realized_net":-0.010797430371087158,"one_session_net":-0.010797430371087158,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'outer_noise', 'ungated')|other":{"source_line":66529,"row":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.00453543423749298,"radius":0.0022888604149391067,"reason":"INTERVAL","true_ev":-0.004,"realized_net":0.01612976260707466,"one_session_net":0.01612976260707466,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'outer_noise', 'ungated')|AVERAGE":{"source_line":66539,"row":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"ungated","index":606,"j":10,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.0003064585494696586,"radius":0.001460581952538745,"reason":"INTERVAL","true_ev":0,"realized_net":-0.010797430371087158,"one_session_net":-0.010797430371087158,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'outer_noise', 'iteration2')|other":{"source_line":69553,"row":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.002471948456839069,"radius":0.005875643776931313,"reason":"DRIFT_QUARANTINE","true_ev":-0.004,"realized_net":0.01612976260707466,"one_session_net":0.01612976260707466,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 1634635432866334191, 'outer_noise', 'iteration2')|funded":{"source_line":71139,"row":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"iteration2","index":672,"j":2,"execution_index":673,"exit_index":674,"available_index":675,"inferred_tier":"GREAT","inferred_net":0.012716822409812329,"radius":0.0029373183262102072,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.0039999894513975676,"one_session_net":0.0039999894513975676,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 5015368413594993126, 'learnable', 'candidate')|other":{"source_line":72577,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"POOR","inferred_net":-0.004176022337985152,"radius":0.0014925999287972455,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'learnable', 'candidate')|AVERAGE":{"source_line":72578,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"candidate","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00020212422669061583,"radius":0.0016887135764618103,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008119028743839962,"one_session_net":-0.008119028743839962,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'learnable', 'candidate')|funded":{"source_line":72579,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"candidate","index":606,"j":2,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.01166510592077785,"radius":0.001883294177271276,"reason":"INTERVAL","true_ev":0.012,"realized_net":0.017845065370593938,"one_session_net":0.017845065370593938,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 5015368413594993126, 'learnable', 'ungated')|other":{"source_line":75601,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"POOR","inferred_net":-0.004176022337985152,"radius":0.0014925999287972455,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'learnable', 'ungated')|AVERAGE":{"source_line":75602,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"ungated","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00020212422669061583,"radius":0.0016887135764618103,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008119028743839962,"one_session_net":-0.008119028743839962,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'learnable', 'iteration2')|other":{"source_line":78625,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"POOR","inferred_net":-0.0041125825238367405,"radius":0.001661066250465482,"reason":"CONFIDENT","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'learnable', 'iteration2')|funded":{"source_line":78627,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"iteration2","index":606,"j":2,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.013720030861184741,"radius":0.002444979674706305,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.017845065370593938,"one_session_net":0.017845065370593938,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 5015368413594993126, 'learnable', 'iteration2')|AVERAGE":{"source_line":79083,"row":{"seed":5015368413594993126,"scenario":"learnable","variant":"iteration2","index":625,"j":2,"execution_index":626,"exit_index":627,"available_index":628,"inferred_tier":"AVERAGE","inferred_net":0.0001957782019331611,"radius":0.0017264869552711991,"reason":"CONFIDENT","true_ev":0,"realized_net":-0.008978772875206098,"one_session_net":-0.008978772875206098,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'null', 'candidate')|other":{"source_line":81649,"row":{"seed":5015368413594993126,"scenario":"null","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.0005580263908460235,"radius":0.002092240983502034,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'null', 'ungated')|other":{"source_line":84673,"row":{"seed":5015368413594993126,"scenario":"null","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.0005580263908460235,"radius":0.002092240983502034,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'null', 'iteration2')|other":{"source_line":87697,"row":{"seed":5015368413594993126,"scenario":"null","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.00021112656086046794,"radius":0.004240763728670929,"reason":"DRIFT_QUARANTINE","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'reversal', 'candidate')|funded":{"source_line":90721,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.003905563813404369,"radius":0.0018953138116802395,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 5015368413594993126, 'reversal', 'candidate')|AVERAGE":{"source_line":90722,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"candidate","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00020212422669061583,"radius":0.0016887135764618103,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008119028743839962,"one_session_net":-0.008119028743839962,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'reversal', 'candidate')|other":{"source_line":90723,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"candidate","index":606,"j":2,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.012177797967129023,"radius":0.0012994438853522767,"reason":"INTERVAL","true_ev":0.012,"realized_net":0.017845065370593938,"one_session_net":0.017845065370593938,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'reversal', 'candidate')|false_GREAT":{"source_line":90724,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"candidate","index":606,"j":3,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.01166514520272111,"radius":0.0018832548953280153,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.01182537851322596,"one_session_net":-0.01182537851322596,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":8230.45267489712}},"(None, 5015368413594993126, 'reversal', 'ungated')|other":{"source_line":93745,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.003905563813404369,"radius":0.0018953138116802395,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'reversal', 'ungated')|AVERAGE":{"source_line":93746,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"ungated","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"AVERAGE","inferred_net":-0.00020212422669061583,"radius":0.0016887135764618103,"reason":"INTERVAL","true_ev":0,"realized_net":-0.008119028743839962,"one_session_net":-0.008119028743839962,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'reversal', 'ungated')|false_GREAT":{"source_line":93748,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"ungated","index":606,"j":3,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.01166514520272111,"radius":0.0018832548953280153,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.01182537851322596,"one_session_net":-0.01182537851322596,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'reversal', 'iteration2')|other":{"source_line":96769,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.0048182397338910185,"radius":0.002572706097057362,"reason":"BOUNDARY_UNCERTAINTY","true_ev":-0.004,"realized_net":-0.01494929802080136,"one_session_net":-0.01494929802080136,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'reversal', 'iteration2')|false_GREAT":{"source_line":96772,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration2","index":606,"j":3,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.013720030861184741,"radius":0.002444979674706305,"reason":"CONFIDENT","true_ev":-0.012,"realized_net":-0.01182537851322596,"one_session_net":-0.01182537851322596,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":8230.45267489712}},"(None, 5015368413594993126, 'reversal', 'iteration2')|funded":{"source_line":96845,"row":{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration2","index":609,"j":4,"execution_index":610,"exit_index":611,"available_index":612,"inferred_tier":"GREAT","inferred_net":0.013320392848181041,"radius":0.003580946007894303,"reason":"CONFIDENT","true_ev":-0.004,"realized_net":-0.0027098634407909383,"one_session_net":-0.0027098634407909383,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":9898.050101498062}},"(None, 5015368413594993126, 'outer_noise', 'candidate')|other":{"source_line":99793,"row":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.004165537562394191,"radius":0.0018731583240019722,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01768662252600195,"one_session_net":-0.01768662252600195,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'outer_noise', 'candidate')|funded":{"source_line":99795,"row":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"candidate","index":606,"j":2,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011622420249968719,"radius":0.002359755050414517,"reason":"INTERVAL","true_ev":0.012,"realized_net":0.019306331713242475,"one_session_net":0.019306331713242475,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 5015368413594993126, 'outer_noise', 'ungated')|other":{"source_line":102817,"row":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.004165537562394191,"radius":0.0018731583240019722,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01768662252600195,"one_session_net":-0.01768662252600195,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'outer_noise', 'iteration2')|other":{"source_line":105841,"row":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.004120346567881372,"radius":0.002047392526354625,"reason":"BOUNDARY_UNCERTAINTY","true_ev":-0.004,"realized_net":-0.01768662252600195,"one_session_net":-0.01768662252600195,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 5015368413594993126, 'outer_noise', 'iteration2')|funded":{"source_line":105843,"row":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"iteration2","index":606,"j":2,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.014220699224967435,"radius":0.002985412428441804,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.019306331713242475,"one_session_net":0.019306331713242475,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 5015368413594993126, 'outer_noise', 'iteration2')|AVERAGE":{"source_line":106658,"row":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"iteration2","index":640,"j":1,"execution_index":641,"exit_index":642,"available_index":643,"inferred_tier":"AVERAGE","inferred_net":0.00015236943906984224,"radius":0.0018376334704102693,"reason":"CONFIDENT","true_ev":0,"realized_net":0.021236866285177625,"one_session_net":0.021236866285177625,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'learnable', 'candidate')|other":{"source_line":108865,"row":{"seed":3584306075979195116,"scenario":"learnable","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.012244347917120485,"radius":0.0019366897890755125,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'learnable', 'candidate')|funded":{"source_line":108871,"row":{"seed":3584306075979195116,"scenario":"learnable","variant":"candidate","index":606,"j":6,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.0037693309738478396,"radius":0.0015247895899842393,"reason":"INTERVAL","true_ev":0.004,"realized_net":-0.015584698559292343,"one_session_net":-0.015584698559292343,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 3584306075979195116, 'learnable', 'ungated')|other":{"source_line":111889,"row":{"seed":3584306075979195116,"scenario":"learnable","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.012244347917120485,"radius":0.0019366897890755125,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'learnable', 'iteration2')|other":{"source_line":114913,"row":{"seed":3584306075979195116,"scenario":"learnable","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.010385955755153593,"radius":0.002751127481874147,"reason":"INSUFFICIENT_MATURE_DATES","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'learnable', 'iteration2')|funded":{"source_line":115009,"row":{"seed":3584306075979195116,"scenario":"learnable","variant":"iteration2","index":610,"j":0,"execution_index":611,"exit_index":612,"available_index":613,"inferred_tier":"GREAT","inferred_net":0.011063482027649464,"radius":0.001549335775248532,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.013747898384893986,"one_session_net":0.013747898384893986,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 3584306075979195116, 'null', 'candidate')|other":{"source_line":117937,"row":{"seed":3584306075979195116,"scenario":"null","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.00025579168966930447,"radius":0.0018483964698862339,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'null', 'ungated')|other":{"source_line":120961,"row":{"seed":3584306075979195116,"scenario":"null","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.00025579168966930447,"radius":0.0018483964698862339,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'null', 'iteration2')|other":{"source_line":123985,"row":{"seed":3584306075979195116,"scenario":"null","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.000679969354342837,"radius":0.0034280648251278894,"reason":"NO_IDENTIFIABLE_SIGNAL","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'reversal', 'candidate')|false_GREAT":{"source_line":127009,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011749827287551145,"radius":0.0011002117635249143,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 3584306075979195116, 'reversal', 'candidate')|funded":{"source_line":127010,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"candidate","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.0037706605200315524,"radius":0.0015243477748533001,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01887398901732984,"one_session_net":-0.01887398901732984,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 3584306075979195116, 'reversal', 'candidate')|other":{"source_line":127011,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"candidate","index":606,"j":2,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.0007308996141247535,"radius":0.001839058064580763,"reason":"INTERVAL","true_ev":0,"realized_net":-0.009413132454997863,"one_session_net":-0.009413132454997863,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'reversal', 'ungated')|false_GREAT":{"source_line":130033,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011749827287551145,"radius":0.0011002117635249143,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'reversal', 'ungated')|other":{"source_line":130034,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"ungated","index":606,"j":1,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GOOD","inferred_net":0.0037706605200315524,"radius":0.0015243477748533001,"reason":"INTERVAL","true_ev":-0.004,"realized_net":-0.01887398901732984,"one_session_net":-0.01887398901732984,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'reversal', 'iteration2')|other":{"source_line":133057,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":0.011074788976932157,"radius":0.0015782537393440412,"reason":"INSUFFICIENT_MATURE_DATES","true_ev":-0.012,"realized_net":-0.013697418181011778,"one_session_net":-0.013697418181011778,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'reversal', 'iteration2')|false_GREAT":{"source_line":133159,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration2","index":610,"j":6,"execution_index":611,"exit_index":612,"available_index":613,"inferred_tier":"GREAT","inferred_net":0.010221233102619348,"radius":0.0028955327328646263,"reason":"CONFIDENT","true_ev":-0.012,"realized_net":-0.026713974023778397,"one_session_net":-0.026713974023778397,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 3584306075979195116, 'reversal', 'iteration2')|funded":{"source_line":134262,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration2","index":656,"j":5,"execution_index":657,"exit_index":658,"available_index":659,"inferred_tier":"GREAT","inferred_net":0.011405682747947328,"radius":0.0038152882769212203,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.009793734500489037,"one_session_net":0.009793734500489037,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":9914.00271398002}},"(None, 3584306075979195116, 'reversal', 'iteration2')|AVERAGE":{"source_line":134501,"row":{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration2","index":666,"j":4,"execution_index":667,"exit_index":668,"available_index":669,"inferred_tier":"AVERAGE","inferred_net":0.0004541533814729262,"radius":0.0014663700532409653,"reason":"CONFIDENT","true_ev":0,"realized_net":0.00010111252722211361,"one_session_net":0.00010111252722211361,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'outer_noise', 'candidate')|other":{"source_line":136081,"row":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"candidate","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.012367786923017526,"radius":0.0024334407851853415,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.01412177272626447,"one_session_net":-0.01412177272626447,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'outer_noise', 'candidate')|funded":{"source_line":136089,"row":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"candidate","index":606,"j":8,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"GREAT","inferred_net":0.011735966033842738,"radius":0.0013805428583848556,"reason":"INTERVAL","true_ev":0.012,"realized_net":0.013254426749577775,"one_session_net":0.013254426749577775,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}},"(None, 3584306075979195116, 'outer_noise', 'ungated')|other":{"source_line":139105,"row":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"ungated","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"TERRIBLE","inferred_net":-0.012367786923017526,"radius":0.0024334407851853415,"reason":"INTERVAL","true_ev":-0.012,"realized_net":-0.01412177272626447,"one_session_net":-0.01412177272626447,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'outer_noise', 'iteration2')|other":{"source_line":142129,"row":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"iteration2","index":606,"j":0,"execution_index":607,"exit_index":608,"available_index":609,"inferred_tier":"UNKNOWN","inferred_net":-0.010040787454864038,"radius":0.0034423624325560136,"reason":"INSUFFICIENT_MATURE_DATES","true_ev":-0.012,"realized_net":-0.01412177272626447,"one_session_net":-0.01412177272626447,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":false,"funded_debit":0.0}},"(None, 3584306075979195116, 'outer_noise', 'iteration2')|funded":{"source_line":142225,"row":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"iteration2","index":610,"j":0,"execution_index":611,"exit_index":612,"available_index":613,"inferred_tier":"GREAT","inferred_net":0.010885552810078592,"radius":0.0019261779681512185,"reason":"CONFIDENT","true_ev":0.012,"realized_net":0.014184872981117591,"one_session_net":0.014184872981117591,"horizon_mismatch":0.0,"cost_fraction":0.003,"eligible":true,"funded":true,"funded_debit":10000.0}}}}
```

## discrimination_iteration5/replays.jsonl.gz exact ledger counts and samples
```json
{"group_counts":{"(None, 1564008556893530022, 'learnable', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":713,"daily_rows":126},"(None, 1564008556893530022, 'learnable', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":309,"daily_rows":126},"(None, 1564008556893530022, 'learnable', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":690,"daily_rows":126},"(None, 1564008556893530022, 'learnable', 'scaled')":{"rows":1,"funded_opportunities":0,"trades":541,"daily_rows":126},"(None, 1564008556893530022, 'null', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 1564008556893530022, 'null', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 1564008556893530022, 'null', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":692,"daily_rows":126},"(None, 1564008556893530022, 'reversal', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":129,"daily_rows":126},"(None, 1564008556893530022, 'reversal', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":310,"daily_rows":126},"(None, 1564008556893530022, 'reversal', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":692,"daily_rows":126},"(None, 1564008556893530022, 'outer_noise', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":700,"daily_rows":126},"(None, 1564008556893530022, 'outer_noise', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":271,"daily_rows":126},"(None, 1564008556893530022, 'outer_noise', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":690,"daily_rows":126},"(None, 1634635432866334191, 'learnable', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":711,"daily_rows":126},"(None, 1634635432866334191, 'learnable', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":276,"daily_rows":126},"(None, 1634635432866334191, 'learnable', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":691,"daily_rows":126},"(None, 1634635432866334191, 'learnable', 'scaled')":{"rows":1,"funded_opportunities":0,"trades":539,"daily_rows":126},"(None, 1634635432866334191, 'null', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 1634635432866334191, 'null', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 1634635432866334191, 'null', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":695,"daily_rows":126},"(None, 1634635432866334191, 'reversal', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":125,"daily_rows":126},"(None, 1634635432866334191, 'reversal', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":280,"daily_rows":126},"(None, 1634635432866334191, 'reversal', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":692,"daily_rows":126},"(None, 1634635432866334191, 'outer_noise', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":706,"daily_rows":126},"(None, 1634635432866334191, 'outer_noise', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":138,"daily_rows":126},"(None, 1634635432866334191, 'outer_noise', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":691,"daily_rows":126},"(None, 5015368413594993126, 'learnable', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":688,"daily_rows":126},"(None, 5015368413594993126, 'learnable', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":360,"daily_rows":126},"(None, 5015368413594993126, 'learnable', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":692,"daily_rows":126},"(None, 5015368413594993126, 'learnable', 'scaled')":{"rows":1,"funded_opportunities":0,"trades":531,"daily_rows":126},"(None, 5015368413594993126, 'null', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 5015368413594993126, 'null', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 5015368413594993126, 'null', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":691,"daily_rows":126},"(None, 5015368413594993126, 'reversal', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":121,"daily_rows":126},"(None, 5015368413594993126, 'reversal', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":65,"daily_rows":126},"(None, 5015368413594993126, 'reversal', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":690,"daily_rows":126},"(None, 5015368413594993126, 'outer_noise', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":537,"daily_rows":126},"(None, 5015368413594993126, 'outer_noise', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":346,"daily_rows":126},"(None, 5015368413594993126, 'outer_noise', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":692,"daily_rows":126},"(None, 3584306075979195116, 'learnable', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":710,"daily_rows":126},"(None, 3584306075979195116, 'learnable', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":75,"daily_rows":126},"(None, 3584306075979195116, 'learnable', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":692,"daily_rows":126},"(None, 3584306075979195116, 'learnable', 'scaled')":{"rows":1,"funded_opportunities":0,"trades":534,"daily_rows":126},"(None, 3584306075979195116, 'null', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 3584306075979195116, 'null', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"(None, 3584306075979195116, 'null', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":691,"daily_rows":126},"(None, 3584306075979195116, 'reversal', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":124,"daily_rows":126},"(None, 3584306075979195116, 'reversal', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":222,"daily_rows":126},"(None, 3584306075979195116, 'reversal', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":691,"daily_rows":126},"(None, 3584306075979195116, 'outer_noise', 'candidate')":{"rows":1,"funded_opportunities":0,"trades":560,"daily_rows":126},"(None, 3584306075979195116, 'outer_noise', 'iteration2')":{"rows":1,"funded_opportunities":0,"trades":75,"daily_rows":126},"(None, 3584306075979195116, 'outer_noise', 'benchmark')":{"rows":1,"funded_opportunities":0,"trades":692,"daily_rows":126}},"samples":{"(None, 1564008556893530022, 'learnable', 'candidate')":{"source_line":1,"metadata":{"seed":1564008556893530022,"scenario":"learnable","variant":"candidate"},"trades_first_2":[{"signal":606,"j":19,"entry_index":607,"entry_open":686.4307836735534,"shares":11.97225660930647,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":707.382710802779,"net":0.02743606187144776,"realized_loss_nav":0.0},{"signal":606,"j":15,"entry_index":607,"entry_open":984.8298082379058,"shares":8.34471643518924,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":1005.925705249528,"net":0.018361182440316925,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":2,"entry_index":732,"entry_open":1110.9376439417215,"shares":7.98464096172725,"debit":8883.743875068445,"entry_nav":184882.90489337157,"modeled_risk":0.005901377963589981,"tier":"GREAT","exit_index":733,"exit_open":1117.43507551087,"net":0.0028355752334479067,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":184763.73567419883,"cash":0.0,"receivable":105317.58955906764,"exposure":0.42998776694589963}]},"(None, 1564008556893530022, 'learnable', 'iteration2')":{"source_line":2,"metadata":{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration2"},"trades_first_2":[{"signal":606,"j":1,"entry_index":607,"entry_open":660.3490419394099,"shares":15.120825248682229,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":679.5901282752503,"net":0.026054962502403134,"realized_loss_nav":0.0},{"signal":606,"j":2,"entry_index":607,"entry_open":858.3798854485719,"shares":11.632404994069239,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549676,"tier":"GREAT","exit_index":608,"exit_open":885.5366628883859,"net":0.028546971816454825,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":714,"j":9,"entry_index":715,"entry_open":1202.4841047054406,"shares":0.4993346486740678,"debit":601.342640926181,"entry_nav":139133.81971712265,"modeled_risk":0.00027188101849242143,"tier":"GREAT","exit_index":716,"exit_open":1224.1314034088841,"net":0.014952717265585447,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99903.10830051219,"cash":35308.64197530864,"receivable":0.0,"exposure":0.6465711370150871}],"daily_last_1":[{"index":731,"nav":139237.7115486836,"cash":139237.7115486836,"receivable":0.0,"exposure":0.0}]},"(None, 1564008556893530022, 'learnable', 'benchmark')":{"source_line":3,"metadata":{"seed":1564008556893530022,"scenario":"learnable","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":19,"entry_index":607,"entry_open":686.4307836735534,"shares":11.97225660930647,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":707.382710802779,"net":0.02743606187144776,"realized_loss_nav":0.0},{"signal":606,"j":15,"entry_index":607,"entry_open":984.8298082379058,"shares":8.34471643518924,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":1005.925705249528,"net":0.018361182440316925,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":20,"entry_index":731,"entry_open":671.7990668387787,"shares":12.131106989118328,"debit":8161.890854543595,"entry_nav":153747.24632977453,"modeled_risk":0.0017492280098370982,"tier":"AVERAGE","exit_index":732,"exit_open":675.5119458364071,"net":0.002514707885720613,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":154564.74145097245,"cash":0.0,"receivable":154564.74145097245,"exposure":0.0}]},"(None, 1564008556893530022, 'learnable', 'scaled')":{"source_line":4,"metadata":{"seed":1564008556893530022,"scenario":"learnable","variant":"scaled"},"trades_first_2":[{"signal":606,"j":19,"entry_index":607,"entry_open":686.4307836735534,"shares":11.97225660930647,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":707.382710802779,"net":0.02743606187144776,"realized_loss_nav":0.0},{"signal":606,"j":15,"entry_index":607,"entry_open":984.8298082379058,"shares":8.34471643518924,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":1005.925705249528,"net":0.018361182440316925,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":6,"entry_index":732,"entry_open":1055.8334002498955,"shares":3.2841242556107235,"debit":3472.689311764094,"entry_nav":188915.5100967568,"modeled_risk":0.0022576284688210525,"tier":"GREAT","exit_index":733,"exit_open":1068.516792184618,"net":0.008981192184111197,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":188844.57856782968,"cash":0.0,"receivable":141556.89261642512,"exposure":0.2504053137772216}]},"(None, 1564008556893530022, 'null', 'candidate')":{"source_line":5,"metadata":{"seed":1564008556893530022,"scenario":"null","variant":"candidate"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 1564008556893530022, 'null', 'iteration2')":{"source_line":6,"metadata":{"seed":1564008556893530022,"scenario":"null","variant":"iteration2"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 1564008556893530022, 'null', 'benchmark')":{"source_line":7,"metadata":{"seed":1564008556893530022,"scenario":"null","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":5,"entry_index":607,"entry_open":530.6057569184081,"shares":18.81815705183907,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"UNKNOWN","exit_index":608,"exit_open":531.4478506527872,"net":-0.0014132185231204852,"realized_loss_nav":0.00014132185231204857},{"signal":606,"j":4,"entry_index":607,"entry_open":1113.5210421259517,"shares":8.967071198975269,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"UNKNOWN","exit_index":608,"exit_open":1097.27309365001,"net":-0.01754330334537224,"realized_loss_nav":0.001754330334537226}],"trades_last_1":[{"signal":730,"j":9,"entry_index":731,"entry_open":1408.8762954018641,"shares":4.975472911638014,"debit":7020.340582386323,"entry_nav":99182.71869301601,"modeled_risk":0.004452580388676248,"tier":"UNKNOWN","exit_index":732,"exit_open":1416.3284952331653,"net":0.0022781122007708987,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":98709.01624175056,"cash":0.0,"receivable":98709.01624175056,"exposure":0.0}]},"(None, 1564008556893530022, 'reversal', 'candidate')":{"source_line":8,"metadata":{"seed":1564008556893530022,"scenario":"reversal","variant":"candidate"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":790.2736236326258,"shares":12.634892735509395,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":793.7442787865415,"net":0.001383051115938061,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":952.3234797834983,"shares":10.48490631415551,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":952.9761446557808,"net":-0.002312220205354265,"realized_loss_nav":0.00023122202053542425}],"trades_last_1":[{"signal":627,"j":14,"entry_index":628,"entry_open":645.3494262806063,"shares":7.5728288373147,"debit":4894.451426600495,"entry_nav":90918.63988725201,"modeled_risk":0.006611579896485054,"tier":"GOOD","exit_index":629,"exit_open":645.169651044318,"net":-0.0032732426625657896,"realized_loss_nav":0.00017620949058710103}],"daily_first_1":[{"index":606,"nav":99910.13479780329,"cash":40000.0,"receivable":0.0,"exposure":0.5996402158704777}],"daily_last_1":[{"index":731,"nav":90664.61234282482,"cash":90664.61234282482,"receivable":0.0,"exposure":0.0}]},"(None, 1564008556893530022, 'reversal', 'iteration2')":{"source_line":9,"metadata":{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration2"},"trades_first_2":[{"signal":606,"j":4,"entry_index":607,"entry_open":1113.5210421259517,"shares":8.967071198975269,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":1097.27309365001,"net":-0.01754330334537224,"realized_loss_nav":0.001754330334537226},{"signal":606,"j":5,"entry_index":607,"entry_open":530.6057569184081,"shares":18.81815705183907,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":531.4478506527872,"net":-0.0014132185231204852,"realized_loss_nav":0.00014132185231204857}],"trades_last_1":[{"signal":714,"j":9,"entry_index":715,"entry_open":1202.4841047054406,"shares":0.4638613272648598,"debit":558.6225516327977,"entry_nav":129249.58933411146,"modeled_risk":0.0002718810184924136,"tier":"GREAT","exit_index":716,"exit_open":1224.1314034088841,"net":0.014952717265585225,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99940.0898652022,"cash":60000.0,"receivable":0.0,"exposure":0.39964032370866215}],"daily_last_1":[{"index":731,"nav":129346.10056762552,"cash":129346.10056762552,"receivable":0.0,"exposure":0.0}]},"(None, 1564008556893530022, 'reversal', 'benchmark')":{"source_line":10,"metadata":{"seed":1564008556893530022,"scenario":"reversal","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":790.2736236326258,"shares":12.634892735509395,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":793.7442787865415,"net":0.001383051115938061,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":952.3234797834983,"shares":10.48490631415551,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":952.9761446557808,"net":-0.002312220205354265,"realized_loss_nav":0.00023122202053542425}],"trades_last_1":[{"signal":730,"j":11,"entry_index":731,"entry_open":1347.1710821742754,"shares":1.7023554391429205,"debit":2296.8040652242253,"entry_nav":64898.06835459131,"modeled_risk":0.008587119321018494,"tier":"UNKNOWN","exit_index":732,"exit_open":1349.4654117609084,"net":-0.0012975361278719788,"realized_loss_nav":4.5921031686005954e-05}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":64175.944110918375,"cash":0.0,"receivable":64175.944110918375,"exposure":0.0}]},"(None, 1564008556893530022, 'outer_noise', 'candidate')":{"source_line":11,"metadata":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"candidate"},"trades_first_2":[{"signal":606,"j":19,"entry_index":607,"entry_open":720.9102314862923,"shares":11.399651617821963,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":745.7049371004096,"net":0.03129507733931014,"realized_loss_nav":0.0},{"signal":606,"j":15,"entry_index":607,"entry_open":1050.173454954196,"shares":7.8254934438669075,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":1074.344172800409,"net":0.019951478050396654,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":2,"entry_index":732,"entry_open":1156.7874250573752,"shares":0.242718279660634,"debit":281.19461392359517,"entry_nav":183255.70141577616,"modeled_risk":0.00018845326253742167,"tier":"GREAT","exit_index":733,"exit_open":1160.894727980242,"net":0.0005444690418099363,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":183150.34842703264,"cash":0.0,"receivable":112915.02259804348,"exposure":0.38348453296539065}]},"(None, 1564008556893530022, 'outer_noise', 'iteration2')":{"source_line":12,"metadata":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"iteration2"},"trades_first_2":[{"signal":612,"j":6,"entry_index":613,"entry_open":883.1694439185047,"shares":11.305896660099945,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":614,"exit_open":892.9914366505105,"net":0.008092479777317196,"realized_loss_nav":0.0},{"signal":612,"j":16,"entry_index":613,"entry_open":1220.6060793361455,"shares":8.180380743090458,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":614,"exit_open":1252.2947072473773,"net":0.022888113657878684,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":714,"j":19,"entry_index":715,"entry_open":1058.1747510432476,"shares":10.411544605416026,"debit":11033.75947124299,"entry_nav":134060.1775756023,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":716,"exit_open":1074.2935899358968,"net":0.012191545102221202,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":134642.92042015571,"cash":134642.92042015571,"receivable":0.0,"exposure":0.0}]},"(None, 1564008556893530022, 'outer_noise', 'benchmark')":{"source_line":13,"metadata":{"seed":1564008556893530022,"scenario":"outer_noise","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":19,"entry_index":607,"entry_open":720.9102314862923,"shares":11.399651617821963,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":745.7049371004096,"net":0.03129507733931014,"realized_loss_nav":0.0},{"signal":606,"j":15,"entry_index":607,"entry_open":1050.173454954196,"shares":7.8254934438669075,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":1074.344172800409,"net":0.019951478050396654,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":20,"entry_index":731,"entry_open":645.2026760125727,"shares":12.605604778818996,"debit":8145.369690954969,"entry_nav":153436.0337133381,"modeled_risk":0.0017492280098370925,"tier":"UNKNOWN","exit_index":732,"exit_open":649.1754056371005,"net":0.0031433848571504885,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":154185.07955059377,"cash":0.0,"receivable":154185.07955059377,"exposure":0.0}]},"(None, 1634635432866334191, 'learnable', 'candidate')":{"source_line":14,"metadata":{"seed":1634635432866334191,"scenario":"learnable","variant":"candidate"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":774.6416123391231,"shares":10.608938837989228,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":776.1225664940246,"net":-0.0010894408595788496,"realized_loss_nav":8.966591436863382e-05},{"signal":606,"j":12,"entry_index":607,"entry_open":789.1323077933245,"shares":12.653166481324256,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":801.110857577801,"net":0.012138416735197,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":1,"entry_index":732,"entry_open":678.56073973848,"shares":21.462661521258532,"debit":14585.565057839733,"entry_nav":184556.20209226618,"modeled_risk":0.0049714629839124865,"tier":"GOOD","exit_index":733,"exit_open":683.0232579435958,"net":0.0035612396811748326,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99873.15323311328,"cash":15308.641975308637,"receivable":0.0,"exposure":0.8467191484424564}],"daily_last_1":[{"index":731,"nav":184405.92943011574,"cash":0.0,"receivable":84224.15466316366,"exposure":0.543267643706207}]},"(None, 1634635432866334191, 'learnable', 'iteration2')":{"source_line":15,"metadata":{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration2"},"trades_first_2":[{"signal":672,"j":2,"entry_index":673,"entry_open":949.1016094765569,"shares":10.520498929305822,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":674,"exit_open":957.284121518267,"net":0.005599991561118012,"realized_loss_nav":0.0},{"signal":672,"j":3,"entry_index":673,"entry_open":1062.5223557902596,"shares":7.7345435998424925,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.019970044932601103,"tier":"GREAT","exit_index":674,"exit_open":1074.5833043488117,"net":0.00832173269542702,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":5,"entry_index":732,"entry_open":1362.5333350630287,"shares":4.849184866934648,"debit":6617.086793125258,"entry_nav":131134.18026226535,"modeled_risk":0.0031742455628246454,"tier":"GOOD","exit_index":733,"exit_open":1389.8320930636319,"net":0.016979772900341805,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":131033.01718563128,"cash":0.0,"receivable":63590.966096260425,"exposure":0.5146950939382503}]},"(None, 1634635432866334191, 'learnable', 'benchmark')":{"source_line":16,"metadata":{"seed":1634635432866334191,"scenario":"learnable","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":774.6416123391231,"shares":10.608938837989228,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":776.1225664940246,"net":-0.0010894408595788496,"realized_loss_nav":8.966591436863382e-05},{"signal":606,"j":12,"entry_index":607,"entry_open":789.1323077933245,"shares":12.653166481324256,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":801.110857577801,"net":0.012138416735197,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":7,"entry_index":731,"entry_open":677.6596356016108,"shares":7.661940616946401,"debit":5199.976168310801,"entry_nav":146929.55917436327,"modeled_risk":0.008587119321018476,"tier":"AVERAGE","exit_index":732,"exit_open":681.5208240591138,"net":0.0026852539830604094,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":148105.557509877,"cash":0.0,"receivable":148105.557509877,"exposure":0.0}]},"(None, 1634635432866334191, 'learnable', 'scaled')":{"source_line":17,"metadata":{"seed":1634635432866334191,"scenario":"learnable","variant":"scaled"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":774.6416123391231,"shares":10.608938837989228,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":776.1225664940246,"net":-0.0010894408595788496,"realized_loss_nav":8.966591436863382e-05},{"signal":606,"j":12,"entry_index":607,"entry_open":789.1323077933245,"shares":18.979749721986387,"debit":15000.000000000002,"entry_nav":100000.0,"modeled_risk":0.004942586120818773,"tier":"GREAT","exit_index":608,"exit_open":801.110857577801,"net":0.012138416735197,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":18,"entry_index":732,"entry_open":946.5852001749683,"shares":19.785952064711246,"debit":18757.183029920765,"entry_nav":185795.36055644276,"modeled_risk":0.012399007105384044,"tier":"GOOD","exit_index":733,"exit_open":936.3612861224283,"net":-0.013763991443859203,"realized_loss_nav":0.0013895594914831077}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":185679.71889060317,"cash":0.0,"receivable":108585.27499755059,"exposure":0.41520120966186014}]},"(None, 1634635432866334191, 'null', 'candidate')":{"source_line":18,"metadata":{"seed":1634635432866334191,"scenario":"null","variant":"candidate"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 1634635432866334191, 'null', 'iteration2')":{"source_line":19,"metadata":{"seed":1634635432866334191,"scenario":"null","variant":"iteration2"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 1634635432866334191, 'null', 'benchmark')":{"source_line":20,"metadata":{"seed":1634635432866334191,"scenario":"null","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":618.8638314581221,"shares":16.13444179275199,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"UNKNOWN","exit_index":608,"exit_open":625.6221829735415,"net":0.007892359839787977,"realized_loss_nav":0.0},{"signal":606,"j":10,"entry_index":607,"entry_open":1026.7266536105965,"shares":9.72510300690756,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"UNKNOWN","exit_index":608,"exit_open":1020.916006747671,"net":-0.008637944296869815,"realized_loss_nav":0.0008637944296869864}],"trades_last_1":[{"signal":730,"j":5,"entry_index":731,"entry_open":1353.1442753666217,"shares":2.4703249502691516,"debit":3347.7201238491652,"entry_nav":94592.5569878311,"modeled_risk":0.0022262901943381212,"tier":"UNKNOWN","exit_index":732,"exit_open":1362.5333350630287,"net":0.0039224065049991985,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":94775.68171814659,"cash":0.0,"receivable":94775.68171814659,"exposure":0.0}]},"(None, 1634635432866334191, 'reversal', 'candidate')":{"source_line":21,"metadata":{"seed":1634635432866334191,"scenario":"reversal","variant":"candidate"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":438.18199861551153,"shares":22.787386286633,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":435.67470480647506,"net":-0.00870040379506587,"realized_loss_nav":0.0008700403795065904},{"signal":606,"j":4,"entry_index":607,"entry_open":423.63640582131393,"shares":23.56979317427252,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":425.3880445519174,"net":0.0011268766553571563,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":627,"j":9,"entry_index":628,"entry_open":798.0029210962279,"shares":4.393099128059916,"debit":3510.9644957623905,"entry_nav":89068.44487885298,"modeled_risk":0.0024796601571117696,"tier":"GOOD","exit_index":629,"exit_open":784.0318765664305,"net":-0.02045057338627576,"realized_loss_nav":0.0008061355194295634}],"daily_first_1":[{"index":606,"nav":99867.8525421744,"cash":11769.547325102882,"receivable":0.0,"exposure":0.882148789370107}],"daily_last_1":[{"index":731,"nav":88391.093403871,"cash":88391.093403871,"receivable":0.0,"exposure":0.0}]},"(None, 1634635432866334191, 'reversal', 'iteration2')":{"source_line":22,"metadata":{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration2"},"trades_first_2":[{"signal":671,"j":0,"entry_index":672,"entry_open":403.03073973412313,"shares":24.77484092872818,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":673,"exit_open":406.6653155052114,"net":0.005995590011836249,"realized_loss_nav":0.0},{"signal":671,"j":4,"entry_index":672,"entry_open":492.7369939743849,"shares":20.264405937459657,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":673,"exit_open":505.7944206598693,"net":0.02342490259620922,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":5,"entry_index":732,"entry_open":1362.5333350630287,"shares":4.8806051747062265,"debit":6659.962226687079,"entry_nav":131983.86457339762,"modeled_risk":0.003174245562824644,"tier":"GOOD","exit_index":733,"exit_open":1389.8320930636319,"net":0.016979772900341583,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":131882.04601030756,"cash":0.0,"receivable":64003.00395026368,"exposure":0.5146950939382503}]},"(None, 1634635432866334191, 'reversal', 'benchmark')":{"source_line":23,"metadata":{"seed":1634635432866334191,"scenario":"reversal","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":438.18199861551153,"shares":22.787386286633,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":435.67470480647506,"net":-0.00870040379506587,"realized_loss_nav":0.0008700403795065904},{"signal":606,"j":4,"entry_index":607,"entry_open":423.63640582131393,"shares":23.56979317427252,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":425.3880445519174,"net":0.0011268766553571563,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":12,"entry_index":731,"entry_open":1102.2017692673212,"shares":3.056593003775276,"debit":3374.0356900162615,"entry_nav":63557.416486352624,"modeled_risk":0.001749228009837102,"tier":"UNKNOWN","exit_index":732,"exit_open":1112.6169608793139,"net":0.006425629321454185,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.2246630055,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":63226.64490506843,"cash":0.0,"receivable":63226.64490506843,"exposure":0.0}]},"(None, 1634635432866334191, 'outer_noise', 'candidate')":{"source_line":24,"metadata":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"candidate"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":774.6711653404808,"shares":10.608534116608196,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":773.6095564595531,"net":-0.004361801074473481,"realized_loss_nav":0.00035899597320769317},{"signal":606,"j":12,"entry_index":607,"entry_open":779.5099090277416,"shares":12.80935925337313,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":791.3694519840626,"net":0.01217302091899608,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":5,"entry_index":732,"entry_open":1473.151519673118,"shares":9.10409869831678,"debit":13431.83440792844,"entry_nav":185054.03246745263,"modeled_risk":0.004565899749347054,"tier":"GOOD","exit_index":733,"exit_open":1507.4612011564354,"net":0.0202247161254272,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99888.13076681273,"cash":25308.641975308637,"receivable":0.0,"exposure":0.7466301373244107}],"daily_last_1":[{"index":731,"nav":184932.85791423466,"cash":0.0,"receivable":104149.82243558878,"exposure":0.4368235931124268}]},"(None, 1634635432866334191, 'outer_noise', 'iteration2')":{"source_line":25,"metadata":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"iteration2"},"trades_first_2":[{"signal":672,"j":2,"entry_index":673,"entry_open":1000.1085864020157,"shares":9.98393834635757,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":674,"exit_open":1007.1258625069331,"net":0.0039999894513975676,"realized_loss_nav":0.0},{"signal":672,"j":3,"entry_index":673,"entry_open":1085.478138623348,"shares":7.570972822252979,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":674,"exit_open":1096.798495137405,"net":0.007402165869283772,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":704,"j":9,"entry_index":705,"entry_open":979.0095919574976,"shares":11.74420730132821,"debit":11514.938135334502,"entry_nav":115149.381353345,"modeled_risk":0.006290564153769347,"tier":"GREAT","exit_index":706,"exit_open":994.101703743722,"net":0.012374008929066482,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":115613.97344789827,"cash":115613.97344789827,"receivable":0.0,"exposure":0.0}]},"(None, 1634635432866334191, 'outer_noise', 'benchmark')":{"source_line":26,"metadata":{"seed":1634635432866334191,"scenario":"outer_noise","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":774.6711653404808,"shares":10.608534116608196,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":773.6095564595531,"net":-0.004361801074473481,"realized_loss_nav":0.00035899597320769317},{"signal":606,"j":12,"entry_index":607,"entry_open":779.5099090277416,"shares":12.80935925337313,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":791.3694519840626,"net":0.01217302091899608,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":7,"entry_index":731,"entry_open":628.1864776616607,"shares":8.187557376776613,"debit":5151.027798413803,"entry_nav":145546.48314122806,"modeled_risk":0.008587119321018421,"tier":"AVERAGE","exit_index":732,"exit_open":632.1887536356161,"net":0.0033565674788254007,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":146721.85277845873,"cash":0.0,"receivable":146721.85277845873,"exposure":0.0}]},"(None, 5015368413594993126, 'learnable', 'candidate')":{"source_line":27,"metadata":{"seed":5015368413594993126,"scenario":"learnable","variant":"candidate"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":1194.8895801740703,"shares":8.356439483593071,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0062905641537693464,"tier":"GREAT","exit_index":608,"exit_open":1201.2039041281116,"net":0.0022731050703845845,"realized_loss_nav":0.0},{"signal":606,"j":7,"entry_index":607,"entry_open":799.9166801614313,"shares":10.273726864913753,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":819.405236595745,"net":0.021294746000235953,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":5,"entry_index":732,"entry_open":608.4126408475121,"shares":21.28380751576753,"debit":12968.761544265188,"entry_nav":184741.42375327347,"modeled_risk":0.004415946615096465,"tier":"GREAT","exit_index":733,"exit_open":616.93540276339,"net":0.010970724982843016,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99870.50288764384,"cash":13539.094650205756,"receivable":0.0,"exposure":0.8644334987935578}],"daily_last_1":[{"index":731,"nav":184593.44377387836,"cash":0.0,"receivable":85940.12417713761,"exposure":0.5344356634766955}]},"(None, 5015368413594993126, 'learnable', 'iteration2')":{"source_line":28,"metadata":{"seed":5015368413594993126,"scenario":"learnable","variant":"iteration2"},"trades_first_2":[{"signal":606,"j":2,"entry_index":607,"entry_open":684.4994443686978,"shares":14.58733465519401,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549676,"tier":"GREAT","exit_index":608,"exit_open":698.8076647692958,"net":0.01784506537059416,"realized_loss_nav":0.0},{"signal":606,"j":7,"entry_index":607,"entry_open":799.9166801614313,"shares":10.273726864913753,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":819.405236595745,"net":0.021294746000235953,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":13,"entry_index":732,"entry_open":1276.311389043323,"shares":2.042064356548936,"debit":2610.2194604159668,"entry_nav":147816.04588712682,"modeled_risk":0.00111082344765886,"tier":"GREAT","exit_index":733,"exit_open":1301.1246351443135,"net":0.016387629748141785,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.094650205756,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":147664.9973072827,"cash":0.0,"receivable":46965.944077859094,"exposure":0.6819426070206364}]},"(None, 5015368413594993126, 'learnable', 'benchmark')":{"source_line":29,"metadata":{"seed":5015368413594993126,"scenario":"learnable","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":1194.8895801740703,"shares":8.356439483593071,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0062905641537693464,"tier":"GREAT","exit_index":608,"exit_open":1201.2039041281116,"net":0.0022731050703845845,"realized_loss_nav":0.0},{"signal":606,"j":7,"entry_index":607,"entry_open":799.9166801614313,"shares":10.273726864913753,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":819.405236595745,"net":0.021294746000235953,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":23,"entry_index":731,"entry_open":782.4344961056405,"shares":7.063559287617834,"debit":5535.062610597457,"entry_nav":156397.69934595234,"modeled_risk":0.008587119321018421,"tier":"UNKNOWN","exit_index":732,"exit_open":790.2660864683887,"net":0.00698377052855248,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":157416.08338490664,"cash":0.0,"receivable":157416.08338490664,"exposure":0.0}]},"(None, 5015368413594993126, 'learnable', 'scaled')":{"source_line":30,"metadata":{"seed":5015368413594993126,"scenario":"learnable","variant":"scaled"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":1194.8895801740703,"shares":12.534659225389607,"debit":15000.000000000002,"entry_nav":100000.0,"modeled_risk":0.00943584623065402,"tier":"GREAT","exit_index":608,"exit_open":1201.2039041281116,"net":0.0022731050703843625,"realized_loss_nav":0.0},{"signal":606,"j":7,"entry_index":607,"entry_open":799.9166801614313,"shares":10.273726864913753,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":819.405236595745,"net":0.021294746000235953,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":11,"entry_index":732,"entry_open":509.56256139292407,"shares":26.160131364385126,"debit":13350.218879728072,"entry_nav":195404.82051263645,"modeled_risk":0.016577095246647244,"tier":"GREAT","exit_index":733,"exit_open":515.9789570012942,"net":0.0095587422115877,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":195272.93678875684,"cash":0.0,"receivable":107350.45420235723,"exposure":0.45025431599624455}]},"(None, 5015368413594993126, 'null', 'candidate')":{"source_line":31,"metadata":{"seed":5015368413594993126,"scenario":"null","variant":"candidate"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 5015368413594993126, 'null', 'iteration2')":{"source_line":32,"metadata":{"seed":5015368413594993126,"scenario":"null","variant":"iteration2"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 5015368413594993126, 'null', 'benchmark')":{"source_line":33,"metadata":{"seed":5015368413594993126,"scenario":"null","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":22,"entry_index":607,"entry_open":1142.9890448131202,"shares":8.735886412571093,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"UNKNOWN","exit_index":608,"exit_open":1157.5605528559042,"net":0.009714902916404311,"realized_loss_nav":0.0},{"signal":606,"j":20,"entry_index":607,"entry_open":942.0377744640333,"shares":10.599386496981468,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"UNKNOWN","exit_index":608,"exit_open":941.9017996487656,"net":-0.0031394155145347824,"realized_loss_nav":0.0003139415514534812}],"trades_last_1":[{"signal":730,"j":8,"entry_index":731,"entry_open":1085.7829896702094,"shares":4.949102915335059,"debit":5381.712237237447,"entry_nav":101376.43981772891,"modeled_risk":0.0017492280098370917,"tier":"UNKNOWN","exit_index":732,"exit_open":1074.2422738919422,"net":-0.013592601735700649,"realized_loss_nav":0.0007215825612779321}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":101344.69166808718,"cash":0.0,"receivable":101344.69166808718,"exposure":0.0}]},"(None, 5015368413594993126, 'reversal', 'candidate')":{"source_line":34,"metadata":{"seed":5015368413594993126,"scenario":"reversal","variant":"candidate"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":450.8029533031123,"shares":18.229972599894193,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":446.81046149428244,"net":-0.01182537851322596,"realized_loss_nav":0.0009732821821585185},{"signal":606,"j":0,"entry_index":607,"entry_open":391.6073397823145,"shares":25.497536567754302,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GOOD","exit_index":608,"exit_open":386.91208270426097,"net":-0.014949298020801471,"realized_loss_nav":0.0014949298020801507}],"trades_last_1":[{"signal":627,"j":5,"entry_index":628,"entry_open":499.1677912386911,"shares":3.565095821706035,"debit":1782.250378385601,"entry_nav":90226.2174267396,"modeled_risk":0.0012425834378369603,"tier":"GOOD","exit_index":629,"exit_open":501.06671252745883,"net":0.0007972721422382367,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99942.74021067165,"cash":61769.547325102874,"receivable":0.0,"exposure":0.3819506329834723}],"daily_last_1":[{"index":731,"nav":90067.68136556458,"cash":90067.68136556458,"receivable":0.0,"exposure":0.0}]},"(None, 5015368413594993126, 'reversal', 'iteration2')":{"source_line":35,"metadata":{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration2"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":450.8029533031123,"shares":18.229972599894193,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":446.81046149428244,"net":-0.01182537851322596,"realized_loss_nav":0.0009732821821585185},{"signal":607,"j":2,"entry_index":608,"entry_open":698.8076647692958,"shares":14.274749297632406,"debit":9990.267178178416,"entry_nav":99902.67178178414,"modeled_risk":0.012281577633549676,"tier":"GREAT","exit_index":609,"exit_open":696.6253322108505,"net":-0.006109089312393956,"realized_loss_nav":0.0006109089312393912}],"trades_last_1":[{"signal":731,"j":13,"entry_index":732,"entry_open":1276.311389043323,"shares":1.3912612987959836,"debit":1778.3461647497024,"entry_nav":100707.27855578372,"modeled_risk":0.001110823447658859,"tier":"GREAT","exit_index":733,"exit_open":1301.1246351443135,"net":0.016387629748141785,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99987.67281177,"cash":91769.54732510287,"receivable":0.0,"exposure":0.08219138675362515}],"daily_last_1":[{"index":731,"nav":100604.36894732731,"cash":0.0,"receivable":31997.963309720977,"exposure":0.6819426070206364}]},"(None, 5015368413594993126, 'reversal', 'benchmark')":{"source_line":36,"metadata":{"seed":5015368413594993126,"scenario":"reversal","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":450.8029533031123,"shares":18.229972599894193,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":446.81046149428244,"net":-0.01182537851322596,"realized_loss_nav":0.0009732821821585185},{"signal":606,"j":0,"entry_index":607,"entry_open":391.6073397823145,"shares":25.497536567754302,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GOOD","exit_index":608,"exit_open":386.91208270426097,"net":-0.014949298020801471,"realized_loss_nav":0.0014949298020801507}],"trades_last_1":[{"signal":730,"j":22,"entry_index":731,"entry_open":1510.1342275905813,"shares":2.3686586967913965,"debit":3582.3580603620458,"entry_nav":67481.62857891312,"modeled_risk":0.006519849854847342,"tier":"UNKNOWN","exit_index":732,"exit_open":1540.2574881999844,"net":0.016892146708729516,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":67125.93178281876,"cash":0.0,"receivable":67125.93178281876,"exposure":0.0}]},"(None, 5015368413594993126, 'outer_noise', 'candidate')":{"source_line":37,"metadata":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"candidate"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":1189.0215608453605,"shares":8.397679903467422,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0062905641537693464,"tier":"GREAT","exit_index":608,"exit_open":1192.4048165007728,"net":-0.00015861866201904995,"realized_loss_nav":1.5861866201903468e-05},{"signal":606,"j":7,"entry_index":607,"entry_open":834.5583064169335,"shares":9.847275407215777,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":856.835923227611,"net":0.023618432500295272,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":10,"entry_index":732,"entry_open":1601.9005915410187,"shares":1.961432208255177,"debit":3146.732443793582,"entry_nav":178291.39758784155,"modeled_risk":0.0021676221805047905,"tier":"GREAT","exit_index":733,"exit_open":1627.9566574030616,"net":0.01322148879548668,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.094650205756,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":178109.20965557772,"cash":0.0,"receivable":56650.58814636724,"exposure":0.6819334145835778}]},"(None, 5015368413594993126, 'outer_noise', 'iteration2')":{"source_line":38,"metadata":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"iteration2"},"trades_first_2":[{"signal":606,"j":2,"entry_index":607,"entry_open":742.0841096342475,"shares":13.455378354917055,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":758.6836736719013,"net":0.019306331713242475,"realized_loss_nav":0.0},{"signal":606,"j":7,"entry_index":607,"entry_open":834.5583064169335,"shares":9.847275407215777,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":856.835923227611,"net":0.023618432500295272,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":13,"entry_index":732,"entry_open":1248.9856825144498,"shares":2.084409887256233,"debit":2607.3032028331054,"entry_nav":147727.75896000673,"modeled_risk":0.0011102455070878163,"tier":"GREAT","exit_index":733,"exit_open":1274.6418172787319,"net":0.017484537185177063,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.094650205756,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":147576.8026306099,"cash":0.0,"receivable":46939.24969939136,"exposure":0.6819334145835778}]},"(None, 5015368413594993126, 'outer_noise', 'benchmark')":{"source_line":39,"metadata":{"seed":5015368413594993126,"scenario":"outer_noise","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":1189.0215608453605,"shares":8.397679903467422,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0062905641537693464,"tier":"GREAT","exit_index":608,"exit_open":1192.4048165007728,"net":-0.00015861866201904995,"realized_loss_nav":1.5861866201903468e-05},{"signal":606,"j":7,"entry_index":607,"entry_open":834.5583064169335,"shares":9.847275407215777,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":856.835923227611,"net":0.023618432500295272,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":23,"entry_index":731,"entry_open":744.5788699043973,"shares":7.554036700843651,"debit":5633.0129740954035,"entry_nav":159165.36659362557,"modeled_risk":0.008587119321018492,"tier":"UNKNOWN","exit_index":732,"exit_open":752.5886353237466,"net":0.007729713160690821,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":160180.00908631124,"cash":0.0,"receivable":160180.00908631124,"exposure":0.0}]},"(None, 3584306075979195116, 'learnable', 'candidate')":{"source_line":40,"metadata":{"seed":3584306075979195116,"scenario":"learnable","variant":"candidate"},"trades_first_2":[{"signal":606,"j":8,"entry_index":607,"entry_open":336.0743887027897,"shares":29.71075095856498,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":341.4674138693511,"net":0.01300354139966231,"realized_loss_nav":0.0},{"signal":606,"j":21,"entry_index":607,"entry_open":883.6391868553379,"shares":11.299886441019975,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":893.6126278655292,"net":0.008257463531621045,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":8,"entry_index":732,"entry_open":565.1002136953025,"shares":17.776668844212125,"debit":10060.667761698882,"entry_nav":187869.84940166955,"modeled_risk":0.0017645448698840847,"tier":"GREAT","exit_index":733,"exit_open":579.4116004943822,"net":0.02225402705547208,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99897.8076095733,"cash":31769.54732510288,"receivable":0.0,"exposure":0.681979534032753}],"daily_last_1":[{"index":731,"nav":187719.06885264142,"cash":0.0,"receivable":87198.70283389793,"exposure":0.5354829780114214}]},"(None, 3584306075979195116, 'learnable', 'iteration2')":{"source_line":41,"metadata":{"seed":3584306075979195116,"scenario":"learnable","variant":"iteration2"},"trades_first_2":[{"signal":610,"j":0,"entry_index":611,"entry_open":546.1222685801738,"shares":18.283492618347044,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":612,"exit_open":555.2936880194225,"net":0.013747898384893986,"realized_loss_nav":0.0},{"signal":610,"j":5,"entry_index":611,"entry_open":526.7636179625108,"shares":18.955414014585898,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0062905641537693464,"tier":"GREAT","exit_index":612,"exit_open":531.1457520127669,"net":0.0052985500043334355,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":624,"j":21,"entry_index":625,"entry_open":979.0362465600241,"shares":7.649421676813508,"debit":7500.294678452616,"entry_nav":107579.99258613444,"modeled_risk":0.004385674669869981,"tier":"GREAT","exit_index":626,"exit_open":1022.5252950033047,"net":0.04129169596369131,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":108770.19160574023,"cash":108770.19160574023,"receivable":0.0,"exposure":0.0}]},"(None, 3584306075979195116, 'learnable', 'benchmark')":{"source_line":42,"metadata":{"seed":3584306075979195116,"scenario":"learnable","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":8,"entry_index":607,"entry_open":336.0743887027897,"shares":29.71075095856498,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":341.4674138693511,"net":0.01300354139966231,"realized_loss_nav":0.0},{"signal":606,"j":21,"entry_index":607,"entry_open":883.6391868553379,"shares":11.299886441019975,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":893.6126278655292,"net":0.008257463531621045,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":16,"entry_index":731,"entry_open":807.5065379363946,"shares":6.647947039150617,"debit":5376.313089015974,"entry_nav":151912.10239893934,"modeled_risk":0.0011661520065580672,"tier":"POOR","exit_index":732,"exit_open":795.9680128040686,"net":-0.017241783224440255,"realized_loss_nav":0.0006102030276962413}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":151093.18564790837,"cash":0.0,"receivable":151093.18564790837,"exposure":0.0}]},"(None, 3584306075979195116, 'learnable', 'scaled')":{"source_line":43,"metadata":{"seed":3584306075979195116,"scenario":"learnable","variant":"scaled"},"trades_first_2":[{"signal":606,"j":8,"entry_index":607,"entry_open":336.0743887027897,"shares":44.56612643784747,"debit":15000.000000000002,"entry_nav":100000.0,"modeled_risk":0.004942586120818772,"tier":"GREAT","exit_index":608,"exit_open":341.4674138693511,"net":0.013003541399662089,"realized_loss_nav":0.0},{"signal":606,"j":21,"entry_index":607,"entry_open":883.6391868553379,"shares":16.949829661529964,"debit":15000.000000000002,"entry_nav":100000.0,"modeled_risk":0.009435846230654021,"tier":"GREAT","exit_index":608,"exit_open":893.6126278655292,"net":0.008257463531620823,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":14,"entry_index":732,"entry_open":807.4172416949699,"shares":24.578051513789255,"debit":19874.509673339853,"entry_nav":189931.48685012612,"modeled_risk":0.012851493848119438,"tier":"GREAT","exit_index":733,"exit_open":821.419921753211,"net":0.014295101157512313,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99852.87500847495,"cash":1769.5473251028798,"receivable":0.0,"exposure":0.9822784539258115}],"daily_last_1":[{"index":731,"nav":189792.96536704828,"cash":0.0,"receivable":97445.30998182035,"exposure":0.4865704859325691}]},"(None, 3584306075979195116, 'null', 'candidate')":{"source_line":44,"metadata":{"seed":3584306075979195116,"scenario":"null","variant":"candidate"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 3584306075979195116, 'null', 'iteration2')":{"source_line":45,"metadata":{"seed":3584306075979195116,"scenario":"null","variant":"iteration2"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"(None, 3584306075979195116, 'null', 'benchmark')":{"source_line":46,"metadata":{"seed":3584306075979195116,"scenario":"null","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":10,"entry_index":607,"entry_open":726.4008315341819,"shares":13.745885236959133,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"UNKNOWN","exit_index":608,"exit_open":722.293212514418,"net":-0.008633323275226257,"realized_loss_nav":0.0008633323275226212},{"signal":606,"j":20,"entry_index":607,"entry_open":904.1550624449164,"shares":11.043484553744744,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"UNKNOWN","exit_index":608,"exit_open":892.867838073517,"net":-0.015441837996710284,"realized_loss_nav":0.0015441837996710273}],"trades_last_1":[{"signal":730,"j":7,"entry_index":731,"entry_open":995.1353490626082,"shares":5.418879090371429,"debit":5400.606912327528,"entry_nav":101732.36276710012,"modeled_risk":0.012880678981527685,"tier":"UNKNOWN","exit_index":732,"exit_open":974.4273147179033,"net":-0.023742436599937244,"realized_loss_nav":0.001260400955305308}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":100638.37634648984,"cash":0.0,"receivable":100638.37634648984,"exposure":0.0}]},"(None, 3584306075979195116, 'reversal', 'candidate')":{"source_line":47,"metadata":{"seed":3584306075979195116,"scenario":"reversal","variant":"candidate"},"trades_first_2":[{"signal":606,"j":0,"entry_index":607,"entry_open":571.6147652251367,"shares":17.468097526080943,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":565.4790149479502,"net":-0.013697418181011778,"realized_loss_nav":0.0013697418181011745},{"signal":606,"j":7,"entry_index":607,"entry_open":716.5729362817169,"shares":11.468651787647484,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.019970044932601103,"tier":"GREAT","exit_index":608,"exit_open":708.9783555066326,"net":-0.013562234526842243,"realized_loss_nav":0.001116233294390304}],"trades_last_1":[{"signal":627,"j":16,"entry_index":628,"entry_open":633.9693718141547,"shares":6.860808447396423,"debit":4356.066735165456,"entry_nav":90213.67788086174,"modeled_risk":0.0015910547411685139,"tier":"GOOD","exit_index":629,"exit_open":628.7879116139769,"net":-0.011144069321774697,"realized_loss_nav":0.0005381036535398688}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":89637.5590256102,"cash":89637.5590256102,"receivable":0.0,"exposure":0.0}]},"(None, 3584306075979195116, 'reversal', 'iteration2')":{"source_line":48,"metadata":{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration2"},"trades_first_2":[{"signal":610,"j":6,"entry_index":611,"entry_open":529.0410929749614,"shares":18.87381263741099,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":612,"exit_open":516.4553484368117,"net":-0.026713974023778397,"realized_loss_nav":0.0026713974023778427},{"signal":610,"j":10,"entry_index":611,"entry_open":746.466169367119,"shares":13.37638981652204,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":612,"exit_open":742.4478662468574,"net":-0.00836248307530607,"realized_loss_nav":0.0008362483075306045}],"trades_last_1":[{"signal":699,"j":18,"entry_index":700,"entry_open":773.9233100070022,"shares":15.389619076236448,"debit":11928.250512630657,"entry_nav":119282.50512630655,"modeled_risk":0.012281577633549678,"tier":"GREAT","exit_index":701,"exit_open":782.1859575599937,"net":0.007648825366455947,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":119621.53471843754,"cash":119621.53471843754,"receivable":0.0,"exposure":0.0}]},"(None, 3584306075979195116, 'reversal', 'benchmark')":{"source_line":49,"metadata":{"seed":3584306075979195116,"scenario":"reversal","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":0,"entry_index":607,"entry_open":571.6147652251367,"shares":17.468097526080943,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":565.4790149479502,"net":-0.013697418181011778,"realized_loss_nav":0.0013697418181011745},{"signal":606,"j":7,"entry_index":607,"entry_open":716.5729362817169,"shares":11.468651787647484,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.019970044932601103,"tier":"GREAT","exit_index":608,"exit_open":708.9783555066326,"net":-0.013562234526842243,"realized_loss_nav":0.001116233294390304}],"trades_last_1":[{"signal":730,"j":5,"entry_index":731,"entry_open":672.2072209078747,"shares":7.1404236384296444,"debit":4807.044096588827,"entry_nav":67913.47182971438,"modeled_risk":0.004452580388676235,"tier":"UNKNOWN","exit_index":732,"exit_open":666.2243476178639,"net":-0.01186918641368262,"realized_loss_nav":0.0008401234827791761}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":67045.50224216764,"cash":0.0,"receivable":67045.50224216764,"exposure":0.0}]},"(None, 3584306075979195116, 'outer_noise', 'candidate')":{"source_line":50,"metadata":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"candidate"},"trades_first_2":[{"signal":606,"j":8,"entry_index":607,"entry_open":313.9312459304996,"shares":31.806398998942296,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":319.04793487335024,"net":0.013254426749577997,"realized_loss_nav":0.0},{"signal":606,"j":21,"entry_index":607,"entry_open":931.5118489127719,"shares":10.719157762678723,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":941.1514452656719,"net":0.007321829414526304,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":8,"entry_index":732,"entry_open":535.8832257945455,"shares":34.576768727398644,"debit":18556.904028735134,"entry_nav":185569.04028735135,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":733,"exit_open":550.8325484854577,"net":0.024817533819339932,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99942.74021067165,"cash":61769.54732510288,"receivable":0.0,"exposure":0.3819506329834723}],"daily_last_1":[{"index":731,"nav":185407.1965147346,"cash":28202.650013412906,"receivable":49308.698090151534,"exposure":0.5819399162458913}]},"(None, 3584306075979195116, 'outer_noise', 'iteration2')":{"source_line":51,"metadata":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"iteration2"},"trades_first_2":[{"signal":610,"j":0,"entry_index":611,"entry_open":539.5591425079226,"shares":18.505890605224863,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":612,"exit_open":548.8568247279053,"net":0.014184872981117147,"realized_loss_nav":0.0},{"signal":610,"j":5,"entry_index":611,"entry_open":449.14997120746585,"shares":22.230931996850533,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":612,"exit_open":452.1316892938003,"net":0.0036231875054162366,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":624,"j":21,"entry_index":625,"entry_open":1034.240129931552,"shares":7.286441709714601,"debit":7547.2343162248,"entry_nav":108176.89481164241,"modeled_risk":0.004388770978535431,"tier":"GREAT","exit_index":626,"exit_open":1087.7777664208015,"net":0.04861461995461447,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":109434.84538067406,"cash":109434.84538067406,"receivable":0.0,"exposure":0.0}]},"(None, 3584306075979195116, 'outer_noise', 'benchmark')":{"source_line":52,"metadata":{"seed":3584306075979195116,"scenario":"outer_noise","variant":"benchmark"},"trades_first_2":[{"signal":606,"j":8,"entry_index":607,"entry_open":313.9312459304996,"shares":31.806398998942296,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":319.04793487335024,"net":0.013254426749577997,"realized_loss_nav":0.0},{"signal":606,"j":21,"entry_index":607,"entry_open":931.5118489127719,"shares":10.719157762678723,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":941.1514452656719,"net":0.007321829414526304,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":730,"j":16,"entry_index":731,"entry_open":790.7828424293282,"shares":6.849913281568264,"debit":5424.9190860357485,"entry_nav":153285.50440775434,"modeled_risk":0.0011661520065580637,"tier":"UNKNOWN","exit_index":732,"exit_open":776.8575744384563,"net":-0.020552229030550095,"realized_loss_nav":0.0007273628381182349}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":152105.68954545495,"cash":0.0,"receivable":152105.68954545495,"exposure":0.0}]}}}
```

## discrimination_iteration5/corrected_benchmark_replays.jsonl.gz exact ledger counts and samples
```json
{"group_counts":{"(None, 1564008556893530022, None, None)":{"rows":1,"funded_opportunities":0,"trades":1512,"daily_rows":126},"(None, 1634635432866334191, None, None)":{"rows":1,"funded_opportunities":0,"trades":1512,"daily_rows":126},"(None, 5015368413594993126, None, None)":{"rows":1,"funded_opportunities":0,"trades":1512,"daily_rows":126},"(None, 3584306075979195116, None, None)":{"rows":1,"funded_opportunities":0,"trades":1512,"daily_rows":126}},"samples":{"(None, 1564008556893530022, None, None)":{"source_line":1,"metadata":{"seed":1564008556893530022},"trades_first_2":[{"signal":606,"j":0,"shares":5.20038867724743,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.0013729405891163256,"exit_index":608,"net":-0.00017168006808920833},{"signal":606,"j":1,"shares":6.300343853617596,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.0026210683974038943,"exit_index":608,"net":0.026054962502402912}],"trades_last_1":[{"signal":730,"j":23,"shares":8.12979372355775,"debit":4181.329607304881,"entry_index":731,"modeled_risk":0.010109835247129306,"exit_index":732,"net":-0.006339629282575809}],"daily_first_1":[{"index":606,"nav":99850.22466300546,"cash":0}],"daily_last_1":[{"index":731,"nav":100121.00007917365,"cash":0}]},"(None, 1634635432866334191, None, None)":{"source_line":2,"metadata":{"seed":1634635432866334191},"trades_first_2":[{"signal":606,"j":0,"shares":13.652515835507847,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.0013729405891163256,"exit_index":608,"net":0.012103810085660083},{"signal":606,"j":1,"shares":9.178944340390016,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.0026210683974038943,"exit_index":608,"net":0.015943195952868416}],"trades_last_1":[{"signal":730,"j":23,"shares":3.3829036467800315,"debit":4064.991272856732,"entry_index":731,"modeled_risk":0.010109835247129306,"exit_index":732,"net":0.002570509971245416}],"daily_first_1":[{"index":606,"nav":99850.22466300546,"cash":0}],"daily_last_1":[{"index":731,"nav":97724.82339925597,"cash":4.092726157978177e-11}]},"(None, 5015368413594993126, None, None)":{"source_line":3,"metadata":{"seed":5015368413594993126},"trades_first_2":[{"signal":606,"j":0,"shares":10.623973569897627,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.0013729405891163256,"exit_index":608,"net":-0.014949298020801471},{"signal":606,"j":1,"shares":6.066364447637449,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.0026210683974038943,"exit_index":608,"net":-0.008119028743840073}],"trades_last_1":[{"signal":730,"j":23,"shares":5.467827054696668,"debit":4284.633831093878,"entry_index":731,"modeled_risk":0.010109835247129304,"exit_index":732,"net":0.00698377052855248}],"daily_first_1":[{"index":606,"nav":99850.22466300546,"cash":0}],"daily_last_1":[{"index":731,"nav":103000.39914694341,"cash":2.7284841053187847e-11}]},"(None, 3584306075979195116, None, None)":{"source_line":4,"metadata":{"seed":3584306075979195116},"trades_first_2":[{"signal":606,"j":0,"shares":7.278373969200393,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.0013729405891163256,"exit_index":608,"net":-0.013697418181011556},{"signal":606,"j":1,"shares":7.056731684057344,"debit":4166.666666666667,"entry_index":607,"modeled_risk":0.002621068397403895,"exit_index":608,"net":-0.01887398901732973}],"trades_last_1":[{"signal":730,"j":23,"shares":5.099095265638309,"debit":4228.098407911693,"entry_index":731,"modeled_risk":0.010109835247129304,"exit_index":732,"net":0.016635661570672866}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0}],"daily_last_1":[{"index":731,"nav":100522.1912988778,"cash":5.820766091346741e-11}]}}}
```

## discrimination_iteration6/README.md

```
# Iteration6 — FAIL

Five-tier support: seed2098214662956861329 has0 AVERAGE assignments. Frozen interval straddles a band; this experiment cannot repair it after final evaluation. Next independent step must obtain more independent fit/calibration evidence under unchanged bands, then freeze and test fresh tapes. Rapid safety is promising but residual4–7-session exposure and false-alarm power need independent episode validation; no safe zero-delay detection from this DGP.

Completed 59 portfolio replays, six tests; runner elapsed 9.06s. Limit64 replays/720s. Three test portfolios, four fixed design probes, twelve paired regressions, forty frozen final portfolios. No candidate tuning, GA, production changes or final reruns. All new files stay here.

## Diagnosis

Iteration5 false GREAT count442 comprised49 in sessions606–608, before any post-change outcome was eligible, and393 after first outcome availability. Funded false GREAT trades lost $36,554 across four separate $100,000 accounts; these are a subset of portfolio PnL. Full reversal mean return was−10.31%. The frozen sensor/full models agree on the wrong sign, so disagreement cannot reveal remapping. The20-date drift window and hard-coded first scan628 impose delay. Replacing only the schedule would cross the original threshold at [623, 621, 623, 623]. See iteration5_diagnosis.json for exact per-seed counts and timestamps.

No zero-delay switch detector is identifiable here: iid symmetric sensor marginals, unconditional returns, and entire price paths are unchanged by sensor remapping. Under the required signal+3 availability rule,606 outcomes first enter at609. Later statistical accumulation is necessary to avoid excessive false alarms; not all393 later errors can simply be eliminated.

## Frozen gate

Iteration5 classifier, bands, train/cal split, disagreement filter and DGP remain unchanged. Before each entry, the gate evaluates2/4/8-date sensor-conditioned extreme-cell residual contrasts, which cancel common-date return shocks. At least2 names in each extreme cell are required per date; missing dates conservatively skip the look. An independent channel monitors date-grouped forecast errors of actual funded, matured fills. A drift alarm causes full abstention for the remaining horizon. There is no forecast-sign flip or automatic recovery. All outcomes obey signal+3<=decision.

Market/sector breadth was assessed and rejected as a switch detector: there are no sector effects or memberships, and prices are bit-identical across stable and reversal scenarios. No informative synthetic indicator was added. Residual trend conditioned on the sensor is informative. All first fresh alarms came from cross-sectional residual evidence; funded surprise did not lead detection, so this run does not establish incremental benefit from that second channel. Threshold envelopes and multiplicity bounds are prescribed synthetic engineering assumptions, not certified real-data error guarantees.

## Measured comparisons

Arithmetic per-seed means; return and MDD below use the adverse segment starting at the switch, including terminal liquidation. Costs are full-window dollars per initial$100,000 account. Random-switch total returns include earlier planted gains and therefore are not used as the adverse-loss metric.

| Phase / scenario / policy | False GREAT | Detection delay | Adverse return | Adverse MDD | Costs |
|---|---:|---|---:|---:|---:|
| paired_regression / reversal / iteration5 | 442 | [22, 22, 22, 22] | -10.31% | 10.31% | $3,104 |
| paired_regression / reversal / iteration6 | 116 | [7, 6, 5, 6] | -2.83% | 2.83% | $886 |
| final / reversal / iteration5 | 393 | [22, 22, 22, 22] | -10.30% | 10.30% | $3,136 |
| final / reversal / iteration6 | 86 | [5, 5, 5, 4] | -2.24% | 2.24% | $762 |
| final / random_reversal / iteration5 | 338 | [18, 18, 18, 16] | -8.26% | 8.71% | $11,154 |
| final / random_reversal / iteration6 | 84 | [4, 4, 4, 7] | -2.61% | 3.09% | $8,966 |

Stable final learnable coverage76.3%–100%; outer-noise38.9%–100%. Stable extreme errors0; no observed alarms across four seeds, paired stable scenarios. Stable classifications, funded trades, return and costs match iteration5 exactly: no observed stable economic cost. All four null tapes fully abstain with zero costs and returns. Three of four fresh learnable seeds support all five tiers; the failing seed has inferred support[590,518,0,614,585]. No forced tiers or widened bands.

All frozen hashes match. Artifact audit verifies no funded entries on/after the latch, nonnegative cash, net/PnL reconciliation, one-session matched horizons and both-leg costs (max recomputation error7.3e-11). Modeled per-trade risk remains<=2%; the50% gap probe exceeds modeled loss as expected. Aggregate portfolio and realized gap losses are not capped at2%. Cash is a zero-yield control; no SGOV data or alpha claim.

## Process and limitations

preregister.json predates all runs. Design seeds620101/620102 and already-viewed paired tapes are separate from final seeds. commitment.json records core, reference dependency, test, runner and preregistration hashes before OS-entropy seeds/switch dates were drawn. Random switches are drawn uniformly from626–686; neither policy sees the switch. Source-freeze is local, without a trusted public timestamp. The post-run analyze.py only reads evidence and writes documentation/audits; it executes no portfolios and is separately checksummed.

Zero alarms on four independent seeds gives a52.7% one-sided95% upper seed alarm probability; paired scenarios do not increase independent seed count. The observed false-alarm criterion passes, but a population<=5% claim is unsupported. Fresh tapes validate this synthetic engineering change, not real PIT predictors or production readiness. The inherited five-tier support failure remains. Available PIT information supports faster detection after outcomes accrue; it cannot support risk-free immediate recognition.

## Artifacts and commands

report.json contains explicit PASS/FAIL for every preregistered check. confusion.csv includes UNKNOWN and individual-latent truth; portfolio.csv contains all return/CAGR/MDD/cost/risk metrics. detection.csv, economic_paired.csv, audit.csv, opportunities.jsonl.gz and replays.jsonl.gz provide timestamps, all-opportunity outcomes and actual funded ledgers. checksums.json covers artifacts.

Run `python3 analyze.py` in this directory to re-audit archived results without portfolios. `python3 run.py` refuses reuse after commitment. Tests are in test_engine.py; rerunning them executes three additional portfolios outside the archived59 and must not be presented as part of this frozen experiment.

**Next blocker:** obtain enough independent fit/calibration evidence for the missing middle tier, and independently validate residual exposure and false-alarm rates before any promotion. Do not tune these evaluated final seeds.

```


## discrimination_iteration6/analyze.py

```
"""Post-evaluation artifact audit and documentation only; zero portfolio replays."""
import csv,gzip,json,math,statistics as st
from pathlib import Path
import engine as x
O=x.O

def main():
 r=json.loads((O/'report.json').read_text());commit=json.loads((O/'commitment.json').read_text());assert all(x.e.sha(p)==h for p,h in commit['sources'].items())
 diag=json.loads((O/'iteration5_diagnosis.json').read_text())
 for z in diag['rows']:
  p,f,_=x.e.generate(z['seed'],'reversal');models=x.e.fit(p,f);first=None
  for now in range(x.START,x.START+23):
   for c,m in enumerate(models):
    vals=x.e.dates(p,f,range(now-22,now-2),c)
    if len(vals)<15:continue
    threshold=.018*math.sqrt(2*math.log(2*5*26/.05)*(1/len(vals)+1/m['ntrain']))
    if abs(x.e.mean([v for _,v in vals])-m['mean'])>threshold:first=now;break
   if first is not None:break
  z['earliest_original_window_threshold_crossing_without_scan_schedule']=first
  # After availability is potentially detectable, not guaranteed immediately distinguishable.
  z['post_first_information']=z.pop('fixable_after_first3')
 diag['qualification']='First3 counts quantify an information lower bound for these tapes. Later counts are potentially avoidable exposure, not a guarantee of error-free detection at session609. Original20-date window itself needs accumulation; threshold crossings below isolate scheduling from window/threshold delay.'
 (O/'iteration5_diagnosis.json').write_text(json.dumps(diag,indent=2));r['diagnosis']=diag
 funded_gate_ok=True;null_ok=True;cost_error=0.;funded_count=0
 with gzip.open(O/'replays.jsonl.gz','rt') as f:
  for line in f:
   a=json.loads(line)
   if a['variant']!='iteration6':continue
   det=next(d for d in r['detection'] if all(d[k]==a[k] for k in ['seed','scenario','phase','variant']))
   if det['first_detection'] is not None:funded_gate_ok &= all(t['signal']<det['first_detection'] for t in a['trades'])
   if a['scenario']=='null':null_ok &= not a['trades'] and all(d['nav']==100000 for d in a['daily'])
   expected=sum(t['shares']*(t['entry_open']+t['exit_open'])*x.COST/2 for t in a['trades'])
   metric=next(m for m in r['portfolio'] if all(m[k]==a[k] for k in ['seed','scenario','phase','variant']))
   cost_error=max(cost_error,abs(expected-metric['costs']));funded_count+=len(a['trades'])
 assert funded_gate_ok and null_ok and cost_error<1e-7
 r['post_run_artifact_audit']=dict(zero_new_replays=True,funded_gate_ok=funded_gate_ok,null_cash_and_cost_ok=null_ok,max_both_leg_cost_error=cost_error,funded_trades_checked=funded_count,frozen_hashes_match=True)
 paired=[]
 for a in r['portfolio']:
  if a['variant']!='iteration6':continue
  b=next((b for b in r['portfolio'] if b['variant']=='iteration5' and all(b[k]==a[k] for k in ['seed','scenario','phase'])),None)
  if b:paired.append(dict(seed=a['seed'],scenario=a['scenario'],phase=a['phase'],**{k+'_delta':a[k]-b[k] for k in ['total_return','adverse_return','adverse_mdd','mdd','costs','trades']}))
 with (O/'economic_paired.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
 with (O/'detection.csv').open('w') as f:
  rows=[dict(d,events=json.dumps(d['events'])) for d in r['detection']];w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 final=[s for s in r['discrimination'] if s['phase']=='final' and s['variant']=='iteration6']
 r['next_blocker']='Five-tier support: seed2098214662956861329 has0 AVERAGE assignments. Frozen interval straddles a band; this experiment cannot repair it after final evaluation. Next independent step must obtain more independent fit/calibration evidence under unchanged bands, then freeze and test fresh tapes. Rapid safety is promising but residual4–7-session exposure and false-alarm power need independent episode validation; no safe zero-delay detection from this DGP.'
 r['false_alarm_power']=dict(independent_fresh_seeds=4,alarmed=0,one_sided95_upper_seed_probability=1-.05**.25,paired_scenarios_not_independent=True)
 (O/'report.json').write_text(json.dumps(r,indent=2))
 lines=['# Iteration6 — FAIL','',r['next_blocker'],'',f"Completed {r['portfolio_replays']} portfolio replays, six tests; runner elapsed {r['elapsed_seconds']:.2f}s. Limit64 replays/720s. Three test portfolios, four fixed design probes, twelve paired regressions, forty frozen final portfolios. No candidate tuning, GA, production changes or final reruns. All new files stay here.",'','## Diagnosis','', 'Iteration5 false GREAT count442 comprised49 in sessions606–608, before any post-change outcome was eligible, and393 after first outcome availability. Funded false GREAT trades lost $36,554 across four separate $100,000 accounts; these are a subset of portfolio PnL. Full reversal mean return was−10.31%. The frozen sensor/full models agree on the wrong sign, so disagreement cannot reveal remapping. The20-date drift window and hard-coded first scan628 impose delay. Replacing only the schedule would cross the original threshold at '+str([z['earliest_original_window_threshold_crossing_without_scan_schedule'] for z in diag['rows']])+'. See iteration5_diagnosis.json for exact per-seed counts and timestamps.','', 'No zero-delay switch detector is identifiable here: iid symmetric sensor marginals, unconditional returns, and entire price paths are unchanged by sensor remapping. Under the required signal+3 availability rule,606 outcomes first enter at609. Later statistical accumulation is necessary to avoid excessive false alarms; not all393 later errors can simply be eliminated.','', '## Frozen gate','', 'Iteration5 classifier, bands, train/cal split, disagreement filter and DGP remain unchanged. Before each entry, the gate evaluates2/4/8-date sensor-conditioned extreme-cell residual contrasts, which cancel common-date return shocks. At least2 names in each extreme cell are required per date; missing dates conservatively skip the look. An independent channel monitors date-grouped forecast errors of actual funded, matured fills. A drift alarm causes full abstention for the remaining horizon. There is no forecast-sign flip or automatic recovery. All outcomes obey signal+3<=decision.','', 'Market/sector breadth was assessed and rejected as a switch detector: there are no sector effects or memberships, and prices are bit-identical across stable and reversal scenarios. No informative synthetic indicator was added. Residual trend conditioned on the sensor is informative. All first fresh alarms came from cross-sectional residual evidence; funded surprise did not lead detection, so this run does not establish incremental benefit from that second channel. Threshold envelopes and multiplicity bounds are prescribed synthetic engineering assumptions, not certified real-data error guarantees.','', '## Measured comparisons','', 'Arithmetic per-seed means; return and MDD below use the adverse segment starting at the switch, including terminal liquidation. Costs are full-window dollars per initial$100,000 account. Random-switch total returns include earlier planted gains and therefore are not used as the adverse-loss metric.','', '| Phase / scenario / policy | False GREAT | Detection delay | Adverse return | Adverse MDD | Costs |','|---|---:|---|---:|---:|---:|']
 for phase,scenario in [('paired_regression','reversal'),('final','reversal'),('final','random_reversal')]:
  for var in ['iteration5','iteration6']:
   ms=[m for m in r['portfolio'] if m['phase']==phase and m['scenario']==scenario and m['variant']==var];ss=[s for s in r['discrimination'] if s['phase']==phase and s['scenario']==scenario and s['variant']==var];ds=[d['delay'] for d in r['detection'] if d['phase']==phase and d['scenario']==scenario and d['variant']==var]
   lines.append(f"| {phase} / {scenario} / {var} | {sum(s['false_great'] for s in ss)} | {ds} | {st.mean(m['adverse_return'] for m in ms):.2%} | {st.mean(m['adverse_mdd'] for m in ms):.2%} | ${st.mean(m['costs'] for m in ms):,.0f} |")
 lines+=['', 'Stable final learnable coverage76.3%–100%; outer-noise38.9%–100%. Stable extreme errors0; no observed alarms across four seeds, paired stable scenarios. Stable classifications, funded trades, return and costs match iteration5 exactly: no observed stable economic cost. All four null tapes fully abstain with zero costs and returns. Three of four fresh learnable seeds support all five tiers; the failing seed has inferred support[590,518,0,614,585]. No forced tiers or widened bands.','', f"All frozen hashes match. Artifact audit verifies no funded entries on/after the latch, nonnegative cash, net/PnL reconciliation, one-session matched horizons and both-leg costs (max recomputation error{cost_error:.2g}). Modeled per-trade risk remains<=2%; the50% gap probe exceeds modeled loss as expected. Aggregate portfolio and realized gap losses are not capped at2%. Cash is a zero-yield control; no SGOV data or alpha claim.",'', '## Process and limitations','', 'preregister.json predates all runs. Design seeds620101/620102 and already-viewed paired tapes are separate from final seeds. commitment.json records core, reference dependency, test, runner and preregistration hashes before OS-entropy seeds/switch dates were drawn. Random switches are drawn uniformly from626–686; neither policy sees the switch. Source-freeze is local, without a trusted public timestamp. The post-run analyze.py only reads evidence and writes documentation/audits; it executes no portfolios and is separately checksummed.','', 'Zero alarms on four independent seeds gives a52.7% one-sided95% upper seed alarm probability; paired scenarios do not increase independent seed count. The observed false-alarm criterion passes, but a population<=5% claim is unsupported. Fresh tapes validate this synthetic engineering change, not real PIT predictors or production readiness. The inherited five-tier support failure remains. Available PIT information supports faster detection after outcomes accrue; it cannot support risk-free immediate recognition.','', '## Artifacts and commands','', 'report.json contains explicit PASS/FAIL for every preregistered check. confusion.csv includes UNKNOWN and individual-latent truth; portfolio.csv contains all return/CAGR/MDD/cost/risk metrics. detection.csv, economic_paired.csv, audit.csv, opportunities.jsonl.gz and replays.jsonl.gz provide timestamps, all-opportunity outcomes and actual funded ledgers. checksums.json covers artifacts.','', 'Run `python3 analyze.py` in this directory to re-audit archived results without portfolios. `python3 run.py` refuses reuse after commitment. Tests are in test_engine.py; rerunning them executes three additional portfolios outside the archived59 and must not be presented as part of this frozen experiment.','', '**Next blocker:** obtain enough independent fit/calibration evidence for the missing middle tier, and independently validate residual exposure and false-alarm rates before any promotion. Do not tune these evaluated final seeds.']
 (O/'README.md').write_text('\n'.join(lines)+'\n')
 (O/'checksums.json').write_text(json.dumps({p.name:x.e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'},indent=2))
 print('Artifact audit PASS; overall FAIL; no additional replays')
if __name__=='__main__':main()

```


## discrimination_iteration6/audit.csv

```
seed,scenario,phase,variant,min_cash,net_error,pnl_error,horizon_ok,max_risk,gap_exceed
620101,learnable,design,iteration6,0.0,2.220446049250313e-16,5.820766091346741e-11,True,0.019970044932601103,0
620101,reversal,design,iteration6,0.0,3.3306690738754696e-16,6.366462912410498e-12,True,0.019970044932601103,0
620102,learnable,design,iteration6,0.0,4.440892098500626e-16,1.4551915228366852e-10,True,0.019970044932601103,0
620102,reversal,design,iteration6,0.0,2.220446049250313e-16,1.3642420526593924e-11,True,0.0199700449326011,0
1564008556893530022,reversal,paired_regression,iteration6,0.0,2.220446049250313e-16,9.094947017729282e-13,True,0.019970044932601103,0
1564008556893530022,reversal,paired_regression,iteration5,0.0,2.220446049250313e-16,2.000888343900442e-11,True,0.019970044932601103,0
1634635432866334191,reversal,paired_regression,iteration6,0.0,2.220446049250313e-16,3.637978807091713e-12,True,0.0199700449326011,0
1634635432866334191,reversal,paired_regression,iteration5,0.0,2.220446049250313e-16,3.637978807091713e-12,True,0.0199700449326011,0
5015368413594993126,reversal,paired_regression,iteration6,0.0,2.220446049250313e-16,1.1823431123048067e-11,True,0.0199700449326011,0
5015368413594993126,reversal,paired_regression,iteration5,0.0,2.220446049250313e-16,3.092281986027956e-11,True,0.019970044932601103,0
3584306075979195116,reversal,paired_regression,iteration6,0.0,2.220446049250313e-16,1.546140993013978e-11,True,0.019970044932601103,0
3584306075979195116,reversal,paired_regression,iteration5,0.0,2.220446049250313e-16,1.0913936421275139e-11,True,0.019970044932601103,0
1564008556893530022,learnable,paired_regression,iteration6,0.0,4.440892098500626e-16,4.3655745685100555e-11,True,0.019970044932601103,0
1564008556893530022,learnable,paired_regression,iteration5,0.0,4.440892098500626e-16,4.3655745685100555e-11,True,0.019970044932601103,0
1634635432866334191,learnable,paired_regression,iteration6,0.0,4.440892098500626e-16,0.0,True,0.019970044932601103,0
1634635432866334191,learnable,paired_regression,iteration5,0.0,4.440892098500626e-16,0.0,True,0.019970044932601103,0
2098214662956861329,learnable,final,iteration6,0.0,2.220446049250313e-16,0.0,True,0.019970044932601103,0
2098214662956861329,learnable,final,iteration5,0.0,2.220446049250313e-16,0.0,True,0.019970044932601103,0
2098214662956861329,null,final,iteration6,100000.0,0,0.0,True,0,0
2098214662956861329,null,final,iteration5,100000.0,0,0.0,True,0,0
2098214662956861329,outer_noise,final,iteration6,0.0,4.440892098500626e-16,1.6007106751203537e-10,True,0.019970044932601103,0
2098214662956861329,outer_noise,final,iteration5,0.0,4.440892098500626e-16,1.6007106751203537e-10,True,0.019970044932601103,0
2098214662956861329,reversal,final,iteration6,0.0,2.220446049250313e-16,9.094947017729282e-13,True,0.019970044932601103,0
2098214662956861329,reversal,final,iteration5,0.0,2.220446049250313e-16,2.7284841053187847e-11,True,0.019970044932601103,0
2098214662956861329,random_reversal,final,iteration6,0.0,2.220446049250313e-16,7.275957614183426e-12,True,0.019970044932601103,0
2098214662956861329,random_reversal,final,iteration5,0.0,2.220446049250313e-16,9.640643838793039e-11,True,0.019970044932601103,1
2928371724749768812,learnable,final,iteration6,0.0,4.440892098500626e-16,4.3655745685100555e-11,True,0.019970044932601103,0
2928371724749768812,learnable,final,iteration5,0.0,4.440892098500626e-16,4.3655745685100555e-11,True,0.019970044932601103,0
2928371724749768812,null,final,iteration6,100000.0,0,0.0,True,0,0
2928371724749768812,null,final,iteration5,100000.0,0,0.0,True,0,0
2928371724749768812,outer_noise,final,iteration6,0.0,3.3306690738754696e-16,2.9103830456733704e-11,True,0.019970044932601103,0
2928371724749768812,outer_noise,final,iteration5,0.0,3.3306690738754696e-16,2.9103830456733704e-11,True,0.019970044932601103,0
2928371724749768812,reversal,final,iteration6,0.0,2.220446049250313e-16,2.0463630789890885e-11,True,0.019970044932601103,0
2928371724749768812,reversal,final,iteration5,0.0,3.3306690738754696e-16,3.8198777474462986e-11,True,0.019970044932601103,0
2928371724749768812,random_reversal,final,iteration6,0.0,4.440892098500626e-16,1.8189894035458565e-11,True,0.019970044932601103,0
2928371724749768812,random_reversal,final,iteration5,0.0,4.440892098500626e-16,3.001332515850663e-11,True,0.019970044932601103,0
5618266449171873643,learnable,final,iteration6,0.0,4.440892098500626e-16,1.0186340659856796e-10,True,0.019970044932601103,0
5618266449171873643,learnable,final,iteration5,0.0,4.440892098500626e-16,1.0186340659856796e-10,True,0.019970044932601103,0
5618266449171873643,null,final,iteration6,100000.0,0,0.0,True,0,0
5618266449171873643,null,final,iteration5,100000.0,0,0.0,True,0,0
5618266449171873643,outer_noise,final,iteration6,0.0,4.440892098500626e-16,1.7462298274040222e-10,True,0.019970044932601103,0
5618266449171873643,outer_noise,final,iteration5,0.0,4.440892098500626e-16,1.7462298274040222e-10,True,0.019970044932601103,0
5618266449171873643,reversal,final,iteration6,0.0,1.1102230246251565e-16,6.821210263296962e-12,True,0.0199700449326011,0
5618266449171873643,reversal,final,iteration5,0.0,2.220446049250313e-16,3.2741809263825417e-11,True,0.0199700449326011,0
5618266449171873643,random_reversal,final,iteration6,0.0,2.220446049250313e-16,1.4551915228366852e-11,True,0.019970044932601103,0
5618266449171873643,random_reversal,final,iteration5,0.0,2.220446049250313e-16,2.7284841053187847e-12,True,0.019970044932601103,0
8582935296371253491,learnable,final,iteration6,0.0,4.440892098500626e-16,7.275957614183426e-11,True,0.019970044932601103,0
8582935296371253491,learnable,final,iteration5,0.0,4.440892098500626e-16,7.275957614183426e-11,True,0.019970044932601103,0
8582935296371253491,null,final,iteration6,100000.0,0,0.0,True,0,0
8582935296371253491,null,final,iteration5,100000.0,0,0.0,True,0,0
8582935296371253491,outer_noise,final,iteration6,0.0,2.220446049250313e-16,1.4551915228366852e-11,True,0.019970044932601103,0
8582935296371253491,outer_noise,final,iteration5,0.0,2.220446049250313e-16,1.4551915228366852e-11,True,0.019970044932601103,0
8582935296371253491,reversal,final,iteration6,0.0,2.220446049250313e-16,2.432898327242583e-11,True,0.0199700449326011,0
8582935296371253491,reversal,final,iteration5,0.0,2.220446049250313e-16,3.637978807091713e-11,True,0.019970044932601103,0
8582935296371253491,random_reversal,final,iteration6,0.0,4.440892098500626e-16,1.1641532182693481e-10,True,0.019970044932601103,0
8582935296371253491,random_reversal,final,iteration5,0.0,4.440892098500626e-16,1.0913936421275139e-10,True,0.019970044932601103,0

```


## discrimination_iteration6/checksums.json

```
{
  "README.md": "8db5b65448905b58e26ad726aff16226e517b901d226e09793d0ff1d145062df",
  "analyze.py": "789010a010d39f5a2713bdf845bfe8fe95a1e05f9fb92aec2aaef4a27f3593c8",
  "audit.csv": "f94d042f765215a0405b278c3ee9e8c55054f70f741ab9d427d53acc35c4219c",
  "commitment.json": "aacaaedb6fae349e737d8dd92d23463abfae354551e3fe3c7ceeb8da9ab3c596",
  "confusion.csv": "a2c7049524f02ef77b14b0ff67401090c599ec21927b5db73734e050cf60b23a",
  "detection.csv": "549b4af865c9cc210df6c86d92149225f6a1be3f7b430c48616d33082c2467a4",
  "economic_paired.csv": "368befdbee6460fe954af6bdae2d3c952ee48fa56ff2f79104deddc9983cf343",
  "engine.py": "0cb88a0fa95620f1d6881235bdf748be3349a142cd4002a565ba4d45bfb1b319",
  "iteration5_diagnosis.json": "1374a92cd2c79654f86b71ee2da8bdae93c82cc25dab3c345395c2bf8945ea2b",
  "opportunities.jsonl.gz": "a59fc743228adcef3aa522dc15e4fc5e0677451bff602d84f889ad691c44e379",
  "paired.csv": "ba5f70a5d2d343f863e4885e40f3e7377e87d65080db1826c698b4cd02d0c236",
  "portfolio.csv": "51c0281836b479f73fac1d720bf9014465b4993e184bb4c0d977c35cfdefd0b5",
  "preregister.json": "6fc3d1acbe2ad094c3986175f49a87c934e8c101965e96d8df2aa136c3ecdb57",
  "replays.jsonl.gz": "bcc810a063d1e6af49e1f2dd8c5d13ffc89fdc31eb0d4a63f6cef7a0b8b03f78",
  "report.json": "bf5d6f58651f932cf36e2d32c4f77de80d2f8e5312d1f78063430eab007663b4",
  "run.py": "0b01f2a6ffe8b15de312a3dc435bbfd9466657ff7b07f2e1d53defd06ca6df21",
  "seeds.json": "0d12cc468412377eeba76c2cc0e7de36abfc4b9f0206dba90e6464b40c6da511",
  "test_engine.py": "b517d042804dd3704d2636244a37c33f8fe89f8ef4d40409d90299d875627bd6",
  "tests.log": "ff49442e6ba703461108559dd030276de2effec6559ba2daf9644a36e4ab95d8"
}
```


## discrimination_iteration6/commitment.json

```
{
  "utc": "2026-11-01T14:34:59.751034+00:00",
  "sources": {
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration6/engine.py": "0cb88a0fa95620f1d6881235bdf748be3349a142cd4002a565ba4d45bfb1b319",
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration6/run.py": "0b01f2a6ffe8b15de312a3dc435bbfd9466657ff7b07f2e1d53defd06ca6df21",
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration6/test_engine.py": "b517d042804dd3704d2636244a37c33f8fe89f8ef4d40409d90299d875627bd6",
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration6/preregister.json": "6fc3d1acbe2ad094c3986175f49a87c934e8c101965e96d8df2aa136c3ecdb57",
    "/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/discrimination_iteration5/experiment.py": "374e1fda136c50c643cbfce4ab2bd1ed26274b19b433dfc38109ead03a1b50a0"
  },
  "pre_final_replays": 19,
  "public_timestamp": false
}
```


## discrimination_iteration6/confusion.csv

```
seed,scenario,phase,variant,truth,TERRIBLE,POOR,AVERAGE,GOOD,GREAT,UNKNOWN
620101,learnable,design,iteration6,TERRIBLE,568,26,0,0,0,0
620101,learnable,design,iteration6,POOR,19,541,10,0,0,0
620101,learnable,design,iteration6,AVERAGE,0,9,608,11,0,0
620101,learnable,design,iteration6,GOOD,0,0,12,573,16,0
620101,learnable,design,iteration6,GREAT,0,0,0,14,617,0
620101,reversal,design,iteration6,TERRIBLE,0,0,0,2,68,524
620101,reversal,design,iteration6,POOR,0,0,1,54,0,515
620101,reversal,design,iteration6,AVERAGE,0,4,73,0,0,551
620101,reversal,design,iteration6,GOOD,1,65,5,0,0,530
620101,reversal,design,iteration6,GREAT,61,2,0,0,0,568
620102,learnable,design,iteration6,TERRIBLE,571,11,0,0,0,4
620102,learnable,design,iteration6,POOR,22,390,14,0,0,197
620102,learnable,design,iteration6,AVERAGE,0,9,559,12,0,2
620102,learnable,design,iteration6,GOOD,0,0,14,575,14,0
620102,learnable,design,iteration6,GREAT,0,0,0,21,609,0
620102,reversal,design,iteration6,TERRIBLE,0,0,0,0,17,569
620102,reversal,design,iteration6,POOR,0,0,1,16,0,606
620102,reversal,design,iteration6,AVERAGE,0,0,25,1,0,556
620102,reversal,design,iteration6,GOOD,0,9,2,0,0,592
620102,reversal,design,iteration6,GREAT,16,1,0,0,0,613
1564008556893530022,reversal,paired_regression,iteration6,TERRIBLE,0,0,0,0,36,586
1564008556893530022,reversal,paired_regression,iteration6,POOR,0,0,0,30,1,521
1564008556893530022,reversal,paired_regression,iteration6,AVERAGE,0,2,32,1,0,581
1564008556893530022,reversal,paired_regression,iteration6,GOOD,0,33,1,0,0,597
1564008556893530022,reversal,paired_regression,iteration6,GREAT,31,1,0,0,0,571
1564008556893530022,reversal,paired_regression,iteration5,TERRIBLE,0,0,0,0,108,514
1564008556893530022,reversal,paired_regression,iteration5,POOR,0,0,0,94,1,457
1564008556893530022,reversal,paired_regression,iteration5,AVERAGE,0,4,108,3,0,501
1564008556893530022,reversal,paired_regression,iteration5,GOOD,1,105,2,0,0,523
1564008556893530022,reversal,paired_regression,iteration5,GREAT,98,4,0,0,0,501
1634635432866334191,reversal,paired_regression,iteration6,TERRIBLE,0,0,0,1,33,552
1634635432866334191,reversal,paired_regression,iteration6,POOR,0,0,0,21,0,571
1634635432866334191,reversal,paired_regression,iteration6,AVERAGE,0,0,27,1,0,589
1634635432866334191,reversal,paired_regression,iteration6,GOOD,0,0,1,0,0,649
1634635432866334191,reversal,paired_regression,iteration6,GREAT,30,0,0,0,0,549
1634635432866334191,reversal,paired_regression,iteration5,TERRIBLE,0,0,0,3,120,463
1634635432866334191,reversal,paired_regression,iteration5,POOR,0,0,0,78,4,510
1634635432866334191,reversal,paired_regression,iteration5,AVERAGE,0,0,109,2,0,506
1634635432866334191,reversal,paired_regression,iteration5,GOOD,1,0,6,0,0,643
1634635432866334191,reversal,paired_regression,iteration5,GREAT,106,0,0,0,0,473
5015368413594993126,reversal,paired_regression,iteration6,TERRIBLE,0,0,0,0,19,604
5015368413594993126,reversal,paired_regression,iteration6,POOR,0,0,0,13,1,598
5015368413594993126,reversal,paired_regression,iteration6,AVERAGE,0,0,19,0,0,600
5015368413594993126,reversal,paired_regression,iteration6,GOOD,1,25,0,0,0,584
5015368413594993126,reversal,paired_regression,iteration6,GREAT,23,1,0,0,0,536
5015368413594993126,reversal,paired_regression,iteration5,TERRIBLE,0,0,0,0,105,518
5015368413594993126,reversal,paired_regression,iteration5,POOR,0,0,1,40,2,569
5015368413594993126,reversal,paired_regression,iteration5,AVERAGE,0,2,114,1,0,502
5015368413594993126,reversal,paired_regression,iteration5,GOOD,2,104,3,0,0,501
5015368413594993126,reversal,paired_regression,iteration5,GREAT,98,3,0,0,0,459
3584306075979195116,reversal,paired_regression,iteration6,TERRIBLE,0,0,0,1,28,581
3584306075979195116,reversal,paired_regression,iteration6,POOR,0,0,0,25,1,603
3584306075979195116,reversal,paired_regression,iteration6,AVERAGE,0,1,0,1,0,602
3584306075979195116,reversal,paired_regression,iteration6,GOOD,1,26,0,0,0,563
3584306075979195116,reversal,paired_regression,iteration6,GREAT,28,1,0,0,0,562
3584306075979195116,reversal,paired_regression,iteration5,TERRIBLE,0,0,0,4,109,497
3584306075979195116,reversal,paired_regression,iteration5,POOR,0,0,0,103,3,523
3584306075979195116,reversal,paired_regression,iteration5,AVERAGE,0,3,0,3,0,598
3584306075979195116,reversal,paired_regression,iteration5,GOOD,4,93,0,0,0,493
3584306075979195116,reversal,paired_regression,iteration5,GREAT,108,2,0,0,0,481
1564008556893530022,learnable,paired_regression,iteration6,TERRIBLE,611,11,0,0,0,0
1564008556893530022,learnable,paired_regression,iteration6,POOR,14,519,19,0,0,0
1564008556893530022,learnable,paired_regression,iteration6,AVERAGE,0,17,576,23,0,0
1564008556893530022,learnable,paired_regression,iteration6,GOOD,0,0,20,588,23,0
1564008556893530022,learnable,paired_regression,iteration6,GREAT,0,0,0,18,585,0
1564008556893530022,learnable,paired_regression,iteration5,TERRIBLE,611,11,0,0,0,0
1564008556893530022,learnable,paired_regression,iteration5,POOR,14,519,19,0,0,0
1564008556893530022,learnable,paired_regression,iteration5,AVERAGE,0,17,576,23,0,0
1564008556893530022,learnable,paired_regression,iteration5,GOOD,0,0,20,588,23,0
1564008556893530022,learnable,paired_regression,iteration5,GREAT,0,0,0,18,585,0
1634635432866334191,learnable,paired_regression,iteration6,TERRIBLE,570,0,0,0,0,16
1634635432866334191,learnable,paired_regression,iteration6,POOR,20,0,9,0,0,563
1634635432866334191,learnable,paired_regression,iteration6,AVERAGE,0,0,595,15,0,7
1634635432866334191,learnable,paired_regression,iteration6,GOOD,0,0,19,607,24,0
1634635432866334191,learnable,paired_regression,iteration6,GREAT,0,0,0,12,567,0
1634635432866334191,learnable,paired_regression,iteration5,TERRIBLE,570,0,0,0,0,16
1634635432866334191,learnable,paired_regression,iteration5,POOR,20,0,9,0,0,563
1634635432866334191,learnable,paired_regression,iteration5,AVERAGE,0,0,595,15,0,7
1634635432866334191,learnable,paired_regression,iteration5,GOOD,0,0,19,607,24,0
1634635432866334191,learnable,paired_regression,iteration5,GREAT,0,0,0,12,567,0
2098214662956861329,learnable,final,iteration6,TERRIBLE,578,14,0,0,0,2
2098214662956861329,learnable,final,iteration6,POOR,12,491,0,0,0,122
2098214662956861329,learnable,final,iteration6,AVERAGE,0,13,0,12,0,575
2098214662956861329,learnable,final,iteration6,GOOD,0,0,0,582,18,18
2098214662956861329,learnable,final,iteration6,GREAT,0,0,0,20,567,0
2098214662956861329,learnable,final,iteration5,TERRIBLE,578,14,0,0,0,2
2098214662956861329,learnable,final,iteration5,POOR,12,491,0,0,0,122
2098214662956861329,learnable,final,iteration5,AVERAGE,0,13,0,12,0,575
2098214662956861329,learnable,final,iteration5,GOOD,0,0,0,582,18,18
2098214662956861329,learnable,final,iteration5,GREAT,0,0,0,20,567,0
2098214662956861329,null,final,iteration6,TERRIBLE,0,0,0,0,0,594
2098214662956861329,null,final,iteration6,POOR,0,0,0,0,0,625
2098214662956861329,null,final,iteration6,AVERAGE,0,0,0,0,0,600
2098214662956861329,null,final,iteration6,GOOD,0,0,0,0,0,618
2098214662956861329,null,final,iteration6,GREAT,0,0,0,0,0,587
2098214662956861329,null,final,iteration5,TERRIBLE,0,0,0,0,0,594
2098214662956861329,null,final,iteration5,POOR,0,0,0,0,0,625
2098214662956861329,null,final,iteration5,AVERAGE,0,0,0,0,0,600
2098214662956861329,null,final,iteration5,GOOD,0,0,0,0,0,618
2098214662956861329,null,final,iteration5,GREAT,0,0,0,0,0,587
2098214662956861329,outer_noise,final,iteration6,TERRIBLE,578,0,0,0,0,16
2098214662956861329,outer_noise,final,iteration6,POOR,12,0,0,0,0,613
2098214662956861329,outer_noise,final,iteration6,AVERAGE,0,0,0,0,0,600
2098214662956861329,outer_noise,final,iteration6,GOOD,0,0,0,0,18,600
2098214662956861329,outer_noise,final,iteration6,GREAT,0,0,0,0,567,20
2098214662956861329,outer_noise,final,iteration5,TERRIBLE,578,0,0,0,0,16
2098214662956861329,outer_noise,final,iteration5,POOR,12,0,0,0,0,613
2098214662956861329,outer_noise,final,iteration5,AVERAGE,0,0,0,0,0,600
2098214662956861329,outer_noise,final,iteration5,GOOD,0,0,0,0,18,600
2098214662956861329,outer_noise,final,iteration5,GREAT,0,0,0,0,567,20
2098214662956861329,reversal,final,iteration6,TERRIBLE,0,0,0,1,22,571
2098214662956861329,reversal,final,iteration6,POOR,0,0,0,21,0,604
2098214662956861329,reversal,final,iteration6,AVERAGE,0,0,0,1,0,599
2098214662956861329,reversal,final,iteration6,GOOD,1,19,0,0,0,598
2098214662956861329,reversal,final,iteration6,GREAT,27,1,0,0,0,559
2098214662956861329,reversal,final,iteration5,TERRIBLE,0,0,0,4,107,483
2098214662956861329,reversal,final,iteration5,POOR,0,0,0,94,1,530
2098214662956861329,reversal,final,iteration5,AVERAGE,0,0,0,2,0,598
2098214662956861329,reversal,final,iteration5,GOOD,5,93,0,0,0,520
2098214662956861329,reversal,final,iteration5,GREAT,108,3,0,0,0,476
2098214662956861329,random_reversal,final,iteration6,TERRIBLE,238,4,0,0,21,331
2098214662956861329,random_reversal,final,iteration6,POOR,5,188,0,15,0,417
2098214662956861329,random_reversal,final,iteration6,AVERAGE,0,6,0,5,0,589
2098214662956861329,random_reversal,final,iteration6,GOOD,1,13,0,263,10,331
2098214662956861329,random_reversal,final,iteration6,GREAT,16,0,0,10,246,315
2098214662956861329,random_reversal,final,iteration5,TERRIBLE,238,4,0,1,85,266
2098214662956861329,random_reversal,final,iteration5,POOR,5,188,0,87,2,343
2098214662956861329,random_reversal,final,iteration5,AVERAGE,0,8,0,6,0,586
2098214662956861329,random_reversal,final,iteration5,GOOD,2,51,0,263,10,292
2098214662956861329,random_reversal,final,iteration5,GREAT,80,1,0,10,246,250
2928371724749768812,learnable,final,iteration6,TERRIBLE,577,16,0,0,0,0
2928371724749768812,learnable,final,iteration6,POOR,9,532,13,0,0,1
2928371724749768812,learnable,final,iteration6,AVERAGE,0,21,570,20,0,52
2928371724749768812,learnable,final,iteration6,GOOD,0,0,13,564,12,1
2928371724749768812,learnable,final,iteration6,GREAT,0,0,0,21,602,0
2928371724749768812,learnable,final,iteration5,TERRIBLE,577,16,0,0,0,0
2928371724749768812,learnable,final,iteration5,POOR,9,532,13,0,0,1
2928371724749768812,learnable,final,iteration5,AVERAGE,0,21,570,20,0,52
2928371724749768812,learnable,final,iteration5,GOOD,0,0,13,564,12,1
2928371724749768812,learnable,final,iteration5,GREAT,0,0,0,21,602,0
2928371724749768812,null,final,iteration6,TERRIBLE,0,0,0,0,0,593
2928371724749768812,null,final,iteration6,POOR,0,0,0,0,0,555
2928371724749768812,null,final,iteration6,AVERAGE,0,0,0,0,0,663
2928371724749768812,null,final,iteration6,GOOD,0,0,0,0,0,590
2928371724749768812,null,final,iteration6,GREAT,0,0,0,0,0,623
2928371724749768812,null,final,iteration5,TERRIBLE,0,0,0,0,0,593
2928371724749768812,null,final,iteration5,POOR,0,0,0,0,0,555
2928371724749768812,null,final,iteration5,AVERAGE,0,0,0,0,0,663
2928371724749768812,null,final,iteration5,GOOD,0,0,0,0,0,590
2928371724749768812,null,final,iteration5,GREAT,0,0,0,0,0,623
2928371724749768812,outer_noise,final,iteration6,TERRIBLE,577,16,0,0,0,0
2928371724749768812,outer_noise,final,iteration6,POOR,9,528,0,0,0,18
2928371724749768812,outer_noise,final,iteration6,AVERAGE,0,21,0,20,0,622
2928371724749768812,outer_noise,final,iteration6,GOOD,0,0,0,564,12,14
2928371724749768812,outer_noise,final,iteration6,GREAT,0,0,0,21,602,0
2928371724749768812,outer_noise,final,iteration5,TERRIBLE,577,16,0,0,0,0
2928371724749768812,outer_noise,final,iteration5,POOR,9,528,0,0,0,18
2928371724749768812,outer_noise,final,iteration5,AVERAGE,0,21,0,20,0,622
2928371724749768812,outer_noise,final,iteration5,GOOD,0,0,0,564,12,14
2928371724749768812,outer_noise,final,iteration5,GREAT,0,0,0,21,602,0
2928371724749768812,reversal,final,iteration6,TERRIBLE,0,0,0,1,28,564
2928371724749768812,reversal,final,iteration6,POOR,0,0,0,17,0,538
2928371724749768812,reversal,final,iteration6,AVERAGE,0,1,27,0,0,635
2928371724749768812,reversal,final,iteration6,GOOD,0,20,0,0,0,570
2928371724749768812,reversal,final,iteration6,GREAT,23,1,0,0,0,599
2928371724749768812,reversal,final,iteration5,TERRIBLE,0,0,0,5,100,488
2928371724749768812,reversal,final,iteration5,POOR,0,0,1,97,2,455
2928371724749768812,reversal,final,iteration5,AVERAGE,0,4,111,2,0,546
2928371724749768812,reversal,final,iteration5,GOOD,3,105,1,0,0,481
2928371724749768812,reversal,final,iteration5,GREAT,83,3,0,0,0,537
2928371724749768812,random_reversal,final,iteration6,TERRIBLE,189,6,0,1,13,384
2928371724749768812,random_reversal,final,iteration6,POOR,4,183,4,14,1,349
2928371724749768812,random_reversal,final,iteration6,AVERAGE,0,5,204,8,0,446
2928371724749768812,random_reversal,final,iteration6,GOOD,0,9,4,190,4,383
2928371724749768812,random_reversal,final,iteration6,GREAT,20,2,0,8,164,429
2928371724749768812,random_reversal,final,iteration5,TERRIBLE,189,6,0,3,81,314
2928371724749768812,random_reversal,final,iteration5,POOR,4,183,5,64,1,298
2928371724749768812,random_reversal,final,iteration5,AVERAGE,0,7,261,11,0,384
2928371724749768812,random_reversal,final,iteration5,GOOD,1,85,7,190,4,303
2928371724749768812,random_reversal,final,iteration5,GREAT,87,4,0,8,164,360
5618266449171873643,learnable,final,iteration6,TERRIBLE,559,20,0,0,0,0
5618266449171873643,learnable,final,iteration6,POOR,17,606,15,0,0,0
5618266449171873643,learnable,final,iteration6,AVERAGE,0,18,576,22,0,0
5618266449171873643,learnable,final,iteration6,GOOD,0,0,11,559,18,0
5618266449171873643,learnable,final,iteration6,GREAT,0,0,0,20,583,0
5618266449171873643,learnable,final,iteration5,TERRIBLE,559,20,0,0,0,0
5618266449171873643,learnable,final,iteration5,POOR,17,606,15,0,0,0
5618266449171873643,learnable,final,iteration5,AVERAGE,0,18,576,22,0,0
5618266449171873643,learnable,final,iteration5,GOOD,0,0,11,559,18,0
5618266449171873643,learnable,final,iteration5,GREAT,0,0,0,20,583,0
5618266449171873643,null,final,iteration6,TERRIBLE,0,0,0,0,0,579
5618266449171873643,null,final,iteration6,POOR,0,0,0,0,0,638
5618266449171873643,null,final,iteration6,AVERAGE,0,0,0,0,0,616
5618266449171873643,null,final,iteration6,GOOD,0,0,0,0,0,588
5618266449171873643,null,final,iteration6,GREAT,0,0,0,0,0,603
5618266449171873643,null,final,iteration5,TERRIBLE,0,0,0,0,0,579
5618266449171873643,null,final,iteration5,POOR,0,0,0,0,0,638
5618266449171873643,null,final,iteration5,AVERAGE,0,0,0,0,0,616
5618266449171873643,null,final,iteration5,GOOD,0,0,0,0,0,588
5618266449171873643,null,final,iteration5,GREAT,0,0,0,0,0,603
5618266449171873643,outer_noise,final,iteration6,TERRIBLE,559,20,0,0,0,0
5618266449171873643,outer_noise,final,iteration6,POOR,17,606,15,0,0,0
5618266449171873643,outer_noise,final,iteration6,AVERAGE,0,18,576,22,0,0
5618266449171873643,outer_noise,final,iteration6,GOOD,0,0,11,559,18,0
5618266449171873643,outer_noise,final,iteration6,GREAT,0,0,0,20,583,0
5618266449171873643,outer_noise,final,iteration5,TERRIBLE,559,20,0,0,0,0
5618266449171873643,outer_noise,final,iteration5,POOR,17,606,15,0,0,0
5618266449171873643,outer_noise,final,iteration5,AVERAGE,0,18,576,22,0,0
5618266449171873643,outer_noise,final,iteration5,GOOD,0,0,11,559,18,0
5618266449171873643,outer_noise,final,iteration5,GREAT,0,0,0,20,583,0
5618266449171873643,reversal,final,iteration6,TERRIBLE,0,0,0,1,23,555
5618266449171873643,reversal,final,iteration6,POOR,0,0,0,27,0,611
5618266449171873643,reversal,final,iteration6,AVERAGE,0,1,21,1,0,593
5618266449171873643,reversal,final,iteration6,GOOD,0,23,0,0,0,565
5618266449171873643,reversal,final,iteration6,GREAT,23,0,0,0,0,580
5618266449171873643,reversal,final,iteration5,TERRIBLE,0,0,0,6,81,492
5618266449171873643,reversal,final,iteration5,POOR,0,0,4,115,3,516
5618266449171873643,reversal,final,iteration5,AVERAGE,0,7,102,4,0,503
5618266449171873643,reversal,final,iteration5,GOOD,6,94,1,0,0,487
5618266449171873643,reversal,final,iteration5,GREAT,100,5,0,0,0,498
5618266449171873643,random_reversal,final,iteration6,TERRIBLE,107,6,0,3,23,440
5618266449171873643,random_reversal,final,iteration6,POOR,5,142,5,16,0,470
5618266449171873643,random_reversal,final,iteration6,AVERAGE,0,4,145,9,0,458
5618266449171873643,random_reversal,final,iteration6,GOOD,1,17,1,128,6,435
5618266449171873643,random_reversal,final,iteration6,GREAT,17,1,0,5,127,453
5618266449171873643,random_reversal,final,iteration5,TERRIBLE,107,6,0,5,101,360
5618266449171873643,random_reversal,final,iteration5,POOR,5,142,6,77,2,406
5618266449171873643,random_reversal,final,iteration5,AVERAGE,0,8,204,12,0,392
5618266449171873643,random_reversal,final,iteration5,GOOD,3,88,3,128,6,360
5618266449171873643,random_reversal,final,iteration5,GREAT,65,4,0,5,127,402
8582935296371253491,learnable,final,iteration6,TERRIBLE,616,10,0,0,0,0
8582935296371253491,learnable,final,iteration6,POOR,18,583,18,0,0,0
8582935296371253491,learnable,final,iteration6,AVERAGE,0,17,537,13,0,0
8582935296371253491,learnable,final,iteration6,GOOD,0,0,15,573,9,0
8582935296371253491,learnable,final,iteration6,GREAT,0,0,0,15,600,0
8582935296371253491,learnable,final,iteration5,TERRIBLE,616,10,0,0,0,0
8582935296371253491,learnable,final,iteration5,POOR,18,583,18,0,0,0
8582935296371253491,learnable,final,iteration5,AVERAGE,0,17,537,13,0,0
8582935296371253491,learnable,final,iteration5,GOOD,0,0,15,573,9,0
8582935296371253491,learnable,final,iteration5,GREAT,0,0,0,15,600,0
8582935296371253491,null,final,iteration6,TERRIBLE,0,0,0,0,0,626
8582935296371253491,null,final,iteration6,POOR,0,0,0,0,0,619
8582935296371253491,null,final,iteration6,AVERAGE,0,0,0,0,0,567
8582935296371253491,null,final,iteration6,GOOD,0,0,0,0,0,597
8582935296371253491,null,final,iteration6,GREAT,0,0,0,0,0,615
8582935296371253491,null,final,iteration5,TERRIBLE,0,0,0,0,0,626
8582935296371253491,null,final,iteration5,POOR,0,0,0,0,0,619
8582935296371253491,null,final,iteration5,AVERAGE,0,0,0,0,0,567
8582935296371253491,null,final,iteration5,GOOD,0,0,0,0,0,597
8582935296371253491,null,final,iteration5,GREAT,0,0,0,0,0,615
8582935296371253491,outer_noise,final,iteration6,TERRIBLE,616,10,0,0,0,0
8582935296371253491,outer_noise,final,iteration6,POOR,18,583,18,0,0,0
8582935296371253491,outer_noise,final,iteration6,AVERAGE,0,17,537,13,0,0
8582935296371253491,outer_noise,final,iteration6,GOOD,0,0,15,499,9,74
8582935296371253491,outer_noise,final,iteration6,GREAT,0,0,0,11,600,4
8582935296371253491,outer_noise,final,iteration5,TERRIBLE,616,10,0,0,0,0
8582935296371253491,outer_noise,final,iteration5,POOR,18,583,18,0,0,0
8582935296371253491,outer_noise,final,iteration5,AVERAGE,0,17,537,13,0,0
8582935296371253491,outer_noise,final,iteration5,GOOD,0,0,15,499,9,74
8582935296371253491,outer_noise,final,iteration5,GREAT,0,0,0,11,600,4
8582935296371253491,reversal,final,iteration6,TERRIBLE,0,0,0,0,13,613
8582935296371253491,reversal,final,iteration6,POOR,0,0,1,17,2,599
8582935296371253491,reversal,final,iteration6,AVERAGE,0,1,15,0,0,551
8582935296371253491,reversal,final,iteration6,GOOD,0,22,1,0,0,574
8582935296371253491,reversal,final,iteration6,GREAT,23,1,0,0,0,591
8582935296371253491,reversal,final,iteration5,TERRIBLE,0,0,0,2,105,519
8582935296371253491,reversal,final,iteration5,POOR,0,0,5,105,6,503
8582935296371253491,reversal,final,iteration5,AVERAGE,0,2,94,3,0,468
8582935296371253491,reversal,final,iteration5,GOOD,2,87,3,0,0,505
8582935296371253491,reversal,final,iteration5,GREAT,112,2,0,0,0,501
8582935296371253491,random_reversal,final,iteration6,TERRIBLE,345,6,0,0,27,248
8582935296371253491,random_reversal,final,iteration6,POOR,15,314,13,36,0,241
8582935296371253491,random_reversal,final,iteration6,AVERAGE,0,13,319,7,0,228
8582935296371253491,random_reversal,final,iteration6,GOOD,1,33,10,320,6,227
8582935296371253491,random_reversal,final,iteration6,GREAT,40,1,0,5,337,232
8582935296371253491,random_reversal,final,iteration5,TERRIBLE,345,6,0,0,71,204
8582935296371253491,random_reversal,final,iteration5,POOR,15,314,13,75,2,200
8582935296371253491,random_reversal,final,iteration5,AVERAGE,0,14,360,8,0,185
8582935296371253491,random_reversal,final,iteration5,GOOD,1,74,10,320,6,186
8582935296371253491,random_reversal,final,iteration5,GREAT,85,3,0,5,337,185

```


## discrimination_iteration6/detection.csv

```
seed,scenario,phase,variant,change,first_detection,delay,false_alarm,events
620101,learnable,design,iteration6,,,,False,[]
620101,reversal,design,iteration6,606,620,14,False,"[{""index"": 620, ""last_signal"": 617, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.047450806708842386, ""threshold"": 0.04692237703041966}]}]"
620102,learnable,design,iteration6,,,,False,[]
620102,reversal,design,iteration6,606,610,4,False,"[{""index"": 610, ""last_signal"": 607, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.05355248796100778, ""threshold"": 0.04692237703041966}]}]"
1564008556893530022,reversal,paired_regression,iteration6,606,613,7,False,"[{""index"": 613, ""last_signal"": 610, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.052406149088733756, ""threshold"": 0.04692237703041966}]}]"
1564008556893530022,reversal,paired_regression,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.024490399442385492, ""threshold"": 0.01706337763346477, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.022953208316379807, ""threshold"": 0.017062354508114826, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
1634635432866334191,reversal,paired_regression,iteration6,606,612,6,False,"[{""index"": 612, ""last_signal"": 609, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 4, ""value"": 0.04309254165374039, ""threshold"": 0.03317913098760164}, {""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 8, ""value"": 0.023872912241235944, ""threshold"": 0.02346118851520983}]}]"
1634635432866334191,reversal,paired_regression,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.023786640078661186, ""threshold"": 0.017062354508114826, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.024722636901506195, ""threshold"": 0.01706133643749677, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
5015368413594993126,reversal,paired_regression,iteration6,606,611,5,False,"[{""index"": 611, ""last_signal"": 608, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.05027436122000256, ""threshold"": 0.04692237703041966}]}]"
5015368413594993126,reversal,paired_regression,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.02213517899573353, ""threshold"": 0.017067521442752503, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.023413777877967182, ""threshold"": 0.01706133643749677, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
3584306075979195116,reversal,paired_regression,iteration6,606,612,6,False,"[{""index"": 612, ""last_signal"": 609, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 4, ""value"": 0.044458824009818876, ""threshold"": 0.03317913098760164}]}]"
3584306075979195116,reversal,paired_regression,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.025065602999812024, ""threshold"": 0.017062354508114826, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.022543543419335565, ""threshold"": 0.017062354508114826, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
1564008556893530022,learnable,paired_regression,iteration6,,,,False,[]
1564008556893530022,learnable,paired_regression,iteration5,,,,False,[]
1634635432866334191,learnable,paired_regression,iteration6,,,,False,[]
1634635432866334191,learnable,paired_regression,iteration5,,,,False,[]
2098214662956861329,learnable,final,iteration6,,,,False,[]
2098214662956861329,learnable,final,iteration5,,,,False,[]
2098214662956861329,null,final,iteration6,,,,False,[]
2098214662956861329,null,final,iteration5,,,,False,[]
2098214662956861329,outer_noise,final,iteration6,,,,False,[]
2098214662956861329,outer_noise,final,iteration5,,,,False,[]
2098214662956861329,reversal,final,iteration6,606,611,5,False,"[{""index"": 611, ""last_signal"": 608, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.04764179111708946, ""threshold"": 0.04692237703041966}, {""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 4, ""value"": 0.03489331344990517, ""threshold"": 0.03317913098760164}]}]"
2098214662956861329,reversal,final,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.02465466809538363, ""threshold"": 0.01706337763346477, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.0239434842311612, ""threshold"": 0.01706337763346477, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
2098214662956861329,random_reversal,final,iteration6,658,662,4,False,"[{""index"": 662, ""last_signal"": 659, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.048864062325174984, ""threshold"": 0.04692237703041966}]}]"
2098214662956861329,random_reversal,final,iteration5,658,676,18,False,"[{""index"": 676, ""cell"": 4, ""delta"": -0.019973062048084342, ""threshold"": 0.01706337763346477, ""last_signal"": 673, ""reason"": ""CELL_RETURN_DRIFT""}]"
2928371724749768812,learnable,final,iteration6,,,,False,[]
2928371724749768812,learnable,final,iteration5,,,,False,[]
2928371724749768812,null,final,iteration6,,,,False,[]
2928371724749768812,null,final,iteration5,,,,False,[]
2928371724749768812,outer_noise,final,iteration6,,,,False,[]
2928371724749768812,outer_noise,final,iteration5,,,,False,[]
2928371724749768812,reversal,final,iteration6,606,611,5,False,"[{""index"": 611, ""last_signal"": 608, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 4, ""value"": 0.037827217366968056, ""threshold"": 0.03317913098760164}]}]"
2928371724749768812,reversal,final,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.023466275262102015, ""threshold"": 0.017062354508114826, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.023612056097011093, ""threshold"": 0.017062354508114826, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
2928371724749768812,random_reversal,final,iteration6,646,650,4,False,"[{""index"": 650, ""last_signal"": 647, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.055040178262618054, ""threshold"": 0.04692237703041966}]}]"
2928371724749768812,random_reversal,final,iteration5,646,664,18,False,"[{""index"": 664, ""cell"": 0, ""delta"": 0.020426986812477975, ""threshold"": 0.017062354508114826, ""last_signal"": 661, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 664, ""cell"": 4, ""delta"": -0.021199408871530184, ""threshold"": 0.017062354508114826, ""last_signal"": 661, ""reason"": ""CELL_RETURN_DRIFT""}]"
5618266449171873643,learnable,final,iteration6,,,,False,[]
5618266449171873643,learnable,final,iteration5,,,,False,[]
5618266449171873643,null,final,iteration6,,,,False,[]
5618266449171873643,null,final,iteration5,,,,False,[]
5618266449171873643,outer_noise,final,iteration6,,,,False,[]
5618266449171873643,outer_noise,final,iteration5,,,,False,[]
5618266449171873643,reversal,final,iteration6,606,611,5,False,"[{""index"": 611, ""last_signal"": 608, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.04877671662522916, ""threshold"": 0.04692237703041966}]}]"
5618266449171873643,reversal,final,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.023772152271162604, ""threshold"": 0.01748470413692342, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.022542732940539587, ""threshold"": 0.01706337763346477, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
5618266449171873643,random_reversal,final,iteration6,634,638,4,False,"[{""index"": 638, ""last_signal"": 635, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.04835710147216621, ""threshold"": 0.04692237703041966}]}]"
5618266449171873643,random_reversal,final,iteration5,634,652,18,False,"[{""index"": 652, ""cell"": 0, ""delta"": 0.018881536132618837, ""threshold"": 0.017062354508114826, ""last_signal"": 649, ""reason"": ""CELL_RETURN_DRIFT""}]"
8582935296371253491,learnable,final,iteration6,,,,False,[]
8582935296371253491,learnable,final,iteration5,,,,False,[]
8582935296371253491,null,final,iteration6,,,,False,[]
8582935296371253491,null,final,iteration5,,,,False,[]
8582935296371253491,outer_noise,final,iteration6,,,,False,[]
8582935296371253491,outer_noise,final,iteration5,,,,False,[]
8582935296371253491,reversal,final,iteration6,606,610,4,False,"[{""index"": 610, ""last_signal"": 607, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 2, ""value"": 0.04803198523726011, ""threshold"": 0.04692237703041966}]}]"
8582935296371253491,reversal,final,iteration5,606,628,22,False,"[{""index"": 628, ""cell"": 0, ""delta"": 0.023950249874225102, ""threshold"": 0.01706337763346477, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}, {""index"": 628, ""cell"": 4, ""delta"": -0.023039019232057315, ""threshold"": 0.01706133643749677, ""last_signal"": 625, ""reason"": ""CELL_RETURN_DRIFT""}]"
8582935296371253491,random_reversal,final,iteration6,676,683,7,False,"[{""index"": 683, ""last_signal"": 680, ""evidence"": [{""channel"": ""CROSS_SECTIONAL_RESIDUAL"", ""window"": 4, ""value"": 0.04449225292099386, ""threshold"": 0.03317913098760164}]}]"
8582935296371253491,random_reversal,final,iteration5,676,692,16,False,"[{""index"": 692, ""cell"": 4, ""delta"": -0.017222526177696436, ""threshold"": 0.01706133643749677, ""last_signal"": 689, ""reason"": ""CELL_RETURN_DRIFT""}]"

```


## discrimination_iteration6/economic_paired.csv

```
seed,scenario,phase,total_return_delta,adverse_return_delta,adverse_mdd_delta,mdd_delta,costs_delta,trades_delta
1564008556893530022,reversal,paired_regression,0.06729850125967884,0.06729850125967884,-0.06729850125967884,-0.06729850125967884,-2082.219975070305,-87
1634635432866334191,reversal,paired_regression,0.08420225874817777,0.08420225874817777,-0.08420225874817777,-0.08420225874817777,-2227.1345781945824,-90
5015368413594993126,reversal,paired_regression,0.07532090811477277,0.07532090811477277,-0.07532090811477277,-0.07532090811477277,-2335.983253518578,-94
3584306075979195116,reversal,paired_regression,0.07255089302054374,0.07255089302054374,-0.07255089302054374,-0.07255089302054374,-2226.1239347909104,-91
1564008556893530022,learnable,paired_regression,0.0,0.0,0.0,0.0,0.0,0
1634635432866334191,learnable,paired_regression,0.0,0.0,0.0,0.0,0.0,0
2098214662956861329,learnable,final,0.0,0.0,0.0,0.0,0.0,0
2098214662956861329,null,final,0.0,0.0,0.0,0.0,0.0,0
2098214662956861329,outer_noise,final,0.0,0.0,0.0,0.0,0.0,0
2098214662956861329,reversal,final,0.08315979061667411,0.08315979061667411,-0.08315979061667411,-0.08315979061667411,-2309.2612989670242,-95
2098214662956861329,random_reversal,final,0.08836824786874242,0.06904073579716452,-0.06874655583728262,-0.06874655583728262,-2519.2731359787213,-81
2928371724749768812,learnable,final,0.0,0.0,0.0,0.0,0.0,0
2928371724749768812,null,final,0.0,0.0,0.0,0.0,0.0,0
2928371724749768812,outer_noise,final,0.0,0.0,0.0,0.0,0.0,0
2928371724749768812,reversal,final,0.07820506217200984,0.07820506217200984,-0.07820506217200984,-0.07820506217200984,-2268.47239525739,-97
2928371724749768812,random_reversal,final,0.08056166449007951,0.06903470144844814,-0.06851391770893234,-0.06851391770893234,-2287.2249738660576,-78
5618266449171873643,learnable,final,0.0,0.0,0.0,0.0,0.0,0
5618266449171873643,null,final,0.0,0.0,0.0,0.0,0.0,0
5618266449171873643,outer_noise,final,0.0,0.0,0.0,0.0,0.0,0
5618266449171873643,reversal,final,0.0717748437206227,0.0717748437206227,-0.0717748437206227,-0.0717748437206227,-2374.8643130143723,-96
5618266449171873643,random_reversal,final,0.053123931299992266,0.046817310866702155,-0.046576030078744446,-0.046576030078744446,-2263.613964357947,-80
8582935296371253491,learnable,final,0.0,0.0,0.0,0.0,0.0,0
8582935296371253491,null,final,0.0,0.0,0.0,0.0,0.0,0
8582935296371253491,outer_noise,final,0.0,0.0,0.0,0.0,0.0,0
8582935296371253491,reversal,final,0.08934221686638344,0.08934221686638344,-0.08934221686638344,-0.08934221686638344,-2543.967589171173,-107
8582935296371253491,random_reversal,final,0.0558855201720827,0.041148012916779164,-0.04103484524299883,-0.04103484524299883,-1680.157806419813,-50

```


## discrimination_iteration6/engine.py

```
"""Independent iteration6; inherited DGP, classifier and horizon accounting."""
import copy,csv,gzip,hashlib,importlib.util,json,math,random,secrets,statistics as st,time
from pathlib import Path
O=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('iteration5_reference',O.parent/'discrimination_iteration5/experiment.py')
e=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(e)
START=e.START;END=e.END;COST=e.COST;mean=e.mean

def generate(seed,scenario,change=None):
    # Identical RNG, noise, prices, sensor noise and class law. Only switch time varies.
    p,f,t=e.generate(seed,'learnable' if scenario=='random_reversal' else scenario)
    if scenario=='random_reversal':
        for i in range(change,e.N):f[i]=[4-c for c in f[i]]
    return p,f,t

class Gate:
    """PIT safety latch; no truth, switch time, seed or scenario is supplied."""
    def __init__(self,p,f,models):
        self.p=p;self.f=f;self.models=models;self.latched=False;self.events=[];self.trace=[]
    def contrast(self,d):
        groups=[]
        for c in [0,4]:
            vals=[e.observed(self.p,d,j)-self.models[c]['mean'] for j in range(24) if self.f[d][j]==c]
            if len(vals)<2:return None
            groups.append(mean(vals))
        return groups[1]-groups[0]
    def __call__(self,now,row,trades):
        # All scan endpoints require signal+3 <= now; no scheduled-change indicator.
        signals=[]
        for w in [2,4,8]:
            ds=list(range(now-2-w,now-2))
            contrasts=[self.contrast(d) for d in ds]
            if all(v is not None for v in contrasts):
                value=-mean(contrasts)
                # Conservative fixed date-contrast envelope, max126*3 looks.
                threshold=.014*math.sqrt(2*math.log(2*126*3/.01)/w)
                if value>threshold:signals.append(dict(channel='CROSS_SECTIONAL_RESIDUAL',window=w,value=value,threshold=threshold))
        # Actual funded fills only, grouped by signal date to avoid pseudo replication.
        mature=[t for t in trades if t['signal']+3<=now and t['signal']>=now-10]
        errors=[]
        for d in sorted(set(t['signal'] for t in mature)):
            ts=[t for t in mature if t['signal']==d]
            errors.append(sum(t['debit']*(t['net']-self.models[self.f[d][t['j']]]['mean']) for t in ts)/sum(t['debit'] for t in ts))
        if len(errors)>=3:
            threshold=.018*math.sqrt(2*math.log(2*126/.01)/len(errors))
            if -mean(errors)>threshold:signals.append(dict(channel='MATURED_FUNDED_SURPRISE',window=len(errors),value=-mean(errors),threshold=threshold))
        if signals and not self.latched:
            self.events.append(dict(index=now,last_signal=now-3,evidence=signals));self.latched=True
        self.trace.append(dict(index=now,matured_fills=len(mature),funded_error=mean(errors) if errors else None,alarm=bool(signals),latched=self.latched))
        # Full abstention is conservative under detected drift. Recovery needs new disjoint evidence,
        # not a countdown or fitted reversal sign; no automatic re-entry in this bounded horizon.
        if self.latched:return [dict(z,label='UNKNOWN',reason='RAPID_DRIFT_ABSTAIN') for z in row]
        return row

def replay(prices,states,policy='tier',scale=1.,gate=None):
    cash=100000.;nav=cash;peak=nav;mdd=0.;costs=0.;risks=[];trades=[];daily=[];gap_exceed=0
    # All trades hold exactly one open-to-open session. Prior sales settle one session later.
    receivable=0.;positions=[]
    for k,i in enumerate(range(START,END)):
        opening=nav;cash+=receivable;receivable=0.;pnl=0.;exit_value=0.
        for t in positions:
            exitp=prices[i+1][t['j']]; proceeds=t['shares']*exitp*(1-COST/2)
            exit_value+=proceeds;costs+=t['shares']*exitp*COST/2
            t.update(exit_index=i+1,exit_open=exitp,net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav'])
            gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        receivable=exit_value;positions=[]
        opening=cash+receivable
        available=cash
        if gate is not None: states[k]=gate(i,states[k],trades)
        order=sorted(range(24),key=lambda j:states[k][j]['mean'],reverse=True)
        for j in order:
            c=states[k][j]
            if policy=='cash' or (policy=='tier' and c['label'] not in ('GOOD','GREAT')):continue
            gap=[.03,.06,.12,.24][j%4];weight=min(.10*scale,.02/(gap+COST)); debit=min(available,opening*weight)
            if debit<=1e-8:continue
            entry=prices[i+1][j];shares=debit/(entry*(1+COST/2));risk=shares*entry/opening*(gap+COST)
            assert risk<=.02+1e-12
            costs+=shares*entry*COST/2;available-=debit
            positions.append(dict(signal=i,j=j,entry_index=i+1,entry_open=entry,shares=shares,debit=debit,entry_nav=opening,modeled_risk=risk,tier=c['label']))
        cash=available;nav=cash+receivable+sum(t['shares']*prices[i+1][t['j']] for t in positions)
        assert cash>=-1e-8
        peak=max(peak,nav);mdd=max(mdd,1-nav/peak);daily.append(dict(index=i,nav=nav,cash=cash,receivable=receivable,exposure=sum(t['shares']*prices[i+1][t['j']] for t in positions)/nav))
    # Explicit final horizon liquidation; settle for ending NAV.
    for t in positions:
        proceeds=t['shares']*prices[END+1][t['j']]*(1-COST/2);costs+=t['shares']*prices[END+1][t['j']]*COST/2
        t.update(exit_index=END+1,exit_open=prices[END+1][t['j']],net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav']);gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        cash+=proceeds
    nav=cash+receivable;peak=max(peak,nav);mdd=max(mdd,1-nav/peak)
    return dict(total_return=nav/100000-1,cagr=(nav/100000)**(252/126)-1,mdd=mdd,costs=costs,final_nav=nav,max_modeled_risk=max((t['modeled_risk'] for t in trades),default=0),gap_loss_exceedances=gap_exceed,max_realized_trade_loss_nav=max((t['realized_loss_nav'] for t in trades),default=0),trades=len(trades),mean_exposure=mean([d['exposure'] for d in daily])),trades,daily

```


## discrimination_iteration6/iteration5_diagnosis.json

```
{
  "rows": [
    {
      "seed": 1564008556893530022,
      "first": 606,
      "last": 627,
      "unavoidable_first3": 13,
      "count": 108,
      "funded": 98,
      "funded_pnl": -8376.142758054018,
      "earliest_original_window_threshold_crossing_without_scan_schedule": 623,
      "post_first_information": 95
    },
    {
      "seed": 1634635432866334191,
      "first": 606,
      "last": 627,
      "unavoidable_first3": 15,
      "count": 120,
      "funded": 93,
      "funded_pnl": -9873.711183342166,
      "earliest_original_window_threshold_crossing_without_scan_schedule": 621,
      "post_first_information": 105
    },
    {
      "seed": 5015368413594993126,
      "first": 606,
      "last": 627,
      "unavoidable_first3": 9,
      "count": 105,
      "funded": 99,
      "funded_pnl": -9163.047269291692,
      "earliest_original_window_threshold_crossing_without_scan_schedule": 623,
      "post_first_information": 96
    },
    {
      "seed": 3584306075979195116,
      "first": 606,
      "last": 627,
      "unavoidable_first3": 12,
      "count": 109,
      "funded": 93,
      "funded_pnl": -9140.929660953743,
      "earliest_original_window_threshold_crossing_without_scan_schedule": 623,
      "post_first_information": 97
    }
  ],
  "first_eligible_outcome": 609,
  "first_allowed_scan": 628,
  "hard_min_delay": 3,
  "explanation": "Sensor marginal and complete price paths identical under reversal. Earliest post-switch outcome signal606 available609. First scan628 uses signals606..625; 19 extra sessions are hard-coded. Frozen means and sensor/full agreement cannot detect reversed sign.",
  "qualification": "First3 counts quantify an information lower bound for these tapes. Later counts are potentially avoidable exposure, not a guarantee of error-free detection at session609. Original20-date window itself needs accumulation; threshold crossings below isolate scheduling from window/threshold delay."
}
```


## discrimination_iteration6/paired.csv

```
seed,scenario,phase,false_great_delta
1564008556893530022,reversal,paired_regression,-72
1634635432866334191,reversal,paired_regression,-87
5015368413594993126,reversal,paired_regression,-86
3584306075979195116,reversal,paired_regression,-81
1564008556893530022,learnable,paired_regression,0
1634635432866334191,learnable,paired_regression,0
2098214662956861329,learnable,final,0
2098214662956861329,null,final,0
2098214662956861329,outer_noise,final,0
2098214662956861329,reversal,final,-85
2098214662956861329,random_reversal,final,-64
2928371724749768812,learnable,final,0
2928371724749768812,null,final,0
2928371724749768812,outer_noise,final,0
2928371724749768812,reversal,final,-72
2928371724749768812,random_reversal,final,-68
5618266449171873643,learnable,final,0
5618266449171873643,null,final,0
5618266449171873643,outer_noise,final,0
5618266449171873643,reversal,final,-58
5618266449171873643,random_reversal,final,-78
8582935296371253491,learnable,final,0
8582935296371253491,null,final,0
8582935296371253491,outer_noise,final,0
8582935296371253491,reversal,final,-92
8582935296371253491,random_reversal,final,-44

```


## discrimination_iteration6/portfolio.csv

```
seed,scenario,phase,variant,total_return,cagr,mdd,costs,final_nav,max_modeled_risk,gap_loss_exceedances,max_realized_trade_loss_nav,trades,mean_exposure,adverse_return,adverse_mdd
620101,learnable,design,iteration6,0.8940517219737703,2.587431925511804,0.0014977533699451762,25909.180274835708,189405.17219737702,0.019970044932601103,0,0.0016103690434886302,734,0.49776500385124006,0.8940517219737703,0.0014977533699451762
620101,reversal,design,iteration6,-0.06438946461736272,-0.12463292608101484,0.06438946461736272,1968.509367930332,93561.05353826373,0.019970044932601103,0,0.00266826044839728,76,0.053908282444780575,-0.06438946461736272,0.06438946461736272
620102,learnable,design,iteration6,0.9439214906614815,2.778830761855556,0.0011583046089330695,26774.44860376415,194392.14906614815,0.019970044932601103,0,0.001324531806452074,717,0.4979394944395119,0.9439214906614815,0.0011583046089330695
620102,reversal,design,iteration6,-0.01683181448207416,-0.0333803189853894,0.01683181448207416,595.7192056903581,98316.81855179259,0.0199700449326011,0,0.003429002258910077,22,0.015886556378336553,-0.01683181448207416,0.01683181448207416
1564008556893530022,reversal,paired_regression,iteration6,-0.026055375312072915,-0.0514318680414928,0.026055375312072915,1065.6311234215548,97394.46246879271,0.019970044932601103,0,0.0021303594754191204,42,0.028606940752759377,-0.026055375312072915,0.026055375312072915
1564008556893530022,reversal,paired_regression,iteration5,-0.09335387657175176,-0.1779928068725296,0.09335387657175176,3147.85109849186,90664.61234282482,0.019970044932601103,0,0.00328233948439627,129,0.08740442927292283,-0.09335387657175176,0.09335387657175176
1634635432866334191,reversal,paired_regression,iteration6,-0.03188680721311221,-0.06275684595197828,0.03188680721311221,888.102638488901,96811.31927868878,0.0199700449326011,0,0.0032217073400820483,35,0.023828573969865784,-0.03188680721311221,0.03188680721311221
1634635432866334191,reversal,paired_regression,iteration5,-0.11608906596128998,-0.21870146068681517,0.11608906596128998,3115.2372166834834,88391.093403871,0.0199700449326011,0,0.0032217073400820483,125,0.0874371708236961,-0.11608906596128998,0.11608906596128998
5015368413594993126,reversal,paired_regression,iteration6,-0.024002278229581453,-0.047428447098952664,0.024002278229581453,705.6349386080876,97599.77217704186,0.0199700449326011,0,0.0023171847217666095,27,0.018933714115878228,-0.024002278229581453,0.024002278229581453
5015368413594993126,reversal,paired_regression,iteration5,-0.09932318634435422,-0.18878127734311312,0.09932318634435422,3041.6181921266652,90067.68136556458,0.019970044932601103,0,0.0030038860486007236,121,0.0849147521816611,-0.09932318634435422,0.09932318634435422
3584306075979195116,reversal,paired_regression,iteration6,-0.031073516723354233,-0.06118147000515184,0.031073516723354233,886.0395496830652,96892.64832766457,0.019970044932601103,0,0.002671397402377856,33,0.02383063953301846,-0.031073516723354233,0.031073516723354233
3584306075979195116,reversal,paired_regression,iteration5,-0.10362440974389797,-0.19651080119302466,0.10362440974389797,3112.1634844739756,89637.5590256102,0.019970044932601103,0,0.002923011157214521,124,0.08745282346965874,-0.10362440974389797,0.10362440974389797
1564008556893530022,learnable,paired_regression,iteration6,0.8565803518951918,2.446890603043274,0.001963545471879824,26390.734316483435,185658.03518951917,0.019970044932601103,0,0.0018333001423728027,713,0.49860300716718614,0.8565803518951918,0.001963545471879824
1564008556893530022,learnable,paired_regression,iteration5,0.8565803518951918,2.446890603043274,0.001963545471879824,26390.734316483435,185658.03518951917,0.019970044932601103,0,0.0018333001423728027,713,0.49860300716718614,0.8565803518951918,0.001963545471879824
1634635432866334191,learnable,paired_regression,iteration6,0.8532868241113967,2.434672052424907,0.003995693570929326,26113.89853369401,185328.68241113966,0.019970044932601103,0,0.0017168536902495927,711,0.49857151938894406,0.8532868241113967,0.003995693570929326
1634635432866334191,learnable,paired_regression,iteration5,0.8532868241113967,2.434672052424907,0.003995693570929326,26113.89853369401,185328.68241113966,0.019970044932601103,0,0.0017168536902495927,711,0.49857151938894406,0.8532868241113967,0.003995693570929326
2098214662956861329,learnable,final,iteration6,0.81631118785166,2.298986331115108,0.0014977533699451762,25718.576468907453,181631.118785166,0.019970044932601103,0,0.0016926044265318239,722,0.4986810633488832,0.81631118785166,0.0014977533699451762
2098214662956861329,learnable,final,iteration5,0.81631118785166,2.298986331115108,0.0014977533699451762,25718.576468907453,181631.118785166,0.019970044932601103,0,0.0016926044265318239,722,0.4986810633488832,0.81631118785166,0.0014977533699451762
2098214662956861329,null,final,iteration6,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
2098214662956861329,null,final,iteration5,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
2098214662956861329,outer_noise,final,iteration6,0.8651721717471816,2.4788672302600983,0.001803312905802934,21989.132204031932,186517.21717471816,0.019970044932601103,0,0.0019533583169471787,559,0.4147968461458722,0.8651721717471816,0.001803312905802934
2098214662956861329,outer_noise,final,iteration5,0.8651721717471816,2.4788672302600983,0.001803312905802934,21989.132204031932,186517.21717471816,0.019970044932601103,0,0.0019533583169471787,559,0.4147968461458722,0.8651721717471816,0.001803312905802934
2098214662956861329,reversal,final,iteration6,-0.024393305489778028,-0.048191577626838455,0.024393305489778028,817.5013942304197,97560.6694510222,0.019970044932601103,0,0.002349879220985422,30,0.021945710661287237,-0.024393305489778028,0.024393305489778028
2098214662956861329,reversal,final,iteration5,-0.10755309610645214,-0.2035385237308206,0.10755309610645214,3126.7626931974437,89244.69038935479,0.019970044932601103,0,0.0031670474165727863,125,0.087422703794017,-0.10755309610645214,0.10755309610645214
2098214662956861329,random_reversal,final,iteration6,0.24793849545334878,0.5573504884343679,0.029159505497852733,9628.875577594667,124793.84954533487,0.019970044932601103,0,0.0026124641861204317,315,0.22181358554367403,-0.0250050891166117,0.029159505497852733
2098214662956861329,random_reversal,final,iteration5,0.15957024758460636,0.3446031590834253,0.09790606133513535,12148.148713573388,115957.02475846064,0.019970044932601103,1,0.0033369846230726394,396,0.277458064516062,-0.09404582491377622,0.09790606133513535
2928371724749768812,learnable,final,iteration6,0.8504453823643263,2.424148113113458,0.002473713338672412,25733.33599489699,185044.53823643262,0.019970044932601103,0,0.0015337588484140284,717,0.49705171792761027,0.8504453823643263,0.002473713338672412
2928371724749768812,learnable,final,iteration5,0.8504453823643263,2.424148113113458,0.002473713338672412,25733.33599489699,185044.53823643262,0.019970044932601103,0,0.0015337588484140284,717,0.49705171792761027,0.8504453823643263,0.002473713338672412
2928371724749768812,null,final,iteration6,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
2928371724749768812,null,final,iteration5,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
2928371724749768812,outer_noise,final,iteration6,0.8547208848906116,2.4399895608494133,0.004324185048012019,25858.06598751037,185472.08848906116,0.019970044932601103,0,0.0022171985605175457,716,0.49704676274094073,0.8547208848906116,0.004324185048012019
2928371724749768812,outer_noise,final,iteration5,0.8547208848906116,2.4399895608494133,0.004324185048012019,25858.06598751037,185472.08848906116,0.019970044932601103,0,0.0022171985605175457,716,0.49704676274094073,0.8547208848906116,0.004324185048012019
2928371724749768812,reversal,final,iteration6,-0.03575999687358267,-0.07024121637076675,0.03575999687358267,841.4668434742601,96424.00031264173,0.019970044932601103,0,0.003210813216924959,31,0.02259300911462267,-0.03575999687358267,0.03575999687358267
2928371724749768812,reversal,final,iteration5,-0.11396505904559251,-0.21494208340791965,0.11396505904559251,3109.93923873165,88603.49409544075,0.019970044932601103,0,0.003210813216924959,128,0.08741276223106023,-0.11396505904559251,0.11396505904559251
2928371724749768812,random_reversal,final,iteration6,0.13925442671961563,0.29790064880024003,0.031117535420133735,7207.941005554794,113925.44267196156,0.019970044932601103,0,0.0034037312633723883,244,0.1742909564264474,-0.023752926156381138,0.031117535420133735
2928371724749768812,random_reversal,final,iteration5,0.05869276222953612,0.1208303647972051,0.09963145312906607,9495.165979420852,105869.2762229536,0.019970044932601103,0,0.0034037312633723883,322,0.22938691321045607,-0.09278762760482928,0.09963145312906607
5618266449171873643,learnable,final,iteration6,0.874409602355974,2.5134113574042805,0.0008456451125780085,26199.97576841569,187440.9602355974,0.019970044932601103,0,0.0012888158575118408,718,0.49790802615549573,0.874409602355974,0.0008456451125780085
5618266449171873643,learnable,final,iteration5,0.874409602355974,2.5134113574042805,0.0008456451125780085,26199.97576841569,187440.9602355974,0.019970044932601103,0,0.0012888158575118408,718,0.49790802615549573,0.874409602355974,0.0008456451125780085
5618266449171873643,null,final,iteration6,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
5618266449171873643,null,final,iteration5,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
5618266449171873643,outer_noise,final,iteration6,0.8744341121501213,2.5135032407920135,0.0020469272718128817,26126.36033463142,187443.41121501214,0.019970044932601103,0,0.0018822853202226592,720,0.4978893403936581,0.8744341121501213,0.0020469272718128817
5618266449171873643,outer_noise,final,iteration5,0.8744341121501213,2.5135032407920135,0.0020469272718128817,26126.36033463142,187443.41121501214,0.019970044932601103,0,0.0018822853202226592,720,0.4978893403936581,0.8744341121501213,0.0020469272718128817
5618266449171873643,reversal,final,iteration6,-0.016336906927685635,-0.03240691932740736,0.016336906927685635,793.9423304585371,98366.30930723144,0.0199700449326011,0,0.002548161607520415,29,0.021162084933629272,-0.016336906927685635,0.016336906927685635
5618266449171873643,reversal,final,iteration5,-0.08811175064830834,-0.16845982069430698,0.08811175064830834,3168.8066434729094,91188.82493516916,0.0199700449326011,0,0.0027077403368593505,125,0.08738490701128236,-0.08811175064830834,0.08811175064830834
5618266449171873643,random_reversal,final,iteration6,0.10853163460753401,0.22884238492565134,0.028102749678697858,5177.5337334307105,110853.16346075339,0.019970044932601103,0,0.002684587524622102,184,0.12665354190170924,-0.023067968183259402,0.028102749678697858
5618266449171873643,random_reversal,final,iteration5,0.055407703307541745,0.11388542020090009,0.0746787797574423,7441.147697788658,105540.77033075417,0.019970044932601103,0,0.002684587524622102,264,0.1822714431439817,-0.06988527904996156,0.0746787797574423
8582935296371253491,learnable,final,iteration6,0.8204923601488163,2.3141924333602075,0.001092188877178324,25456.607087425324,182049.23601488164,0.019970044932601103,0,0.00194740584562284,710,0.49819613772205956,0.8204923601488163,0.001092188877178324
8582935296371253491,learnable,final,iteration5,0.8204923601488163,2.3141924333602075,0.001092188877178324,25456.607087425324,182049.23601488164,0.019970044932601103,0,0.00194740584562284,710,0.49819613772205956,0.8204923601488163,0.001092188877178324
8582935296371253491,null,final,iteration6,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
8582935296371253491,null,final,iteration5,0.0,0.0,0.0,0.0,100000.0,0,0,0,0,0.0,0.0,0.0
8582935296371253491,outer_noise,final,iteration6,0.8187634499350103,2.3079004868195008,0.0024892167442193136,25322.77378377802,181876.34499350103,0.019970044932601103,0,0.0027342573070285488,733,0.4955742932131512,0.8187634499350103,0.0024892167442193136
8582935296371253491,outer_noise,final,iteration5,0.8187634499350103,2.3079004868195008,0.0024892167442193136,25322.77378377802,181876.34499350103,0.019970044932601103,0,0.0027342573070285488,733,0.4955742932131512,0.8187634499350103,0.0024892167442193136
8582935296371253491,reversal,final,iteration6,-0.013088688584461106,-0.026006063400061175,0.013088688584461106,595.9687531458937,98691.1311415539,0.0199700449326011,0,0.0020456929777978947,22,0.015879804590185658,-0.013088688584461106,0.013088688584461106
8582935296371253491,reversal,final,iteration5,-0.10243090545084454,-0.1943697205102093,0.10243090545084454,3139.9363423170666,89756.90945491554,0.019970044932601103,0,0.003532373518231643,129,0.08740311188381342,-0.10243090545084454,0.10243090545084454
8582935296371253491,random_reversal,final,iteration6,0.314095253454145,0.7268463351507137,0.03510434914073657,13850.403311740392,131409.5253454145,0.019970044932601103,0,0.0023173693996002007,429,0.3060695457438013,-0.03244331811693324,0.03510434914073657
8582935296371253491,random_reversal,final,iteration5,0.2582097332820623,0.5830917329257184,0.0761391943837354,15530.561118160205,125820.97332820624,0.019970044932601103,0,0.002991422724634421,479,0.34067214764215786,-0.0735913310337124,0.0761391943837354

```


## discrimination_iteration6/preregister.json

```
{
  "purpose": "Independent bounded reversal safety fix preserving iteration5 classifier; no GA, production, band or noise changes",
  "max_portfolio_replays": 64,
  "max_seconds": 720,
  "planned_replays": 59,
  "accounting": "3 tests + 4 fixed design probes + 12 paired regression + 40 final. No outcome-driven reruns or search.",
  "design_seeds": [620101, 620102],
  "final_seeds": "4 OS entropy seeds after local code/dependency/preregistration hash freeze",
  "final_scenarios": ["learnable", "null", "outer_noise", "reversal", "random_reversal"],
  "random_switch": "OS entropy uniform606+20..606+80, evaluator-only. Same switch applied to both candidates; random seed and switch never enter gate.",
  "dgp": "Unchanged iteration5 generation for original scenarios; random_reversal changes ONLY sensor mapping switch time on exact learnable tape. Prices remain bit identical. No new sensor, sector label, oracle indicator, or noise reduction.",
  "classifier": "Iteration5 unchanged fit/calibration/bands and stable gate. Safety latch may only replace label with UNKNOWN. No retraining or class forcing.",
  "channels": "Cross-sectional cell4-cell0 forecast residual contrast with at least2 members per extreme cell per date; windows2,4,8; fixed envelope .014 times sqrt(2log(2*126*3/.01)/w). Actual funded-fill date-grouped weighted forecast surprise, at least3 mature dates in10-session span; fixed .018 envelope times sqrt(2log(2*126/.01)/n). Each channel alpha .01; envelope a synthetic conservative engineering assumption, not real-market certification. All signals+3<=now. Monitor pretest dates too, no forced test-start warmup.",
  "other_channels": "Market breadth and independent sector breadth cannot reveal sensor remapping: prices and unconditional returns identical. No sector membership or sector shocks in DGP. Price-only veto rejected. Sensor-conditioned residual trend is informative and used in contrast. Funded surprise may corroborate or fire separately; ablations limited to trace evidence, not optimized.",
  "risk": "Detected drift => full pre-entry abstention, no automatic re-entry. Existing one-session fills exit normally. Per-trade modeled loss <=2%, prescribed gaps 3/6/12/24%, 30bp costs, cash settlement and liquidation unchanged.",
  "metrics_and_pass": {
    "stable_coverage": ">=15% each fresh learnable and outer_noise seed",
    "stable_extreme_errors": "false GREAT on TERRIBLE and false TERRIBLE on GREAT each <=1% conditional on true tier",
    "five_tier_support": ">=20 inferred opportunities in each tier per fresh learnable seed",
    "null": "100% abstention, zero costs and return",
    "false_alarms": "zero observed among stable fresh scenarios; <=5% population rate cannot be certified with4 seeds",
    "detection": "first switch alarm delay3..8 sessions on all8 fresh reversal episodes; first detection and evidence timestamps recorded for both versions",
    "false_great": "strictly fewer on every paired reversal tape vs iteration5; report absolute counts and unavoidable first3 sessions separately",
    "economics": "adverse segment return >=-5% and MDD<=5% for each fresh reversal; paired return/MDD/cost/trades and stable opportunity costs reported. No return target on stable planted alpha",
    "accounting": "nonnegative cash, fees both legs, net reconciliation <1e-12, total PnL reconciliation<1e-6, one-session matched horizon, <=2% modeled trade risk; 50% gap test must exceed modeled risk"
  },
  "stop": "No repair after final outcomes. Any failed criterion => FAIL and precise blocker. Distinguish unavoidable information delay from preventable scan delay. Synthetic engineering only; no public timestamp, real PIT dataset or alpha claim."
}

```


## discrimination_iteration6/report.json

```json
{"status":"FAIL","checks":{"stable_coverage":true,"stable_extreme_errors":true,"five_tier_support":false,"null_abstention":true,"observed_false_alarm":true,"rapid_detection":true,"reversal_false_great_reduced":true,"adverse_loss_limit":true,"accounting":true,"frozen_hashes":true,"budget":true},"portfolio_replays":59,"elapsed_seconds":9.059752707136795,"tests":6,"diagnosis":{"rows":[{"seed":1564008556893530022,"first":606,"last":627,"unavoidable_first3":13,"count":108,"funded":98,"funded_pnl":-8376.142758054018,"earliest_original_window_threshold_crossing_without_scan_schedule":623,"post_first_information":95},{"seed":1634635432866334191,"first":606,"last":627,"unavoidable_first3":15,"count":120,"funded":93,"funded_pnl":-9873.711183342166,"earliest_original_window_threshold_crossing_without_scan_schedule":621,"post_first_information":105},{"seed":5015368413594993126,"first":606,"last":627,"unavoidable_first3":9,"count":105,"funded":99,"funded_pnl":-9163.047269291692,"earliest_original_window_threshold_crossing_without_scan_schedule":623,"post_first_information":96},{"seed":3584306075979195116,"first":606,"last":627,"unavoidable_first3":12,"count":109,"funded":93,"funded_pnl":-9140.929660953743,"earliest_original_window_threshold_crossing_without_scan_schedule":623,"post_first_information":97}],"first_eligible_outcome":609,"first_allowed_scan":628,"hard_min_delay":3,"explanation":"Sensor marginal and complete price paths identical under reversal. Earliest post-switch outcome signal606 available609. First scan628 uses signals606..625; 19 extra sessions are hard-coded. Frozen means and sensor/full agreement cannot detect reversed sign.","qualification":"First3 counts quantify an information lower bound for these tapes. Later counts are potentially avoidable exposure, not a guarantee of error-free detection at session609. Original20-date window itself needs accumulation; threshold crossings below isolate scheduling from window/threshold delay."},"discrimination":[{"seed":620101,"scenario":"learnable","variant":"iteration6","phase":"design","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[587,576,630,598,633],"recall":[0.9562289562289562,0.9491228070175438,0.9681528662420382,0.9534109816971714,0.9778129952456418],"confusion":[[568,26,0,0,0,0],[19,541,10,0,0,0],[0,9,608,11,0,0],[0,0,12,573,16,0],[0,0,0,14,617,0]]},{"seed":620101,"scenario":"reversal","variant":"iteration6","phase":"design","coverage":0.1111111111111111,"false_great":68,"false_great_rate":0.11447811447811448,"false_terrible":61,"false_terrible_rate":0.09667194928684628,"support":[62,71,79,56,68],"recall":[0.0,0.0,0.11624203821656051,0.0,0.0],"confusion":[[0,0,0,2,68,524],[0,0,1,54,0,515],[0,4,73,0,0,551],[1,65,5,0,0,530],[61,2,0,0,0,568]]},{"seed":620102,"scenario":"learnable","variant":"iteration6","phase":"design","coverage":0.9328703703703703,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[593,410,587,608,623],"recall":[0.9744027303754266,0.6260032102728732,0.9604810996563574,0.9535655058043118,0.9666666666666667],"confusion":[[571,11,0,0,0,4],[22,390,14,0,0,197],[0,9,559,12,0,2],[0,0,14,575,14,0],[0,0,0,21,609,0]]},{"seed":620102,"scenario":"reversal","variant":"iteration6","phase":"design","coverage":0.0291005291005291,"false_great":17,"false_great_rate":0.02901023890784983,"false_terrible":16,"false_terrible_rate":0.025396825396825397,"support":[16,10,28,17,17],"recall":[0.0,0.0,0.0429553264604811,0.0,0.0],"confusion":[[0,0,0,0,17,569],[0,0,1,16,0,606],[0,0,25,1,0,556],[0,9,2,0,0,592],[16,1,0,0,0,613]]},{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration6","phase":"paired_regression","coverage":0.05555555555555555,"false_great":36,"false_great_rate":0.05787781350482315,"false_terrible":31,"false_terrible_rate":0.05140961857379768,"support":[31,36,33,31,37],"recall":[0.0,0.0,0.05194805194805195,0.0,0.0],"confusion":[[0,0,0,0,36,586],[0,0,0,30,1,521],[0,2,32,1,0,581],[0,33,1,0,0,597],[31,1,0,0,0,571]]},{"seed":1564008556893530022,"scenario":"reversal","variant":"iteration5","phase":"paired_regression","coverage":0.1746031746031746,"false_great":108,"false_great_rate":0.17363344051446947,"false_terrible":98,"false_terrible_rate":0.1625207296849088,"support":[99,113,110,97,109],"recall":[0.0,0.0,0.17532467532467533,0.0,0.0],"confusion":[[0,0,0,0,108,514],[0,0,0,94,1,457],[0,4,108,3,0,501],[1,105,2,0,0,523],[98,4,0,0,0,501]]},{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration6","phase":"paired_regression","coverage":0.037698412698412696,"false_great":33,"false_great_rate":0.05631399317406143,"false_terrible":30,"false_terrible_rate":0.05181347150259067,"support":[30,0,28,23,33],"recall":[0.0,0.0,0.04376012965964344,0.0,0.0],"confusion":[[0,0,0,1,33,552],[0,0,0,21,0,571],[0,0,27,1,0,589],[0,0,1,0,0,649],[30,0,0,0,0,549]]},{"seed":1634635432866334191,"scenario":"reversal","variant":"iteration5","phase":"paired_regression","coverage":0.14186507936507936,"false_great":120,"false_great_rate":0.20477815699658702,"false_terrible":106,"false_terrible_rate":0.18307426597582038,"support":[107,0,115,83,124],"recall":[0.0,0.0,0.1766612641815235,0.0,0.0],"confusion":[[0,0,0,3,120,463],[0,0,0,78,4,510],[0,0,109,2,0,506],[1,0,6,0,0,643],[106,0,0,0,0,473]]},{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration6","phase":"paired_regression","coverage":0.03373015873015873,"false_great":19,"false_great_rate":0.030497592295345103,"false_terrible":23,"false_terrible_rate":0.04107142857142857,"support":[24,26,19,13,20],"recall":[0.0,0.0,0.030694668820678513,0.0,0.0],"confusion":[[0,0,0,0,19,604],[0,0,0,13,1,598],[0,0,19,0,0,600],[1,25,0,0,0,584],[23,1,0,0,0,536]]},{"seed":5015368413594993126,"scenario":"reversal","variant":"iteration5","phase":"paired_regression","coverage":0.15707671957671956,"false_great":105,"false_great_rate":0.16853932584269662,"false_terrible":98,"false_terrible_rate":0.175,"support":[100,109,118,41,107],"recall":[0.0,0.0,0.1841680129240711,0.0,0.0],"confusion":[[0,0,0,0,105,518],[0,0,1,40,2,569],[0,2,114,1,0,502],[2,104,3,0,0,501],[98,3,0,0,0,459]]},{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration6","phase":"paired_regression","coverage":0.03736772486772487,"false_great":28,"false_great_rate":0.04590163934426229,"false_terrible":28,"false_terrible_rate":0.047377326565143825,"support":[29,28,0,27,29],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,1,28,581],[0,0,0,25,1,603],[0,1,0,1,0,602],[1,26,0,0,0,563],[28,1,0,0,0,562]]},{"seed":3584306075979195116,"scenario":"reversal","variant":"iteration5","phase":"paired_regression","coverage":0.14285714285714285,"false_great":109,"false_great_rate":0.17868852459016393,"false_terrible":108,"false_terrible_rate":0.18274111675126903,"support":[112,98,0,110,112],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,4,109,497],[0,0,0,103,3,523],[0,3,0,3,0,598],[4,93,0,0,0,493],[108,2,0,0,0,481]]},{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration6","phase":"paired_regression","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[625,547,615,629,608],"recall":[0.9823151125401929,0.9402173913043478,0.935064935064935,0.9318541996830428,0.9701492537313433],"confusion":[[611,11,0,0,0,0],[14,519,19,0,0,0],[0,17,576,23,0,0],[0,0,20,588,23,0],[0,0,0,18,585,0]]},{"seed":1564008556893530022,"scenario":"learnable","variant":"iteration5","phase":"paired_regression","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[625,547,615,629,608],"recall":[0.9823151125401929,0.9402173913043478,0.935064935064935,0.9318541996830428,0.9701492537313433],"confusion":[[611,11,0,0,0,0],[14,519,19,0,0,0],[0,17,576,23,0,0],[0,0,20,588,23,0],[0,0,0,18,585,0]]},{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration6","phase":"paired_regression","coverage":0.8062169312169312,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[590,0,623,634,591],"recall":[0.9726962457337884,0.0,0.9643435980551054,0.9338461538461539,0.9792746113989638],"confusion":[[570,0,0,0,0,16],[20,0,9,0,0,563],[0,0,595,15,0,7],[0,0,19,607,24,0],[0,0,0,12,567,0]]},{"seed":1634635432866334191,"scenario":"learnable","variant":"iteration5","phase":"paired_regression","coverage":0.8062169312169312,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[590,0,623,634,591],"recall":[0.9726962457337884,0.0,0.9643435980551054,0.9338461538461539,0.9792746113989638],"confusion":[[570,0,0,0,0,16],[20,0,9,0,0,563],[0,0,595,15,0,7],[0,0,19,607,24,0],[0,0,0,12,567,0]]},{"seed":2098214662956861329,"scenario":"learnable","variant":"iteration6","phase":"final","coverage":0.7628968253968254,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[590,518,0,614,585],"recall":[0.9730639730639731,0.7856,0.0,0.941747572815534,0.9659284497444633],"confusion":[[578,14,0,0,0,2],[12,491,0,0,0,122],[0,13,0,12,0,575],[0,0,0,582,18,18],[0,0,0,20,567,0]]},{"seed":2098214662956861329,"scenario":"learnable","variant":"iteration5","phase":"final","coverage":0.7628968253968254,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[590,518,0,614,585],"recall":[0.9730639730639731,0.7856,0.0,0.941747572815534,0.9659284497444633],"confusion":[[578,14,0,0,0,2],[12,491,0,0,0,122],[0,13,0,12,0,575],[0,0,0,582,18,18],[0,0,0,20,567,0]]},{"seed":2098214662956861329,"scenario":"null","variant":"iteration6","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,594],[0,0,0,0,0,625],[0,0,0,0,0,600],[0,0,0,0,0,618],[0,0,0,0,0,587]]},{"seed":2098214662956861329,"scenario":"null","variant":"iteration5","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,594],[0,0,0,0,0,625],[0,0,0,0,0,600],[0,0,0,0,0,618],[0,0,0,0,0,587]]},{"seed":2098214662956861329,"scenario":"outer_noise","variant":"iteration6","phase":"final","coverage":0.38855820105820105,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[590,0,0,0,585],"recall":[0.9730639730639731,0.0,0.0,0.0,0.9659284497444633],"confusion":[[578,0,0,0,0,16],[12,0,0,0,0,613],[0,0,0,0,0,600],[0,0,0,0,18,600],[0,0,0,0,567,20]]},{"seed":2098214662956861329,"scenario":"outer_noise","variant":"iteration5","phase":"final","coverage":0.38855820105820105,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[590,0,0,0,585],"recall":[0.9730639730639731,0.0,0.0,0.0,0.9659284497444633],"confusion":[[578,0,0,0,0,16],[12,0,0,0,0,613],[0,0,0,0,0,600],[0,0,0,0,18,600],[0,0,0,0,567,20]]},{"seed":2098214662956861329,"scenario":"reversal","variant":"iteration6","phase":"final","coverage":0.030753968253968252,"false_great":22,"false_great_rate":0.037037037037037035,"false_terrible":27,"false_terrible_rate":0.04599659284497445,"support":[28,20,0,23,22],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,1,22,571],[0,0,0,21,0,604],[0,0,0,1,0,599],[1,19,0,0,0,598],[27,1,0,0,0,559]]},{"seed":2098214662956861329,"scenario":"reversal","variant":"iteration5","phase":"final","coverage":0.1378968253968254,"false_great":107,"false_great_rate":0.18013468013468015,"false_terrible":108,"false_terrible_rate":0.1839863713798978,"support":[113,96,0,100,108],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,4,107,483],[0,0,0,94,1,530],[0,0,0,2,0,598],[5,93,0,0,0,520],[108,3,0,0,0,476]]},{"seed":2098214662956861329,"scenario":"random_reversal","variant":"iteration6","phase":"final","coverage":0.34424603174603174,"false_great":21,"false_great_rate":0.03535353535353535,"false_terrible":16,"false_terrible_rate":0.027257240204429302,"support":[260,211,0,293,277],"recall":[0.4006734006734007,0.3008,0.0,0.4255663430420712,0.4190800681431005],"confusion":[[238,4,0,0,21,331],[5,188,0,15,0,417],[0,6,0,5,0,589],[1,13,0,263,10,331],[16,0,0,10,246,315]]},{"seed":2098214662956861329,"scenario":"random_reversal","variant":"iteration5","phase":"final","coverage":0.4255952380952381,"false_great":85,"false_great_rate":0.14309764309764308,"false_terrible":80,"false_terrible_rate":0.1362862010221465,"support":[325,252,0,367,343],"recall":[0.4006734006734007,0.3008,0.0,0.4255663430420712,0.4190800681431005],"confusion":[[238,4,0,1,85,266],[5,188,0,87,2,343],[0,8,0,6,0,586],[2,51,0,263,10,292],[80,1,0,10,246,250]]},{"seed":2928371724749768812,"scenario":"learnable","variant":"iteration6","phase":"final","coverage":0.9821428571428571,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[586,569,596,605,614],"recall":[0.9730185497470489,0.9585585585585585,0.8597285067873304,0.9559322033898305,0.9662921348314607],"confusion":[[577,16,0,0,0,0],[9,532,13,0,0,1],[0,21,570,20,0,52],[0,0,13,564,12,1],[0,0,0,21,602,0]]},{"seed":2928371724749768812,"scenario":"learnable","variant":"iteration5","phase":"final","coverage":0.9821428571428571,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[586,569,596,605,614],"recall":[0.9730185497470489,0.9585585585585585,0.8597285067873304,0.9559322033898305,0.9662921348314607],"confusion":[[577,16,0,0,0,0],[9,532,13,0,0,1],[0,21,570,20,0,52],[0,0,13,564,12,1],[0,0,0,21,602,0]]},{"seed":2928371724749768812,"scenario":"null","variant":"iteration6","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,593],[0,0,0,0,0,555],[0,0,0,0,0,663],[0,0,0,0,0,590],[0,0,0,0,0,623]]},{"seed":2928371724749768812,"scenario":"null","variant":"iteration5","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,593],[0,0,0,0,0,555],[0,0,0,0,0,663],[0,0,0,0,0,590],[0,0,0,0,0,623]]},{"seed":2928371724749768812,"scenario":"outer_noise","variant":"iteration6","phase":"final","coverage":0.7837301587301587,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[586,565,0,605,614],"recall":[0.9730185497470489,0.9513513513513514,0.0,0.9559322033898305,0.9662921348314607],"confusion":[[577,16,0,0,0,0],[9,528,0,0,0,18],[0,21,0,20,0,622],[0,0,0,564,12,14],[0,0,0,21,602,0]]},{"seed":2928371724749768812,"scenario":"outer_noise","variant":"iteration5","phase":"final","coverage":0.7837301587301587,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[586,565,0,605,614],"recall":[0.9730185497470489,0.9513513513513514,0.0,0.9559322033898305,0.9662921348314607],"confusion":[[577,16,0,0,0,0],[9,528,0,0,0,18],[0,21,0,20,0,622],[0,0,0,564,12,14],[0,0,0,21,602,0]]},{"seed":2928371724749768812,"scenario":"reversal","variant":"iteration6","phase":"final","coverage":0.03902116402116402,"false_great":28,"false_great_rate":0.047217537942664416,"false_terrible":23,"false_terrible_rate":0.03691813804173355,"support":[23,22,27,18,28],"recall":[0.0,0.0,0.04072398190045249,0.0,0.0],"confusion":[[0,0,0,1,28,564],[0,0,0,17,0,538],[0,1,27,0,0,635],[0,20,0,0,0,570],[23,1,0,0,0,599]]},{"seed":2928371724749768812,"scenario":"reversal","variant":"iteration5","phase":"final","coverage":0.17096560846560846,"false_great":100,"false_great_rate":0.16863406408094436,"false_terrible":83,"false_terrible_rate":0.1332263242375602,"support":[86,112,113,104,102],"recall":[0.0,0.0,0.167420814479638,0.0,0.0],"confusion":[[0,0,0,5,100,488],[0,0,1,97,2,455],[0,4,111,2,0,546],[3,105,1,0,0,481],[83,3,0,0,0,537]]},{"seed":2928371724749768812,"scenario":"random_reversal","variant":"iteration6","phase":"final","coverage":0.3416005291005291,"false_great":13,"false_great_rate":0.021922428330522766,"false_terrible":20,"false_terrible_rate":0.03210272873194221,"support":[213,205,212,221,182],"recall":[0.31871838111298484,0.32972972972972975,0.3076923076923077,0.3220338983050847,0.26324237560192615],"confusion":[[189,6,0,1,13,384],[4,183,4,14,1,349],[0,5,204,8,0,446],[0,9,4,190,4,383],[20,2,0,8,164,429]]},{"seed":2928371724749768812,"scenario":"random_reversal","variant":"iteration5","phase":"final","coverage":0.4513888888888889,"false_great":81,"false_great_rate":0.13659359190556492,"false_terrible":87,"false_terrible_rate":0.13964686998394862,"support":[281,285,273,276,250],"recall":[0.31871838111298484,0.32972972972972975,0.3936651583710407,0.3220338983050847,0.26324237560192615],"confusion":[[189,6,0,3,81,314],[4,183,5,64,1,298],[0,7,261,11,0,384],[1,85,7,190,4,303],[87,4,0,8,164,360]]},{"seed":5618266449171873643,"scenario":"learnable","variant":"iteration6","phase":"final","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[576,644,602,601,601],"recall":[0.9654576856649395,0.9498432601880877,0.935064935064935,0.9506802721088435,0.966832504145937],"confusion":[[559,20,0,0,0,0],[17,606,15,0,0,0],[0,18,576,22,0,0],[0,0,11,559,18,0],[0,0,0,20,583,0]]},{"seed":5618266449171873643,"scenario":"learnable","variant":"iteration5","phase":"final","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[576,644,602,601,601],"recall":[0.9654576856649395,0.9498432601880877,0.935064935064935,0.9506802721088435,0.966832504145937],"confusion":[[559,20,0,0,0,0],[17,606,15,0,0,0],[0,18,576,22,0,0],[0,0,11,559,18,0],[0,0,0,20,583,0]]},{"seed":5618266449171873643,"scenario":"null","variant":"iteration6","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,579],[0,0,0,0,0,638],[0,0,0,0,0,616],[0,0,0,0,0,588],[0,0,0,0,0,603]]},{"seed":5618266449171873643,"scenario":"null","variant":"iteration5","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,579],[0,0,0,0,0,638],[0,0,0,0,0,616],[0,0,0,0,0,588],[0,0,0,0,0,603]]},{"seed":5618266449171873643,"scenario":"outer_noise","variant":"iteration6","phase":"final","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[576,644,602,601,601],"recall":[0.9654576856649395,0.9498432601880877,0.935064935064935,0.9506802721088435,0.966832504145937],"confusion":[[559,20,0,0,0,0],[17,606,15,0,0,0],[0,18,576,22,0,0],[0,0,11,559,18,0],[0,0,0,20,583,0]]},{"seed":5618266449171873643,"scenario":"outer_noise","variant":"iteration5","phase":"final","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[576,644,602,601,601],"recall":[0.9654576856649395,0.9498432601880877,0.935064935064935,0.9506802721088435,0.966832504145937],"confusion":[[559,20,0,0,0,0],[17,606,15,0,0,0],[0,18,576,22,0,0],[0,0,11,559,18,0],[0,0,0,20,583,0]]},{"seed":5618266449171873643,"scenario":"reversal","variant":"iteration6","phase":"final","coverage":0.03968253968253968,"false_great":23,"false_great_rate":0.039723661485319514,"false_terrible":23,"false_terrible_rate":0.03814262023217247,"support":[23,24,21,29,23],"recall":[0.0,0.0,0.03409090909090909,0.0,0.0],"confusion":[[0,0,0,1,23,555],[0,0,0,27,0,611],[0,1,21,1,0,593],[0,23,0,0,0,565],[23,0,0,0,0,580]]},{"seed":5618266449171873643,"scenario":"reversal","variant":"iteration5","phase":"final","coverage":0.1746031746031746,"false_great":81,"false_great_rate":0.13989637305699482,"false_terrible":100,"false_terrible_rate":0.16583747927031509,"support":[106,106,107,125,84],"recall":[0.0,0.0,0.16558441558441558,0.0,0.0],"confusion":[[0,0,0,6,81,492],[0,0,4,115,3,516],[0,7,102,4,0,503],[6,94,1,0,0,487],[100,5,0,0,0,498]]},{"seed":5618266449171873643,"scenario":"random_reversal","variant":"iteration6","phase":"final","coverage":0.25396825396825395,"false_great":23,"false_great_rate":0.039723661485319514,"false_terrible":17,"false_terrible_rate":0.028192371475953566,"support":[130,170,151,161,156],"recall":[0.1848013816925734,0.2225705329153605,0.2353896103896104,0.21768707482993196,0.21061359867330018],"confusion":[[107,6,0,3,23,440],[5,142,5,16,0,470],[0,4,145,9,0,458],[1,17,1,128,6,435],[17,1,0,5,127,453]]},{"seed":5618266449171873643,"scenario":"random_reversal","variant":"iteration5","phase":"final","coverage":0.36507936507936506,"false_great":101,"false_great_rate":0.17443868739205526,"false_terrible":65,"false_terrible_rate":0.1077943615257048,"support":[180,248,213,227,236],"recall":[0.1848013816925734,0.2225705329153605,0.33116883116883117,0.21768707482993196,0.21061359867330018],"confusion":[[107,6,0,5,101,360],[5,142,6,77,2,406],[0,8,204,12,0,392],[3,88,3,128,6,360],[65,4,0,5,127,402]]},{"seed":8582935296371253491,"scenario":"learnable","variant":"iteration6","phase":"final","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[634,610,570,601,609],"recall":[0.9840255591054313,0.9418416801292407,0.9470899470899471,0.9597989949748744,0.975609756097561],"confusion":[[616,10,0,0,0,0],[18,583,18,0,0,0],[0,17,537,13,0,0],[0,0,15,573,9,0],[0,0,0,15,600,0]]},{"seed":8582935296371253491,"scenario":"learnable","variant":"iteration5","phase":"final","coverage":1.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[634,610,570,601,609],"recall":[0.9840255591054313,0.9418416801292407,0.9470899470899471,0.9597989949748744,0.975609756097561],"confusion":[[616,10,0,0,0,0],[18,583,18,0,0,0],[0,17,537,13,0,0],[0,0,15,573,9,0],[0,0,0,15,600,0]]},{"seed":8582935296371253491,"scenario":"null","variant":"iteration6","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,626],[0,0,0,0,0,619],[0,0,0,0,0,567],[0,0,0,0,0,597],[0,0,0,0,0,615]]},{"seed":8582935296371253491,"scenario":"null","variant":"iteration5","phase":"final","coverage":0.0,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[0,0,0,0,0],"recall":[0.0,0.0,0.0,0.0,0.0],"confusion":[[0,0,0,0,0,626],[0,0,0,0,0,619],[0,0,0,0,0,567],[0,0,0,0,0,597],[0,0,0,0,0,615]]},{"seed":8582935296371253491,"scenario":"outer_noise","variant":"iteration6","phase":"final","coverage":0.9742063492063492,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[634,610,570,523,609],"recall":[0.9840255591054313,0.9418416801292407,0.9470899470899471,0.8358458961474037,0.975609756097561],"confusion":[[616,10,0,0,0,0],[18,583,18,0,0,0],[0,17,537,13,0,0],[0,0,15,499,9,74],[0,0,0,11,600,4]]},{"seed":8582935296371253491,"scenario":"outer_noise","variant":"iteration5","phase":"final","coverage":0.9742063492063492,"false_great":0,"false_great_rate":0.0,"false_terrible":0,"false_terrible_rate":0.0,"support":[634,610,570,523,609],"recall":[0.9840255591054313,0.9418416801292407,0.9470899470899471,0.8358458961474037,0.975609756097561],"confusion":[[616,10,0,0,0,0],[18,583,18,0,0,0],[0,17,537,13,0,0],[0,0,15,499,9,74],[0,0,0,11,600,4]]},{"seed":8582935296371253491,"scenario":"reversal","variant":"iteration6","phase":"final","coverage":0.031746031746031744,"false_great":13,"false_great_rate":0.020766773162939296,"false_terrible":23,"false_terrible_rate":0.03739837398373984,"support":[23,24,17,17,15],"recall":[0.0,0.0,0.026455026455026454,0.0,0.0],"confusion":[[0,0,0,0,13,613],[0,0,1,17,2,599],[0,1,15,0,0,551],[0,22,1,0,0,574],[23,1,0,0,0,591]]},{"seed":8582935296371253491,"scenario":"reversal","variant":"iteration5","phase":"final","coverage":0.1746031746031746,"false_great":105,"false_great_rate":0.16773162939297126,"false_terrible":112,"false_terrible_rate":0.1821138211382114,"support":[114,91,102,110,111],"recall":[0.0,0.0,0.1657848324514991,0.0,0.0],"confusion":[[0,0,0,2,105,519],[0,0,5,105,6,503],[0,2,94,3,0,468],[2,87,3,0,0,505],[112,2,0,0,0,501]]},{"seed":8582935296371253491,"scenario":"random_reversal","variant":"iteration6","phase":"final","coverage":0.6111111111111112,"false_great":27,"false_great_rate":0.04313099041533546,"false_terrible":40,"false_terrible_rate":0.06504065040650407,"support":[401,367,342,368,370],"recall":[0.5511182108626198,0.5072697899838449,0.562610229276896,0.5360134003350083,0.5479674796747968],"confusion":[[345,6,0,0,27,248],[15,314,13,36,0,241],[0,13,319,7,0,228],[1,33,10,320,6,227],[40,1,0,5,337,232]]},{"seed":8582935296371253491,"scenario":"random_reversal","variant":"iteration5","phase":"final","coverage":0.6825396825396826,"false_great":71,"false_great_rate":0.1134185303514377,"false_terrible":85,"false_terrible_rate":0.13821138211382114,"support":[446,411,383,408,416],"recall":[0.5511182108626198,0.5072697899838449,0.6349206349206349,0.5360134003350083,0.5479674796747968],"confusion":[[345,6,0,0,71,204],[15,314,13,75,2,200],[0,14,360,8,0,185],[1,74,10,320,6,186],[85,3,0,5,337,185]]}],"detection":[{"seed":620101,"scenario":"learnable","phase":"design","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6","change":606,"first_detection":620,"delay":14,"false_alarm":false,"events":[{"index":620,"last_signal":617,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.047450806708842386,"threshold":0.04692237703041966}]}]},{"seed":620102,"scenario":"learnable","phase":"design","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6","change":606,"first_detection":610,"delay":4,"false_alarm":false,"events":[{"index":610,"last_signal":607,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.05355248796100778,"threshold":0.04692237703041966}]}]},{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","change":606,"first_detection":613,"delay":7,"false_alarm":false,"events":[{"index":613,"last_signal":610,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.052406149088733756,"threshold":0.04692237703041966}]}]},{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.024490399442385492,"threshold":0.01706337763346477,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.022953208316379807,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","change":606,"first_detection":612,"delay":6,"false_alarm":false,"events":[{"index":612,"last_signal":609,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.04309254165374039,"threshold":0.03317913098760164},{"channel":"CROSS_SECTIONAL_RESIDUAL","window":8,"value":0.023872912241235944,"threshold":0.02346118851520983}]}]},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.023786640078661186,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.024722636901506195,"threshold":0.01706133643749677,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","change":606,"first_detection":611,"delay":5,"false_alarm":false,"events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.05027436122000256,"threshold":0.04692237703041966}]}]},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.02213517899573353,"threshold":0.017067521442752503,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.023413777877967182,"threshold":0.01706133643749677,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","change":606,"first_detection":612,"delay":6,"false_alarm":false,"events":[{"index":612,"last_signal":609,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.044458824009818876,"threshold":0.03317913098760164}]}]},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.025065602999812024,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.022543543419335565,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration6","change":606,"first_detection":611,"delay":5,"false_alarm":false,"events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04764179111708946,"threshold":0.04692237703041966},{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.03489331344990517,"threshold":0.03317913098760164}]}]},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.02465466809538363,"threshold":0.01706337763346477,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.0239434842311612,"threshold":0.01706337763346477,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration6","change":658,"first_detection":662,"delay":4,"false_alarm":false,"events":[{"index":662,"last_signal":659,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.048864062325174984,"threshold":0.04692237703041966}]}]},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration5","change":658,"first_detection":676,"delay":18,"false_alarm":false,"events":[{"index":676,"cell":4,"delta":-0.019973062048084342,"threshold":0.01706337763346477,"last_signal":673,"reason":"CELL_RETURN_DRIFT"}]},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6","change":606,"first_detection":611,"delay":5,"false_alarm":false,"events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.037827217366968056,"threshold":0.03317913098760164}]}]},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.023466275262102015,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.023612056097011093,"threshold":0.017062354508114826,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6","change":646,"first_detection":650,"delay":4,"false_alarm":false,"events":[{"index":650,"last_signal":647,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.055040178262618054,"threshold":0.04692237703041966}]}]},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5","change":646,"first_detection":664,"delay":18,"false_alarm":false,"events":[{"index":664,"cell":0,"delta":0.020426986812477975,"threshold":0.017062354508114826,"last_signal":661,"reason":"CELL_RETURN_DRIFT"},{"index":664,"cell":4,"delta":-0.021199408871530184,"threshold":0.017062354508114826,"last_signal":661,"reason":"CELL_RETURN_DRIFT"}]},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6","change":606,"first_detection":611,"delay":5,"false_alarm":false,"events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04877671662522916,"threshold":0.04692237703041966}]}]},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.023772152271162604,"threshold":0.01748470413692342,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.022542732940539587,"threshold":0.01706337763346477,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6","change":634,"first_detection":638,"delay":4,"false_alarm":false,"events":[{"index":638,"last_signal":635,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04835710147216621,"threshold":0.04692237703041966}]}]},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5","change":634,"first_detection":652,"delay":18,"false_alarm":false,"events":[{"index":652,"cell":0,"delta":0.018881536132618837,"threshold":0.017062354508114826,"last_signal":649,"reason":"CELL_RETURN_DRIFT"}]},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration6","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration5","change":null,"first_detection":null,"delay":null,"false_alarm":false,"events":[]},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6","change":606,"first_detection":610,"delay":4,"false_alarm":false,"events":[{"index":610,"last_signal":607,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04803198523726011,"threshold":0.04692237703041966}]}]},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5","change":606,"first_detection":628,"delay":22,"false_alarm":false,"events":[{"index":628,"cell":0,"delta":0.023950249874225102,"threshold":0.01706337763346477,"last_signal":625,"reason":"CELL_RETURN_DRIFT"},{"index":628,"cell":4,"delta":-0.023039019232057315,"threshold":0.01706133643749677,"last_signal":625,"reason":"CELL_RETURN_DRIFT"}]},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6","change":676,"first_detection":683,"delay":7,"false_alarm":false,"events":[{"index":683,"last_signal":680,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.04449225292099386,"threshold":0.03317913098760164}]}]},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5","change":676,"first_detection":692,"delay":16,"false_alarm":false,"events":[{"index":692,"cell":4,"delta":-0.017222526177696436,"threshold":0.01706133643749677,"last_signal":689,"reason":"CELL_RETURN_DRIFT"}]}],"portfolio":[{"seed":620101,"scenario":"learnable","phase":"design","variant":"iteration6","total_return":0.8940517219737703,"cagr":2.587431925511804,"mdd":0.0014977533699451762,"costs":25909.180274835708,"final_nav":189405.17219737702,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0016103690434886302,"trades":734,"mean_exposure":0.49776500385124006,"adverse_return":0.8940517219737703,"adverse_mdd":0.0014977533699451762},{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6","total_return":-0.06438946461736272,"cagr":-0.12463292608101484,"mdd":0.06438946461736272,"costs":1968.509367930332,"final_nav":93561.05353826373,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.00266826044839728,"trades":76,"mean_exposure":0.053908282444780575,"adverse_return":-0.06438946461736272,"adverse_mdd":0.06438946461736272},{"seed":620102,"scenario":"learnable","phase":"design","variant":"iteration6","total_return":0.9439214906614815,"cagr":2.778830761855556,"mdd":0.0011583046089330695,"costs":26774.44860376415,"final_nav":194392.14906614815,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.001324531806452074,"trades":717,"mean_exposure":0.4979394944395119,"adverse_return":0.9439214906614815,"adverse_mdd":0.0011583046089330695},{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6","total_return":-0.01683181448207416,"cagr":-0.0333803189853894,"mdd":0.01683181448207416,"costs":595.7192056903581,"final_nav":98316.81855179259,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.003429002258910077,"trades":22,"mean_exposure":0.015886556378336553,"adverse_return":-0.01683181448207416,"adverse_mdd":0.01683181448207416},{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","total_return":-0.026055375312072915,"cagr":-0.0514318680414928,"mdd":0.026055375312072915,"costs":1065.6311234215548,"final_nav":97394.46246879271,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0021303594754191204,"trades":42,"mean_exposure":0.028606940752759377,"adverse_return":-0.026055375312072915,"adverse_mdd":0.026055375312072915},{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","total_return":-0.09335387657175176,"cagr":-0.1779928068725296,"mdd":0.09335387657175176,"costs":3147.85109849186,"final_nav":90664.61234282482,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.00328233948439627,"trades":129,"mean_exposure":0.08740442927292283,"adverse_return":-0.09335387657175176,"adverse_mdd":0.09335387657175176},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","total_return":-0.03188680721311221,"cagr":-0.06275684595197828,"mdd":0.03188680721311221,"costs":888.102638488901,"final_nav":96811.31927868878,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0032217073400820483,"trades":35,"mean_exposure":0.023828573969865784,"adverse_return":-0.03188680721311221,"adverse_mdd":0.03188680721311221},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","total_return":-0.11608906596128998,"cagr":-0.21870146068681517,"mdd":0.11608906596128998,"costs":3115.2372166834834,"final_nav":88391.093403871,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0032217073400820483,"trades":125,"mean_exposure":0.0874371708236961,"adverse_return":-0.11608906596128998,"adverse_mdd":0.11608906596128998},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","total_return":-0.024002278229581453,"cagr":-0.047428447098952664,"mdd":0.024002278229581453,"costs":705.6349386080876,"final_nav":97599.77217704186,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0023171847217666095,"trades":27,"mean_exposure":0.018933714115878228,"adverse_return":-0.024002278229581453,"adverse_mdd":0.024002278229581453},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","total_return":-0.09932318634435422,"cagr":-0.18878127734311312,"mdd":0.09932318634435422,"costs":3041.6181921266652,"final_nav":90067.68136556458,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0030038860486007236,"trades":121,"mean_exposure":0.0849147521816611,"adverse_return":-0.09932318634435422,"adverse_mdd":0.09932318634435422},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","total_return":-0.031073516723354233,"cagr":-0.06118147000515184,"mdd":0.031073516723354233,"costs":886.0395496830652,"final_nav":96892.64832766457,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002671397402377856,"trades":33,"mean_exposure":0.02383063953301846,"adverse_return":-0.031073516723354233,"adverse_mdd":0.031073516723354233},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","total_return":-0.10362440974389797,"cagr":-0.19651080119302466,"mdd":0.10362440974389797,"costs":3112.1634844739756,"final_nav":89637.5590256102,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002923011157214521,"trades":124,"mean_exposure":0.08745282346965874,"adverse_return":-0.10362440974389797,"adverse_mdd":0.10362440974389797},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","total_return":0.8565803518951918,"cagr":2.446890603043274,"mdd":0.001963545471879824,"costs":26390.734316483435,"final_nav":185658.03518951917,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0018333001423728027,"trades":713,"mean_exposure":0.49860300716718614,"adverse_return":0.8565803518951918,"adverse_mdd":0.001963545471879824},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","total_return":0.8565803518951918,"cagr":2.446890603043274,"mdd":0.001963545471879824,"costs":26390.734316483435,"final_nav":185658.03518951917,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0018333001423728027,"trades":713,"mean_exposure":0.49860300716718614,"adverse_return":0.8565803518951918,"adverse_mdd":0.001963545471879824},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","total_return":0.8532868241113967,"cagr":2.434672052424907,"mdd":0.003995693570929326,"costs":26113.89853369401,"final_nav":185328.68241113966,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0017168536902495927,"trades":711,"mean_exposure":0.49857151938894406,"adverse_return":0.8532868241113967,"adverse_mdd":0.003995693570929326},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","total_return":0.8532868241113967,"cagr":2.434672052424907,"mdd":0.003995693570929326,"costs":26113.89853369401,"final_nav":185328.68241113966,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0017168536902495927,"trades":711,"mean_exposure":0.49857151938894406,"adverse_return":0.8532868241113967,"adverse_mdd":0.003995693570929326},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration6","total_return":0.81631118785166,"cagr":2.298986331115108,"mdd":0.0014977533699451762,"costs":25718.576468907453,"final_nav":181631.118785166,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0016926044265318239,"trades":722,"mean_exposure":0.4986810633488832,"adverse_return":0.81631118785166,"adverse_mdd":0.0014977533699451762},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration5","total_return":0.81631118785166,"cagr":2.298986331115108,"mdd":0.0014977533699451762,"costs":25718.576468907453,"final_nav":181631.118785166,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0016926044265318239,"trades":722,"mean_exposure":0.4986810633488832,"adverse_return":0.81631118785166,"adverse_mdd":0.0014977533699451762},{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration6","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration5","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration6","total_return":0.8651721717471816,"cagr":2.4788672302600983,"mdd":0.001803312905802934,"costs":21989.132204031932,"final_nav":186517.21717471816,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0019533583169471787,"trades":559,"mean_exposure":0.4147968461458722,"adverse_return":0.8651721717471816,"adverse_mdd":0.001803312905802934},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration5","total_return":0.8651721717471816,"cagr":2.4788672302600983,"mdd":0.001803312905802934,"costs":21989.132204031932,"final_nav":186517.21717471816,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0019533583169471787,"trades":559,"mean_exposure":0.4147968461458722,"adverse_return":0.8651721717471816,"adverse_mdd":0.001803312905802934},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration6","total_return":-0.024393305489778028,"cagr":-0.048191577626838455,"mdd":0.024393305489778028,"costs":817.5013942304197,"final_nav":97560.6694510222,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002349879220985422,"trades":30,"mean_exposure":0.021945710661287237,"adverse_return":-0.024393305489778028,"adverse_mdd":0.024393305489778028},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration5","total_return":-0.10755309610645214,"cagr":-0.2035385237308206,"mdd":0.10755309610645214,"costs":3126.7626931974437,"final_nav":89244.69038935479,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0031670474165727863,"trades":125,"mean_exposure":0.087422703794017,"adverse_return":-0.10755309610645214,"adverse_mdd":0.10755309610645214},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration6","total_return":0.24793849545334878,"cagr":0.5573504884343679,"mdd":0.029159505497852733,"costs":9628.875577594667,"final_nav":124793.84954533487,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0026124641861204317,"trades":315,"mean_exposure":0.22181358554367403,"adverse_return":-0.0250050891166117,"adverse_mdd":0.029159505497852733},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration5","total_return":0.15957024758460636,"cagr":0.3446031590834253,"mdd":0.09790606133513535,"costs":12148.148713573388,"final_nav":115957.02475846064,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":1,"max_realized_trade_loss_nav":0.0033369846230726394,"trades":396,"mean_exposure":0.277458064516062,"adverse_return":-0.09404582491377622,"adverse_mdd":0.09790606133513535},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration6","total_return":0.8504453823643263,"cagr":2.424148113113458,"mdd":0.002473713338672412,"costs":25733.33599489699,"final_nav":185044.53823643262,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0015337588484140284,"trades":717,"mean_exposure":0.49705171792761027,"adverse_return":0.8504453823643263,"adverse_mdd":0.002473713338672412},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration5","total_return":0.8504453823643263,"cagr":2.424148113113458,"mdd":0.002473713338672412,"costs":25733.33599489699,"final_nav":185044.53823643262,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0015337588484140284,"trades":717,"mean_exposure":0.49705171792761027,"adverse_return":0.8504453823643263,"adverse_mdd":0.002473713338672412},{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration6","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration5","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration6","total_return":0.8547208848906116,"cagr":2.4399895608494133,"mdd":0.004324185048012019,"costs":25858.06598751037,"final_nav":185472.08848906116,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0022171985605175457,"trades":716,"mean_exposure":0.49704676274094073,"adverse_return":0.8547208848906116,"adverse_mdd":0.004324185048012019},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration5","total_return":0.8547208848906116,"cagr":2.4399895608494133,"mdd":0.004324185048012019,"costs":25858.06598751037,"final_nav":185472.08848906116,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0022171985605175457,"trades":716,"mean_exposure":0.49704676274094073,"adverse_return":0.8547208848906116,"adverse_mdd":0.004324185048012019},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6","total_return":-0.03575999687358267,"cagr":-0.07024121637076675,"mdd":0.03575999687358267,"costs":841.4668434742601,"final_nav":96424.00031264173,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.003210813216924959,"trades":31,"mean_exposure":0.02259300911462267,"adverse_return":-0.03575999687358267,"adverse_mdd":0.03575999687358267},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5","total_return":-0.11396505904559251,"cagr":-0.21494208340791965,"mdd":0.11396505904559251,"costs":3109.93923873165,"final_nav":88603.49409544075,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.003210813216924959,"trades":128,"mean_exposure":0.08741276223106023,"adverse_return":-0.11396505904559251,"adverse_mdd":0.11396505904559251},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6","total_return":0.13925442671961563,"cagr":0.29790064880024003,"mdd":0.031117535420133735,"costs":7207.941005554794,"final_nav":113925.44267196156,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0034037312633723883,"trades":244,"mean_exposure":0.1742909564264474,"adverse_return":-0.023752926156381138,"adverse_mdd":0.031117535420133735},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5","total_return":0.05869276222953612,"cagr":0.1208303647972051,"mdd":0.09963145312906607,"costs":9495.165979420852,"final_nav":105869.2762229536,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0034037312633723883,"trades":322,"mean_exposure":0.22938691321045607,"adverse_return":-0.09278762760482928,"adverse_mdd":0.09963145312906607},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration6","total_return":0.874409602355974,"cagr":2.5134113574042805,"mdd":0.0008456451125780085,"costs":26199.97576841569,"final_nav":187440.9602355974,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0012888158575118408,"trades":718,"mean_exposure":0.49790802615549573,"adverse_return":0.874409602355974,"adverse_mdd":0.0008456451125780085},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration5","total_return":0.874409602355974,"cagr":2.5134113574042805,"mdd":0.0008456451125780085,"costs":26199.97576841569,"final_nav":187440.9602355974,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0012888158575118408,"trades":718,"mean_exposure":0.49790802615549573,"adverse_return":0.874409602355974,"adverse_mdd":0.0008456451125780085},{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration6","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration5","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration6","total_return":0.8744341121501213,"cagr":2.5135032407920135,"mdd":0.0020469272718128817,"costs":26126.36033463142,"final_nav":187443.41121501214,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0018822853202226592,"trades":720,"mean_exposure":0.4978893403936581,"adverse_return":0.8744341121501213,"adverse_mdd":0.0020469272718128817},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration5","total_return":0.8744341121501213,"cagr":2.5135032407920135,"mdd":0.0020469272718128817,"costs":26126.36033463142,"final_nav":187443.41121501214,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0018822853202226592,"trades":720,"mean_exposure":0.4978893403936581,"adverse_return":0.8744341121501213,"adverse_mdd":0.0020469272718128817},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6","total_return":-0.016336906927685635,"cagr":-0.03240691932740736,"mdd":0.016336906927685635,"costs":793.9423304585371,"final_nav":98366.30930723144,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002548161607520415,"trades":29,"mean_exposure":0.021162084933629272,"adverse_return":-0.016336906927685635,"adverse_mdd":0.016336906927685635},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5","total_return":-0.08811175064830834,"cagr":-0.16845982069430698,"mdd":0.08811175064830834,"costs":3168.8066434729094,"final_nav":91188.82493516916,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0027077403368593505,"trades":125,"mean_exposure":0.08738490701128236,"adverse_return":-0.08811175064830834,"adverse_mdd":0.08811175064830834},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6","total_return":0.10853163460753401,"cagr":0.22884238492565134,"mdd":0.028102749678697858,"costs":5177.5337334307105,"final_nav":110853.16346075339,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002684587524622102,"trades":184,"mean_exposure":0.12665354190170924,"adverse_return":-0.023067968183259402,"adverse_mdd":0.028102749678697858},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5","total_return":0.055407703307541745,"cagr":0.11388542020090009,"mdd":0.0746787797574423,"costs":7441.147697788658,"final_nav":105540.77033075417,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002684587524622102,"trades":264,"mean_exposure":0.1822714431439817,"adverse_return":-0.06988527904996156,"adverse_mdd":0.0746787797574423},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration6","total_return":0.8204923601488163,"cagr":2.3141924333602075,"mdd":0.001092188877178324,"costs":25456.607087425324,"final_nav":182049.23601488164,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.00194740584562284,"trades":710,"mean_exposure":0.49819613772205956,"adverse_return":0.8204923601488163,"adverse_mdd":0.001092188877178324},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration5","total_return":0.8204923601488163,"cagr":2.3141924333602075,"mdd":0.001092188877178324,"costs":25456.607087425324,"final_nav":182049.23601488164,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.00194740584562284,"trades":710,"mean_exposure":0.49819613772205956,"adverse_return":0.8204923601488163,"adverse_mdd":0.001092188877178324},{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration6","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration5","total_return":0.0,"cagr":0.0,"mdd":0.0,"costs":0.0,"final_nav":100000.0,"max_modeled_risk":0,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0,"trades":0,"mean_exposure":0.0,"adverse_return":0.0,"adverse_mdd":0.0},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration6","total_return":0.8187634499350103,"cagr":2.3079004868195008,"mdd":0.0024892167442193136,"costs":25322.77378377802,"final_nav":181876.34499350103,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0027342573070285488,"trades":733,"mean_exposure":0.4955742932131512,"adverse_return":0.8187634499350103,"adverse_mdd":0.0024892167442193136},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration5","total_return":0.8187634499350103,"cagr":2.3079004868195008,"mdd":0.0024892167442193136,"costs":25322.77378377802,"final_nav":181876.34499350103,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0027342573070285488,"trades":733,"mean_exposure":0.4955742932131512,"adverse_return":0.8187634499350103,"adverse_mdd":0.0024892167442193136},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6","total_return":-0.013088688584461106,"cagr":-0.026006063400061175,"mdd":0.013088688584461106,"costs":595.9687531458937,"final_nav":98691.1311415539,"max_modeled_risk":0.0199700449326011,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0020456929777978947,"trades":22,"mean_exposure":0.015879804590185658,"adverse_return":-0.013088688584461106,"adverse_mdd":0.013088688584461106},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5","total_return":-0.10243090545084454,"cagr":-0.1943697205102093,"mdd":0.10243090545084454,"costs":3139.9363423170666,"final_nav":89756.90945491554,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.003532373518231643,"trades":129,"mean_exposure":0.08740311188381342,"adverse_return":-0.10243090545084454,"adverse_mdd":0.10243090545084454},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6","total_return":0.314095253454145,"cagr":0.7268463351507137,"mdd":0.03510434914073657,"costs":13850.403311740392,"final_nav":131409.5253454145,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.0023173693996002007,"trades":429,"mean_exposure":0.3060695457438013,"adverse_return":-0.03244331811693324,"adverse_mdd":0.03510434914073657},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5","total_return":0.2582097332820623,"cagr":0.5830917329257184,"mdd":0.0761391943837354,"costs":15530.561118160205,"final_nav":125820.97332820624,"max_modeled_risk":0.019970044932601103,"gap_loss_exceedances":0,"max_realized_trade_loss_nav":0.002991422724634421,"trades":479,"mean_exposure":0.34067214764215786,"adverse_return":-0.0735913310337124,"adverse_mdd":0.0761391943837354}],"paired":[{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","false_great_delta":-72},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","false_great_delta":-87},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","false_great_delta":-86},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","false_great_delta":-81},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","false_great_delta":0},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","false_great_delta":0},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","false_great_delta":0},{"seed":2098214662956861329,"scenario":"null","phase":"final","false_great_delta":0},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","false_great_delta":0},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","false_great_delta":-85},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","false_great_delta":-64},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","false_great_delta":0},{"seed":2928371724749768812,"scenario":"null","phase":"final","false_great_delta":0},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","false_great_delta":0},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","false_great_delta":-72},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","false_great_delta":-68},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","false_great_delta":0},{"seed":5618266449171873643,"scenario":"null","phase":"final","false_great_delta":0},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","false_great_delta":0},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","false_great_delta":-58},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","false_great_delta":-78},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","false_great_delta":0},{"seed":8582935296371253491,"scenario":"null","phase":"final","false_great_delta":0},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","false_great_delta":0},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","false_great_delta":-92},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","false_great_delta":-44}],"channels":[{"seed":620101,"scenario":"learnable","phase":"design","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"974712dd3b8813e43104dd55a8a6f31e7d3128dcf2a37b927ab65d65a51cd639","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":11,"funded_error":-0.004317921367845048,"alarm":false,"latched":false},{"index":730,"matured_fills":48,"funded_error":0.0024467905493189847,"alarm":false,"latched":false},{"index":731,"matured_fills":48,"funded_error":0.0025158366176078004,"alarm":false,"latched":false}]}},{"seed":620101,"scenario":"reversal","phase":"design","events":[{"index":620,"last_signal":617,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.047450806708842386,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"e4c212218ff54c3e754d626fa74c8a90fdfbcb6c2c8ca1ee27d9c35277d857bc","alarm_rows":99,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":6,"funded_error":-0.03037540383708524,"alarm":false,"latched":false},{"index":619,"matured_fills":44,"funded_error":-0.01810036912119699,"alarm":false,"latched":false},{"index":620,"matured_fills":43,"funded_error":-0.018885286938729637,"alarm":true,"latched":true},{"index":621,"matured_fills":43,"funded_error":-0.0185839340666563,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":620102,"scenario":"learnable","phase":"design","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"fe9a55972b80924ec2291c6d8901a4b7063c04463938ce8c1d4f5569c3e903bf","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":7,"funded_error":0.010819650240603822,"alarm":false,"latched":false},{"index":730,"matured_fills":45,"funded_error":0.0017633987211077896,"alarm":false,"latched":false},{"index":731,"matured_fills":46,"funded_error":0.0024795704078796606,"alarm":false,"latched":false}]}},{"seed":620102,"scenario":"reversal","phase":"design","events":[{"index":610,"last_signal":607,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.05355248796100778,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"b877fc8afd4e122b0620c36f7fcd6c1de3e9df1fd44e9d2c60fc10e32d597439","alarm_rows":108,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":8,"funded_error":-0.010637773579050937,"alarm":false,"latched":false},{"index":610,"matured_fills":11,"funded_error":-0.01815284270918504,"alarm":true,"latched":true},{"index":611,"matured_fills":19,"funded_error":-0.01894978618201605,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","events":[{"index":613,"last_signal":610,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.052406149088733756,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"57ca1bd9276b506ffba8fcbb5763ac1fd33c9b7e53679da31a78393f6c9e5c16","alarm_rows":104,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":6,"funded_error":-0.011118654534471615,"alarm":false,"latched":false},{"index":612,"matured_fills":23,"funded_error":-0.01997396096078354,"alarm":false,"latched":false},{"index":613,"matured_fills":30,"funded_error":-0.018955419979949387,"alarm":true,"latched":true},{"index":614,"matured_fills":35,"funded_error":-0.018959691602306997,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","events":[{"index":612,"last_signal":609,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.04309254165374039,"threshold":0.03317913098760164},{"channel":"CROSS_SECTIONAL_RESIDUAL","window":8,"value":0.023872912241235944,"threshold":0.02346118851520983}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"80fe4c280870f8432f8326147e698dba09e5ac817bd8af29a0f87d3905a10b7a","alarm_rows":86,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":9,"funded_error":-0.011743376531782477,"alarm":false,"latched":false},{"index":611,"matured_fills":21,"funded_error":-0.01858751407257168,"alarm":false,"latched":false},{"index":612,"matured_fills":23,"funded_error":-0.019866010701772734,"alarm":true,"latched":true},{"index":613,"matured_fills":33,"funded_error":-0.020753598418579308,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.05027436122000256,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"1c73adc08251b25d94730213c6ef6856c713553c8a72938290a00743795f09d9","alarm_rows":100,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":4,"funded_error":-0.012574372056757826,"alarm":false,"latched":false},{"index":610,"matured_fills":11,"funded_error":-0.016974270706826125,"alarm":false,"latched":false},{"index":611,"matured_fills":15,"funded_error":-0.01950777371755344,"alarm":true,"latched":true},{"index":612,"matured_fills":22,"funded_error":-0.019260205663938823,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":false,"latched":true}]}},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","events":[{"index":612,"last_signal":609,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.044458824009818876,"threshold":0.03317913098760164}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"eeb77d09c5ab1dc59402e354b0e8a15ed8ed51144ab139129135930186594ef5","alarm_rows":87,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":11,"funded_error":-0.017655631582207332,"alarm":false,"latched":false},{"index":611,"matured_fills":22,"funded_error":-0.01780062599980764,"alarm":false,"latched":false},{"index":612,"matured_fills":22,"funded_error":-0.01780062599980764,"alarm":true,"latched":true},{"index":613,"matured_fills":28,"funded_error":-0.019555772973064732,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"f30597dbf8364012df71ec857e63e96283876dd582aa13203de7a435580237c9","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":11,"funded_error":0.008805113522367325,"alarm":false,"latched":false},{"index":730,"matured_fills":46,"funded_error":-0.003348468171800803,"alarm":false,"latched":false},{"index":731,"matured_fills":45,"funded_error":-0.0025509142694897066,"alarm":false,"latched":false}]}},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"85a896e0495348046bf226f64cd488f6ff21debca6e488c7e3d867ba5f8b5abb","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":9,"funded_error":-0.0016386918489880923,"alarm":false,"latched":false},{"index":730,"matured_fills":44,"funded_error":0.0005494007930522493,"alarm":false,"latched":false},{"index":731,"matured_fills":44,"funded_error":-0.0005477279401936729,"alarm":false,"latched":false}]}},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"76bfa191a242758e3505faac01ec14b06ca3c518e6c4d33ad7e210c5942aea38","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":11,"funded_error":-0.004839138135868936,"alarm":false,"latched":false},{"index":730,"matured_fills":47,"funded_error":0.0007087324434724404,"alarm":false,"latched":false},{"index":731,"matured_fills":47,"funded_error":0.0006534215456484976,"alarm":false,"latched":false}]}},{"seed":2098214662956861329,"scenario":"null","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"ea826a0484a7056fae27d5ea45260bad399ced8a99adef34ce056604445c9427","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":730,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":731,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false}]}},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"d7ea45df76981142f5cc7d2c518641ff7d6f545918033977899f005ce283a227","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":6,"funded_error":-0.006991695660838785,"alarm":false,"latched":false},{"index":730,"matured_fills":39,"funded_error":0.0006096317170329785,"alarm":false,"latched":false},{"index":731,"matured_fills":37,"funded_error":0.0006999586442057031,"alarm":false,"latched":false}]}},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04764179111708946,"threshold":0.04692237703041966},{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.03489331344990517,"threshold":0.03317913098760164}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"b7800dc55673b60c6ca5afc013e399591ff6319c99e116221be3efd2e1ec34ed","alarm_rows":102,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":8,"funded_error":-0.02270884218948751,"alarm":false,"latched":false},{"index":610,"matured_fills":11,"funded_error":-0.01600708218153105,"alarm":false,"latched":false},{"index":611,"matured_fills":19,"funded_error":-0.01605800749212207,"alarm":true,"latched":true},{"index":612,"matured_fills":22,"funded_error":-0.01810164873874568,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","events":[{"index":662,"last_signal":659,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.048864062325174984,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"ce006ee9d92deeb3c4d44e16da211bd286c4fa114f1b6a4c1388274e6a86e094","alarm_rows":61,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":11,"funded_error":-0.004839138135868936,"alarm":false,"latched":false},{"index":661,"matured_fills":43,"funded_error":-0.004465371106292965,"alarm":false,"latched":false},{"index":662,"matured_fills":44,"funded_error":-0.008203150863074741,"alarm":true,"latched":true},{"index":663,"matured_fills":44,"funded_error":-0.011203613190557788,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"1053ce399131db75e8a21823d32adce9557a2284e7da65cbbccea014c36f8e1a","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":7,"funded_error":0.007215406286721769,"alarm":false,"latched":false},{"index":730,"matured_fills":46,"funded_error":-0.002899104778249846,"alarm":false,"latched":false},{"index":731,"matured_fills":46,"funded_error":-0.003750128412089142,"alarm":false,"latched":false}]}},{"seed":2928371724749768812,"scenario":"null","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"ea826a0484a7056fae27d5ea45260bad399ced8a99adef34ce056604445c9427","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":730,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":731,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false}]}},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"d799f409173a31dc40e5a2c49d2d548a8caf1b26eafaa8d9deaccfeeacd3abf1","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":7,"funded_error":0.008722171239878722,"alarm":false,"latched":false},{"index":730,"matured_fills":46,"funded_error":-0.0035917130103061473,"alarm":false,"latched":false},{"index":731,"matured_fills":46,"funded_error":-0.004659625072902,"alarm":false,"latched":false}]}},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.037827217366968056,"threshold":0.03317913098760164}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"ce18a71671402447affac77fc5e9696c9f525953cc49d1efe47aa2d7ff4f8a14","alarm_rows":107,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":11,"funded_error":-0.016576215259901574,"alarm":false,"latched":false},{"index":610,"matured_fills":11,"funded_error":-0.016576215259901574,"alarm":false,"latched":false},{"index":611,"matured_fills":22,"funded_error":-0.02102293418957677,"alarm":true,"latched":true},{"index":612,"matured_fills":22,"funded_error":-0.02102293418957677,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","events":[{"index":650,"last_signal":647,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.055040178262618054,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"4272084035f99ab964f19e9a61f737db535c1af09686eeb362af447b7a5a0d67","alarm_rows":72,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":7,"funded_error":0.007215406286721769,"alarm":false,"latched":false},{"index":649,"matured_fills":44,"funded_error":-0.003110572151654574,"alarm":false,"latched":false},{"index":650,"matured_fills":45,"funded_error":-0.006125728792943403,"alarm":true,"latched":true},{"index":651,"matured_fills":43,"funded_error":-0.009987744015812563,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"07e40de0130b301fa21efd9ca896e5b0363389b4e3c0e13c4eaf167fd2a9f8fb","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":6,"funded_error":0.0036638075714688777,"alarm":false,"latched":false},{"index":730,"matured_fills":44,"funded_error":-0.0012431121298687477,"alarm":false,"latched":false},{"index":731,"matured_fills":44,"funded_error":-0.0011813723021852176,"alarm":false,"latched":false}]}},{"seed":5618266449171873643,"scenario":"null","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"ea826a0484a7056fae27d5ea45260bad399ced8a99adef34ce056604445c9427","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":730,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":731,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false}]}},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"fb62be788e9b98d57a95c45c7ba72751dc3b8f3efff4113d511933764b613bc0","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":6,"funded_error":0.004591888925828164,"alarm":false,"latched":false},{"index":730,"matured_fills":44,"funded_error":-0.0011187779832266757,"alarm":false,"latched":false},{"index":731,"matured_fills":44,"funded_error":-0.0009900539459881787,"alarm":false,"latched":false}]}},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","events":[{"index":611,"last_signal":608,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04877671662522916,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"7d910269ffde77f88b71b05693d3a13130b176bd81c4fbd093b4e5d168ca17d9","alarm_rows":90,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":11,"funded_error":-0.010782142109494706,"alarm":false,"latched":false},{"index":610,"matured_fills":11,"funded_error":-0.010782142109494706,"alarm":false,"latched":false},{"index":611,"matured_fills":18,"funded_error":-0.011072219309255182,"alarm":true,"latched":true},{"index":612,"matured_fills":22,"funded_error":-0.015439234514798705,"alarm":false,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","events":[{"index":638,"last_signal":635,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04835710147216621,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"42c29ecbc71444b89eff5a38a346fa0b59fd29aa55dab413c694141631a3cf6f","alarm_rows":76,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":6,"funded_error":0.0036638075714688777,"alarm":false,"latched":false},{"index":637,"matured_fills":48,"funded_error":-0.0034194711914345356,"alarm":false,"latched":false},{"index":638,"matured_fills":48,"funded_error":-0.007040940269738308,"alarm":true,"latched":true},{"index":639,"matured_fills":47,"funded_error":-0.010460493924206627,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"67e6d2c471b7f1a44c9731b7821111fb2e7bee8c6f487de1cbb0d292b8ddb6fe","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":8,"funded_error":0.005283742883183452,"alarm":false,"latched":false},{"index":730,"matured_fills":47,"funded_error":0.0030205392786931537,"alarm":false,"latched":false},{"index":731,"matured_fills":46,"funded_error":0.002372870188446263,"alarm":false,"latched":false}]}},{"seed":8582935296371253491,"scenario":"null","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"ea826a0484a7056fae27d5ea45260bad399ced8a99adef34ce056604445c9427","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":730,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":731,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false}]}},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","events":[],"trace_summary":{"rows":126,"canonical_json_sha256":"4cb5987434e2a983d85eae44f0c9fb8f092e6f3c86ad7f63b57dd05845a3be47","alarm_rows":0,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":8,"funded_error":0.0065859547654041175,"alarm":false,"latched":false},{"index":730,"matured_fills":45,"funded_error":0.0034587176885792787,"alarm":false,"latched":false},{"index":731,"matured_fills":43,"funded_error":0.002936976108222349,"alarm":false,"latched":false}]}},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","events":[{"index":610,"last_signal":607,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":2,"value":0.04803198523726011,"threshold":0.04692237703041966}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"c755c2b7790ac9794859ca81143a8f88b3f8ae7fadfd0798bcf995c3e8b1982b","alarm_rows":102,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":10,"funded_error":-0.014022878895225141,"alarm":false,"latched":false},{"index":610,"matured_fills":11,"funded_error":-0.016291098996882372,"alarm":true,"latched":true},{"index":611,"matured_fills":18,"funded_error":-0.0158670283275044,"alarm":true,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","events":[{"index":683,"last_signal":680,"evidence":[{"channel":"CROSS_SECTIONAL_RESIDUAL","window":4,"value":0.04449225292099386,"threshold":0.03317913098760164}]}],"trace_summary":{"rows":126,"canonical_json_sha256":"44e7403b9729d0e5e22b888a8929948dfd2985e1f74881366f3240a0eebd5982","alarm_rows":37,"selected_rows":[{"index":606,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":607,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":608,"matured_fills":0,"funded_error":null,"alarm":false,"latched":false},{"index":609,"matured_fills":8,"funded_error":0.005283742883183452,"alarm":false,"latched":false},{"index":682,"matured_fills":44,"funded_error":-0.011421791621130198,"alarm":false,"latched":false},{"index":683,"matured_fills":44,"funded_error":-0.013488877385364244,"alarm":true,"latched":true},{"index":684,"matured_fills":44,"funded_error":-0.015062687882014989,"alarm":false,"latched":true},{"index":730,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true},{"index":731,"matured_fills":0,"funded_error":null,"alarm":true,"latched":true}]}}],"audits":[{"seed":620101,"scenario":"learnable","phase":"design","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":5.820766091346741e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6","min_cash":0.0,"net_error":3.3306690738754696e-16,"pnl_error":6.366462912410498e-12,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":620102,"scenario":"learnable","phase":"design","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.4551915228366852e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":1.3642420526593924e-11,"horizon_ok":true,"max_risk":0.0199700449326011,"gap_exceed":0},{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":9.094947017729282e-13,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":2.000888343900442e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":3.637978807091713e-12,"horizon_ok":true,"max_risk":0.0199700449326011,"gap_exceed":0},{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":3.637978807091713e-12,"horizon_ok":true,"max_risk":0.0199700449326011,"gap_exceed":0},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":1.1823431123048067e-11,"horizon_ok":true,"max_risk":0.0199700449326011,"gap_exceed":0},{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":3.092281986027956e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":1.546140993013978e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":1.0913936421275139e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":4.3655745685100555e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":4.3655745685100555e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":0.0,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":0.0,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":0.0,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":0.0,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration6","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration5","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.6007106751203537e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.6007106751203537e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":9.094947017729282e-13,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":2.7284841053187847e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":7.275957614183426e-12,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":9.640643838793039e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":1},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":4.3655745685100555e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":4.3655745685100555e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration6","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration5","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":3.3306690738754696e-16,"pnl_error":2.9103830456733704e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":3.3306690738754696e-16,"pnl_error":2.9103830456733704e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":2.0463630789890885e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":3.3306690738754696e-16,"pnl_error":3.8198777474462986e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.8189894035458565e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":3.001332515850663e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.0186340659856796e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.0186340659856796e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration6","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration5","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.7462298274040222e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.7462298274040222e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":1.1102230246251565e-16,"pnl_error":6.821210263296962e-12,"horizon_ok":true,"max_risk":0.0199700449326011,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":3.2741809263825417e-11,"horizon_ok":true,"max_risk":0.0199700449326011,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":1.4551915228366852e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":2.7284841053187847e-12,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":7.275957614183426e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":7.275957614183426e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration6","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration5","min_cash":100000.0,"net_error":0,"pnl_error":0.0,"horizon_ok":true,"max_risk":0,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":1.4551915228366852e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":1.4551915228366852e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":2.432898327242583e-11,"horizon_ok":true,"max_risk":0.0199700449326011,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":2.220446049250313e-16,"pnl_error":3.637978807091713e-11,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.1641532182693481e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0},{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5","min_cash":0.0,"net_error":4.440892098500626e-16,"pnl_error":1.0913936421275139e-10,"horizon_ok":true,"max_risk":0.019970044932601103,"gap_exceed":0}],"blocker":"Failed checks: five_tier_support","limitations":["Four fresh seeds cannot establish <=5% population false alarm probability.","No safe zero-delay detection is identifiable from this DGP; first3 sessions remain exposed.","Model loss is per trade, not portfolio or realized gap cap.","Fresh seeds use inherited synthetic DGP; no real alpha or production readiness.","No independent sector data exists; market price breadth has exactly no switch information.","Local hash freeze only; no trusted public timestamp."],"post_run_artifact_audit":{"zero_new_replays":true,"funded_gate_ok":true,"null_cash_and_cost_ok":true,"max_both_leg_cost_error":7.275957614183426e-11,"funded_trades_checked":9989,"frozen_hashes_match":true},"next_blocker":"Five-tier support: seed2098214662956861329 has0 AVERAGE assignments. Frozen interval straddles a band; this experiment cannot repair it after final evaluation. Next independent step must obtain more independent fit/calibration evidence under unchanged bands, then freeze and test fresh tapes. Rapid safety is promising but residual4\u20137-session exposure and false-alarm power need independent episode validation; no safe zero-delay detection from this DGP.","false_alarm_power":{"independent_fresh_seeds":4,"alarmed":0,"one_sided95_upper_seed_probability":0.5271291954984121,"paired_scenarios_not_independent":true}}
```


## discrimination_iteration6/run.py

```
"""One bounded run. Refuses fresh-seed reuse; all budgeted replay calls counted."""
import copy,csv,gzip,json,math,secrets,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import engine as x
O=x.O

def dump(name,obj):(O/name).write_text(json.dumps(obj,indent=2))
def csvout(name,rows):
 with (O/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def score(ss,truth,seed,scenario,variant,phase,change):
 mat=[[0]*6 for _ in range(5)];real=[[0]*6 for _ in range(5)]
 for k,i in enumerate(range(x.START,x.END)):
  for j,z in enumerate(ss[k]):
   a=x.e.TIERS.index(x.e.tier(truth[i][j]));b=x.e.TIERS.index(z['label']) if z['label']!='UNKNOWN' else 5;mat[a][b]+=1
 n=126*24;assigned=sum(sum(r[:5]) for r in mat)
 return dict(seed=seed,scenario=scenario,variant=variant,phase=phase,coverage=assigned/n,false_great=mat[0][4],false_great_rate=mat[0][4]/max(1,sum(mat[0])),false_terrible=mat[4][0],false_terrible_rate=mat[4][0]/max(1,sum(mat[4])),support=[sum(r[c] for r in mat) for c in range(5)],recall=[mat[c][c]/max(1,sum(mat[c])) for c in range(5)],confusion=mat)

def main():
 start=time.monotonic()
 if (O/'commitment.json').exists():raise SystemExit('Refusing final-seed reuse')
 plan=json.loads((O/'preregister.json').read_text());count=0
 tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(O),'-p','test_*.py','-v'],capture_output=True,text=True)
 (O/'tests.log').write_text(tests.stdout+tests.stderr);count+=3
 if tests.returncode:raise SystemExit(tests.stderr)
 scores=[];metrics=[];detection=[];audits=[];confusions=[];channels=[]
 old=json.loads((O.parent/'discrimination_iteration5/report.json').read_text())
 diagnosis=[]
 with gzip.open(O.parent/'discrimination_iteration5/opportunities.jsonl.gz','rt') as f:
  agg={}
  for line in f:
   z=json.loads(line)
   if z['scenario']=='reversal' and z['variant']=='candidate' and z['true_ev']==-.012 and z['inferred_tier']=='GREAT':
    a=agg.setdefault(z['seed'],dict(first=z['index'],last=z['index'],unavoidable_first3=0,fixable_after_first3=0,count=0,funded=0,funded_pnl=0.))
    a['last']=z['index'];a['count']+=1;a['unavoidable_first3']+=z['index']<609;a['fixable_after_first3']+=z['index']>=609;a['funded']+=z['funded'];a['funded_pnl']+=z['funded_debit']*z['realized_net']
 for seed,a in agg.items():diagnosis.append(dict(seed=seed,**a))
 dump('iteration5_diagnosis.json',dict(rows=diagnosis,first_eligible_outcome=609,first_allowed_scan=628,hard_min_delay=3,explanation='Sensor marginal and complete price paths identical under reversal. Earliest post-switch outcome signal606 available609. First scan628 uses signals606..625; 19 extra sessions are hard-coded. Frozen means and sensor/full agreement cannot detect reversed sign.'))
 rp=gzip.open(O/'replays.jsonl.gz','wt');op=gzip.open(O/'opportunities.jsonl.gz','wt')
 def run(seed,scenario,phase,change=None,paired=True):
  nonlocal count
  p,f,truth=x.generate(seed,scenario,change);base,models,oldalarms=x.e.predict(p,f)
  gate=x.Gate(p,f,models);states=copy.deepcopy(base['candidate'])
  variants=[('iteration6',states,gate)]
  if paired:variants.append(('iteration5',base['candidate'],None))
  for variant,ss,g in variants:
   if count>=64 or time.monotonic()-start>710:raise RuntimeError('Budget exhausted')
   count+=1;m,ts,ds=x.replay(p,ss,gate=g)
   change0=change if change is not None else x.START
   before=next((d['nav'] for d in ds if d['index']==change0-1),100000.)
   adverse_nav=[before]+[d['nav'] for d in ds if d['index']>=change0]+[m['final_nav']]
   peak=adverse_nav[0];dd=0.
   for v in adverse_nav:peak=max(peak,v);dd=max(dd,1-v/peak)
   m.update(adverse_return=m['final_nav']/before-1,adverse_mdd=dd)
   metrics.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,**m))
   sc=score(ss,truth,seed,scenario,variant,phase,change);scores.append(sc)
   for a,row in zip(x.e.TIERS,sc['confusion']):
    confusions.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,truth=a,**dict(zip(x.e.TIERS+['UNKNOWN'],row))))
   alarms=gate.events if g else oldalarms
   first=alarms[0]['index'] if alarms else None
   detection.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,change=change if scenario=='random_reversal' else x.START if scenario=='reversal' else None,first_detection=first,delay=(first-change0) if first is not None and scenario in ['reversal','random_reversal'] else None,false_alarm=bool(alarms) and scenario not in ['reversal','random_reversal'],events=alarms))
   err=max((abs(t['net']-x.e.observed(p,t['signal'],t['j'])) for t in ts),default=0)
   audits.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,min_cash=min(d['cash'] for d in ds),net_error=err,pnl_error=abs(m['final_nav']-100000-sum(t['debit']*t['net'] for t in ts)),horizon_ok=all(t['exit_index']==t['entry_index']+1 for t in ts),max_risk=m['max_modeled_risk'],gap_exceed=m['gap_loss_exceedances']))
   rp.write(json.dumps(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,trades=ts,daily=ds))+'\n')
   funded={(t['signal'],t['j']) for t in ts}
   for k,i in enumerate(range(x.START,x.END)):
    for j,z in enumerate(ss[k]):op.write(json.dumps(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,index=i,j=j,label=z['label'],truth=truth[i][j],realized=x.e.observed(p,i,j),funded=(i,j) in funded))+'\n')
  channels.append(dict(seed=seed,scenario=scenario,phase=phase,events=gate.events,trace=gate.trace))
  print(phase,seed,scenario,'replays',count,flush=True)
 # Design probes are separate and fixed: no threshold search or candidate selection.
 for seed in plan['design_seeds']:
  for scenario in ['learnable','reversal']:run(seed,scenario,'design',paired=False)
 for seed in old['seeds']:run(seed,'reversal','paired_regression')
 for seed in old['seeds'][:2]:run(seed,'learnable','paired_regression')
 sources={str(p.resolve()):x.e.sha(p) for p in sorted(O.glob('*.py'))}
 sources[str((O/'preregister.json').resolve())]=x.e.sha(O/'preregister.json')
 sources[str(Path(x.e.__file__).resolve())]=x.e.sha(x.e.__file__)
 dump('commitment.json',dict(utc=datetime.now(timezone.utc).isoformat(),sources=sources,pre_final_replays=count,public_timestamp=False))
 seeds=[secrets.randbits(63) for _ in range(4)];changes=[secrets.randbelow(61)+x.START+20 for _ in seeds];dump('seeds.json',dict(seeds=seeds,random_changes=changes))
 for seed,change in zip(seeds,changes):
  for scenario in plan['final_scenarios']:run(seed,scenario,'final',change if scenario=='random_reversal' else None)
 rp.close();op.close()
 final=[s for s in scores if s['phase']=='final' and s['variant']=='iteration6'];stable=[s for s in final if s['scenario'] in ['learnable','outer_noise']]
 det=[d for d in detection if d['phase']=='final' and d['variant']=='iteration6'];rev=[d for d in det if d['scenario'] in ['reversal','random_reversal']]
 improvements=[]
 for s in [s for s in scores if s['variant']=='iteration6']:
  b=next((b for b in scores if b['seed']==s['seed'] and b['scenario']==s['scenario'] and b['phase']==s['phase'] and b['variant']=='iteration5'),None)
  if b:improvements.append(dict(seed=s['seed'],scenario=s['scenario'],phase=s['phase'],false_great_delta=s['false_great']-b['false_great']))
 reversal_metrics=[m for m in metrics if m['phase']=='final' and m['variant']=='iteration6' and m['scenario'] in ['reversal','random_reversal']]
 checks=dict(stable_coverage=all(s['coverage']>=.15 for s in stable),stable_extreme_errors=all(max(s['false_great_rate'],s['false_terrible_rate'])<=.01 for s in stable),five_tier_support=all(min(s['support'])>=20 for s in stable if s['scenario']=='learnable'),null_abstention=all(s['coverage']==0 for s in final if s['scenario']=='null'),observed_false_alarm=not any(d['false_alarm'] for d in det),rapid_detection=all(d['delay'] is not None and 3<=d['delay']<=8 for d in rev),reversal_false_great_reduced=all(d['false_great_delta']<0 for d in improvements if d['scenario'] in ['reversal','random_reversal']),adverse_loss_limit=all(m['adverse_return']>=-.05 and m['adverse_mdd']<=.05 for m in reversal_metrics),accounting=all(a['min_cash']>=-1e-8 and a['net_error']<1e-12 and a['pnl_error']<1e-6 and a['horizon_ok'] and a['max_risk']<=.02+1e-12 for a in audits),frozen_hashes=all(x.e.sha(p)==h for p,h in sources.items()),budget=count<=64 and time.monotonic()-start<=720)
 dump('report.json',dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,portfolio_replays=count,elapsed_seconds=time.monotonic()-start,tests=6,diagnosis=diagnosis,discrimination=scores,detection=detection,portfolio=metrics,paired=improvements,channels=channels,audits=audits,blocker='Failed checks: '+', '.join(k for k,v in checks.items() if not v),limitations=['Four fresh seeds cannot establish <=5% population false alarm probability.','No safe zero-delay detection is identifiable from this DGP; first3 sessions remain exposed.','Model loss is per trade, not portfolio or realized gap cap.','Fresh seeds use inherited synthetic DGP; no real alpha or production readiness.','No independent sector data exists; market price breadth has exactly no switch information.','Local hash freeze only; no trusted public timestamp.']))
 csvout('confusion.csv',confusions);csvout('portfolio.csv',metrics);csvout('audit.csv',audits);csvout('paired.csv',improvements)
 dump('checksums.json',{p.name:x.e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'})
 print(checks,flush=True)
if __name__=='__main__':main()

```


## discrimination_iteration6/seeds.json

```
{
  "seeds": [
    2098214662956861329,
    2928371724749768812,
    5618266449171873643,
    8582935296371253491
  ],
  "random_changes": [
    658,
    646,
    634,
    676
  ]
}
```


## discrimination_iteration6/test_engine.py

```
import copy,unittest
import engine as x
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p,cls.f,_=x.generate(9182,'learnable');cls.ss,cls.models,_=x.e.predict(cls.p,cls.f)
 def test_future_invariance_and_maturity(self):
  now=x.START+8;p=copy.deepcopy(self.p);f=copy.deepcopy(self.f)
  for i in range(now,len(p)):p[i]=[v*.3 for v in p[i]]
  for i in range(now+1,len(f)):f[i]=[4-c for c in f[i]]
  a=x.Gate(self.p,self.f,self.models);b=x.Gate(p,f,self.models)
  self.assertEqual(a(now,self.ss['candidate'][8],[]),b(now,self.ss['candidate'][8],[]))
  self.assertEqual(a.trace,b.trace)
 def test_no_outcome_before_available(self):
  a=x.Gate(self.p,self.f,self.models);now=x.START+3
  t=dict(signal=now-2,net=-1,debit=100,j=0)
  a(now,self.ss['candidate'][3],[t]);self.assertEqual(a.trace[-1]['matured_fills'],0)
 def test_gating_and_null(self):
  a=x.Gate(self.p,self.f,self.models);a.latched=True
  self.assertTrue(all(z['label']=='UNKNOWN' for z in a(x.START,self.ss['candidate'][0],[])))
  p,f,_=x.generate(9182,'null');ss,_,_=x.e.predict(p,f)
  self.assertTrue(all(z['label']=='UNKNOWN' for row in ss['candidate'] for z in row))
 def test_stable_false_alarm_probe(self):
  a=x.Gate(self.p,self.f,self.models)
  for k,now in enumerate(range(x.START,x.END)):a(now,self.ss['candidate'][k],[])
  self.assertEqual(a.events,[])
 def test_accounting_cash_cost_risk_and_gap_three_replays(self):
  m,ts,ds=x.replay(self.p,copy.deepcopy(self.ss['candidate']))
  self.assertGreater(m['costs'],0);self.assertLessEqual(m['max_modeled_risk'],.02)
  self.assertTrue(all(d['cash']>=-1e-8 for d in ds))
  self.assertAlmostEqual(m['final_nav']-100000,sum(t['debit']*t['net'] for t in ts),places=7)
  for t in ts:
   self.assertEqual(t['exit_index'],t['entry_index']+1)
   self.assertAlmostEqual(t['net'],x.e.observed(self.p,t['signal'],t['j']))
  m,ts,_=x.replay(self.p,self.ss['candidate'],'cash');self.assertEqual(m['total_return'],0);self.assertEqual(m['costs'],0);self.assertEqual(ts,[])
  p=copy.deepcopy(self.p)
  for i in range(x.START+2,len(p)):p[i]=[v*.5 for v in p[i]]
  ss=[[dict(mean=.012,label='GREAT') for j in range(24)] for k in range(126)]
  m,_,_=x.replay(p,ss);self.assertGreater(m['gap_loss_exceedances'],0)
 def test_original_dgp_identity_and_uninformative_breadth(self):
  p,f,t=x.generate(3,'reversal');a,b,c=x.e.generate(3,'reversal');self.assertEqual((p,f,t),(a,b,c))
  q,_,_=x.generate(3,'learnable');self.assertEqual(p,q)
  r,_,_=x.generate(3,'random_reversal',650);self.assertEqual(p,r)
if __name__=='__main__':unittest.main()

```


## discrimination_iteration6/tests.log

```
test_accounting_cash_cost_risk_and_gap_three_replays (test_engine.Tests.test_accounting_cash_cost_risk_and_gap_three_replays) ... ok
test_future_invariance_and_maturity (test_engine.Tests.test_future_invariance_and_maturity) ... ok
test_gating_and_null (test_engine.Tests.test_gating_and_null) ... ok
test_no_outcome_before_available (test_engine.Tests.test_no_outcome_before_available) ... ok
test_original_dgp_identity_and_uninformative_breadth (test_engine.Tests.test_original_dgp_identity_and_uninformative_breadth) ... ok
test_stable_false_alarm_probe (test_engine.Tests.test_stable_false_alarm_probe) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.467s

OK

```


## discrimination_iteration6/opportunities.jsonl.gz exact ledger counts and samples
```json
{"group_counts":{"('design', 620101, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":734,"trades":0,"daily_rows":0},"('design', 620101, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":76,"trades":0,"daily_rows":0},"('design', 620102, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":717,"trades":0,"daily_rows":0},"('design', 620102, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":22,"trades":0,"daily_rows":0},"('paired_regression', 1564008556893530022, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":42,"trades":0,"daily_rows":0},"('paired_regression', 1564008556893530022, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":129,"trades":0,"daily_rows":0},"('paired_regression', 1634635432866334191, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":35,"trades":0,"daily_rows":0},"('paired_regression', 1634635432866334191, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":125,"trades":0,"daily_rows":0},"('paired_regression', 5015368413594993126, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":27,"trades":0,"daily_rows":0},"('paired_regression', 5015368413594993126, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":121,"trades":0,"daily_rows":0},"('paired_regression', 3584306075979195116, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":33,"trades":0,"daily_rows":0},"('paired_regression', 3584306075979195116, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":124,"trades":0,"daily_rows":0},"('paired_regression', 1564008556893530022, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":713,"trades":0,"daily_rows":0},"('paired_regression', 1564008556893530022, 'learnable', 'iteration5')":{"rows":3024,"funded_opportunities":713,"trades":0,"daily_rows":0},"('paired_regression', 1634635432866334191, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":711,"trades":0,"daily_rows":0},"('paired_regression', 1634635432866334191, 'learnable', 'iteration5')":{"rows":3024,"funded_opportunities":711,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":722,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'learnable', 'iteration5')":{"rows":3024,"funded_opportunities":722,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'null', 'iteration6')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'null', 'iteration5')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'outer_noise', 'iteration6')":{"rows":3024,"funded_opportunities":559,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'outer_noise', 'iteration5')":{"rows":3024,"funded_opportunities":559,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":30,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":125,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'random_reversal', 'iteration6')":{"rows":3024,"funded_opportunities":315,"trades":0,"daily_rows":0},"('final', 2098214662956861329, 'random_reversal', 'iteration5')":{"rows":3024,"funded_opportunities":396,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":717,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'learnable', 'iteration5')":{"rows":3024,"funded_opportunities":717,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'null', 'iteration6')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'null', 'iteration5')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'outer_noise', 'iteration6')":{"rows":3024,"funded_opportunities":716,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'outer_noise', 'iteration5')":{"rows":3024,"funded_opportunities":716,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":31,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":128,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'random_reversal', 'iteration6')":{"rows":3024,"funded_opportunities":244,"trades":0,"daily_rows":0},"('final', 2928371724749768812, 'random_reversal', 'iteration5')":{"rows":3024,"funded_opportunities":322,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":718,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'learnable', 'iteration5')":{"rows":3024,"funded_opportunities":718,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'null', 'iteration6')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'null', 'iteration5')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'outer_noise', 'iteration6')":{"rows":3024,"funded_opportunities":720,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'outer_noise', 'iteration5')":{"rows":3024,"funded_opportunities":720,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":29,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":125,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'random_reversal', 'iteration6')":{"rows":3024,"funded_opportunities":184,"trades":0,"daily_rows":0},"('final', 5618266449171873643, 'random_reversal', 'iteration5')":{"rows":3024,"funded_opportunities":264,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'learnable', 'iteration6')":{"rows":3024,"funded_opportunities":710,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'learnable', 'iteration5')":{"rows":3024,"funded_opportunities":710,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'null', 'iteration6')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'null', 'iteration5')":{"rows":3024,"funded_opportunities":0,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'outer_noise', 'iteration6')":{"rows":3024,"funded_opportunities":733,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'outer_noise', 'iteration5')":{"rows":3024,"funded_opportunities":733,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'reversal', 'iteration6')":{"rows":3024,"funded_opportunities":22,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'reversal', 'iteration5')":{"rows":3024,"funded_opportunities":129,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'random_reversal', 'iteration6')":{"rows":3024,"funded_opportunities":429,"trades":0,"daily_rows":0},"('final', 8582935296371253491, 'random_reversal', 'iteration5')":{"rows":3024,"funded_opportunities":479,"trades":0,"daily_rows":0}},"samples":{"('design', 620101, 'learnable', 'iteration6')|funded":{"source_line":1,"row":{"seed":620101,"scenario":"learnable","phase":"design","variant":"iteration6","index":606,"j":0,"label":"GREAT","truth":0.012,"realized":0.00030567454861119003,"funded":true}},"('design', 620101, 'learnable', 'iteration6')|AVERAGE":{"source_line":2,"row":{"seed":620101,"scenario":"learnable","phase":"design","variant":"iteration6","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":-0.0016231030854756412,"funded":false}},"('design', 620101, 'learnable', 'iteration6')|other":{"source_line":3,"row":{"seed":620101,"scenario":"learnable","phase":"design","variant":"iteration6","index":606,"j":2,"label":"TERRIBLE","truth":-0.012,"realized":-0.020316922115476865,"funded":false}},"('design', 620101, 'reversal', 'iteration6')|other":{"source_line":3025,"row":{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6","index":606,"j":0,"label":"TERRIBLE","truth":0.012,"realized":0.00030567454861119003,"funded":false}},"('design', 620101, 'reversal', 'iteration6')|AVERAGE":{"source_line":3026,"row":{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":-0.0016231030854756412,"funded":false}},"('design', 620101, 'reversal', 'iteration6')|false_GREAT":{"source_line":3027,"row":{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6","index":606,"j":2,"label":"GREAT","truth":-0.012,"realized":-0.020316922115476865,"funded":true}},"('design', 620101, 'reversal', 'iteration6')|funded":{"source_line":3084,"row":{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6","index":608,"j":11,"label":"GOOD","truth":-0.004,"realized":-0.007485821931066838,"funded":true}},"('design', 620102, 'learnable', 'iteration6')|funded":{"source_line":6049,"row":{"seed":620102,"scenario":"learnable","phase":"design","variant":"iteration6","index":606,"j":0,"label":"GREAT","truth":0.012,"realized":0.02340639938853828,"funded":true}},"('design', 620102, 'learnable', 'iteration6')|AVERAGE":{"source_line":6051,"row":{"seed":620102,"scenario":"learnable","phase":"design","variant":"iteration6","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.006154028907135012,"funded":false}},"('design', 620102, 'learnable', 'iteration6')|other":{"source_line":6057,"row":{"seed":620102,"scenario":"learnable","phase":"design","variant":"iteration6","index":606,"j":8,"label":"TERRIBLE","truth":-0.012,"realized":-0.020334566567720258,"funded":false}},"('design', 620102, 'reversal', 'iteration6')|other":{"source_line":9073,"row":{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6","index":606,"j":0,"label":"TERRIBLE","truth":0.012,"realized":0.02340639938853828,"funded":false}},"('design', 620102, 'reversal', 'iteration6')|AVERAGE":{"source_line":9075,"row":{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.006154028907135012,"funded":false}},"('design', 620102, 'reversal', 'iteration6')|false_GREAT":{"source_line":9081,"row":{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6","index":606,"j":8,"label":"GREAT","truth":-0.012,"realized":-0.020334566567720258,"funded":true}},"('design', 620102, 'reversal', 'iteration6')|funded":{"source_line":9082,"row":{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6","index":606,"j":9,"label":"GOOD","truth":-0.004,"realized":0.016454811638671574,"funded":true}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration6')|other":{"source_line":12097,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":0,"label":"POOR","truth":0.004,"realized":-0.00017168006808920833,"funded":false}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration6')|false_GREAT":{"source_line":12101,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":4,"label":"GREAT","truth":-0.012,"realized":-0.01754330334537213,"funded":true}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration6')|AVERAGE":{"source_line":12105,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":8,"label":"AVERAGE","truth":0,"realized":0.0023916107031118905,"funded":false}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration6')|funded":{"source_line":12106,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":9,"label":"GOOD","truth":-0.004,"realized":0.0019088709971941675,"funded":true}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration5')|other":{"source_line":15121,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":0,"label":"POOR","truth":0.004,"realized":-0.00017168006808920833,"funded":false}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration5')|false_GREAT":{"source_line":15125,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":4,"label":"GREAT","truth":-0.012,"realized":-0.01754330334537213,"funded":true}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration5')|AVERAGE":{"source_line":15129,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":8,"label":"AVERAGE","truth":0,"realized":0.0023916107031118905,"funded":false}},"('paired_regression', 1564008556893530022, 'reversal', 'iteration5')|funded":{"source_line":15130,"row":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":9,"label":"GOOD","truth":-0.004,"realized":0.0019088709971941675,"funded":true}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration6')|funded":{"source_line":18145,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":-0.004,"realized":0.01210381008565986,"funded":true}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration6')|other":{"source_line":18146,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":1,"label":"TERRIBLE","truth":0.012,"realized":0.015943195952868416,"funded":false}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration6')|false_GREAT":{"source_line":18149,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":4,"label":"GREAT","truth":-0.012,"realized":0.0011268766553573784,"funded":true}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration6')|AVERAGE":{"source_line":18155,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":10,"label":"AVERAGE","truth":0,"realized":-0.008637944296869926,"funded":false}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration5')|funded":{"source_line":21169,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":-0.004,"realized":0.01210381008565986,"funded":true}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration5')|other":{"source_line":21170,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":1,"label":"TERRIBLE","truth":0.012,"realized":0.015943195952868416,"funded":false}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration5')|false_GREAT":{"source_line":21173,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":4,"label":"GREAT","truth":-0.012,"realized":0.0011268766553573784,"funded":true}},"('paired_regression', 1634635432866334191, 'reversal', 'iteration5')|AVERAGE":{"source_line":21179,"row":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":10,"label":"AVERAGE","truth":0,"realized":-0.008637944296869926,"funded":false}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration6')|funded":{"source_line":24193,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":-0.004,"realized":-0.01494929802080136,"funded":true}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration6')|AVERAGE":{"source_line":24194,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":-0.008119028743839962,"funded":false}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration6')|other":{"source_line":24195,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":2,"label":"TERRIBLE","truth":0.012,"realized":0.017845065370593938,"funded":false}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration6')|false_GREAT":{"source_line":24196,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":3,"label":"GREAT","truth":-0.012,"realized":-0.01182537851322596,"funded":true}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration5')|funded":{"source_line":27217,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":-0.004,"realized":-0.01494929802080136,"funded":true}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration5')|AVERAGE":{"source_line":27218,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":-0.008119028743839962,"funded":false}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration5')|other":{"source_line":27219,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":2,"label":"TERRIBLE","truth":0.012,"realized":0.017845065370593938,"funded":false}},"('paired_regression', 5015368413594993126, 'reversal', 'iteration5')|false_GREAT":{"source_line":27220,"row":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":3,"label":"GREAT","truth":-0.012,"realized":-0.01182537851322596,"funded":true}},"('paired_regression', 3584306075979195116, 'reversal', 'iteration6')|false_GREAT":{"source_line":30241,"row":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.013697418181011778,"funded":true}},"('paired_regression', 3584306075979195116, 'reversal', 'iteration6')|funded":{"source_line":30242,"row":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":1,"label":"GOOD","truth":-0.004,"realized":-0.01887398901732984,"funded":true}},"('paired_regression', 3584306075979195116, 'reversal', 'iteration6')|other":{"source_line":30243,"row":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration6","index":606,"j":2,"label":"UNKNOWN","truth":0,"realized":-0.009413132454997863,"funded":false}},"('paired_regression', 3584306075979195116, 'reversal', 'iteration5')|false_GREAT":{"source_line":33265,"row":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.013697418181011778,"funded":true}},"('paired_regression', 3584306075979195116, 'reversal', 'iteration5')|funded":{"source_line":33266,"row":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":1,"label":"GOOD","truth":-0.004,"realized":-0.01887398901732984,"funded":true}},"('paired_regression', 3584306075979195116, 'reversal', 'iteration5')|other":{"source_line":33267,"row":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration5","index":606,"j":2,"label":"UNKNOWN","truth":0,"realized":-0.009413132454997863,"funded":false}},"('paired_regression', 1564008556893530022, 'learnable', 'iteration6')|funded":{"source_line":36289,"row":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":-0.00017168006808920833,"funded":true}},"('paired_regression', 1564008556893530022, 'learnable', 'iteration6')|other":{"source_line":36293,"row":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","index":606,"j":4,"label":"TERRIBLE","truth":-0.012,"realized":-0.01754330334537213,"funded":false}},"('paired_regression', 1564008556893530022, 'learnable', 'iteration6')|AVERAGE":{"source_line":36297,"row":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","index":606,"j":8,"label":"AVERAGE","truth":0,"realized":0.0023916107031118905,"funded":false}},"('paired_regression', 1564008556893530022, 'learnable', 'iteration5')|funded":{"source_line":39313,"row":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":-0.00017168006808920833,"funded":true}},"('paired_regression', 1564008556893530022, 'learnable', 'iteration5')|other":{"source_line":39317,"row":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","index":606,"j":4,"label":"TERRIBLE","truth":-0.012,"realized":-0.01754330334537213,"funded":false}},"('paired_regression', 1564008556893530022, 'learnable', 'iteration5')|AVERAGE":{"source_line":39321,"row":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","index":606,"j":8,"label":"AVERAGE","truth":0,"realized":0.0023916107031118905,"funded":false}},"('paired_regression', 1634635432866334191, 'learnable', 'iteration6')|other":{"source_line":42337,"row":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","index":606,"j":0,"label":"UNKNOWN","truth":-0.004,"realized":0.01210381008565986,"funded":false}},"('paired_regression', 1634635432866334191, 'learnable', 'iteration6')|funded":{"source_line":42338,"row":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","index":606,"j":1,"label":"GREAT","truth":0.012,"realized":0.015943195952868416,"funded":true}},"('paired_regression', 1634635432866334191, 'learnable', 'iteration6')|AVERAGE":{"source_line":42347,"row":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration6","index":606,"j":10,"label":"AVERAGE","truth":0,"realized":-0.008637944296869926,"funded":false}},"('paired_regression', 1634635432866334191, 'learnable', 'iteration5')|other":{"source_line":45361,"row":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","index":606,"j":0,"label":"UNKNOWN","truth":-0.004,"realized":0.01210381008565986,"funded":false}},"('paired_regression', 1634635432866334191, 'learnable', 'iteration5')|funded":{"source_line":45362,"row":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","index":606,"j":1,"label":"GREAT","truth":0.012,"realized":0.015943195952868416,"funded":true}},"('paired_regression', 1634635432866334191, 'learnable', 'iteration5')|AVERAGE":{"source_line":45371,"row":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration5","index":606,"j":10,"label":"AVERAGE","truth":0,"realized":-0.008637944296869926,"funded":false}},"('final', 2098214662956861329, 'learnable', 'iteration6')|funded":{"source_line":48385,"row":{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":-0.003960061662117154,"funded":true}},"('final', 2098214662956861329, 'learnable', 'iteration6')|other":{"source_line":48386,"row":{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":1,"label":"GOOD","truth":0.004,"realized":0.0017939381474929572,"funded":false}},"('final', 2098214662956861329, 'learnable', 'iteration5')|funded":{"source_line":51409,"row":{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":-0.003960061662117154,"funded":true}},"('final', 2098214662956861329, 'learnable', 'iteration5')|other":{"source_line":51410,"row":{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":1,"label":"GOOD","truth":0.004,"realized":0.0017939381474929572,"funded":false}},"('final', 2098214662956861329, 'null', 'iteration6')|other":{"source_line":54433,"row":{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration6","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":-0.003960061662117154,"funded":false}},"('final', 2098214662956861329, 'null', 'iteration5')|other":{"source_line":57457,"row":{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration5","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":-0.003960061662117154,"funded":false}},"('final', 2098214662956861329, 'outer_noise', 'iteration6')|other":{"source_line":60481,"row":{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":-0.005950077077646609,"funded":false}},"('final', 2098214662956861329, 'outer_noise', 'iteration6')|funded":{"source_line":60485,"row":{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":4,"label":"GREAT","truth":0.012,"realized":0.021504459741128468,"funded":true}},"('final', 2098214662956861329, 'outer_noise', 'iteration5')|other":{"source_line":63505,"row":{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":-0.005950077077646609,"funded":false}},"('final', 2098214662956861329, 'outer_noise', 'iteration5')|funded":{"source_line":63509,"row":{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":4,"label":"GREAT","truth":0.012,"realized":0.021504459741128468,"funded":true}},"('final', 2098214662956861329, 'reversal', 'iteration6')|other":{"source_line":66529,"row":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"POOR","truth":0.004,"realized":-0.003960061662117154,"funded":false}},"('final', 2098214662956861329, 'reversal', 'iteration6')|false_GREAT":{"source_line":66531,"row":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":2,"label":"GREAT","truth":-0.012,"realized":-0.016071971791440598,"funded":true}},"('final', 2098214662956861329, 'reversal', 'iteration6')|funded":{"source_line":66535,"row":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":6,"label":"GOOD","truth":-0.004,"realized":-0.016016281673552624,"funded":true}},"('final', 2098214662956861329, 'reversal', 'iteration5')|other":{"source_line":69553,"row":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"POOR","truth":0.004,"realized":-0.003960061662117154,"funded":false}},"('final', 2098214662956861329, 'reversal', 'iteration5')|false_GREAT":{"source_line":69555,"row":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":2,"label":"GREAT","truth":-0.012,"realized":-0.016071971791440598,"funded":true}},"('final', 2098214662956861329, 'reversal', 'iteration5')|funded":{"source_line":69559,"row":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":6,"label":"GOOD","truth":-0.004,"realized":-0.016016281673552624,"funded":true}},"('final', 2098214662956861329, 'random_reversal', 'iteration6')|funded":{"source_line":72577,"row":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":-0.003960061662117154,"funded":true}},"('final', 2098214662956861329, 'random_reversal', 'iteration6')|other":{"source_line":72578,"row":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":1,"label":"GOOD","truth":0.004,"realized":0.0017939381474929572,"funded":false}},"('final', 2098214662956861329, 'random_reversal', 'iteration6')|false_GREAT":{"source_line":73827,"row":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":658,"j":2,"label":"GREAT","truth":-0.012,"realized":-0.020078642433302152,"funded":true}},"('final', 2098214662956861329, 'random_reversal', 'iteration5')|funded":{"source_line":75601,"row":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":-0.003960061662117154,"funded":true}},"('final', 2098214662956861329, 'random_reversal', 'iteration5')|other":{"source_line":75602,"row":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":1,"label":"GOOD","truth":0.004,"realized":0.0017939381474929572,"funded":false}},"('final', 2098214662956861329, 'random_reversal', 'iteration5')|false_GREAT":{"source_line":76851,"row":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":658,"j":2,"label":"GREAT","truth":-0.012,"realized":-0.020078642433302152,"funded":true}},"('final', 2928371724749768812, 'learnable', 'iteration6')|funded":{"source_line":78625,"row":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.0060010614516330385,"funded":true}},"('final', 2928371724749768812, 'learnable', 'iteration6')|other":{"source_line":78627,"row":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":2,"label":"TERRIBLE","truth":-0.012,"realized":-0.0023633046038613603,"funded":false}},"('final', 2928371724749768812, 'learnable', 'iteration6')|AVERAGE":{"source_line":78629,"row":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":4,"label":"AVERAGE","truth":0,"realized":0.004666479365936116,"funded":false}},"('final', 2928371724749768812, 'learnable', 'iteration5')|funded":{"source_line":81649,"row":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.0060010614516330385,"funded":true}},"('final', 2928371724749768812, 'learnable', 'iteration5')|other":{"source_line":81651,"row":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":2,"label":"TERRIBLE","truth":-0.012,"realized":-0.0023633046038613603,"funded":false}},"('final', 2928371724749768812, 'learnable', 'iteration5')|AVERAGE":{"source_line":81653,"row":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":4,"label":"AVERAGE","truth":0,"realized":0.004666479365936116,"funded":false}},"('final', 2928371724749768812, 'null', 'iteration6')|other":{"source_line":84673,"row":{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration6","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":0.0060010614516330385,"funded":false}},"('final', 2928371724749768812, 'null', 'iteration5')|other":{"source_line":87697,"row":{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration5","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":0.0060010614516330385,"funded":false}},"('final', 2928371724749768812, 'outer_noise', 'iteration6')|funded":{"source_line":90721,"row":{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.006501326814541297,"funded":true}},"('final', 2928371724749768812, 'outer_noise', 'iteration6')|other":{"source_line":90723,"row":{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":2,"label":"TERRIBLE","truth":-0.012,"realized":4.586924517324675e-05,"funded":false}},"('final', 2928371724749768812, 'outer_noise', 'iteration5')|funded":{"source_line":93745,"row":{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.006501326814541297,"funded":true}},"('final', 2928371724749768812, 'outer_noise', 'iteration5')|other":{"source_line":93747,"row":{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":2,"label":"TERRIBLE","truth":-0.012,"realized":4.586924517324675e-05,"funded":false}},"('final', 2928371724749768812, 'reversal', 'iteration6')|other":{"source_line":96769,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"POOR","truth":0.004,"realized":0.0060010614516330385,"funded":false}},"('final', 2928371724749768812, 'reversal', 'iteration6')|false_GREAT":{"source_line":96771,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":2,"label":"GREAT","truth":-0.012,"realized":-0.0023633046038613603,"funded":true}},"('final', 2928371724749768812, 'reversal', 'iteration6')|AVERAGE":{"source_line":96773,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":4,"label":"AVERAGE","truth":0,"realized":0.004666479365936116,"funded":false}},"('final', 2928371724749768812, 'reversal', 'iteration6')|funded":{"source_line":96776,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":7,"label":"GOOD","truth":-0.004,"realized":-0.0057126283245105824,"funded":true}},"('final', 2928371724749768812, 'reversal', 'iteration5')|other":{"source_line":99793,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"POOR","truth":0.004,"realized":0.0060010614516330385,"funded":false}},"('final', 2928371724749768812, 'reversal', 'iteration5')|false_GREAT":{"source_line":99795,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":2,"label":"GREAT","truth":-0.012,"realized":-0.0023633046038613603,"funded":true}},"('final', 2928371724749768812, 'reversal', 'iteration5')|AVERAGE":{"source_line":99797,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":4,"label":"AVERAGE","truth":0,"realized":0.004666479365936116,"funded":false}},"('final', 2928371724749768812, 'reversal', 'iteration5')|funded":{"source_line":99800,"row":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":7,"label":"GOOD","truth":-0.004,"realized":-0.0057126283245105824,"funded":true}},"('final', 2928371724749768812, 'random_reversal', 'iteration6')|funded":{"source_line":102817,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.0060010614516330385,"funded":true}},"('final', 2928371724749768812, 'random_reversal', 'iteration6')|other":{"source_line":102819,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":2,"label":"TERRIBLE","truth":-0.012,"realized":-0.0023633046038613603,"funded":false}},"('final', 2928371724749768812, 'random_reversal', 'iteration6')|AVERAGE":{"source_line":102821,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":4,"label":"AVERAGE","truth":0,"realized":0.004666479365936116,"funded":false}},"('final', 2928371724749768812, 'random_reversal', 'iteration6')|false_GREAT":{"source_line":103777,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":646,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.01849252107149557,"funded":true}},"('final', 2928371724749768812, 'random_reversal', 'iteration5')|funded":{"source_line":105841,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.0060010614516330385,"funded":true}},"('final', 2928371724749768812, 'random_reversal', 'iteration5')|other":{"source_line":105843,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":2,"label":"TERRIBLE","truth":-0.012,"realized":-0.0023633046038613603,"funded":false}},"('final', 2928371724749768812, 'random_reversal', 'iteration5')|AVERAGE":{"source_line":105845,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":4,"label":"AVERAGE","truth":0,"realized":0.004666479365936116,"funded":false}},"('final', 2928371724749768812, 'random_reversal', 'iteration5')|false_GREAT":{"source_line":106801,"row":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":646,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.01849252107149557,"funded":true}},"('final', 5618266449171873643, 'learnable', 'iteration6')|funded":{"source_line":108865,"row":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.00861970093494846,"funded":true}},"('final', 5618266449171873643, 'learnable', 'iteration6')|AVERAGE":{"source_line":108867,"row":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.007276165801398893,"funded":false}},"('final', 5618266449171873643, 'learnable', 'iteration6')|other":{"source_line":108868,"row":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":3,"label":"POOR","truth":-0.004,"realized":0.002554624004192263,"funded":false}},"('final', 5618266449171873643, 'learnable', 'iteration5')|funded":{"source_line":111889,"row":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.00861970093494846,"funded":true}},"('final', 5618266449171873643, 'learnable', 'iteration5')|AVERAGE":{"source_line":111891,"row":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.007276165801398893,"funded":false}},"('final', 5618266449171873643, 'learnable', 'iteration5')|other":{"source_line":111892,"row":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":3,"label":"POOR","truth":-0.004,"realized":0.002554624004192263,"funded":false}},"('final', 5618266449171873643, 'null', 'iteration6')|other":{"source_line":114913,"row":{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration6","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":0.00861970093494846,"funded":false}},"('final', 5618266449171873643, 'null', 'iteration5')|other":{"source_line":117937,"row":{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration5","index":606,"j":0,"label":"UNKNOWN","truth":0.004,"realized":0.00861970093494846,"funded":false}},"('final', 5618266449171873643, 'outer_noise', 'iteration6')|funded":{"source_line":120961,"row":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.009774626168685518,"funded":true}},"('final', 5618266449171873643, 'outer_noise', 'iteration6')|AVERAGE":{"source_line":120963,"row":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.009095207251748505,"funded":false}},"('final', 5618266449171873643, 'outer_noise', 'iteration6')|other":{"source_line":120964,"row":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":3,"label":"POOR","truth":-0.004,"realized":0.0041932800052399966,"funded":false}},"('final', 5618266449171873643, 'outer_noise', 'iteration5')|funded":{"source_line":123985,"row":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.009774626168685518,"funded":true}},"('final', 5618266449171873643, 'outer_noise', 'iteration5')|AVERAGE":{"source_line":123987,"row":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.009095207251748505,"funded":false}},"('final', 5618266449171873643, 'outer_noise', 'iteration5')|other":{"source_line":123988,"row":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":3,"label":"POOR","truth":-0.004,"realized":0.0041932800052399966,"funded":false}},"('final', 5618266449171873643, 'reversal', 'iteration6')|other":{"source_line":127009,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"POOR","truth":0.004,"realized":0.00861970093494846,"funded":false}},"('final', 5618266449171873643, 'reversal', 'iteration6')|AVERAGE":{"source_line":127011,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.007276165801398893,"funded":false}},"('final', 5618266449171873643, 'reversal', 'iteration6')|funded":{"source_line":127012,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":3,"label":"GOOD","truth":-0.004,"realized":0.002554624004192263,"funded":true}},"('final', 5618266449171873643, 'reversal', 'iteration6')|false_GREAT":{"source_line":127023,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":14,"label":"GREAT","truth":-0.012,"realized":-0.02548161607520416,"funded":true}},"('final', 5618266449171873643, 'reversal', 'iteration5')|other":{"source_line":130033,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"POOR","truth":0.004,"realized":0.00861970093494846,"funded":false}},"('final', 5618266449171873643, 'reversal', 'iteration5')|AVERAGE":{"source_line":130035,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.007276165801398893,"funded":false}},"('final', 5618266449171873643, 'reversal', 'iteration5')|funded":{"source_line":130036,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":3,"label":"GOOD","truth":-0.004,"realized":0.002554624004192263,"funded":true}},"('final', 5618266449171873643, 'reversal', 'iteration5')|false_GREAT":{"source_line":130047,"row":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":14,"label":"GREAT","truth":-0.012,"realized":-0.02548161607520416,"funded":true}},"('final', 5618266449171873643, 'random_reversal', 'iteration6')|funded":{"source_line":133057,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.00861970093494846,"funded":true}},"('final', 5618266449171873643, 'random_reversal', 'iteration6')|AVERAGE":{"source_line":133059,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.007276165801398893,"funded":false}},"('final', 5618266449171873643, 'random_reversal', 'iteration6')|other":{"source_line":133060,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":3,"label":"POOR","truth":-0.004,"realized":0.002554624004192263,"funded":false}},"('final', 5618266449171873643, 'random_reversal', 'iteration6')|false_GREAT":{"source_line":133729,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":634,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.018634305630034542,"funded":true}},"('final', 5618266449171873643, 'random_reversal', 'iteration5')|funded":{"source_line":136081,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GOOD","truth":0.004,"realized":0.00861970093494846,"funded":true}},"('final', 5618266449171873643, 'random_reversal', 'iteration5')|AVERAGE":{"source_line":136083,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":2,"label":"AVERAGE","truth":0,"realized":-0.007276165801398893,"funded":false}},"('final', 5618266449171873643, 'random_reversal', 'iteration5')|other":{"source_line":136084,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":3,"label":"POOR","truth":-0.004,"realized":0.002554624004192263,"funded":false}},"('final', 5618266449171873643, 'random_reversal', 'iteration5')|false_GREAT":{"source_line":136753,"row":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":634,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.018634305630034542,"funded":true}},"('final', 8582935296371253491, 'learnable', 'iteration6')|other":{"source_line":139105,"row":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":0,"label":"TERRIBLE","truth":-0.012,"realized":-0.012206141160580497,"funded":false}},"('final', 8582935296371253491, 'learnable', 'iteration6')|AVERAGE":{"source_line":139106,"row":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.0150430601052296,"funded":false}},"('final', 8582935296371253491, 'learnable', 'iteration6')|funded":{"source_line":139107,"row":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration6","index":606,"j":2,"label":"GREAT","truth":0.012,"realized":0.013436925742521533,"funded":true}},"('final', 8582935296371253491, 'learnable', 'iteration5')|other":{"source_line":142129,"row":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":0,"label":"TERRIBLE","truth":-0.012,"realized":-0.012206141160580497,"funded":false}},"('final', 8582935296371253491, 'learnable', 'iteration5')|AVERAGE":{"source_line":142130,"row":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.0150430601052296,"funded":false}},"('final', 8582935296371253491, 'learnable', 'iteration5')|funded":{"source_line":142131,"row":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration5","index":606,"j":2,"label":"GREAT","truth":0.012,"realized":0.013436925742521533,"funded":true}},"('final', 8582935296371253491, 'null', 'iteration6')|other":{"source_line":145153,"row":{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration6","index":606,"j":0,"label":"UNKNOWN","truth":-0.012,"realized":-0.012206141160580497,"funded":false}},"('final', 8582935296371253491, 'null', 'iteration5')|other":{"source_line":148177,"row":{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration5","index":606,"j":0,"label":"UNKNOWN","truth":-0.012,"realized":-0.012206141160580497,"funded":false}},"('final', 8582935296371253491, 'outer_noise', 'iteration6')|other":{"source_line":151201,"row":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":0,"label":"TERRIBLE","truth":-0.012,"realized":-0.012257676450725508,"funded":false}},"('final', 8582935296371253491, 'outer_noise', 'iteration6')|AVERAGE":{"source_line":151202,"row":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.018803825131537,"funded":false}},"('final', 8582935296371253491, 'outer_noise', 'iteration6')|funded":{"source_line":151203,"row":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration6","index":606,"j":2,"label":"GREAT","truth":0.012,"realized":0.013796157178151747,"funded":true}},"('final', 8582935296371253491, 'outer_noise', 'iteration5')|other":{"source_line":154225,"row":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":0,"label":"TERRIBLE","truth":-0.012,"realized":-0.012257676450725508,"funded":false}},"('final', 8582935296371253491, 'outer_noise', 'iteration5')|AVERAGE":{"source_line":154226,"row":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.018803825131537,"funded":false}},"('final', 8582935296371253491, 'outer_noise', 'iteration5')|funded":{"source_line":154227,"row":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration5","index":606,"j":2,"label":"GREAT","truth":0.012,"realized":0.013796157178151747,"funded":true}},"('final', 8582935296371253491, 'reversal', 'iteration6')|false_GREAT":{"source_line":157249,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.012206141160580497,"funded":true}},"('final', 8582935296371253491, 'reversal', 'iteration6')|AVERAGE":{"source_line":157250,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.0150430601052296,"funded":false}},"('final', 8582935296371253491, 'reversal', 'iteration6')|other":{"source_line":157251,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":2,"label":"TERRIBLE","truth":0.012,"realized":0.013436925742521533,"funded":false}},"('final', 8582935296371253491, 'reversal', 'iteration6')|funded":{"source_line":157255,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6","index":606,"j":6,"label":"GOOD","truth":-0.004,"realized":0.009164643926433014,"funded":true}},"('final', 8582935296371253491, 'reversal', 'iteration5')|false_GREAT":{"source_line":160273,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"GREAT","truth":-0.012,"realized":-0.012206141160580497,"funded":true}},"('final', 8582935296371253491, 'reversal', 'iteration5')|AVERAGE":{"source_line":160274,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.0150430601052296,"funded":false}},"('final', 8582935296371253491, 'reversal', 'iteration5')|other":{"source_line":160275,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":2,"label":"TERRIBLE","truth":0.012,"realized":0.013436925742521533,"funded":false}},"('final', 8582935296371253491, 'reversal', 'iteration5')|funded":{"source_line":160279,"row":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5","index":606,"j":6,"label":"GOOD","truth":-0.004,"realized":0.009164643926433014,"funded":true}},"('final', 8582935296371253491, 'random_reversal', 'iteration6')|other":{"source_line":163297,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":0,"label":"TERRIBLE","truth":-0.012,"realized":-0.012206141160580497,"funded":false}},"('final', 8582935296371253491, 'random_reversal', 'iteration6')|AVERAGE":{"source_line":163298,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.0150430601052296,"funded":false}},"('final', 8582935296371253491, 'random_reversal', 'iteration6')|funded":{"source_line":163299,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":606,"j":2,"label":"GREAT","truth":0.012,"realized":0.013436925742521533,"funded":true}},"('final', 8582935296371253491, 'random_reversal', 'iteration6')|false_GREAT":{"source_line":164983,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6","index":676,"j":6,"label":"GREAT","truth":-0.012,"realized":-0.011770219152809513,"funded":true}},"('final', 8582935296371253491, 'random_reversal', 'iteration5')|other":{"source_line":166321,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":0,"label":"TERRIBLE","truth":-0.012,"realized":-0.012206141160580497,"funded":false}},"('final', 8582935296371253491, 'random_reversal', 'iteration5')|AVERAGE":{"source_line":166322,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":1,"label":"AVERAGE","truth":0,"realized":0.0150430601052296,"funded":false}},"('final', 8582935296371253491, 'random_reversal', 'iteration5')|funded":{"source_line":166323,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":606,"j":2,"label":"GREAT","truth":0.012,"realized":0.013436925742521533,"funded":true}},"('final', 8582935296371253491, 'random_reversal', 'iteration5')|false_GREAT":{"source_line":168007,"row":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5","index":676,"j":6,"label":"GREAT","truth":-0.012,"realized":-0.011770219152809513,"funded":true}}}}
```

## discrimination_iteration6/replays.jsonl.gz exact ledger counts and samples
```json
{"group_counts":{"('design', 620101, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":734,"daily_rows":126},"('design', 620101, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":76,"daily_rows":126},"('design', 620102, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":717,"daily_rows":126},"('design', 620102, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":22,"daily_rows":126},"('paired_regression', 1564008556893530022, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":42,"daily_rows":126},"('paired_regression', 1564008556893530022, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":129,"daily_rows":126},"('paired_regression', 1634635432866334191, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":35,"daily_rows":126},"('paired_regression', 1634635432866334191, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":125,"daily_rows":126},"('paired_regression', 5015368413594993126, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":27,"daily_rows":126},"('paired_regression', 5015368413594993126, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":121,"daily_rows":126},"('paired_regression', 3584306075979195116, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":33,"daily_rows":126},"('paired_regression', 3584306075979195116, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":124,"daily_rows":126},"('paired_regression', 1564008556893530022, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":713,"daily_rows":126},"('paired_regression', 1564008556893530022, 'learnable', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":713,"daily_rows":126},"('paired_regression', 1634635432866334191, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":711,"daily_rows":126},"('paired_regression', 1634635432866334191, 'learnable', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":711,"daily_rows":126},"('final', 2098214662956861329, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":722,"daily_rows":126},"('final', 2098214662956861329, 'learnable', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":722,"daily_rows":126},"('final', 2098214662956861329, 'null', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 2098214662956861329, 'null', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 2098214662956861329, 'outer_noise', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":559,"daily_rows":126},"('final', 2098214662956861329, 'outer_noise', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":559,"daily_rows":126},"('final', 2098214662956861329, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":30,"daily_rows":126},"('final', 2098214662956861329, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":125,"daily_rows":126},"('final', 2098214662956861329, 'random_reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":315,"daily_rows":126},"('final', 2098214662956861329, 'random_reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":396,"daily_rows":126},"('final', 2928371724749768812, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":717,"daily_rows":126},"('final', 2928371724749768812, 'learnable', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":717,"daily_rows":126},"('final', 2928371724749768812, 'null', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 2928371724749768812, 'null', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 2928371724749768812, 'outer_noise', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":716,"daily_rows":126},"('final', 2928371724749768812, 'outer_noise', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":716,"daily_rows":126},"('final', 2928371724749768812, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":31,"daily_rows":126},"('final', 2928371724749768812, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":128,"daily_rows":126},"('final', 2928371724749768812, 'random_reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":244,"daily_rows":126},"('final', 2928371724749768812, 'random_reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":322,"daily_rows":126},"('final', 5618266449171873643, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":718,"daily_rows":126},"('final', 5618266449171873643, 'learnable', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":718,"daily_rows":126},"('final', 5618266449171873643, 'null', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 5618266449171873643, 'null', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 5618266449171873643, 'outer_noise', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":720,"daily_rows":126},"('final', 5618266449171873643, 'outer_noise', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":720,"daily_rows":126},"('final', 5618266449171873643, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":29,"daily_rows":126},"('final', 5618266449171873643, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":125,"daily_rows":126},"('final', 5618266449171873643, 'random_reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":184,"daily_rows":126},"('final', 5618266449171873643, 'random_reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":264,"daily_rows":126},"('final', 8582935296371253491, 'learnable', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":710,"daily_rows":126},"('final', 8582935296371253491, 'learnable', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":710,"daily_rows":126},"('final', 8582935296371253491, 'null', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 8582935296371253491, 'null', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":0,"daily_rows":126},"('final', 8582935296371253491, 'outer_noise', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":733,"daily_rows":126},"('final', 8582935296371253491, 'outer_noise', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":733,"daily_rows":126},"('final', 8582935296371253491, 'reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":22,"daily_rows":126},"('final', 8582935296371253491, 'reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":129,"daily_rows":126},"('final', 8582935296371253491, 'random_reversal', 'iteration6')":{"rows":1,"funded_opportunities":0,"trades":429,"daily_rows":126},"('final', 8582935296371253491, 'random_reversal', 'iteration5')":{"rows":1,"funded_opportunities":0,"trades":479,"daily_rows":126}},"samples":{"('design', 620101, 'learnable', 'iteration6')":{"source_line":1,"metadata":{"seed":620101,"scenario":"learnable","phase":"design","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":22,"entry_index":607,"entry_open":865.6646756976114,"shares":11.53451532286903,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":880.8562482375146,"net":0.014500951770172854,"realized_loss_nav":0.0},{"signal":606,"j":0,"entry_index":607,"entry_open":278.7050495097554,"shares":35.82648568393106,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":279.6278697183624,"net":0.000305674548610968,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":8,"entry_index":732,"entry_open":1233.421049493561,"shares":0.8005805226640932,"debit":988.9340477711521,"entry_nav":187569.8194563567,"modeled_risk":0.00017372701404684592,"tier":"GREAT","exit_index":733,"exit_open":1264.1734996766502,"net":0.02186245317889557,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":187455.9649453777,"cash":0.0,"receivable":111552.95762604287,"exposure":0.4049111338839071}]},"('design', 620101, 'reversal', 'iteration6')":{"source_line":2,"metadata":{"seed":620101,"scenario":"reversal","phase":"design","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":2,"entry_index":607,"entry_open":727.5007162208389,"shares":13.725103279856445,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":714.8615133116396,"net":-0.020316922115476865,"realized_loss_nav":0.002031692211547688},{"signal":606,"j":15,"entry_index":607,"entry_open":644.6401736316343,"shares":12.748391773925013,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":635.2964596822159,"net":-0.017446552722374387,"realized_loss_nav":0.0014359302652160021}],"trades_last_1":[{"signal":619,"j":22,"entry_index":620,"entry_open":895.8087861823833,"shares":7.56844783525952,"debit":6790.051891691401,"entry_nav":94229.1436193508,"modeled_risk":0.008849974247936744,"tier":"GOOD","exit_index":621,"exit_open":895.4755792204971,"net":-0.0033663546745279493,"realized_loss_nav":0.00024257593827042473}],"daily_first_1":[{"index":606,"nav":99915.43548874218,"cash":43539.09465020575,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":93561.05353826373,"cash":93561.05353826373,"receivable":0.0,"exposure":0.0}]},"('design', 620102, 'learnable', 'iteration6')":{"source_line":3,"metadata":{"seed":620102,"scenario":"learnable","phase":"design","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":18,"entry_index":607,"entry_open":469.1245606955018,"shares":21.284373709825015,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":489.6111940167109,"net":0.040543602452636884,"realized_loss_nav":0.0},{"signal":606,"j":6,"entry_index":607,"entry_open":537.1283363711601,"shares":18.58964011051693,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":553.8898128472288,"net":0.02811673632889944,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":0,"entry_index":732,"entry_open":1015.0427128260595,"shares":3.1871058775970638,"debit":3239.901168954093,"entry_nav":193787.02155866107,"modeled_risk":0.0005508965606226829,"tier":"GOOD","exit_index":733,"exit_open":1030.333814257557,"net":0.012023858102061524,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99900.45795504274,"cash":33539.09465020576,"receivable":0.0,"exposure":0.664274865833958}],"daily_last_1":[{"index":731,"nav":193637.04640347144,"cash":0.0,"receivable":93653.60961037644,"exposure":0.5163445665493405}]},"('design', 620102, 'reversal', 'iteration6')":{"source_line":4,"metadata":{"seed":620102,"scenario":"reversal","phase":"design","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":12,"entry_index":607,"entry_open":575.3961574218359,"shares":17.35330056954187,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":577.589118918504,"net":0.0008042969910226905,"realized_loss_nav":0.0},{"signal":606,"j":20,"entry_index":607,"entry_open":913.0409226427528,"shares":10.936007596898706,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":902.9318809395706,"net":-0.014034179542697367,"realized_loss_nav":0.0014034179542697347}],"trades_last_1":[{"signal":609,"j":0,"entry_index":610,"entry_open":604.4584521922532,"shares":6.107434337351231,"debit":3697.2278418807764,"entry_nav":98521.3744403579,"modeled_risk":0.0012365416215914416,"tier":"GREAT","exit_index":611,"exit_open":593.9261176890419,"net":-0.020367726097789363,"realized_loss_nav":0.0007643430111720135}],"daily_first_1":[{"index":606,"nav":99882.83007587385,"cash":21769.54732510288,"receivable":0.0,"exposure":0.7820491539079728}],"daily_last_1":[{"index":731,"nav":98316.81855179259,"cash":98316.81855179259,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 1564008556893530022, 'reversal', 'iteration6')":{"source_line":5,"metadata":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":790.2736236326258,"shares":12.634892735509395,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":793.7442787865415,"net":0.001383051115938061,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":952.3234797834983,"shares":10.48490631415551,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":952.9761446557808,"net":-0.002312220205354265,"realized_loss_nav":0.00023122202053542425}],"trades_last_1":[{"signal":612,"j":11,"entry_index":613,"entry_open":795.7584135502652,"shares":4.641182261106382,"debit":3698.7997228452914,"entry_nav":97726.57356656046,"modeled_risk":0.009183399219773023,"tier":"GREAT","exit_index":614,"exit_open":800.3860071133547,"net":0.0028023981227145445,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99910.13479780329,"cash":40000.0,"receivable":0.0,"exposure":0.5996402158704777}],"daily_last_1":[{"index":731,"nav":97394.46246879271,"cash":97394.46246879271,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 1564008556893530022, 'reversal', 'iteration5')":{"source_line":6,"metadata":{"seed":1564008556893530022,"scenario":"reversal","phase":"paired_regression","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":790.2736236326258,"shares":12.634892735509395,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":793.7442787865415,"net":0.001383051115938061,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":952.3234797834983,"shares":10.48490631415551,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":952.9761446557808,"net":-0.002312220205354265,"realized_loss_nav":0.00023122202053542425}],"trades_last_1":[{"signal":627,"j":14,"entry_index":628,"entry_open":645.3494262806063,"shares":7.5728288373147,"debit":4894.451426600495,"entry_nav":90918.63988725201,"modeled_risk":0.006611579896485054,"tier":"GOOD","exit_index":629,"exit_open":645.169651044318,"net":-0.0032732426625657896,"realized_loss_nav":0.00017620949058710103}],"daily_first_1":[{"index":606,"nav":99910.13479780329,"cash":40000.0,"receivable":0.0,"exposure":0.5996402158704777}],"daily_last_1":[{"index":731,"nav":90664.61234282482,"cash":90664.61234282482,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 1634635432866334191, 'reversal', 'iteration6')":{"source_line":7,"metadata":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":438.18199861551153,"shares":22.787386286633,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":435.67470480647506,"net":-0.00870040379506587,"realized_loss_nav":0.0008700403795065904},{"signal":606,"j":4,"entry_index":607,"entry_open":423.63640582131393,"shares":23.56979317427252,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":425.3880445519174,"net":0.0011268766553571563,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":611,"j":12,"entry_index":612,"entry_open":800.7127232836381,"shares":2.270601042726441,"debit":1820.8262931287754,"entry_nav":96963.6875421532,"modeled_risk":0.0006187602110276433,"tier":"GREAT","exit_index":613,"exit_open":796.1988637545537,"net":-0.00861592227916963,"realized_loss_nav":0.0001617935355299466}],"daily_first_1":[{"index":606,"nav":99867.8525421744,"cash":11769.547325102882,"receivable":0.0,"exposure":0.882148789370107}],"daily_last_1":[{"index":731,"nav":96811.31927868878,"cash":96811.31927868878,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 1634635432866334191, 'reversal', 'iteration5')":{"source_line":8,"metadata":{"seed":1634635432866334191,"scenario":"reversal","phase":"paired_regression","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":6,"entry_index":607,"entry_open":438.18199861551153,"shares":22.787386286633,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":435.67470480647506,"net":-0.00870040379506587,"realized_loss_nav":0.0008700403795065904},{"signal":606,"j":4,"entry_index":607,"entry_open":423.63640582131393,"shares":23.56979317427252,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":425.3880445519174,"net":0.0011268766553571563,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":627,"j":9,"entry_index":628,"entry_open":798.0029210962279,"shares":4.393099128059916,"debit":3510.9644957623905,"entry_nav":89068.44487885298,"modeled_risk":0.0024796601571117696,"tier":"GOOD","exit_index":629,"exit_open":784.0318765664305,"net":-0.02045057338627576,"realized_loss_nav":0.0008061355194295634}],"daily_first_1":[{"index":606,"nav":99867.8525421744,"cash":11769.547325102882,"receivable":0.0,"exposure":0.882148789370107}],"daily_last_1":[{"index":731,"nav":88391.093403871,"cash":88391.093403871,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 5015368413594993126, 'reversal', 'iteration6')":{"source_line":9,"metadata":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":450.8029533031123,"shares":18.229972599894193,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":446.81046149428244,"net":-0.01182537851322596,"realized_loss_nav":0.0009732821821585185},{"signal":606,"j":0,"entry_index":607,"entry_open":391.6073397823145,"shares":25.497536567754302,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GOOD","exit_index":608,"exit_open":386.91208270426097,"net":-0.014949298020801471,"realized_loss_nav":0.0014949298020801507}],"trades_last_1":[{"signal":610,"j":12,"entry_index":611,"entry_open":476.0607889297435,"shares":0.0755082438454429,"debit":36.000433906964645,"entry_nav":97915.76204854598,"modeled_risk":1.211485200811679e-05,"tier":"GREAT","exit_index":612,"exit_open":467.26093730645226,"net":-0.021424858227055976,"realized_loss_nav":7.877221975628507e-06}],"daily_first_1":[{"index":606,"nav":99942.74021067165,"cash":61769.547325102874,"receivable":0.0,"exposure":0.3819506329834723}],"daily_last_1":[{"index":731,"nav":97599.77217704186,"cash":97599.77217704186,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 5015368413594993126, 'reversal', 'iteration5')":{"source_line":10,"metadata":{"seed":5015368413594993126,"scenario":"reversal","phase":"paired_regression","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":450.8029533031123,"shares":18.229972599894193,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":446.81046149428244,"net":-0.01182537851322596,"realized_loss_nav":0.0009732821821585185},{"signal":606,"j":0,"entry_index":607,"entry_open":391.6073397823145,"shares":25.497536567754302,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GOOD","exit_index":608,"exit_open":386.91208270426097,"net":-0.014949298020801471,"realized_loss_nav":0.0014949298020801507}],"trades_last_1":[{"signal":627,"j":5,"entry_index":628,"entry_open":499.1677912386911,"shares":3.565095821706035,"debit":1782.250378385601,"entry_nav":90226.2174267396,"modeled_risk":0.0012425834378369603,"tier":"GOOD","exit_index":629,"exit_open":501.06671252745883,"net":0.0007972721422382367,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99942.74021067165,"cash":61769.547325102874,"receivable":0.0,"exposure":0.3819506329834723}],"daily_last_1":[{"index":731,"nav":90067.68136556458,"cash":90067.68136556458,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 3584306075979195116, 'reversal', 'iteration6')":{"source_line":11,"metadata":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":0,"entry_index":607,"entry_open":571.6147652251367,"shares":17.468097526080943,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":565.4790149479502,"net":-0.013697418181011778,"realized_loss_nav":0.0013697418181011745},{"signal":606,"j":7,"entry_index":607,"entry_open":716.5729362817169,"shares":11.468651787647484,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.019970044932601103,"tier":"GREAT","exit_index":608,"exit_open":708.9783555066326,"net":-0.013562234526842243,"realized_loss_nav":0.001116233294390304}],"trades_last_1":[{"signal":611,"j":20,"entry_index":612,"entry_open":898.2503100522808,"shares":8.01396509050713,"debit":7209.344447237128,"entry_nav":97197.09611834935,"modeled_risk":0.002444024031453835,"tier":"GREAT","exit_index":613,"exit_open":891.0605836308763,"net":-0.010975676039285065,"realized_loss_nav":0.0008140925219838504}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":96892.64832766457,"cash":96892.64832766457,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 3584306075979195116, 'reversal', 'iteration5')":{"source_line":12,"metadata":{"seed":3584306075979195116,"scenario":"reversal","phase":"paired_regression","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":0,"entry_index":607,"entry_open":571.6147652251367,"shares":17.468097526080943,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":565.4790149479502,"net":-0.013697418181011778,"realized_loss_nav":0.0013697418181011745},{"signal":606,"j":7,"entry_index":607,"entry_open":716.5729362817169,"shares":11.468651787647484,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.019970044932601103,"tier":"GREAT","exit_index":608,"exit_open":708.9783555066326,"net":-0.013562234526842243,"realized_loss_nav":0.001116233294390304}],"trades_last_1":[{"signal":627,"j":16,"entry_index":628,"entry_open":633.9693718141547,"shares":6.860808447396423,"debit":4356.066735165456,"entry_nav":90213.67788086174,"modeled_risk":0.0015910547411685139,"tier":"GOOD","exit_index":629,"exit_open":628.7879116139769,"net":-0.011144069321774697,"realized_loss_nav":0.0005381036535398688}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":89637.5590256102,"cash":89637.5590256102,"receivable":0.0,"exposure":0.0}]},"('paired_regression', 1564008556893530022, 'learnable', 'iteration6')":{"source_line":13,"metadata":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":19,"entry_index":607,"entry_open":686.4307836735534,"shares":11.97225660930647,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":707.382710802779,"net":0.02743606187144776,"realized_loss_nav":0.0},{"signal":606,"j":15,"entry_index":607,"entry_open":984.8298082379058,"shares":8.34471643518924,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":1005.925705249528,"net":0.018361182440316925,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":2,"entry_index":732,"entry_open":1110.9376439417215,"shares":7.98464096172725,"debit":8883.743875068445,"entry_nav":184882.90489337157,"modeled_risk":0.005901377963589981,"tier":"GREAT","exit_index":733,"exit_open":1117.43507551087,"net":0.0028355752334479067,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":184763.73567419883,"cash":0.0,"receivable":105317.58955906764,"exposure":0.42998776694589963}]},"('paired_regression', 1564008556893530022, 'learnable', 'iteration5')":{"source_line":14,"metadata":{"seed":1564008556893530022,"scenario":"learnable","phase":"paired_regression","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":19,"entry_index":607,"entry_open":686.4307836735534,"shares":11.97225660930647,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":707.382710802779,"net":0.02743606187144776,"realized_loss_nav":0.0},{"signal":606,"j":15,"entry_index":607,"entry_open":984.8298082379058,"shares":8.34471643518924,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":1005.925705249528,"net":0.018361182440316925,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":2,"entry_index":732,"entry_open":1110.9376439417215,"shares":7.98464096172725,"debit":8883.743875068445,"entry_nav":184882.90489337157,"modeled_risk":0.005901377963589981,"tier":"GREAT","exit_index":733,"exit_open":1117.43507551087,"net":0.0028355752334479067,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300547,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":184763.73567419883,"cash":0.0,"receivable":105317.58955906764,"exposure":0.42998776694589963}]},"('paired_regression', 1634635432866334191, 'learnable', 'iteration6')":{"source_line":15,"metadata":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":774.6416123391231,"shares":10.608938837989228,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":776.1225664940246,"net":-0.0010894408595788496,"realized_loss_nav":8.966591436863382e-05},{"signal":606,"j":12,"entry_index":607,"entry_open":789.1323077933245,"shares":12.653166481324256,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":801.110857577801,"net":0.012138416735197,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":1,"entry_index":732,"entry_open":678.56073973848,"shares":21.462661521258532,"debit":14585.565057839733,"entry_nav":184556.20209226618,"modeled_risk":0.0049714629839124865,"tier":"GOOD","exit_index":733,"exit_open":683.0232579435958,"net":0.0035612396811748326,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99873.15323311328,"cash":15308.641975308637,"receivable":0.0,"exposure":0.8467191484424564}],"daily_last_1":[{"index":731,"nav":184405.92943011574,"cash":0.0,"receivable":84224.15466316366,"exposure":0.543267643706207}]},"('paired_regression', 1634635432866334191, 'learnable', 'iteration5')":{"source_line":16,"metadata":{"seed":1634635432866334191,"scenario":"learnable","phase":"paired_regression","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":774.6416123391231,"shares":10.608938837989228,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":776.1225664940246,"net":-0.0010894408595788496,"realized_loss_nav":8.966591436863382e-05},{"signal":606,"j":12,"entry_index":607,"entry_open":789.1323077933245,"shares":12.653166481324256,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":801.110857577801,"net":0.012138416735197,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":1,"entry_index":732,"entry_open":678.56073973848,"shares":21.462661521258532,"debit":14585.565057839733,"entry_nav":184556.20209226618,"modeled_risk":0.0049714629839124865,"tier":"GOOD","exit_index":733,"exit_open":683.0232579435958,"net":0.0035612396811748326,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99873.15323311328,"cash":15308.641975308637,"receivable":0.0,"exposure":0.8467191484424564}],"daily_last_1":[{"index":731,"nav":184405.92943011574,"cash":0.0,"receivable":84224.15466316366,"exposure":0.543267643706207}]},"('final', 2098214662956861329, 'learnable', 'iteration6')":{"source_line":17,"metadata":{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":4,"entry_index":607,"entry_open":507.76513406148575,"shares":19.66464768156266,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":519.2746329527968,"net":0.019603567792903176,"realized_loss_nav":0.0},{"signal":606,"j":18,"entry_index":607,"entry_open":748.3422718426357,"shares":13.342855057104455,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":745.8547783207358,"net":-0.006309554751882218,"realized_loss_nav":0.0006309554751882206}],"trades_last_1":[{"signal":731,"j":21,"entry_index":732,"entry_open":752.573042405692,"shares":0.947289092778196,"debit":713.9735909416995,"entry_nav":180732.25879997315,"modeled_risk":0.00024850553563249663,"tier":"GOOD","exit_index":733,"exit_open":755.4062805966928,"net":0.0007579511276336603,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":180595.84326878353,"cash":0.0,"receivable":89652.15580904485,"exposure":0.5035757513221708}]},"('final', 2098214662956861329, 'learnable', 'iteration5')":{"source_line":18,"metadata":{"seed":2098214662956861329,"scenario":"learnable","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":4,"entry_index":607,"entry_open":507.76513406148575,"shares":19.66464768156266,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":519.2746329527968,"net":0.019603567792903176,"realized_loss_nav":0.0},{"signal":606,"j":18,"entry_index":607,"entry_open":748.3422718426357,"shares":13.342855057104455,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":745.8547783207358,"net":-0.006309554751882218,"realized_loss_nav":0.0006309554751882206}],"trades_last_1":[{"signal":731,"j":21,"entry_index":732,"entry_open":752.573042405692,"shares":0.947289092778196,"debit":713.9735909416995,"entry_nav":180732.25879997315,"modeled_risk":0.00024850553563249663,"tier":"GOOD","exit_index":733,"exit_open":755.4062805966928,"net":0.0007579511276336603,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":180595.84326878353,"cash":0.0,"receivable":89652.15580904485,"exposure":0.5035757513221708}]},"('final', 2098214662956861329, 'null', 'iteration6')":{"source_line":19,"metadata":{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration6"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 2098214662956861329, 'null', 'iteration5')":{"source_line":20,"metadata":{"seed":2098214662956861329,"scenario":"null","phase":"final","variant":"iteration5"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 2098214662956861329, 'outer_noise', 'iteration6')":{"source_line":21,"metadata":{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":4,"entry_index":607,"entry_open":512.1843616241772,"shares":19.494977227803776,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":524.7705633682255,"net":0.02150445974112869,"realized_loss_nav":0.0},{"signal":606,"j":18,"entry_index":607,"entry_open":700.1890617337763,"shares":14.260466225473575,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":694.6469626800293,"net":-0.010886943439852637,"realized_loss_nav":0.001088694343985262}],"trades_last_1":[{"signal":731,"j":17,"entry_index":732,"entry_open":1176.671971305278,"shares":15.768060693208376,"debit":18581.665812128078,"entry_nav":185816.65812128078,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":733,"exit_open":1179.381574949605,"net":-0.0006996357799052833,"realized_loss_nav":6.996357799052387e-05}],"daily_first_1":[{"index":606,"nav":99912.78514327275,"cash":41769.54732510288,"receivable":0.0,"exposure":0.5819399162458911}],"daily_last_1":[{"index":731,"nav":185733.16586351284,"cash":55249.52628909296,"receivable":74822.13439580359,"exposure":0.29968533040307677}]},"('final', 2098214662956861329, 'outer_noise', 'iteration5')":{"source_line":22,"metadata":{"seed":2098214662956861329,"scenario":"outer_noise","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":4,"entry_index":607,"entry_open":512.1843616241772,"shares":19.494977227803776,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":524.7705633682255,"net":0.02150445974112869,"realized_loss_nav":0.0},{"signal":606,"j":18,"entry_index":607,"entry_open":700.1890617337763,"shares":14.260466225473575,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":694.6469626800293,"net":-0.010886943439852637,"realized_loss_nav":0.001088694343985262}],"trades_last_1":[{"signal":731,"j":17,"entry_index":732,"entry_open":1176.671971305278,"shares":15.768060693208376,"debit":18581.665812128078,"entry_nav":185816.65812128078,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":733,"exit_open":1179.381574949605,"net":-0.0006996357799052833,"realized_loss_nav":6.996357799052387e-05}],"daily_first_1":[{"index":606,"nav":99912.78514327275,"cash":41769.54732510288,"receivable":0.0,"exposure":0.5819399162458911}],"daily_last_1":[{"index":731,"nav":185733.16586351284,"cash":55249.52628909296,"receivable":74822.13439580359,"exposure":0.29968533040307677}]},"('final', 2098214662956861329, 'reversal', 'iteration6')":{"source_line":23,"metadata":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":304.4423948602187,"shares":26.994024568885614,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":301.2594450256409,"net":-0.013419203769184151,"realized_loss_nav":0.001104461215570709},{"signal":606,"j":20,"entry_index":607,"entry_open":951.8980804739876,"shares":10.489591975360021,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":932.3224033188626,"net":-0.02349879220985418,"realized_loss_nav":0.002349879220985422}],"trades_last_1":[{"signal":610,"j":9,"entry_index":611,"entry_open":480.25848157447274,"shares":19.920427443595816,"debit":9581.304667730346,"entry_nav":98018.66511686429,"modeled_risk":0.006149013722774884,"tier":"GOOD","exit_index":612,"exit_open":475.69764841048874,"net":-0.01246368134160547,"realized_loss_nav":0.0012183223274164134}],"daily_first_1":[{"index":606,"nav":99885.4804213433,"cash":23539.094650205756,"receivable":0.0,"exposure":0.7643391757149122}],"daily_last_1":[{"index":731,"nav":97560.6694510222,"cash":97560.6694510222,"receivable":0.0,"exposure":0.0}]},"('final', 2098214662956861329, 'reversal', 'iteration5')":{"source_line":24,"metadata":{"seed":2098214662956861329,"scenario":"reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":304.4423948602187,"shares":26.994024568885614,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":301.2594450256409,"net":-0.013419203769184151,"realized_loss_nav":0.001104461215570709},{"signal":606,"j":20,"entry_index":607,"entry_open":951.8980804739876,"shares":10.489591975360021,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":932.3224033188626,"net":-0.02349879220985418,"realized_loss_nav":0.002349879220985422}],"trades_last_1":[{"signal":627,"j":1,"entry_index":628,"entry_open":685.6781600590076,"shares":5.199708406235274,"debit":3570.6744825700043,"entry_nav":89476.7686892726,"modeled_risk":0.0025103227613009114,"tier":"GREAT","exit_index":629,"exit_open":672.3835652378885,"net":-0.02232639919763979,"realized_loss_nav":0.000890960917235735}],"daily_first_1":[{"index":606,"nav":99885.4804213433,"cash":23539.094650205756,"receivable":0.0,"exposure":0.7643391757149122}],"daily_last_1":[{"index":731,"nav":89244.69038935479,"cash":89244.69038935479,"receivable":0.0,"exposure":0.0}]},"('final', 2098214662956861329, 'random_reversal', 'iteration6')":{"source_line":25,"metadata":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":4,"entry_index":607,"entry_open":507.76513406148575,"shares":19.66464768156266,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":519.2746329527968,"net":0.019603567792903176,"realized_loss_nav":0.0},{"signal":606,"j":18,"entry_index":607,"entry_open":748.3422718426357,"shares":13.342855057104455,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":745.8547783207358,"net":-0.006309554751882218,"realized_loss_nav":0.0006309554751882206}],"trades_last_1":[{"signal":661,"j":3,"entry_index":662,"entry_open":326.57623543391264,"shares":7.650573440937138,"debit":2502.243216461804,"entry_nav":125669.58228872517,"modeled_risk":0.004831196133089152,"tier":"GREAT","exit_index":663,"exit_open":324.3776760312089,"net":-0.009707488094817696,"realized_loss_nav":0.00019328858894695792}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":124793.84954533487,"cash":124793.84954533487,"receivable":0.0,"exposure":0.0}]},"('final', 2098214662956861329, 'random_reversal', 'iteration5')":{"source_line":26,"metadata":{"seed":2098214662956861329,"scenario":"random_reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":4,"entry_index":607,"entry_open":507.76513406148575,"shares":19.66464768156266,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":519.2746329527968,"net":0.019603567792903176,"realized_loss_nav":0.0},{"signal":606,"j":18,"entry_index":607,"entry_open":748.3422718426357,"shares":13.342855057104455,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":745.8547783207358,"net":-0.006309554751882218,"realized_loss_nav":0.0006309554751882206}],"trades_last_1":[{"signal":675,"j":9,"entry_index":676,"entry_open":480.6866675595584,"shares":7.668487347021958,"debit":3691.668837504718,"entry_nav":116344.43728035444,"modeled_risk":0.0019960283619607,"tier":"GOOD","exit_index":677,"exit_open":478.02161170688305,"net":-0.008523167145776611,"realized_loss_nav":0.0002704444774878856}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":115957.02475846064,"cash":115957.02475846064,"receivable":0.0,"exposure":0.0}]},"('final', 2928371724749768812, 'learnable', 'iteration6')":{"source_line":27,"metadata":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":20,"entry_index":607,"entry_open":378.1581356206876,"shares":26.404357134646045,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":391.572251065008,"net":0.03237047407960514,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":666.9549642921335,"shares":14.971059518086143,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":680.3701160729593,"net":0.017058270980236934,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":10,"entry_index":732,"entry_open":968.8220207511099,"shares":18.93384316757972,"debit":18371.03948449648,"entry_nav":184267.43751326425,"modeled_risk":0.012244450277418578,"tier":"GOOD","exit_index":733,"exit_open":981.851408328,"net":0.010412898189340991,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99897.8076095733,"cash":31769.54732510288,"receivable":0.0,"exposure":0.681979534032753}],"daily_last_1":[{"index":731,"nav":184134.41108044607,"cash":0.0,"receivable":95450.12253501362,"exposure":0.4816280022026267}]},"('final', 2928371724749768812, 'learnable', 'iteration5')":{"source_line":28,"metadata":{"seed":2928371724749768812,"scenario":"learnable","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":20,"entry_index":607,"entry_open":378.1581356206876,"shares":26.404357134646045,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":391.572251065008,"net":0.03237047407960514,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":666.9549642921335,"shares":14.971059518086143,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":680.3701160729593,"net":0.017058270980236934,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":10,"entry_index":732,"entry_open":968.8220207511099,"shares":18.93384316757972,"debit":18371.03948449648,"entry_nav":184267.43751326425,"modeled_risk":0.012244450277418578,"tier":"GOOD","exit_index":733,"exit_open":981.851408328,"net":0.010412898189340991,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99897.8076095733,"cash":31769.54732510288,"receivable":0.0,"exposure":0.681979534032753}],"daily_last_1":[{"index":731,"nav":184134.41108044607,"cash":0.0,"receivable":95450.12253501362,"exposure":0.4816280022026267}]},"('final', 2928371724749768812, 'null', 'iteration6')":{"source_line":29,"metadata":{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration6"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 2928371724749768812, 'null', 'iteration5')":{"source_line":30,"metadata":{"seed":2928371724749768812,"scenario":"null","phase":"final","variant":"iteration5"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 2928371724749768812, 'outer_noise', 'iteration6')":{"source_line":31,"metadata":{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":661.7407633486818,"shares":15.08902431183506,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0062905641537693464,"tier":"GREAT","exit_index":608,"exit_open":675.8903667825982,"net":0.018322838725296497,"realized_loss_nav":0.0},{"signal":606,"j":20,"entry_index":607,"entry_open":349.80174345017645,"shares":28.544804745156316,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":363.9967532842803,"net":0.03746309259950631,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":13,"entry_index":732,"entry_open":793.0419244281981,"shares":0.04829721689841154,"debit":38.359170410392835,"entry_nav":184727.90916919863,"modeled_risk":1.3062499512779699e-05,"tier":"GOOD","exit_index":733,"exit_open":795.1941922911689,"net":-0.000289696789642635,"realized_loss_nav":6.015619714001568e-08}],"daily_first_1":[{"index":606,"nav":99897.8076095733,"cash":31769.54732510288,"receivable":0.0,"exposure":0.681979534032753}],"daily_last_1":[{"index":731,"nav":184594.4092201528,"cash":0.0,"receivable":95594.44318961093,"exposure":0.4821379282641104}]},"('final', 2928371724749768812, 'outer_noise', 'iteration5')":{"source_line":32,"metadata":{"seed":2928371724749768812,"scenario":"outer_noise","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":17,"entry_index":607,"entry_open":661.7407633486818,"shares":15.08902431183506,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0062905641537693464,"tier":"GREAT","exit_index":608,"exit_open":675.8903667825982,"net":0.018322838725296497,"realized_loss_nav":0.0},{"signal":606,"j":20,"entry_index":607,"entry_open":349.80174345017645,"shares":28.544804745156316,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":363.9967532842803,"net":0.03746309259950631,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":13,"entry_index":732,"entry_open":793.0419244281981,"shares":0.04829721689841154,"debit":38.359170410392835,"entry_nav":184727.90916919863,"modeled_risk":1.3062499512779699e-05,"tier":"GOOD","exit_index":733,"exit_open":795.1941922911689,"net":-0.000289696789642635,"realized_loss_nav":6.015619714001568e-08}],"daily_first_1":[{"index":606,"nav":99897.8076095733,"cash":31769.54732510288,"receivable":0.0,"exposure":0.681979534032753}],"daily_last_1":[{"index":731,"nav":184594.4092201528,"cash":0.0,"receivable":95594.44318961093,"exposure":0.4821379282641104}]},"('final', 2928371724749768812, 'reversal', 'iteration6')":{"source_line":33,"metadata":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":10,"entry_index":607,"entry_open":886.7650768426948,"shares":11.260053792208389,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549676,"tier":"GREAT","exit_index":608,"exit_open":879.5858880481907,"net":-0.01106718623314229,"realized_loss_nav":0.0011067186233142275},{"signal":606,"j":8,"entry_index":607,"entry_open":754.5671073817008,"shares":13.232782569794134,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":750.9409742666791,"net":-0.0077866922732493515,"realized_loss_nav":0.0007786692273249355}],"trades_last_1":[{"signal":610,"j":21,"entry_index":611,"entry_open":687.7261688063328,"shares":14.202638857372758,"debit":9782.1776979334,"entry_nav":97821.77697933401,"modeled_risk":0.006290564153769346,"tier":"GOOD","exit_index":612,"exit_open":682.535300652076,"net":-0.010520767677244636,"realized_loss_nav":0.0010520767677244687}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":96424.00031264173,"cash":96424.00031264173,"receivable":0.0,"exposure":0.0}]},"('final', 2928371724749768812, 'reversal', 'iteration5')":{"source_line":34,"metadata":{"seed":2928371724749768812,"scenario":"reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":10,"entry_index":607,"entry_open":886.7650768426948,"shares":11.260053792208389,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549676,"tier":"GREAT","exit_index":608,"exit_open":879.5858880481907,"net":-0.01106718623314229,"realized_loss_nav":0.0011067186233142275},{"signal":606,"j":8,"entry_index":607,"entry_open":754.5671073817008,"shares":13.232782569794134,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":750.9409742666791,"net":-0.0077866922732493515,"realized_loss_nav":0.0007786692273249355}],"trades_last_1":[{"signal":627,"j":1,"entry_index":628,"entry_open":510.86064648314425,"shares":6.2215052062018055,"debit":3183.08965499611,"entry_nav":88894.54735336182,"modeled_risk":0.002252492450673952,"tier":"GOOD","exit_index":629,"exit_open":505.1497567069049,"net":-0.014140978223397216,"realized_loss_nav":0.0005063527835458252}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":88603.49409544075,"cash":88603.49409544075,"receivable":0.0,"exposure":0.0}]},"('final', 2928371724749768812, 'random_reversal', 'iteration6')":{"source_line":35,"metadata":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":20,"entry_index":607,"entry_open":378.1581356206876,"shares":26.404357134646045,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":391.572251065008,"net":0.03237047407960514,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":666.9549642921335,"shares":14.971059518086143,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":680.3701160729593,"net":0.017058270980236934,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":649,"j":5,"entry_index":650,"entry_open":668.0337002526315,"shares":3.658966041690191,"debit":2447.9790928649163,"entry_nav":115230.1865767497,"modeled_risk":0.0013363832853378348,"tier":"GOOD","exit_index":651,"exit_open":660.3889616240084,"net":-0.014404869410746368,"realized_loss_nav":0.0003060206721913931}],"daily_first_1":[{"index":606,"nav":99897.8076095733,"cash":31769.54732510288,"receivable":0.0,"exposure":0.681979534032753}],"daily_last_1":[{"index":731,"nav":113925.44267196156,"cash":113925.44267196156,"receivable":0.0,"exposure":0.0}]},"('final', 2928371724749768812, 'random_reversal', 'iteration5')":{"source_line":36,"metadata":{"seed":2928371724749768812,"scenario":"random_reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":20,"entry_index":607,"entry_open":378.1581356206876,"shares":26.404357134646045,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":391.572251065008,"net":0.03237047407960514,"realized_loss_nav":0.0},{"signal":606,"j":17,"entry_index":607,"entry_open":666.9549642921335,"shares":14.971059518086143,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":680.3701160729593,"net":0.017058270980236934,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":663,"j":5,"entry_index":664,"entry_open":724.2891552092628,"shares":12.466031822414141,"debit":9042.555174954328,"entry_nav":106370.41540434971,"modeled_risk":0.005347612230883808,"tier":"GOOD","exit_index":665,"exit_open":728.6870822274534,"net":0.003058364102479505,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99897.8076095733,"cash":31769.54732510288,"receivable":0.0,"exposure":0.681979534032753}],"daily_last_1":[{"index":731,"nav":105869.2762229536,"cash":105869.2762229536,"receivable":0.0,"exposure":0.0}]},"('final', 5618266449171873643, 'learnable', 'iteration6')":{"source_line":37,"metadata":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":12,"entry_index":607,"entry_open":726.9158840550317,"shares":13.736145660485562,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":751.8713613489786,"net":0.031232281563098985,"realized_loss_nav":0.0},{"signal":606,"j":0,"entry_index":607,"entry_open":748.2029097877833,"shares":13.345340329046106,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GOOD","exit_index":608,"exit_open":756.9195527305712,"net":0.00861970093494846,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":21,"entry_index":732,"entry_open":1172.560937891128,"shares":15.819576011780395,"debit":18577.241010741334,"entry_nav":186430.73616423842,"modeled_risk":0.00626835085150084,"tier":"GOOD","exit_index":733,"exit_open":1189.7813165305874,"net":0.01164662768943825,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.09465020576,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":186296.16219213934,"cash":0.0,"receivable":96580.18079276558,"exposure":0.4815771851856177}]},"('final', 5618266449171873643, 'learnable', 'iteration5')":{"source_line":38,"metadata":{"seed":5618266449171873643,"scenario":"learnable","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":12,"entry_index":607,"entry_open":726.9158840550317,"shares":13.736145660485562,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":751.8713613489786,"net":0.031232281563098985,"realized_loss_nav":0.0},{"signal":606,"j":0,"entry_index":607,"entry_open":748.2029097877833,"shares":13.345340329046106,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GOOD","exit_index":608,"exit_open":756.9195527305712,"net":0.00861970093494846,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":21,"entry_index":732,"entry_open":1172.560937891128,"shares":15.819576011780395,"debit":18577.241010741334,"entry_nav":186430.73616423842,"modeled_risk":0.00626835085150084,"tier":"GOOD","exit_index":733,"exit_open":1189.7813165305874,"net":0.01164662768943825,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.09465020576,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":186296.16219213934,"cash":0.0,"receivable":96580.18079276558,"exposure":0.4815771851856177}]},"('final', 5618266449171873643, 'null', 'iteration6')":{"source_line":39,"metadata":{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration6"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 5618266449171873643, 'null', 'iteration5')":{"source_line":40,"metadata":{"seed":5618266449171873643,"scenario":"null","phase":"final","variant":"iteration5"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 5618266449171873643, 'outer_noise', 'iteration6')":{"source_line":41,"metadata":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":12,"entry_index":607,"entry_open":746.6367919097067,"shares":13.37333302416213,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":775.8699683914385,"net":0.03604035195387367,"realized_loss_nav":0.0},{"signal":606,"j":0,"entry_index":607,"entry_open":770.6509445677125,"shares":12.956608353865743,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GOOD","exit_index":608,"exit_open":780.5218278533724,"net":0.009774626168685518,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":21,"entry_index":732,"entry_open":1213.1959820890643,"shares":15.293131397815609,"debit":18581.3959137381,"entry_nav":186345.3851752361,"modeled_risk":0.006272624511309365,"tier":"GOOD","exit_index":733,"exit_open":1233.3393147339746,"net":0.013558284611797866,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.09465020576,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":186210.85385191356,"cash":0.0,"receivable":96523.3049702246,"exposure":0.48164511910253127}]},"('final', 5618266449171873643, 'outer_noise', 'iteration5')":{"source_line":42,"metadata":{"seed":5618266449171873643,"scenario":"outer_noise","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":12,"entry_index":607,"entry_open":746.6367919097067,"shares":13.37333302416213,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":775.8699683914385,"net":0.03604035195387367,"realized_loss_nav":0.0},{"signal":606,"j":0,"entry_index":607,"entry_open":770.6509445677125,"shares":12.956608353865743,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GOOD","exit_index":608,"exit_open":780.5218278533724,"net":0.009774626168685518,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":21,"entry_index":732,"entry_open":1213.1959820890643,"shares":15.293131397815609,"debit":18581.3959137381,"entry_nav":186345.3851752361,"modeled_risk":0.006272624511309365,"tier":"GOOD","exit_index":733,"exit_open":1233.3393147339746,"net":0.013558284611797866,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.09465020576,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":186210.85385191356,"cash":0.0,"receivable":96523.3049702246,"exposure":0.48164511910253127}]},"('final', 5618266449171873643, 'reversal', 'iteration6')":{"source_line":43,"metadata":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":16,"entry_index":607,"entry_open":1019.600658984896,"shares":9.79307180542776,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":1006.2620540273502,"net":-0.016038504465818226,"realized_loss_nav":0.0016038504465818186},{"signal":606,"j":22,"entry_index":607,"entry_open":600.2948122937814,"shares":16.6335311613753,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":595.8733978840277,"net":-0.010338848615935037,"realized_loss_nav":0.0010338848615935058}],"trades_last_1":[{"signal":610,"j":1,"entry_index":611,"entry_open":712.7646614800466,"shares":11.670619678519271,"debit":8330.882892348793,"entry_nav":98879.7087047376,"modeled_risk":0.005299970436639109,"tier":"GOOD","exit_index":612,"exit_open":717.3039665172041,"net":0.0033540049052673826,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":98366.30930723144,"cash":98366.30930723144,"receivable":0.0,"exposure":0.0}]},"('final', 5618266449171873643, 'reversal', 'iteration5')":{"source_line":44,"metadata":{"seed":5618266449171873643,"scenario":"reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":16,"entry_index":607,"entry_open":1019.600658984896,"shares":9.79307180542776,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":1006.2620540273502,"net":-0.016038504465818226,"realized_loss_nav":0.0016038504465818186},{"signal":606,"j":22,"entry_index":607,"entry_open":600.2948122937814,"shares":16.6335311613753,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":595.8733978840277,"net":-0.010338848615935037,"realized_loss_nav":0.0010338848615935058}],"trades_last_1":[{"signal":627,"j":8,"entry_index":628,"entry_open":481.90078811126574,"shares":6.286150141294614,"debit":3033.844658336533,"entry_nav":91828.37916816634,"modeled_risk":0.0010886277667715868,"tier":"GREAT","exit_index":629,"exit_open":473.40183325027414,"net":-0.020578993618245556,"realized_loss_nav":0.0006798929745707552}],"daily_first_1":[{"index":606,"nav":99850.22466300549,"cash":0.0,"receivable":0.0,"exposure":1.0}],"daily_last_1":[{"index":731,"nav":91188.82493516916,"cash":91188.82493516916,"receivable":0.0,"exposure":0.0}]},"('final', 5618266449171873643, 'random_reversal', 'iteration6')":{"source_line":45,"metadata":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":12,"entry_index":607,"entry_open":726.9158840550317,"shares":13.736145660485562,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":751.8713613489786,"net":0.031232281563098985,"realized_loss_nav":0.0},{"signal":606,"j":0,"entry_index":607,"entry_open":748.2029097877833,"shares":13.345340329046106,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GOOD","exit_index":608,"exit_open":756.9195527305712,"net":0.00861970093494846,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":637,"j":14,"entry_index":638,"entry_open":589.0131423835817,"shares":8.81578063761366,"debit":5200.399571909045,"entry_nav":111690.89895341767,"modeled_risk":0.005718380966251959,"tier":"GREAT","exit_index":639,"exit_open":582.5617238179841,"net":-0.013915625214282024,"realized_loss_nav":0.0006479203953527179}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.09465020576,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":110853.16346075339,"cash":110853.16346075339,"receivable":0.0,"exposure":0.0}]},"('final', 5618266449171873643, 'random_reversal', 'iteration5')":{"source_line":46,"metadata":{"seed":5618266449171873643,"scenario":"random_reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":12,"entry_index":607,"entry_open":726.9158840550317,"shares":13.736145660485562,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GREAT","exit_index":608,"exit_open":751.8713613489786,"net":0.031232281563098985,"realized_loss_nav":0.0},{"signal":606,"j":0,"entry_index":607,"entry_open":748.2029097877833,"shares":13.345340329046106,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.0032950574138791815,"tier":"GOOD","exit_index":608,"exit_open":756.9195527305712,"net":0.00861970093494846,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":651,"j":9,"entry_index":652,"entry_open":595.6071902107074,"shares":5.124611846917882,"debit":3056.8340465578585,"entry_nav":105916.54874100386,"modeled_risk":0.0018155057831726995,"tier":"GOOD","exit_index":653,"exit_open":587.5256343033972,"net":-0.016523462218853813,"realized_loss_nav":0.0004768799821934791}],"daily_first_1":[{"index":606,"nav":99915.4354887422,"cash":43539.09465020576,"receivable":0.0,"exposure":0.5642405556535711}],"daily_last_1":[{"index":731,"nav":105540.77033075417,"cash":105540.77033075417,"receivable":0.0,"exposure":0.0}]},"('final', 8582935296371253491, 'learnable', 'iteration6')":{"source_line":47,"metadata":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":374.0723572869646,"shares":21.969347177296754,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":377.80613504715654,"net":0.006956025714271563,"realized_loss_nav":0.0},{"signal":606,"j":2,"entry_index":607,"entry_open":509.8998235235689,"shares":19.582321871188125,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":518.3038923913496,"net":0.013436925742521533,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":23,"entry_index":732,"entry_open":1084.0317137168072,"shares":8.023349756713285,"debit":8710.61193489901,"entry_nav":180186.81713129795,"modeled_risk":0.011729539769738586,"tier":"GOOD","exit_index":733,"exit_open":1103.5272350203193,"net":0.014934893350902145,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99890.78111228217,"cash":27078.18930041151,"receivable":0.0,"exposure":0.7289220386616629}],"daily_last_1":[{"index":731,"nav":180021.3966816601,"cash":0.0,"receivable":69741.09692308995,"exposure":0.6125955124855726}]},"('final', 8582935296371253491, 'learnable', 'iteration5')":{"source_line":48,"metadata":{"seed":8582935296371253491,"scenario":"learnable","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":374.0723572869646,"shares":21.969347177296754,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":377.80613504715654,"net":0.006956025714271563,"realized_loss_nav":0.0},{"signal":606,"j":2,"entry_index":607,"entry_open":509.8998235235689,"shares":19.582321871188125,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":518.3038923913496,"net":0.013436925742521533,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":23,"entry_index":732,"entry_open":1084.0317137168072,"shares":8.023349756713285,"debit":8710.61193489901,"entry_nav":180186.81713129795,"modeled_risk":0.011729539769738586,"tier":"GOOD","exit_index":733,"exit_open":1103.5272350203193,"net":0.014934893350902145,"realized_loss_nav":0.0}],"daily_first_1":[{"index":606,"nav":99890.78111228217,"cash":27078.18930041151,"receivable":0.0,"exposure":0.7289220386616629}],"daily_last_1":[{"index":731,"nav":180021.3966816601,"cash":0.0,"receivable":69741.09692308995,"exposure":0.6125955124855726}]},"('final', 8582935296371253491, 'null', 'iteration6')":{"source_line":49,"metadata":{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration6"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 8582935296371253491, 'null', 'iteration5')":{"source_line":50,"metadata":{"seed":8582935296371253491,"scenario":"null","phase":"final","variant":"iteration5"},"trades_first_2":[],"trades_last_1":[],"daily_first_1":[{"index":606,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}],"daily_last_1":[{"index":731,"nav":100000.0,"cash":100000.0,"receivable":0.0,"exposure":0.0}]},"('final', 8582935296371253491, 'outer_noise', 'iteration6')":{"source_line":51,"metadata":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":332.2687479125547,"shares":24.733368811531847,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":335.1650181829202,"net":0.005695032142839729,"realized_loss_nav":0.0},{"signal":606,"j":2,"entry_index":607,"entry_open":483.5259119550451,"shares":20.650439241049167,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":491.6695107693943,"net":0.013796157178151525,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":15,"entry_index":732,"entry_open":684.2406344833354,"shares":4.867603471697181,"debit":3335.608006019196,"entry_nav":179729.33644703616,"modeled_risk":0.004503097565238778,"tier":"GOOD","exit_index":733,"exit_open":679.7669803830339,"net":-0.009514051553674796,"realized_loss_nav":0.00017657187835592476}],"daily_first_1":[{"index":606,"nav":99890.78111228217,"cash":27078.18930041151,"receivable":0.0,"exposure":0.7289220386616629}],"daily_last_1":[{"index":731,"nav":179545.4342720168,"cash":0.0,"receivable":56943.984259139,"exposure":0.6828435961625895}]},"('final', 8582935296371253491, 'outer_noise', 'iteration5')":{"source_line":52,"metadata":{"seed":8582935296371253491,"scenario":"outer_noise","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":332.2687479125547,"shares":24.733368811531847,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":335.1650181829202,"net":0.005695032142839729,"realized_loss_nav":0.0},{"signal":606,"j":2,"entry_index":607,"entry_open":483.5259119550451,"shares":20.650439241049167,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":491.6695107693943,"net":0.013796157178151525,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":731,"j":15,"entry_index":732,"entry_open":684.2406344833354,"shares":4.867603471697181,"debit":3335.608006019196,"entry_nav":179729.33644703616,"modeled_risk":0.004503097565238778,"tier":"GOOD","exit_index":733,"exit_open":679.7669803830339,"net":-0.009514051553674796,"realized_loss_nav":0.00017657187835592476}],"daily_first_1":[{"index":606,"nav":99890.78111228217,"cash":27078.18930041151,"receivable":0.0,"exposure":0.7289220386616629}],"daily_last_1":[{"index":731,"nav":179545.4342720168,"cash":0.0,"receivable":56943.984259139,"exposure":0.6828435961625895}]},"('final', 8582935296371253491, 'reversal', 'iteration6')":{"source_line":53,"metadata":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":8,"entry_index":607,"entry_open":937.6006688113279,"shares":10.649547081658302,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":936.2660209493424,"net":-0.0044147142549685325,"realized_loss_nav":0.0004414714254968567},{"signal":606,"j":13,"entry_index":607,"entry_open":1230.5368583801646,"shares":8.114362766381886,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":1218.8004334457262,"net":-0.012504582648309781,"realized_loss_nav":0.0012504582648309769}],"trades_last_1":[{"signal":609,"j":13,"entry_index":610,"entry_open":1229.2669881329496,"shares":2.9575081833244043,"debit":3641.0205276590823,"entry_nav":98863.82226800726,"modeled_risk":0.0023167294859731944,"tier":"GREAT","exit_index":611,"exit_open":1217.0869791378645,"net":-0.012874177373104034,"realized_loss_nav":0.000474138496943032}],"daily_first_1":[{"index":606,"nav":99852.87500847495,"cash":1769.5473251028816,"receivable":0.0,"exposure":0.9822784539258114}],"daily_last_1":[{"index":731,"nav":98691.1311415539,"cash":98691.1311415539,"receivable":0.0,"exposure":0.0}]},"('final', 8582935296371253491, 'reversal', 'iteration5')":{"source_line":54,"metadata":{"seed":8582935296371253491,"scenario":"reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":8,"entry_index":607,"entry_open":937.6006688113279,"shares":10.649547081658302,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.003295057413879181,"tier":"GREAT","exit_index":608,"exit_open":936.2660209493424,"net":-0.0044147142549685325,"realized_loss_nav":0.0004414714254968567},{"signal":606,"j":13,"entry_index":607,"entry_open":1230.5368583801646,"shares":8.114362766381886,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.006290564153769346,"tier":"GREAT","exit_index":608,"exit_open":1218.8004334457262,"net":-0.012504582648309781,"realized_loss_nav":0.0012504582648309769}],"trades_last_1":[{"signal":627,"j":3,"entry_index":628,"entry_open":425.0538791369397,"shares":10.224724414231389,"debit":4352.5778635382885,"entry_nav":90213.57554319024,"modeled_risk":0.011706578262276833,"tier":"GREAT","exit_index":629,"exit_open":418.4797995343042,"net":-0.01841563869159879,"realized_loss_nav":0.0008885081965695667}],"daily_first_1":[{"index":606,"nav":99852.87500847495,"cash":1769.5473251028816,"receivable":0.0,"exposure":0.9822784539258114}],"daily_last_1":[{"index":731,"nav":89756.90945491554,"cash":89756.90945491554,"receivable":0.0,"exposure":0.0}]},"('final', 8582935296371253491, 'random_reversal', 'iteration6')":{"source_line":55,"metadata":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration6"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":374.0723572869646,"shares":21.969347177296754,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":377.80613504715654,"net":0.006956025714271563,"realized_loss_nav":0.0},{"signal":606,"j":2,"entry_index":607,"entry_open":509.8998235235689,"shares":19.582321871188125,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":518.3038923913496,"net":0.013436925742521533,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":682,"j":2,"entry_index":683,"entry_open":564.1350671929381,"shares":23.42116469054058,"debit":13232.519366909632,"entry_nav":132325.1936690963,"modeled_risk":0.012281577633549676,"tier":"GOOD","exit_index":684,"exit_open":562.7022682665221,"net":-0.005527714097045111,"realized_loss_nav":0.0005527714097045106}],"daily_first_1":[{"index":606,"nav":99890.78111228217,"cash":27078.18930041151,"receivable":0.0,"exposure":0.7289220386616629}],"daily_last_1":[{"index":731,"nav":131409.5253454145,"cash":131409.5253454145,"receivable":0.0,"exposure":0.0}]},"('final', 8582935296371253491, 'random_reversal', 'iteration5')":{"source_line":56,"metadata":{"seed":8582935296371253491,"scenario":"random_reversal","phase":"final","variant":"iteration5"},"trades_first_2":[{"signal":606,"j":3,"entry_index":607,"entry_open":374.0723572869646,"shares":21.969347177296754,"debit":8230.45267489712,"entry_nav":100000.0,"modeled_risk":0.0199700449326011,"tier":"GREAT","exit_index":608,"exit_open":377.80613504715654,"net":0.006956025714271563,"realized_loss_nav":0.0},{"signal":606,"j":2,"entry_index":607,"entry_open":509.8998235235689,"shares":19.582321871188125,"debit":10000.0,"entry_nav":100000.0,"modeled_risk":0.012281577633549675,"tier":"GREAT","exit_index":608,"exit_open":518.3038923913496,"net":0.013436925742521533,"realized_loss_nav":0.0}],"trades_last_1":[{"signal":691,"j":2,"entry_index":692,"entry_open":573.603306641277,"shares":4.174905310082859,"debit":2398.3316000139203,"entry_nav":126149.87496148716,"modeled_risk":0.0023349445051419116,"tier":"GOOD","exit_index":693,"exit_open":572.7257771666729,"net":-0.004520778332676834,"realized_loss_nav":8.594796891576183e-05}],"daily_first_1":[{"index":606,"nav":99890.78111228217,"cash":27078.18930041151,"receivable":0.0,"exposure":0.7289220386616629}],"daily_last_1":[{"index":731,"nav":125820.97332820624,"cash":125820.97332820624,"receivable":0.0,"exposure":0.0}]}}}
```

## discrimination_iteration2/audit_artifacts.py

```python
"""Final deterministic artifact checks and interpretation; no fitting or replays."""
import json,hashlib,statistics as st
from pathlib import Path
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((O/'report.json').read_text())
assert sha(O/'preregister.json')==r['preregister_sha256']
assert all(sha(Path(p))==h for p,h in r['source_sha256'].items())
assert r['full_portfolio_replays']==48 and r['total_compute_seconds']<900
static=[]
for sc in ('learnable','misleading','null','reversal'):
    rows=[z for z in r['static_independent_split_ablation'] if z['scenario']==sc]
    static.append(dict(scenario=sc,coverage=st.mean(z['coverage'] for z in rows),false_great=sum(z['false_great_on_terrible_count'] for z in rows),passed_seeds=sum(z['status']=='PASS' for z in rows)))
r['static_split_summary']=static
r['followup_diagnosis']=[
    'Independent static ablation reaches55.3% stable coverage but fails every seed and causes2336 false GREAT at inversion; static mean confidence cannot certify temporal validity.',
    'Online stable scenarios emit only5 GOOD predictions each across four seeds; populated aggregate tiers are not reliable five-way identification.',
    'Stable tapes produce2..6 nuisance alarms per seed; quarantine and post-reset warmup remove large fractions of coverage. Detector scans five cells repeatedly without multiplicity calibration; nominal3SE comparisons do not control a sequential false-alarm rate.',
    'All online holdout decisions:13920 quarantine,9405 insufficient matured dates,7549 boundary uncertainty,9192 absent signal,32 residual-bias veto,7518 confident. These mutually exclusive prioritized reasons are not causal effect estimates.',
    'Future work requires independent sequential false-alarm calibration and better time-stamped change predictors. No post-holdout detector tuning was performed.',
    'Earlier radius attribution is descriptive of the repaired prior estimator:33812 middle-centered UNKNOWN intervals all have radius>=.002. Narrowing economic bands or counting stocks as independent would not be a valid fix.'
]
# Correct the diagnostic wording: direct band audit, not an additional pre-replay unit test.
r['diagnosis']['conclusions'][0]='Absolute-band dispatch supports all five tiers; bands are disjoint. The pre-replay tests cover AVERAGE/GREAT and UNKNOWN; a direct all-five dispatch audit is recorded in artifact_audit.log.'
import experiment as e
assert [e.infer(v,.0001,40,20) for v in (-.01,-.004,0,.004,.01)]==list(e.TIERS)
r['source_sha256'][str(O/'audit_artifacts.py')]=sha(O/'audit_artifacts.py')
(O/'source_checksums.json').write_text(json.dumps(r['source_sha256'],indent=2))
(O/'report.json').write_text(json.dumps(r,indent=2))
p=O/'README.md';s=p.read_text().replace('execution.log contains replay progress extracted from it.','execution.log summarizes the test/replay timing and budget.')
s=s.replace('python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/finalize.py\n','python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/finalize.py\npython3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/audit_artifacts.py\n')
marker='\nAdditional artifact interpretation:\n'
s=s.split(marker)[0]+marker+'\n'+'\n'.join('- '+v for v in r['followup_diagnosis'])+'\n'
p.write_text(s)
(O/'artifact_audit.log').write_text('PASS: frozen preregistration and all recorded sources unchanged;48 replays;581.951s replay/report compute; all-five absolute tier dispatch;96000 ledger rows, strict maturity,384 pending; independent full-position risk audit passed. No new tests, fitting or portfolios in this audit.\n')
manifest={p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','run.log','finalize.log')}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
assert all(sha(O/n)==h for n,h in manifest.items())
print('PASS:',len(manifest),'artifact checksums; experiment result remains FAIL')

```


## discrimination_iteration2/corrected_kernel.py

```python
"""Deterministic research replay kernel; NOT broker/production parity certified."""
from dataclasses import dataclass, field
from math import isfinite
from discovery.competitive_ga.progressive_scaling import allowed_target

@dataclass(frozen=True)
class Bar:
    open: float
    close: float
    dividend: float = 0.0
    split: float = 1.0

@dataclass(frozen=True)
class Signal:
    ticker: str
    family: str
    chromosome: str
    target_weight: float
    score: float = 0.0
    scaling_evidence: object = None
    stop_distance: float = None
    gap_risk: float = None
    other_equity_risk: float = 0.0

@dataclass
class Replay:
    cash: float = 100000.0
    shares: dict = field(default_factory=dict)
    pending: list = field(default_factory=list)
    ledger: list = field(default_factory=list)
    nav: list = field(default_factory=list)
    fees: float = 0.001
    cap: float = 0.10
    max_equity_risk: float = .02
    settlement_sessions: int = 0
    unsettled: list = field(default_factory=list)
    session: int = -1
    risk_snapshot: object = None
    risk_audit: list = field(default_factory=list)
    spread: float = 0.0  # full proportional bid/ask spread
    slippage: float = 0.0  # one-way adverse execution allowance
    impact: float = 0.0  # one-way scenario allowance, not a fitted liquidity model
    mdd_limit: float = .20
    high_water: float = None
    max_drawdown: float = 0.0
    admission_halted: bool = False
    drawdowns: list = field(default_factory=list)

    @property
    def friction(self):
        return self.spread / 2 + self.slippage + self.impact

    @property
    def round_trip_cost(self):
        return (1 + self.friction) * (1 + self.fees) - (1 - self.friction) * (1 - self.fees)

    def monitor(self, equity):
        if not isfinite(equity) or equity <= 0:
            raise ValueError('nonpositive or nonfinite NAV')
        if self.high_water is None:
            self.high_water = equity
        drawdown = max(0., 1 - equity / self.high_water)
        self.max_drawdown = max(self.max_drawdown, drawdown)
        self.high_water = max(self.high_water, equity)
        if drawdown >= self.mdd_limit:
            self.admission_halted = True
        return drawdown

    def day(self, date, bars, signals=(), defense=False, cash_yield_daily=0.0):
        """Execute yesterday's close signals at today's open, then mark close.
        Scaling requires explicit historical evidence and risk estimates; absent
        evidence, only initial 10% exposure is allowed, never an unearned add.
        """
        if self.high_water is None:
            self.high_water = self.cash
        if any(not isfinite(v) or not 0 <= v < 1 for v in (self.spread, self.slippage, self.impact)) or self.friction >= 1:
            raise ValueError('invalid execution costs')
        if not isfinite(self.mdd_limit) or not 0 < self.mdd_limit <= .20:
            raise ValueError('MDD policy cannot exceed 20%')
        if not isfinite(self.max_equity_risk) or not 0 < self.max_equity_risk <= .02:
            raise ValueError('risk budget cannot exceed 2%')
        if not isfinite(self.fees) or not 0<=self.fees<1:raise ValueError('invalid fee')
        if type(self.settlement_sessions) is not int or not 0 <= self.settlement_sessions <= 2:
            raise ValueError('bounded settlement lag required')
        if len({s.ticker for s in self.pending}) != len(self.pending):
            raise ValueError('duplicate pending ticker')
        if any(not isfinite(s.target_weight) or not 0 <= s.target_weight <= 1
               or not isfinite(s.score) for s in self.pending):
            raise ValueError('invalid pending order')
        self.session += 1
        self.cash += sum(v for due,v in self.unsettled if due <= self.session)
        self.unsettled = [(due,v) for due,v in self.unsettled if due > self.session]
        if not 0 <= cash_yield_daily < 1: raise ValueError('invalid yield')
        for ticker,bar in bars.items():
            if not all(isfinite(v) for v in (bar.open,bar.close,bar.split,bar.dividend)) or bar.open<=0 or bar.close<=0 or bar.split<=0:raise ValueError('invalid bar')
            if ticker in self.shares:
                self.shares[ticker]*=bar.split
                self.cash+=self.shares[ticker]*bar.dividend
        self.cash*=(1+cash_yield_daily)
        receivable=sum(v for _,v in self.unsettled)
        open_equity=self.cash+receivable+sum(q*bars[t].open for t,q in self.shares.items())
        self.monitor(open_equity)
        ordered=sorted(self.pending,key=lambda x:(-x.score,x.ticker,x.chromosome))
        targets={}
        # Per-trade loss limit; other holdings do not consume this trade budget.
        # Any aggregate portfolio guard must be a separately configured policy.
        reserved_risk=0.0
        if defense:
            targets={t:0. for t in self.shares}
        else:
            for s in ordered:
                t=s.ticker
                if t not in bars or t in targets:continue
                existing=self.shares.get(t,0.)*bars[t].open/open_equity
                requested=max(0.,s.target_weight)
                if requested<=existing:
                    targets[t]=requested
                elif s.scaling_evidence is not None:
                    if s.stop_distance is None or s.gap_risk is None:
                        raise ValueError('scaling risk inputs required')
                    targets[t]=max(existing,allowed_target(existing,requested,s.scaling_evidence,
                        stop_distance=s.stop_distance,gap_risk=s.gap_risk,
                        other_equity_risk=0.,max_equity_risk=self.max_equity_risk))
                    reserved_risk+=max(0.,targets[t]-existing)*max(s.stop_distance,s.gap_risk)
                else:
                    # No evidence means no increases beyond ordinary 10% entry.
                    targets[t]=min(requested,self.cap) if existing<=self.cap else existing
            # Every increase, ordinary or scaled, gets the same prefill loss gate.
            # Missing gap information means a conservative total-loss scenario.
            for s in ordered:
                t = s.ticker
                if t not in targets:
                    continue
                existing = self.shares.get(t, 0.) * bars[t].open / open_equity
                if targets[t] <= existing:
                    continue
                stop = s.stop_distance
                gap = 1.0 if s.gap_risk is None else s.gap_risk
                if stop is None:
                    stop = 1.0
                if any(not isfinite(v) or not 0 <= v <= 1 for v in (stop, gap)):
                    raise ValueError('invalid mandatory loss inputs')
                loss = max(stop, gap) + self.round_trip_cost
                limit = self.max_equity_risk / loss if loss > 0 else 0.
                allowed = existing if self.admission_halted else max(existing, min(targets[t], limit))
                self.risk_audit.append(dict(date=date, ticker=t, requested=targets[t],
                    allowed=allowed, modeled_equity_loss=allowed * loss,
                    gap_stress_equity_loss=allowed * (1 + self.friction) * (1 + self.fees),
                    gap_loss_guaranteed=False, admission_halted=self.admission_halted))
                targets[t] = allowed
            for t,q in self.shares.items():
                if t not in targets:targets[t]=q*bars[t].open/open_equity
        if self.risk_snapshot is not None:
            if self.risk_snapshot.as_of >= date:
                raise ValueError('risk snapshot must precede execution')
            existing={t:q*bars[t].open/open_equity for t,q in self.shares.items()}
            rejected=self.risk_snapshot.constrain(existing,targets,ordered,bars)
            self.risk_audit.append((date,rejected,dict(targets)))
        proceeds=0.
        for t in sorted(set(self.shares)&set(targets)):
            desired=targets[t]*open_equity/bars[t].open
            sell=max(0.,self.shares[t]-desired)
            if sell>1e-10:
                sell_price = bars[t].open * (1 - self.friction)
                gross=sell*sell_price
                proceeds+=gross*(1-self.fees)
                self.shares[t]-=sell
                self.ledger.append((date,t,'SELL',sell,sell_price,gross*self.fees))
        spendable=self.cash
        for s in ordered:
            t=s.ticker
            if defense or t not in targets:continue
            mark_price=bars[t].open
            price=mark_price*(1+self.friction)
            desired=targets[t]*open_equity/mark_price
            buy=max(0.,desired-self.shares.get(t,0.))
            cost=buy*price*(1+self.fees)
            if cost>spendable:
                buy=spendable/(price*(1+self.fees))
                cost=buy*price*(1+self.fees)
            if buy>1e-10:
                self.shares[t]=self.shares.get(t,0.)+buy
                spendable-=cost
                self.ledger.append((date,t,'BUY',buy,price,buy*price*self.fees))
        self.cash=spendable
        if self.settlement_sessions and proceeds:
            self.unsettled.append((self.session+self.settlement_sessions,proceeds))
        else:
            self.cash+=proceeds
        self.shares={t:q for t,q in self.shares.items() if q>1e-10}
        equity=self.cash+sum(v for _,v in self.unsettled)+sum(q*bars[t].close for t,q in self.shares.items())
        drawdown = self.monitor(equity)
        self.drawdowns.append((date, drawdown, self.max_drawdown, self.admission_halted))
        self.nav.append((date,equity,self.cash,dict(self.shares),defense))
        self.pending=[] if defense else list(signals)
        return equity

```


## discrimination_iteration2/corrected_manager.py

```python
"""Bounded functionality baseline; no fitted utility, fabricated features or I/O.

The caller supplies dated native niche matches (including native center distances),
feature eligibility and native decisions. GA4 is research-only and never traded.
"""
from dataclasses import dataclass, replace
from datetime import date as iso_date
from math import isfinite

from engines.portfolio_replay.kernel import Replay, Signal
from .hierarchical_search import RoutedCandidate, tier
from .native_signal_contract import normalize_proposals
from .position_fill_book import FillBook
from .capital_competition import Opportunity, compare
from .progressive_scaling import allowed_target
from .native_shadow_trade_book import ShadowBook
from .causal_calibration import Calibrator, TradeOutcome
from .shadow_learning_interface import ShadowLearningView
from .evolved_selection_policy import score as selection_score
from .causal_market_state import state_from_closes
from .genome_identity import GenomeIdentityRegistry


@dataclass(frozen=True)
class NicheObservation:
    as_of: str
    trained_through: str
    source: str
    # Only matches returned by the native classifier; never inferred here.
    matches: tuple  # (niche identity, native center distance)
    native_controller: str | None = None

    def controlling(self, date):
        if self.as_of != date or not self.source:
            raise ValueError('dated native niche observation required')
        if iso_date.fromisoformat(self.trained_through) >= iso_date.fromisoformat(date):
            raise ValueError('niche model must precede decision')
        names = [name for name, _ in self.matches]
        if len(names) != len(set(names)):
            raise ValueError('duplicate niche match')
        if any(not name or not isfinite(distance) or distance < 0
               for name, distance in self.matches):
            raise ValueError('invalid native center distance')
        if self.native_controller is not None:
            if self.native_controller not in names:
                raise ValueError('native controller must be a qualifying niche')
            return self.native_controller
        return min(self.matches, key=lambda x: (x[1], x[0]))[0] if self.matches else None


@dataclass(frozen=True)
class Candidate:
    chromosome_id: str
    family: str
    niche: str | None
    stop: float
    # Caller supplies dated gap loss estimate; missing information assumes total loss.
    gap_risk: float = 1.0


def run_slice(days, candidates, *, classify, eligible, native, cash=100000.,
              max_sessions=64, max_stocks=32, selector=None, defense_at_close=None,
              manager_override=None, opportunity_at_close=None, conditional_ev=None,
              shadow_horizon=0, native_shadow=False, selection_genes=None,
              native_genomes=None, genome_registry=None, require_genome_identity=False, session_hook=None, retain_audit=True, funded_entry_scale=None, candidate_provider=None,
              fees=.001, spread=0., slippage=0., impact=0., mdd_limit=.20,
              allocation_priority=None, scaling_evidence=None):
    """Stream dated bars through native callbacks and a single funded bank.

    classify(ticker, date) -> NicheObservation; eligible(candidate,ticker,date)
    -> explicit bool; native(candidate,ticker,date,held) -> NativeProposal/None.
    Callbacks receive only today's cutoff and filled incumbent state. They must
    query sources at that cutoff; this API cannot certify caller provenance.
    conditional_ev must supply comparable marginal net return per dollar, after
    all execution costs and risk/reliability adjustments, using the same horizon.
    Unavailable estimates abstain. Niche tiers apply within each ticker, then
    all funded increases compete globally. No raw family score is used as EV.
    SGOV is unavailable on this seam: explicit zero-yield settled-cash fallback.
    allocation_priority(c,t,date,controlling,matches,net_ev) optionally orders
    funded increases only; finite signed priorities never change EV admission.
    scaling_evidence(c,t,date,held,realized,nav_history) optionally supplies causal
    ScaleEvidence for native ADDs; the kernel validates evidence and risk.
    Defaults retain the 10% cap and EV queue ordering.
    """
    if selector is not None:
        raise ValueError('unpriced selector disabled; provide comparable conditional_ev')
    candidates = tuple(sorted(candidates, key=lambda c: (c.family, c.chromosome_id)))
    keys = [(c.family, c.chromosome_id) for c in candidates]
    if not 1 <= len(candidates) <= 20000 or len(keys) != len(set(keys)):
        raise ValueError('require 1..20000 unique candidates')
    if any(c.family not in ('GA6', 'GA7', 'HORIZONS') or
           not c.chromosome_id or not 0 < c.stop <= .02 or
           not isfinite(c.gap_risk) or not 0 <= c.gap_risk <= 1 for c in candidates):
        raise ValueError('trading candidate invalid; GA4 is research-only')
    if type(max_sessions) is not int or not 2 <= max_sessions <= 10000:
        raise ValueError('require 2..10000 sessions')
    if type(max_stocks) is not int or not 1 <= max_stocks <= 10000:
        raise ValueError('require 1..10000 stocks')
    if not isfinite(cash) or cash <= 0:
        raise ValueError('positive funded cash required')
    if require_genome_identity and (native_genomes is None or genome_registry is None):
        raise ValueError('production requires registered native genomes')
    if native_genomes is not None:
        if set(native_genomes) != set(keys):
            raise ValueError('complete family-qualified native genomes required')
        registry = genome_registry if genome_registry is not None else GenomeIdentityRegistry()
        for family, chromosome_id in keys:
            if require_genome_identity:
                registry.require(family, chromosome_id, native_genomes[(family, chromosome_id)])
            else:
                registry.register(family, chromosome_id, native_genomes[(family, chromosome_id)])
    elif genome_registry is not None:
        raise ValueError('native genomes required for registry verification')
    genome_hashes = {key: registry.by_id[key] for key in keys} if native_genomes is not None else {}
    bank = Replay(cash=cash, settlement_sessions=1, fees=fees, spread=spread,
                  slippage=slippage, impact=impact, mdd_limit=mdd_limit)
    book = FillBook()
    by_owner = dict(zip(keys, candidates))
    decisions = []
    shadow_ledger = []
    shadow_open = []
    shadow_book = ShadowBook(genome_hashes=genome_hashes) if native_shadow else None
    shadow_calibrator = Calibrator(min_samples=5) if native_shadow else None
    shadow_outcomes = []
    shadow_learning = ShadowLearningView() if native_shadow else None
    learning_snapshots = []
    close_history = {}
    if type(shadow_horizon) is not int or not 0 <= shadow_horizon <= 20:
        raise ValueError('shadow horizon must be 0..20 sessions')
    pending = {}
    last = None
    for session, (date, bars) in enumerate(days):
        iso_date.fromisoformat(date)
        if session >= max_sessions or (last is not None and date <= last):
            raise ValueError('bounded chronological sessions required')
        if not bars or len(bars) > max_stocks or set(book.positions) - set(bars):
            raise ValueError('bounded complete market bars required')
        last = date
        for t,bar in bars.items():
            close_history.setdefault(t,[]).append(bar.close)
        if native_shadow:
            matured = shadow_book.open_session(session, bars)
            for outcome in matured:
                shadow_calibrator.record(outcome)
                shadow_learning.ingest(outcome)
                shadow_outcomes.append(outcome)
        if native_shadow:
            snapshot = shadow_learning.snapshot(session) if session_hook is None else {}
            snapshot['genome_hashes'] = genome_hashes
            if retain_audit: learning_snapshots.append(snapshot)
        if session_hook is not None:
            session_hook(session, date, matured if native_shadow else [])
        if candidate_provider is not None:
            updated = tuple(sorted(candidate_provider(), key=lambda c: (c.family,c.chromosome_id)))
            if updated != candidates:
                updated_keys = [(c.family,c.chromosome_id) for c in updated]
                if len(updated_keys) != len(set(updated_keys)) or not set(keys) <= set(updated_keys):
                    raise ValueError('evolution must preserve incumbent and shadow identities')
                for key in updated_keys:
                    registry.require(*key,native_genomes[key])
                    genome_hashes[key] = registry.by_id[key]
                candidates=updated;keys=updated_keys;by_owner=dict(zip(keys,candidates))
        if shadow_horizon:
            for trial in shadow_open:
                if trial['ticker'] not in bars:
                    raise ValueError('shadow ticker missing from bars')
                if session == trial['entry_session']:
                    trial['entry_price'] = bars[trial['ticker']].open
                if session == trial['entry_session'] + shadow_horizon:
                    trial['exit_price'] = bars[trial['ticker']].close
                    trial['exit_date'] = date
                    trial['gross_return'] = trial['exit_price'] / trial['entry_price'] - 1
                    trial['net_return_estimate'] = trial['gross_return'] - bank.round_trip_cost
                    trial['status'] = 'MATURED_FIXED_HORIZON'
                    shadow_ledger.append(trial)
            shadow_open = [t for t in shadow_open if t['status'] == 'OPEN']
        before = len(bank.ledger)
        for ticker, p in book.positions.items():
            p.shares *= bars[ticker].split
            p.entry /= bars[ticker].split
            p.basis /= bars[ticker].split
            p.peak /= bars[ticker].split
        bank.day(date, bars)
        for fill in bank.ledger[before:]:
            _, ticker, side, *_ = fill
            owner = pending[ticker] if side == 'BUY' else book.positions[ticker].owner
            book.apply(fill, owner, stop=by_owner[owner].stop, session=session)
        if set(book.positions) != set(bank.shares) or any(
                abs(p.shares-bank.shares[t]) > 1e-7 for t, p in book.positions.items()):
            raise ValueError(f'fill attribution mismatch at {date}: book_only={set(book.positions)-set(bank.shares)}, bank_only={set(bank.shares)-set(book.positions)}')
        nav = bank.nav[-1][1]
        if nav <= 0 or bank.cash < -1e-7:
            raise ValueError('invalid funded bank')
        defensive = False if defense_at_close is None else defense_at_close(date)
        if type(defensive) is not bool:
            raise ValueError('defense controller must return explicit boolean')
        # Flag the state known at this close. Do not pass it to day(defense=):
        # that would liquidate at an open preceding this close's observation.
        bank.nav[-1] = (*bank.nav[-1][:4], defensive)
        signals = []
        shadow_proposals = []
        shadow_contexts = {}
        pending = {}
        remaining = bank.cash / nav
        estimates = {}
        def estimate_for(candidate, ticker, controlling, matches):
            key = (candidate.family, candidate.chromosome_id, ticker)
            if key not in estimates:
                value = (conditional_ev(candidate, ticker, date, controlling, matches)
                         if conditional_ev is not None else None)
                if value is not None and (type(value) not in (int, float) or not isfinite(value)):
                    raise ValueError('conditional EV must be finite or unavailable')
                estimates[key] = value
            return estimates[key]
        for ticker in sorted(bars):
            observation = classify(ticker, date)
            if not isinstance(observation, NicheObservation):
                raise TypeError('native niche observation required')
            controlling = observation.controlling(date)
            position = book.positions.get(ticker)
            held = None
            if position:
                position.peak = max(position.peak, bars[ticker].close)
                held = {**book.held(ticker, bars[ticker].close, nav),
                        'shares': position.shares, 'peak': position.peak,
                        'entry_session': position.entry_session}
            pool = []
            audit = dict(date=date, ticker=ticker, defensive=defensive, controlling_niche=controlling,
                         matches=observation.matches, eligible=[], actions=[], selected=None,
                         opportunity_evaluations=[])
            if defensive:
                if position:
                    signals.append(Signal(ticker, position.owner[0], position.owner[1], 0.))
                    pending[ticker] = position.owner
                    audit['selected'] = (*position.owner, 'DEFENSE_EXIT', 0.)
                if retain_audit: decisions.append(audit)
                continue
            for c in candidates:
                owner = (c.family, c.chromosome_id)
                # The filled incumbent retains management even after niche drift
                # or loss of entry eligibility. Challengers cannot manage it.
                if position:
                    if owner != position.owner:
                        continue
                else:
                    # Related means explicitly supplied qualifying native matches.
                    # No historical center relationship or provenance is inferred.
                    route = tier(RoutedCandidate(c.chromosome_id, c.family, c.niche), controlling)
                    if route is None and c.niche not in dict(observation.matches):
                        continue
                    gate = eligible(c, ticker, date)
                    if type(gate) is not bool:
                        raise ValueError('explicit native chromosome eligibility required')
                    if not gate:
                        continue
                audit['eligible'].append(owner)
                p = native(c, ticker, date, held)
                if p is None:
                    continue
                normalize_proposals([p], date)
                if (p.family, p.chromosome_id) != owner or p.ticker != ticker:
                    raise ValueError('native identity mismatch')
                if p.model_trained_through >= date:
                    raise ValueError('native model must precede decision')
                if position is None and p.action != 'ENTER':
                    raise ValueError('non-entry without incumbent')
                if position is not None and p.action == 'ENTER':
                    raise ValueError('incumbent cannot enter again')
                if p.action in ('ENTER', 'ADD') and p.target_weight <= 0:
                    continue  # zero is abstention, never a minimum allocation
                audit['actions'].append((owner, p.action, p.target_weight))
                pool.append((c, p))
            selected = None
            if position:
                selected = pool[0] if pool else None
            elif pool:
                # Family-qualified identities avoid cross-family alias collisions.
                ranked = []
                for c, p in pool:
                    estimate = estimate_for(c, ticker, controlling, observation.matches)
                    audit['opportunity_evaluations'].append(dict(owner=(c.family, c.chromosome_id),
                        marginal_net_ev=estimate, positive=estimate is not None and estimate > 0))
                    if estimate is None:
                        continue
                    if type(estimate) not in (float, int) or not isfinite(estimate):
                        raise ValueError('conditional EV must be finite or unavailable')
                    if estimate <= 0 or bank.admission_halted:
                        continue
                    route = tier(RoutedCandidate(c.chromosome_id, c.family, c.niche), controlling)
                    priority = 0 if c.niche == controlling and controlling is not None else (1 if route is None else 2)
                    distance = next((dist for name, dist in observation.matches if name == c.niche), float('inf'))
                    value = estimate
                    if selection_genes is not None:
                        value = selection_score(selection_genes,c,controlling,observation.matches,
                            estimate,learning_snapshots[-1] if native_shadow else None,
                            state_from_closes(close_history[ticker],session))
                        if value is None:
                            continue
                        if not isfinite(value) or value <= 0:
                            continue
                    ranked.append((priority, -value, distance, c.family, c.chromosome_id, c, p))
                ranked.sort(key=lambda item: item[:5])
                selected = (ranked[0][-2], ranked[0][-1]) if ranked else None
            if shadow_horizon and position is None and not defensive:
                for c, proposal in pool:
                    if proposal.action != 'ENTER':
                        continue
                    ev = estimate_for(c, ticker, controlling, observation.matches)
                    chosen = selected is not None and (c.family, c.chromosome_id) == (selected[0].family, selected[0].chromosome_id)
                    distance = next((dist for name, dist in observation.matches if name == c.niche), None)
                    shadow_open.append(dict(date=date, ticker=ticker, owner=(c.family,c.chromosome_id),
                        controlling_niche=controlling, specialized_niche=c.niche, niche_distance=distance,
                        conditional_ev=ev, selected=chosen, entry_session=session+1,
                        status='OPEN', horizon=shadow_horizon))
            if native_shadow:
                for c in candidates:
                    skey=(c.family,c.chromosome_id,ticker)
                    shadow_held=shadow_book.positions.get(skey)
                    if shadow_held is None:
                        continue  # Existing native shadow positions need their own exit decisions.
                    shadow_equity=shadow_held['cash']+shadow_held['units']*bars[ticker].close
                    shadow_held['peak']=max(shadow_held.get('peak',shadow_held['entry_price']),bars[ticker].close)
                    sp=native(c,ticker,date,{'shadow':True,'entry_session':shadow_held['entry_session'],
                        'entry':shadow_held['entry_price'],
                        'shares':shadow_held['units'],'peak':shadow_held['peak'],
                        'weight':shadow_held['units']*bars[ticker].close/shadow_equity})
                    if sp is not None:
                        normalize_proposals([sp],date)
                        if (sp.family,sp.chromosome_id,sp.ticker)!=skey or sp.model_trained_through>=date:
                            raise ValueError('invalid native shadow identity/cutoff')
                        if sp.action in ('EXIT','ADD','REDUCE'):shadow_proposals.append(sp)
                for c in candidates:
                    skey=(c.family,c.chromosome_id,ticker)
                    if skey in shadow_book.positions or skey in shadow_book.pending:
                        continue
                    # Shadow all eligible library members, including noncontrolling niches.
                    # The funded selection loop retains its niche-first restriction.
                    gate=eligible(c,ticker,date)
                    if type(gate) is not bool:raise ValueError('explicit shadow eligibility required')
                    if not gate:continue
                    entry=next((p for owner,p in pool if owner==c),None)
                    if entry is None:
                        entry=native(c,ticker,date,None)
                        if entry is None:continue
                        normalize_proposals([entry],date)
                        if (entry.family,entry.chromosome_id,entry.ticker)!=skey or entry.model_trained_through>=date:
                            raise ValueError('invalid shadow entry identity/cutoff')
                    if entry.action!='ENTER':continue
                    shadow_proposals.append(entry)
                    distance=next((d for n,d in observation.matches if n==c.niche), None)
                    shadow_contexts[skey]=(controlling,c.niche,distance)

            if selected:
                c, p = selected
                current = held['weight'] if held else 0.
                target = p.target_weight
                marginal_ev = 0.
                evidence = None
                other_risk = 0.
                if p.action in ('ENTER', 'ADD'):
                    marginal_ev = estimate_for(c, ticker, controlling, observation.matches)
                    if marginal_ev is not None and (type(marginal_ev) not in (int, float) or not isfinite(marginal_ev)):
                        raise ValueError('conditional EV must be finite or unavailable')
                    if marginal_ev is None or marginal_ev <= 0 or bank.admission_halted:
                        target = current
                        marginal_ev = 0.
                evidence = None
                other_risk = 0.
                if position is None and funded_entry_scale is not None:
                    scale = funded_entry_scale()
                    if not isfinite(scale) or not 0 < scale <= 1:
                        raise ValueError('invalid funded entry scale')
                    target *= scale
                if p.action == 'HOLD':
                    target = current
                elif p.action in ('ENTER', 'ADD'):
                    if p.action == 'ADD' and target > current and marginal_ev > 0 and scaling_evidence is not None:
                        evidence = scaling_evidence(c, ticker, date, held, tuple(dict(x) for x in book.realized), tuple(bank.nav))
                        other_risk = sum(pos.shares * bars[t].close / nav *
                            (max(by_owner[pos.owner].stop, by_owner[pos.owner].gap_risk) + bank.round_trip_cost)
                            for t, pos in book.positions.items() if t != ticker)
                    desired = max(0., min(.20 if evidence is not None else .10, target)-current)
                    target = current + desired
                elif p.action == 'REDUCE':
                    target = min(current, target)
                action = p.action
                if position and manager_override is not None:
                    override = manager_override(ticker, date, held, (c, p), tuple(audit['actions']))
                    if override is not None:
                        if (not isinstance(override, tuple) or len(override) != 2 or
                            type(override[0]) not in (int, float) or
                            not isfinite(override[0]) or not 0 <= override[0] <= current or
                            not isinstance(override[1], str) or not override[1]):
                            raise ValueError('manager override requires funded reduction and reason')
                        raise ValueError('unverified manager override disabled: requires funded competing opportunity evidence')
                audit['selected'] = (c.family, c.chromosome_id, action, target)
                if action != 'HOLD' and (action in ('REDUCE', 'EXIT', 'MANAGER_EXIT', 'MANAGER_REDUCE') or target > current):
                    priority_score = marginal_ev
                    if target > current and allocation_priority is not None:
                        priority_score = allocation_priority(c, ticker, date, controlling, observation.matches, marginal_ev)
                        if type(priority_score) not in (int, float) or not isfinite(priority_score):
                            raise ValueError('allocation priority must be finite')
                    audit['marginal_net_ev'] = marginal_ev
                    audit['allocation_priority'] = priority_score
                    audit['scaling_evidence'] = None if evidence is None else vars(evidence)
                    signals.append(Signal(ticker, c.family, c.chromosome_id, target,
                                          score=priority_score, scaling_evidence=evidence, stop_distance=c.stop,
                                          gap_risk=c.gap_risk, other_equity_risk=other_risk))
                    pending[ticker] = (c.family, c.chromosome_id)
            if retain_audit: decisions.append(audit)
        # Compete across funded tickers only with causal, comparable estimates.
        # Sales settle after execution; their proceeds are never credited to
        # today's buying budget. The challenger must remain eligible tomorrow.
        if opportunity_at_close is not None and not defensive:
            entrants = [s for s in signals if s.ticker not in book.positions and s.target_weight > 0]
            committed = sum(s.target_weight for s in entrants)
            available = max(0., bank.cash / nav)
            for ticker, position in sorted(book.positions.items()):
                if committed <= available + 1e-10:
                    break
                if any(s.ticker == ticker for s in signals):
                    continue  # respect incumbent native exit/reduction/add
                held_weight = position.shares * bars[ticker].close / nav
                incumbent = opportunity_at_close(date, ticker, position.owner, True)
                if not isinstance(incumbent, Opportunity) or incumbent.owner != position.owner or incumbent.ticker != ticker:
                    raise ValueError('comparable funded incumbent estimate required')
                challengers = []
                for entry in entrants:
                    estimate = opportunity_at_close(date, entry.ticker, (entry.family, entry.chromosome), False)
                    if not isinstance(estimate, Opportunity) or estimate.owner != (entry.family, entry.chromosome) or estimate.ticker != entry.ticker:
                        raise ValueError('comparable challenger estimate required')
                    challengers.append(estimate)
                transfer = compare(incumbent, challengers, held_weight=held_weight,
                                   free_weight=available, required_weight=committed)
                if transfer is None:
                    continue
                target = max(0., held_weight - transfer.released_weight)
                signals.append(Signal(ticker, *position.owner, target))
                pending[ticker] = position.owner
                available += transfer.released_weight  # forecast only, not spendable
                decisions.append({'date': date, 'ticker': ticker, 'action': 'COMPETITIVE_RELEASE',
                                  'incumbent': transfer.incumbent, 'challenger': transfer.challenger,
                                  'challenger_ticker': transfer.challenger_ticker,
                                  'released_weight': transfer.released_weight,
                                  'net_advantage': transfer.net_advantage,
                                  'settlement_deferred': True})
        # Reserve only settled cash, fees and execution allowances, in global
        # marginal net-EV order. Sales and receivables cannot fund this close.
        remaining = bank.cash / nav
        ranked_signals = []
        reserved_loss = 0.
        for signal in sorted(signals, key=lambda s: (-s.score, s.ticker, s.family, s.chromosome)):
            current = bank.shares.get(signal.ticker, 0.) * bars[signal.ticker].close / nav
            if signal.target_weight > current:
                per_dollar_loss = max(signal.stop_distance, signal.gap_risk) + bank.round_trip_cost
                risk_cap = bank.max_equity_risk / per_dollar_loss if per_dollar_loss else 0.
                requested = signal.target_weight
                cap_target = requested
                # Evidence approval precedes cash reservation. A denied scale
                # request is not permission to top up a drifting ordinary holding.
                if signal.scaling_evidence is not None:
                    cap_target = allowed_target(current, requested, signal.scaling_evidence,
                        stop_distance=signal.stop_distance, gap_risk=signal.gap_risk,
                        max_equity_risk=bank.max_equity_risk)
                    if cap_target <= .10 + 1e-12:
                        cap_target = current
                    # Mandatory limit is per trade (entire candidate position), not portfolio aggregate.
                approved = max(current, min(cap_target, risk_cap))
                desired = max(0., approved - current)
                for audit in reversed(decisions):
                    if audit.get('ticker') == signal.ticker and audit.get('date') == date and audit.get('selected'):
                        audit['reservation'] = dict(requested=requested, current=current,
                            cap_target=cap_target, approved=approved,
                            cap_rejected=cap_target < requested - 1e-12,
                            risk_rejected=min(cap_target, risk_cap) < cap_target - 1e-12)
                        break
                funded = min(desired, remaining / ((1 + bank.friction) * (1 + bank.fees)))
                reserved_loss += funded * per_dollar_loss
                remaining = max(0., remaining - funded * (1 + bank.friction) * (1 + bank.fees))
                signal = replace(signal, target_weight=current + funded)
                for audit in reversed(decisions):
                    if audit.get('ticker') == signal.ticker and audit.get('date') == date and audit.get('selected'):
                        audit['selected'] = (*audit['selected'][:3], signal.target_weight)
                        audit['funding_reason'] = ('GLOBAL_PRIORITY' if allocation_priority is not None else 'GLOBAL_NET_EV') if funded else 'NO_SETTLED_CASH_OR_RISK_BUDGET'
                        break
                if funded <= 0:
                    continue
            ranked_signals.append(signal)
        signals = ranked_signals
        if native_shadow:
            shadow_book.close_session(session,shadow_proposals,shadow_contexts)
        bank.pending = signals
    if len(bank.nav) < 2:
        raise ValueError('require at least two sessions')
    if shadow_horizon:
        shadow_ledger.extend(shadow_open)
    return dict(scope='FUNCTIONAL_RESEARCH_BASELINE', learning_snapshots=learning_snapshots,
                native_shadow_outcomes=shadow_outcomes,
                native_shadow_open=dict(shadow_book.positions) if native_shadow else {},
                native_shadow_calibrator=shadow_calibrator if native_shadow else None,
                shadow_markouts=shadow_ledger,
                shadow_method=('NATIVE_POSITION_EXIT_REPLAY' if native_shadow else
                               'FIXED_HORIZON_MARKOUT_NOT_NATIVE_EXIT_REPLAY'), decisions=decisions,
                ledger=bank.ledger, nav=bank.nav, realized=book.realized,
                pending=list(bank.pending), unsettled=list(bank.unsettled),
                owners={t: p.owner for t, p in book.positions.items()},
                risk_audit=bank.risk_audit, drawdowns=bank.drawdowns,
                max_drawdown=bank.max_drawdown, admission_halted=bank.admission_halted,
                mdd_policy={'ceiling': bank.mdd_limit, 'breached': bank.admission_halted,
                            'feasible': not bank.admission_halted,
                            'action': 'LATCH_NEW_RISK_ADMISSION_KEEP_NATIVE_EXITS',
                            'guaranteed_loss_ceiling': False},
                liquidity={'mode': 'SAFE_SETTLED_CASH_FALLBACK', 'sgov_enabled': False,
                           'reason': 'No verified SGOV price/yield/pay-date adapter on run_slice',
                           'cash_yield_daily': 0., 'settled_cash': bank.cash,
                           'unsettled_cash': sum(v for _, v in bank.unsettled)},
                costs={'fees': fees, 'spread': spread, 'slippage': slippage,
                       'impact': impact, 'round_trip_allowance': bank.round_trip_cost},
                launch_ready=False)

```


## discrimination_iteration2/experiment.py

```python
#!/usr/bin/env python3
"""Independent injected-signal diagnostic; no production writes or oracle decision inputs."""
import sys,json,math,random,statistics as st,time,subprocess,gzip,csv,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent/'opportunity_evaluator_fix'))
import importlib.util
spec=importlib.util.spec_from_file_location('previous_evaluator',OUT.parent/'opportunity_evaluator_fix/experiment.py')
b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
sys.path.remove(str(OUT.parent/'opportunity_evaluator_fix'))
m,k,r,s=b.m,b.k,b.r,b.s
TIERS,EDGES,tier,infer,observed=b.TIERS,b.EDGES,b.tier,b.infer,b.observed
sha=b.sha

def isotonic(values,weights):
    blocks=[]
    for i,(v,w) in enumerate(zip(values,weights)):
        blocks.append([i,i,v*w,w])
        while len(blocks)>1 and blocks[-2][2]/blocks[-2][3]>blocks[-1][2]/blocks[-1][3]:
            q=blocks.pop();p=blocks.pop();blocks.append([p[0],q[1],p[2]+q[2],p[3]+q[3]])
    result=[0.]*len(values)
    for lo,hi,v,w in blocks:result[lo:hi+1]=[v/w]*(hi-lo+1)
    return result

def generate(seed,scenario):
    """Truth separately returned for scoring. Sensors are injected noisy PIT measurements.

    Independent sensor RNG keeps tape outcomes identical across scenario variants.
    Sensor1 sd .30 and sensor2 sd .50 latent-class units; inverse-variance fusion.
    No observable change flag is provided at inversion.
    """
    rng=random.Random(seed);sensor=random.Random(seed+90000)
    coarse=[];features=[];pred=[];truth=[];rets=[];mu=(-.012,-.004,0.,.004,.012)
    for i in range(252):
        common=rng.gauss(0,.003);cc=[];ff=[];pp=[];tt=[];rr=[]
        for j in range(24):
            z=rng.randrange(5);c=z if rng.random()<.8 else rng.randrange(5)
            net=mu[z]+common+rng.gauss(0,.008)
            # Null: sensors and coarse feature independent of the outcome class.
            source=sensor.randrange(5) if scenario=='null' else z
            x=source+sensor.gauss(0,.30);y=source+sensor.gauss(0,.50)
            f=max(0,min(4,int(math.floor((x/.09+y/.25)/(1/.09+1/.25)+.5))))
            if scenario=='null':c=sensor.randrange(5)
            if scenario=='reversal' and i>=126:c=4-c;f=4-f
            prediction=.010-mu[c] if scenario in ('misleading','null','reversal') else mu[c]
            gross=(1+net)*(1+s.FRICTION)*(1+s.COSTS['fees'])/((1-s.FRICTION)*(1-s.COSTS['fees']))-1
            cc.append(c);ff.append(f);pp.append(prediction);tt.append(mu[z]);rr.append(gross)
        coarse.append(cc);features.append(ff);pred.append(pp);truth.append(tt);rets.append(rr)
    prices=[100.+j for j in range(24)];days=[]
    for i,d in enumerate(s.DATES):
        if i>=2:prices=[p*(1+v) for p,v in zip(prices,rets[i-2])]
        days.append((d,{t:k.Bar(prices[j],prices[j]) for j,t in enumerate(s.TICKERS)}))
    return days,coarse,features,pred,truth

def estimate(grouped):
    raw=[st.mean(v) if v else 0. for v in grouped];weights=[max(1,len(v)) for v in grouped]
    center=sum(v*w for v,w in zip(raw,weights))/sum(weights)
    slope=sum((i-2)*(v-center)*w for i,v,w in zip(range(5),raw,weights))/sum((i-2)**2*w for i,w in enumerate(weights))
    # Hierarchical shrinkage: six pseudo dates toward the learned linear parent.
    shrunk=[(v*w+6*(center+slope*(i-2)))/(w+6) for i,(v,w) in enumerate(zip(raw,weights))]
    sign=1 if slope>=0 else -1
    return [sign*v for v in isotonic([sign*v for v in shrunk],weights)]

def predict(days,features):
    ledger=[];states=[];alarms=[];quarantine=-1;floor=0
    bysignal={};residuals={}
    for now in range(252):
        for row in bysignal.get(now-3,[]):
            try:row['realized_net']=observed(days,row['index'],row['j']);row['missingness']='OBSERVED';row['available_index']=now
            except (KeyError,IndexError,TypeError):row['missingness']='MISSING'
        matured=[z for i in range(max(floor,now-93),now-2) for z in bysignal.get(i,[]) if z['missingness']=='OBSERVED']
        grouped=[];dated=[];cal=[];drift=[]
        for c in range(5):
            dates={}
            for z in matured:
                if z['signal']==c:dates.setdefault(z['index'],[]).append(z['realized_net'])
            dv=[(i,st.mean(v)) for i,v in sorted(dates.items())];dated.append(dv)
            grouped.append([v for _,v in dv]);cal.append([v for i,v in dv if i>=now-33])
            old=[v for i,v in dv if i<now-11];recent=[v for i,v in dv if i>=now-11]
            if len(old)>=24 and len(recent)>=7 and abs(st.mean(old)-st.mean(recent))>max(.004,3*math.hypot(b.se(old),b.se(recent))):drift.append(c)
        if drift and now>quarantine:
            alarms.append(dict(index=now,cells=drift));quarantine=now+20;floor=now-10
        means=estimate(grouped);identifiable=max(means)-min(means)>=.003
        cells=[]
        for c in range(5):
            values=grouped[c];cv=cal[c];mean=means[c]
            bias=abs(st.mean(cv)-mean) if cv else 1.
            radius=max(2.58*b.se(values),bias+1.64*b.se(cv)) if values and cv else 1.
            # Shrinkage displacement is additional model uncertainty, never hidden.
            if values:radius+=abs(mean-st.mean(values))
            ntrain=sum(i<now-33 for i,v in dated[c]);ncal=len(cv)
            label=infer(mean,radius,ntrain,ncal)
            # Causal rolling interval reliability of forecasts as issued, date clustered.
            rv=[]
            for i in range(max(0,now-63),now-2):
                rows=[z for z in bysignal.get(i,[]) if z['signal']==c and z['missingness']=='OBSERVED' and z['forecast_ready']]
                if rows:rv.append(st.mean(z['realized_net']-z['inferred_net'] for z in rows))
            reliability=st.mean(abs(v)<=.006 for v in rv) if rv else 0.
            reason='CONFIDENT'
            if now<=quarantine:reason='DRIFT_QUARANTINE'
            elif not identifiable:reason='NO_IDENTIFIABLE_SIGNAL'
            elif ntrain<20 or ncal<20:reason='INSUFFICIENT_MATURE_DATES'
            elif len(rv)>=20 and abs(st.mean(rv))>max(.003,2.58*b.se(rv)):reason='UNRELIABLE_RESIDUAL_BIAS'
            elif label=='UNKNOWN':reason='BOUNDARY_UNCERTAINTY'
            if reason!='CONFIDENT':label='UNKNOWN'
            cells.append(dict(mean=mean,radius=radius,ntrain=ntrain,ncal=ncal,label=label,reason=reason,reliability=reliability,reliability_dates=len(rv),latest_outcome_signal=max((i for i,v in dated[c]),default=-3)))
        states.append(cells)
        if now<250:
            rows=[]
            for j in range(24):
                c=cells[features[now][j]]
                rows.append(dict(index=now,j=j,signal=features[now][j],execution_index=now+1,maturity_index=now+2,available_index=None,realized_net=None,missingness='PENDING',inferred_net=c['mean'],radius=c['radius'],inferred_tier=c['label'],reason=c['reason'],forecast_ready=min(c['ntrain'],c['ncal'])>=20))
            ledger.extend(rows);bysignal[now]=rows
    return states,ledger,alarms

def writecsv(name,rows):
    if not rows:return
    with (OUT/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def diagnose():
    """Prior saved outcomes only; descriptive attribution, no portfolio/tuning."""
    reasons={};cells={};unknown=0;center_middle=0;narrow=0;gate_middle=0
    p=OUT.parent/'opportunity_evaluator_fix/opportunities.jsonl.gz'
    with gzip.open(p,'rt') as f:
        for line in f:
            z=json.loads(line)
            if not 126<=z['index']<250:continue
            reason=z['reason'];reasons[reason]=reasons.get(reason,0)+1
            key=(z['scenario'],z['signal']);v=cells.setdefault(key,[])
            if z['realized_net'] is not None:v.append(z['realized_net'])
            if z['inferred_tier']=='UNKNOWN':
                unknown+=1
                if tier(z['inferred_net']) in TIERS[1:4]:
                    center_middle+=1
                    if z['radius']<.002:narrow+=1
                    if b.tier(z['inferred_net']-z['radius'])==b.tier(z['inferred_net']+z['radius']):gate_middle+=1
    return dict(prior_reasons=reasons,unknown=unknown,middle_center_unknown=center_middle,middle_center_radius_below_half_band=narrow,middle_interval_fits_but_gated=gate_middle,realized_cell_means={str(k):st.mean(v) for k,v in cells.items()},conclusions=['No tier dispatch bug: absolute infer emits all five tiers in unit tests. Bands are disjoint, not overlapping.','80% faithful coarse sensor mixes neighboring latent states; conditional cell EV is not individual latent EV.','Middle bands have half-width .002. Diagnostic radius and window bias dominate when center lies near boundaries.','All samples are date clustered: 24 stocks are not 24 independent dates. Prior recent calibration has at most 21 dates.','Global quarantine and signal-identifiability gates additionally suppress coverage; counters isolate these from interval rejection.','Original manager delegates quality to caller conditional_ev; causal ledger handles outcome availability, not inference validity.'])

def main():
    start=time.monotonic();plan=json.loads((OUT/'preregister.json').read_text());ph=sha(OUT/'preregister.json')
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(OUT),'-p','test_*.py','-v'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        (OUT/'report.json').write_text(json.dumps(dict(status='STOP_TEST_FAILURE',full_portfolio_replays=0)));raise SystemExit(result.returncode)
    sources=list(b.a.SOURCES)+[b.PRIOR/'corrected_manager.py',b.PRIOR/'corrected_kernel.py',Path(b.__file__),OUT/'experiment.py',OUT/'test_iteration2.py',OUT/'preregister.json']
    sources+=list((OUT.parent/'five_tier_discrimination').glob('*.py'))
    sources+=[OUT.parent/'five_tier_discrimination/report.json',OUT.parent/'opportunity_evaluator_fix/report.json',OUT.parent.parent/'mts_v5_manager_repair_20261031/v5_working_copy/engines/counterfactual_learning/causal_ledger.py']
    before={str(p):sha(p) for p in sources};diagnosis=diagnose();scores=[];metrics=[];attempts=0;opps=[];riskmax=0.;buys=0
    with gzip.open(OUT/'opportunities.jsonl.gz','wt') as of,gzip.open(OUT/'replays.jsonl.gz','wt') as rf:
        for seed in plan['seeds']:
            for scenario in plan['scenarios']:
                assert time.monotonic()-start<plan['max_seconds']
                days,coarse,f,p,truth=generate(seed,scenario)
                new,ledger,alarms=predict(days,f);previous,oldledger,oldalarms=b.causal_predictions(days,coarse,p)
                for variant,features,cells,als in [('iteration2',f,new,alarms),('previous_repaired',coarse,previous,oldalarms)]:
                    score,rows=b.discrimination(days,features,p,truth,cells)
                    score.pop('cells',None)
                    scores.append(dict(seed=seed,scenario=scenario,variant=variant,alarms=als,reversal_lag=next((z['index']-126 for z in als if z['index']>=126),None) if scenario=='reversal' else None,**score))
                    for z in rows:
                        z.update(seed=seed,scenario=scenario,variant=variant);of.write(json.dumps(z)+'\n')
                    for t in (*TIERS,'UNKNOWN'):
                        v=[z for z in rows if z['inferred_tier']==t]
                        opps.append(dict(seed=seed,scenario=scenario,variant=variant,tier=t,n=len(v),coverage=len(v)/len(rows),precision=st.mean(z['true_ev_tier']==t for z in v) if v and t!='UNKNOWN' else None,realized_net=st.mean(z['realized_net'] for z in v) if v else None,abstained_positive_net_sum=sum(max(0,z['realized_net']) for z in v) if t=='UNKNOWN' else 0,abstained_signed_net_sum=sum(z['realized_net'] for z in v) if t=='UNKNOWN' else 0,abstained_positive_ev_sum=sum(max(0,z['true_ev']) for z in v) if t=='UNKNOWN' else 0))
                with gzip.open(OUT/f'ledger_{seed}_{scenario}.jsonl.gz','wt') as lf:
                    for z in ledger:lf.write(json.dumps(z)+'\n')
                for variant,features,cells,policy in [('iteration2',f,new,'tier10'),('previous_repaired',coarse,previous,'tier10'),('existing_ev10',coarse,previous,'existing_ev10')]:
                    assert attempts<plan['max_full_replays'] and time.monotonic()-start<plan['max_seconds']
                    attempts+=1;(OUT/'attempts.json').write_text(json.dumps(dict(attempts=attempts,seed=seed,scenario=scenario,variant=variant)))
                    kw=b.callbacks(features,p,cells,policy,days);evdays=days[126:252]
                    candidates=[m.Candidate(t,'GA7','synthetic',.02,s.GAPS[j]) for j,t in enumerate(s.TICKERS)]
                    result=m.run_slice(evdays,candidates,max_sessions=126,max_stocks=24,**s.COSTS,**kw)
                    metric,_=s.measure(result,evdays);metric['total_return']=metric['final_nav']/s.INITIAL-1
                    metric['cagr']=(metric['final_nav']/s.INITIAL)**2-1
                    metrics.append(dict(seed=seed,scenario=scenario,variant=variant,**metric))
                    # Independent full post-BUY position risk, reconstructed from actual fills/NAV.
                    previous_shares={};bydate={d:[] for d,_ in evdays}
                    for fill in result['ledger']:bydate[fill[0]].append(fill)
                    for (d,bars),nav in zip(evdays,result['nav']):
                        fills=bydate[d];opening=nav[1]+sum(z[5]+z[3]*abs(z[4]-bars[z[1]].open) for z in fills)
                        for z in fills:
                            if z[2]=='BUY':
                                loss=(previous_shares.get(z[1],0)+z[3])*bars[z[1]].open/opening*(max(.02,s.GAPS[int(z[1][3:])])+s.ROUND_TRIP)
                                assert loss<=.02+1e-10;buys+=1;riskmax=max(riskmax,loss)
                        previous_shares=nav[3]
                    rf.write(json.dumps(dict(seed=seed,scenario=scenario,variant=variant,ledger=result['ledger'],nav=result['nav'],risk=result['risk_audit'],decisions=result['decisions']))+'\n')
                print(f'{seed} {scenario} {attempts}/{plan["max_full_replays"]} elapsed={time.monotonic()-start:.1f}s',flush=True)
    paired=[]
    for z in metrics:
        if z['variant']!='iteration2':continue
        for comparator in ('previous_repaired','existing_ev10'):
            old=next(v for v in metrics if v['seed']==z['seed'] and v['scenario']==z['scenario'] and v['variant']==comparator)
            paired.append(dict(seed=z['seed'],scenario=z['scenario'],comparator=comparator,return_delta=z['total_return']-old['total_return'],mdd_delta=z['mdd']-old['mdd'],iteration2_return=z['total_return'],comparator_return=old['total_return']))
    assert all(sha(p)==h for p,h in before.items());assert sha(OUT/'preregister.json')==ph
    for score in scores:
        with (OUT/f'confusion_{score["seed"]}_{score["scenario"]}_{score["variant"]}.csv').open('w') as cf:
            w=csv.writer(cf);w.writerow(['true / predicted',*TIERS,'UNKNOWN'])
            for i,t in enumerate(TIERS):w.writerow([t,*score['confusion_ev'][i],score['unknown_by_ev_tier'][i]])
    writecsv('tier_metrics.csv',opps);writecsv('portfolio_runs.csv',metrics);writecsv('paired.csv',paired)
    report=dict(status='PASS' if all(z['status']=='PASS' for z in scores if z['variant']=='iteration2' and z['scenario']!='null') and all(z['coverage']==0 for z in scores if z['variant']=='iteration2' and z['scenario']=='null') else 'FAIL',execution_status='COMPLETE',full_portfolio_replays=attempts,elapsed_seconds=time.monotonic()-start,preregister_sha256=ph,source_sha256=before,production_sources_unchanged=True,diagnosis=diagnosis,discrimination=scores,portfolio_runs=metrics,paired=paired,tier_metrics=opps,independent_risk_audit=dict(actual_buys=buys,max_candidate_modeled_loss=riskmax,passed=True),limitations=plan['limitations'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(report['status'])
if __name__=='__main__':main()

```


## discrimination_iteration2/finalize.py

```python
"""Report-only saved-ledger aggregation plus preregistered independent static split ablation.
No portfolios, parameter changes, or choices based on holdout scores.
"""
import json,csv,gzip,statistics as st,shutil,hashlib,time
from pathlib import Path
import experiment as e
O=e.OUT

def main():
    final_start=time.monotonic()
    report=json.loads((O/'report.json').read_text());assert report['execution_status']=='COMPLETE'
    plan=json.loads((O/'preregister.json').read_text());summary=[];tierrows=[];port=[]
    for scenario in plan['scenarios']:
        for variant in ('iteration2','previous_repaired'):
            ss=[z for z in report['discrimination'] if z['scenario']==scenario and z['variant']==variant]
            counts={t:sum(z['counts'][t] for z in ss) for t in (*e.TIERS,'UNKNOWN')};n=sum(z['n'] for z in ss);assigned=n-counts['UNKNOWN']
            mat=[[sum(z['confusion_ev'][i][j] for z in ss) for j in range(5)] for i in range(5)]
            q=dict(scenario=scenario,variant=variant,coverage=assigned/n,accuracy=sum(mat[i][i] for i in range(5))/assigned if assigned else None,false_great=sum(z['false_great_on_terrible_count'] for z in ss),true_terrible=sum(z['true_ev_counts']['TERRIBLE'] for z in ss),monotonic_seeds=sum(z['monotonic'] for z in ss),populated_tiers=sum(counts[t]>0 for t in e.TIERS),reversal_lags=[z['reversal_lag'] for z in ss],alarm_counts=[len(z['alarms']) for z in ss],seed_passes=sum(z['status']=='PASS' for z in ss))
            q['false_great_rate']=q['false_great']/q['true_terrible'];summary.append(q)
            for t in (*e.TIERS,'UNKNOWN'):
                rows=[z for z in report['tier_metrics'] if z['scenario']==scenario and z['variant']==variant and z['tier']==t];count=counts[t]
                tierrows.append(dict(scenario=scenario,variant=variant,tier=t,n=count,coverage=count/n,precision=sum(z['precision']*z['n'] for z in rows if z['precision'] is not None)/count if count and t!='UNKNOWN' else None,realized_net=sum(z['realized_net']*z['n'] for z in rows if z['n'])/count if count else None,abstained_positive_net_sum=sum(z['abstained_positive_net_sum'] for z in rows),abstained_signed_net_sum=sum(z['abstained_signed_net_sum'] for z in rows),abstained_positive_ev_sum=sum(z['abstained_positive_ev_sum'] for z in rows)))
            for kind,key,uk in [('ev','confusion_ev','unknown_by_ev_tier'),('realized','confusion_realized','unknown_by_realized_tier')]:
                with (O/f'confusion_aggregate_{scenario}_{variant}_{kind}.csv').open('w') as f:
                    w=csv.writer(f);w.writerow(['true / predicted',*e.TIERS,'UNKNOWN'])
                    for i,t in enumerate(e.TIERS):w.writerow([t,*[sum(z[key][i][j] for z in ss) for j in range(5)],sum(z[uk][i] for z in ss)])
        for variant in plan['policies']:
            rows=[z for z in report['portfolio_runs'] if z['scenario']==scenario and z['variant']==variant]
            port.append(dict(scenario=scenario,variant=variant,n=len(rows),mean_return=st.mean(z['total_return'] for z in rows),mean_mdd=st.mean(z['mdd'] for z in rows),worst_mdd=max(z['mdd'] for z in rows),worst_return=min(z['total_return'] for z in rows)))
    # Static independent split ablation explicitly reserved in preregistration.
    static=[]
    for seed in plan['seeds']:
        for scenario in plan['scenarios']:
            days,coarse,features,p,truth=e.generate(seed,scenario)
            train=[];cal=[]
            for c in range(5):
                def vals(lo,hi):
                    out=[]
                    for i in range(lo,hi):
                        assert i+2<126
                        row=[e.observed(days,i,j) for j in range(24) if features[i][j]==c]
                        if row:out.append(st.mean(row))
                    return out
                train.append(vals(0,78));cal.append(vals(80,122))
            means=e.estimate(train);cells=[]
            for c in range(5):
                mean=means[c];radius=max(2.58*e.b.se(train[c]),abs(st.mean(cal[c])-mean)+1.64*e.b.se(cal[c]))+abs(mean-st.mean(train[c]))
                label=e.infer(mean,radius,len(train[c]),len(cal[c]))
                if max(means)-min(means)<.003:label='UNKNOWN'
                cells.append(dict(mean=mean,radius=radius,ntrain=len(train[c]),ncal=len(cal[c]),label=label))
            score,_=e.b.discrimination(days,features,p,truth,cells)
            static.append(dict(seed=seed,scenario=scenario,**score))
    reasons={};count=pending=observed=missing=0
    for p in O.glob('ledger_*.jsonl.gz'):
        with gzip.open(p,'rt') as f:
            for line in f:
                z=json.loads(line);count+=1
                assert z['execution_index']==z['index']+1 and z['maturity_index']==z['index']+2
                if z['realized_net'] is not None:observed+=1;assert z['available_index']>z['maturity_index']
                elif z['missingness']=='PENDING':pending+=1
                else:missing+=1
                if 126<=z['index']<250:reasons[z['reason']]=reasons.get(z['reason'],0)+1
    assert count==96000 and pending==384 and missing==0
    pairedsummary=[]
    for scenario in plan['scenarios']:
        for comparator in ('previous_repaired','existing_ev10'):
            rows=[z for z in report['paired'] if z['scenario']==scenario and z['comparator']==comparator]
            pairedsummary.append(dict(scenario=scenario,comparator=comparator,n=len(rows),mean_return_delta=st.mean(z['return_delta'] for z in rows),min_return_delta=min(z['return_delta'] for z in rows),max_return_delta=max(z['return_delta'] for z in rows),mean_mdd_delta=st.mean(z['mdd_delta'] for z in rows),return_wins=sum(z['return_delta']>0 for z in rows)))
    # Preregistered improvement criterion includes reversal protection, independently of portfolio gains.
    coverage_ok=all(next(q for q in summary if q['scenario']==sc and q['variant']=='iteration2')['coverage']>next(q for q in summary if q['scenario']==sc and q['variant']=='previous_repaired')['coverage'] for sc in plan['scenarios'] if sc!='null')
    rev=[next(q for q in summary if q['scenario']=='reversal' and q['variant']==v) for v in ('iteration2','previous_repaired')]
    protection=rev[0]['false_great_rate']<=rev[1]['false_great_rate']
    report.update(quality_aggregates=summary,portfolio_aggregates=port,paired_aggregates=pairedsummary,tier_aggregates=tierrows,static_independent_split_ablation=static,focused_tests=dict(passed=12,failed=0,before_portfolios=True),ledger_audit=dict(rows=count,observed=observed,pending=pending,missing=missing,unknown_reasons=reasons,strict_maturity=True),improvement_claim=dict(coverage_improved=coverage_ok,reversal_protection=protection,robust_five_way=report['status']=='PASS',claim=False),protocol_limitations=['Primary pooled estimator uses its recent calibration window in the point estimate. That window is a drift/stability diagnostic, not independent calibration. Independent static train0..77/cal80..121 ablation is reported separately and was reserved before execution.','Primary initial rolling split is33..92 older,93..123 recent, as explicitly stated before execution; it does not use nominal static ranges.','Static ablation radius formula is inherited unchanged from primary method, but static ablation has no rolling drift adaptation or residual gate and no portfolio replay; cannot certify the complete online bundle.'],missing_data=['Real PIT sensor time series with release timestamps, revision history, missingness, and measured noise covariance; injected Gaussian quality has no empirical realism validation.','Longer independent matured stable-regime dates for narrow middle economic bands; independent calibration episodes and more forward seeds/regimes.','Observable change predictors available before entry, or more rapid genuinely matured horizon outcomes to protect inversion before alarms.','A holding-horizon-specific net-return label and causal selection-aware portfolio counterfactual for attainable abstention cost.'])
    report['limitations']+=report['protocol_limitations']
    report['status']='FAIL' if not protection or not coverage_ok else report['status']
    report['source_sha256'][str(O/'finalize.py')]=e.sha(O/'finalize.py')
    report['reporting_seconds']=time.monotonic()-final_start
    report['total_compute_seconds']=report['elapsed_seconds']+report['reporting_seconds']
    assert report['total_compute_seconds']<=900
    (O/'execution.log').write_text(f"Tests:12 passed before portfolios. Replays:{report['full_portfolio_replays']}/48. Replay elapsed:{report['elapsed_seconds']:.3f}s. Reporting:{report['reporting_seconds']:.3f}s. Total:{report['total_compute_seconds']:.3f}s. Budget900s.\n")
    (O/'source_checksums.json').write_text(json.dumps(report['source_sha256'],indent=2))
    for name,rows in [('summary.csv',summary),('tier_aggregate.csv',tierrows),('portfolio_aggregate.csv',port),('paired_aggregate.csv',pairedsummary)]:e.writecsv(name,rows)
    for name in ('corrected_manager.py','corrected_kernel.py','source.patch'):shutil.copyfile(e.b.PRIOR/name,O/name)
    report['environment_note']='Runtime skill read; environment_status tool unavailable. Local filesystem experiment only; no network or credentials used.'
    (O/'report.json').write_text(json.dumps(report,indent=2))
    lines=['# Discrimination iteration2 — '+report['status'],'',f"Completed {report['full_portfolio_replays']}/48 paired full replays in {report['elapsed_seconds']:.1f}s, after all12 unit tests passed. No GA or production changes. No thresholds changed after evaluation.",'','No overall improvement or reliable five-way claim. Synthetic injected sensor bundle is more informative by construction; it is not measured real alpha. Primary online estimator pools recent calibration observations into its mean, so it does not meet independent calibration certification. The separately reported static ablation uses disjoint chronological train0–77/cal80–121/holdout126–249, with no holdout refitting.','', 'Decision boundary bands are TERRIBLE <−0.6%, POOR [−0.6%,−0.2%), AVERAGE [−0.2%,0.2%), GOOD [0.2%,0.6%), GREAT ≥0.6%. UNKNOWN remains explicit. Conditional mean bands do not guarantee the individual hidden latent class.','', '| Scenario | Evaluator | Coverage | Accuracy | False GREAT / true TERRIBLE | Monotone seeds |', '|---|---|---:|---:|---:|---:|']
    for q in summary:
        acc=f"{q['accuracy']:.1%}" if q['accuracy'] is not None else 'n/a'
        lines.append(f"| {q['scenario']} | {q['variant']} | {q['coverage']:.1%} | {acc} | {q['false_great']}/{q['true_terrible']} | {q['monotonic_seeds']}/4 |")
    lines+=['', 'Reversal lag (first post126 alarm minus126): '+str(rev[0]['reversal_lags'])+'; previous repaired: '+str(rev[1]['reversal_lags'])+'. Repeated/nuisance alarm counts are in summary.csv. Stronger measurements can increase damage before an unannounced reversal is observed; inspect false-GREAT protection separately from stable coverage.','', 'Prior diagnosis: no tier-dispatch bug or overlapping thresholds. The prior80% coarse sensor mixes states; the narrow0.4-percentage-point middle bands, at most21 recent independent date clusters, and train/calibration discrepancy produce intervals crossing boundaries. Global gates further suppress coverage. Exact counts and descriptive realized cell means are in report.json diagnosis; these are overlapping diagnostics, not causal ablation estimates.','', '| Scenario | Policy | Mean return | Mean MDD | Worst MDD |','|---|---|---:|---:|---:|']
    for q in port:lines.append(f"| {q['scenario']} | {q['variant']} | {q['mean_return']:.2%} | {q['mean_mdd']:.2%} | {q['worst_mdd']:.2%} |")
    lines+=['',f"Independent full post-BUY risk reconstruction: {report['independent_risk_audit']['actual_buys']} BUYs, maximum modeled entire-candidate loss {report['independent_risk_audit']['max_candidate_modeled_loss']:.8f} <=0.02. T+1 tested. No scale-up or terminal liquidation. Risk is modeled, not a realized-loss guarantee.",'', 'tier_aggregate.csv reports per-tier precision, coverage and forward realized net return. Confusion CSVs provide5×5 plus UNKNOWN, for latent EV and individual realized tiers. paired.csv and paired_aggregate.csv report matched return/MDD deltas against both comparators. Abstention costs are signed forgone net sum, positive realized sum and positive evaluator-EV sum per opportunity; these ex-post quantities ignore cash conflicts and are not attainable portfolio returns.','', 'Reproduce from repository root (requires the original MTS checkout and sibling dependencies):','```bash','python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/experiment.py > /tmp/discrimination_iteration2_execution.log 2>&1','python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/finalize.py','```','Runner stops on any failed test. It overwrites outputs; archive this directory before reproduction. preregister.json is frozen and its execution hash is in report.json. source_checksums.json covers reviewed/executed sources, local corrected manager/kernel and patch are preserved, all6000 eligible outcome events per tape are in ledger archives, held-out scoring records in opportunities.jsonl.gz, actual executions in replays.jsonl.gz. run.log is the external task transcript; execution.log contains replay progress extracted from it.','', 'Missing data and limitations:']
    lines+=['- '+v for v in report['missing_data']+report['limitations']]
    (O/'README.md').write_text('\n'.join(lines)+'\n')
    # Exclude active external transcript from manifest to avoid self-referential mutation.
    manifest={p.name:e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','run.log','finalize.log')}
    (O/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(dict(status=report['status'],summary=summary,risk=report['independent_risk_audit']),indent=2))
if __name__=='__main__':main()

```


## discrimination_iteration2/test_iteration2.py

```python
"""Contract tests authored before implementation and portfolio execution."""
import unittest
import experiment as e

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.days,cls.coarse,cls.f,cls.p,_=e.generate(17,'reversal')
        cls.states,cls.ledger,cls.alarms=e.predict(cls.days,cls.f)
    def test_maturation_all_eligible(self):
        self.assertEqual(len(self.ledger),6000)
        for z in self.ledger:
            self.assertEqual(z['execution_index'],z['index']+1)
            self.assertEqual(z['maturity_index'],z['index']+2)
            if z['available_index'] is not None:self.assertGreater(z['available_index'],z['maturity_index'])
        self.assertEqual(sum(z['realized_net'] is None for z in self.ledger),24)
    def test_pit_future_prices(self):
        days=list(self.days);days[128:]=[(d,{}) for d,b in days[128:]]
        states,ledger,_=e.predict(days,self.f)
        self.assertEqual(states[:129],self.states[:129])
        self.assertTrue(any(z['missingness']=='MISSING' for z in ledger))
    def test_future_features(self):
        f=[list(v) for v in self.f];f[128:]=[[0]*24 for _ in f[128:]]
        states,_,_=e.predict(self.days,f)
        self.assertEqual(states[:129],self.states[:129])
    def test_decision_api_no_truth_or_forecasts(self):
        import inspect
        self.assertEqual(list(inspect.signature(e.predict).parameters),['days','features'])
    def test_absolute_unknown(self):
        self.assertEqual(e.infer(0,.001,40,20),'AVERAGE')
        self.assertEqual(e.infer(0,.003,40,20),'UNKNOWN')
        self.assertEqual(e.infer(.01,.001,19,40),'UNKNOWN')
        self.assertTrue(all(c['label']=='UNKNOWN' for c in self.states[20]))
    def test_monotonic_pool(self):
        v=e.isotonic([0,2,1,4,3],[1]*5)
        self.assertEqual(v,[0,1.5,1.5,3.5,3.5])
        self.assertEqual(e.isotonic([3,2,1],[1]*3),[2,2,2])
    def test_drift_after_maturation(self):
        hit=[a for a in self.alarms if a['index']>=126]
        self.assertTrue(hit)
        self.assertGreaterEqual(hit[0]['index'],129)
        self.assertTrue(all(c['label']=='UNKNOWN' for c in self.states[hit[0]['index']]))
    def test_reliability_is_causal(self):
        for i,cells in enumerate(self.states):
            for c in cells:
                self.assertLess(c['latest_outcome_signal'],i-2)
                self.assertGreaterEqual(c['radius'],0)
                self.assertTrue(0<=c['reliability']<=1)
    def test_null_abstention(self):
        days,_,f,_,_=e.generate(18,'null');states,_,_=e.predict(days,f)
        self.assertTrue(all(c['label']=='UNKNOWN' for cells in states[:30] for c in cells))
    def test_cost(self):
        self.assertAlmostEqual(self.ledger[0]['realized_net'],e.observed(self.days,0,0))
    def test_entire_candidate_risk(self):
        ev=e.r.ScaleEvidence(50,2,True,.01,True,True,False)
        for gap in (.03,.24):
            bank=e.k.Replay(cash=95000,shares={'A':50},**e.s.COSTS)
            bank.pending=[e.k.Signal('A','GA7','a',.20,1,ev,.02,gap,.9)]
            bank.day('2030-01-02',{'A':e.k.Bar(100,100)})
            self.assertLessEqual(bank.risk_audit[-1]['modeled_equity_loss'],.02+1e-12)
            self.assertAlmostEqual(bank.shares['A']*100/100000,min(.20,.02/(gap+e.s.ROUND_TRIP)))
    def test_tplus1(self):
        bank=e.k.Replay(cash=0,shares={'A':1000},high_water=100000,settlement_sessions=1,**e.s.COSTS)
        bars={t:e.k.Bar(100,100) for t in ('A','B')}
        bank.pending=[e.k.Signal('A','GA7','a',0),e.k.Signal('B','GA7','b',.1,1,None,.02,.03)]
        bank.day('2030-01-02',bars);self.assertFalse(bank.shares);self.assertEqual(bank.cash,0);self.assertTrue(bank.unsettled)
        bank.pending=[e.k.Signal('B','GA7','b',.1,1,None,.02,.03)]
        bank.day('2030-01-03',bars);self.assertIn('B',bank.shares)

```


## opportunity_evaluator_fix/experiment.py

```python
#!/usr/bin/env python3
"""Frozen five-tier diagnostic. Standard library; experiment-local MTS seam only."""
import sys,json,time,math,random,statistics as st,hashlib,csv,gzip,importlib.util,subprocess,unittest
from pathlib import Path
from dataclasses import replace
OUT=Path(__file__).resolve().parent
PRIOR=OUT.parent/'scaling_robustness'
sys.path.insert(0,str(OUT.parent/'scaling_blocker_audit'))
import audit as a
r=a.r;s=r.s1

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
m=load('discovery.competitive_ga.five_tier_manager',PRIOR/'corrected_manager.py')
k=load('five_tier_kernel',PRIOR/'corrected_kernel.py');m.Replay=k.Replay
TIERS=('TERRIBLE','POOR','AVERAGE','GOOD','GREAT');EDGES=(-.006,-.002,.002,.006)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def tier(x):return TIERS[sum(x>=b for b in EDGES)]
def infer(mean,radius,ntrain,ncal):
    return tier(mean) if min(ntrain,ncal)>=20 and tier(mean-radius)==tier(mean+radius) else 'UNKNOWN'
def se(v):return st.stdev(v)/len(v)**.5 if len(v)>1 else float('inf')

def generate(seed,scenario):
    rng=random.Random(seed);features=[];pred=[];truth=[];rets=[]
    mu=(-.012,-.004,0.,.004,.012)
    for i in range(252):
        common=rng.gauss(0,.003);ff=[];pp=[];tt=[];rr=[]
        for j in range(24):
            z=rng.randrange(5)
            # Observable noisy measurement, never an oracle class or forward return.
            f=z if rng.random()<.8 else rng.randrange(5)
            if scenario=='null':f=rng.randrange(5)
            if scenario=='reversal' and i>=126:f=4-f
            guessed=mu[f]
            predicted=(.010-guessed if scenario in ('misleading','null','reversal') else guessed)
            # Exact execution net return: gross-to-net uses full multiplicative costs.
            net=mu[z]+common+rng.gauss(0,.008)
            gross=(1+net)*(1+s.FRICTION)*(1+s.COSTS['fees'])/((1-s.FRICTION)*(1-s.COSTS['fees']))-1
            ff.append(f);pp.append(predicted);tt.append(mu[z]);rr.append(gross)
        features.append(ff);pred.append(pp);truth.append(tt);rets.append(rr)
    prices=[100.+j for j in range(24)];days=[]
    for i,d in enumerate(s.DATES):
        if i>=2:prices=[v*(1+rr) for v,rr in zip(prices,rets[i-2])]
        days.append((d,{t:k.Bar(prices[j],prices[j]) for j,t in enumerate(s.TICKERS)}))
    return days,features,pred,truth

def observed(days,i,j):
    t=s.TICKERS[j]
    return days[i+2][1][t].open*(1-s.FRICTION)*(1-s.COSTS['fees'])/(days[i+1][1][t].open*(1+s.FRICTION)*(1+s.COSTS['fees']))-1

def fit(days,features,cutoff=126):
    cells=[]
    for cell in range(5):
        groups=[]
        for lo,hi in ((0,78),(80,122)):
            values=[]
            for i in range(lo,hi):
                assert i+2<cutoff
                row=[observed(days,i,j) for j in range(24) if features[i][j]==cell]
                if row:values.append(st.mean(row))
            groups.append(values)
        train,cal=groups;mean=st.mean(train)
        radius=max(2.58*se(train),abs(st.mean(cal)-mean)+2.58*se(cal))
        cells.append(dict(mean=mean,radius=radius,ntrain=len(train),ncal=len(cal),label=infer(mean,radius,len(train),len(cal))))
    return cells

def callbacks(features,pred,cells,variant,days):
    idx={d:i for i,d in enumerate(s.DATES)}
    def value(t,d):
        i=idx[d];j=int(t[3:]);cell=cells[features[i][j]]
        return pred[i][j] if variant=='existing_ev10' else (cell['mean'] if cell['label'] in ('GOOD','GREAT') else -1.)
    def native(c,t,d,h):
        i=idx[d];j=int(t[3:]);v=value(t,d)
        if h:action='EXIT' if v<=0 else 'HOLD'
        else:action='ENTER' if v>0 else None
        if action is None:return None
        target=0. if action=='EXIT' else h['weight'] if h else .10
        # Conditional scaling needs GREAT plus actual native evidence, never truth.
        if h and action=='HOLD' and variant in ('tier15','tier20') and cells[features[i][j]]['label']=='GREAT':
            target=.15 if variant=='tier15' else .20
            if h['weight']<target-1e-6:action='ADD'
        return r.NativeProposal(d,t,c.family,c.chromosome_id,action,target,v+s.ROUND_TRIP,'net_return_fraction','FROZEN_CAUSAL_CELLS','FIVE_TIER','2029-12-31')
    def evidence(c,t,d,h,realized,nav):
        # Filter strictly earlier closes, including exclusion of same-close exits.
        past=[z for z in realized if z['date']<d];folds={}
        for z in past:folds.setdefault(idx[z['date']]//42,[]).append(z['return'])
        positive_folds=sum(f<idx[d]//42 and st.mean(v)>0 for f,v in folds.items())
        peak=s.INITIAL;mdd=0
        for row in nav:
            if row[0]>=d:continue
            peak=max(peak,row[1]);mdd=max(mdd,1-row[1]/peak)
        confirmed=cells[features[idx[d]][int(t[3:])]]['label']=='GREAT'
        return r.ScaleEvidence(len(past),positive_folds,bool(past) and st.mean(z['return'] for z in past)>0,mdd,confirmed,dict(days)[d][t].close>h['entry']*(1+s.COSTS['fees']),False)
    return dict(classify=lambda t,d:m.NicheObservation(d,'2029-12-31','PIT_NOISY_MEASUREMENT',(('synthetic',.1),)),eligible=lambda c,t,d:c.chromosome_id==t,native=native,conditional_ev=lambda c,t,d,*args:value(t,d),scaling_evidence=evidence if variant in ('tier15','tier20') else None)

def causal_predictions(days,features,pred):
    """Sequential close clock: publish matured outcomes, then predict all eligibles.

    No truth, scenario, oracle regime, portfolio selection or holdout label input.
    Evaluation outcomes enter only after their predeclared execution horizon matures.
    """
    ledger=[];states=[];alarms=[];quarantine=-1
    for now in range(252):
        for row in ledger:
            if row['maturity_index'] < now and row['missingness']=='PENDING':
                try:
                    row['realized_net']=observed(days,row['index'],row['j'])
                    row['missingness']='OBSERVED'
                    row['available_index']=now
                except (KeyError,IndexError,TypeError):row['missingness']='MISSING_BARS'
        matured=[z for z in ledger if z['missingness']=='OBSERVED' and z['index']>=now-63]
        groups=[];drift=[]
        for cell in range(5):
            dates={}
            for z in matured:
                if z['signal']==cell:dates.setdefault(z['index'],[]).append(z['realized_net'])
            grouped=[(d,st.mean(v)) for d,v in sorted(dates.items())]
            old=[v for d,v in grouped if d<now-11];recent=[v for d,v in grouped if d>=now-11]
            alarm=len(old)>=30 and len(recent)>=7 and abs(st.mean(recent)-st.mean(old))>max(.004,3*(se(old)**2+se(recent)**2)**.5)
            if alarm:drift.append(cell)
            train=[v for d,v in grouped if d<now-23];cal=[v for d,v in grouped if d>=now-23]
            mean=st.mean(cal) if cal else 0.
            radius=max(2.58*se(cal),abs(st.mean(train)-mean)+2.58*se(train)) if train and cal else 1.
            outcomes=[z['realized_net'] for z in matured if z['signal']==cell]
            downside=sorted(outcomes)[int(.05*len(outcomes))] if outcomes else -1.
            groups.append(dict(mean=mean,radius=radius,ntrain=len(train),ncal=len(cal),label=infer(mean,radius,len(train),len(cal)),downside05=downside))
        if drift and now>quarantine:
            alarms.append(dict(index=now,date=s.DATES[now],cells=drift));quarantine=now+20
        # Explicit absence of identifiable conditional signal must never mean AVERAGE.
        identifiable=max(z['mean'] for z in groups)-min(z['mean'] for z in groups)>=.003
        for z in groups:
            reason='CONFIDENT'
            if now<=quarantine:reason='DRIFT_QUARANTINE'
            elif not identifiable:reason='NO_IDENTIFIABLE_SIGNAL'
            elif z['downside05']<(-.03 if z['label'] in ('GOOD','GREAT') else -.05):reason='OUTCOME_RISK'
            elif z['label']=='UNKNOWN':reason='INSUFFICIENT_OR_BOUNDARY_UNCERTAINTY'
            if reason!='CONFIDENT':z['label']='UNKNOWN'
            z['reason']=reason
        states.append(groups)
        if now<250:
            for j,t in enumerate(s.TICKERS):
                c=groups[features[now][j]]
                ledger.append(dict(index=now,j=j,ticker=t,decision_timestamp=s.DATES[now],execution_index=now+1,
                    maturity_index=now+2,maturation_timestamp=s.DATES[now+2],available_index=None,
                    horizon='open(k+1) to open(k+2)',signal=features[now][j],predicted_net=pred[now][j],
                    inferred_net=c['mean'],radius=c['radius'],inferred_tier=c['label'],reason=c['reason'],
                    context={'measurement_cell':features[now][j],'clock_window_start':max(0,now-63),'drift_quarantine':now<=quarantine},
                    costs=dict(s.COSTS),friction=s.FRICTION,realized_net=None,missingness='PENDING',eligible=True))
    return states,ledger,alarms

# Existing native seam, with a PIT state selected on each callback date.
_frozen_callbacks=callbacks
def callbacks(features,pred,cells,variant,days):
    if not isinstance(cells[0],list):return _frozen_callbacks(features,pred,cells,variant,days)
    def dispatch(name,*args):
        # All callbacks have date as third positional argument.
        date=args[2];i=s.DATES.index(date)
        return _frozen_callbacks(features,pred,cells[i],variant,days)[name](*args)
    kw=_frozen_callbacks(features,pred,cells[0],variant,days)
    for name in ('native','conditional_ev','scaling_evidence'):
        if kw[name] is not None:kw[name]=lambda *args,_name=name:dispatch(_name,*args)
    return kw

def discrimination(days,features,pred,truth,cells):
    rows=[];mat=[[0]*5 for _ in range(5)];realmat=[[0]*5 for _ in range(5)];unknown=[0]*5;unknown_real=[0]*5
    for i in range(126,250):
        for j in range(24):
            cell=(cells[i] if isinstance(cells[0],list) else cells)[features[i][j]];actual=observed(days,i,j);true=tier(truth[i][j]);label=cell['label']
            row=dict(index=i,ticker=s.TICKERS[j],signal=features[i][j],predicted_net=pred[i][j],inferred_net=cell['mean'],radius=cell['radius'],inferred_tier=label,true_ev=truth[i][j],true_ev_tier=true,realized_net=actual,realized_tier=tier(actual))
            rows.append(row)
            if label=='UNKNOWN':unknown[TIERS.index(true)]+=1;unknown_real[TIERS.index(tier(actual))]+=1
            else:mat[TIERS.index(true)][TIERS.index(label)]+=1;realmat[TIERS.index(tier(actual))][TIERS.index(label)]+=1
    assigned=[z for z in rows if z['inferred_tier']!='UNKNOWN'];counts={t:sum(z['inferred_tier']==t for z in rows) for t in (*TIERS,'UNKNOWN')}
    means={t:st.mean(z['realized_net'] for z in rows if z['inferred_tier']==t) if counts[t] else None for t in (*TIERS,'UNKNOWN')}
    recalls={t:mat[h][h]/sum(z['true_ev_tier']==t for z in rows) for h,t in enumerate(TIERS)}
    accuracy=sum(z['true_ev_tier']==z['inferred_tier'] for z in assigned)/len(assigned) if assigned else None
    monotone=all(means[t] is not None for t in TIERS) and all(means[TIERS[i]]<means[TIERS[i+1]] for i in range(4))
    false=mat[0][4]/sum(z['true_ev_tier']=='TERRIBLE' for z in rows)
    x=[z['inferred_net'] for z in rows];y=[z['realized_net'] for z in rows];px=[z['predicted_net'] for z in rows]
    def calibration(xx):
        slope=s.corr(xx,y);variance=st.pvariance(xx)
        b=sum((v-st.mean(xx))*(w-st.mean(y)) for v,w in zip(xx,y))/len(xx)/variance if variance else None
        return dict(bias=st.mean(w-v for v,w in zip(xx,y)),rmse=math.sqrt(st.mean((v-w)**2 for v,w in zip(xx,y))),slope=b,intercept=st.mean(y)-b*st.mean(xx) if b is not None else None,rank_correlation=s.corr(s.ranks(xx),s.ranks(y)))
    passed=len(assigned)/len(rows)>=.5 and all(counts[t]>=20 for t in TIERS) and (accuracy or 0)>=.7 and min(recalls.values())>=.5 and false<=.01 and monotone
    return dict(status='PASS' if passed else 'FAIL',n=len(rows),coverage=len(assigned)/len(rows),counts=counts,true_ev_counts={t:sum(z['true_ev_tier']==t for z in rows) for t in TIERS},conditional_accuracy=accuracy,recall_including_abstain=recalls,forward_realized_net_by_tier=means,monotonic=monotone,false_great_on_terrible_rate=false,false_great_on_terrible_count=mat[0][4],great_precision=mat[4][4]/counts['GREAT'] if counts['GREAT'] else None,calibration=calibration(x),raw_prediction_calibration=calibration(px),confusion_ev=mat,confusion_realized=realmat,unknown_by_ev_tier=unknown,unknown_by_realized_tier=unknown_real,cells=cells[-1] if isinstance(cells[0],list) else cells),rows

def main():
    start=time.monotonic();plan=json.loads((OUT/'preregister.json').read_text());frozen=sha(OUT/'preregister.json')
    # Mandatory tests execute before generating any full experiment tape or replay.
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(OUT),'-p','test_*.py'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        (OUT/'report.json').write_text(json.dumps(dict(status='STOP_TEST_FAILURE',full_portfolio_replays=0)))
        raise SystemExit(result.returncode)
    sources=list(a.SOURCES)+[PRIOR/'corrected_manager.py',PRIOR/'corrected_kernel.py',PRIOR/'source.patch',OUT.parent/'run.py']
    before={str(p):sha(p) for p in sources};metrics=[];scores=[];tapes=[];attempts=0
    with gzip.open(OUT/'replays.jsonl.gz','wt') as archive,gzip.open(OUT/'opportunities.jsonl.gz','wt') as opportunities:
        for seed in plan['seeds']:
            for scenario in plan['scenarios']:
                assert time.monotonic()-start<plan['max_seconds']
                days,features,pred,truth=generate(seed,scenario);cells,ledger,alarms=causal_predictions(days,features,pred)
                frozen_cells=sha_bytes(json.dumps(cells).encode());score,rows=discrimination(days,features,pred,truth,cells)
                scores.append(dict(seed=seed,scenario=scenario,drift_alarms=alarms,drift_detection_delay=(next((z['index']-126 for z in alarms if z['index']>=126),None) if scenario=='reversal' else None),**score));tapes.append(dict(seed=seed,scenario=scenario,sha256=sha_bytes(json.dumps([features,pred,truth,[(d,{t:vars(b) for t,b in bars.items()}) for d,bars in days]]).encode()),frozen_cells_sha256=frozen_cells))
                for z in ledger:opportunities.write(json.dumps(dict(seed=seed,scenario=scenario,**z))+'\n')
                for variant in plan['policies']:
                    assert attempts<64 and time.monotonic()-start<plan['max_seconds']
                    attempts+=1;(OUT/'attempts.json').write_text(json.dumps(dict(attempts=attempts,seed=seed,scenario=scenario,variant=variant)))
                    kw=callbacks(features,pred,cells,variant,days)
                    evdays=days[126:252]
                    candidates=[m.Candidate(t,'GA7','synthetic',.02,s.GAPS[j]) for j,t in enumerate(s.TICKERS)]
                    result=m.run_slice(evdays,candidates,max_sessions=126,max_stocks=24,**s.COSTS,**kw)
                    metric,daily=s.measure(result,evdays)
                    # measure's legacy annualization assumes 252 sessions; correct locally.
                    metric['total_return']=metric['final_nav']/s.INITIAL-1
                    metric['cagr']=(metric['final_nav']/s.INITIAL)**(252/len(evdays))-1
                    metric['annualized_turnover']=metric['turnover']*252/len(evdays)
                    metric['calmar']=metric['cagr']/metric['mdd'] if metric['mdd'] else None
                    metric['fees']=sum(f[5] for f in result['ledger'])
                    metric['spread_slippage_impact_cost']=sum(f[3]*abs(f[4]-dict(evdays)[f[0]][f[1]].open) for f in result['ledger'])
                    fills=a.scaling_fills(result,evdays,.15 if variant=='tier15' else .20) if variant in ('tier15','tier20') else []
                    metrics.append(dict(seed=seed,scenario=scenario,variant=variant,scaled_fills=len(fills),full_target_fills=sum(z['full'] for z in fills),**metric))
                    archive.write(json.dumps(dict(seed=seed,scenario=scenario,variant=variant,ledger=result['ledger'],nav=result['nav'],risk=result['risk_audit'],decisions=result['decisions'],scaled_fills=fills))+'\n')
                    assert sha_bytes(json.dumps(cells).encode())==frozen_cells
                print(f'seed={seed} scenario={scenario} replays={attempts}/64 elapsed={time.monotonic()-start:.1f}s',flush=True)
    paired=[]
    for z in metrics:
        base=next(b for b in metrics if b['seed']==z['seed'] and b['scenario']==z['scenario'] and b['variant']=='existing_ev10')
        ten=next(b for b in metrics if b['seed']==z['seed'] and b['scenario']==z['scenario'] and b['variant']=='tier10')
        paired.append(dict(seed=z['seed'],scenario=z['scenario'],variant=z['variant'],total_return_delta_vs_ev10=z['total_return']-base['total_return'],total_return_delta_vs_tier10=z['total_return']-ten['total_return'],mdd_delta_vs_ev10=z['mdd']-base['mdd']))
    for score in scores:
        for kind,key,uk in [('ev','confusion_ev','unknown_by_ev_tier'),('realized','confusion_realized','unknown_by_realized_tier')]:
            with (OUT/f"confusion_{score['seed']}_{score['scenario']}_{kind}.csv").open('w') as f:
                w=csv.writer(f);w.writerow(['true / predicted',*TIERS,'UNKNOWN'])
                for i,t in enumerate(TIERS):w.writerow([t,*score[key][i],score[uk][i]])
    assert all(sha(p)==h for p,h in before.items());assert sha(OUT/'preregister.json')==frozen
    report=dict(status='PASS' if all(z['status']=='PASS' for z in scores) else 'FAIL',execution_status='COMPLETE',full_portfolio_replays=attempts,elapsed_seconds=time.monotonic()-start,preregister_sha256=frozen,production_sources_unchanged=True,source_sha256=before,discrimination=scores,portfolio_runs=metrics,paired=paired,tapes=tapes,minimum_engineering_change='Add a horizon-specific causal outcome ledger for all eligible opportunities, date-clustered calibrated absolute net-EV intervals and explicit abstention at the manager admission seam; independently validate native PIT features across forward regimes before enabling five-tier claims or tier scaling.',limitations=['No production quality classifier exists at this seam; this is a frozen experiment-local estimator.','Frozen algorithm updates only with strictly matured realized outcomes; evaluation truth and oracle regimes never enter inference.','Synthetic noisy measurements are artificially informative in learnable/misleading; no historical or native-alpha claim.','Unannounced reversal is detectable only after delayed noisy outcomes; rolling detection cannot guarantee immediate safety.','EV ground truth is evaluator-only generative conditional mean; realized outcome tiers also reported separately.','SE intervals are date-clustered diagnostics; not formal simultaneous/dependence-robust coverage.','No terminal liquidation; NAV includes open positions and receivables, costs reported on executed fills.','Portfolio tests cover 126 sessions, four seeds; no statistical robustness claim.','Native funded-exit scale gates may prevent every scaled add; no fabricated fills.'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(report['status'],flush=True)

def sha_bytes(x):return hashlib.sha256(x).hexdigest()
if __name__=='__main__':main()

```


## scaling_blocker_audit/audit.py

```python
#!/usr/bin/env python3
"""Bounded diagnostic: 72 instrumented original replays + 36 corrected strong replays.
No production writes. No fitting, GA or evidence relaxation.
"""
import sys, importlib.util, json, hashlib, time, csv, gzip, difflib, subprocess, tempfile
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent
FIX=OUT.parent/'stage2_fix'
sys.path.insert(0,str(FIX))
import support as r
from engines.portfolio_replay import kernel as original_kernel
START=time.monotonic()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCES=[Path(r.original.__file__),Path(original_kernel.__file__),r.ROOT/'discovery/competitive_ga/progressive_scaling.py',FIX/'functional_niche_manager.py',FIX/'support.py',OUT.parent/'run.py']
BEFORE={str(p):sha(p) for p in SOURCES}

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def once(s,a,b):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)

def prepare():
    manager=(FIX/'functional_niche_manager.py').read_text()
    kernel=Path(original_kernel.__file__).read_text()
    corrected=once(manager,'                    remaining_risk = max(0., bank.max_equity_risk - signal.other_equity_risk - reserved_loss)\n                    risk_cap = min(risk_cap, remaining_risk / per_dollar_loss if per_dollar_loss else 0.)\n','                    # Mandatory limit is per trade (entire candidate position), not portfolio aggregate.\n')
    corrected_kernel=once(kernel,'other_equity_risk=max(s.other_equity_risk,reserved_risk),max_equity_risk=self.max_equity_risk)','other_equity_risk=0.,max_equity_risk=self.max_equity_risk)')
    corrected_kernel=corrected_kernel.replace('        # Reserve portfolio risk across all evidence-based additions in score order.\n        # The caller-supplied other_equity_risk remains a separate floor.','        # Per-trade loss limit; other holdings do not consume this trade budget.\n        # Any aggregate portfolio guard must be a separately configured policy.')
    (OUT/'corrected_manager.py').write_text(corrected);(OUT/'corrected_kernel.py').write_text(corrected_kernel)
    patches=[]
    for name,old,new in [('discovery/competitive_ga/functional_niche_manager.py',manager,corrected),('engines/portfolio_replay/kernel.py',kernel,corrected_kernel)]:
        patches.append(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
    (OUT/'source.patch').write_text(''.join(patches))
    with tempfile.TemporaryDirectory(dir='/tmp') as td:
        for name,txt in [('discovery/competitive_ga/functional_niche_manager.py',manager),('engines/portfolio_replay/kernel.py',kernel)]:
            p=Path(td)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(txt)
        p=subprocess.run(['patch','--batch','-p1','-i',str(OUT/'source.patch')],cwd=td,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert (Path(td)/'discovery/competitive_ga/functional_niche_manager.py').read_text()==corrected
        assert (Path(td)/'engines/portfolio_replay/kernel.py').read_text()==corrected_kernel
        (OUT/'reconstruction.log').write_text(p.stdout+'Exact byte equality verified for both corrected modules.\n')
    mods=[]
    for label,txt in [('original',manager),('corrected',corrected)]:
        txt=once(txt,'            if selected:\n',"            audit['context'] = dict(held=None if held is None else dict(held), nav=nav, cash=bank.cash, unsettled=list(bank.unsettled), admission_halted=bank.admission_halted)\n            if selected:\n")
        txt=once(txt,'                funded = min(desired, remaining / ((1 + bank.friction) * (1 + bank.fees)))',"                funded = min(desired, remaining / ((1 + bank.friction) * (1 + bank.fees)))\n                audit['reservation_detail'] = dict(other_equity_risk=signal.other_equity_risk, reserved_loss=reserved_loss, per_dollar_loss=per_dollar_loss, risk_cap=risk_cap, remaining_cash_weight=remaining, initial_cash_weight=bank.cash/nav, desired=desired, funded=funded, unsettled_weight=sum(v for _,v in bank.unsettled)/nav, other_positions={t:dict(weight=pos.shares*bars[t].close/nav, loss=max(by_owner[pos.owner].stop,by_owner[pos.owner].gap_risk)+bank.round_trip_cost) for t,pos in book.positions.items() if t!=signal.ticker})")
        # 'audit' loop variable at this point is the matching decision from reverse search.
        path=OUT/f'{label}_instrumented_manager.py';path.write_text(txt)
        mods.append(load('discovery.competitive_ga.blocker_'+label,path))
    k=load('blocker_corrected_kernel',OUT/'corrected_kernel.py');mods[1].Replay=k.Replay
    return mods,k


def execute(days,kw,manager):
    kw=dict(kw); classify=kw["classify"]
    kw["classify"]=lambda t,d:manager.NicheObservation(**vars(classify(t,d)))
    return r.execute(days,kw,manager)

def evidence_fail(e,target):
    if e is None:return ['scaling_evidence_missing']
    fail=[]
    for key in ('position_profitable','current_signal_confirmed','positive_net_ev'):
        if not e[key]:fail.append(key)
    if e['matured_trades']<(50 if target>.15 else 30):fail.append('matured_trades')
    if target>.15:
        if e['forward_folds']<2:fail.append('forward_folds')
        if e['historical_mdd']>.20:fail.append('historical_mdd')
    return fail


def extract(x,days,seed,q,v,tape):
    records=[];ctx_by={};dayidx={d:i for i,(d,b) in enumerate(days)}
    risk={(a['date'],a['ticker']):a for a in x['risk_audit']}
    fills=defaultdict(list)
    for f in x['ledger']:fills[f[0],f[1]].append(f)
    for a in x['decisions']:
        c=a.get('context',{});h=c.get('held')
        if not h:continue
        d,t=a['date'],a['ticker'];i=dayidx[d];ev=r.s1.expected(tape[i][int(t[3:])],'strong' if q=='misnull' else q)-r.s1.ROUND_TRIP
        if ev<=0:continue
        target=.15 if v=='scale15' else .20
        native=next((ac for owner,ac,w in a.get('actions',[]) if ac in ('ADD','HOLD','EXIT','REDUCE')),None)
        add=native=='ADD';res=a.get('reservation');detail=a.get('reservation_detail',{});e=a.get('scaling_evidence')
        fail=evidence_fail(e,target) if add else []
        current=h['weight'];per=max(.02,r.s1.GAPS[int(t[3:])])+r.s1.ROUND_TRIP
        standalone=target*per;other=detail.get('other_equity_risk',0);reserved=detail.get('reserved_loss',0)
        requested_risk=target*per
        B=add and bool(fail)
        # Separate raw counterfactual constraints from operative funding constraints.
        C_own=add and requested_risk>.02+1e-12
        C_other=add and other+requested_risk>.02+1e-12 and not C_own
        C_queue=add and other+requested_risk<=.02+1e-12 and other+reserved+requested_risk>.02+1e-12
        need=max(0,min(target,.02/per)-current)
        cost=(1+r.s1.FRICTION)*(1+r.s1.COSTS['fees'])
        initial=detail.get('initial_cash_weight',c['cash']/c['nav'])
        remaining=detail.get('remaining_cash_weight',initial)
        E=add and initial+1e-12<need*cost
        F=add and remaining+1e-12<need*cost and remaining<initial-1e-12
        # D is a policy concentration cap distinct from B's failed prerequisites.
        effective_cap=.10
        if e and not evidence_fail(e,.15):effective_cap=.15
        if e and not evidence_fail(e,.20):effective_cap=.20
        D=add and target>effective_cap+1e-12
        cats=[k for k,b in [('A',not add),('B',B),('C',C_own or C_other or C_queue),('D',D),('E',E),('F',F)] if b]
        future=None;exitdate=None;realized=None
        for z in x['realized']:
            if z['ticker']==t and z['date']>d:
                exitdate=z['date'];realized=z['return'];break
        if exitdate:
            end=dayidx[exitdate];future=days[end][1][t].open/days[min(i+1,len(days)-1)][1][t].open-1
        nextd=days[i+1][0] if i+1<len(days) else None
        record=dict(seed=seed,quality=q,variant=v,date=d,ticker=t,native_action=native,net_ev=ev,current=current,requested=target,evidence=e,evidence_failed_fields=fail,standalone_target_loss=standalone,other_equity_risk=other,reserved_loss=reserved,per_dollar_loss=per,other_exhausts=C_other,standalone_exceeds=C_own,queue_risk_exhausts=C_queue,categories=cats,concentration_cap=effective_cap,nav=c['nav'],cash=c['cash'],unsettled=c['unsettled'],reservation=res,reservation_detail=detail,next_open_risk=risk.get((nextd,t)),next_open_fills=fills.get((nextd,t),[]),diagnostic_forward_return_to_next_native_exit=future,diagnostic_next_exit=exitdate,diagnostic_whole_trade_realized_return=realized)
        records.append(record)
    return records


def count(rows):
    adds=[z for z in rows if z['native_action']=='ADD']
    return dict(unique_positive_ev_incumbent_stock_dates=len(rows),unique_native_add_stock_dates=len(adds),categories=dict(Counter(k for z in rows for k in z['categories'])),exact_overlap=dict(Counter('+'.join(z['categories']) or 'none' for z in adds)),evidence_failed_fields=dict(Counter(k for z in adds for k in z['evidence_failed_fields'])),other_exhausts=sum(z['other_exhausts'] for z in adds),standalone_exceeds=sum(z['standalone_exceeds'] for z in adds),queue_risk_exhausts=sum(z['queue_risk_exhausts'] for z in adds),evidence_valid_adds=sum(not z['evidence_failed_fields'] for z in adds),evidence_valid_other_blocked=sum(not z['evidence_failed_fields'] and z['other_exhausts'] for z in adds),evidence_valid_other_blocked_cash_sufficient=sum(not z['evidence_failed_fields'] and z['other_exhausts'] and 'E' not in z['categories'] for z in adds))


def scaling_fills(x,days,target):
    previous={};out=[]
    for (d,bars),nav in zip(days,x['nav']):
        # Same DGP open==close; opening NAV before costs = close NAV plus net execution costs.
        fs=[f for f in x['ledger'] if f[0]==d]
        oe=nav[1]+sum(f[5]+f[3]*abs(f[4]-bars[f[1]].open) for f in fs)
        for f in fs:
            t=f[1]
            if f[2]=='BUY' and t in previous:
                w=(previous[t]+f[3])*bars[t].open/oe
                if w>.10001:out.append(dict(date=d,ticker=t,weight=w,full=w>=target-1e-9))
        previous=nav[3]
    return out


def main():
    (old,new),kernel=prepare()
    allrows=[];metrics=[];rawpath=OUT/'original_decision_risk.jsonl.gz'
    oldruns=list(csv.DictReader((FIX/'runs.csv').open()))
    oldreport=json.loads((FIX/'report.json').read_text())
    with gzip.open(rawpath,'wt') as raw:
        for seed in r.s1.SEEDS:
            assert time.monotonic()-START<600
            days,tapes,_=r.s1.generate(seed)
            for q in r.QUALITIES:
                tape=tapes['null' if q=='misnull' else q]
                assert hashlib.sha256(json.dumps(tape).encode()).hexdigest()==next(t['sha256'] for t in oldreport['tapes'] if t['seed']==seed and t['quality']==q)
                for v in ('scale15','scale20'):
                    kw,stats=r.callbacks(tape,q,v,seed,days);x=execute(days,kw,old);m,_=r.s1.measure(x,days)
                    ref=next(z for z in oldruns if int(z['seed'])==seed and z['quality']==q and z['variant']==v)
                    for key in ('cagr','mdd','exposure','turnover','final_nav'):assert abs(m[key]-float(ref[key]))<1e-10,(seed,q,v,key)
                    if seed==1101:
                        saved=json.loads((FIX/f'{q}_{v}_audit.json').read_text());clean=[{k:w for k,w in z.items() if k not in ('context','reservation_detail')} for z in x['decisions']]
                        assert json.loads(json.dumps(clean))==saved,'Instrumentation changed recorded decisions'
                    raw.write(json.dumps(dict(seed=seed,quality=q,variant=v,decisions=x['decisions'],risk=x['risk_audit'],nav=x['nav'],ledger=x['ledger'],realized=x['realized']))+'\n')
                    allrows.extend(extract(x,days,seed,q,v,tape))
            # Corrected run deliberately restricted to calibrated strong signal quality.
            for v in ('ev','scale15','scale20'):
                kw,stats=r.callbacks(tapes['strong'],'strong',v,seed,days);x=execute(days,kw,new);m,daily=r.s1.measure(x,days)
                if v=='ev':
                    ref=next(z for z in oldruns if int(z['seed'])==seed and z['quality']=='strong' and z['variant']==v)
                    for key in ('cagr','mdd','exposure','turnover','final_nav'):assert abs(m[key]-float(ref[key]))<1e-10
                fs=scaling_fills(x,days,.15 if v=='scale15' else .20)
                metrics.append(dict(seed=seed,quality='strong',variant=v,**m,scaled_fills=len(fs),full_target_fills=sum(f['full'] for f in fs),max_scaled_weight=max((f['weight'] for f in fs),default=0),**stats))
                if seed==1101:
                    (OUT/f'corrected_{v}_audit.json').write_text(json.dumps(dict(decisions=x['decisions'],risk=x['risk_audit'],scaled_fills=fs)))
            print(f'seed {seed}: original {6*(seed-1100)}, corrected {3*(seed-1100)}; {time.monotonic()-START:.2f}s',flush=True)
    with gzip.open(OUT/'unique_opportunities.jsonl.gz','wt') as f:
        for z in allrows:f.write(json.dumps(z)+'\n')
    bygroup={q+'_'+v:count([z for z in allrows if z['quality']==q and z['variant']==v]) for q in r.QUALITIES for v in ('scale15','scale20')}
    dedup={}
    for z in allrows:
        key=(z['seed'],z['quality'],z['date'],z['ticker'])
        if key not in dedup:dedup[key]=dict(z,categories=list(z['categories']))
        else:dedup[key]['categories']=sorted(set(dedup[key]['categories']+z['categories']))
    # Case selection is diagnostic ONLY, after all fixed-policy replays.
    cases=[z for z in allrows if z['quality']=='strong' and z['variant']=='scale15' and z['native_action']=='ADD' and not z['evidence_failed_fields'] and z['other_exhausts'] and 'E' not in z['categories'] and (z['diagnostic_forward_return_to_next_native_exit'] or 0)>.03]
    cases.sort(key=lambda z:z['net_ev'],reverse=True)
    chosen=[];seen=set()
    for z in cases:
        key=(z['seed'],z['ticker'],z['diagnostic_next_exit'])
        if key in seen:continue
        seen.add(key);chosen.append(z)
        if len(chosen)==8:break
    assert len(chosen)>=5,len(chosen)
    import statistics as st
    aggregates=[]
    for v in ('ev','scale15','scale20'):
        rr=[z for z in metrics if z['variant']==v]
        aggregates.append(dict(variant=v,n=len(rr),**{k:st.mean(z[k] for z in rr) for k in ('cagr','mdd','exposure','turnover')},scaled_fills=sum(z['scaled_fills'] for z in rr),full_target_fills=sum(z['full_target_fills'] for z in rr),max_scaled_weight=max(z['max_scaled_weight'] for z in rr)))
    report=dict(status='COMPLETE_DIAGNOSTIC_SYNTHETIC_ONLY',elapsed_seconds=time.monotonic()-START,original_instrumented_replays=72,corrected_replays=36,total_comparison_replays=108,original_metrics_identical=True,first_seed_original_decisions_identical=True,original_sources_sha256=BEFORE,source_unchanged=all(sha(p)==BEFORE[str(p)] for p in SOURCES),reconstruction_exact=True,groups=bygroup,all_variant_observations=count(allrows),deduplicated_across_targets=dict(stock_dates=len(dedup),category_union_counts=dict(Counter(k for z in dedup.values() for k in z['categories']))),cases=chosen,corrected_strong_aggregates=aggregates,limitations=['Synthetic assets only, not historical stocks or native model alpha.','ScaleEvidence is endogenous pooled funded exits, not verified independent trades.','Categories are simultaneous counterfactual constraints on target; evidence failure and evidence-implied concentration cap overlap.','A counted over positive-EV incumbents; B-F over native ADDs; per-group keys are seed/quality/variant/date/ticker.','F means prior ranked commitments reduce available cash; no claim alternate queue improves outcomes.','Future return used only for post-run case selection, never callbacks.','Corrected rerun restricted to strong quality; weak and misnull only audited, not retuned.'])
    assert report['source_unchanged']
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    with (OUT/'corrected_runs.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
    print(json.dumps(dict(groups=bygroup,corrected=aggregates,cases=len(chosen)),indent=2))
if __name__=='__main__':main()

```
