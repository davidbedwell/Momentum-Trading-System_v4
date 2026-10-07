# Independent Methodological Review

## Executive Summary

The project's core idea—requiring that evolutionary search on real data be distinguishable from matched null controls before proceeding—is scientifically sound and unusually disciplined for financial research. However, the current null battery has one fatally flawed arm (N2), one arm with a subtle but repairable confound (N1), and one reasonably well-constructed arm (N3). The real-vs-null comparison framework also lacks formal statistical testing, has multiplicity issues, and relies on a pilot sample too small (8 stocks) to support confident conclusions. None of these are reasons to abandon the framework; most are repairable. Below I work through each question from first principles.

---

## 1. Is N2 a Scientifically Valid Null?

**No. N2 is fatally flawed as constructed and should be removed from the gate battery.**

### The core problem

A valid null for testing "does the search find genuine stock-specific feature→future structure?" must break the feature→outcome link *while preserving the marginal difficulty of the optimization problem for each stock*. N2 violates this by homogenizing stock-specific marginal distributions.

Specifically, N2 performs a cross-sectional permutation that:

- **Preserves:** pooled outcome distribution, each date's cross-sectional multiset of outcomes
- **Destroys (intended):** stock-specific feature→outcome association
- **Destroys (unintended, fatal):** stock-specific marginal outcome distributions—both drift and volatility

The autopsy data make this concrete. NVDA's forward-path std collapses from 0.0316 to 0.0195 (a 38% reduction), while JNJ's inflates from 0.0119 to 0.0192 (a 62% increase). Stock-specific mean forward returns are similarly homogenized.

### Why this makes N2 an *easier* placebo, not a harder one

An evolutionary search optimizing for net return on a per-stock basis will find it easier to identify high-return episodes when:

1. **Volatility is compressed for high-vol stocks:** NVDA under N2 has lower outcome variance, meaning the search can more easily find feature combinations that select above-average-return subsets (the signal-to-noise ratio of any spurious pattern improves when noise drops by 38%).

2. **Drift is redistributed to low-drift stocks:** JNJ and WMT, which have low real drift, receive outcome paths from higher-drift stocks. The search can now "discover" specialists for these stocks that appear to capture positive returns that never existed in the real JNJ/WMT series.

3. **The search has 8 stocks × generations of opportunities to exploit these artifacts.** Even a modest per-stock bias compounds across the portfolio of discovered specialists.

This explains the observed result: N2 beats real in 5/6 generations with widening advantage. The search is genuinely finding structure—but it is *artifactual* structure created by the distribution mismatch, not evidence that real data lack genuine signal.

### Verdict

N2's superiority over real data is **not evidence against the system**; it is evidence that N2 is a broken null. It should be **discarded entirely** from the gate criterion. Any gate logic that required real to beat N2 would be an unfairly conservative test; any logic that interpreted N2's superiority as a red flag would be drawing the wrong conclusion.

---

## 2. Recommended Null Constructions

I recommend a battery of three nulls, each targeting a different threat to validity. For each I state the invariant preserved, the relationship destroyed, and the construction.

### N-A: Within-Stock Stationary Block Bootstrap (replaces N1)

**Threat addressed:** The search finds genuine feature→outcome temporal associations (the primary hypothesis).

**Invariants preserved:**
- Each stock's marginal outcome distribution (mean, variance, all moments)
- Local autocorrelation structure of outcomes (approximately, via block structure)
- Each stock's feature distribution (untouched)
- Cross-sectional structure of features on each date (untouched)

**Relationship destroyed:** The contemporaneous mapping from feature vector to forward outcome path within each stock.

