# MTS v2 Architecture Consistency Audit

**Status:** Completed  
**Scope:** `SYSTEM_ARCHITECTURE.md`, `RESEARCH_NEXUS_ARCHITECTURE.md`, `ENGINE_ARCHITECTURE.md`, `DATA_ARCHITECTURE.md`, `DECISION_ARCHITECTURE.md`

## Result

The five architecture documents are structurally coherent and support the same mature MTS model:

- engines perform bounded work;
- the Task Manager is a permanent first-class scheduling/routing/supervision component;
- the Research Nexus is the canonical durable system of record and relationship layer;
- `mts` is an operator/control interface rather than a replacement for the Task Manager;
- the Research Director determines what research is needed;
- Decision Intelligence determines what action is appropriate;
- Learning & Governance evaluates outcome and lifecycle behavior;
- the three persistence classes remain independent of semantic artifact type;
- physical storage remains deployment configuration;
- the architecture is designed for the known server-scale end state from the beginning.

No fundamental architectural contradiction was found.

## Harmonizations Applied

### 1. `mts` Initiation Boundary

A small gap existed around the fact that `mts` is the practical initiation point while the Task Manager is the permanent coordination authority.

The System Architecture now explicitly defines `mts` as the initial canonical MTS Control Interface. It may submit work and expose operational controls, but it does not replace the Task Manager or gain scientific/decision authority.

### 2. Durable Task State vs Transient Queue State

The documents correctly described both durable task recovery and temporary queues, but the storage-class boundary could be read ambiguously.

The architecture now explicitly states:

- governed Task Requests, dependencies, and material execution records required for recovery/provenance are **Class II Research Nexus state**;
- reconstructable scheduler queues, worker-local scheduling caches, locks, and equivalent runtime structures are **Class III**.

### 3. Class II Backup Rule

The documents agreed that valuable Nexus state requires protection but differed slightly in wording around rebuildable/semi-permanent data.

The harmonized rule is:

- every Class II artifact carries an explicit `backup_requirement`;
- **Permanent Class II** assets require independent verified backup;
- **Semi-Permanent Class II** assets are independently backed up or explicitly designated recoverable-from-source according to retention, reacquisition cost, and recoverability policy.

This preserves selective backup without weakening permanent knowledge protection.

### 4. Task Outcome vs Semantic Result

Engine and Decision documents used overlapping terms for task failure and legitimate scientific/decision results.

The architecture now explicitly separates:

- **task-execution state** — e.g. `SUCCEEDED`, `FAILED_RETRYABLE`, `TIMED_OUT`;
- **semantic result** — e.g. `NO_ACTION`, `RESEARCH_REQUIRED`, `INSUFFICIENT_EVIDENCE`.

A successful task can legitimately produce `NO_ACTION`; a failed task cannot masquerade as `NO_ACTION`.

## Confirmed Consistent Areas

The audit confirmed consistent treatment of:

- Research Nexus as platform, not engine;
- stable identity independent of paths;
- mandatory metadata and provenance;
- State of Knowledge as a logical view, not a file/table;
- publication distinct from validation and promotion;
- Research Director iterative questioning;
- research/decision separation;
- Market Discovery/Decision separation;
- outcome feedback to Learning & Governance;
- long/short symmetry;
- instrument and scalability awareness;
- cache retirement based on dependency and durability criteria;
- v1 migration by semantics rather than directory structure;
- Git for system definition, Nexus for durable scientific/operational state, cache for transient work;
- backend relocation without engine redesign;
- mature server/concurrent design as a governing input.

## Remaining Work

The architecture is now ready to be frozen into Git.

The next layer should define governed standards/contracts/schemas rather than introduce new architecture unless implementation exposes a genuine architectural gap.
