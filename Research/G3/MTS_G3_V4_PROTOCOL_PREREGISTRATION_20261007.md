# MTS G3 V4 Prospective Gate Preregistration — 2026-10-07

Status: prospective; frozen before V4 outcomes are generated.

Purpose: repair the V3C undefined-endpoint defect and test the already-motivated stock-local specialist hypothesis without p-threshold shopping.

Unchanged controls: AAPL/MSFT/XOM/JPM/JNJ/CAT/WMT/NVDA; same 2500 aligned rows; first 70% discovery; 10-session embargo; remainder validation; 25 paired replicates; Real plus N-A stationary-bootstrap Y expected block 50, N-B guarded shift Y, N-C guarded shift X; one-sided paired Wilcoxon Real>Null; Bonferroni alpha 0.0166667; >=2/3 significant PASS, 3/3 STRONG PASS, <=1/3 FAIL. Null transform occurs before split. Validation cannot mutate, rank-repair, retune thresholds, alter scope, or select candidates.

Stock-local discovery: each ticker independently runs the exact structural screen and six lifecycle generations with population 48 under that ticker's discovery rows only. The terminal 48-candidate population for each ticker is frozen before any validation outcome for that ticker is read. There is no pooled cross-stock evolutionary ranking.

Validation endpoint: for each ticker, evaluate its frozen terminal population on that ticker's untouched validation rows. Among frozen candidates meeting >=25 validation events, compute that ticker endpoint as the median candidate mean net return. If none meets the event floor, that ticker endpoint is missing, not a numeric penalty. The arm/replicate endpoint is the median of available ticker endpoints, provided >=6 of 8 tickers have defined endpoints; otherwise the arm/replicate endpoint is missing.

Paired gate: a Real-vs-null replicate pair enters Wilcoxon only when both arm endpoints are defined. Each null family requires >=20 valid paired replicates out of the preregistered 25; otherwise that family automatically fails significance. No replacement replicates are generated. Missingness counts are reported by arm/family/ticker.

Stopping: this is the only V4 gate for this failure line. If V4 fails <=1/3, STOP_NO_LARGE_DISCOVERY. No V5 repair is authorized from this result. If V4 passes >=2/3, the already-frozen production controller may proceed to reachability/benchmark/G3 after its formal gate is updated to recognize this exact V4 artifact.
