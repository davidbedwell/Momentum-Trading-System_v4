# Momentum Trading System — Research Nexus Technical Design

**Status:** Initial Implementation Design  
**Authority:** Technical design subordinate to `CHARTER.md`, `Architecture/SYSTEM_ARCHITECTURE.md`, `Architecture/RESEARCH_NEXUS_ARCHITECTURE.md`, `Architecture/DATA_ARCHITECTURE.md`, and applicable Governance standards, policies, contracts, and schemas.  
**Implementation target:** Minimum durable Research Nexus vertical slice, designed to preserve the mature-system contracts.

---

## 1. Purpose

This document defines the initial technical mechanisms used to implement the canonical MTS Research Nexus without weakening or replacing its governing architecture.

The first implementation SHALL prove permanent Nexus semantics while keeping physical mechanisms replaceable. It is not intended to implement every future Nexus capability before the first end-to-end research flow can operate.

The initial implementation must support the canonical vertical slice:

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
Knowledge Management
    ↓
State of Knowledge / Active Research State
    ↓
Research Director
    ↓
Next Question / Conclusion
```

The implementation SHALL preserve the architectural rule:

> **The Research Nexus remembers and connects. Engines perform work. The Task Manager schedules, routes, and supervises work.**

---

## 2. Design Principles

The implementation SHALL follow these principles from its first usable version:

1. **Semantic identity is independent of physical location.**
2. **Engines use governed Nexus interfaces, not Nexus directory knowledge.**
3. **Durable publication is validated and atomic from the client perspective.**
4. **Published immutable content is never silently overwritten.**
5. **Provenance and relationships are first-class data.**
6. **Metadata, payload storage, and indexes are logically distinct.**
7. **The initial backend is replaceable without changing client contracts.**
8. **No silent fallback Nexus is permitted.**
9. **Class II data remains outside Git.**
10. **Core grows only where an immediate shared dependency exists.**
11. **Initial simplicity may reduce deployment complexity, not semantic rigor.**
12. **Concurrency safety is designed in even when an initial workload happens to execute serially.**
13. **Knowledge Management is a first-class Nexus subsystem, not engine-local storage or cleanup logic.**
14. **Raw analytical volume is not equivalent to knowledge; evidence must remain queryable without requiring wholesale materialization.**
15. **Scientific quality, decision utility, and access priority remain distinct governed dimensions.**
16. **Retrieval frequency may influence operational priority but SHALL NOT establish scientific validity.**

---

## 3. Initial Technical Architecture

The first Research Nexus implementation SHALL use three logical layers:

```text
Nexus Client/API
      ↓
Nexus Services
  ┌───────────────┬──────────────────────┐
  │ Core Artifact │ Knowledge Management │
  │ Services      │ Services             │
  └───────────────┴──────────────────────┘
      ↓
Storage Ports
   ↙         ↓         ↘
