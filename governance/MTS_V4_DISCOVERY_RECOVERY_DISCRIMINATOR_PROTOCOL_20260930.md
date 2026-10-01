# MTS v4 — Discovery Recovery Discriminator Analysis Protocol
Date: 2026-09-30
Role: Discovery-only descriptive discriminator analysis using ONLY the already-written Recovery-Pattern checkpoints. No OHLCV reacquisition. No Verification access. No Search/refit/selection.

## Frozen populations
Use trades with adverse excursion and classify without changing the original frozen terminal exit:
A. CONFIRMED_RECLAIM_WIN: original-level reclaim occurred, executable next-open confirmation entry existed, and terminal exit > confirmation entry.
B. CONFIRMED_RECLAIM_LOSS: same reclaim/confirmation condition, but terminal exit <= confirmation entry.
C. NO_CONFIRMED_RECLAIM: adverse excursion occurred but no executable original-level reclaim confirmation entry existed before original terminal exit.

Also retain original terminal-return sign as a separate descriptive label; do not conflate it with post-reclaim profitability.

## Frozen feature source
Read only fields already recorded in discovery_recovery_pattern_checkpoints_20260930. No market-data fetches and no feature recomputation from future bars.

Analyze the recorded reclaim-observation features individually:
close_vs_ref; SMA10/20/50 distance and 5-session slope; EMA20 distance and 5-session slope; ATR14; reference distance in ATR; RSI14; volume/20-session mean; prior 5/10/20-session low distance, swept, reclaimed; swing10 swept/reclaimed; lower-wick fraction; body fraction; realized-volatility20.

For depth-conditioned observations, separately analyze the same recorded feature set at each frozen AE depth 1%,2%,3%,5%,7.5%,10%. Do not select a preferred depth.

## Descriptive comparisons
For each continuous feature and each eligible group report count, median, mean, p25, p75. Report pairwise standardized median separation using pooled IQR where available and absolute rank-biserial/AUC-style discrimination computed deterministically. For Boolean features report prevalence and percentage-point differences.

Report results overall and breadth by ticker and family. Because candidate-trade rows are dependent/repeated, raw row counts are descriptive only; do not present conventional independent-trial p-values.

## Ranking boundary
The report may order features by descriptive separation solely to make the dataset inspectable. Such ordering is NOT winner selection, parameter selection, validation, promotion, or permission to construct a rule. Preserve all measured features in output, not only leaders.

## Outputs
Detailed JSON to disk; terminal limited to group sizes plus top descriptive continuous and Boolean separations. Any rule/composite suggested after viewing this report is a newly observed Discovery hypothesis and must be frozen before subsequent testing.

SEARCH_RUN=False
REFIT=False
RULE_SELECTION=False
VERIFICATION_A_ACCESSED=False
VERIFICATION_B_ACCESSED=False
SOL_CALLS=0