**Construction:**
For each stock independently:
1. Choose block length $b$ via a principled rule (e.g., Politis–Romano optimal block length estimator applied to the forward-path mean-return series; or conservatively, $b = \lceil \sqrt{T} \rceil \approx 50$ for $T = 2500$).
2. Partition the $T$ outcome paths into $\lceil T/b \rceil$ contiguous blocks.
3. Draw $\lceil T/b \rceil$ blocks with replacement from the stock's own blocks; concatenate and trim to length $T$.
4. Assign the resampled outcome paths to the original date indices (so date $t$'s feature vector is now paired with a randomly drawn outcome path from the same stock).

**Why this is better than N1 as described:** The current N1 "permutes outcome paths in temporal blocks" but the description is ambiguous about whether blocks are permuted (shuffled in order) or bootstrap-resampled. Permuting blocks preserves the marginal distribution exactly but may leave residual local associations at block boundaries. Bootstrap resampling is cleaner and has well-understood theoretical properties. Either way, the key improvement over N2 is that each stock retains its own marginal distribution.

### N-B: Within-Stock Guarded Circular Shift (≈ current N3, with tightened specification)

**Threat addressed:** Same as N-A, but with a different destruction mechanism to provide robustness.

**Invariants preserved:**
- Each stock's marginal outcome distribution (exactly, since it's a permutation)
- Each stock's outcome autocorrelation structure (exactly, since it's a circular shift)
- Feature distributions (untouched)

**Relationship destroyed:** Contemporaneous feature→outcome association.

**Construction:**
For each stock independently:
1. Let $T = 2500$. Choose shift $\delta$ uniformly from $[\lfloor T/4 \rfloor, \lfloor 3T/4 \rfloor] = [625, 1875]$.
2. Circularly shift the outcome path series by $\delta$: date $t$ receives the outcome path originally at date $(t + \delta) \mod T$.

**Guard specification:** The guard band $[T/4, 3T/4]$ ensures the shift is large enough that no date's features are paired with an outcome from within ±625 sessions of its true outcome. This is important because features may have slow-moving components (e.g., earnings-based features that change quarterly).

**Why retain this alongside N-A:** N-A and N-B destroy the feature→outcome link by different mechanisms. If the search beats both, the evidence is stronger. If it beats one but not the other, the discrepancy is diagnostic (e.g., if it beats N-A but not N-B, the search may be exploiting autocorrelation structure that N-B preserves but N-A disrupts).

### N-C: Within-Stock Feature Permutation (new, recommended addition)

**Threat addressed:** The search exploits structure in the *outcome* series alone (e.g., momentum, mean-reversion) without using features, or the features are merely proxies for time/trend.

**Invariants preserved:**
- Each stock's marginal outcome distribution (exactly, untouched)
- Each stock's outcome autocorrelation structure (exactly, untouched)
- Each stock's marginal feature distributions (exactly, since features are permuted)

**Relationship destroyed:** The contemporaneous mapping from feature vector to forward outcome path, but now by shuffling features rather than outcomes.

**Construction:**
For each stock independently:
1. Randomly permute the row indices of the feature matrix $X_{\text{stock}}$.
2. Pair the permuted feature rows with the original (unpermuted) outcome paths.

**Why this is valuable:** This null is the *complement* of N-A/N-B. In N-A/N-B, outcomes are shuffled and features are fixed; in N-C, features are shuffled and outcomes are fixed. If the search beats N-A/N-B but not N-C, it suggests the search is finding structure in the outcome series that happens to correlate with feature order (a calendar effect), not genuine feature→outcome causation. If it beats all three, the evidence for genuine feature-conditional structure is much stronger.

**Important caveat:** Simple row permutation of features destroys any temporal autocorrelation in features. If the specialist discovery mechanism uses feature *dynamics* (e.g., "feature X crossed above threshold Y within the last 5 sessions"), this null may be too destructive and create an artificially easy placebo. In that case, apply the same block-bootstrap or circular-shift mechanism to features instead of simple permutation.

### What about a repaired N2?

A cross-sectional null could in principle be repaired by stratifying: permute outcomes only among stocks with similar marginal distributions. But with 8 stocks, the strata would be tiny (perhaps 2–3 stocks per stratum), making the permutation nearly trivial. I do not recommend pursuing a cross-sectional null with this pilot panel. It becomes viable with ≥50 stocks where meaningful strata can be formed.

---

## 3. Gate Logic: Must Real Beat Every Null?

**No. Requiring real to beat every null is neither necessary nor sufficient. The correct gate is a formal hypothesis test with a pre-specified decision rule.**

