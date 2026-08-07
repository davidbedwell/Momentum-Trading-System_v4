# Momentum Trading System — Research Nexus Architecture

**Status:** Canonical
**Authority:** Governing Research Nexus architecture subordinate to `CHARTER.md` and `Architecture/SYSTEM_ARCHITECTURE.md`

---

## 1. Purpose

This document defines the enduring architecture of the MTS Research Nexus.

The Research Nexus is the canonical persistent system of record and exchange for MTS data, evidence, findings, knowledge, research state, decisions, outcomes, policies, and provenance.

This document defines:

- the Nexus responsibility boundary;
- the logical artifact model;
- identity and metadata requirements;
- persistence and retention classes;
- canonical publication and retrieval behavior;
- provenance and relationship requirements;
- State of Knowledge representation;
- lifecycle and promotion concepts;
- backup and recoverability requirements;
- cache and retirement behavior;
- engine and Task Manager interaction;
- portability and deployment independence;
- adoption rules for imported or preexisting assets.

This document intentionally does **not** prescribe specific databases, directory trees, object-store products, serialization formats, or physical storage devices. Those choices belong in technical design.

---

## 2. Governing Principle

> **The Research Nexus remembers and connects. Engines perform work. The Task Manager schedules, routes, and supervises work.**

The Research Nexus does not conduct scientific research merely by storing research artifacts.

It does not make investment decisions merely by storing decisions.

It does not become authoritative because it contains an artifact.

Its purpose is to preserve governed state, identity, provenance, relationships, lifecycle, discovery, and reproducibility across the entire MTS system.

The Research Nexus SHALL be designed for the known mature MTS operating
model from the beginning: server deployment, concurrent workers,
scheduled and autonomous tasks, live-market activity, large durable
datasets, high-volume provenance, and scalable retrieval.

A smaller initial deployment may use simpler physical mechanisms, but
the logical contracts must be the same contracts intended for the
mature system.

---

## 3. Architectural Role

The Research Nexus is the semantic system of record for durable MTS scientific and operational state.

The Nexus is responsible for durable MTS state across the research and decision lifecycle.

Conceptually:

```text
External Sources
      ↓
Data Intake
      ↓
Research Nexus
      ↓
Discovery
      ↓
Research Nexus
      ↓
Research Director
      ↓
Research Nexus
      ↓
Decision / Market Discovery
      ↓
Research Nexus
      ↓
Outcomes
      ↓
Learning & Governance
      ↓
Research Nexus
```

The same Nexus connects historical research, live-market interpretation, decisions, outcomes, and future learning.

No individual engine owns this durable state.

---

## 4. What the Research Nexus Is Not

The Research Nexus is not:

- a Git repository;
- an engine;
- a single directory tree;
- a dumping ground for all runtime files;
- a cache;
- a substitute for governance;
- a substitute for scientific validation;
- a mechanism for declaring stored conclusions true;
- a storage technology;
- a vendor product;
- a private implementation detail of one engine.

The Nexus may use filesystems, databases, object stores, indexes, catalogs, caches, or future technologies internally, but those are implementation choices.

---

## 5. Logical Asset Model

The Research Nexus manages **logical artifacts**, not merely files.

An artifact is a governed MTS object whose identity and meaning persist independently of physical representation.

One logical artifact may have one or more physical representations.

Examples include:

- a Parquet file;
- a JSON descriptor;
- a database record;
- an object-store blob;
- a report;
- a model artifact;
- a research plan;
- a knowledge object.

Moving or re-encoding an artifact does not, by itself, create a new logical artifact.

A materially new dataset, finding, conclusion, policy, decision, or outcome does require a new logical identity.

---

## 6. Core Artifact Families

The Nexus must support an extensible set of semantic artifact families.

Initial families include:

### 6.1 Source and Data

External or internally accepted data used as the observational basis of MTS.

Examples:

- raw vendor data;
- normalized market history;
- fundamentals;
- options data;
- institutional activity;
- market context;
- reference datasets;
- accepted feature datasets.

### 6.2 Observations and Measurements

Direct or deterministic measurements derived from source data.

