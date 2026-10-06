# Independent post-experiment audit

## Executive verdict

**DEV117 supports a narrower and less flattering conclusion than “MTS has discovered a robust 15–18% system,” but a more favorable conclusion than “the GA found nothing except equity drift.”**

My assessment is:

1. **There is evidence of partial cross-stock economic transfer, conditional on the same historical market path.** Some frozen strategies remained profitable on different stocks, with materially less than full investment. That merits attribution work. It does not yet establish factor-adjusted alpha, prospective performance, or reliable crash defense.

2. **The 15–18% headline describes a favorable subset, not the whole experiment.** All 23 reported finalist rows lost CAGR from training to blind; 21 experienced worse drawdowns. The representative genomes are also not matched at the same training risk level.

3. **Risk control has not been demonstrated as portable.** This is not merely failure on an unseen crash: the stock folds share the same crash dates. Several policies failed to maintain risk behavior even when transported across stocks on a familiar market path.

4. **The experiment confounds stock generalization with a substantial change in portfolio opportunity-set size: 80 stocks become 37.** Under the proposed allocation equations, that can mechanically change gross exposure, qualification, concentration, peer estimates, and lifecycle behavior. This is a major unresolved design issue.

5. **The prior lifecycle design contains a potentially consequential defect.** If implemented as written, applying uncertainty penalties both inside asset values and again in the move hurdle causes incumbent uncertainty to cancel from exit decisions. Combined with large kappa, this can make “opportunity disappeared” mean “stop buying,” not “sell.”

6. **Gamma and kappa saturation are warnings about concentration, scale identification, and path dependence—not evidence that their bounds should simply be increased.**

7. **Nothing presented establishes a credible path to durable, cost-inclusive returns near 96% annually, much less 10–11% compounded monthly, under the stated constraints.** Such returns are not mathematically prohibited. They are economically extraordinary, and these results do not demonstrate the information advantage needed.

**Recommendation:** Do not launch another large GA or open protected evidence yet. Conduct a bounded forensic audit using consumed artifacts, starting with lifecycle semantics, 80-to-37 cardinality effects, and daily return attribution. Continue only if that audit identifies an economically meaningful residual edge or a specific, material implementation/design failure.

### Scope and evidentiary labels

This is a documentary audit of the supplied packet. I have not inspected source code, daily ledgers, search archives, or protected evidence. The appended prior review is a design proposal to audit—not proof of implementation.

I distinguish:

- **Findings:** supported by the supplied observations.
- **Hypotheses:** explanations consistent with those observations.
- **Required audits:** tests needed to distinguish those explanations.
- **Scientific changes:** recommendations requiring owner approval before implementation.

---

## 1. What the results establish—and what they do not

### 1.1 The reported result is heterogeneous

The four highlighted representatives are:

| Fold | Train CAGR / MDD | Blind CAGR / MDD | Blind average gross |
|---|---:|---:|---:|
| 0 | 19.12% / −24.26% | 17.60% / −27.35% | 79.0% |
| 1 | 25.87% / −39.99% | 15.99% / −29.52% | 66.6% |
| 2 | 19.58% / −24.96% | 15.76% / −30.03% | 87.1% |
| 3 | 24.78% / −24.46% | 14.75% / −47.48% | 83.0% |

**Fold 1 is not a comparable “middle-risk” training point:** its representative is a roughly 40%-drawdown training candidate, versus roughly 25% in the other folds.

Across the complete report:

- Blind CAGR ranges from **1.20% to 17.60%**.
- Seven of the 23 reported rows fall strictly between 15% and 18%.
- **All 23 have lower blind CAGR than training CAGR.**
- **21 of 23 have worse blind MDD than training MDD.**

Different finalists deliberately occupy different risk regions, so these counts are not failure probabilities for one deployable strategy. Nevertheless, they prevent treating the favorable representatives as the outcome of the entire procedure.

Unless those particular representatives were designated before blind replay, their similar returns are a **retrospective descriptive pattern**, not the estimated performance of a preselected deployment rule.

### 1.2 Some findings are genuinely positive

The experiment appears to have repaired important operational deficiencies:

- SAFE is materially used.
- Genomes are structurally diverse.
- Some attractive candidates survive substantial cost stress.
- Training MDD retains some association with blind MDD.
- Some policies produce attractive returns on stocks excluded from their own evolution.
- The reported freeze-before-blind ordering is substantially better governance than selecting a frontier after viewing blind results.

Those are real improvements. They should not be dismissed merely because an unverified commercial claim is much larger.

### 1.3 But the scope of validation remains narrow

The experiment does **not** establish:

- Independent market-timing or crash-defense replication.
- Prospective return expectations.
- Statistically significant residual alpha.
- Robustness to changing market structure.
- Robustness to survivorship or universe-selection bias.
- A deployable combined portfolio earning the average of the four representative CAGRs.
- That the architecture was faithfully implemented.
- That the GA exhausted the economically useful hypothesis space.

The four folds are also dependent in more than one way:

- They share the market path.
- Blind memberships overlap.
- Any two training sets of 80 drawn from 117 must share at least **43 stocks**.
- The research architecture was developed with knowledge of this historical environment.

