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

---

## 3. Initial Technical Architecture

The first Research Nexus implementation SHALL use three logical layers:

```text
Nexus Client/API
      ↓
Nexus Services
      ↓
Storage Ports
   ↙       ↘
Catalog    Payload Store
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

### 3.3 Storage Ports

Storage behavior SHALL be expressed behind interfaces/protocols so physical mechanisms can later be replaced.

Initial ports:

```text
CatalogStore
PayloadStore
```

Future implementations may add specialized index, object-store, graph, cache, backup, or distributed transaction mechanisms without changing Nexus semantic contracts.

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

### 4.2 Payload Store: Filesystem-Backed Content Store

Initial artifact payloads SHALL be stored outside Git beneath the configured Research Nexus root using a filesystem-backed `PayloadStore`.

Payload addressing SHALL be derived from content integrity information and/or governed storage locators rather than artifact meaning.

The physical payload path SHALL NOT be the artifact identity.

A future object-store implementation must be substitutable behind the same storage port.

### 4.3 Serialization

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
storage_class
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
- storage/retention class;
- producer;
- schema ID/version;
- ticker/instrument tag or governed field where applicable;
- campaign/research-plan reference;
- validation status;
- tags;
- creation time.

Query results SHALL return stable Nexus artifact references/envelopes, not expose raw database rows as the domain contract.

Query capability SHALL be extensible without breaking callers.

---

## 17. Lifecycle Scope for the First Slice

The first implementation SHALL support only lifecycle transitions immediately required by its artifact contracts while preserving a generic transition-validation mechanism.

Publication and promotion SHALL remain distinct.

The initial Nexus SHALL NOT independently decide that a Finding has become canonical Knowledge merely because the Finding is validly stored.

Future Accountability and Learning/Governance services will invoke governed lifecycle transitions under their respective authority.

---

## 18. Backup Classification

Every durable artifact SHALL carry explicit backup requirement/status metadata as required by governance.

The minimum vertical slice SHALL implement **classification and observability** of backup requirements even if automated backup transport is introduced during Nexus hardening rather than the first publication milestone.

No implementation may falsely mark a backup complete merely because a copy command was attempted.

Verified backup requires integrity verification according to policy.

---

## 19. Concurrency and Locking

The first implementation may operate under modest local concurrency, but it SHALL be safe for multiple execution instances.

SQLite SHALL use transaction boundaries and an appropriate journaling/locking configuration for concurrent readers and bounded writers.

Payload publication SHALL avoid shared mutable filenames and use unique staging locations followed by atomic filesystem operations where supported.

The implementation SHALL NOT depend on process-global mutable state for correctness.

Concurrency limits belong to Task Management/configuration rather than hard-coded Nexus worker ownership.

---

## 20. Crash Recovery

Publication design SHALL tolerate interruption between major publication stages.

On startup or maintenance invocation, the Nexus SHALL be capable of identifying abandoned staging material without treating it as canonical publication.

Committed catalog records SHALL be reconcilable with their referenced payload representations.

Missing or hash-invalid durable payloads SHALL surface as integrity failures; the Nexus SHALL not silently regenerate or redirect them unless a governed recovery mechanism explicitly authorizes it.

---

## 21. Configuration

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

## 22. Python Package Boundary

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
    config.py
    storage/
        __init__.py
        catalog.py
        payload.py
        sqlite_catalog.py
        filesystem_payload.py
```

This is a technical starting structure, not a permanent architectural directory contract.

Responsibilities SHALL remain separated enough that backend implementations can be replaced without rewriting Nexus clients.

Shared mechanisms that become independently useful across multiple MTS components may later move into appropriate `Core/` packages under governed refactoring.

---