Examples:

- OHLCV measurements;
- volatility measures;
- relative volume;
- indicator values;
- event observations;
- feature values.

Observations and measurements are not automatically evidence.

### 6.3 Evidence

Governed analytical material that bears on a research question or claim.

Evidence may support, contradict, qualify, or fail to resolve a hypothesis.

### 6.4 Findings

Reproducible analytical conclusions produced from evidence.

Findings may describe:

- relationships;
- conditional behavior;
- interactions;
- temporal effects;
- regime dependencies;
- contradictions;
- absence of effect;
- instability;
- insufficient evidence.

A finding is not automatically canonical knowledge.

### 6.5 Knowledge

Governed evidence-supported conclusions that have passed the required promotion criteria for their lifecycle state.

Knowledge may be:

- candidate;
- validated;
- canonical;
- constrained;
- contradicted;
- superseded;
- retired.

### 6.6 Research State

State required to reproduce or continue scientific inquiry.

Examples:

- research questions;
- research plans;
- campaigns;
- hypotheses;
- unresolved dependencies;
- missing-tool reports;
- conclusions;
- follow-up requests.

### 6.7 Task and Execution State

Governed state required to schedule, recover, audit, or relate MTS work.

Examples:

- task requests;
- required capabilities;
- task dependencies;
- priority;
- eligibility state;
- assigned worker identity;
- attempts;
- failure records;
- completion records;
- result references.

Durable task state belongs in the Research Nexus when it is required
for recovery, provenance, or downstream dependency resolution.

Purely reconstructable scheduler internals may remain transient.


### 6.8 Decisions

Governed records of Decision Intelligence output.

A decision record should preserve the knowledge, evidence, current state, policy, model/engine versions, constraints, and reasoning references that materially influenced it.

### 6.9 Outcomes

Observed real-world results following decisions or monitored opportunities.

Outcomes enable learning, evaluation, calibration, and knowledge re-assessment.

### 6.10 Policies

Versioned operational policies actually applied by MTS.

Governance authors and controls policy.

The Research Nexus preserves the operational policy versions used so historical research and decisions can be reconstructed exactly.

### 6.11 Provenance and Audit

Durable lineage, validation, lifecycle, execution, backup, migration, and governance records needed to explain or reproduce material system behavior.

---

## 7. Mandatory Artifact Metadata

Every governed durable Nexus artifact must possess sufficient metadata to identify, interpret, relate, protect, discover, reproduce, and retire it.

Required or inheritable metadata includes, as applicable:

```text
artifact_id
artifact_version
artifact_type
schema_id
schema_version
created_at
producer
provenance
lifecycle_state
persistence_class
retention_class
backup_requirement
tags
```

Exact field names and required combinations belong in governed schemas.

### 7.1 Identity Must Be Stable

Artifact identity must not depend on:

- filename;
- folder;
- computer name;
- storage device;
- absolute path;
- database row position;
- engine-private directory.

### 7.2 Metadata Is Not Optional Decoration

Metadata drives:

- discovery;
- retention;
- backup;
- lifecycle;
- dependency analysis;
- deletion eligibility;
- lineage;
- promotion;
- audit;
- reproducibility.

MTS must not depend on a human recognizing what an unlabeled file probably means.

### 7.3 Controlled Fields and Flexible Tags

Controlled fields use governed values.

Examples:

- artifact type;
- lifecycle state;
- persistence class;
- retention class;
- validation state.

Free-form or extensible tags may aid search and topical discovery.

Examples:

- ticker;
- feature;
- event family;
- market regime;
- strategy concept;
- research topic.

Tags never replace governed classification.

---

## 8. Relationship and Provenance Graph

Material relationships between governed MTS identities must be explicit.

The Nexus must be able to represent relationships such as:

```text
DERIVED_FROM
SUPPORTS
CONTRADICTS
SUPERSEDES
INVALIDATES
DEPENDS_ON
ANSWERS
TESTS
GENERATED_BY
REQUESTED_BY
USED_IN_DECISION
PRODUCED_OUTCOME
APPLIES_TO
REQUIRES_CAPABILITY
```