Catalog   Index Store   Payload Store
```

### 3.1 Nexus Client/API

The public interface used by engines and governed MTS services.

Initial operations:

```text
publish(...)
get(...)
query(...)
add_relationship(...)
get_relationships(...)
verify(...)
get_state_of_knowledge(...)
get_active_research_state(...)
query_evidence(...)
rank_knowledge(...)
```

Clients SHALL NOT receive or require knowledge of physical catalog rows, payload directories, SQLite row IDs, filesystem layouts, or backend-specific keys as semantic identity.

### 3.2 Nexus Services

The service layer SHALL coordinate:

- identity handling;
- schema validation;
- metadata validation;
- provenance validation;
- content hashing;
- publication conflict/idempotency checks;
- lifecycle checks required for initial artifact types;
- payload persistence;
- catalog registration;
- relationship registration;
- post-write verification;
- retrieval and governed query translation.

Knowledge Management SHALL be implemented as a first-class service boundary within the Nexus service layer. Its durable responsibilities include:

- knowledge identity and version lineage;
- evidence-to-claim synthesis records;
- scientific-status representation;
- contradiction state;
- applicability and recency state;
- knowledge promotion/demotion records when authorized by governance;
- State of Knowledge assembly;
- Active Research State assembly;
- knowledge ranking and retrieval-tier metadata;
- provenance from knowledge back to findings/evidence;
- archival/cold-retrieval eligibility signals;
- durable explanation of why a knowledge object is ranked, promoted, demoted, superseded, or retained.

Knowledge Management SHALL NOT independently invent scientific truth, bypass Accountability/governance gates, or convert usage frequency into scientific validity. Engines and governed authorities produce/evaluate research; the Nexus preserves, connects, indexes, and serves the resulting governed state.

### 3.3 Storage Ports

Storage behavior SHALL be expressed behind interfaces/protocols so physical mechanisms can later be replaced.

Initial ports:

```text
CatalogStore
IndexStore
PayloadStore
```

`IndexStore` is a permanent logical boundary even when its first implementation shares the same SQLite database as `CatalogStore`. It exists so evidence and knowledge can be queried selectively without requiring clients to load complete artifact payloads or million-row publications into memory.

The initial `IndexStore` SHALL support the vertical-slice retrieval predicates required for evidence, findings, knowledge, State of Knowledge, and Active Research State. Later implementations may move indexing to a server relational index, columnar query service, search engine, graph/index service, or other scalable backend without changing Nexus client contracts.

Future implementations may add specialized object-store, graph, cache, backup, or distributed transaction mechanisms without changing Nexus semantic contracts.

---

## 4. Initial Backend Selection

### 4.1 Catalog: SQLite

The initial durable catalog SHALL use **SQLite**.

Rationale:

- transactional behavior;
- referential constraints;
- indexes and governed querying;
- crash-resistant local persistence;
- mature Python support;
- no external database service required for the first Mac deployment;
- straightforward backup and inspection;
- suitable implementation of a replaceable `CatalogStore` port.

SQLite is an implementation mechanism, not MTS architecture. No engine or domain contract may depend upon SQLite-specific semantics.

The design SHALL avoid assumptions that prevent later migration to a server database.

### 4.2 Index Store: SQLite-Backed Governed Index

The initial `IndexStore` SHALL use SQLite-backed indexed tables or views colocated with the catalog where practical.

This implementation SHALL support selective retrieval of evidence and knowledge metadata without copying durable payloads into engine-private working directories.

Index records SHALL reference stable Nexus artifact identities and representation identities. Index rows are discovery/retrieval structures; they SHALL NOT become an alternate source of truth for artifact content.

The design SHALL permit later separation of `IndexStore` from the catalog database without changing the public Nexus API.

### 4.3 Payload Store: Filesystem-Backed Content Store

Initial artifact payloads SHALL be stored outside Git beneath the configured Research Nexus root using a filesystem-backed `PayloadStore`.

Payload addressing SHALL be derived from content integrity information and/or governed storage locators rather than artifact meaning.

The physical payload path SHALL NOT be the artifact identity.

A future object-store implementation must be substitutable behind the same storage port.

### 4.4 Serialization

Initial structured metadata and small structured payloads SHOULD use deterministic JSON where appropriate.

Large tabular datasets SHOULD use a format appropriate to the dataset contract, with Parquet preferred when governed schemas and dependencies support it.

Serialization format SHALL remain representation metadata and SHALL NOT define logical artifact identity.

---

## 5. Research Nexus Root

Production/development Nexus data SHALL reside outside the Git repository.

The primary root SHALL be supplied through governed configuration, initially using:

```text
MTS_RESEARCH_NEXUS_ROOT
```

The Nexus SHALL NOT infer durable storage from repository location.

If the configured root is missing, inaccessible, invalid, or unsafe, durable operations SHALL fail explicitly.

The implementation SHALL NOT silently create or redirect to a second Nexus.

Tests SHALL use isolated temporary Nexus roots.

---

## 6. Initial Physical Layout

The following layout is an implementation detail for the first filesystem backend:

```text
<MTS_RESEARCH_NEXUS_ROOT>/
    catalog/
        nexus.sqlite3
    objects/
        ... payload representations ...
    staging/
        ... incomplete publication material ...
    runtime/
        ... reconstructable runtime material ...
