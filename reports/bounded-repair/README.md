# Bounded free-data repair: NO-GO — STOP

One experiment, completed 2026-10-31. Sourcing capped at ten minutes and stopped early after the bounded probes. No primary rerun was justified: recovered price rows **0**, newly verified historical sector labels **0**, usable coverage gain **0 percentage points**. No further sourcing is scheduled.

## Alignment and reversal controls

Synthetic fixed seed 731, 120 independent monthly cross-sections, four sectors and 80 stocks: known perfect rank IC **1.00000**; one-month lag negative control **0.01565**, NW t **1.853**, original twelve-test Holm p **0.767**. Perfect positive control has zero sampling variance, so its t/p are undefined rather than invented. Twenty-four artificial stock/horizon rows passed actual row-builder assertions for next-session entry open, terminal month-end close and independently calculated returns. These are artificial diagnostics, never empirical research evidence.

Saved historical observations reproduce all six frozen H1/H2/H5 1m/3m means to floating-point precision. Prior nonoverlapping realized-return reversal diagnostic: 1m IC **−0.01137**, NW t **−0.931** (103 months); 3m IC **−0.01237**, t **−0.718** (99 months). No statistically persuasive reversal or proven alignment defect. No core change was made. Same-symbol/sector joins require matching calendar months; no positional shifts bridge missing months.

H2 future-month signal vs current return IC is 0.45509 at 1m and 0.24129 at 3m. This deliberately contaminated diagnostic contains prices from the return window; it is a warning, not proof that correctly dated signals leak. Full historical past/current/future diagnostics are in [diagnostics.json](diagnostics.json). These diagnostic variants do not qualify as new primary tests or gate evidence.

## Source comparison

Pinned pitindex commit: `2df030e5c9be7c83cf4b28c3d8597d74d274757e`. Only small membership tables, documentation and API/loader code were retrieved; no package was executed or universe prices downloaded. Source URLs, retrieval timestamps, byte counts and SHA256s are in [acquisition.json](sources/acquisition.json). The pinned build metadata says seed 2004-12-30, whereas the README advertises 2005-01-03; both cover requested Stage1 membership dates. It also reports two synthetic reconciliation events: membership is a community reconstruction requiring validation.

Across all **111** existing IVV snapshot dates:

| Measure | Result |
|---|---:|
| Mean exact-ticker Jaccard overlap | 78.90% |
| Minimum overlap | 74.00% |
| Mean common tickers per snapshot | 439.76 |
| IVV-only / pitindex-only stock-months | 6,658 / 6,563 |
| IVV priced stock-months | 27,511 |
| pitindex priced stock-months using existing cache | 29,821 |
| pitindex missing-price stock-months | 25,555 |
| Comparable current-vs-IVV sector stock-months | 23,975 |
| Sector disagreements among those | 1,577 (6.58%) |

The 2,310 net additional priced matches are a roster-composition difference, not recovered prices or approved usable observations. Exact-ticker differences include aliases and renames; neither source is assumed ground truth. Pitindex can supply candidate membership for all nine missing January–September 2006 months (498 members each), but **zero newly verified historical sector labels**. Its API explicitly enriches with current Wikipedia sectors for surviving members and generally lacks sectors for removed members. Current labels were compared as a source diagnostic only and never backfilled. Dated IVV sector evidence remains available only from April 2007 and itself has unverified publication/classification vintage. See [per-date comparison](membership_comparison.csv).

## Targeted price recovery and blockers

Read-only, depth-four, maximum-60-second filename search of three known cache locations checked LEH, LEHMQ, BSC, BSC.1, WAMUQ, WB, MER, CFC, AABA and YHOO: **no hits**. [Search provenance](local_price_search.json) records exact roots and bounds. Free Yahoo daily historical requests restricted to 2004–2015 for LEH, LEHMQ, BSC, WAMUQ, MER and CFC each returned **HTTP 404**; [request provenance](price_probes.json). No terminal prices, cash merger proceeds, successor returns, or aliases were manufactured. These bounded failures do not establish that no other free source exists anywhere.

Unchanged baseline: **869,522** price rows, **322/803** historical proxy symbols priced, **481** without cache/Stage1 prices. Of **55,471** IVV holding stock-months, **27,960** lack a formation-date price; **26,018** have a price and known dated sector (**46.90%**). Full-holdings benchmark outcome rows remain **0**. Missing terminal prices and permanent issuer/share-class identities remain unresolved.

Meaningful improvement rule: at least five percentage points of priced, historically sector-verified stock-month coverage, or twelve additional complete sector-month benchmarks. Actual gain is zero under either rule; the decision does not depend on the threshold. Membership alone cannot satisfy the missing-price or historical-sector requirements.

## Frozen results and decision

Existing dated-IVV results below are copied for comparison, **not rerun**:

| Signal | 1m mean IC / NW t | 3m mean IC / NW t |
|---|---:|---:|
| H1 | 0.00128 / 0.07356 | 0.00103 / 0.03577 |
| H2 | −0.01070 / −0.55818 | −0.02706 / −0.92523 |
| H5 (raw; expects negative) | 0.00957 / 0.49011 | 0.02378 / 0.75330 |

All six existing primary pairs failed their original 1,000-shuffle placebo comparison. The original twelve-test Holm family and criteria remain frozen; no new primary permutation, significance calculation or gate was run. No H3/H4/H6 historical evaluation, Stage2 access, paid data, main MTS write or GitHub push. Protected manifest/protocol/core/executor/gate SHA256s match the previous expanded study. Existing provisional results remain unsuitable for certification or Stage2 release.

Machine-readable decision and counts: [comparison.json](comparison.json). Reproduce diagnostic and comparison with `/opt/mts/.venv/bin/python -m sector_pipeline.bounded_repair` and `/opt/mts/.venv/bin/python -m sector_pipeline.compare_bounded_repair` using the pinned saved sources. Network sourcing is not repeated by those commands.

Validation: existing analysis-environment suite **43 passed**; six baseline means independently reproduced within 1e-12; protected-file hash check passed. See [validation.json](validation.json).