Freezing all finalists before blind replay controls an important form of adaptive selection. It does not remove historical design hindsight or make these four independent experiments.

---

## 2. Is the return skill, exposure, or overfit?

**The best current answer is a mixture, with the proportions unidentified.**

There is a clear common-exposure component, substantial training optimism, and a plausible—but unmeasured—stock-selection/timing contribution.

### 2.1 What the exposure correlations say

The supplied correlation between blind CAGR and average gross is **0.865**.

Its squared value is approximately **0.748**. Thus, descriptively, a simple pooled linear relationship with gross accounts for about three quarters of the cross-finalist variation in CAGR.

That is **not** equivalent to saying “75% of returns are equity drift.”

Reasons:

- These are selected, dependent finalists.
- Risk bands deliberately generate exposure variation.
- Gross is not beta.
- Stock selection can affect both exposure and performance.
- Fold-specific opportunity sets and policy parameters confound the relationship.
- A cross-strategy correlation is not a time-series P&L attribution.

Nevertheless, the association is too strong to ignore. Much of the observed performance frontier appears to be an **exposure frontier**, not solely a stock-picking frontier.

Likewise:

- Gross versus absolute blind MDD: \(r=0.599\), \(r^2\approx0.359\).
- Train versus blind absolute MDD: \(r=0.670\), \(r^2\approx0.449\).

The latter means training risk is not completely uninformative. It does not mean it is calibrated. A predictor can rank candidates moderately well while systematically understating their losses.

### 2.2 The SPY/SAFE comparison is encouraging, but not an alpha estimate

The stated excesses of approximately **5.2–8.4 percentage points** deserve investigation.

They are inconsistent with dismissing the favorable representatives as obviously equivalent to a constant, low-gross SPY allocation.

But the quoted mixtures are numerically consistent with linearly combining approximately:

- SPY CAGR: **11.18%**
- SAFE CAGR: **1.66%**

For example:

\[
0.79(11.18\%)+0.21(1.66\%)\approx9.18\%.
\]

If that is the construction, it is **not the realized CAGR of a rebalanced SPY/SAFE portfolio**. Portfolio CAGR is not a weighted average of component CAGRs.

More importantly, the comparison fails to control for:

- Actual daily exposure timing.
- Market beta.
- Technology, growth, momentum, quality, size, or other style exposures.
- The return characteristics of the DEV117 stock-selection universe.
- Concentration.
- Benchmark implementation costs.

A strategy holding high-beta growth winners at 70% gross can have more market risk than SPY at 70% gross.

### 2.3 The attribution that should replace it

For an execution-consistent return interval, with no shorts:

\[
R^{MTS}_t
=
\sum_i w_{it}R_{it}+(1-g_t)R^{SAFE}_t-C_t,
\]

where \(g_t=\sum_i w_{it}\).

Construct a benchmark with **the identical exposure path**:

\[
R^{B,path}_t
=
g_tR^B_t+(1-g_t)R^{SAFE}_t-C^B_t.
\]

The daily difference is:

\[
R^{MTS}_t-R^{B,path}_t
=
\sum_i w_{it}(R_{it}-R^B_t)-(C_t-C^B_t).
\]

That separates security selection from aggregate exposure.

Then compare the same-exposure-path benchmark with a constant-\(\bar g\) benchmark. Before cost differences, its daily timing contribution is:

\[
(g_t-\bar g)(R^B_t-R^{SAFE}_t).
\]

Run this against:

1. Actual SPY.
2. Appropriate passive portfolios of each fold’s eligible stocks.
3. Simple, implementable style baselines.
4. A factor-attribution model, with uncertainty estimates.

Compound the resulting portfolios correctly. Do not add annual CAGR differences as if they were exact additive contributions.

**Until this exists, neither “meaningful alpha” nor “just drift” is established.**

---

## 3. Why different genomes can produce similar economic returns

First, the convergence is narrower than the question suggests: **the full finalist set did not converge to 15–18%.** The favorable representatives did.

Second, structural diversity does not imply economic diversity.

The Jaccard results convincingly reject “all folds found almost the same feature list.” They do not reject:

- Different features measuring the same trend or momentum state.
- Different gates activating on the same dates.
- Different stock rankings producing similar factor exposures.
- Different strategies repeatedly owning the same economic type of stock.
- Allocation and lifecycle rules overwhelming differences in raw signals.

Many price-derived features are highly redundant. Momentum, breakout, moving-average geometry, relative strength, and pullback logic can all result in persistent ownership of recent leaders.

### Most plausible explanations for the common neighborhood

1. **Common equity/style exposure on the same market path.**
2. **A shared restricted opportunity set.** Different selection rules can reach similar results from the same collection of historical stocks.
3. **A shared allocation bottleneck.** High gamma and similar lifecycle friction may convert different scores into similar concentrated, persistent portfolios.
4. **Selection of favorable representatives.**
5. **Training overfit regressing toward a common out-of-sample economic baseline.**
6. **Search or representation limitations.** Possible, but not demonstrated by genotype overlap.