The relationship vocabulary is extensible but governed.

The Nexus must support both upstream and downstream lineage.

For any material artifact, MTS should be able to answer:

- What produced this?
- What source data was used?
- What evidence supports it?
- What contradicts it?
- What research question did it address?
- What policy governed it?
- What decisions used it?
- What outcomes followed?
- What later artifact superseded or constrained it?

---

## 9. Three Persistence Classes

The Research Nexus architecture follows the system-wide three-class persistence model.

### 9.1 Class I — Source-Controlled System Assets

These define the software and governance of MTS.

Canonical home: Git repository.

Examples:

- source code;
- architecture;
- standards;
- contracts;
- schemas;
- authored governance policies;
- tests;
- configuration templates.

These do not become Nexus payloads merely because Nexus operations reference them.

A Nexus artifact may record the Git commit, content hash, schema identifier, or policy version that governed an operation.

### 9.2 Class II — Durable Research Nexus Assets

These are the durable observational, research, knowledge, decision, outcome, policy, and provenance assets of MTS.

Canonical home: Research Nexus.

Git: prohibited except small deliberate fixtures or examples.

Independent backup: required according to policy.

Class II has two retention levels.

#### Semi-Permanent

Retained while scientifically, operationally, or reproducibly useful.

Examples:

- accepted raw source data;
- normalized datasets;
- evidence underlying retained findings;
- completed campaigns;
- intermediate scientific assets needed for reproducibility;
- expensive-to-reacquire source history.

#### Permanent

Preserved as durable intellectual, decision, or governance history.

Examples:

- canonical knowledge;
- material supporting findings;
- critical provenance;
- promotion/supersession/retirement history;
- material decisions;
- realized outcomes;
- critical research conclusions;
- operational policy versions governing material actions.

Retirement from active retrieval does not imply physical deletion.

### 9.3 Class III — Transient / Cached Working Data

These are temporary or reproducible operational artifacts.

Examples:

- scratch;
- staging;
- query materializations;
- decompressed working copies;
- live buffers;
- intermediate calculations;
- temporary engine context;
- runtime queues;
- test caches.

Class III is not Git-tracked and is normally not backed up.

Deletion is policy-driven.

---

## 10. Lifecycle Model

Lifecycle state describes where an artifact stands in its governed existence.

Persistence class and lifecycle state are separate concepts.

Illustrative durable lifecycle states may include:

```text
INGESTED
VALIDATED
PUBLISHED
CANDIDATE
PROMOTED
CANONICAL
CONSTRAINED
CONTRADICTED
SUPERSEDED
RETIRED
ARCHIVED
```

Not every artifact type uses every state.

Exact legal transitions belong in lifecycle standards and schemas.

### 10.1 Publication Is Not Promotion

Publication means an artifact has entered governed Nexus state.

Promotion means an artifact has met the objective criteria required to advance in semantic authority or lifecycle.

A published finding is not automatically knowledge.

A published knowledge candidate is not automatically canonical knowledge.

When policy requires independent Accountability review, the Nexus may record a higher knowledge-authority transition only when a valid applicable Knowledge Promotion gate verdict is present.

### 10.2 Retirement Is Not Erasure

Retirement normally means an artifact is removed from normal active use.

Historical identity, provenance, relationships, and material evidence should remain available when required for audit, reproducibility, or learning.

---

## 11. Knowledge Promotion Architecture

Knowledge formation must preserve the distinction:

```text
Observation
    ↓
Evidence
    ↓
Finding
    ↓
Knowledge Candidate
    ↓
Validated Knowledge
    ↓
Canonical Knowledge
```

Promotion must be based on governed objective criteria rather than an engine's confidence language or unsupported concept of "trust."

Potential measurable criteria may include:

- reproducibility;
- sample adequacy;
- independent validation;
- generalization;
- stability;
- contradiction rate;
- regime applicability;
- economic value;
- outcome performance;
- evidence freshness;
- dependency integrity.

The architecture does not prescribe numerical thresholds.

Thresholds belong in governed policy and may evolve with evidence.

---

## 12. State of Knowledge Architecture