```

This tree SHALL NOT leak into engine contracts.

`catalog/` and durable `objects/` are Class II Nexus data where applicable.

`staging/` and `runtime/` are Class III unless explicitly promoted/reclassified through governed publication.

The exact internal sharding/layout of `objects/` may change without changing artifact identity.

---

## 7. Artifact Identity

The implementation SHALL use governed stable artifact identifiers independent of path and catalog row position.

The initial identity utility SHALL support opaque canonical IDs suitable for distributed/server operation. UUID-based identifiers are acceptable for the initial implementation unless an applicable governed schema requires another identity form.

Logical identity and content identity SHALL remain distinct:

```text
artifact_id   → identifies governed logical artifact/version semantics
content_hash  → proves representation content integrity
locator       → locates a physical representation
```

A changed physical locator SHALL NOT change `artifact_id`.

A materially new governed artifact SHALL receive identity according to the Identity Standard rather than reusing an old ID merely because filenames or subjects match.

---

## 8. Initial Artifact Envelope

Every initial durable publication SHALL carry a governed artifact envelope containing, as applicable:

```text
artifact_id
artifact_type
artifact_family
persistence_class
retention_class
lifecycle_state
created_at
producer
producer_version
schema_id
schema_version
content_hash
validation_status
backup_requirement
backup_status
source_refs
parent_refs
dependency_refs
campaign_id
research_plan_id
decision_id
policy_refs
supersedes
superseded_by
tags
provenance
```

Required combinations SHALL be determined by governed schemas/contracts, not merely by Python optional fields.

The initial implementation may support only the artifact families needed by the vertical slice, but its envelope and persistence model SHALL be extensible without redesign.

---

## 9. Catalog Model

The initial catalog SHOULD normalize durable state into at least these conceptual records:

```text
artifacts
representations
relationships
validation_records
publication_records
scientific_status_records
knowledge_rank_records
retrieval_tier_records
research_dependency_records
```

### 9.1 `artifacts`

Stores canonical logical metadata required for identity, classification, lifecycle, discovery, retention, and provenance references.

### 9.2 `representations`

Maps an artifact/version to one or more physical representations and records:

- locator;
- media/serialization type;
- content hash;
- size;
- creation time;
- verification state.

### 9.3 `relationships`

Stores explicit governed edges such as:

```text
DERIVED_FROM
SUPPORTED_BY
CONTRADICTED_BY
PRODUCED_BY
VALIDATED_BY
USED_BY
GOVERNED_BY
SUPERSEDES
SUPERSEDED_BY
PART_OF_CAMPAIGN
ANSWERS_QUESTION
REQUIRES
GENERATED_REQUEST
RESULTED_IN
EVALUATED_BY
```

Relationship vocabulary validation SHALL occur before durable insertion.

### 9.4 Validation and Publication Records

Material validation/publication facts SHALL be preserved sufficiently to explain whether an artifact was accepted and how publication completed.

### 9.5 Knowledge Management Records

The catalog SHALL be able to represent knowledge-management state without rewriting immutable historical artifacts. At minimum this includes separable records for:

```text
scientific_status
knowledge_quality inputs/results
decision_utility inputs/results
access_priority inputs/results
retrieval_tier
contradiction state
applicability state
recency state
promotion/demotion/gate references
open research dependencies
supersession/current-view status
```

Scientific status, lifecycle state, Decision eligibility, active utility, retrieval rank, retrieval tier, and physical retention state SHALL NOT be collapsed into one opaque status field.

Ranking/retrieval records SHALL identify the policy/model version and evidence inputs that produced them so ranking changes remain auditable without rewriting scientific history.

The catalog schema SHALL use explicit schema migrations rather than ad hoc mutation.

---

## 10. Publication Transaction

The first implementation SHALL treat publication as a coordinated transaction from the client's perspective.

Required sequence:

```text
receive publication request
        ↓