The decisive measurements are behavioral:

- Daily return correlations.
- Exposure-path correlations.
- Holdings overlap.
- Factor loadings.
- Contribution overlap by stock and episode.
- Similarity of entry and exit dates.
- Performance when evaluated on a common consumed universe.

**Do not interpret this neighborhood as a discovered mathematical ceiling. Equally, do not assume more genome diversity will move it upward.**

---

## 4. A major confound: 80 stocks versus 37

This deserves priority comparable to the prior rank-cancellation defect.

### 4.1 Allocation cardinality is built into the proposed equations

The prior design specifies:

\[
r_i=\tau g_i,\qquad
G=\sum_i |r_i|,\qquad
g^{target}=\min(1,G).
\]

If the opportunity distribution is otherwise similar, the expected sum of claims scales with the number of eligible stocks.

Moving from 80 stocks to 37 changes that count by:

\[
37/80=0.4625.
\]

Before saturation, gross exposure could therefore fall substantially **without any deterioration in predictive skill**.

This does not imply every portfolio should be invariant to universe size. More genuinely attractive opportunities can reasonably attract more capital. But the experiment currently mixes:

- Transfer to unfamiliar stocks.
- Fewer opportunities.
- Reduced diversification.
- Different score order statistics.
- Different peer estimates.
- Different calibration samples.
- Different cross-sectional normalization.

It is not a clean stock-generalization test.

### 4.2 Discrete percentile effects could be severe

As one concrete implementation audit:

If cross-sectional percentiles use \(r/(N+1)\), then the maximum is:

- \(80/81\approx0.9877\) in training.
- \(37/38\approx0.9737\) in blind.

A qualification threshold of 0.98 would be reachable in the former and impossible in the latter.

I am **not claiming this normalization was used**. It illustrates why thresholds trained on one cross-sectional size can become structurally different policies on another.

Sharp gates and large gamma make such effects more consequential.

### 4.3 Dynamic peers introduce another distribution shift

A peer feature computed within 80 stocks is not necessarily the same statistical object when recomputed within 37:

- Peers disappear.
- Clusters change.
- Peer-count reliability declines.
- Relative ranks become coarser.
- Group estimates become noisier.

The prescribed causality and permutation tests do not eliminate this issue.

### 4.4 The immediate diagnostic

Replay each frozen genome on repeated **37-of-80 training subsets**, without evolving anything.

Compare:

- Full training-80.
- Subsampled training-37.
- Actual blind-37.

Recompute the relevant features and contextual relationships exactly as the production algorithm would.

Also perform forensic variants that separate:

1. Removing securities while preserving their existing feature values.
2. Recomputing cross-sectional transforms.
3. Recomputing peer relationships.
4. Reinitializing online calibration.

These are diagnostics, not new validation results.

**If training-37 reproduces much of the blind degradation, the original experiment overstates stock-generalization failure and exposes a portfolio portability problem instead.**

---

## 5. Gamma and kappa: what the boundary solutions actually imply

### 5.1 Gamma: concentration and estimation-error amplification

With normalized strength-like claims, relative allocations satisfy approximately:

\[
\frac{w_i}{w_j}
=
\left(\frac{x_i}{x_j}\right)^\gamma.
\]

At \(\gamma=6\), a 2:1 advantage becomes **64:1**.

For downside allocation:

\[
g_i=
\left(\frac{\max(V_i-q,0)}{d_i}\right)^\gamma.
\]

At gamma 6, underestimating downside by 10% increases the claim by approximately:

\[
(1/0.9)^6\approx1.88.
\]

Thus a modest estimation error can almost double an allocation claim.

This matters because three of the four representatives use downside allocation. The label “downside” does not make the result conservative. Raising an uncertain inverse-downside estimate to a high power can be an aggressive concentration mechanism.

Required checks:

- Effective holdings count.
- Largest weights.
- Sector/style concentration.
- Downside-estimator definitions and floors.
- Weight sensitivity to small input perturbations.
- Contribution dependence on a few stocks.
- Whether high gamma improves training primarily through hindsight winner selection.

Also, when gross is not saturated, gamma changes total claim mass—not just relative concentration. Its economic meaning is entangled with opportunity scaling, q, and tau.

**Boundary saturation says “the chosen formulation is pushing against a constraint.” It does not identify whether the right response is a wider bound, regularization, better calibration, or a different allocation rule.**

### 5.2 Kappa: persistence, scaling, or a pathology

Large kappa could reflect:

- A useful preference for lower turnover.
- Compensation for noisy signals.
- Excessively large opportunity-score units.
- A fitness advantage from holding a small number of historical winners.
- Avoidance of bad replacement trades.
- A lifecycle mechanism that prevents timely defensive exits.

Those explanations are economically very different.

If values really are expected returns **per session**, kappa 20 is striking. At 5 bps one-way cost:

- Entry/exit hurdle: \(20\times5=100\) bps in daily-value units.
- Replacement hurdle: \(20\times10=200\) bps.

Those are very large daily expected-return differences.

If this is not the effective economic scale, then the “absolute expected return” interpretation needs auditing.