### Recommended gate logic

**Primary gate (must pass):**

For each valid null $k \in \{A, B, C\}$, test:

$$H_0^{(k)}: \text{The search on real data produces the same or worse fitness distribution as the search on null } k$$

using a one-sided test. The gate passes if real significantly outperforms *at least two of three* nulls at a Bonferroni-corrected significance level (see §5 for details).

**Rationale for "at least two of three" rather than "all three":**

- Each null preserves different invariants and destroys different relationships. A null that preserves outcome autocorrelation (N-B) may be harder to beat than one that disrupts it (N-A), not because the system lacks genuine signal, but because the null retains more exploitable structure.
- Requiring all three creates an excessively conservative gate that penalizes the system for the *strongest* null being hard to beat, even if the other two provide clear evidence of genuine signal.
- However, if real fails to beat *any* null, the system should not proceed. If real beats exactly one of three, the evidence is ambiguous and the system should not proceed without investigation.

**Secondary diagnostic (informational, not gating):**

For any null that real fails to beat, investigate *why*. The pattern of which nulls are beaten and which are not is diagnostic:

| Pattern | Interpretation |
|---------|---------------|
| Beats A, B, C | Strong evidence of genuine feature→outcome structure |
| Beats A, B; not C | Search may exploit outcome-series structure (momentum/mean-reversion) rather than features |
| Beats A, C; not B | Search may exploit autocorrelation that circular shift preserves |
| Beats B, C; not A | Unusual; investigate block-bootstrap implementation |
| Beats only one | Insufficient evidence; do not proceed |
| Beats none | No evidence of genuine structure; do not proceed |

---

## 4. Avoiding Null-Tuning with 8 Stocks

This is a serious concern. With only 8 stocks, there are many researcher degrees of freedom in null construction, and the temptation to adjust null parameters until real wins is acute.

### Pre-registration protocol

Before any further runs, **freeze and document in writing:**

1. **Null constructions:** Exact algorithms, including all parameters (block length formula, shift guard bounds, random seeds or seed-generation protocol).

2. **Fitness metric:** Which metric(s) from the evaluation suite (net return, MFE, MAE, etc.) constitute the primary comparison. I recommend **one** primary metric for the gate (median final-generation mean net return is reasonable) and the others as secondary diagnostics.

3. **Test statistic and decision rule:** Exact specification of the statistical test (see §5), significance level, and multiplicity correction.

4. **Number of independent runs per arm:** To generate a distribution of outcomes for the statistical test.

5. **Stopping rule:** How many pilot stocks will be tested before the gate decision. If you plan to expand from 8 to more stocks, specify this now.

### Calibration diagnostics to freeze

Before running the gate comparison, verify and document:

- **Marginal distribution preservation:** For each null, compare the per-stock mean, std, skewness, kurtosis, and quantiles (1%, 5%, 25%, 50%, 75%, 95%, 99%) of forward-path returns before and after null transformation. Require that these match within sampling noise (formal test: two-sample KS test, $p > 0.10$).

- **Autocorrelation preservation:** For N-B (circular shift) and N-C (feature permutation), verify that the autocorrelation function of the outcome series is preserved. For N-A (block bootstrap), document the expected autocorrelation disruption.

