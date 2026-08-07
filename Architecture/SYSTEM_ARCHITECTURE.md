# Momentum Trading System --- System Architecture

**Status:** Canonical\
**Authority:** Governing system architecture subordinate only to
`CHARTER.md`

## 1. Purpose

This document defines the enduring system architecture of MTS. It
translates the Charter into system boundaries, component
responsibilities, information flows, persistence rules, authority
boundaries, and expansion rules while leaving implementation details to
technical designs, contracts, schemas, standards, policies, and source
code.

## 2. Governing Model

> **Engines perform work. The Research Nexus preserves and connects
> durable state. The Task Manager schedules, routes, and supervises work.**

No engine owns the Research Nexus or becomes the hidden architecture of
MTS. Components communicate through governed contracts and artifacts,
not private directories or undocumented conventions. Physical location
is configuration, not architecture.

### 2.1 Design With the End in Mind

MTS SHALL be architected for its known intended mature operating model
from the beginning.

The architecture must assume eventual:

- server deployment;
- concurrent workloads;
- scheduled and autonomous intake;
- iterative autonomous research;
- live-market processing;
- worker pools;
- task prioritization and dependency management;
- retry and recovery after interruption;
- scalable durable storage;
- independently scalable engines and services.

A component that is clearly required by the intended mature system
SHALL exist as a first-class architectural component now, even when its
initial implementation is intentionally small.

Initial implementations MAY operate with one worker, one computer, or
one local process. They SHALL NOT use a temporary architecture that
must later be replaced merely to reach the already-known mature state.

The governing design test is:

> **Would MTS still choose this component boundary and contract if the
> system were running at its intended server scale today?**

If the answer is no, the architecture must be reconsidered before
implementation.

## 3. System Boundary

MTS includes the Research Nexus, Task Manager, engines, shared core
services, governed schemas/contracts/policies/standards, validation and
lifecycle services, Control Center, observability/audit, Decision
Intelligence, and learning/governance capabilities. External providers
supply information or services but do not define MTS semantics,
identity, lifecycle, policy, or architecture.

## 4. Information Hierarchy

`Source Data → Observations/Measurements → Evidence → Findings → Knowledge → Decisions → Outcomes → Learning/Re-evaluation`

Research state, policies, provenance, contradictions, validation
records, and work requests may relate to any stage. Producing an
artifact does not establish its truth.

## 5. Research Nexus

The Research Nexus is the canonical persistent system of record and
exchange for MTS data, evidence, findings, knowledge, research state,
decisions, outcomes, policies, and provenance. It is a platform, not an
engine.

It provides canonical identity, publication/retrieval, discovery,
relationship resolution, provenance, lifecycle, retention, validation
state, promotion/supersession history, archive/retirement, backup
classification, auditability, reproducibility, and backend independence.

Canonical durable content should be stored once when practical and
referenced by stable identity. Engines create artifacts but do not own
their permanent storage.

The Nexus can assemble a governed **State of Knowledge (SoK)** as a
point-in-time logical view of current applicable canonical knowledge for
a defined subject and use. The SoK may include uncertainty, applicability,
limitations, validation context, recency, decision eligibility, and
provenance references.

Unresolved contradictions, hypotheses, open questions, gaps, and other
research working state remain governed Research Nexus state but are not
automatically canonical knowledge or part of an ordinary Decision SoK.

## 6. Three Storage and Persistence Classes

Every managed artifact receives a persistence class. Semantic type
answers **what it means**; storage class answers **how it is
preserved**.

### 6.1 Class I --- Source-Controlled System Assets

Includes source code, Charter, architecture, ADRs, standards, authored
policies, contracts, schemas, configuration templates, tests, utilities,
small deliberate fixtures, and documentation required to rebuild MTS.

-   **Git/GitHub:** required.
-   **Research Nexus:** not the primary home.
-   **Retention:** permanent through source-control history unless
    deliberately changed.
-   Large datasets, research payloads, market histories, runtime
    outputs, and Nexus contents do not enter Git merely because they are
    important.

### 6.2 Class II --- Durable Research Nexus Assets

Includes accepted source datasets, evidence, material findings,
knowledge, research state, valuable research plans, material active research state,
decisions, outcomes, applied operational-policy versions, provenance,
validation history, and supersession/retirement history.

-   **Git:** prohibited except intentionally reduced fixtures/examples.
-   **Research Nexus:** required.
-   **Independent backup:** every Class II artifact SHALL carry an
    explicit backup requirement. Permanent Class II assets require
    independent verified backup. Semi-permanent Class II assets are
    backed up according to recoverability, reacquisition cost, and
    retention policy.

