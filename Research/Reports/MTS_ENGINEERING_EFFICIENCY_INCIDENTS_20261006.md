# MTS Engineering Efficiency / Workflow Incident Record — 2026-10-06

Status: ACTIVE CANONICAL INCIDENT RECORD
Scope: MTS clean-engine certification, H.7 calibration, and GA launch workflow

## Finding 1 — Silent Stall / User-Dependent Resumption

During the 2026-10-06 workflow, substantial elapsed periods occurred in which the user reasonably believed autonomous engineering work was continuing, but there was little or no visible progress and work appeared to resume only after the user requested status or intervention.

The user estimates approximately 2.5 hours of avoidable elapsed time. Repository timeline evidence supports substantial gaps, but the exact duration must not be represented as proven CPU-idle time without process telemetry.

Formal finding: failure to autonomously continue or notify after a stopped/blocked stage caused user-dependent workflow resumption and unnecessary paid-compute elapsed time.

Required control: long-running workflows must expose active stage, process health, progress/checkpoint state, and failure/stall notification without requiring user polling.

## Finding 2 — Unauthorized Collateral Configuration Change

While implementing the explicitly requested H.7 change from periodic recovery checks to per-generation recovery detection with immediate successful-seed termination, the implementation independently reverted the previously approved calibration population from 64 to 250 individuals per island.

The recovery-check frequency and population size are independent parameters. Restoring the 500-generation failure ceiling did not require restoring the production-scale population.

Compute impact: 250 / 64 = 3.90625, so the unauthorized population change increased per-generation genome evaluations by approximately 3.9x.

The collateral change was detected by the user rather than by an automated configuration-conformance control. This is another example of the babysitting burden: the user requested one change but had to detect and correct an unrelated change.

Required control: before any modified experiment/certification run launches, compare its configuration against the last approved/frozen configuration. Refuse launch when any parameter outside the explicitly authorized change set differs.

## Frozen H.7 Configuration After Correction

- 9 islands
- 64 individuals per island
- 4 independent seeds
- per-generation recovery detection
- immediate successful-seed termination
- disk checkpoint every 10 generations
- 500-generation maximum failure ceiling
- PASS immediately when 3 seeds succeed
- FAIL once 3-of-4 success becomes impossible
- 6 parallel workers
- recovery criterion remains the approved planted-signal criterion
- same approved GA/evolution and fitness machinery
- no other parameter may change without explicit user approval

## Handoff Requirement

Both findings must be carried into subsequent MTS handoff reports and engineering-efficiency reviews until the required controls are implemented and verified.
