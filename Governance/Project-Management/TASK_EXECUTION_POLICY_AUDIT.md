# Task Execution Policy Addition Audit

## Scope

This audit records the addition of `TASK_EXECUTION_POLICY.md`.

## Purpose

The policy operationalizes the boundary between authorization and execution.

It defines governed behavior for:

- readiness;
- dependencies;
- scheduling;
- priority;
- configurable resources;
- concurrency;
- leases and heartbeats;
- timeouts;
- retries;
- idempotency;
- checkpoint/restart;
- failure classification;
- cancellation;
- completion;
- publication;
- observability;
- recovery;
- external-provider limits.

## Authority Harmonization

The policy preserves these current architecture boundaries:

- Accountability controls required Research Admission.
- Task Manager verifies authority and executes admitted/authorized work.
- Research Director owns scientific intent and interpretation.
- Workers execute only granted capabilities.
- Decision Engine retains investment Decision authority granted by applicable
  Decision/Risk/Automation governance.
- Accountability research gates are not individual-trade approvals.
- Research Nexus/artifact governance remains authoritative for durable governed
  state.

## Resource Model

Temporary deployment constraints are not made permanent policy.

CPU count, worker count, daily throughput, retry values, timeouts, lease
duration, provider quotas, and similar operational limits are governed
configuration.

## Interface Readiness

The policy requires machine-readable task state so future graphical control and
observability interfaces can display execution state without becoming a source
of task authority.

## Deferred Work

Exact task-state schemas, configuration values, transport contracts, worker
implementation, and deployment-specific limits remain implementation/schema/
contract concerns.