**Semi-permanent:** retained while scientifically, operationally, or
reproducibly useful. Examples include difficult-to-reacquire source
history, accepted normalized datasets, detailed evidence, completed
campaigns, and intermediate scientific assets needed for retained
findings. Removal requires governed criteria and
dependency/reproducibility verification.

**Permanent:** durable intellectual and decision history: canonical
knowledge, material supporting findings, critical provenance, knowledge
lifecycle history, material decisions, realized outcomes, critical
conclusions, and policy versions governing material actions. Retirement
normally removes material from active use without erasing lineage;
physical deletion is exceptional and governed.

### 6.3 Class III --- Transient / Cached Working Data

Includes caches, scratch, staging, decompressed working copies, joins,
materialized queries, live buffers, intermediate calculations, temporary
Research Director context, replaceable local copies, queues, locks, and
test/runtime caches.

-   **Git:** prohibited.
-   **Durable backup:** normally prohibited.
-   **Retention:** temporary.
-   **Deletion:** automated only under governed conditions.

A cached object is not deletion-eligible merely because another copy is
assumed. Required durable publication must be verified; no active
research/decision dependency may remain; and retention policy must
permit deletion. Fully reproducible cache with no durable-publication
requirement may expire by policy.

## 7. Meaning and Persistence Are Independent

Example: `artifact_type=EVIDENCE`, `storage_class=DURABLE_NEXUS`,
`retention_class=SEMI_PERMANENT`, `lifecycle_state=VALIDATED`. A
materialized query may instead be `TRANSIENT_CACHE/TEMPORARY/ACTIVE`.

## 8. Mandatory Identity and Metadata

No managed artifact may exist without sufficient metadata to identify,
govern, discover, relate, reproduce, retain, back up, and retire it.
Filenames and paths are not canonical identity.

Durable artifacts provide or inherit as applicable: `artifact_id`,
`artifact_type`, `artifact_family`, `storage_class`, `retention_class`,
`lifecycle_state`, `created_at`, `producer`, `producer_version`,
`schema_id`, `schema_version`, `content_hash`, provenance,
source/dependency references, validation status, backup
requirement/status, supersession relationships,
research/campaign/decision relationships, and tags.

Transient managed artifacts carry enough metadata to determine identity,
producer/owner, storage class, lifecycle, dependencies, expiration, and
deletion eligibility.

Governed classification fields use controlled values. Flexible tags may
aid discovery but never replace governed metadata. Material
relationships are explicit, not inferred from filenames or directory
proximity.

## 9. Backup and Recoverability

Backup follows meaning, retention, recoverability, and scientific value.
A Git push is not a complete data-backup strategy.

-   Class I: Git plus off-machine source control.
-   Class II: independently backed up according to policy; selection
    should ultimately be metadata-driven, not folder-driven; completion
    must be verifiable.
-   Class III: normally excluded from durable backup. Valuable transient
    artifacts must be reclassified and durably published before
    protection is assumed.

## 10. Physical Storage Independence

The Nexus may live on local storage, directly attached storage, network
storage, a server, object storage, distributed storage, or future
technology. Backend changes must not change identity, meaning,
relationships, lifecycle semantics, contracts, or client behavior.
Components use governed services/adapters, not hard-coded physical
paths.

### 10.1 MTS Control Interface

`mts` is the initial canonical operator entry point to MTS.

It is a control interface, not a substitute for the Task Manager or an
engine. It may:

- submit governed work to the Task Manager;
- start or stop authorized services;
- request system status;
- inspect task state;
- query Research Nexus state;
- invoke governed administrative operations;
- expose human-facing commands for development and operations.

As MTS matures, additional interfaces such as a Control Center UI,
service API, or remote administrative client may use the same governed
control services.

The mature architecture therefore remains:

```text
Human / Automation
       ↓
MTS Control Interface (`mts`, UI, API)
       ↓
Task Manager / governed services
       ↓
Engines and Research Nexus
```

The `mts` command does not acquire scheduling, scientific, or investment
authority merely because it initiates an operation.

## 11. Task Manager

The Task Manager is a first-class permanent MTS component responsible
for scheduling, routing, supervising, and recovering system work.

Its architectural role exists from the first v2 implementation even
when only one worker or one task may execute at a time.

The Task Manager does not decide what research is scientifically
necessary and does not make investment judgments.

Scientific and decision components determine **what work is required**.
The Task Manager determines **when, where, and by which capable worker
that work executes**.

The Task Manager owns:

- durable task intake and reconciliation;
- task queues and priority;
- dependency readiness;
- capability-based routing;
- worker registration and availability;
- concurrency and resource limits;
- CPU/core allocation policy;
- scheduling;
- retries and retry limits;
- timeout handling;
- duplicate-execution prevention where policy permits;
- interruption recovery;
- resumability;
- task status;
- execution supervision;
- failure isolation;
- execution provenance;
- operational task visibility.