The affine opportunity map can create scale non-identification: rescaling opportunities, qualifications, risk appetite, and kappa together can preserve similar behavior. An endpoint kappa may therefore be compensating for arbitrary score units rather than expressing meaningful economic patience.

**Kappa is not a 20-day holding horizon.** The original design’s “horizon-free” wording should not obscure that it still embeds a relationship between one-session opportunity and one-time trading costs.

---

## 6. A design-level lifecycle defect that could explain poor defense

This is the most important criticism of the prior recommendation itself.

The prior design defines:

\[
V_i=E_i-\lambda u_i
\]

and permits a move \(a\rightarrow b\) only when:

\[
V_b-V_a>
\kappa c_{ab}+\lambda(u_a+u_b).
\]

If implemented literally, consider exiting a long position to SAFE.

Because SAFE has value and uncertainty zero:

\[
-(E_i-\lambda u_i)>
\kappa c_i+\lambda u_i.
\]

The uncertainty terms cancel:

\[
-E_i>\kappa c_i.
\]

**An increase in incumbent uncertainty does not, by itself, make exit to SAFE easier.**

For entry from SAFE:

\[
E_i>\kappa c_i+2\lambda u_i.
\]

For replacement of \(i\) with \(j\):

\[
E_j-E_i>
\kappa c_{ij}+2\lambda u_j.
\]

Again, incumbent uncertainty cancels.

The result is an asymmetric policy:

- Uncertainty strongly discourages new positions.
- Incumbent uncertainty does not directly encourage exit.
- Large kappa creates a wide inaction region.

That is not the intended intuitive meaning of continuous competition among opportunity, uncertainty, and SAFE.

### A related trap: zero opportunity is not an exit instruction

Suppose a market gate shuts down a strategy and its opportunity falls to zero.

The allocation target may become SAFE. But moving from a zero-valued incumbent to zero-valued SAFE does not clear a positive friction hurdle.

The portfolio can therefore remain invested despite a defensive target.

This is especially concerning if market information primarily enters through applicability gates.

### What is established here?

- **Finding about the prior equations:** the algebra above follows from them.
- **Hypothesis about DEV117:** this mechanism contributed to poor crash transport.
- **Required audit:** determine whether the actual engine used these equations and how target reductions interact with the move ledger.
- **Scientific change requiring approval:** revise the lifecycle if the economic behavior is undesirable.

This should not be blamed solely on implementation. **If implemented faithfully, the design itself deserves responsibility.**

A coherent replacement need not impose fixed holding periods. It can remain state-based while using a consistent risk-adjusted continuation value and transaction-cost no-trade region.

---

## 7. Why risk transports worse than returns

There are several mutually compatible explanations.

### 7.1 Return averages many opportunities; MDD selects one extreme path

CAGR aggregates roughly two decades of compounding.

MDD is a nonlinear extreme statistic driven by:

- Particular holdings.
- Their overlap during a loss episode.
- Entry and exit timing.
- Concentration.
- Correlation jumps.
- The preceding wealth peak.

A stock-selection strategy can retain some average edge while its worst loss changes dramatically.

### 7.2 Single-path MDD is easy to overfit

A large search can find policies that avoid particular historical losses through:

- Fortunate stock selection.
- Particular start-date allocations.
- Narrow gate thresholds.
- Exposure reductions tailored to recognizable historical states.

That does not require transferable crash forecasting.

The near-band training MDD values are consistent with optimization spending the allowed historical drawdown budget. A historical band is not a forward risk guarantee.

### 7.3 The risk estimator may not represent portfolio risk

Per-stock downside weighting does not necessarily control:

- Common factor exposure.
- Sector concentration.
- Correlation during stress.
- Gap risk.
- Joint losses among ostensibly attractive stocks.

No position caps are allowed, and portfolio-composition state was only a proposed extension in the prior review. Whether an effective portfolio-risk mechanism exists must be checked.

### 7.4 Lifecycle and universe-size effects can distort defense

The mechanisms described above can cause:

- Lower average exposure but occasional concentrated risk bursts.
- Defensive targets that are not executed.
- Different exposure on 37 stocks despite identical market inputs.
- Persistent incumbents after the original opportunity disappears.

Average SAFE is not a measure of protection at the moments that matter.

For example, Fold 1’s 99.13% average SAFE still accompanies a 24.81% drawdown. Over roughly 5,000 sessions, the remaining average gross corresponds to about **44 fully invested days’ equivalent**. A severe loss can occur in that small amount of risk-taking.

This is not mathematically impossible. It is an urgent request for a date-level ledger.

### 7.5 Daily bars cannot eliminate surprise risk

Close-to-next-open implementation cannot escape an adverse overnight event using information first revealed during that event.

An unlevered, potentially concentrated equity portfolio without options cannot promise very small drawdowns while consistently retaining upside participation. SAFE helps only when the decision to use it is timely.

### The key interpretation

**Poor cross-stock crash transport on the same historical crashes is more concerning than merely failing to predict a novel crash type.**

But it still does not isolate market-state failure. The decisive distinction is:

