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
