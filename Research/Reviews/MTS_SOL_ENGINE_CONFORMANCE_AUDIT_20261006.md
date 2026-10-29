# MTS Sol Engine Conformance Audit — 2026-10-06
Status: IN PROGRESS; findings below are verified against controlling freeze, Claude implementation instruction set, and executed runner.
Scope: consumed DEV117 only. Protected DV25/A25/A75/B100 not opened.

## Verified critical findings
1. FAIL — Lifecycle resize semantics. Executed _lifecycle tests trade as abs(target)-abs(prev)>hurdle. Active target reductions therefore cannot clear a positive hurdle. Full exit occurs only through separate inactive rule. This violates Claude E.4/E.5 partial resize/EXIT semantics and freeze lifecycle intent.
2. FAIL — Fold isolation / blind-derived stock ranks. build_arrays calls v2.make_arrays(dev) on all DEV117. v2.make_arrays computes cross-sectional stock ranks across N=len(dev)=117 before fold subsetting. Training-80 features therefore depend on blind-37 values. Claude D.6 explicitly requires transforms within training80 during evolution and blind37 during replay.
3. FAIL — Fold isolation / blind-derived dynamic peers. dynamic_peer_context(px,dates,dev) is computed on all 117 before fold subsetting. Training stock peer selection and peer aggregates can therefore use blind stocks/prices.
4. FAIL — Blind replay universe semantics. Blind37 replay subsets an X tensor whose cross-sectional ranks and peers were constructed on all117, so blind replay is not a true 37-stock feature reconstruction.
5. FAIL — Mandatory preflight absent. --preflight-only runs build_arrays + calibration and returns. The frozen/Claude PF conformance suite is not implemented in the executed runner; no PF-21 lifecycle test exists.
6. FAIL — Claimed fail-closed behavior is false. Runner docstring says fail-closed implementation, but no requirement-to-code traceability matrix or conformance gate blocks evolution.
7. FAIL — Null calibration not matched pipeline. Actual null uses one circular shift and 24 random genomes on 40 stocks; Claude H.7 required full GA with predictability destroyed and pipeline carried through finalist/blind evaluation.
8. FAIL — Planted power calibration not matched pipeline. Actual planted test selects best of 40 random genomes per seed and calls any positive CAGR recovery; Claude H.7 required GA recovery of the planted conditional structure in >=3/4 seeds.
9. FAIL — GA stage semantics. mutate(...,stage) does not use stage. Stage B/C merely apply an additional generic random mutation; they do not specifically upweight context/applicability or lifecycle/allocation operators as comments claim.
10. FAIL — Novelty/MAP implementation mismatch. Novelty island does not calculate behavioral-distance novelty; MAP archive descriptors are only gross, SAFE, short share, turnover, omitting specified HHI/GFC/recovery descriptors.
11. FAIL — Migration topology mismatch. Code pools migrants from all islands and samples them into every island; this is not the specified ring migration.
12. FAIL — Plateau rule incomplete. First plateau injects immigrants; second consecutive plateau does not freeze the island archive or reallocate compute as specified.
13. FAIL — Economic-cost completeness. Baseline runner models spread and short borrow, but no SEC Section 31, FINRA TAF, or size/ADV impact term is present.
14. WARNING — Market-feature provenance. V2 load_panel constructs market aggregates before filtering to DEV117, from the full eligible predictor table. Exact ticker scope and any overlap with protected sets require provenance audit before certification.
15. INVALIDATED DIAGNOSTIC — Initial 37-of-80 cardinality replay reused the all117 feature tensor; its cardinality estimates are not valid and are withdrawn.

## Consequence
The completed GA run is nonconforming to the intended experiment. Its outputs remain useful as forensic artifacts but cannot establish clean cross-stock blind transport, lifecycle risk performance, or search adequacy of the approved architecture.

