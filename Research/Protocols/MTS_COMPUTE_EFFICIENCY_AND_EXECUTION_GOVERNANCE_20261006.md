# MTS COMPUTE EFFICIENCY AND EXECUTION GOVERNANCE — 2026-10-06
Status: USER APPROVED / CONTROLLING ENGINEERING REQUIREMENT

## Governing Principle
If an inefficiency, configuration error, governance violation, or avoidable compute waste can be detected mechanically before or during compute, MTS MUST detect and prevent it mechanically rather than relying on ChatGPT or the user to notice it.

This protocol complements:
- MTS_ENGINEERING_CONFORMANCE_RECOVERY_FREEZE_20261006.md
- MTS_AUTONOMOUS_RUNNER_ORCHESTRATION_GOVERNANCE_20261006.md
- MTS_HANDOFF_MANDATORY_GOVERNANCE_20261006.md

## 1. Mandatory Dependency Graph / Cheap-to-Expensive Ordering
Runner construction must explicitly encode stage dependencies. Unless the controlling scientific protocol requires otherwise, execution order is:
compile/static checks -> structural/property tests -> tiny behavioral smoke -> calibration/conformance -> certification -> production compute -> validation/reporting.

An expensive stage may not launch while a required cheaper predecessor is unfinished or failed.

## 2. Compute-Budget Gate
Before launching calibration, certification stress tests, GA, or other material compute, the runner must calculate and record the effective workload budget using applicable dimensions such as seeds, folds, islands, population, generations/iterations, instruments, dates, and workers.

A calibration/smoke/conformance workload that unexpectedly approaches production-scale expense must block and require explicit approval unless that scale is itself frozen by the controlling protocol.

## 3. Configuration-Diff Enforcement
Every launch/relaunch must compare the complete effective configuration with the approved/frozen manifest. Only explicitly authorized deltas are permitted. Unrelated changes block launch.

One requested parameter change never authorizes collateral changes.

## 4. Parallelization / Resource Utilization
The dependency graph must identify independent work units. Independent folds, seeds, tests, or other units should execute concurrently up to the approved resource limit when doing so is safe and cost-effective.

The runner must not silently serialize independent expensive work while paid compute capacity sits unused.

## 5. Measured ETA / Throughput
ETAs for expensive work must be based on observed throughput whenever practical, not unsupported assumptions. The runner should benchmark an early representative unit and maintain rolling throughput/ETA telemetry.

Any material change in population, workers, folds, algorithm, data volume, hardware, or other runtime driver invalidates the previous ETA and requires recalculation.

## 6. Continuous Terminal-Condition Evaluation
Every expensive experiment must declare approved terminal conditions before launch where scientifically applicable: early PASS, early FAIL, recovery, convergence/staleness, or maximum budget.

The runner must evaluate those conditions at the cheapest scientifically valid frequency and terminate immediately when the decision is determined. Checkpoint frequency must not artificially delay decision detection.

## 7. Runtime / Progress Instrumentation
Long-running work must expose durable machine-readable progress including, where applicable:
- workflow and stage;
- PID/process health;
- seed/fold/island/unit;
- generation/iteration;
- elapsed time;
- last-progress timestamp;
- completed/remaining work;
- checkpoint/result status;
- measured throughput and ETA inputs;
- PASS/FAIL/running state.

Zero-byte or non-informative logs are not acceptable as the sole observability mechanism for paid long-running compute.

## 8. Code / Configuration Stability and Certification Binding
Certification must bind to the exact relevant code revision/hash and configuration/manifest it evaluated.

A subsequent relevant code or configuration change invalidates affected certification evidence and blocks production GA until the required affected tests/certification are rerun. A runner may not launch production compute under stale certification.

## 9. Durable Run Manifest / Evidence
Each material run must produce a durable machine-readable manifest containing enough information to reproduce and audit the run, including as applicable:
- code commit/hashes;
- controlling protocol hashes;
- effective configuration;
- explicitly authorized deltas;
- input/data identifiers and partition permissions;
- dependency/gate results;
- calibration/certification evidence;
- timestamps and runtime;
- output/checkpoint locations;
- final decision/status.

Handoffs should reference these artifacts rather than reconstructing run state from Chat memory.

## 10. Stall / Failure / Idle-Cost Protection
The runner must distinguish active progress from stopped, failed, or abnormally non-progressing work. Known terminal failures stop downstream compute immediately. Paid infrastructure must not remain active solely because Chat has not polled the workflow.

External monitoring is secondary protection; autonomous runner state is primary.

## 11. Fail Closed; No Scientific Improvisation
Efficiency controls may optimize execution of approved work but may not change scientific meaning. The runner must stop for explicit approval rather than alter scientific parameters, protected partitions, fitness, signals, thresholds, costs, allocation, or validation criteria.

## 12. Handoff Requirement
Every MTS handoff must identify this protocol as controlling. Future Chat engineering must use these controls when constructing or modifying runners. Omission makes the handoff incomplete/nonconforming.

Related incident evidence:
Research/Reports/MTS_ENGINEERING_EFFICIENCY_INCIDENTS_20261006.md

This governance remains controlling until David E. Bedwell explicitly changes or supersedes it.