- Did both universes receive similar defensive targets, but different holdings lost different amounts?
- Did targets differ because of stock/peer/cardinality effects?
- Did defensive targets exist but the lifecycle refuse to execute them?
- Did neither portfolio actually de-risk, with low training MDD arising from fortunate holdings?

Those are different problems requiring different remedies.

---

## 8. Zero realized shorting

**Zero shorting is not, by itself, an implementation defect or an evolutionary failure.**

Under gross ≤ 1:

- Shorting consumes capital that could fund a long or SAFE.
- A 50/50 long-short portfolio has only half its equity in each leg.
- Borrow and dividend obligations reduce expected return.
- The long-run equity premium favors the long side.
- SAFE can be a cheaper defensive alternative than a noisy short forecast.

The prior short-value formula is also conservative. If \(E=\mu-r_s\), short collateral earns no SAFE yield, and there is no rebate, then short excess value relative to SAFE is:

\[
-\mu-b-r_s=-E-2r_s-b.
\]

That expression is internally consistent with the stated convention; the second SAFE term is not automatically a bug.

Nevertheless, **capability must be demonstrated behaviorally, not inferred from a Boolean gene.**

Audit:

1. Did short-only and both-sided genomes receive meaningful search exposure?
2. Did the opportunity map produce sufficiently negative values?
3. Did short candidates ever beat SAFE before friction?
4. Did they qualify but fail lifecycle hurdles?
5. Did initialization, mutation, or niche selection remove shorts prematurely?
6. Does a planted negative-return opportunity generate correct short positions and P&L?
7. Are borrow, dividends, collateral, and bankruptcy handled correctly?

The conclusion could be “shorting was rationally unused.” It could also be “shorting was technically reachable but economically unreachable under the score scale.” Current evidence does not distinguish them.

---

## 9. Does the implementation faithfully test the intended architecture?

**The packet is insufficient to certify that.**

There is evidence that several intended mechanisms exist. There is not enough evidence that they have the intended economic semantics.

### Required conformance audit

| Area | Required verification | Why it matters |
|---|---|---|
| Train/blind parity | Same genome, universe, dates, and costs produce identical results through both paths | Rules out engine, state, or metric divergence |
| Lifecycle | Targets, attempted moves, hurdle components, accepted/rejected trades | Tests the uncertainty cancellation and sticky-exit mechanisms |
| Opportunity units | Raw scores, mapped returns, uncertainty, downside, q, tau, kappa | “Economic opportunity” may otherwise be only a label |
| Market influence | Perturb actual finalists’ market inputs and trace resulting executed exposure | Existence of a market-sensitive fixture does not prove finalists use that path |
| Aggregation | Check whether common applicability multipliers cancel in weighted means | A market gate can be present yet economically inert |
| Allocation saturation | Measure when total claims exceed one and common scaling disappears | Tau or market-driven strength changes can cancel after normalization |
| Universe dependence | 80-to-37 qualification, gross, concentration, peer/calibration changes | Separates transport from cardinality effects |
| Data and execution | PIT universe, delistings, adjustments, publication lags, open/close alignment | Determines whether reported profitability is real |
| Caching/state | Cache keys include universe, data, costs, engine version, and relevant state | Prevents stale or cross-fold fitness reuse |
| Finalist selection | Reproduce training-only choices, deduplication, and band mapping | Explains, among other things, Fold 1’s two finalists |
| Bounds/search | Actual mutation reachability, evaluations, diversity, saturation history | Distinguishes insufficient search from constrained representation |
| Governance | Approved requirement-to-code manifest and preflight results | Hashes identify artifacts; they do not certify scientific conformance |

### 9.1 Market information can still cancel without the old rank bug

Suppose:

\[
O_i=
\frac{\sum_k a_{ik}w_kz_{ik}}
{\sum_k a_{ik}w_k}
\]

and a market gate multiplies all applicability terms by the same positive \(h_t\). That multiplier cancels.

Similarly, when claims are normalized to full gross, a common positive multiplier can disappear from final weights.

Therefore:

> “Market features are present in gates” is not proof that they govern exposure or defense.

This must be tested on the actual finalists.

### 9.2 The null calibration is inadequate for the claims being considered

The report provides:

- One shift length.
- A “small calibration.”
- Null best CAGR of 13.54%.
- Null equal-weight CAGR of 14.86%.
- No matched null frontier, uncertainty distribution, or full-search multiplicity adjustment.

This is a useful smoke test. It is **not a sufficient chance benchmark for a large adaptive search**.

The original review requested a full, matched-pipeline null experiment. The reported small calibration is a departure from that intended evidentiary standard, although the controlling freeze does not specify enough detail to establish an approval violation.

Audit:

- How was predictability destroyed?
- Was the market path preserved?
- Were features recomputed?
- Was serial dependence retained?
- Were multiple shifts/seeds tested?
- Was exposure comparable?
- Was search budget comparable?
- Were null finalists evaluated under the same selection procedure?

The null’s double-digit CAGR illustrates why absolute return is not itself evidence of skill. It does not establish that real MTS performance is—or is not—above chance.