The Task Manager must support the known future operating model of
multiple concurrent research, intake, discovery, live-market, decision,
and lifecycle workloads without requiring a new coordination
architecture.

The first implementation MAY use `max_workers = 1`. The mature
implementation MAY use many local or distributed workers. Both use the
same architectural task contracts and responsibility boundary.

The Task Manager does not:

- interpret scientific findings;
- formulate research conclusions;
- promote knowledge by scientific authority;
- determine whether a trade is desirable;
- alter engine-internal algorithms;
- own canonical research data.

## 12. Work Requests and Artifact Exchange

Components exchange governed artifacts and work requests through stable
contracts. Point-to-point implementation dependencies are prohibited
unless explicitly justified. A requester need not know how the receiver
performs the work.

`Decision Engine → Research Need → Research Nexus → Task Manager → Research Director → Research Plan → Research Nexus → Task Manager → Data Intake and/or Discovery`

Transport technology is technical design.

## 13. Engine Model

Engines are bounded work-performing components. Each has a defined
responsibility, consumes governed inputs, produces governed outputs,
exposes capabilities by contract, avoids other engines' private
filesystems, does not own enterprise durable state, may keep temporary
operational state, fails without corrupting the Nexus, and may evolve
internally behind compatible contracts.

### Data Intake Engine

Acquires, interprets, normalizes, measures, quality-checks, validates,
and publishes data for scientific use. It establishes intake integrity,
not economic meaning.

### Discovery Engine

Converts governed data/evidence into reproducible analytical findings
and searches/tests relationships, temporal effects, conditions,
interactions, contradictions, and statistical behavior. It does not
self-promote findings to unquestionable knowledge.

### Research Director

Directs iterative inquiry: formulates questions, inspects SoK and Active Research State,
identifies gaps/contradictions, creates proposed Research Plans, requests
intake/analysis after Research Admission, evaluates findings, asks follow-ups,
reports missing tools/evidence, converges or terminates by governed criteria,
and proposes Knowledge Candidates. Scientific authorship does not grant
independent gate authority.

### Accountability Engine

Controls two independent research gates by applying Charter-derived,
policy-defined, machine-inspectable criteria:

1. **Research Admission** — determines whether a proposed Research Plan may
   consume governed MTS research resources.
2. **Knowledge Promotion** — determines whether a Knowledge Candidate has
   satisfied the required objective gates for promotion.

Accountability evaluates alignment and gate compliance. It does not formulate
scientific conclusions, schedule workers, own canonical knowledge, make
investment Decisions, approve individual trades, or alter the criteria it
enforces.

### Market Discovery Engine

Examines current/live market state for known opportunities, event
families, unusual behavior, anomalies, and novel phenomena. It asks,
"Where is something happening that deserves evaluation?" It may route
candidates to Decision Intelligence or Research Director but does not
itself gain trading authority.

### Decision Engine

Applies governed knowledge and current market state to action:
enter/no-enter, long/short, instrument choice, stock/options, sizing,
scalability, risk, management, and exit. It does not silently conduct
scientific research. Insufficient SoK generates a governed research
need.

### Learning & Governance

Evaluates knowledge and decisions after application using objective governed
criteria: usefulness, stability, generalization, outcomes, contradiction,
decay, degradation, supersession, retirement, and whether the research and
Accountability gates are producing useful system outcomes. It may recommend
changes to knowledge, models, or policy but does not retroactively replace an
Accountability gate verdict.

## 14. Research Loop

`Question/Gap → Research Director → Proposed Research Plan → Accountability: Research Admission → Task Manager → Data Intake/Discovery → Research Nexus → Evidence/Findings → Research Director → follow-up or convergence → Knowledge Candidate → Accountability: Knowledge Promotion → governed lifecycle transition → Research Nexus`

Research may iterate. Insufficient evidence, contradiction, and missing
tooling are valid outcomes; convergence must not be forced.

## 15. Live Market and Decision Loop

`Current Market → Market Discovery → Candidate/Phenomenon → Research Nexus → Decision Engine and/or Research Director → Decision or Research Loop → Research Nexus`

Low-latency paths may be optimized, but material persistent records
eventually enter the Nexus with governed identity/provenance.
Performance optimization may not create an alternate system of record.

## 16. Outcome and Learning Loop

`Decision → Market Outcome → Outcome Record → Learning & Governance → reinforce/retain/constrain/degrade/contradict/supersede/retire → Research Nexus/SoK`

Objective lifecycle criteria belong in governance, not ad hoc engine
logic.

## 17. Authority Boundaries