The Research Nexus is the canonical body of durable MTS scientific and operational state.

The State of Knowledge (SoK) is a governed point-in-time logical view assembled from the subset of canonical knowledge relevant to a defined subject and use. The SoK is not a single file or table, and it is not synonymous with everything stored in the Nexus.

For Decision use, a SoK view should be capable of returning:

- current applicable canonical knowledge;
- applicability conditions;
- uncertainty or confidence qualification;
- validation context;
- recency;
- decision-eligibility state;
- material limitations;
- provenance references needed to explain the knowledge.

Research additionally operates over **Active Research State**, which may contain:

- unresolved contradictory evidence;
- open questions;
- hypotheses;
- research plans;
- anomalies;
- known tooling/data gaps;
- temporary research working material.

Active Research State is not automatically part of the Decision SoK.

The Nexus may also preserve **Historical Research Lineage** sufficient for reproducibility, audit, and learning. This does not require permanent retention of every contradictory, negative, duplicate, or reproducible intermediate artifact.

Contradictory working material is default-to-expire after its Research Plan is resolved. Durable retention requires objective justification. When a contradiction materially changes knowledge, applicability, uncertainty, decision eligibility, supersession, retirement, or a material historical Decision, MTS should normally preserve the minimum necessary evidence and a compact durable resolution record.

The Research Director may query canonical knowledge, Active Research State, and justified historical lineage to determine what is known and what remains unanswered.

The Decision Engine normally consumes the scoped SoK rather than unresolved research debris.

Learning & Governance uses Decisions, Outcomes, current knowledge, and justified lineage to evaluate whether knowledge remains useful.


---


### Active Utility and Retrieval-Tier Architecture

The Nexus must represent active utility separately from lifecycle state,
scientific status, Decision eligibility, and physical retention.

Where implemented, active-utility metadata should be capable of representing:

```text
last_relevant_access
last_material_decision_use
last_material_research_use
decision_use_count
material_decision_use_count
eligible_opportunities_since_use
applicable_context_count
incremental_utility_evidence
retrieval_tier
utility_review_status
```

These fields are operational evidence for retrieval and lifecycle review. They
are not themselves scientific conclusions.

A maintenance read, backup, migration, integrity check, index scan, or other
technical touch must not be recorded as relevant scientific/Decision use.

Non-use should be interpreted against applicable-opportunity exposure where
measurable. Knowledge intended for rare conditions must not be demoted merely
because those conditions have not occurred.

The Nexus may maintain retrieval treatment such as:

```text
HOT
NORMAL
COLD
```

Retrieval tier is not lifecycle state and is not archival state.

`COLD` means valid canonical knowledge is kept outside the ordinary hot
retrieval path while remaining discoverable through governed targeted
retrieval. `ARCHIVE` remains a retention/storage-implementation condition governed separately.

Retrieval optimization must preserve a path for context-triggered discovery of
cold knowledge so that low rank does not become a self-fulfilling reason for
permanent non-use.

## 13. Discovery and Retrieval

The Nexus must support discovery by logical meaning rather than only path lookup.

Clients should be able to query by combinations of:

- artifact identity;
- artifact type/family;
- lifecycle state;
- retention class;
- producer;
- schema;
- ticker/instrument;
- date/time;
- campaign;
- research plan;
- feature;
- event family;
- tags;
- upstream/downstream relationships;
- validation status;
- knowledge applicability;
- decision/outcome relationship.

Performance optimizations may introduce indexes or cached views, but those must not become alternate sources of truth.

---

## 14. Publication Contract

Durable publication to the Nexus must be atomic from the perspective of clients.

A publication is not considered complete until required conditions succeed.

At minimum, durable publication should be capable of verifying:

1. valid identity;
2. valid schema;
3. required metadata;
4. content integrity;
5. provenance completeness appropriate to type;
6. allowed lifecycle transition;
7. required relationships;
8. successful durable write;
9. catalog/registry registration;
10. post-write verification.

If publication fails, clients must not observe a partially promoted artifact as complete.

Exact transactional mechanisms belong in technical design.

---

## 15. Immutability and Correction

