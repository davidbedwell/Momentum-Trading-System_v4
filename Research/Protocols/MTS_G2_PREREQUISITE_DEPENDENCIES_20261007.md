# MTS G2 prerequisite-first dependency register

This register is not evidence of completion. Resolve dependencies before marking a downstream task PASS. Frozen scientific parameters and protected cohorts may not be altered to clear blockers.

| Task | Required predecessor or authorization | Work possible before predecessor completes |
|---|---|---|
| 01 Baseline inventory | Access to authoritative repository and artifact locations | Inventory independently |
| 02 Protected cohort/PIT integrity | 01, frozen cohort identifiers and authoritative provenance | Verify metadata and hashes without opening protected observations |
| 03 Requirement-to-test matrix | 01 and controlling governance | Build matrix independently of calibration |
| 04 Preflight/config/hash gates | 01, 03 and frozen manifest | Implement and test independently |
| 05 GA engine conformance | 03, 04 | Run deterministic, bounded tests independently |
| 06 H7 null/planted calibration | 04, 05, authoritative PIT inputs and frozen H7 protocol | Existing null job may continue; do not duplicate or change experiment |
| 07 Adversarial certification | 03–06 and complete adversarial fixtures | Build negative tests now; final verdict awaits 06 |
| 08 Catastrophic-risk policy and 45-case evidence | Pre-frozen policy, authoritative 45-case evidence, 03 | Implement schema/tests now; do not fabricate missing observations or retroactively freeze policy |
| 09 Provenance/evidence verdict | 02, 04, 06–08 | Implement hash-bound ledger now; final verdict awaits evidence |
| 10 Production runner | 03–05 and approved fold/evaluator specification | Build and test in no-production mode now |
| 11 Durable orchestration | 04, 09, 10 | Implement recovery/heartbeat/failure-injection tests now |
| 12 Final scientific certification | 02–11, each PASS with executable evidence | No bypass; fail closed until satisfied |
| 13 Production GA | 12 PASS, approved compute authorization and resources | No material compute before PASS |
| 14 Out-of-sample validation | 13 outputs, approved frozen validation partitions and access policy | Prepare scripts only; do not touch protected cohorts prematurely |
| 15 Four-era/composite reporting | 13–14 results and valid historical benchmark series | Prepare report pipeline now; no invented performance metrics |
| 16 GitHub/Backblaze/restore proof | Repository authentication, Backblaze access, generated artifacts from 01–15 | Back up completed intermediate work when authenticated; final proof only after restore verification |

External authorization blockers: server `git push origin main` currently fails with `Permission denied (publickey)`; this is not proof that other GitHub connector write routes are unavailable. Backblaze access/restore path requires verification. No status may be inferred solely from this document.