validate identity and authority-relevant structure
        ↓
validate schema + mandatory metadata
        ↓
validate provenance/required references
        ↓
serialize/stage payload
        ↓
compute content hash
        ↓
check existing identity/idempotency/conflict
        ↓
write durable payload representation
        ↓
open catalog transaction
        ↓
register artifact + representation + required relationships
        ↓
commit catalog transaction
        ↓
post-write payload/catalog verification
        ↓
return durable artifact reference
```

A client SHALL NOT observe an incomplete publication as successfully published.

### 10.1 Failure Handling

If failure occurs before catalog commit, staged/incomplete material SHALL remain non-canonical and eligible for cleanup/recovery.

If an exceptional failure occurs after catalog commit but before final verification response, retry/reconciliation SHALL determine whether publication already succeeded rather than blindly creating another artifact.

---

## 11. Idempotency and Immutable Publication

Publication SHALL distinguish:

### Same logical request, same immutable content

Return/reconcile to the existing durable publication where governed idempotency permits.

### Same immutable identity, conflicting content

Reject explicitly.

### Materially new artifact

Require a new governed identity/version/superseding artifact according to contract and lifecycle semantics.

No normal `publish()` operation may silently overwrite an existing immutable durable artifact.

---

## 12. Content Integrity

The initial implementation SHALL compute a cryptographic content hash for durable payload representations.

SHA-256 is the initial recommended mechanism.

Hash verification SHALL be available through Nexus verification services.

Content hash is an integrity mechanism, not a replacement for artifact identity or scientific validation.

---

## 13. Schema Validation

Schemas SHALL remain governed Class I assets in the repository under `Governance/Schemas/`.

The Nexus validation layer SHALL resolve schemas by governed schema identity/version rather than arbitrary engine-private paths.

Initial publication SHALL reject artifacts when:

- a required schema cannot be resolved;
- payload/envelope validation fails;
- required metadata is absent;
- prohibited/unknown controlled values are supplied where strict validation applies.

Schema validation proves structural conformance only. It does not establish scientific truth.

---

## 14. Provenance

Provenance SHALL be mandatory at the level required by artifact contract.

The initial vertical slice must be able to reconstruct at minimum:

```text
raw source
  ↓
Data Intake publication
  ↓
accepted/normalized artifact
  ↓
Discovery execution
  ↓
Finding
  ↓
Research Director use
  ↓
Next Question / Conclusion
```

Where material, provenance SHALL reference producer identity/version, input artifacts, schema/version, applicable configuration/policy references, and transformations/execution records available in the initial slice.

Provenance SHALL use stable artifact references rather than filesystem paths.

---

## 15. Relationship Traversal

The initial Nexus SHALL support both directions of relationship lookup.

Examples:

```text
What produced this finding?
What source data does it derive from?
What artifacts were derived from this dataset?
What finding answered this question?
What later artifact superseded this one?
```

Initial implementation may use indexed relational queries. The public interface SHALL not assume a graph database.

---

## 16. Query Model

Initial `query()` SHALL support governed criteria required by the vertical slice, including combinations of:

- artifact ID;
- artifact type/family;
- lifecycle state;
- persistence/retention class;
- producer;
- schema ID/version;
- ticker/instrument tag or governed field where applicable;
- campaign/research-plan reference;
- validation status;
- tags;
- creation time.

Query results SHALL return stable Nexus artifact references/envelopes, not expose raw database rows as the domain contract.

Query capability SHALL be extensible without breaking callers.

For potentially large evidence-bearing artifacts, `query_evidence()` SHALL support selective predicate-based retrieval through `IndexStore`. Callers SHALL NOT be required to retrieve the entire publication merely to inspect matching evidence.

The first implementation SHOULD support bounded result sets and deterministic pagination/cursors for query surfaces that can grow without practical bound.

---

## 17. Knowledge Management and State-of-Knowledge Services

Knowledge Management is a first-class Research Nexus subsystem.

The initial implementation SHALL establish permanent contracts for these distinct concepts:

```text
Evidence / Finding
      ↓ synthesis + provenance
