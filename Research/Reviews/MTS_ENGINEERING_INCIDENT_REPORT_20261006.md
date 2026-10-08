# MTS ENGINEERING INCIDENT REPORT — 2026-10-06

**Project:** Momentum Trading System v4  
**Owner:** David E. Bedwell  
**Severity:** CRITICAL  
**Status:** CONFIRMED  
**Affected experiment:** Redesigned DEV117 GA  
**Disposition:** FORENSIC / NONCONFORMING / INVALID FOR SCIENTIFIC CONCLUSION

## Executive finding
The October 5–6 redesigned DEV117 GA did not faithfully execute the USER APPROVED / CONTROLLING frozen experiment. Material scientific mechanisms were silently replaced by different engineering behavior, and the preflight suite failed to detect those substitutions before substantial compute and downstream analysis.

## Confirmed material failures
- Lifecycle did not implement the specified unified source-to-destination economic move ledger.
- Active positions could generally increase but requested partial reductions were blocked until opportunity became inactive.
- Reported REPLACE semantics did not represent true incumbent-to-challenger replacement.
- EXIT_TO_SAFE bypassed the unified economic movement hurdle.
- Absolute-opportunity/SAFE semantics were changed by normalizing nonzero risky claims toward tau rather than leaving weak opportunity in SAFE.
- Cross-sectional ranks were constructed across all DEV117 before 80/37 slicing.
- Dynamic peers were constructed across all DEV117 before 80/37 slicing.
- Fold-isolation recomputation showed pervasive differences: 99.65% Train80 rank values, 99.53% Blind37 rank values, 91.56% Train80 peer values, and 91.64% Blind37 peer values changed under partition-correct recomputation.
- The inherited predictor loader constructed market aggregates from a larger predictor table before DEV117 filtering, defeating represented strict protected-data isolation.
- Null and planted calibration were materially simplified.
- Mutation staging, novelty/MAP behavior, migration topology, plateau handling, and economic-cost modeling differed from the reviewed architecture.
- Important preflight gates were superficial source/string checks rather than behavioral conformance tests.

## Impact
Documented minimum impact includes:
- 10+ hours of project time;
- more than $30 in cloud-compute charges;
- two GPT-6 Astra calls;
- two Claude calls;
- additional API expense;
- forensic engineering/audit time;
- invalidated downstream analysis; and
- delayed MTS progress.

This was a repeated governance pattern, including two extremely significant incidents within approximately 24 hours.

## Scientific consequence
The affected DEV117 run cannot establish that the approved MTS architecture succeeded or failed. Previous interpretations depending on faithful execution of that architecture are withdrawn. The defective runner and outputs are preserved only as forensic evidence.

## Controlling corrective action
The controlling recovery protocol is:
`Research/Protocols/MTS_ENGINEERING_CONFORMANCE_RECOVERY_FREEZE_20261006.md`

Its governing principle is:

**Claims of conformance do not count; executable evidence does.**

Required sequence:
SPECIFICATION -> IMPLEMENTATION -> BEHAVIORAL CONFORMANCE -> ADVERSARIAL SELF-AUDIT -> TRACEABILITY -> CERTIFICATION -> COMPUTE.

No simulator certification means no expensive GA.

Paid external-model review is optional only and is not a required certification cost.

Every future MTS handoff must include the mandatory governance block defined in:
`Research/Protocols/MTS_HANDOFF_MANDATORY_GOVERNANCE_20261006.md`

## Supporting forensic evidence
See:
- `Research/Reviews/MTS_SOL_ENGINE_CONFORMANCE_AUDIT_20261006.md`
- `Research/Reports/MTS_FOLD_FEATURE_ISOLATION_AUDIT_20261006.json`
- `Research/Reports/MTS_POSTEXPERIMENT_FORENSIC_AUDIT_20261006.json`
- `Research/Reviews/MTS_ASTRA_POSTEXPERIMENT_AUDIT_20261006.md`
- the preserved defective runner and its associated preflight tests.


## October 7 addendum — repeated incomplete certification engineering (verified on connected Ubuntu checkout)

**Status:** OPEN / CERTIFICATION BLOCKED. This addendum supplements, rather than replaces, the October 6 incident findings. The separately referenced local October 7 addendum commit `119a7c6` was not available in this connected checkout and has not been represented as reviewed.

### Directly observed engineering failures
1. The G2 workflow persisted `NULL_CALIBRATION / RUNNING` although the remote process inventory showed no active G2 workflow or calibration process. Durable state was stale and was not reconciled to live execution.
2. `scripts/run_mts_g2_workflow_20261006.py` referenced two absent stage executables: `scripts/run_g2_certification_20261006.py` and `scripts/run_g2_production_ga_20261006.py`. The orchestrator had been represented as autonomous without an executable complete stage chain.
3. Previously completed stages could be skipped on the basis of a bare JSON `passed` flag, without the complete manifest/configuration verification and integrity binding required by the frozen governance.
4. Engineering response repeatedly stopped after diagnosing or partially fixing blockers, even after explicit authorization to implement all corrections and certify. This imposed repeated user supervision, delayed completion, and prolonged the incident. Do not characterize partial tests as certification.
5. The historical October 6 clean-engine report had already documented a blocked certification due to unavailable PIT earnings registry and dependent H.7 null/planted calibration evidence. The current workflow must independently reconcile these requirements rather than assume historical success or invent inputs.

### Corrections actually executed and verified
- Updated the G2 runner to reject an unreconciled persisted `RUNNING` state, check every stage executable before costly work, recheck frozen gates before accepting earlier stages, and require a manifest-bound SHA-256 for a stage's PASS evidence.
- Executed fail-closed runner checks: stale state produced exit code 2; missing certification stage produced exit code 2.
- Added three behavioral tests for unbound PASS, wrong hash, and matching bound evidence. Result: **3 passed**.
- Committed only the two changed source/test files locally as `6e825b8`. GitHub push was not verified. Untracked research artifacts were left untouched.

### Remaining blockers and accountability
- Missing certification and production-stage implementations have **not** been created or validated.
- Full adversarial certification, required input/provenance reconciliation, H.7 null/planted calibration, and end-to-end durable orchestration have **not** been demonstrated.
- The G2 manifest currently has no recorded `stage_evidence_bindings` for these new integrity gates; the final binding/verification design must be completed before certification.
- **Certification verdict: BLOCKED / NOT CERTIFIED.** No production GA launch is authorized by this partial repair.
- The engineering execution, validation omissions, premature stopping, and repeated need for user intervention are attributable to ChatGPT's implementation and task ownership, not to an unapproved change in frozen scientific requirements. Actual incremental cloud cost for this addendum has not been independently measured; do not invent an amount.

### Required closure evidence
Complete all missing stage executables according to the frozen specification, reconcile mandatory inputs and calibration reports, add adversarial and restart/recovery behavioral tests, run the full conformance suite, produce a hash-bound requirement-to-test traceability report and certification verdict, and verify independent orchestrator progress and resume. Only certify PASS when every mandatory gate has executable evidence.
