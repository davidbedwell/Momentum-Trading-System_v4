# MTS G3 V5 Prospective Gate Preregistration — 2026-10-07

Status: prospectively specified after V4 fail-stop and before any V5 outcome is generated.

Purpose: repair only V4's endpoint/statistical defect. V4 made a null arm's failure to produce enough viable stock-local specialists cause the paired comparison itself to disappear. V5 retains that viability information explicitly rather than imputing an arbitrary return.

## Frozen search and data
Unchanged from V4: AAPL/MSFT/XOM/JPM/JNJ/CAT/WMT/NVDA; same 2500 aligned rows; first 70% discovery; 10-session embargo; remainder untouched validation; stock-local exact structural screen; population 48 per ticker; six lifecycle generations; terminal stock-local candidate banks frozen before validation; >=25 validation events defines a viable candidate; 25 paired replicates; Real plus N-A stationary-bootstrap Y expected block 50, N-B guarded shift Y, N-C guarded shift X. Null transform occurs before temporal split. Validation cannot mutate, select, rank-repair, retune, or alter scope.

## Ordered validation endpoint
For every arm/replicate and every ticker, evaluate the frozen terminal population on untouched validation. A ticker is viable if at least one frozen candidate has >=25 validation events. Its ticker return endpoint is the median mean net return among all viable frozen candidates.

The arm/replicate endpoint is the ordered pair:
1. `viable_stock_count`: integer 0..8; number of ticker banks with at least one viable candidate.
2. `median_viable_return`: median ticker return endpoint among viable ticker banks; null only when viable_stock_count=0.

No numeric sentinel or arbitrary return is substituted for non-viability.

## Paired Real-vs-Null comparison
For each replicate and null family, compare the ordered endpoints lexicographically:
- larger viable_stock_count wins;
- if viable_stock_count ties and is >0, larger median_viable_return wins;
- if both counts are zero, or both ordered endpoints are exactly equal, the replicate is a tie.

The primary family test is a one-sided exact paired sign test over non-tied replicate outcomes, H1: Real wins more often than Null. Ties are excluded from the binomial denominator. All 25 preregistered replicates are generated; no replacements.

For k Real wins among n non-tied pairs, p = P[Binomial(n,0.5) >= k]. If n=0, p=1.

## Frozen multiplicity and gate
Bonferroni per-family alpha remains 0.05/3 = 0.0166666666667. A family is significant only when exact sign-test p < alpha. Overall: 3/3 STRONG_PASS_3_OF_3; 2/3 PASS_2_OF_3; <=1/3 FAIL_NO_LARGE_DISCOVERY.

Report wins, losses, ties, non-tied n, exact p, and separate diagnostics for viability-count and return tie-break contributions. No Wilcoxon test is used for the V5 primary gate.

## Stopping
V5 is the final repair authorized on this null-gate line. If V5 fails <=1/3, STOP_NO_LARGE_DISCOVERY. No V6 is authorized from the V5 outcome.
