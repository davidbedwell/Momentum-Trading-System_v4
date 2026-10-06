# MTS CLEAN ENGINE TRACEABILITY — 2026-10-06

Status: ENGINEERING IN PROGRESS — NOT CERTIFIED — GA BLOCKED

Controlling authority:
- Research/Protocols/MTS_ENGINEERING_CONFORMANCE_RECOVERY_FREEZE_20261006.md
- SHA-256 519229799e3c785eee7923d1ad34560599ef73521535ce241d3e4da6c720e81c
- Research/Protocols/MTS_HANDOFF_MANDATORY_GOVERNANCE_20261006.md
- SHA-256 e84a5ca69297c481c5a1031b1c4a73180fcd8df1781f600f986c46ed18097070

Architecture authority: MTS_GA_REDESIGN_EXPERIMENT_FREEZE_20261005.md plus Claude reviewed architecture MTS_CLAUDE_GA_REDESIGN_REVIEW_20261005_221916.md, subject to the user-approved freeze and no unapproved numeric guard thresholds.

The invalid October 5–6 runner is not imported by this clean namespace.

| # | Frozen coverage | Implementation / evidence | State |
|---|---|---|---|
|1|Train80 feature isolation|data.PartitionStore; engine.partition_rank; adversarial Blind37 mutation|PASS synthetic; real-fold integration pending|
|2|Blind37 independent reconstruction|partition-local materialization/ranking|PASS synthetic; real-fold integration pending|
|3|Protected-data denial/isolation|PartitionStore fail-closed deny set|PASS unit; OS/file provenance integration pending|
|4|PIT causality|causal_view; future mutation adversarial test|PASS synthetic|
|5|Absolute opportunity|claims.frozen_claims literal F.2|PASS|
|6|SAFE competition|absolute non-normalized claims|PASS|
|7|Weak-opportunity underinvestment|weak-claim adversarial fixture|PASS|
|8|ENTER|ledger.move_ledger|PASS|
|9|CONTINUE|ledger.move_ledger|PASS|
|10|Partial resizing|hand-computed 60→30 fixture|PASS|
|11|EXIT_TO_SAFE|source→SAFE E.4 hurdle|PASS|
|12|Genuine REPLACE|source→destination E.4 inequality|PASS|
|13|SHORT entry|clean engine lifecycle fixture|PASS primitive; literal E.2 short valuation integration pending|
|14|SHORT covering|exit/replace ledger semantics|PASS primitive; integration pending|
|15|Friction hurdles|ledger.hurdle_gain with source exit + destination entry cost and kappa|PASS|
|16|Uncertainty hurdles|ledger.hurdle_gain lambda_u*(u_a+u_b)|PASS|
|17|Immediate re-entry|no cooldown state; fixture|PASS|
|18|Gross exposure <=1|ledger invariant and randomized primitive fixture|PASS primitive; full-run randomized 1000-genome gate pending|
|19|Exactly four allocation modes|enum + literal F.2 claim functions|PASS|
|20|Execution timing|execution.next_open_return T+1 open onward|PASS fixture|
|21|Transaction-cost accounting|primitive hand fixture|PASS primitive; historical SEC/TAF + realistic spread/impact integration pending|
|22|Borrow-cost accounting|primitive hand fixture|PASS primitive; E.2/J.4 full short economics pending|
|23|No position-age dependence|decision API/static adversarial test|PASS|
|24|No entry-price/date dependence|decision API contains neither|PASS|
|25|No cooldown/fixed holding period|decision API + immediate re-entry fixture|PASS|
|26|Deterministic reproducibility|deterministic SHA-256 stage seeds + deterministic fixtures|PASS primitive; worker/checkpoint bit-identity pending|
|27|Matched null calibration|Claude H.7 full-pipeline block-permuted null|PENDING|
|28|Planted-signal recovery|Claude H.7 conditional planted structure, >=3/4 seeds|PENDING|
|29|Train/blind freeze barrier|four-hash fail-closed barrier|PASS mechanism; actual fold freeze integration pending|
|30|Exact provenance/permitted universe|provenance hash primitive|PENDING real dataset certification|

## Staged GA mechanics
- A 0–100 baseline; B 100–250 context/applicability/sector up-weight; C 250–450 lifecycle/allocation/short up-weight; D 450–500 robustness.
- Nine-island ring topology helper; top 5% migration count.
- Seven required MAP descriptors.
- Behavioral-distance novelty primitive.
- First plateau immigrant/structural action; second consecutive plateau freeze/reallocate action.
- Deterministic SHA-256(fold,island,generation) seed derivation.
These mechanisms have unit evidence but are not yet a complete certified evolutionary runner.

## Certification state
FAIL-CLOSED / NOT CERTIFIED.
No GA may launch. Remaining blockers include real-data provenance and protected-path isolation, literal short valuation/economics, complete cost model, full simulator integration, 1000-random-genome gross gate, worker/checkpoint determinism, matched null, planted recovery, and actual fold freeze/replay ordering.