The 4/4 planted recovery result shows that the machinery can recover that planted case. It does not prove adequate power for weak, noisy, costly real-world signals.

### 9.3 Non-monotonic cost sensitivity requires a corrected test

The prior review was too broad in demanding monotonic returns with increasing costs.

There are two distinct experiments:

1. **Frozen decisions and turnover; change only charged costs.**  
   Terminal net wealth must not improve under a standard nonnegative cost model.

2. **Re-run a cost-aware policy using higher costs in its decisions.**  
   Performance can improve because the strategy trades less or avoids bad switches.

With high kappa, the second effect could be substantial.

Report both. A policy-response sensitivity is not the same as friction applied to identical trades.

### 9.4 Bound changes are not automatically unauthorized

The supplied observations identify gamma 6 and kappa 20 as allowed bounds. I accept that as the operative report.

The earlier review proposed a different gamma range and a saturation-monitor procedure. That discrepancy calls for the approved bound registry and archive history—not an unsupported accusation of noncompliance.

Finalist saturation alone does not prove that the prior monitor’s duration and archive-percentage conditions were met.

---

## 10. Reassessment of the prior recommendations

### Recommendations that remain sound

- Repairing rank cancellation.
- Providing a non-cancelled market-to-exposure path.
- Making SAFE operationally reachable.
- Using point-in-time information and taxonomy.
- Allowing dynamic peers without predictive ticker labels.
- Freezing all finalists before blind replay.
- Treating crash evidence by episode, not by stock fold.
- Using actual SPY.
- Requiring execution and cost realism.
- Separating diagnosis from unapproved fitness thresholds.

These were necessary scientific improvements.

### Recommendations I would reverse or substantially revise

**1. The lifecycle equations.**  
The duplicated uncertainty treatment and target-versus-execution inconsistency should not survive merely because they were previously recommended.

**2. Confidence in the economic meaning of the opportunity map.**  
An evolved affine transformation does not become a calibrated expected return simply because it is named one.

**3. Ignoring allocation portability across universe sizes.**  
The 80/37 design and absolute claim-summing allocation interact materially. This should have been analyzed before launch.

**4. Complexity before baseline economics.**  
A large grammar, many modules, contextual units, and elaborate evolution create enormous adaptive capacity. They do not create information. A stronger design would establish simple baselines, signal calibration, and portfolio semantics before expanding the hypothesis space.

**5. Treating individual downside weighting as sufficient portfolio defense.**  
It is not a substitute for common-risk and concentration analysis.

**6. The overly broad cost-monotonicity preflight.**  
It should distinguish fixed-trade accounting from endogenous policy response.

**7. Overconfidence in numerical robustness guards.**  
The proposed thresholds were not uniquely derived from first principles. They were policy choices requiring empirical justification and owner approval.

Their absence is **not an implementation defect**: the controlling freeze explicitly prohibited unapproved numeric guards.

**8. Implicitly expecting robust risk from CAGR/MDD optimization on one historical path.**  
The objective remained vulnerable to exactly the path-specific risk fitting now observed. Diagnostics reveal that vulnerability; they do not remove it from evolutionary incentives.

**9. Treating permutation invariance as enough protection against identity-like overfit.**  
An anonymous stock can still be identified by a distinctive historical state. A GA can fit a first-day feature fingerprint to a future winner without ever reading a ticker string.

The prior review was right that the reduced runner could not test the intended architecture. It would have been wrong to infer that restoring the architecture would, by itself, create exceptional alpha or portable crash protection.

---

## 11. Is the OmniFunds magnitude plausible under these constraints?

### 11.1 The claims are not one consistent compounded target

If 10–11% means steady geometric monthly returns:

\[
1.10^{12}-1\approx214\%,
\]

\[
1.11^{12}-1\approx250\%.
\]

A 96% annual compounded return corresponds to roughly **5.77% monthly**, not 10–11%.

Different windows, arithmetic averages, or reporting conventions could explain the difference. The claims need verified definitions before they are used as a research target.

### 11.2 What 96% annually requires

The constant-equivalent daily compounded return is:

\[
1.96^{1/252}-1\approx0.2674\%,
\]

or about **26.7 bps per trading day net on total equity**.

For 16% CAGR, the corresponding figure is approximately **5.9 bps**.

The gap is roughly **20.8 bps of daily log growth**.

That is an enormous persistent advantage in liquid equities without leverage.

At 96% annually, twenty-year wealth grows by approximately:

\[
1.96^{20}\approx700{,}000.
\]

This does not prove impossibility, especially at small initial capital and changing capacity. It illustrates how extraordinary a durable, scalable claim would be.

### 11.3 No mathematical prohibition—but no demonstrated path

Unlevered equities can double in a year. Concentrated portfolios can produce spectacular short windows. An ex-post oracle selecting daily winners could produce immense returns.

None of those establishes that a causal system can repeatedly identify those opportunities while controlling losses.

Under the present constraints:

- High concentration increases upside and gap risk.
- Long-short portfolios sacrifice some long exposure because gross is capped.
- SAFE reduces losses only when used at the right times.
- No options means no explicit convex crash insurance.
- Daily bars limit response to surprise events.
- Common price-derived information is heavily competed over.

