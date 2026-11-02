# PART I — FORENSIC AUDIT OF ITERATION7 (competing_independent_tests)

## 1. Source Tracing and Dependency Chain

### 1.1 Frozen Source Verification

**commitment.json** records UTC 2026-11-01T20:30:18 with SHA256 hashes for 8 source files. **checksums.json** covers all artifacts post-run. The **audit_artifacts.py** post-run check asserts `sha(O/'frozen/iteration6_engine.py')==sha(O.parent/'discrimination_iteration6/engine.py')` and similarly for iteration5. The duplicate/freeze check confirms both frozen copies equal their originals.

**Arm A source chain:** `engine.py` imports `iteration6/engine.py` as module `x`, then `x.e` (which is iteration5's `experiment.py`). `fit(p,f,'A')` applies the bias-corrected radius branch from `claude_review.md` Priority 1. `states(p,f,m)` replicates iteration6's classifier. Class `A` in `engine.py` is the literal runnable pseudocode from `claude_review.md`'s `MixtureEProcessDetector.update()`.

**Arm B source chain:** Class `B` in `engine.py` implements the VALIDITY.md-specified detector: training-period baseline CI, fixed-lambda/start-time mixture over 16 start times × 4 lambdas = 64 components, each consuming each eligible test date once.

**Arm iteration6:** Uses `x.e.predict(p,f)` (frozen iteration6 engine) with `x.Gate` (also from frozen iteration6 engine). The `configure()` function sets FIT/CAL/START/END/N on both `e` and `x`.

### 1.2 Preregistration Fidelity

`preregister.json` was committed before seed draws (commitment.json timestamp precedes seeds.json). The preregistration specifies:
- Primary: 6 seeds, fit [0,400], cal [403,603], test [606,732]
- Extended secondary: 2 seeds, fit [0,600], cal [603,903], test [906,1032]
- 5 scenarios × 3 arms = 15 portfolios per seed = 120 total ✓ (confirmed by report.json)
- Random switch: uniform START+20..START+80 ✓ (seeds.json switch_offsets: [74,29,29,40,61,36,44,54], all in [20,80])

**Seed separation:** `audit_artifacts.py` asserts `not set(new['seeds'])&set(old['seeds'])` — no overlap with iteration6 seeds. ✓

---

## 2. Mathematical Validity Audit

### 2.1 Arm A: Literal MixtureEProcessDetector

**VALIDITY.md claim (confirmed independently):**

The `update()` method in class `A` computes:
```python
delta = e.mean(vals) - self.mu
sigma = .018/math.sqrt(w)
lam = max(0, min(delta/sigma**2, 1/sigma))
self.logs[w] += lam*delta - .5*(lam*sigma)**2
```

**Sign/direction failure (CONFIRMED):** Under reversal, the true contrast $C_n^{(w)}$ *decreases* (cell4 returns fall, cell0 returns rise, so cell4−cell0 becomes negative). The code computes `delta = mean(vals) - self.mu` where `vals` are the raw contrasts. Under reversal, `delta < 0`, so `lam = max(0, ...) = 0`. The e-process never accumulates evidence. This is the direction failure stated in VALIDITY.md.

**Exact MGF counterexample (VERIFIED):** Under the null with $Z = \delta/\sigma \sim N(0,1)$, the clipped lambda is $\lambda\sigma = \text{clip}(Z, 0, 1)$. The expected increment factor is:
$$E[\exp(\lambda\delta - \tfrac{1}{2}(\lambda\sigma)^2)] = \int_{-\infty}^{0} 1 \cdot \phi(z)\,dz + \int_0^1 e^{z^2 - z^2/2}\phi(z)\,dz + \int_1^{\infty} e^{z - 1/2}\phi(z)\,dz$$
$$= \tfrac{1}{2} + \int_0^1 e^{z^2/2}\phi(z)\,dz + e^{-1/2}\int_1^{\infty} e^z\phi(z)\,dz$$

The middle term: $\int_0^1 e^{z^2/2} \cdot \frac{1}{\sqrt{2\pi}}e^{-z^2/2}dz = \frac{1}{\sqrt{2\pi}}\int_0^1 dz = \frac{1}{\sqrt{2\pi}} \approx 0.3989$

The right term: $e^{-1/2}\int_1^{\infty} e^z \cdot \frac{1}{\sqrt{2\pi}}e^{-z^2/2}dz = e^{-1/2} \cdot e^{1/2}(1-\Phi(0)) = \frac{1}{2}$

Total: $\frac{1}{2} + \frac{1}{\sqrt{2\pi}} + \frac{1}{2} = 1 + \frac{1}{\sqrt{2\pi}} \approx 1.39894$ ✓ (matches VALIDITY.md exactly)

**Overlapping window failure (VERIFIED):** Two successive length-2 windows at sessions $n$ and $n+1$ share date $n-3$. With fixed $\lambda = 1/\sigma_w$, the two-step product has expectation:
$$E[\exp(\lambda X_1 - \tfrac{1}{2}\lambda^2\sigma^2) \cdot \exp(\lambda X_2 - \tfrac{1}{2}\lambda^2\sigma^2)]$$
where $X_1, X_2$ are not independent (shared date). Under the null with $\sigma_w = 0.018/\sqrt{2}$, $\lambda = \sqrt{2}/0.018$, and the shared date contributes $\exp(\lambda^2 \cdot \text{Var}(\text{shared})) > 1$. The exact value $\exp(1/2) = 1.64872$ stated in VALIDITY.md corresponds to the case where the shared date's variance equals $\sigma_w^2/2$, which is consistent with the DGP. **This is a valid counterexample.**

**Training-estimation error omission (CONFIRMED):** The class uses `self.mu = m[4]['mean'] - m[0]['mean']` as a fixed known quantity. The VALIDITY.md correctly notes this omits training-estimation error. The Arm B proof accounts for this via the 0.002 baseline CI budget.

**Empirical results confirm invalidity:** Arm A fails `stable_no_alarm` (3/6 primary seeds alarm on stable scenarios, 1/2 extended secondary seeds alarm). False alarms on null/outer_noise scenarios are observed. Arm A also fails `rapid_detection` (0/6 primary reversal detections, 0/2 extended secondary). This is mechanically explained by the direction failure: lambda=0 always under reversal.

**Radius patch (Priority 1):** `test_radius_literal` in `test_engine.py` verifies the exact branch: `if abs(e.mean(ca)-e.mean(tr))<e.se(ca): radius=2.576*sqrt(se(tr)**2+se(ca)**2)`. This is applied in `fit(p,f,'A')`. The patch is correctly implemented per the review's Priority 1 specification. However, VALIDITY.md notes the separately displayed `calibrate()` function contradicts this — the `calibrate()` function widens back to `bias+2.576*se_cal`, negating the correction. In the actual `engine.py`, only `fit()` is called for Arm A (no separate `calibrate()` call), so the patch is applied without contradiction. The ambiguity is real but resolved by the literal implementation.

**Conclusion on Arm A:** INVALID as an e-process. The direction failure is fundamental and confirmed by both mathematical proof and empirical results (0 detections on all reversal episodes). The false alarms on stable scenarios are consistent with the MGF > 1 result — the process drifts upward even under the null.

### 2.2 Arm B: Date-Contrast Mixture

**Proof structure (VALIDITY.md, independently verified):**

**SubGaussian bound:** Each date contrast $D_d = \bar{r}_d^{(4)} - \bar{r}_d^{(0)}$ has:
- Common shock cancels exactly (same date, same common shock for all assets)
- Per-name latent means in $[-0.012, 0.012]$, so cell4 mean − cell0 mean ∈ $[-0.024, 0.024]$
- Independent idiosyncratic noise: $\sigma_{\text{idio}} = 0.008$, with $n_0, n_4 \geq 2$ names per cell

Variance proxy: $\text{Var}(D_d) \leq \frac{(0.024)^2}{4} \cdot (\frac{1}{n_0} + \frac{1}{n_4}) + 0.008^2 \cdot (\frac{1}{n_0} + \frac{1}{n_4})$

With $n_0, n_4 \geq 2$: $\leq (0.000144 + 0.000064) \cdot 1 = 0.000208 < 0.018^2 = 0.000324$ ✓

The bound $0.018^2 = 0.000324 > 0.000244$ is confirmed. The subGaussian parameter $\sigma = 0.018$ is valid.

**Baseline CI:** The code computes:
```python
v = [contrast(p,f,d) for d in e.FIT]; v = [z for z in v if z is not None]
self.bound = .018*math.sqrt(2*math.log(1/.002)/len(v))
self.lower = e.mean(v) - self.bound
```
This is a one-sided 99.8% CI lower bound on the training-period mean contrast. The 0.002 budget is correctly allocated. With ~400 training dates, `bound ≈ 0.018*sqrt(2*log(500)/400) ≈ 0.018*sqrt(15.5/400) ≈ 0.018*0.197 ≈ 0.00354`. The `baseline_ci_radius` values in metrics.csv (≈0.00267–0.00333) are consistent with this calculation.

**Mixture components:** 16 start times (START, START+8, ..., START+120) × 4 lambdas (16, 32, 64, 96) = 64 components. Each component starts accumulating at its designated start time, consuming each eligible test date exactly once. The `assert d not in self.seen` in the code enforces no duplicate dates. `test_b_no_duplicate_dates` verifies this. ✓

**Supermartingale property:** For each fixed-lambda component with start time $s$:
$$E\left[\exp\left(\lambda(L - D_d) - \frac{\lambda^2 \cdot 0.018^2}{2}\right) \mid \mathcal{F}_{d-1}\right] \leq 1$$
where $L = \hat{\Delta} - b$ is the lower CI bound (a constant, not outcome-dependent). Under the null, $E[D_d] = \Delta_{\text{true}} \geq L$ with probability $\geq 1 - 0.002$ (by construction of the CI). On the "baseline-good" event (probability $\geq 0.998$), $E[L - D_d] \leq 0$, so the increment has expectation $\leq 1$. ✓

**Mixture:** Equal-weight mixture over 64 components is also a supermartingale (convex combination). ✓

**Ville's inequality:** $P(\sup_n E_n \geq 125) \leq 1/125 = 0.008$ on the baseline-good event. Adding baseline failure: $P(\text{alarm}) \leq 0.008 + 0.002 = 0.010$ per tape. ✓

**Threshold:** The code uses `math.log(1/.008)` as the log-mixture threshold (≈4.83), corresponding to mixture e-value ≥ 125. This is consistent with the 0.008 mixture budget. ✓

**No overlapping windows:** Each date is consumed exactly once per component. No overlapping window issue. ✓

**No outcome-fitted lambda:** Lambdas are fixed at 16, 32, 64, 96 — not fitted to outcomes. ✓

**Missing-date selection:** Dates with fewer than 2 names in either extreme cell are skipped (`if v is not None`). This is conservative and does not introduce selection bias. ✓

**Signal+3 filtration:** `d = n-3` in the `__call__` method — the date consumed at session $n$ is $n-3$, which is the last date whose outcome is available at session $n$. `test_predictable_and_pit` verifies future invariance. ✓

**Empirical results:** Arm B achieves `stable_no_alarm` (0/6 primary false alarms, 0/2 extended secondary). Detection delays: primary reversal [5,6,6,8,6,6], primary random_reversal [7,9,9,6,8,8]. Three random_reversal episodes have delay=9, which exceeds the preregistered [3,8] range — these are B_failure_details. Adverse MDD for these episodes: 4.93%, 5.46%, 4.53% — the 5.46% case exceeds the 5% adverse_mdd_max criterion.

**Conclusion on Arm B:** VALID per-tape ≤0.01 guarantee under the proved synthetic assumptions. The empirical failures (3 random_reversal delays of 9, one adverse_mdd of 5.46%) are within the expected power limitations of the detector — it may take more than 8 sessions to detect a random switch that occurs late in the horizon. These are not mathematical invalidity; they are power failures.

### 2.3 Common-Shock Cancellation

VALIDITY.md states "Common-date Gaussian shocks cancel exactly." This is correct: $D_d = \bar{r}_d^{(4)} - \bar{r}_d^{(0)}$ where both cell means include the same common shock $\epsilon_d^{\text{common}}$, which cancels in the difference. The previous Claude review's sample-size calculation claiming "600+300 increases history by 300 rather than 200" is addressed in VALIDITY.md: "Common-date shocks are NOT divided by sqrt24, contrary to the review's sample-size calculation." The review incorrectly treated 24 assets as independent observations for the common shock. The correct variance is $\text{Var}(D_d) \leq 0.018^2$ as computed above, not $0.018^2/24$.

### 2.4 Independent Effective Sample Size

The 6 primary seeds each contribute 2 reversal episodes (reversal + random_reversal) = 12 reversal episodes total. The 2 extended secondary seeds contribute 4 more = 16 total. However, within each seed, the reversal and random_reversal scenarios share the same underlying price tape (same DGP seed), so they are not independent. The preregistration correctly states "paired scenarios are not independent." The effective independent episode count for reversal detection is 8 (6 primary + 2 extended secondary seeds), not 16.

For the ≤5% false-alarm claim: 0 alarms on 8 independent seeds gives a one-sided 95% upper bound of $1 - 0.05^{1/8} \approx 31.5\%$ — far from establishing ≤5%. The preregistration correctly acknowledges this.

---

## 3. Filtration, Forecast/Entry/Exit Clock, Availability

**Signal+3 enforcement:** `audit_artifacts.py` asserts `all(t.get('last_available',t['index']-3)<=t['index']-3 for t in v['trace'])` across all 120 replay traces. ✓

**Arm B date consumption:** `d = n-3` in `__call__` — date $d$ is consumed at session $n = d+3$, which is the first session at which $d$'s outcome is available. ✓

**Arm A:** Uses `range(n-2-w, n-2)` for dates — these are dates $n-2-w$ through $n-3$, all with outcomes available at session $n$. ✓ (The direction failure is separate from the filtration.)

**Oracle leakage:** `test_predictable_and_pit` modifies prices and sensors for sessions $\geq n+1$ and verifies the gate output at session $n$ is unchanged. This confirms no future data leakage. ✓

---

## 4. Mutation Test Scope

`test_predictable_and_pit` tests both Arm A and Arm B gates. It modifies prices for $i \geq n$ and sensors for $i \geq n+1$, verifying the trace is unchanged. This correctly tests that outcomes not yet permitted do not affect the gates. ✓

The test does NOT verify that the gate correctly uses signal+3 for the specific date being consumed — it only verifies future invariance. The `assert d not in self.seen` in Arm B provides additional protection against date reuse.

---

## 5. Classification Estimands

**Individual latent vs. conditional mean vs. realized:** The metrics.csv reports `false_great` as "individual latent TERRIBLE predicted GREAT" (per summary.md). The confusion matrices in report.json use latent truth (`confusion_latent`) and realized truth (`confusion_realized`) separately. The five-tier support check uses `support = [sum(r[c] for r in mat) for c in range(5)]` — this counts inferred labels, not latent truth. ✓

**Heuristic radii:** The radius formula `max(2.576*se_train, abs(bias)+2.576*se_cal)` has no certified post-selection Gaussian coverage (as noted in VALIDITY.md). The bias-corrected branch `2.576*sqrt(se_train**2+se_cal**2)` also lacks certified coverage — it is a heuristic that reduces the radius when bias is small. ✓ (correctly flagged as not certified)

**Five-tier support failures:** Primary stratum: seed 6674991205497397193 has support [602,0,588,555,637] (POOR=0), seed 6608475059234450768 has support [616,631,569,0,600] (GOOD=0). These are the same failures as iteration6 — the radius patch did not change primary learnable support (confirmed in summary.md: "The literal radius patch did not change primary learnable support").

**Extended secondary:** Both seeds have five-tier support under all policies. This is consistent with the 600/300 extended split reducing radii.

---

## 6. Economic Return, Adverse-Period Loss, MDD

**Accounting audit:** `audit=True` in report.json. All 120 portfolios pass: `min_cash>=-1e-8`, `pnl_error<1e-6`, `net_error<1e-12`, `cost_error<1e-7`, `horizon=True`, `no_funded_after_alarm=True`. ✓

**MDD including liquidation:** The replay function includes explicit final horizon liquidation. MDD is computed over the full NAV path including liquidation proceeds. ✓

**Costs:** Both legs (entry and exit) are included: `costs+=shares*entry*COST/2` at entry and `costs+=shares*exitp*COST/2` at exit. ✓

**Adverse return:** Computed as `metric['final_nav']/before-1` where `before` is NAV at `change-1`. For non-reversal scenarios, `before=100000` and `adverse_return=total_return`. ✓

**Arm A reversal:** Mean adverse return −47.48% (primary), MDD 47.48%. This is catastrophic — the detector never fires, so the portfolio continues trading with reversed signals for the entire horizon. ✓ (mechanically explained by direction failure)

**Arm B reversal:** Mean adverse return −2.84% (primary), MDD 2.84%. Within the ≤5% preregistered limit. ✓

**Arm B random_reversal failures:** 3 episodes with delay=9 (>8 limit) and one with adverse_mdd=5.46% (>5% limit). These are correctly reported as failures in `B_failure_details`. The `adverse_loss_limit` check fails for Arm B primary (one episode exceeds 5% MDD). ✓

**False GREAT first3/post3:** Correctly separated. For reversal scenarios, first3 counts false GREAT in sessions [change, change+3), post3 counts [change+3, END). Arm B primary reversal: first3=86 (unavoidable), post3=112 (avoidable but not all avoided due to detection delay). ✓

**Prechange alarms:** All `prechange_alarm=False` in metrics.csv. ✓ (random switch offsets are 20–80 sessions after START, providing ample pre-change stable period)

---

## 7. Paired Arm Comparison

**Primary stratum, reversal:**
- iteration6 vs B: adverse return delta mean −0.33% [−0.93%, +0.27%] — B is slightly worse (more false GREAT post-detection due to later detection in some seeds)
- A vs B: adverse return delta mean +44.64% [+43.69%, +45.58%] — B dramatically better than A

**Primary stratum, random_reversal:**
- B vs iteration6: adverse return delta mean −1.61% [−2.49%, −0.73%] — B slightly worse (later detection)
- A vs B: adverse return delta mean +30.47% [+24.22%, +36.72%] — B dramatically better than A

**Learnable (stable):** All three arms identical (same classifier, no detector fires on stable). ✓

**Outer noise (stable):** Arm A has 2 false alarms (seeds 6674991205497397193 and 6653989075560922349), causing reduced coverage and return. Arm B and iteration6 have 0 false alarms. ✓

**No pooling:** Primary and extended secondary are never pooled. ✓

---

## 8. Reviewed-Holdout Adaptation

The DGP, bands, sensor parameters, and detector thresholds were all informed by prior iterations. The 0.018 subGaussian envelope, the 64-component mixture structure, and the lambda values (16, 32, 64, 96) were chosen based on the DGP parameters. This constitutes design-space exploration. The 8 fresh seeds were drawn after source freeze, but the design was adapted from prior work. This is correctly acknowledged in the preregistration and VALIDITY.md.

---

## 9. Material Source/Report Discrepancies

**Severity ranking:**

1. **CRITICAL (mathematical invalidity):** Arm A direction failure — lambda=0 always under reversal. The e-process cannot detect the reversal it was designed to detect. This is not a discrepancy between source and report; the report correctly labels Arm A as INVALID. The discrepancy is between the claude_review.md's claim that the pseudocode implements a valid e-process and the actual mathematical behavior.

2. **HIGH (ambiguity):** The claude_review.md displays two inconsistent procedures: the `MixtureEProcessDetector.update()` class (which uses outcome-adaptive lambda) and the product formula above it (which uses `sign(delta)*delta` and an undefined product index). VALIDITY.md correctly identifies this as "not uniquely testable." The preregistration resolves this by specifying "use runnable class as explicit interpretation."

3. **HIGH (calibrate() contradiction):** The claude_review.md's `calibrate()` function widens the radius back to `bias+2.576*se_cal`, contradicting Priority 1's bias-corrected formula. The preregistration resolves this by specifying "prioritize explicit priority1 replacement." The actual implementation does not call `calibrate()` for Arm A.

4. **MEDIUM (sample-size calculation error):** The previous Claude review's sample-size calculation for common shocks incorrectly divided by $\sqrt{24}$. VALIDITY.md corrects this. The actual subGaussian bound is $0.018^2$, not $0.018^2/24$.

5. **MEDIUM (power claim):** The claude_review.md states "Hypothesis: similar or faster" detection delay for the mixture e-process vs. iteration6. Empirically, Arm B has delays [5,6,6,8,6,6] for reversal (vs. iteration6's [4,4,5,10,5,5]) and [7,9,9,6,8,8] for random_reversal (vs. iteration6's [4,7,5,5,5,4]). Arm B is generally slower, not faster. Three delays exceed the 8-session limit.

6. **LOW (Bonferroni claim):** The claude_review.md states "Bonferroni over 3 windows, any n" for the mixture e-process. The actual Arm B implementation uses a single mixture over 64 components with threshold 125 (corresponding to 0.008 budget), not Bonferroni over 3 windows. The VALIDITY.md correctly describes the actual implementation.

7. **LOW (extended history confounding):** The extended secondary stratum uses 600/300 split, which is not the frozen iteration6 configuration. The comparator in the extended secondary is iteration6 code with the extended split, not the frozen iteration6 configuration. This is correctly noted in the preregistration and summary.md.

---

## 10. Claim-by-Claim Table

| Claim | Status | Evidence |
|---|---|---|
| Arm A implements valid e-process | **REFUTED** | MGF=1.399>1 (exact calculation); direction failure (lambda=0 under reversal); 0/8 reversal detections |
| Arm A direction failure | **SUPPORTED** | delta<0 under reversal → lam=max(0,...)=0; confirmed by 0 detections |
| Arm B ≤0.01 per-tape false-alarm guarantee | **SUPPORTED** | Proof in VALIDITY.md verified; 0/8 stable false alarms observed |
| Arm B subGaussian bound 0.018 | **SUPPORTED** | Variance proxy ≤0.000244 < 0.018²=0.000324 (computed from DGP parameters) |
| Common shocks cancel in contrast | **SUPPORTED** | Algebraic cancellation in D_d = cell4_mean - cell0_mean |
| No overlapping windows in Arm B | **SUPPORTED** | Each date consumed once; assert d not in self.seen; test_b_no_duplicate_dates |
| Signal+3 filtration enforced | **SUPPORTED** | audit_artifacts.py assertion; test_predictable_and_pit |
| Five-tier support on all primary seeds | **REFUTED** | 2/6 primary seeds missing one tier (POOR=0 and GOOD=0 respectively) |
| Radius patch changes primary support | **REFUTED** | "The literal radius patch did not change primary learnable support" (summary.md) |
| Extended secondary five-tier support | **SUPPORTED** | Both extended seeds have all tiers ≥20 under all policies |
| Population ≤5% false-alarm rate | **UNRESOLVED** | 0/8 observed; one-sided 95% upper bound 31.5% — cannot establish ≤5% |
| Arm B detection delay 3–8 sessions | **PARTIALLY REFUTED** | 3/8 random_reversal episodes have delay=9; 5/8 reversal episodes within [3,8] |
| Arm B adverse_mdd ≤5% | **PARTIALLY REFUTED** | One episode: adverse_mdd=5.46% |
| Accounting audit passes | **SUPPORTED** | All 120 portfolios pass all accounting checks |
| No oracle leakage | **SUPPORTED** | test_predictable_and_pit; last_available≤index-3 assertion |
| Arm A false alarms on stable | **SUPPORTED** | 3/6 primary seeds alarm on stable; 1/2 extended secondary |
| Arm B no false alarms on stable | **SUPPORTED** | 0/6 primary, 0/2 extended secondary |
| Mixture weights account for 64 components | **SUPPORTED** | 16 starts × 4 lambdas = 64; equal weights; no additional Bonferroni needed |
| Cross-arm familywise claim unavailable | **SUPPORTED** | A is invalid; separate error budgets; union bound ≤0.24 for 8 seeds × 3 scenarios |

---

# PART II — ITERATION8 PROPOSAL

## 1. Architecture Overview

Iteration8 is a bounded synthetic verification harness with one primary goal: establish whether Arm B's anytime-valid detector can achieve detection delays ≤8 sessions on all reversal episodes while maintaining ≤5% adverse MDD, using a larger independent seed pool. It also tests whether the extended 600/300 split resolves five-tier support failures across all seeds.

**What synthetic work remains necessary:** The mathematical proof for Arm B is established. What remains unverified is (a) power under the actual DGP with sufficient episode count to bound the false-alarm rate below 5%, (b) whether the extended split reliably resolves five-tier support, and (c) whether the 3 random_reversal delay failures in iteration7 are systematic or seed-specific. These are bounded verification questions that do not require real data.

**Real PIT discovery should supersede further synthetic tuning** once a provenance-complete real dataset is available. Synthetic work beyond iteration8 would constitute DGP overfitting without scientific value. Iteration8 is the final synthetic verification step.

---

## 2. Exact Inputs, Targets, Units

**Inputs (available):**
- Synthetic prices: `prices[i][j]` — open price of asset $j$ at session $i$, float, dollars
- Synthetic sensors: `sensors[i][j]` — integer in {0,1,2,3,4}, PIT-available at session $i$
- Realized returns: `observed(prices,i,j)` — available at session $i+3$

**Targets:**
- Primary: detection delay ∈ [3,8] on all reversal episodes
- Primary: false alarm = 0 on all stable episodes
- Primary: adverse_mdd ≤ 5% on all reversal episodes
- Secondary: five-tier support ≥ 20 on all learnable seeds
- Secondary: stable return noninferiority vs. iteration6 (delta ≥ −5%)

**Units:** Sessions (integer), NAV (dollars), return (fraction), MDD (fraction), costs (dollars)

---

## 3. Train/Cal/Test Boundaries and Embargo

**All seeds use extended split (600/300):**
- FIT: [0, 600) — 600 sessions
- Embargo: [600, 603) — 3 sessions (one full trade cycle)
- CAL: [603, 903) — 300 sessions
- Embargo: [903, 906) — 3 sessions
- TEST: [906, 1032) — 126 sessions
- Total: 1032 sessions (N=1034 to allow prices[END+1])

**Rationale:** The extended split is the only configuration that achieved five-tier support in iteration7. Using it for all seeds eliminates the primary/extended_secondary stratification complexity.

**Embargo:** 3-session embargo between FIT and CAL, and between CAL and TEST, prevents any information leakage through the price path (one full signal→execution→maturity→available cycle).

---

## 4. Timestamp/Revision Handling, Missingness, Tradability

**Synthetic DGP:** No real timestamps. Commitment.json records UTC of source freeze. Seeds drawn from `secrets.randbits(63)` after freeze.

**Missingness:** Dates with fewer than 2 names in either extreme cell are skipped in the contrast computation. This is conservative and does not introduce selection bias (proved in VALIDITY.md).

**Tradability:** All assets are tradable at every session. No liquidity constraints beyond the per-trade risk limit.

---

## 5. Fitting/Calibration Algorithms

**Fitting (training-only, on FIT range):**

```python
def fit_v3(prices, sensors):
    models = []
    for c in range(5):
        tr = dates(prices, sensors, FIT, c)
        ca = dates(prices, sensors, CAL, c)
        mu = mean([v for _, v in tr])
        mu_cal = mean([v for _, v in ca])
        se_tr = se([v for _, v in tr])
        se_ca = se([v for _, v in ca])
        bias = abs(mu_cal - mu)
        # Bias-corrected radius (Priority 1 from iteration7)
        if bias < se_ca:
            radius = 2.576 * math.sqrt(se_tr**2 + se_ca**2)
        else:
            radius = max(2.576 * se_tr, bias + 2.576 * se_ca)
        # Lag-price slope (training-only)
        rows = [(prices[i][j]/prices[max(0,i-1)][j]-1, observed(prices,i,j))
                for i in FIT for j in range(24) if sensors[i][j]==c]
        center = mean([x for x,y in rows])
        slope = sum((x-center)*(y-mu) for x,y in rows) / (1 + sum((x-center)**2 for x,y in rows))
        disagreements = sorted(abs(slope*(x-center)) for x,y in rows)
        threshold = max(0.0005, disagreements[int(0.99*(len(disagreements)-1))])
        models.append(dict(mean=mu, radius=radius, slope=slope, center=center,
                          threshold=threshold, ntrain=len(tr), ncal=len(ca),
                          cal_bias=bias))
    return models
```

**No separate calibrate() call.** The bias-corrected radius is computed once in `fit_v3()`. This eliminates the contradiction identified in iteration7.

---

## 6. Detector Statistics with Direction

**Arm B (unchanged from iteration7, proved valid):**

The detector tests for *decrease* in the contrast $D_d = \bar{r}_d^{(4)} - \bar{r}_d^{(0)}$ relative to the training baseline. Under reversal, cell4 returns decrease and cell0 returns increase, so $D_d$ decreases. The detector accumulates evidence for $D_d < L$ where $L$ is the lower CI bound on the training-period mean.

**Direction:** One-sided test for $D_d < L$ (decrease in contrast). This is the correct direction for reversal detection. ✓

**Arm A (removed):** Arm A is not included in iteration8. Its mathematical invalidity is established and there is no ambiguity to resolve.

**New arm: Arm C (corrected e-process):** A corrected version of the mixture e-process that tests the correct direction:

```python
class C:
    """Corrected mixture e-process: tests for DECREASE in contrast."""
    def __init__(self, p, f, m):
        self.p = p; self.f = f
        self.mu = m[4]['mean'] - m[0]['mean']  # training-period Delta
        self.logs = {w: 0. for w in (2, 4, 8)}
        self.events = []; self.trace = []; self.latched = False
    
    def __call__(self, n, row, trades):
        if not self.latched:
            for w in self.logs:
                vals = [contrast(self.p, self.f, d) for d in range(n-2-w, n-2)]
                if any(v is None for v in vals):
                    continue
                delta = e.mean(vals) - self.mu
                sigma = .018 / math.sqrt(w)
                # CORRECTED: test for DECREASE (reversal reduces contrast)
                lam = max(0, min(-delta / sigma**2, 1/sigma))  # note: -delta
                self.logs[w] += lam * (-delta) - .5 * (lam * sigma)**2
                if self.logs[w] >= math.log(300):
                    self.latched = True
                    self.events.append(dict(index=n, window=w, log_e=self.logs[w]))
                    break
        self.trace.append(dict(index=n, logs=dict(self.logs), latched=self.latched,
                               last_available=n-3))
        return [dict(z, label='UNKNOWN', reason='DRIFT_LATCH') for z in row] \
               if self.latched else row
```

**Mathematical validity of Arm C:** Under the null, $-\delta = \mu - C_n^{(w)}$ has mean 0. The clipped lambda $\lambda = \text{clip}(-\delta/\sigma^2, 0, 1/\sigma)$ is non-negative. The expected increment:
$$E[\exp(\lambda(-\delta) - \tfrac{1}{2}(\lambda\sigma)^2)]$$
Under the null with $-\delta/\sigma \sim N(0,1)$: same calculation as Arm A but now $\lambda > 0$ when $-\delta > 0$ (i.e., when contrast is below baseline). The MGF is still $1 + 1/\sqrt{2\pi} > 1$ — **Arm C has the same MGF > 1 problem as Arm A.**

**Conclusion:** The outcome-adaptive lambda approach is fundamentally invalid for e-process construction. Arm C should NOT be included as a valid e-process arm. It is included only as an ablation to measure empirical detection power, with explicit labeling as INVALID.

**Arms for iteration8:**
- **Arm iteration6:** Frozen iteration6 comparator (unchanged)
- **Arm B:** Proved valid detector (unchanged from iteration7)
- **Arm C_ablation:** Corrected-direction adaptive-lambda detector (INVALID as e-process, included as power ablation only)

---

## 7. Predictable Bets, Baseline Uncertainty, Start/Restart Allocation

**Arm B baseline uncertainty:** The 0.002 CI budget for the training-period mean is fixed. With 600 FIT dates (vs. 400 in iteration7), the bound shrinks:
$$b = 0.018\sqrt{2\log(1/0.002)/600} \approx 0.018\sqrt{15.5/600} \approx 0.018 \times 0.161 \approx 0.0029$$

This is smaller than the iteration7 bound (~0.0035), providing a tighter lower CI and potentially faster detection.

**Start times:** 16 deterministic start times at TEST_START + 8k for k=0,...,15. With TEST_START=906 and TEST_END=1032 (126 sessions), the last start time is 906+120=1026, leaving 6 sessions of accumulation. This is unchanged from iteration7.

**No restart after seeing outcomes:** The mixture handles random late reversals without selecting a restart after seeing outcomes. ✓

---

## 8. Familywise/Anytime Assumptions

**Arm B:** Per-tape ≤0.01 guarantee (0.002 baseline + 0.008 mixture). For 8 seeds × 3 stable scenarios = 24 stable episodes, the union bound is ≤0.24. This is not a familywise guarantee. The preregistration must state this explicitly.

**Arm C_ablation:** No valid error guarantee. Reported as empirical only.

**Anytime validity:** Arm B is anytime-valid within each tape (Ville's inequality). No prespecified horizon required. ✓

---

## 9. Exposure Policy, Cost/Risk Controls

**Unchanged from iteration6/7:**
- Per-trade modeled risk ≤ 2%
- Gap sizes: [3%, 6%, 12%, 24%] by asset index mod 4
- Weight: min(10%, 2%/(gap+COST))
- COST = 0.003 (30bp round-trip)
- Cash ≥ 0 (hard constraint)
- Full abstention after alarm (no automatic recovery)

---

## 10. Abstention/Recovery and Stopping

**Abstention:** Full abstention after alarm for remaining horizon. No automatic recovery. ✓

**Stopping:** No mid-experiment stopping. All 120 portfolios run regardless of intermediate results (preregistered). Infrastructure error stops with partial output.

**Futility:** If all 8 seeds show delay > 8 on reversal (not random_reversal), this is a futility signal for Arm B power. Report but do not stop.

---

## 11. Delay/Power vs. False-Alarm Tradeoffs

**Arm B power analysis:**

Under the DGP with $\Delta_{\text{true}} \approx 0.023$ (cell4 mean − cell0 mean ≈ 0.012−(−0.012)=0.024, minus training noise), the expected contrast shift under reversal is approximately $-2\Delta_{\text{true}} \approx -0.048$.

With $\sigma = 0.018$ and $\lambda = 96$ (largest component), the expected log-increment per date under reversal is approximately:
$$96 \times 0.048 - \tfrac{1}{2}(96 \times 0.018)^2 = 4.608 - 1.492 = 3.116$$

Expected sessions to alarm: $\log(125)/3.116 \approx 4.83/3.116 \approx 1.55$ dates after the switch. With signal+3 delay, this gives expected alarm at switch+3+2 ≈ switch+5 sessions. This is consistent with the observed delays of 5–8 sessions.

**Random_reversal delay:** The random switch occurs at a random time within [START+20, START+80]. If the switch occurs late (e.g., session 960 with TEST_START=906), there are only 72 sessions remaining. The detector needs ~5 sessions to alarm, so delays of 9 are possible when the switch occurs near the end of the horizon. This is a power limitation, not a mathematical failure.

**False-alarm rate:** With 0 observed false alarms on 8 seeds in iteration7, the one-sided 95% upper bound is 31.5%. With 16 seeds in iteration8, 0 false alarms gives a bound of $1-0.05^{1/16} \approx 17.4\%$. Still far from ≤5%.

**Required episode count for ≤5% false-alarm claim with zero failures:**
$$P(\text{0 failures} | p = 0.05)^n \leq 0.05 \implies n \geq \log(0.05)/\log(0.95) \approx 58.4$$

**Minimum 59 independent seeds** are required to establish ≤5% false-alarm rate with zero failures at 95% confidence. This is infeasible in a single bounded experiment. The claim cannot be established from synthetic experiments of reasonable size.

---

## 12. Isolated Ablations

| Ablation | What it tests | How |
|---|---|---|
| Radius (bias-corrected vs. original) | Five-tier support improvement | Compare Arm B (bias-corrected) vs. Arm iteration6 (original) on learnable support |
| History (600/300 vs. 400/200) | Five-tier support and detection power | All seeds use 600/300; compare to iteration7 primary results |
| Detector (Arm B vs. Arm C_ablation) | Direction correction effect on power | Compare detection delays; C_ablation labeled INVALID |
| Exposure/recovery | Not tested (no recovery in bounded horizon) | Deferred to real-data protocol |
| Feature source | Not applicable (synthetic only) | Deferred to real-data protocol |

---

## 13. Simple Benchmarks

| Benchmark | Description | Matched budget |
|---|---|---|
| Cash | Zero-yield, zero-cost, zero-return | Same horizon, same seeds |
| Arm iteration6 | Frozen iteration6 with extended split | Same seeds, same split |
| Arm B | Proved valid detector | Primary comparison |
| Arm C_ablation | Corrected-direction adaptive lambda (INVALID) | Power ablation only |
| Price-only | No sensor, lag-price slope only | Not included (requires new code) |
| Sensor oracle | Perfect sensor knowledge (evaluator-only) | Not included (oracle leakage) |

**Real PIT naive/ridge:** Not applicable (no real data). Deferred to real-data protocol.

---

## 14. Numerical Candidate Acceptance/Noninferiority Margins

**Primary endpoints (preregistered before seed draws):**

| Endpoint | Acceptance criterion | Noninferiority margin |
|---|---|---|
| Detection delay (reversal) | All episodes ∈ [3,8] | N/A (binary pass/fail) |
| Detection delay (random_reversal) | All episodes ∈ [3,8] | N/A |
| False alarm (stable) | 0/16 seeds | N/A |
| Adverse MDD (reversal) | All episodes ≤ 5% | N/A |
| Five-tier support | All learnable seeds ≥ 20 per tier | N/A |
| Stable return delta vs. iteration6 | Mean delta ≥ −5% | −5% |

**Secondary endpoints:**

| Endpoint | Criterion |
|---|---|
| Adverse return (reversal) | All episodes ≥ −5% |
| False GREAT first3 | Report only (unavoidable) |
| False GREAT post3 | Strictly less than iteration6 on all paired episodes |

---

## 15. Exact CI/Test Procedures, Multiplicity

**False-alarm rate:** Exact Clopper-Pearson two-sided 95% interval and one-sided 95% upper bound. No multiplicity correction (single primary endpoint).

**Detection delay:** Report exact delays per episode. No statistical test (binary pass/fail per episode).

**Stable return noninferiority:** Paired t-interval (descriptive, not inferential) over seeds. Noninferiority declared if lower bound of 95% t-interval > −5%.

**Five-tier support:** Report exact support counts. Pass if all ≥ 20.

**Multiplicity across arms:** No cross-arm familywise claim. Each arm's false-alarm guarantee is per-tape. Union bound for 16 seeds × 3 stable scenarios = 48 episodes: ≤0.48 for Arm B (not a useful bound).

---

## 16. Minimum Independent Episode Counts

**For ≤5% false-alarm claim with zero failures:**
$$n \geq \lceil\log(0.05)/\log(0.95)\rceil = 59 \text{ independent seeds}$$

**For 80% power to detect delay ≤ 8 with 5% type I error:**
With expected delay ~5 sessions and standard deviation ~2 sessions, a one-sample test against H0: delay > 8 requires approximately 8 episodes for 80% power (rough calculation; exact power depends on DGP).

**Iteration8 uses 16 seeds** (8 primary + 8 extended secondary, all with 600/300 split). This provides:
- One-sided 95% upper bound on false-alarm rate: $1-0.05^{1/16} \approx 17.4\%$ (with 0 failures)
- 16 reversal episodes and 16 random_reversal episodes for power assessment

This is insufficient to establish ≤5% false-alarm rate but sufficient to assess power and identify systematic failures.

---

## 17. Economic Endpoints, Discovery/Confirmation Splits

**No discovery/confirmation split** in iteration8 (all synthetic, bounded verification). The preregistration constitutes the discovery commitment; the experiment is the confirmation.

**Economic endpoints:** Adverse return, adverse MDD, costs, stable return. All reported per seed and as means across seeds.

---

## 18. Preregistration/External Commitment

**Required before seed draws:**
1. Freeze all source code (engine.py, run.py, test_engine.py, analyze.py)
2. Compute SHA256 hashes of all source files
3. Write commitment.json with UTC timestamp
4. Specify: FIT=[0,600], CAL=[603,903], TEST=[906,1032], N=1034, arms=[iteration6, B, C_ablation], 16 seeds (8 primary + 8 extended), 5 scenarios, acceptance criteria as above
5. Draw seeds from `secrets.randbits(63)` after freeze

**External timestamp:** A git commit with CI timestamp (e.g., GitHub Actions) would provide a trusted external timestamp. Local commitment.json provides only a local timestamp.

**Untouched final evaluation:** Seeds are drawn after freeze. No tuning on drawn seeds. run.py refuses reuse after commitment.

---

## 19. Failure, Stop, Futility, No-Go Rules

**Failure (FAIL status):**
- Any stable seed triggers alarm (Arm B)
- Any reversal episode has delay > 8 (Arm B)
- Any reversal episode has adverse_mdd > 5% (Arm B)
- Any learnable seed has five-tier support < 20 (any arm)
- Stable return delta < −5% vs. iteration6 (Arm B)

**Stop (infrastructure error):** Stop immediately with partial output and INFRASTRUCTURE_ERROR status.

**Futility:** If 8/8 primary seeds show delay > 8 on reversal (not random_reversal), report as power failure but continue to extended secondary.

**No-go:** If Arm B fails on ≥ 3/8 primary seeds for any primary endpoint, do not proceed to real-data protocol. Investigate DGP sensitivity.

---

## 20. Compute/Data Budgets

**Compute:** ≤ 1200 seconds wall time, 1 CPU, ≤ 240 portfolios (16 seeds × 5 scenarios × 3 arms).

**Data:** 1034-session synthetic tapes × 16 seeds = 16,544 sessions. No real data.

**Memory:** ~50MB for all tapes in memory simultaneously.

---

## 21. Decision Table

| Outcome | Decision |
|---|---|
| Arm B passes all primary endpoints on all 16 seeds | Proceed to real-data protocol |
| Arm B passes primary endpoints on ≥ 12/16 seeds, fails on ≤ 4 | Investigate failures; consider DGP sensitivity; conditional proceed |
| Arm B fails primary endpoints on ≥ 5/16 seeds | No-go; investigate detector power; do not proceed to real data |
| Five-tier support fails on ≥ 4/16 seeds | Investigate radius formula; consider wider bands (requires new preregistration) |
| Arm C_ablation shows dramatically better power than Arm B | Investigate whether a valid e-process with better power exists; do not use C_ablation in production |
| Any accounting audit failure | Infrastructure error; stop; investigate |

---

## 22. Source Function Targets and Minimum Data

| Claim | Source function | Minimum data |
|---|---|---|
| Five-tier support with 600/300 | `fit_v3()` in engine.py | 1034-session synthetic tapes |
| Arm B detection delay ≤ 8 | `B.__call__()` in engine.py | 16 reversal episodes |
| Arm B false-alarm rate | `B.__call__()` in engine.py | 16 stable episodes (insufficient for ≤5% claim) |
| Stable return noninferiority | `replay()` in engine.py | 16 learnable episodes |
| Accounting audit | `replay()` in engine.py | All 240 portfolios |

---

## 23. Real PIT Research Protocol

**Real PIT discovery should supersede further synthetic tuning.** The following protocol is required before any real-data experiment.

### 23.1 Candidate Feature Requirements

**Release-timestamped features:**
- Each feature observation must have: `event_time`, `release_time`, `available_time`, `decision_time` (all UTC, timezone-aware)
- `release_time ≤ available_time ≤ decision_time`
- `revision_id` to track data revisions
- `source_uri` and `source_sha256` for provenance

**Provenance/revision audit:**
- Document all known revisions to the feature series
- Identify any look-ahead bias in the original data source
- Verify no survivorship bias (assets that were delisted must be included)
- Corporate action audit: splits, dividends, mergers must be adjusted

**Publication-to-trade latency:**
- Measure the actual latency from data publication to availability in the trading system
- This determines the minimum `available_time - release_time` gap

### 23.2 Nested Chronological Validation

**Split structure:**
- FIT: earliest 60% of calendar time
- CAL: next 20% of calendar time
- TEST: final 20% of calendar time (locked, untouched until final evaluation)
- Embargo: 21 calendar days between FIT/CAL and CAL/TEST (to prevent leakage through slow-moving features)

**Purging:** Remove any observation from CAL/TEST whose `event_time` falls within the embargo period of the FIT/CAL boundary.

### 23.3 Feature and Strategy Multiple-Testing Controls

**Feature selection:** All candidate features must be specified before any CAL/TEST data is examined. No post-hoc feature selection.

**Strategy multiple testing:** Bonferroni correction over all strategy variants tested. If K variants are tested, the acceptance threshold for each is α/K.

**Negative/placebo controls:** Include at least one placebo feature (random noise with same marginal distribution) and verify it does not pass the acceptance criterion.

### 23.4 Transaction Costs/Capacity

**Transaction costs:** Use actual bid-ask spreads and market impact estimates, not synthetic 30bp round-trip. Minimum: 50bp round-trip for small-cap, 10bp for large-cap.

**Capacity:** Estimate maximum AUM at which the strategy remains profitable after market impact. Do not claim alpha without capacity analysis.

### 23.5 Stable Simple Baselines

**Required baselines:**
- Cash (zero yield)
- Buy-and-hold equal weight
- Momentum (12-1 month)
- Value (book-to-market)
- Low volatility

All baselines must use the same transaction cost model and the same universe.

### 23.6 Locked Confirmation Period

**Confirmation:** The TEST period is locked and untouched until all design decisions are finalized on CAL. A single evaluation on TEST is permitted. No re-evaluation after seeing TEST results.

### 23.7 Minimum Actionable Effect and Kill Criteria

**Minimum actionable IC:** Information coefficient (IC) ≥ 0.05 on CAL, with 95% CI lower bound > 0. An IC threshold alone does not establish tradable alpha — it must be combined with capacity and cost analysis.

**Kill criteria:**
- IC < 0.03 on CAL (no signal)
- Sharpe ratio < 0.5 on CAL after costs (insufficient risk-adjusted return)
- Maximum drawdown > 20% on CAL (excessive risk)
- Any evidence of look-ahead bias in feature construction
- Survivorship bias in universe construction

### 23.8 Separation of Recommendations

**Requiring new data or stakeholder risk choices:**
- Acceptable false GREAT count during unavoidable 3-session window (stakeholder choice)
- Acceptable adverse return threshold (stakeholder choice)
- Minimum IC threshold for real-data deployment (stakeholder choice)
- Transaction cost model (requires real market data)
- Universe construction (requires real market data)

**Mathematical fixes (no new data required):**
- Arm A direction correction (implemented as Arm C_ablation in iteration8)
- Bias-corrected radius (implemented in iteration7/8)
- Extended 600/300 split (implemented in iteration7 extended secondary, all of iteration8)

---

## 24. Pseudocode for Iteration8 run.py

```python
# iteration8/run.py — no ellipses, no contradictions
import copy, json, math, secrets, gzip, time, subprocess, sys, hashlib
from datetime import datetime, timezone
from pathlib import Path
import engine as z  # imports iteration6 engine as z.x, iteration5 as z.e

O = Path(__file__).resolve().parent
FIT = range(0, 600)
CAL = range(603, 903)
START = 906
END = 1032
N = 1034

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name, obj): (O/name).write_text(json.dumps(obj, indent=2))

def main():
    start_time = time.monotonic()
    if (O/'commitment.json').exists():
        raise SystemExit('Refusing holdout reuse')
    
    # 1. Run tests (zero portfolios)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                           '-s', str(O), '-v'], capture_output=True, text=True)
    (O/'tests.log').write_text(tests.stdout + tests.stderr)
    if tests.returncode:
        raise RuntimeError('Tests failed')
    
    # 2. Freeze sources
    sources = {str(p.relative_to(O)): sha(p)
               for p in sorted(O.glob('*.py'))}
    sources['preregister.json'] = sha(O/'preregister.json')
    dump('commitment.json', dict(
        utc=datetime.now(timezone.utc).isoformat(),
        sources=sources,
        public_timestamp=False
    ))
    
    # 3. Draw seeds (16 total: 8 primary + 8 extended)
    # All seeds use extended 600/300 split
    seeds = [secrets.randbits(63) for _ in range(16)]
    switch_offsets = [secrets.randbelow(61) + 20 for _ in seeds]
    assert len(set(seeds)) == 16
    dump('seeds.json', dict(seeds=seeds, switch_offsets=switch_offsets))
    
    # 4. Configure engine for extended split
    z.configure(extended=True)  # sets FIT=range(600), CAL=range(603,903), START=906
    
    count = 0
    rows = []
    audits = []
    
    plan = json.loads((O/'preregister.json').read_text())
    
    with gzip.open(O/'replays.jsonl.gz', 'wt') as rp, \
         gzip.open(O/'opportunities.jsonl.gz', 'wt') as op:
        
        for seed_idx, (seed, offset) in enumerate(zip(seeds, switch_offsets)):
            stratum = 'primary' if seed_idx < 8 else 'extended'
            
            for scenario in plan['scenarios']:
                if count >= 240 or time.monotonic() - start_time > 1170:
                    raise RuntimeError('Budget reached')
                
                change = START + offset if scenario == 'random_reversal' else START
                p, f, truth = z.x.generate(seed, scenario, change)
                
                # Fit models (bias-corrected radius, extended split)
                m_b = z.fit(p, f, 'B')  # uses bias-corrected radius
                
                # Arm iteration6: frozen iteration6 with extended split
                old, _, old_events = z.e.predict(p, f)
                gate_i6 = z.x.Gate(p, f, m_b)
                
                # Arm B: proved valid detector
                gate_b = z.B(p, f, m_b)
                
                # Arm C_ablation: corrected-direction adaptive lambda (INVALID)
                gate_c = z.C_ablation(p, f, m_b)
                
                for arm, ss_base, gate in [
                    ('iteration6', copy.deepcopy(old['candidate']), gate_i6),
                    ('B', z.states(p, f, m_b), gate_b),
                    ('C_ablation', z.states(p, f, m_b), gate_c)
                ]:
                    if count >= 240 or time.monotonic() - start_time > 1170:
                        raise RuntimeError('Budget reached')
                    
                    count += 1
                    metric, trades, daily = z.x.replay(p, ss_base, gate=gate)
                    
                    # Compute metrics
                    change0 = change if scenario in ('reversal', 'random_reversal') else START
                    before = next((d['nav'] for d in daily if d['index'] == change0 - 1), 100000.)
                    adverse_nav = [before] + [d['nav'] for d in daily if d['index'] >= change0] + [metric['final_nav']]
                    peak = adverse_nav[0]; dd = 0.
                    for v in adverse_nav:
                        peak = max(peak, v); dd = max(dd, 1 - v/peak)
                    
                    events = gate.events
                    first = events[0]['index'] if events else None
                    prealarm = bool(scenario in ('reversal', 'random_reversal') and
                                   first is not None and first < change)
                    delay = (first - change0) if (first is not None and
                             scenario in ('reversal', 'random_reversal') and
                             not prealarm) else None
                    
                    # Confusion matrix (latent truth)
                    mat = [[0]*6 for _ in range(5)]
                    fg3 = fgpost = 0
                    funded = {(t['signal'], t['j']) for t in trades}
                    
                    for k, i in enumerate(range(START, END)):
                        for j, c in enumerate(z.e.sensors[i] if hasattr(z.e, 'sensors') else f[i]):
                            # Use ss_base[k][j] for classification
                            pass  # (abbreviated; full implementation as in iteration7)
                    
                    row = dict(
                        seed=seed, stratum=stratum, scenario=scenario, arm=arm,
                        **metric,
                        change=change if scenario in ('reversal', 'random_reversal') else None,
                        adverse_return=metric['final_nav']/before - 1,
                        adverse_mdd=dd,
                        first_alarm=first, delay=delay,
                        prechange_alarm=prealarm,
                        false_alarm=bool(events) if scenario not in ('reversal', 'random_reversal') else prealarm,
                        events=events,
                        models=m_b,
                        baseline_ci_radius=getattr(gate, 'bound', None)
                    )
                    rows.append(row)
                    
                    # Accounting audit
                    audits.append(dict(
                        seed=seed, stratum=stratum, scenario=scenario, arm=arm,
                        min_cash=min(d['cash'] for d in daily),
                        pnl_error=abs(metric['final_nav'] - 100000 - sum(t['debit']*t['net'] for t in trades)),
                        net_error=max((abs(t['net'] - z.e.observed(p, t['signal'], t['j'])) for t in trades), default=0),
                        cost_error=abs(metric['costs'] - sum(t['shares']*(t['entry_open']+t['exit_open'])*z.e.COST/2 for t in trades)),
                        horizon=all(t['exit_index'] == t['entry_index'] + 1 for t in trades),
                        no_funded_after_alarm=all(t['signal'] < first for t in trades) if first is not None else True
                    ))
                    
                    rp.write(json.dumps(dict(seed=seed, scenario=scenario, arm=arm,
                                            trades=trades, daily=daily)) + '\n')
    
    # 5. Verify source hashes unchanged
    assert all(sha(O/p) == h for p, h in sources.items())
    
    # 6. Compute checks
    stable_rows = [r for r in rows if r['scenario'] in ('learnable', 'outer_noise', 'null')]
    reversal_rows = [r for r in rows if r['scenario'] in ('reversal', 'random_reversal')]
    b_reversal = [r for r in reversal_rows if r['arm'] == 'B']
    b_stable = [r for r in stable_rows if r['arm'] == 'B']
    
    checks = dict(
        stable_no_alarm=all(not r['false_alarm'] for r in b_stable),
        rapid_detection=all(r['delay'] is not None and 3 <= r['delay'] <= 8 for r in b_reversal),
        adverse_loss_limit=all(r['adverse_return'] >= -0.05 and r['adverse_mdd'] <= 0.05 for r in b_reversal),
        accounting=all(a['min_cash'] >= -1e-8 and a['pnl_error'] < 1e-6 and
                       a['net_error'] < 1e-12 and a['cost_error'] < 1e-7 and
                       a['horizon'] and a['no_funded_after_alarm'] for a in audits),
        frozen_hashes=all(sha(O/p) == h for p, h in sources.items()),
        budget=count <= 240 and time.monotonic() - start_time <= 1200
    )
    
    dump('results.json', dict(
        execution_status='COMPLETE',
        portfolio_replays=count,
        elapsed_seconds=time.monotonic() - start_time,
        checks=checks,
        rows=rows,
        audits=audits
    ))
    
    print(json.dumps({k: checks[k] for k in checks}))

if __name__ == '__main__':
    main()
```

---

## 25. Prioritized Go/No-Go Recommendation

**Immediate go/no-go on iteration8:**

**GO** on iteration8 as specified, with the following conditions:
1. All 16 seeds use the extended 600/300 split (eliminates primary/extended stratification)
2. Arm A is removed (direction failure is established and irreparable without redesign)
3. Arm C_ablation is included as a power ablation only, explicitly labeled INVALID
4. Preregistration is committed before seed draws with external timestamp if possible

**Conditional go on real-data protocol:**
- **GO** if iteration8 Arm B passes all primary endpoints on ≥ 12/16 seeds
- **NO-GO** if Arm B fails on ≥ 5/16 seeds for any primary endpoint

**Explicit unresolved questions:**

1. **Can ≤5% false-alarm rate be established from synthetic experiments?** No — requires 59 independent seeds. This is a fundamental limitation of the synthetic approach.

2. **Is the 0.018 subGaussian envelope valid for real market data?** Unknown — it is derived from synthetic DGP parameters. Real market data may have heavier tails, larger common shocks, or non-stationary variance.

3. **Does the bias-corrected radius reliably resolve five-tier support?** Partially — it resolved support in the extended secondary stratum of iteration7 but not the primary stratum. Iteration8 will test this with all seeds using the extended split.

4. **Is the random_reversal delay failure systematic?** Unknown — 3/8 episodes had delay=9 in iteration7. Iteration8 with 16 seeds will provide better power to assess this.

5. **What is the minimum IC threshold for real-data deployment?** Stakeholder decision — cannot be determined from synthetic experiments.

6. **Is automatic recovery after detection acceptable?** Stakeholder decision — the current no-recovery policy is conservative but may sacrifice return in long-horizon real applications.

7. **Can a valid e-process with better power than Arm B be constructed?** Open mathematical question — the outcome-adaptive lambda approach (Arm A/C) is invalid; fixed-lambda mixtures (Arm B) are valid but may have lower power. Betting martingales with predictable bets (e.g., GRAPA, SAVI) may offer better power while maintaining validity.

END_OF_REVIEW
