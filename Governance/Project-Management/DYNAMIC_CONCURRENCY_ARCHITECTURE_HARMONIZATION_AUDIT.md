# Dynamic Concurrency Architecture Harmonization Audit

## Scope

This audit records removal of residual fixed-worker examples remaining after
MTS adopted dynamic worker allocation.

## Finding

The cross-policy conformance audit found three residual examples containing
`max_workers = 1`:

- `Architecture/SYSTEM_ARCHITECTURE.md`
- `Architecture/ENGINE_ARCHITECTURE.md`
- `Governance/Standards/TASK_MANAGEMENT_STANDARD.md`

These examples did not override newer governance, but they could imply that a
fixed worker count is part of the canonical architecture.

## Harmonization

The System Architecture now states that initial effective concurrency is
determined dynamically from runtime capacity, task characteristics, governed
constraints, and optional ceilings/reservations.

The remaining illustrative configuration examples now use:

```text
effective_concurrency = runtime_determined
```

rather than a fixed numeric worker count.

## Canonical Result

A constrained deployment may still resolve to effective concurrency of one.
That is a runtime result, not a hard-coded architectural allocation.

Engines define capabilities. Tasks define work. Workers are execution
instances dynamically allocated as needed. Task Manager determines safe and
efficient concurrency from runtime conditions and governed constraints.
