# MTS HANDOFF MANDATORY GOVERNANCE — 2026-10-06
Status: USER APPROVED / CONTROLLING HANDOFF REQUIREMENT

Every MTS handoff report MUST reproduce the following block. Omission makes the handoff incomplete/nonconforming.

## MANDATORY ENGINEERING CONFORMANCE GOVERNANCE

Controlling protocol:
Research/Protocols/MTS_ENGINEERING_CONFORMANCE_RECOVERY_FREEZE_20261006.md
SHA-256: 519229799e3c785eee7923d1ad34560599ef73521535ce241d3e4da6c720e81c

- Claims of conformance do not count; executable evidence does.
- Scientific requirements may not be silently simplified, substituted, approximated, or redesigned.
- Required sequence: specification -> implementation -> behavioral conformance -> adversarial self-audit -> traceability -> certification -> compute.
- No simulator certification means no expensive GA.
- Protected/train/blind universe isolation must be proven behaviorally.
- Paid Astra/Claude/external review is optional only; it is not a required certification cost.
- If faithful implementation is impossible or materially ambiguous, STOP BEFORE COMPUTE and ask David E. Bedwell.
- The 2026-10-05/06 redesigned DEV117 GA is FORENSIC / NONCONFORMING / INVALID FOR SCIENTIFIC CONCLUSION.
- This governance remains controlling until David E. Bedwell explicitly changes or supersedes it.


## MANDATORY AUTONOMOUS RUNNER / ORCHESTRATION GOVERNANCE

Controlling protocol:
Research/Protocols/MTS_AUTONOMOUS_RUNNER_ORCHESTRATION_GOVERNANCE_20261006.md

- ChatGPT is an engineering/control interface, NOT the runtime process supervisor.
- An authorized multi-stage workflow must be constructed as a durable orchestrator/state-machine that automatically advances through already-approved stages.
- Successful completion of one approved stage must automatically verify evidence/configuration and launch the next approved stage; user polling or a new Chat turn must not be required merely to continue.
- Every launch/relaunch requires a complete configuration-diff gate. Only explicitly authorized parameter changes are permitted; all unrelated changes must block launch.
- The runner must fail closed on failed gates, missing evidence, configuration drift, protected-data risk, unexpected conditions, or any new scientific/design decision.
- Long-running stages require durable heartbeat/progress telemetry; external Chat/automation monitoring is only a safety net.
- Workflow state must survive Chat disconnects and restarts and resume without changing approved configuration.
- Cheap structural/property/smoke/calibration gates precede expensive compute; approved early-stop conditions terminate immediately.
- This block and the controlling orchestration protocol MUST be carried into every MTS handoff.


## MANDATORY COMPUTE EFFICIENCY / EXECUTION GOVERNANCE

Controlling protocol:
Research/Protocols/MTS_COMPUTE_EFFICIENCY_AND_EXECUTION_GOVERNANCE_20261006.md

- Mechanically detectable inefficiency or governance violations MUST be mechanically prevented rather than left for ChatGPT or the user to notice.
- Encode an explicit cheap-to-expensive dependency graph; expensive compute cannot start behind unfinished/failed cheap gates.
- Calculate/record compute budget before material runs and block unexpectedly production-scale calibration/smoke workloads.
- Parallelize independent expensive work up to approved safe resource limits; do not silently serialize while paid capacity is idle.
- Base runtime estimates on measured throughput and reset ETA after material runtime/configuration changes.
- Declare and continuously evaluate terminal conditions; stop immediately once an approved PASS/FAIL decision is determined.
- Require durable progress telemetry for paid long-running compute.
- Bind certification to exact relevant code/configuration; relevant changes invalidate affected certification before production compute.
- Produce durable machine-readable run manifests/evidence for audit and handoff.
- Prevent avoidable stall/idle paid-compute waste; external monitoring is secondary protection.
- Efficiency mechanisms may not alter scientific meaning or governance; unexpected scientific decisions fail closed.
- This block and its controlling protocol MUST be carried into every MTS handoff.
