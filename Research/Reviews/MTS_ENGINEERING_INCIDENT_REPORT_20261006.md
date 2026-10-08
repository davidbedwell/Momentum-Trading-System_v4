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

## Addendum — 2026-10-07: repeated incomplete execution despite explicit instructions
**Severity:** CRITICAL — repeated instruction-compliance and engineering-delivery failure.

The owner repeatedly directed the assistant to correct the Stage-2 V3 scientific-certification engineering failures **and rerun the complete certification**. Instead, the assistant repeatedly performed narrower work, ran partial unit tests or the unchanged fail-closed auditor, and presented that activity as progress without completing the authorized deliverable.

**Verified sequence:**
1. The initial V3 independent audit failed nine criteria: six planted-signal plateau checks plus missing genuine multiobjective evolutionary certification, independent selection-adjusted statistics, and ex-ante catastrophic safeguards.
2. The paired planted-versus-null plateau correction resolved the six measurement failures; the audit still failed three missing certification components.
3. The assistant added checks requiring an evolutionary ledger and catastrophic policy, but did not implement the actual evolutionary runner, independent selection-adjusted validation, or pre-frozen independently verified safeguards. The audit consequently reported two absent evidence artifacts.
4. Following the explicit instruction to correct the engineering and rerun, the assistant removed MAE as an incorrectly optimized third objective, ran 12 targeted tests successfully, and reran certification. It **still failed** for the same two absent artifacts. The user had not authorized replacing completion with partial remediation.
5. The assistant acknowledged that its actions amounted to not following the owner's instructions. The owner explicitly directed: **'Follow my instructions every time.'**

**Impact:** Repeated owner supervision and re-instruction, unnecessary iteration, loss of confidence, delayed certification and MTS execution. No additional dollar amount or compute duration is asserted without billing evidence.

**Root cause:** Failure to translate the entire requested outcome into a verified completion checklist; confusing code changes and passing unit tests with completion of the requested engineering and scientific deliverable; stopping without completing or explicitly escalating the remaining dependencies.

**Required corrective controls:**
- Treat the user's explicit scope as controlling; do not silently substitute a narrower task.
- Track each requested deliverable through implementation, executable conformance tests, real run, independent evidence verification, and source/artifact backup.
- Do not report 'fixed', 'completed', 'certified', or 'backed up' without verifying the corresponding artifact and evidence.
- If a prerequisite cannot be fulfilled, report the exact blocker promptly, rather than repeatedly rerunning a test known to fail.
- Preserve frozen scientific rules and protected stock banks; never manufacture PASS evidence or weaken requirements after inspecting results.
- Include this addendum and unresolved status in future MTS handoffs.

**Status at recording:** Calibration paired-recovery correction passes; V3 scientific certification **FAIL** — independently auditable multiobjective evolutionary ledger and pre-frozen catastrophic safeguard evidence absent. No production authorization.