Promoted or canonical durable artifacts should be immutable where practical.

Correction should normally create:

- a new representation version;
- a new artifact version;
- a superseding artifact;
- or a governed correction record,

depending on the semantics of the change.

Historical mutation that destroys provenance is prohibited.

---

## 16. Cache and Materialization Architecture

The Nexus may expose or support fast caches and materialized views.

Caches exist for performance, not semantic authority.

A cached copy may be deleted only when policy permits.

Deletion eligibility must be based on metadata, not folder age alone.

At minimum, managed cache retirement must consider:

```text
durable publication required?
        ↓
if yes: durable copy verified?
        ↓
active dependency?
        ↓
open research dependency?
        ↓
decision/runtime dependency?
        ↓
retention policy satisfied?
        ↓
deletion eligible
```

A cache object that becomes scientifically valuable must be durably published or reclassified before the cache copy is treated as protected.

---

## 17. Backup Architecture

Backup is a governed Nexus responsibility for Class II assets.

Backup policy must be metadata-driven.

The system should be able to determine:

- whether backup is required;
- destination class;
- last successful backup;
- verification status;
- backup content hash or equivalent integrity proof;
- recovery source;
- retention requirement.

A copy operation without verification is not considered a completed governed backup.

### 17.1 Backup and Primary Storage Are Separate

The primary Research Nexus may initially reside on directly attached storage and later on a server.

Backup must remain logically independent of the primary storage.

The failure of the primary backend must not make the only backup inaccessible for the same reason.

### 17.2 Rebuildable Data

Not every large dataset requires permanent independent backup.

Policy may classify data as rebuildable when:

- the original provider remains a reliable recovery source;
- deterministic regeneration is possible;
- reacquisition cost and time are acceptable.

Irreplaceable research knowledge, provenance, decisions, and outcomes require stronger protection.

---

## 18. Physical Deployment Independence

The Nexus logical architecture must operate without engine changes across physical deployments.

Examples:

```text
Development:
MTS software → local computer
Research Nexus → external attached storage

Future:
MTS software → server
Research Nexus → server-managed storage / object storage
```

The deployment mechanism may change.

The following must not:

- artifact identity;
- semantic type;
- provenance;
- lifecycle;
- retention rules;
- engine contracts;
- policy semantics;
- client behavior.

### 18.1 Root Configuration

Filesystem-backed deployments may expose a configured root such as:

```text
MTS_RESEARCH_NEXUS_ROOT
```

No production component may infer the Nexus root from Git location.

No component may silently fall back to a second Nexus when the configured Nexus is unavailable.

Unavailable durable storage must fail explicitly or use a separately governed durable queue if architecture later authorizes one.

---

## 19. Software / Data Plane Boundary

The Research Nexus has two distinct architectural planes.

### Software Plane

Lives in the Git repository.

Examples:

- Nexus APIs;
- storage adapters;
- schemas;
- catalog services;
- lifecycle services;
- backup services;
- validation code;
- tests.

### Data Plane

Lives outside the Git repository.

Examples:

- source datasets;
- evidence;
- findings;
- knowledge;
- research state;
- decisions;
- outcomes;
- operational policy snapshots;
- provenance;
- catalogs containing operational state.

The data plane must not be a required Python import location.

Moving the data plane must not require moving or editing application source code.

---

## 20. Interaction with Engines

Engines interact with the Research Nexus through governed interfaces.

### Data Intake

Publishes accepted data, observations, validation records, and provenance.

### Discovery

Retrieves governed inputs and publishes evidence and findings.

### Research Director

Retrieves SoK and research artifacts; publishes questions, proposed Research
Plans, conclusions, research needs, and Knowledge Candidates.

### Accountability

Retrieves proposed Research Plans, Knowledge Candidates, applicable policy,
validation/provenance state, and related evidence; publishes governed Research
Admission and Knowledge Promotion verdicts.

Gate verdicts are durable governed artifacts when they authorize, limit, block,
or materially explain research execution or knowledge lifecycle state.

### Market Discovery

Publishes candidate opportunities, anomalies, live observations, and research-worthy phenomena when durable retention is appropriate.