**A durable 96% return with modest drawdowns is not a credible base-case research expectation for this MTS configuration. Ten–eleven percent compounded monthly is less credible still.**

The commercial comparison should require audited daily NAV, live-versus-backtest separation, capital and leverage definitions, PIT universes, realistic fills, and full drawdown history.

Conversely, **a genuinely transferable 15–18% net unlevered return could be commercially valuable.** The problem is that DEV117 has not yet established that claim, and several associated drawdowns are plainly unattractive.

---

## 12. Highest-information analyses available now—without another GA

These analyses should use consumed DEV117 data and frozen artifacts only. They should not be used to retroactively designate a new “blind winner.”

### Priority 1: Reconstruct the extreme failures

Start with:

- Fold 1: 24.93% / −7.93% training → 1.20% / −24.81% blind.
- Fold 3’s near-cash finalist.
- Fold 0’s roughly 20%-training-DD finalist → −46.47% blind MDD.

Produce daily:

- Holdings and actual gross.
- Target gross.
- Raw and mapped opportunities.
- Uncertainty/downside values.
- Entry/exit/replacement attempts.
- Rejected moves and their hurdle components.
- Turnover and costs.
- Stock and episode P&L contributions.
- Initialization and missing-data state.

**Question answered:** Are these failures due to genuine signal non-transfer, portfolio mechanics, a lifecycle trap, or a software/data defect?

### Priority 2: Separate stock transport from cardinality

Run frozen-genome 37-of-80 replays, as described above.

Also inspect qualification rates and score distributions by universe size.

**Question answered:** How much of the blind change is explained by changing the number and statistical context of available stocks?

### Priority 3: Perform exact return attribution

For all finalists—not just representatives—construct:

- Same-daily-exposure SPY/SAFE.
- Same-daily-exposure eligible-universe benchmarks.
- Constant-exposure counterparts.
- Appropriate style comparisons.
- Cost-separated returns.

Examine overnight versus intraday contributions where the existing data support it.

**Question answered:** Is the residual primarily security selection, market timing, style loading, universe selection, or trading-cost behavior?

### Priority 4: Measure economic diversity

Cluster finalists by:

- Return paths.
- Exposure paths.
- Holdings.
- Factor exposures.
- Stock/episode contributions.
- Trade timing.

Use a common consumed universe as an exploratory replay where appropriate.

**Question answered:** Did the GA discover genuinely different economic policies, or different descriptions of the same trade?

### Priority 5: Audit lifecycle and parameter response

For frozen genomes, inspect local response to changes in:

- Gamma.
- Kappa.
- Opportunity scale.
- Qualification margin.
- Downside floors.
- Market-state inputs.

Distinguish target changes from executed changes.

Remain within approved ranges for ordinary diagnostics; testing expanded hypothesis-space bounds should be explicitly authorized.

**Question answered:** Are boundary values robust preferences, scale compensators, or artifacts of a discontinuous/sticky engine?

### Priority 6: Build the complete episode ledger

For each predefined decline and recovery:

- Exposure entering the decline.
- Exposure changes before and after losses.
- Target-versus-executed exposure.
- Stock-selection losses.
- Market/factor losses.
- Exit delay.
- Recovery participation.
- Worst gap/day.
- Concentration and common-risk estimates.

Count each shared market episode once as market-timing evidence.

**Question answered:** What actually failed when risk failed?

### Priority 7: Test concentration and initialization dependence

Without retraining:

- Start-date offsets.
- Removal of major contributing stocks.
- Stock-subset perturbations.
- Modest feature/window perturbations.
- Alternative valid initial states.

These are stress diagnostics, not unbiased new performance estimates.

**Question answered:** Is the strategy an ongoing transferable decision process, or largely a path-dependent selection of historical winners?

### Priority 8: Audit the saved search

Inspect:

- Unique economic behaviors evaluated.
- Mutation and crossover reachability.
- Short-policy participation.
- Complexity growth.
- Saturation frequency over generations.
- Training hypervolume progress.
- Duplicate and cache behavior.
- Seed and island dependence.
- Candidate-selection reproducibility.

**Question answered:** Is “the GA searched enough” supported, or merely assumed?

### Statistical caution

Uncertainty estimation must preserve shared dates, cross-stock dependence, and common crash episodes.

A bootstrap of existing paths cannot manufacture independent crashes. Post-selection permutation exercises on frozen finalists are useful diagnostics but do not substitute for a matched full-search null calibration.

---

## 13. Highest-information next actions after the audit

### Branch A: Material simulator or semantic defect

Repair it under an approved new version.

Replay old frozen genomes through both engines to quantify the defect before evolving replacements.

Do not describe corrected replays on consumed DEV117 as fresh blind validation.

### Branch B: Material 80-to-37 allocation/context shift

Redesign for explicitly defined universe portability.

This may mean separating:

- Total risky capital.
- Relative security allocation.
- Opportunity breadth.
- Estimation reliability.

