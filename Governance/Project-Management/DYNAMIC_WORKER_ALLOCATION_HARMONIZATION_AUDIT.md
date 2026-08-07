# Dynamic Worker Allocation Harmonization Audit

## Scope

This audit records harmonization of worker and concurrency semantics across the
Task Execution Policy, Task Management Standard, and Configuration Standard.

## Canonical Model

> **Engines define capabilities. Tasks define work. Workers are execution
> instances dynamically allocated as needed.**

Workers are not permanently assigned to engines and do not inherently
correspond to CPU cores.

Task Manager discovers effective runtime compute/resource capacity and
determines safe and efficient concurrency according to task resource
requirements, priority, dependencies, capability requirements, current resource
pressure, provider constraints, and applicable policy/configuration.

## Configuration

Configured worker counts are optional ceilings, reservations, or deployment
overrides.

They constrain dynamic allocation but do not define fixed worker ownership by an
engine.

## CPU Relationship

CPU cores are compute resources, not worker identities.

Depending on workload characteristics, safe and efficient concurrency may be
lower than, equal to, or greater than physical core count.

## Result

The same architecture supports constrained local development and larger server
deployment. Additional capacity may be used efficiently without changing engine
identity, task semantics, or scientific/Decision authority.