### Decision Engine

Retrieves applicable knowledge/current state and publishes governed decisions and research needs.

### Learning & Governance

Retrieves knowledge, decisions, and outcomes and publishes lifecycle evaluations, promotion/degradation recommendations, contradictions, or governed state transitions according to authority.

No engine may bypass the Nexus for permanent exchange merely because direct filesystem access is easier.

---

## 21. Interaction with the Task Manager

The Task Manager is a first-class permanent client and coordination
peer of the Research Nexus.

The Nexus preserves governed task and execution state when durability,
recovery, provenance, or dependency tracking requires it.

The Task Manager remains responsible for:

- scheduling;
- routing;
- capability matching;
- worker selection;
- concurrency;
- resource limits;
- retries;
- interruption recovery;
- task status;
- execution supervision.

The Research Nexus remains responsible for:

- durable task identity when required;
- task dependencies represented as governed relationships;
- durable task-request artifacts;
- durable execution provenance;
- durable result artifacts;
- dependency and lineage discoverability;
- completed/failed task history when retention policy requires it.

The Research Nexus does not choose a worker merely because a task is
stored.

The Task Manager does not acquire scientific authority merely because
it schedules a task.

A mature deployment may use an event stream, queue, database-backed
work table, message broker, or distributed scheduler. The initial
implementation may be simpler. These are technical mechanisms beneath
the same permanent architectural boundary.

Task state required for crash recovery must survive Task Manager
process interruption. Transient scheduling optimizations may remain
Class III when they can be reconstructed from durable task state.

---

## 22. Policy Preservation

Governance policies have their authored canonical form in the Git repository.

When an operational policy materially governs research, knowledge lifecycle, decision behavior, retention, risk, or deletion, the Nexus must preserve enough immutable information to reproduce which policy was applied.

This may include:

- policy identity;
- policy revision or Git commit;
- content hash;
- effective date;
- resolved operational parameters;
- applicability scope.

Historical decisions must remain interpretable even after the authored policy changes.

---

## 23. Validation

The Nexus validates structural and storage integrity.

It may enforce:

- schema validity;
- required metadata;
- identity uniqueness;
- referential integrity;
- permitted lifecycle transitions;
- content hash integrity;
- publication completeness.

Structural validity does not prove scientific validity.

Scientific validity belongs to the relevant scientific validation process.

The Nexus records validation results; it does not invent them.

---

## 24. Security and Write Authority

The Nexus must support explicit write authority.

Components should receive only the permissions necessary for their responsibilities.

Examples:

- an intake component may publish data but not promote knowledge;
- a Discovery component may publish findings but not alter prior canonical knowledge;
- a Decision component may publish decisions but not rewrite historical evidence;
- backup services may replicate artifacts but not change semantic lifecycle;
- migration utilities may write imported artifacts only under governed migration authority.

Exact authorization technology belongs in technical design.

---

## 25. Failure Semantics

The Nexus must fail explicitly and preserve integrity.

It must not:

- silently redirect durable writes to an unintended location;
- publish incomplete artifacts as complete;
- overwrite immutable canonical artifacts;
- lose provenance because a dependency is unavailable;
- delete data solely to recover disk space without lifecycle authority.

Failure states should be observable and auditable.

---

## 26. Adoption of Imported and Preexisting Assets

Assets entering the Research Nexus from outside the current governed workflow must be adopted by semantic meaning rather than by source location or physical structure.

### 26.1 Assets Eligible for Deliberate Adoption

Potential candidates include:

- source datasets whose meaning and provenance can be established;
- canonical evidence;
- reproducible findings;
- knowledge objects;
- research plans with continuing value;
- material contradiction-resolution lineage that satisfies retention criteria;
- material provenance;
- decision/outcome history that is valid and interpretable.

### 26.2 Assets Not Automatically Adopted

The following do not become canonical merely because they exist:

- caches;
- scratch output;
- temporary proof-of-concept runs;
- duplicated publications;
- unsupported compatibility artifacts;
- obsolete schemas;
- private filesystem assumptions;
- patch bundles as runtime dependencies;
- unclassified files;
- artifacts whose meaning or provenance cannot be established.

