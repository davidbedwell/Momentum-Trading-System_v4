# Stage-2 V3 certification gap audit — 2026-10-07

**Decision: FAIL CLOSED / NOT CERTIFIED.** This is a substantive scientific conformance gap, not a missing checkbox.

## Existing evidence
- 45/45 synthetic calibration cases executed; 671 unique evaluations; ledger structural audit: 0 failures.
- The run uses LONG only, population 8, two generations. This is evidence generation, not sufficient demonstration of full approved search or LONG/SHORT conformance.
- The run ledger records candidate IDs, per-horizon objectives, first fronts, ranks, and parent IDs, but **does not record the actual candidate genomes**. Reconstructing the selected strategies from that ledger for independent replay is impossible without rerunning or independently recovering exact genomes from reproducible source and seed.
- Selection uses the best nondomination rank across 63 horizons. This is explicitly exploratory in stage2_multiobjective_v3.py; it does not establish prespecified stable-horizon selection or selection-adjusted significance.
- The risk policy contains sensitivity grids (ATR20 6/8/10/12 and loss fractions 20/25/30/40%) but no independently verified hard emergency-cap choice. Selecting a cap after seeing outcomes would violate the freeze.
- Contrary to the earlier claim that price data were missing, the aligned raw execution OHLC data **do exist** in cache/dev117_raw_aligned_v3.parquet. The earlier inspection looked only at the predictor parquet. An independent replay is technically possible with this raw source and the cached execution paths, but it has not been performed.

## Required work to earn certification
1. Fix the runner to persist every candidate's full genome and provenance, as well as selected genome IDs, evaluation hashes, and independently reproducible path and cost hashes. Do not rewrite old evidence as though it had these fields.
2. Freeze a selection procedure based on stable opportunity windows rather than best-of-63 horizon; separately evaluate LONG and SHORT; demonstrate search-budget adequacy under the frozen calibration recovery contract.
3. Run an independent selection-adjusted assessment, including matched null controls, familywise multiple-search adjustment, stable-window overlap, and separate validation samples that do not contaminate protected banks. Do not claim independence for reused discovery outcomes.
4. Independently recalculate catastrophic execution using aligned raw OHLC, ATR20, adjusted entry prices, gap-through first available fills, and all frozen sensitivity scenarios; establish and freeze an actual emergency decision policy prospectively before any new selection run.
5. Independently audit all source hashes, frozen dates, selection procedures, risk evidence, and governance partitions. Only then permit PASS and production consideration.

## Cost control
No further large paid GA run should start until items 1–4 have executable tests and preflight checks. The completed 45-case run remains forensic evidence and cannot be retroactively certified by adding declaration fields.
