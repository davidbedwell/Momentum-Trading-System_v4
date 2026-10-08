# Stage 2 causal and statistical audit — 2026-10-08

Decision: **NOT CERTIFIED.** Read-only audit, no GA or protected bank access.

## Verified
- Active DEV80 predictors: 399,691 rows, 80 securities, 2004-09-01 to 2026-09-14, zero duplicate (security_id,effective_date) keys; 399,691 eligible flags, 11 sector identifiers.
- CausalSignalCompiler quantile thresholds include strictly earlier decision dates, not the current date. The cross-sectional feature builder ranks stocks on the same effective date, using contemporaneous data.
- Outcome path model enters at next session adjusted open and provides 63 daily horizons; cost model distinguishes long and short, including a baseline borrow charge. Both directions were evaluated end-to-end against DEV80 and returned distinct IDs and 63 horizons.

## Certification blockers
1. **Point-in-time membership and survivor selection**: all DEV80 rows are eligible; 80 securities selected from a later universe do not establish contemporaneous S&P membership. Historical universe/sector membership and delisted security coverage require independent source verification.
2. **Adjusted price hindsight**: `stage2_path_v3._adjusted_ohlc` applies `adj_close/close` across OHLC. For outcome calculation this may be valid ex-post, but corporate-action adjustment availability at decision time and alignment with source predictor features are not proven.
3. **Shared-shock uncertainty**: `stage2_evaluator_v3.cluster_ids_from_frame` clusters by security-year. Market-wide common shocks violate independence; reported 95% lower bounds cannot be certified as robust across crash episodes without market-date/episode resampling.
4. **Selection bias and multiple comparisons**: evolutionary search tests many correlated candidates and 63 horizons; nominal confidence bounds are not selection-adjusted. Need frozen validation and nested selection evidence.
5. **Execution realism**: short borrow is fixed 0.3% annual, with no locate availability or recall stress; fixed reference notional and modeled spread/impact may be optimistic in crises. Need sensitivity and eligibility tests.
6. **Optional Stage 1 metadata**: linked and hash-checked but expressly not PIT certified; human labels must remain descriptive only.
7. **Cost-source pre-2005 coverage**: SEC31 schedule begins 2005-12-22; earlier costs become NaN/ineligible. Verify date coverage and ensure this doesn't distort era comparisons.

## Required next actions
- Build deterministic point-in-time membership/source provenance audit and explicit historical coverage report without touching DEV37/DEV50/BLIND17.
- Add market-shock/episode robust uncertainty and multi-testing calibration on DEV80.
- Add short-side borrow/locate stress scenarios and source-adjustment invariance tests.
- Freeze revised scientific policy, source hashes and new run identity before benchmark/production GA.