### 26.3 Adoption Process

Adoption should proceed:

```text
Inventory
   ↓
Classify
   ↓
Verify source integrity
   ↓
Map semantic type
   ↓
Assign governed identity/metadata
   ↓
Preserve source provenance
   ↓
Validate
   ↓
Publish to Research Nexus
   ↓
Verify durable publication
   ↓
Record adoption audit
```

Source location, filename, directory hierarchy, or prior component numbering must not determine canonical identity, routing, ownership, authority, or lifecycle.
---

## 27. Initial v2 Build Boundary

The first implementation should prove the architecture with the smallest useful vertical slice.

Recommended initial flow:

```text
AAPL raw source
    ↓
Data Intake
    ↓
Research Nexus
    ↓
Discovery
    ↓
Finding
    ↓
Research Nexus
    ↓
Research Director
    ↓
Next Question / Conclusion
```

The proof must demonstrate:

- external Nexus root;
- stable artifact identity;
- mandatory metadata;
- explicit provenance;
- schema validation;
- publish/retrieve;
- relationship traversal;
- persistence-class assignment;
- retention classification;
- backup classification;
- no dependency on source-specific physical paths;
- reproducibility.

Only after the core Nexus contract is proven should broader asset adoption begin.

---

## 28. Architectural Quality Attributes

The Research Nexus must continually support:

- durability;
- integrity;
- reliability;
- scalability;
- portability;
- backend independence;
- discoverability;
- auditability;
- recoverability;
- reproducibility;
- observability;
- maintainability;
- extensibility;
- security;
- performance appropriate to workload.

Performance optimizations must not silently weaken identity, provenance, validation, or lifecycle guarantees.

---

## 29. Technical Design Boundary

The following are intentionally deferred to a later Research Nexus Technical Design:

- exact physical directory structure;
- catalog database technology;
- object/blob layout;
- manifest format;
- serialization choices;
- indexing technology;
- query engine;
- cache implementation;
- storage adapter implementation;
- backup transport;
- checksumming implementation;
- replication implementation;
- locking/concurrency mechanics;
- deployment topology;
- local-vs-server configuration;
- performance tuning;
- operational tooling.

Architecture defines guarantees.

Technical design chooses mechanisms.

---

## 30. Conformance Requirements

A Research Nexus implementation conforms to this architecture when it:

1. provides canonical durable identity independent of physical location;
2. preserves governed metadata and provenance;
3. supports explicit relationships and lineage;
4. distinguishes semantic type from persistence class;
5. enforces the three-class storage model;
6. keeps Nexus data out of Git except deliberate fixtures;
7. supports semi-permanent and permanent durable retention;
8. protects Class II assets according to backup policy;
9. manages cache deletion through explicit eligibility;
10. supports publication, retrieval, discovery, lifecycle, audit, and recovery;
11. preserves backend independence;
12. does not require engines to know physical storage layout;
13. prevents silent fallback to an unintended Nexus;
14. preserves policy versions required for reproducibility;
15. supports the State of Knowledge model;
16. allows future artifact and engine types without redesigning the core architecture;
17. supports deliberate, auditable adoption of imported and preexisting assets;
18. fails without corrupting canonical state.

---

## 31. Companion Governance and Architecture

This architecture should be supported by unversioned canonical companion documents including:

```text
Architecture/SYSTEM_ARCHITECTURE.md
Architecture/ENGINE_ARCHITECTURE.md
Architecture/DATA_ARCHITECTURE.md
Architecture/DECISION_ARCHITECTURE.md

Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md

Governance/Contracts/
Governance/Schemas/
Governance/Policies/
```

The exact companion set may evolve as v2 is designed.

---

## 32. Closing Principle

The Research Nexus exists so MTS can accumulate capability without accumulating ambiguity.

It must always be possible to determine:

> **What is this artifact, where did it come from, what does it mean, what does it depend on, who used it, how long must it be kept, is it protected, and what happened because of it?**

If the system cannot answer those questions, the artifact is not adequately governed.
