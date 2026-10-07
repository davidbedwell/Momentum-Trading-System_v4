# G3 V3C Failure Autopsy — 2026-10-07

The conforming V3C formal gate stopped large discovery at 1/3 significant null families.

## Confirmed defect
`run_arm()` returned numeric sentinel `-1e9` when no frozen validation candidate reached the >=25-event floor. `gate()` then treated that sentinel as an ordinary return in paired Wilcoxon ranks. A missing/undefined validation endpoint is not a -100,000,000,000% return and must not enter a rank test as numeric performance.

Re-analysis of the already-frozen V3C records, changing no genome/search/null/alpha setting and merely excluding pairs whose endpoint is undefined:
- N-A: n=23, p=0.0006393, median Real-Null +0.0159408 — significant.
- N-B: n=24, p=0.0677640, median +0.00229370 — not significant.
- N-C: n=24, p=0.0134639, median +0.00788747 — significant at frozen Bonferroni alpha 0.0166667.

Thus the recorded 1/3 gate understates separation because of a sentinel-handling implementation defect. The corrected existing-record result is 2/3, but this post-hoc correction is NOT used to authorize G3. A new prospective gate is required.

## Remaining genuine weakness
N-B remains non-significant after sentinel correction. This is not repaired by changing alpha, null family, replicate count, temporal boundary, or selecting a favorable seed. Those remain frozen.

## Structural diagnosis
V3C initializes stock-local structural candidates but immediately pools every genome across all eight stocks for selection. Earlier consumed V2 diagnostics showed strong stock-local heterogeneity and pooling dilution. Therefore the V3C selection operator is misaligned with the stated V3 specialist hypothesis: local structures compete on pooled cross-stock fitness before temporal validation.

## Prospective repair principle
V4 may repair only machinery defects/hypothesis mismatch, not the observed p-values: (1) represent undefined validation endpoint as missing and require a prospectively frozen minimum number of valid paired replicates; (2) preserve stock-local candidate identity through adaptive discovery and freeze local candidate banks before validation; (3) aggregate the eight independently frozen local validation endpoints only after validation, with no validation-driven selection; (4) retain the same 8 stocks, 2500 aligned rows, 70% discovery, 10-session embargo, 25 paired replicates, N-A/N-B/N-C definitions, Bonferroni alpha, and >=2/3 gate.
