# MTS AUTONOMOUS RUNNER / ORCHESTRATION GOVERNANCE — 2026-10-06
Status: USER APPROVED / CONTROLLING ENGINEERING REQUIREMENT

## Purpose
MTS engineering must not create workflows that depend on an active ChatGPT turn, user polling, or manual user intervention merely to advance from one already-approved stage to the next. Chat is an engineering/control interface, not the runtime process supervisor.

## Mandatory Architecture
For any explicitly authorized multi-stage MTS workflow, construct a durable orchestrator/state-machine runner that owns the approved sequence end-to-end.

Example:
PREFLIGHT -> CALIBRATION/CONFORMANCE -> CERTIFICATION -> GA -> VALIDATION -> REPORTING

The exact stages must come from the controlling protocol for that run.

## Automatic Stage Transition
After an approved stage completes successfully, the runner must:
1. verify the expected result/evidence artifact;
2. verify integrity/hash where required;
3. compare the next stage configuration against the frozen/approved manifest;
4. durably record the completed stage and transition;
5. automatically launch the next already-authorized stage.

No new Chat turn or user status request is required merely to continue an already-authorized workflow.

## Fail Closed
The orchestrator may execute approved decisions but may not make new scientific decisions.

It MUST STOP rather than improvise when:
- a gate fails;
- required evidence is missing or invalid;
- configuration differs from the approved/frozen manifest;
- an unexpected condition occurs;
- protected-data governance would be violated;
- the next action requires a scientific/design decision not already authorized.

It may not silently alter population, generations, thresholds, signals, partitions, fitness, costs, allocation, recovery criteria, or any other scientific/compute parameter.

## Configuration-Diff Gate
Every launch/relaunch must compare the complete effective configuration against the last approved/frozen configuration. Only explicitly authorized deltas are permitted. Any other delta blocks launch and is reported.

Changing one parameter is authorization to change that parameter only.

## Progress / Heartbeat
Long-running stages must expose durable machine-readable progress sufficient to determine:
- workflow/stage;
- process/PID health;
- seed/fold/island or other active unit;
- generation/iteration when applicable;
- elapsed time;
- last-progress timestamp;
- checkpoint/result state;
- PASS/FAIL/running status.

A lightweight heartbeat should be updated approximately every 30-60 seconds where practical. Expensive checkpoint serialization must not be required merely to report progress.

## Stall / Failure Handling
The runner must distinguish active computation from a stopped, failed, or non-progressing stage. It must record failures immediately and must not burn paid compute indefinitely after a known terminal condition.

External periodic monitoring is a safety net, not the primary orchestration mechanism.

## Resume / Restart
Workflow state must survive Chat disconnects and machine/process restarts. Resume must continue from the last verified durable state without silently changing the approved configuration.

## Cost-Efficiency Requirement
Calibration, smoke tests, and structural/property tests must be deliberately cheaper than production compute when scientifically possible. Cheap failure detection precedes expensive compute. Early-stop criteria must terminate work immediately when the approved decision criterion is satisfied.

## Handoff Requirement
Every MTS handoff must state that this governance is controlling and must direct future engineering sessions to construct runners according to it. A handoff that omits this requirement is incomplete/nonconforming.

## Related Incident Evidence
Research/Reports/MTS_ENGINEERING_EFFICIENCY_INCIDENTS_20261006.md

This governance remains controlling until David E. Bedwell explicitly changes or supersedes it.