Knowledge Candidate / Knowledge Artifact
      ↓ governed scientific assessment
Scientific Status
      ↓ governed promotion authority
Lifecycle / Decision Eligibility
      ↓ context-sensitive retrieval
State of Knowledge
```

The Nexus SHALL preserve the distinction between:

1. **Knowledge Quality** — evidence strength, replication, independent evidence, stability, coverage, contradiction burden, provenance sufficiency, and demonstrated generalization/applicability.
2. **Decision Utility** — observed predictive/economic contribution, material Decision use, outcome history, and incremental value when applicable.
3. **Access Priority** — relevance to the current question/context, recency, retrieval/use frequency, applicable-opportunity exposure, computational cost, and operational urgency.

These dimensions MAY contribute to a governed retrieval/ranking model, but SHALL remain inspectable separately. A high Access Priority SHALL NOT imply high Knowledge Quality. A rarely used artifact SHALL NOT be demoted scientifically solely because it is rarely accessed.

### 17.1 State of Knowledge

`get_state_of_knowledge(subject, context, as_of, ...)` SHALL assemble a governed logical view from canonical Nexus artifacts and relationships rather than rely on a monolithic knowledge file.

The initial SoK contract SHALL be capable of returning, where present:

- current applicable knowledge;
- scientific-status qualification;
- applicability conditions;
- recency qualification;
- Decision-eligibility state;
- material limitations;
- supporting/contradictory provenance references;
- supersession/current-view information;
- retrieval rank/tier metadata with explanation.

Ordinary Decision SoK retrieval SHALL prefer governed current knowledge and SHALL NOT indiscriminately load rejected hypotheses, unresolved research debris, or every atomic finding.

### 17.2 Active Research State

`get_active_research_state(...)` SHALL expose unresolved questions, contradictions, missing evidence, open research plans/jobs, known tooling/data gaps, and dependencies that remain scientifically or operationally active.

This state SHALL remain distinct from the ordinary Decision SoK so unfinished research does not masquerade as canonical knowledge.

### 17.3 Knowledge Ranking

The first implementation SHALL provide a deterministic, policy-versioned ranking interface even if the initial ranking model is intentionally simple.

Ranking inputs SHALL be explicit and auditable. Usage frequency alone SHALL never establish scientific validity.

Ranking SHALL NOT mutate knowledge content. A new ranking assessment creates new governed ranking state referencing the knowledge artifact and applicable policy/model version.

### 17.4 Retrieval Tiers and Retention

The Nexus SHALL support the operational retrieval concepts `HOT`, `NORMAL`, and `COLD` when the applicable governance vocabulary authorizes them.

Retrieval tier is not lifecycle state and is not scientific status.

`COLD` canonical knowledge remains governed and directly retrievable. Physical archival/deletion decisions remain subject to storage-retention policy, provenance/dependency checks, open research plans, unresolved evidence dependencies, legal/governance constraints, and reproducibility requirements.

The Nexus SHALL NOT retire or delete an artifact merely because it is low-ranked or infrequently used.

---

## 18. Lifecycle Scope for the First Slice

The first implementation SHALL support only lifecycle transitions immediately required by its artifact contracts while preserving a generic transition-validation mechanism.

Publication and promotion SHALL remain distinct.

The initial Nexus SHALL NOT independently decide that a Finding has become canonical Knowledge merely because the Finding is validly stored.

Future Accountability and Learning/Governance services will invoke governed lifecycle transitions under their respective authority.

---

## 19. Backup Classification

Every durable artifact SHALL carry explicit backup requirement/status metadata as required by governance.

The minimum vertical slice SHALL implement **classification and observability** of backup requirements even if automated backup transport is introduced during Nexus hardening rather than the first publication milestone.

No implementation may falsely mark a backup complete merely because a copy command was attempted.

Verified backup requires integrity verification according to policy.

---

## 20. Concurrency and Locking

The first implementation may operate under modest local concurrency, but it SHALL be safe for multiple execution instances.

SQLite SHALL use transaction boundaries and an appropriate journaling/locking configuration for concurrent readers and bounded writers.

Payload publication SHALL avoid shared mutable filenames and use unique staging locations followed by atomic filesystem operations where supported.

The implementation SHALL NOT depend on process-global mutable state for correctness.

Concurrency limits belong to Task Management/configuration rather than hard-coded Nexus worker ownership.

---

## 21. Crash Recovery

Publication design SHALL tolerate interruption between major publication stages.

On startup or maintenance invocation, the Nexus SHALL be capable of identifying abandoned staging material without treating it as canonical publication.

Committed catalog records SHALL be reconcilable with their referenced payload representations.

Missing or hash-invalid durable payloads SHALL surface as integrity failures; the Nexus SHALL not silently regenerate or redirect them unless a governed recovery mechanism explicitly authorizes it.

---

## 22. Configuration

Initial Nexus configuration SHALL be provided through the canonical MTS configuration layer as it is implemented.

At minimum the Nexus needs:

```text
research_nexus_root
catalog_backend
payload_backend
runtime/staging role
validation/schema location or resolver
```

Deployment values SHALL not be embedded in engine code.

Effective material configuration SHOULD be hashable/snapshot-capable for provenance.

Tests SHALL prove operation independent of current working directory and repository relocation.

---

## 23. Python Package Boundary

Initial implementation target:

```text
Core/research_nexus/
    __init__.py
    api.py
    models.py
    errors.py
    identity.py
    validation.py
    publication.py
    query.py
    relationships.py
    integrity.py
    knowledge.py
    state_of_knowledge.py
    ranking.py
    research_state.py
    config.py
    storage/
        __init__.py
        catalog.py
        index.py
        payload.py
        sqlite_catalog.py
        sqlite_index.py
        filesystem_payload.py