Do not blindly divide claims by stock count. More real opportunities can justify more exposure; duplicated or mechanically rescaled opportunities should not.

Any change to the approved allocation semantics requires approval.

### Branch C: Genuine stock-selection residual, but poor defense

Treat MTS primarily as a stock-selection engine.

Compare its portfolio layer with simple, transparent, predeclared risk-construction alternatives. Consider portfolio common-risk information and more coherent transaction-cost control.

A separate risk overlay, caps, hard gates, or changed objectives would be scientific changes—not silent engineering fixes.

This branch may produce a useful system without producing anything close to the commercial claim.

### Branch D: Returns largely explained by passive/style exposure

Do not respond with a larger grammar and more generations.

Compare against cheap, transparent baselines. Continue only with a specific hypothesis about additional information or implementation advantage.

New PIT fundamentals, earnings information, revisions, flow data, or other economically motivated inputs could be considered. More data is not automatically better; each addition needs a reason it could improve conditional forecasts beyond existing exposures.

### Branch E: Search demonstrably underpowered

Then run a bounded, budget-matched comparison among:

- The GA.
- Random search.
- Simpler regularized models.
- Structured strategy templates.

Use matched execution, information, selection rules, and meaningful null/planted cases.

The question should be whether the GA adds value—not whether it can eventually find an attractive backtest.

---

## 14. Validation and protected evidence

### My recommendation: do not open protected evidence now

Not because opening is intellectually prohibited, but because the highest-priority uncertainties are answerable on consumed artifacts:

- Accounting.
- Lifecycle semantics.
- Universe cardinality.
- Exposure attribution.
- Concentration.
- Search behavior.

Opening another stock set would not resolve those mechanisms efficiently.

### When opening would become scientifically justified

After:

1. A deployable procedure is frozen.
2. Implementation is independently reproduced.
3. Its intended universe size and online calibration are specified.
4. Primary comparisons and decision criteria are approved in advance.
5. There is a consequential question about fresh-stock transfer that consumed DEV117 cannot answer.

A protected stock set could then answer:

> Does the fully specified procedure retain its residual stock-selection value on securities not already consumed by the research process?

Consumed DEV117 cannot provide that clean confirmation because its results now inform diagnosis and redesign.

But a protected stock set sharing the same historical market path still cannot provide independent crash-timing validation. It must not be marketed as doing so.

Use the smallest appropriate approved test, not all protected sets at once, and do not redesign repeatedly against its outcomes.

### Temporal evidence

Consumed historical walk-forward studies can diagnose sequence dependence and training optimism. They are not pristine after the architecture has been developed with knowledge of those periods.

Any historical temporal redesign must also respect the approved requirement not to turn an entirely withheld crash archetype into the sole zero-shot test.

The strongest next timing evidence is prospective. A frozen shadow implementation can begin accumulating it, although a short live period cannot validate rare-crash behavior or extraordinary annual returns.

---

## 15. Final classification and project decision

### Supported findings

- Operational SAFE use and structural genome diversity improved.
- Every reported finalist lost CAGR from training to blind.
- Most experienced worse drawdowns.
- Gross exposure is strongly associated with blind returns.
- No finalist realized shorts.
- Representative gamma/kappa values frequently hit bounds.
- Cross-stock folds do not provide independent market-timing experiments.
- The favorable return subset has not demonstrated portable low drawdowns.

### Leading hypotheses

- Common equity/style exposure explains a material part of returns.
- Some security-selection value may remain.
- Single-path optimization produced substantial training optimism.
- Cardinality/context shifts damaged transport.
- Concentration and lifecycle hysteresis damaged risk behavior.
- The present information set may not support the owner’s desired magnitude.

### Audits required before stronger conclusions

- Daily attribution and exact benchmarks.
- Train/blind engine parity.
- Lifecycle algebra in actual code.
- Opportunity and cost units.
- Cardinality effects.
- PIT universe and execution integrity.
- Full null/search documentation.
- Actual market-feature influence.

### Scientific changes requiring owner approval

- Lifecycle redesign.
- Allocation normalization or portfolio-risk changes.
- New fitness objectives or robustness constraints.
- Bound expansion.
- New data or instruments.
- Changed validation partitions.
- Another evolutionary experiment.
- Opening protected evidence.

## Bottom line

**The results justify a bounded forensic investigation, not another open-ended search for a marketing-level return target.**

MTS as a cost-aware systematic stock-selection research platform remains plausible. MTS as an expected route to durable 96–250% annualized returns, with modest drawdowns and no leverage or options, is not supported by this experiment.

If that extraordinary magnitude is the owner’s minimum acceptable outcome, **the present project direction should stop or change radically**.

If the owner would value a simpler, verifiably transferable system with materially smaller returns, the result may be stronger than the disappointment suggests—but only if attribution and implementation audits survive.

The most valuable next discovery is not another genome. It is understanding exactly why a policy showing **24.9% CAGR and 7.9% MDD in training became a nearly all-SAFE policy with 1.2% CAGR and 24.8% MDD on blind stocks**. Until that is explained, neither optimism about the architecture nor pessimism about the information set is well identified.