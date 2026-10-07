# G3 Null-Gate Pre-Registration — Frozen 2026-10-07

Status: **PRE-REGISTERED BEFORE NEW REAL-vs-NULL RESULTS. Production discovery remains unauthorized.**

## Purpose
Test whether the G3 evolutionary search extracts feature-conditional structure from real data beyond matched null processes. Passing this gate authorizes only the next discovery stage; it does not validate individual specialists.

## Frozen pilot scope
- Tickers: AAPL, MSFT, XOM, JPM, JNJ, CAT, WMT, NVDA.
- Panel: last 2,500 dates of the common aligned causal X / complete 10-session forward-path Y panel.
- Search configuration: 6 generations, population 48, identical operators/objectives/costs across arms.
- Primary run-level endpoint: median of candidate mean net return in the final generation.
- Secondary metrics are diagnostic only and cannot rescue a failed primary gate.

## Null battery
**N-A — WITHIN_STOCK_MOVING_BLOCK_BOOTSTRAP_Y**
For each stock independently, resample contiguous Y blocks with replacement and concatenate to T rows. Frozen block length = ceil(sqrt(T)); T=2500 => 50. X is unchanged. This preserves stock identity and approximately preserves local Y dependence while destroying datewise X→Y alignment.

**N-B — WITHIN_STOCK_GUARDED_SHIFT_Y**
For each stock independently, circularly shift the entire Y path series by a draw uniformly from [floor(T/4), floor(3T/4)], inclusive. X is unchanged. This exactly preserves each stock's Y marginal distribution and circular autocorrelation structure while destroying contemporaneous X→Y alignment.

**N-C — WITHIN_STOCK_GUARDED_SHIFT_X**
For each stock independently, circularly shift the entire multivariate X row vector by a draw uniformly from [floor(T/4), floor(3T/4)], inclusive. Y is unchanged. This exactly preserves each feature's marginal distribution, cross-feature row relationships, and circular temporal structure while destroying contemporaneous X→Y alignment. This guarded shift is frozen instead of IID feature-row permutation to avoid creating an artificially easy null by destroying feature dynamics.

The former unrestricted datewise cross-sectional N2 is retired from the 8-stock gate because it changes stock-specific outcome marginals. It remains historical diagnostic evidence only. Stratified cross-sectional nulls may be reconsidered prospectively on a >=50-stock panel, never retrofitted to this gate.

## Calibration before gate
Before any replicated real-vs-null gate:
1. N-B must exactly preserve each stock's Y row multiset; N-C must exactly preserve each stock's X row multiset.
2. N-A must draw only from the same stock and use only complete contiguous source blocks; report per-stock mean/std/quantiles and ACF diagnostics rather than require exact marginal identity because bootstrap resampling is stochastic.
3. All arms must have identical search generations, population, ticker set, row count, evaluation count, operators, objectives, costs, and primary endpoint.
4. No protected validation bank is loaded.
5. Null calibration cannot use whether real wins as a tuning criterion.

## Replication and pairing
- R = 25 independent paired replicates.
- Replicate r uses the same evolutionary search seed in Real, N-A, N-B, and N-C.
- Each null arm receives a distinct deterministic null seed derived from (replicate, null family); null realizations are redrawn across replicates.
- All 100 runs complete before gate analysis. No stopping on favorable/unfavorable interim results.

## Frozen inferential gate
For each null separately, compare the 25 paired run-level primary endpoints (Real_r - Null_r) using a one-sided paired Wilcoxon signed-rank test with alternative Real > Null.
- Family-wise alpha = 0.05.
- Bonferroni per-null alpha = 0.05 / 3 = 0.0166666667.
- PASS requires significant Real > Null for at least 2 of 3 null families.
- 3/3 = strong pass; 2/3 = pass with the failed null investigated and carried forward as a diagnostic risk; <=1/3 = fail/no large discovery.
- Report median paired difference, all 25 paired differences, exact run seeds, and per-stock diagnostics.
- Generation win counts are descriptive only and have no inferential role.

## Anti-tuning / governance
This protocol is frozen before observing any new replicated gate result. Implementation bugs or failed invariants may be repaired, but any scientific parameter change requires a new versioned pre-registration and invalidates results generated under the superseded protocol for gating. Historical pilot results cannot be used to select or tune parameters in this protocol.

## Independent review provenance
The external Claude review was requested cold after the unrestricted N2 anomaly. It independently judged unrestricted N2 invalid, required replicated run-level inference, and recommended complementary within-stock nulls. The final N-C guarded-X shift is a prospective refinement made before new gate results, addressing the review's explicit warning that IID feature permutation can destroy feature dynamics.

## Authorization boundary
Calibration and exact-controller benchmarking are authorized. The 100-run replicated gate may start only after executable invariant tests pass and an exact-controller timing benchmark is recorded. Large G3 discovery remains prohibited until the frozen gate passes.