Data Intake publishes governed data but not investment meaning.
Discovery publishes evidence/findings but not canonical truth. Research
Director directs inquiry, authors Research Plans, and proposes Knowledge
Candidates but does not control the independent gates applied to those
proposals. Accountability controls Research Admission and Knowledge Promotion
by applying governed criteria, but does not author the scientific conclusion,
schedule execution, own canonical state, make investment Decisions, or approve
individual trades. Research Nexus preserves state but does not perform
scientific judgment by storage. Task Manager routes admitted work but does not
judge scientific merit. Decision Intelligence may independently exercise
trade authority already granted by Decision/Risk/Automation policy; the
research Accountability gates do not constitute per-trade approval.
Learning & Governance evaluates outcomes and recommends lifecycle/policy
changes under objective criteria. Human and automation authority are
policy-controlled.

## 18. Validation and Promotion

Publication, structural validation, scientific validation, and knowledge
promotion are distinct. Promotion criteria must be objective, reproducible, governed, and appropriate to artifact type. Promotion status must be derived from inspectable evidence and explicit gate results.

## 19. Failure and Missing Information

MTS fails explicitly rather than substituting invalid data, stale
knowledge, or fabricated conclusions. Components may request
data/analysis, publish insufficient-evidence or missing-capability
results, defer, or terminate safely. One component's failure must not
corrupt canonical state, and partial work must not be promoted as
complete.

## 20. Extensibility

A new engine normally requires a defined responsibility, declared
capabilities, governed I/O contracts, durable schemas,
lifecycle/retention rules, authority boundaries, task management
registration, and conformance tests. Existing engines should not require
redesign simply because a new capability is added.

## 21. Dependency Rules

1.  Charter governs purpose.
2.  Architecture governs structure.
3.  Governance standards, policies, contracts, and schemas govern
    implementation/operation.
4.  Engines communicate through governed interfaces/artifacts.
5.  Engines do not depend on private directories of other engines.
6.  Durable enterprise state belongs to the Research Nexus.
7.  Task Management coordinates without absorbing domain responsibility.
8.  Research and Decision Intelligence remain distinct.
9.  Presentation may communicate decisions but not bypass Decision
    Intelligence.
10. Storage backends may change without semantic change.
11. Integrations translate external information but do not define MTS
    meaning.
12. Runtime optimization may not bypass provenance, lifecycle, or
    durable-publication requirements.
13. New components are classified before implementation.

## 22. Repository and Data-Plane Separation

The Git repository contains software/system-definition assets. The
Research Nexus data plane is external.

`Momentum-Trading-System_v2/` contains Charter, Architecture,
Governance, Core, Engines, Tests, Control Center, and Documentation.

`MTS_RESEARCH_NEXUS_ROOT` contains durable data, evidence, findings,
knowledge, research, decisions, outcomes, applied policies, provenance,
and catalogs. Its exact physical tree is technical design.

## 23. Configuration and Path Resolution

Production code must not embed developer-specific absolute paths.
Configuration resolves repository root, Research Nexus root,
cache/runtime root, and environment/provider configuration. A path
locates a representation; it does not define artifact meaning or
identity.

## 24. Observability and Audit

MTS must answer what is running/queued/completed/failed; what artifacts
were produced; what inputs, producer/version, validation, policy,
publication, dependencies, backup status, and lifecycle rationale apply.
Operational logs may be transient; material audit/provenance records are
durable when needed for explanation or reproducibility.

## 25. Human Control and Automation

Automation authority is explicit and governed. Automated research does
not automatically grant authority to promote knowledge, change
governance/architecture, execute live trades, increase risk, or delete
permanent artifacts. The architecture supports increasing automation
without requiring removal of human control boundaries.

## 26. Architectural Conformance

A conforming component respects the Charter and responsibility
boundaries; communicates by governed contracts; preserves
identity/provenance; assigns metadata/storage/retention classes; keeps
Nexus data out of Git; uses Nexus durable state; preserves backend
independence; fails safely; respects lifecycle/authority; and supports
reproducibility appropriate to its role.

## 27. Companion Architecture

This document governs the system-wide model. Detailed canonical
documents should subsequently define: -
`Architecture/RESEARCH_NEXUS_ARCHITECTURE.md` -
`Architecture/ENGINE_ARCHITECTURE.md` -
`Architecture/DATA_ARCHITECTURE.md` -
`Architecture/DECISION_ARCHITECTURE.md`

## 28. Closing Principle

MTS favors explicit identity, authority, provenance, lifecycle, stable
contracts, and replaceable implementations.

> **Engines perform work. The Research Nexus remembers and connects. The
> Task Manager schedules, routes, and supervises. Governance defines the rules. Evidence determines
> what MTS should believe.**