## Change control
No repair, retraining, protected-data access, or new scientific threshold has been authorized or executed by this audit.
16. FAIL — Absolute-claim/SAVE allocation semantics. Claude F.2 requires r_i=tau*g_i and scaling only when sum(abs(r_i))>1. Executed lifecycle instead sets scale=tau/sum(abs(raw)) whenever any claim exists, forcing gross to tau. Opportunity magnitude therefore mostly controls relative weights rather than absolute risky capital; weak claims do not naturally leave proportional residual SAFE.
17. FAIL — Protected-data isolation at loader level. v2.load_panel reads the full current-S&P predictor parquet into memory and constructs market aggregates before DEV117 filtering. Protected-cohort predictor rows therefore contribute to imported market features. This contradicts the experiment's sealed/inaccessible representation even though individual protected outcomes were not deliberately inspected.
18. WARNING/FAIL candidate — Point-in-time universe provenance. Market aggregates are formed from a current-S&P calibration store across historical dates. Current membership used backward can create survivorship/future-membership contamination. Exact store construction must be certified before any corrected run.
19. FAIL — Unified move ledger absent. Claude E.4 requires source-to-destination comparisons V_b-V_a, greedy ordering by net gain, and moves bounded toward targets. Executed _lifecycle evaluates each asset independently against its own previous absolute weight; no source/destination value comparison exists.
20. FAIL — REPLACE label semantics. Executed lifecycle increments REPLACE for an active position whose weight changes while remaining nonzero. It does not establish an incumbent-to-challenger transfer or hurdle comparison, so reported REPLACE counts do not represent Claude E.5 REPLACE decisions.
21. FAIL — EXIT hurdle semantics. When prev!=0 and active is false, executed code sets weight directly to zero regardless of the unified source-to-SAFE value-improvement rule. Transaction cost is charged later, but the exit decision itself does not use Claude E.4 source/destination hurdle.
22. FAIL — Preflight PF-21 is non-behavioral. Test passes solely if lifecycle label strings exist in source; it does not execute scripted ENTER/CONTINUE/REPLACE/EXIT/SHORT scenarios required by Claude K.
23. FAIL — Preflight PF-03 misses imported rank construction. It scans only the redesigned runner for np.argsort(np.argsort), while the runner imports v2.make_arrays where that exact cross-sectional ranking occurs.
24. FAIL — Preflight PF-10 misses indirect protected access. It checks only literal protected cohort names in runner path arguments, not transitive file reads or ticker-level access from imported loaders.
25. FAIL — Preflight PF-23 does not verify metric definitions. It only checks that safe_fraction and turnover names occur in source; no hand-computed reference or same-engine path equivalence is tested.
26. FAIL — Preflight integration. The production --preflight-only path does not invoke the pytest conformance suite; it only builds arrays and runs calibration.
27. QUANTIFIED FAIL — Fold0 feature isolation audit. Correctly recomputing cross-sectional stock ranks on training80 changed 5,162,165/5,180,303 finite values (99.650%, mean abs delta .04212, max .24306). Recomputing blind37 changed 2,219,879/2,230,320 (99.532%, mean abs delta .11442, max .66595).
28. QUANTIFIED FAIL — Fold0 peer isolation audit. Recomputing dynamic peers on training80 changed 2,578,675/2,816,240 values (91.564%, mean abs delta .04026, max .84780). Recomputing on blind37 changed 1,193,638/1,302,511 values (91.641%, mean abs delta .07061, max .89823).
29. PASS — Four allocation mode labels are reachable in genome initialization: equal, strength, uncertainty, downside. Their downstream absolute-claim semantics nevertheless fail F.2 as finding 16.
30. PASS — Gross exposure is explicitly renormalized to <=1; no leverage/options or explicit position/sector caps were found in the executed decision path.
31. PASS — Execution-return alignment uses adjusted T+1 open to T+2 open return for a close-T decision, consistent with the intended T+1-open execution convention at daily resolution.
32. PASS WITH LIMITATION — Dynamic peer construction is backward-looking in time through T and its normalization uses prior-history statistics; however its universe isolation fails findings 3/28.
33. PASS — Actual SPY is loaded for final comparator reporting rather than relabeling the DEV equal-weight series. This does not cure exposure attribution or feature contamination.