## 23. Error Model

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
AuthorizationError
```

Error details SHALL avoid exposing secrets while preserving sufficient diagnostic/audit context.

---

## 24. Initial Test Architecture

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

- storage class validation;
- retention class validation;
- publication distinct from promotion;
- prohibited transition rejection for implemented transitions.

### Concurrency/Recovery

- independent publication staging;
- bounded concurrent publication safety;
- abandoned staging does not become canonical;
- retry after ambiguous completion reconciles rather than duplicates.

---

## 25. First Vertical-Slice Artifact Set

Do not implement every future MTS artifact type initially.

Implement the minimum governed schemas/contracts required to prove:

```text
Source Dataset / Raw Source Reference
Accepted or Normalized Dataset
Finding
Research Question or Research State
Research Conclusion / Follow-up Question
Relationship / Provenance records
```

Exact names SHALL follow the existing governed contracts/schemas. If a required contract/schema is absent, it SHALL be created under Governance before production code invents an undocumented representation.

---

## 26. First Acceptance Test

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
9. Research Director retrieval of the Finding;
10. publication of a next question or conclusion;
11. restart of the process;
12. successful retrieval and lineage traversal after restart;
13. identical logical identities despite clients having no knowledge of payload paths;
14. schema and integrity verification;
15. explicit storage/retention/backup classifications.

This test SHALL use the real Nexus interfaces, not direct fixture-directory coupling.

---

## 27. Explicitly Deferred Capabilities

The following SHALL NOT block the minimum vertical slice unless implementation proves one is immediately necessary:

- distributed database deployment;
- remote object storage;
- graph database;
- full-text/vector search;
- high-volume market streaming;
- generalized event bus;
- automated cache ranking;
- complete SoK materialization/ranking;
- all knowledge lifecycle automation;
- full backup transport/replication system;
- multi-node locking;
- production authentication infrastructure;
- large-scale data migration;
- broad adoption of v1 assets;
- speculative performance optimization.

Deferral does not remove the governing architectural requirement. Interfaces must avoid preventing these capabilities later.

---

## 28. Implementation Sequence

Development SHALL proceed in this order unless a discovered dependency requires an explicitly documented adjustment:

```text
1. Confirm/create minimum governed contracts and schemas
2. Implement Nexus configuration/root resolution
3. Implement artifact envelope models + identity
4. Define CatalogStore and PayloadStore ports
5. Implement filesystem PayloadStore
6. Implement SQLite CatalogStore + migrations
7. Implement schema/metadata/provenance validation
8. Implement transactional publication coordinator
9. Implement get/query
10. Implement relationships + traversal
11. Implement integrity verification
12. Implement idempotency/conflict behavior
13. Implement recovery/reconciliation behavior
14. Complete Nexus conformance tests
15. Run AAPL Nexus-only acceptance path
16. Add the minimum Data Intake adapter
17. Add the minimum Discovery adapter
18. Add the minimum Research Director adapter
19. Run full AAPL vertical slice
20. Audit against architecture/governance
21. Commit/freeze the proven Nexus contract
22. Begin Nexus hardening before high-volume producers
```

This sequence intentionally builds permanent infrastructure through a narrow end-to-end use case rather than constructing speculative breadth.

---

## 29. Definition of Done — Minimum Durable Nexus

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
- tests prove the required conformance behaviors;
- the AAPL vertical slice runs through the Nexus without engines sharing private filesystem state.

---

## 30. Design Evolution Rule

When the initial mechanisms become insufficient, MTS SHALL replace or extend mechanisms behind stable contracts rather than allowing implementation convenience to redefine architecture.

Examples:

```text
SQLite CatalogStore
        ↓ later
Server relational CatalogStore

Filesystem PayloadStore
        ↓ later
Object/cluster PayloadStore

Relational relationship queries
        ↓ later if justified
Specialized graph/index implementation
```

Migration must preserve governed identity, provenance, lifecycle, relationships, and historical interpretability.

---

## 31. Closing Principle

The first Research Nexus implementation is deliberately small in **breadth**, not small in **correctness**.

We build only enough functionality to prove the first real research path, but every boundary we establish must be one we are willing to preserve when MTS operates on a server with concurrent workers, large historical datasets, live-market activity, autonomous research, Decision Intelligence, outcomes, and continuous learning.

> **Build the permanent contract now. Replace and scale the mechanisms later.**
