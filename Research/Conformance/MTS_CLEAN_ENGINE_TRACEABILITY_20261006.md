# MTS CLEAN ENGINE TRACEABILITY — 2026-10-06

Status: IMPLEMENTATION + EXECUTABLE VERIFICATION COMPLETE; CERTIFICATION GATE PENDING FINAL PREFLIGHT

## Controlling authority
- Research/Protocols/MTS_ENGINEERING_CONFORMANCE_RECOVERY_FREEZE_20261006.md
- SHA-256: 519229799e3c785eee7923d1ad34560599ef73521535ce241d3e4da6c720e81c
- Research/Protocols/MTS_HANDOFF_MANDATORY_GOVERNANCE_20261006.md
- SHA-256: e84a5ca69297c481c5a1031b1c4a73180fcd8df1781f600f986c46ed18097070

The invalid October 5–6 runner is not imported by the clean namespace.

## Frozen 30-area coverage
|#|Requirement|Evidence|Status|
|---:|---|---|---|
|1|Train80 feature isolation|per-fold physical mirrors; partition-local tape/ranks; Blind37 mutation tests|PASS|
|2|Blind37 independent reconstruction|separate 37-name mirrors and independent tape construction|PASS|
|3|Protected-data denial/isolation|Landlock ABI7; kernel-denied Train→Blind read; application deny boundary|PASS|
|4|PIT causality|200 real-data future-mutation checks|PASS|
|5|Absolute opportunity|literal F.2 claims|PASS|
|6|SAFE competition|SAFE numeraire and non-normalized absolute claims|PASS|
|7|Weak-opportunity underinvestment|hand/adversarial fixtures|PASS|
|8|ENTER|E.4 ledger fixtures|PASS|
|9|CONTINUE|E.4 ledger fixtures|PASS|
|10|Partial resize|60%→30% hand fixture|PASS|
|11|EXIT_TO_SAFE|source→SAFE hurdle fixture|PASS|
|12|True REPLACE|incumbent→challenger direct inequality fixture|PASS|
|13|SHORT entry|E.2 short value + signed ledger path|PASS|
|14|SHORT covering|cover via EXIT/REPLACE path|PASS|
|15|Friction hurdles|kappa*(exit+entry costs)|PASS|
|16|Uncertainty hurdles|lambda_u*(u_a+u_b)|PASS|
|17|Immediate re-entry|no cooldown; next-session fixture|PASS|
|18|Gross<=1|1,000 randomized genomes + ledger invariant|PASS|
|19|Exactly four allocation modes|equal/strength/uncertainty/downside reachable + hand calculations|PASS|
|20|Execution timing|close T decision; T+1 open execution; T+1→T+2 accrual|PASS|
|21|Transaction costs|0/5/10/20 sensitivities; SEC/TAF sell fees; spread/impact hooks|PASS|
|22|Borrow costs|daily short borrow + dividend liability path|PASS|
|23|No position-age dependence|static/API and behavioral tests|PASS|
|24|No entry-price/date dependence|static/API tests|PASS|
|25|No cooldown/fixed holding period|static + immediate re-entry|PASS|
|26|Deterministic reproducibility|workers=1 vs4; checkpoint generation10→12 bit-identical|PASS|
|27|Matched null calibration|same GA machinery implemented; full valid run requires mandatory earnings input|BLOCKED UPSTREAM|
|28|Planted-signal recovery|same GA calibration harness implemented; full H.7 report not executed because certification prerequisites not complete|BLOCKED UPSTREAM|
|29|Train/blind freeze barrier|four-hash gate; blind replay refuses before all four freeze files|PASS|
|30|Exact provenance/permitted universe|DEV117=117; exact fold hashes; SPY/SAFE/OFR hashes; per-fold mirrors|PASS except missing PIT earnings registry|

## Contextual layer
The controlling frozen design permits formal PIT taxonomy, dynamic peers, both, or neither. No current GICS is projected backward. Real Fold0 Train80 dynamic-peer diagnostics:
- selected mean correlation: 0.5574815961
- randomized mean correlation: 0.1349499015
- selected-minus-random: +0.4225316946
- 48,000 peer comparisons
- 60d→70d mean Jaccard churn: 0.25779375
Artifact: Research/Conformance/MTS_DYNAMIC_PEER_DIAGNOSTIC_FOLD0_20261006.json

## Registered external inputs
- SPY Yahoo parquet SHA-256: b182402afd15c074ee4cc596149bf0a821e6cbd00fa5329d84eef269636f6381
- Nasdaq-vs-Yahoo 20-return checkpoint artifact SHA-256: e2c91231f23da7aee81592fbd8ac94b8e1e7a1fd646786070a33b58caad4caa8
- FRED DTB3 SHA-256: f7d5d40d4b1f6e0545b4898c04faa08cad34d30de8708ca3278212a1a508f1db
- OFR FSI SHA-256: ad4de65362098ebace4077bdf598ef4d3f389f99ddcf9580173456ee36320b69
- DEV117 sorted-union SHA-256: 4a1b2dd387b0beece887169c0ad84eee4c77f279db6955fbbc9dbbe6461ed6ec

## Verification
Latest combined run:
- Python compileall: PASS
- Tests/configuration/test_paths.py + Tests/test_ga_redesign_approved_preflight_20261006.py + Tests/conforming_ga: 125 PASS
- Known warnings: NumPy correlation warnings for constant peer vectors; no gate failures.

## Certification prerequisite still absent
A full historical point-in-time earnings event registry is not present in the recovered clean data store or recovery archives, and EODHD_API_TOKEN is not configured on Thunder. Claude D.5 says not to silently drop this family. Therefore H.7 null/planted calibration cannot be represented as a valid full-pipeline calibration until the earnings stream is restored/rebuilt.