- **Feature distribution preservation:** For N-A and N-B (which don't touch features), verify features are identical. For N-C, verify marginal feature distributions are preserved.

- **Search budget equality:** Verify that all arms receive exactly the same number of evaluations, generations, population size, and that the search machinery (selection, crossover, mutation operators) is identical.

### What 8 stocks cannot tell you

With 8 stocks, you have 8 partially correlated "experiments." This is not enough to:
- Estimate the false-positive rate of the gate
- Distinguish stock-specific signal from market-wide signal
- Assess whether the system works on stocks outside the pilot set

The pilot can only tell you whether the machinery *appears* to find something distinguishable from null. The real validation requires a larger universe (see §7).

---

## 5. Effective Sample Size and Multiplicity

### Effective sample size

**Within a single arm-run:**
- 2,500 dates × 8 stocks = 20,000 date-stock observations, but:
- Forward paths span 10 sessions, creating overlap. With 2,500 dates and 10-session paths, consecutive paths overlap by 9 sessions. Effective independent outcome observations per stock ≈ $2500/10 = 250$, not 2,500.
- Cross-stock correlation further reduces effective $N$. If average pairwise correlation of 10-session returns is $\bar{\rho} \approx 0.3$ (typical for a mixed US large-cap panel), the effective number of independent cross-sectional units per date is approximately $8 / (1 + 7\bar{\rho}) \approx 8/3.1 \approx 2.6$.
- **Effective independent observations per arm-run: approximately $250 \times 2.6 \approx 650$.**

**Across the evolutionary search:**
- The search evaluates 2,304 ticker-evaluations per arm, but these are not independent—they share the same data and the evolutionary process creates dependencies across generations.
- The relevant unit for the real-vs-null comparison is the *run-level summary statistic* (e.g., median final-generation fitness), not individual evaluations.

**For the gate test:**
- With a single run per arm, you have $n = 1$ observation per arm. You cannot do a statistical test.
- **This is a critical gap.** You need multiple independent runs per arm to generate a distribution of outcomes.

### Required replication

To perform a valid test, I recommend:

- **$R \geq 20$ independent runs per arm** (each with a different random seed for the evolutionary search, but the same data and null transformation—or, better, a different null realization per run for the null arms).
- This gives you 20 paired observations (real run $r$ vs. null run $r$, using the same search seed) for a paired test.
- With $R = 20$ and a paired Wilcoxon signed-rank test, you can detect a consistent directional effect at $\alpha = 0.05$ (one-sided) with reasonable power if real beats null in ≥16/20 runs.

### Multiplicity correction

- **Three nulls:** Bonferroni correction: test each at $\alpha/3$. For a family-wise $\alpha = 0.05$, test each null at $\alpha = 0.0167$.
- **Eight stocks (if testing per-stock):** If you also want per-stock conclusions, correct for $8 \times 3 = 24$ tests. But I recommend the primary gate be at the pooled level (across all 8 stocks), with per-stock results as diagnostics.
- **Multiple fitness metrics:** If you test on $m$ metrics, correct for $m$ as well. Better: designate one primary metric and treat others as exploratory.

### The generation-counting problem

The current analysis compares real vs. null across 6 generations ("real beat N1 in 5/6 generations"). This is not a valid statistical test because:
- Generations within a run are not independent (each generation is derived from the previous one).
- 6 generations is far too few for any meaningful test.
- "5/6" is not significant even under independence ($p = 6 \times (1/2)^6 = 0.094$ one-sided binomial, and that's before accounting for dependence).

**This is a repairable flaw but it means the current pilot results are not statistically interpretable.** The observed differences may be real or may be noise.

---

## 6. Deeper Flaws

### Flaw 1 (Serious, Repairable): No formal statistical test exists

The current comparison is purely descriptive: "real beat N1 in 5/6 generations." Without a formal test with pre-specified $\alpha$, effect size, and power calculation, the gate is subjective. This must be fixed before proceeding.

### Flaw 2 (Serious, Repairable): Single-run comparison

A single run per arm conflates search stochasticity with real-vs-null differences. The evolutionary search is stochastic; a different seed could reverse the ordering. Multiple runs are essential.

### Flaw 3 (Moderate, Repairable): Overlapping forward paths inflate apparent sample size

10-session forward paths on consecutive dates share 9/10 of their data. Any test statistic that treats these as independent will have severely anti-conservative $p$-values. The block bootstrap null (N-A) partially addresses this by using blocks, but the *test* of real vs. null must also account for this dependence.

### Flaw 4 (Moderate, Conceptual): The null test validates the *search*, not the *specialists*

Even if real data are distinguishable from nulls under equal search budgets, this does not guarantee that the discovered specialists have genuine predictive power. It means the search finds *something* in real data that it doesn't find in null data. That something could be:
- Genuine feature→outcome structure (desired)
- Exploitable structure in the feature space that correlates with time (calendar effects, survivorship, look-ahead in "point-in-time" earnings data)
- Artifacts of the fitness function (e.g., if net return doesn't adequately penalize for selection bias in entry/exit timing)

**Recommendation:** The null gate is a necessary but not sufficient condition. After passing the gate, discovered specialists must undergo out-of-sample validation on held-out time periods and/or held-out stocks.

### Flaw 5 (Minor but worth noting): Pilot stock selection is non-random

AAPL, MSFT, XOM, JPM, JNJ, CAT, WMT, NVDA are all large-cap, liquid, well-covered US stocks with strong long-term positive drift. This is the easiest possible universe for a long-biased system. The null gate should eventually be tested on a more challenging universe (e.g., including stocks with negative drift, small-caps, or international stocks).

### Flaw 6 (Subtle): Evolutionary search may exploit null-specific artifacts

The evolutionary search adapts to whatever structure exists in the data. On null data, it will find the best-available spurious patterns. If a null inadvertently creates exploitable structure (as N2 does by homogenizing volatility), the search will find it. This means the real-vs-null comparison is not just about whether real data have signal; it's about the *relative* amount of exploitable structure. A null that is "too clean" (destroying all structure) may be too easy to beat; a null that preserves too much structure may be too hard to beat. The recommended battery of three nulls with different preservation properties mitigates this, but it's an inherent limitation of the approach.

### Flaw 7 (Potentially Serious): Earnings feature point-in-time integrity

The description mentions "point-in-time earnings features." If these are not rigorously point-in-time (i.e., if there is any look-ahead in the earnings data), the system will find genuine-looking but artifactual signal that null tests cannot detect (because the nulls break the feature→outcome link, and the look-ahead signal *is* a genuine feature→outcome link—just one that wouldn't exist in live trading). This is outside the scope of the null-testing framework but is a common and devastating source of false signal in financial research.

---

## 7. Concrete Next-Step Protocol

### Phase 0: Pre-registration (before any further computation)

**0.1** Write a pre-registration document specifying:
- Primary fitness metric for the gate (recommend: median final-generation mean net return)
- Three null constructions (N-A, N-B, N-C as specified in §2) with all parameters frozen
- Number of independent runs per arm: $R = 25$ (provides reasonable power)
- Statistical test: paired Wilcoxon signed-rank test, one-sided, for each null
- Significance level: $\alpha = 0.05$ family-wise, Bonferroni-corrected to $\alpha_{\text{per-null}} = 0.0167$
- Gate rule: real must significantly outperform at least 2 of 3 nulls
- Stopping rule: no peeking; all 25 runs complete before analysis

**0.2** Have the pre-registration reviewed by someone not on the project team (or at minimum, commit it to version control with a timestamp before running).

### Phase 1: Null Calibration Verification (1–2 days)

**1.1** Implement N-A, N-B, N-C on the existing 8-stock panel.

**1.2** For each null, verify invariant preservation:
- Per-stock marginal distribution: KS test of original vs. null outcome distributions ($p > 0.10$ required)
- For N-B: autocorrelation function of outcome series matches original within sampling noise
- For N-C: marginal feature distributions match original
- For N-A: document expected autocorrelation disruption; verify block length is reasonable

**1.3** Verify that the search machinery treats all arms identically: same population size, generations, evaluation budget, selection/crossover/mutation operators, and that the only difference is the data.

**1.4** Document all calibration results. **Do not adjust null parameters based on real-vs-null comparison results.** If a null fails calibration (e.g., doesn't preserve marginal distributions), fix the implementation bug, don't tune the parameters.

### Phase 2: Pilot Gate Test (3–5 days computation)

**2.1** Run $R = 25$ independent runs for each of the 4 arms (real, N-A, N-B, N-C), using 25 different random seeds for the evolutionary search. For null arms, also use a different null realization per run (different random permutation/shift/bootstrap draw).

**2.2** Total computation: $4 \times 25 = 100$ runs. At 2,304 evaluations per run, this is 230,400 evaluations total. Verify this is computationally feasible.

**2.3** Record the primary metric (median final-generation mean net return) for each run. Also record all secondary metrics for diagnostic purposes.

### Phase 3: Statistical Analysis (1 day)

**3.1** For each null $k$, compute the paired differences $d_r^{(k)} = \text{metric}_{\text{real},r} - \text{metric}_{\text{null}_k,r}$ for $r = 1, \ldots, 25$.

**3.2** Perform paired Wilcoxon signed-rank test (one-sided: $H_1$: real > null) for each null. Report exact $p$-values.

**3.3** Apply Bonferroni correction. Gate passes if at least 2 of 3 nulls are rejected at $\alpha_{\text{per-null}} = 0.0167$.

**3.4** Report effect sizes: median paired difference and its 95% confidence interval (Hodges-Lehmann estimator).

**3.5** Diagnostic analyses:
- Per-stock breakdown: does real beat null consistently across stocks, or is the effect driven by 1–2 stocks?
- Per-generation trajectory: does the real-vs-null gap widen, narrow, or stay constant across generations? (Widening is expected if the search is finding genuine structure; narrowing suggests the null is catching up via overfitting.)
- Secondary metrics: do MFE, MAE, tail loss, duration, etc. show consistent real > null patterns?

### Phase 4: Decision (1 day)

**4.1** If the gate passes (≥2/3 nulls rejected):
- Proceed to expanded discovery on a larger stock universe (≥50 stocks, ideally ≥200)
- The expanded run should include a held-out time period (e.g., train on 2007–2022, validate on 2023–2026) as an additional safeguard
- Re-run the null gate on the expanded universe as a confirmation

**4.2** If the gate fails (≤1/3 nulls rejected):
- Do not proceed to large discovery
- Investigate: is the search budget too small? Are the features too weak? Is the fitness function not discriminating?
- Consider increasing generations/population before concluding the system doesn't work

**4.3** If results are ambiguous (e.g., 2/3 nulls rejected but effect sizes are tiny, or the effect is driven by 1 stock):
- Expand the pilot to 20–30 stocks before making a go/no-go decision
- Do not adjust null constructions or test parameters

### Phase 5: Expanded Validation (if Phase 4.1)

**5.1** On the larger universe, repeat the null gate with the same pre-registered protocol (same null constructions, same test, same $\alpha$).

**5.2** Add an out-of-sample temporal validation: discover specialists on the training period, evaluate them (without re-optimization) on the held-out period.

**5.3** Only after passing both the null gate and out-of-sample validation on the expanded universe should portfolio construction begin.

---

## Summary Classification

| Issue | Classification | Resolution |
|-------|---------------|------------|
| N2 is an invalid null (changes marginal distributions) | **Fatal flaw** | Remove N2; replace with recommended battery |
| No formal statistical test | **Fatal flaw** | Implement pre-registered hypothesis test |
| Single run per arm | **Fatal flaw** | Require ≥25 independent runs per arm |
| Overlapping forward paths inflate effective $N$ | **Repairable flaw** | Use block-aware test statistics; report effective $N$ |
| Generation-level comparison is not a valid test | **Repairable flaw** | Use run-level summary statistics with proper pairing |
| N1 block permutation ambiguously specified | **Repairable flaw** | Replace with well-specified block bootstrap (N-A) |
| Only 8 pilot stocks | **Repairable flaw** | Acknowledge limitation; plan expansion |
| No out-of-sample temporal validation | **Repairable flaw** | Add held-out period in expanded validation |
| Non-random stock selection (large-cap bias) | **Optional improvement** | Expand to more diverse universe |
| Feature permutation null (N-C) not included | **Optional improvement** | Add to distinguish feature signal from outcome-series structure |
| Earnings data point-in-time integrity | **External risk** | Audit independently; outside scope of null framework |

**Bottom line:** The framework is conceptually sound but the current execution has three fatal flaws (invalid N2, no formal test, single run) that must be repaired before any conclusions can be drawn. The observed pilot results—including N2's superiority—are fully explained by methodological artifacts and cannot be interpreted as evidence for or against the system. The path forward is clear and feasible.
