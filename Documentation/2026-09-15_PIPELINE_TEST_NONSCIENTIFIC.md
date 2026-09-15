# PIPELINE_TEST_NONSCIENTIFIC — Mac integration acceptance harness

Status: ENGINEERING TEST ONLY. This branch does not alter production feature/Analysis architecture.

## Purpose

Use the recovered TradingView CSV histories as an arbitrary closed test market to answer one engineering question: can MTS construct and interrogate a multi-security market state using production deterministic mathematics while operating within a constrained notebook environment?

The data are not a scientifically authoritative market universe. They could be any multientity time series. Passing this harness grants no hypothesis validation, generalization, or trading-performance credit.

## Hard boundaries

- No Sol calls.
- No Qwen calls.
- No canonical Nexus writes.
- No finding/hypothesis promotion.
- No scientific-memory contribution.
- Dedicated output root must contain `PIPELINE_TEST_NONSCIENTIFIC` and must be outside the repository.
- Outputs are engineering-test artifacts only.
- Recovered data have unverified survivorship, selection, adjustment, and source semantics and are not point-in-time historical market membership.

## Mac scaling policy

The production feature and deterministic Analysis implementations remain unchanged. The harness adapts the workload to the single-core/8-GB Mac by processing bounded security-history batches, persisting per-security Parquet partitions, releasing working memory, and then constructing date-scoped market cross-sections from persisted partitions.

A Mac-only resource limitation is not authorization to redesign production architecture. If the harness exposes a defect that would also affect the intended server workload, stop and document evidence before changing production architecture.

## Source

Default recovered-data location:

`~/Library/Mobile Documents/com~apple~CloudDocs/David/Trading/Momentum-Trading-System-History/01_Raw/`

The adapter uses `time/open/high/low/close` and reconstructs a numeric volume field from `ICS Dollar Volume / close` only to satisfy the production OHLCV contract. This is normalization for machinery testing, not a claim about scientific validity.

## Execution progression

Use a dedicated output directory outside the repository, for example:

`~/MTS_TEST_OUTPUT/PIPELINE_TEST_NONSCIENTIFIC`

First run a tiny integration slice:

```bash
python scripts/run_pipeline_test_nonscientific.py \
  --output-root "$HOME/MTS_TEST_OUTPUT/PIPELINE_TEST_NONSCIENTIFIC" \
  --ticker-limit 3 \
  --security-batch-size 1 \
  --date-batch-size 10 \
  --reset
```

Require `PIPELINE_TEST_COMPLETE`, `SOL_CALLS=0`, `QWEN_CALLS=0`, and `CANONICAL_NEXUS_WRITES=0` before scaling.

Then run a larger integration slice (10 securities) into a fresh/reset test root. If successful, run the complete recovered market with bounded security batches:

```bash
python scripts/run_pipeline_test_nonscientific.py \
  --output-root "$HOME/MTS_TEST_OUTPUT/PIPELINE_TEST_NONSCIENTIFIC" \
  --security-batch-size 2 \
  --date-batch-size 20 \
  --reset \
  2>&1 | tee "$HOME/MTS_PIPELINE_TEST_NONSCIENTIFIC_FULL_20260915.txt"
```

The checkpoint permits completed security partitions to be skipped on a resumed run when `--reset` is omitted.

## Acceptance evidence

The harness must produce isolated per-security predictor/outcome partitions, date-scoped market cross-sections, a market-profile index, checkpoint state, memory telemetry, and `FINAL_ENGINEERING_REPORT.json`.

The final report must retain `scientific_status=NONSCIENTIFIC_ENGINEERING_TEST` and zero AI/canonical-Nexus activity.

The meaningful pass claim is limited to engineering capability: MTS can move the test population through production deterministic feature mathematics, persist bounded intermediate state, reconstruct date-level population context, execute production cross-sectional Analysis, and produce reproducible market-profile artifacts without requiring the complete history/universe working set to remain resident in memory.