```

This is a technical starting structure, not a permanent architectural directory contract.

Responsibilities SHALL remain separated enough that backend implementations can be replaced without rewriting Nexus clients.

Shared mechanisms that become independently useful across multiple MTS components may later move into appropriate `Core/` packages under governed refactoring.

---

## 24. Error Model

Nexus operations SHALL fail with explicit typed errors rather than ambiguous booleans or silent fallback.

Initial error families SHOULD distinguish:

```text
ConfigurationError
ValidationError
SchemaResolutionError
IdentityConflictError
PublicationConflictError
RelationshipError
ArtifactNotFoundError
StorageUnavailableError
IntegrityError
LifecycleError
KnowledgeStateError
RankingError
ResearchDependencyError
AuthorizationError
```

Error details SHALL avoid exposing secrets while preserving sufficient diagnostic/audit context.

---

## 25. Initial Test Architecture

Tests SHALL be implemented concurrently with production code.

Initial test groups:

### Configuration

- missing Nexus root;
- inaccessible/invalid root;
- CWD independence;
- Nexus relocation without identity change;
- no silent fallback.

### Publication

- valid publication;
- required metadata rejection;
- schema rejection;
- missing provenance rejection;
- successful post-write verification;
- incomplete publication not visible.

### Identity and Immutability

- stable identity independent of path;
- idempotent same-content resubmission;
- conflicting immutable publication rejection;
- physical relocation preserves logical identity.

### Relationships

- valid relationship creation;
- invalid vocabulary rejection;
- upstream traversal;
- downstream traversal;
- missing endpoint handling.

### Integrity

- correct hash recorded;
- corrupted payload detected;
- missing payload detected.

### Lifecycle/Classification

- persistence class validation;
- retention class validation;
- publication distinct from promotion;
- prohibited transition rejection for implemented transitions.

### Knowledge Management / Retrieval

- selective evidence retrieval does not require full payload materialization;
- deterministic bounded evidence query/pagination;
- SoK excludes unfinished research debris from ordinary Decision retrieval;
- Active Research State exposes unresolved questions/dependencies;
- Knowledge Quality, Decision Utility, and Access Priority remain separately inspectable;
- usage frequency alone cannot alter scientific validity;
- ranking is deterministic for the same inputs/policy version;
- ranking changes do not rewrite knowledge content/history;
- `HOT`/`NORMAL`/`COLD` do not mutate lifecycle/scientific status;
- `COLD` canonical knowledge remains directly retrievable;
- open research plans or unresolved dependencies block unsafe retirement/deletion.

### Concurrency/Recovery

- independent publication staging;
- bounded concurrent publication safety;
- abandoned staging does not become canonical;
- retry after ambiguous completion reconciles rather than duplicates.

---

## 26. First Vertical-Slice Artifact Set

Do not implement every future MTS artifact type initially.

Implement the minimum governed schemas/contracts required to prove:

```text
Source Dataset / Raw Source Reference
Accepted or Normalized Dataset
Finding
Knowledge Candidate or minimal Knowledge Artifact
Scientific/Ranking Assessment required for the slice
State of Knowledge projection
Active Research State / Research Question
Research Conclusion / Follow-up Question
Relationship / Provenance records
```

Exact names SHALL follow the existing governed contracts/schemas. If a required contract/schema is absent, it SHALL be created under Governance before production code invents an undocumented representation.

---

## 27. First Acceptance Test

The Nexus foundation is not accepted merely because unit tests pass.

The first system acceptance test SHALL execute one deliberately small AAPL research path and demonstrate:

1. source artifact publication;
2. durable retrieval by identity;
3. governed query discovery;
4. Data Intake output publication;
5. provenance from intake output to source;
6. Discovery consumption by artifact reference;
7. Finding publication;
8. Finding-to-input relationship traversal;
9. selective evidence/Finding retrieval through governed index interfaces;
10. minimal Knowledge Management synthesis/assessment for the Finding;
11. assembly and retrieval of a State of Knowledge view;
12. separate retrieval of Active Research State where unresolved work exists;
13. Research Director retrieval through Nexus interfaces rather than private files;
14. publication of a next question or conclusion;
15. restart of the process;
16. successful retrieval, SoK reconstruction, and lineage traversal after restart;
17. identical logical identities despite clients having no knowledge of payload paths;
18. schema and integrity verification;
19. explicit persistence/retention/backup classifications;
20. proof that low access frequency cannot silently invalidate knowledge or trigger unsafe deletion.

This test SHALL use the real Nexus interfaces, not direct fixture-directory coupling.

---

## 28. Explicitly Deferred Capabilities

The following SHALL NOT block the minimum vertical slice unless implementation proves one is immediately necessary:

- distributed database deployment;
- remote object storage;
- graph database;
- full-text/vector search;
- high-volume market streaming;
- generalized event bus;
- advanced/adaptive cache ranking beyond the governed minimum ranking interface;
- precomputed or fully materialized SoK acceleration beyond logical SoK assembly;
- autonomous knowledge promotion/demotion without the required governance/Accountability gates;
- advanced learned ranking models beyond the deterministic initial policy;
- full backup transport/replication system;
- multi-node locking;
- production authentication infrastructure;
- large-scale data migration;
- broad adoption of v1 assets;
- speculative performance optimization.

Deferral does not remove the governing architectural requirement. Interfaces must avoid preventing these capabilities later.

---

## 29. Implementation Sequence

Development SHALL proceed in this order unless a discovered dependency requires an explicitly documented adjustment:

```text
1. Confirm/create minimum governed contracts and schemas
2. Implement Nexus configuration/root resolution
3. Implement artifact envelope models + identity
4. Define CatalogStore, IndexStore, and PayloadStore ports
5. Implement filesystem PayloadStore
6. Implement SQLite CatalogStore + migrations
7. Implement SQLite-backed IndexStore + bounded query/pagination
8. Implement schema/metadata/provenance validation
9. Implement transactional publication coordinator
10. Implement get/query + selective evidence retrieval
11. Implement relationships + traversal
12. Implement integrity verification
13. Implement idempotency/conflict behavior
14. Implement minimum Knowledge Management records/services
15. Implement logical SoK + Active Research State assembly
16. Implement deterministic three-dimension knowledge ranking interface
17. Implement retrieval-tier metadata without lifecycle conflation
18. Implement recovery/reconciliation behavior
19. Complete Nexus conformance tests
20. Run AAPL Nexus-only acceptance path
21. Add the minimum Data Intake adapter
22. Add the minimum Discovery adapter
23. Add the minimum Research Director adapter
24. Run full AAPL vertical slice through Knowledge Management/SoK
25. Audit against architecture/governance and v1 regression lessons
26. Commit/freeze the proven Nexus contract
27. Begin Nexus hardening before high-volume producers
```

This sequence intentionally builds permanent infrastructure through a narrow end-to-end use case rather than constructing speculative breadth.

---

## 30. Definition of Done — Minimum Durable Nexus

The minimum durable Nexus is complete when all of the following are true:

- durable Nexus root is external to Git;
- clients are backend/path independent;
- governed artifacts have stable identity;
- required metadata is enforced;
- governed schemas are enforced;
- provenance is explicit;
- payload content integrity is verifiable;
- publication is client-atomic;
- immutable publication conflicts fail closed;
- idempotent retries do not duplicate canonical state;
- artifacts can be retrieved by identity/version semantics required by contracts;
- governed query works for the initial slice;
- relationships can be traversed upstream and downstream;
- persistence/retention/backup classification is recorded;
- restart does not lose canonical state;
- backend relocation does not alter semantic identity;
- failures do not silently create alternate canonical state;
- an IndexStore contract supports selective evidence/knowledge retrieval without full publication materialization;
- Knowledge Management is available as a Nexus service rather than engine-private state;
- State of Knowledge and Active Research State are separately retrievable;
- Knowledge Quality, Decision Utility, and Access Priority remain distinct and auditable;
- ranking is policy/model versioned and does not rewrite scientific history;
- retrieval tier is distinct from lifecycle/scientific status;
- low usage or low rank cannot independently authorize deletion of canonical knowledge;
- tests prove the required conformance behaviors;
- the AAPL vertical slice runs through the Nexus without engines sharing private filesystem state.

---

## 31. Design Evolution Rule

When the initial mechanisms become insufficient, MTS SHALL replace or extend mechanisms behind stable contracts rather than allowing implementation convenience to redefine architecture.

Examples:

```text
SQLite CatalogStore
        ↓ later
Server relational CatalogStore

SQLite-backed IndexStore
        ↓ later
Server/search/columnar IndexStore

Filesystem PayloadStore
        ↓ later
Object/cluster PayloadStore

Relational relationship queries
        ↓ later if justified
Specialized graph/index implementation
```

Migration must preserve governed identity, provenance, lifecycle, relationships, and historical interpretability.

---

## 32. Closing Principle

The first Research Nexus implementation is deliberately small in **breadth**, not small in **correctness**.

We build only enough functionality to prove the first real research path, but every boundary we establish must be one we are willing to preserve when MTS operates on a server with concurrent workers, large historical datasets, live-market activity, autonomous research, durable Knowledge Management, Decision Intelligence, outcomes, and continuous learning.

> **Build the permanent contract now. Replace and scale the mechanisms later.**
