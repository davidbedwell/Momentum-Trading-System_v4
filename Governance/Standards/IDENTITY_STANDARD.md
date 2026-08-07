# Momentum Trading System — Identity Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md` and the canonical MTS v2 architecture set.

---

## 1. Purpose

This standard defines how identities are assigned, represented, preserved, versioned, related, and resolved across the Momentum Trading System (MTS).

It governs identity for:

- Research Nexus artifacts;
- source and normalized datasets;
- observations and measurements;
- evidence;
- findings;
- knowledge;
- research questions and plans;
- tasks and execution records;
- decisions;
- outcomes;
- policies and policy snapshots;
- instruments;
- engines and workers;
- schemas;
- campaigns and research state;
- future artifact types.

The purpose of this standard is to ensure that MTS can identify the same logical object regardless of:

- physical storage location;
- filename;
- directory;
- operating system;
- server;
- storage backend;
- process;
- engine implementation;
- serialization format.

---

## 2. Governing Principle

> **Identity is semantic and durable. Location is physical and replaceable.**

No canonical MTS object is identified solely by:

- a file path;
- a filename;
- a database row number;
- a Python object reference;
- a process ID;
- a temporary queue position;
- a storage backend key whose meaning is not governed.

Paths and locators may help resolve a representation. They do not define what the artifact is.

---

## 3. Design With the End in Mind

Identity SHALL be designed for the mature MTS deployment from the beginning.

Identity rules must remain valid when MTS moves from:

```text
single Mac
single local process
direct-attached storage
one worker
```

to:

```text
server deployment
multiple workers
concurrent research
distributed services
live-market workloads
multiple storage backends
large durable Research Nexus
```

An identifier created during local development must remain meaningful after the artifact is relocated to a server or a different storage technology.

---

## 4. Identity Domains

MTS distinguishes multiple identity domains.

### 4.1 Artifact Identity

Identifies a governed logical artifact.

Examples:

- dataset;
- evidence object;
- finding;
- knowledge object;
- research plan;
- decision;
- outcome;
- policy snapshot.

### 4.2 Artifact Version Identity

Identifies a specific immutable version of a governed artifact.

### 4.3 Task Identity

Identifies one governed unit of requested work.

### 4.4 Execution Identity

Identifies one execution attempt of a task.

### 4.5 Engine Identity

Identifies a logical engine/capability domain.

### 4.6 Worker Identity

Identifies a runtime worker instance.

### 4.7 Instrument Identity

Identifies a market instrument independently of its temporary ticker symbol.

### 4.8 Schema Identity

Identifies the governed schema definition used to interpret an artifact.

### 4.9 Research Identity

Identifies durable scientific state such as:

- research questions;
- research plans;
- campaigns;
- hypotheses;
- research needs.

These identity domains may reference one another but must not be conflated.

---

## 5. Artifact Identity

Every durable Research Nexus artifact must have a stable `artifact_id`.

An `artifact_id` identifies the logical object across:

- storage relocation;
- representation changes;
- indexing changes;
- process restarts;
- backend migration.

A logical artifact may have multiple versions.

The logical identity remains stable while version identity changes.

Example:

```text
artifact_id: finding:relative-volume-breakout
version: 3
```

The exact serialization format may differ by artifact family, but logical identity and version must remain separable.

---

## 6. Version Identity

A durable artifact version must be uniquely resolvable.

At minimum, the version identity must distinguish:

```text
artifact_id
artifact_version
```

A published immutable version must not be silently replaced.

Correction requires one of:

- a new version;
- a superseding artifact;
- an explicit invalidation;
- a governed lifecycle transition.

Content mutation without a new governed identity is prohibited.

---

## 7. Identifier Requirements

Governed identifiers must be:

- unique within their identity domain;
- stable once assigned;
- machine-readable;
- safe for durable references;
- independent of physical paths;
- independent of human display names;
- non-reusable after retirement;
- discoverable through the canonical registry/catalog layer.

Identifiers should be reasonably compact and should not encode volatile metadata that would cause identity churn.

---

## 8. Identifier Format

MTS should use structured opaque-or-semi-opaque identifiers.

Recommended general form:

```text
<domain>:<identifier>
```

Illustrative examples:

```text
artifact:01JXYZ...
task:01JXYZ...
execution:01JXYZ...
engine:data-intake
worker:01JXYZ...
instrument:01JXYZ...
schema:mts.dataset
research-plan:01JXYZ...
decision:01JXYZ...
```

The exact generator may use UUID, ULID, another collision-resistant scheme, or a governed deterministic identifier where scientifically justified.

The implementation mechanism is not architectural.

---

## 9. Deterministic vs Generated Identity

### Generated Identity

Use generated identity when the object is a distinct governed occurrence.

Examples:

- task request;
- execution attempt;
- decision;
- research plan;
- research question;
- outcome;
- worker instance.

### Deterministic Identity

Deterministic identity may be used when the same logical object should resolve to the same identity from the same governed definition.

Examples may include:

- registered feature definitions;
- schema definitions;
- canonical policy names;
- some content-addressed objects.

Deterministic identity must be based on governed semantic inputs, not arbitrary filesystem paths.

---

## 10. Content Identity

Content identity is distinct from logical identity.

A `content_hash` identifies payload bytes or canonicalized content.

Two logical artifacts may have:

```text
different artifact_id
same content_hash
```

because they have different:

- provenance;
- role;
- lifecycle;
- research context;
- policy context.

Likewise, one logical artifact may have:

```text
same artifact_id
different content_hash
```

across versions.

Content hashes must not replace semantic artifact identity.

---

## 11. Store Once, Reference Everywhere

Where practical, MTS should avoid duplicating identical canonical payloads.

A logical artifact may reference a shared content object.

Example:

```text
Artifact A ─┐
            ├── content_hash: abc123
Artifact B ─┘
```

Deduplication must preserve each artifact's:

- logical identity;
- provenance;
- lifecycle;
- metadata;
- relationships.

---

## 12. Stable References

Cross-component durable references must use governed identities.

Examples:

```text
source_refs
parent_refs
dependency_refs
knowledge_refs
policy_refs
decision_refs
outcome_refs
task_refs
```

Durable references must not depend on:

```text
/Users/name/...
/Volumes/Drobo/...
/server/share/...
```

Physical locators may be stored separately for resolution.

---

## 13. Locator Identity Separation

MTS distinguishes:

```text
identity
```

from:

```text
locator
```

Example:

```text
artifact_id: artifact:01JABC...
locator: nexus://datasets/...
```

The locator may change.

The identity must not.

A backend migration may update locators without changing artifact identity.

---

## 14. Human-Readable Names

Human-readable names are metadata.

Examples:

```text
AAPL
AAPL Daily OHLCV
Relative Volume Finding
Research Plan 17
```

Display names may change.

They are not canonical identity.

---

## 15. Instrument Identity

Ticker symbols are mutable labels and must not serve as permanent instrument identity.

Instrument identity must support:

- symbol changes;
- share classes;
- mergers;
- acquisitions;
- delistings;
- multiple listings;
- options contracts;
- ETFs;
- future asset types.

An instrument record may include:

```text
instrument_id
symbol
exchange
asset_type
effective_from
effective_to
provider_identifiers
parent_instrument_ref
```

The exact schema belongs in Governance/Schemas.

---

## 16. Task Identity

Every durable governed task must have a stable `task_id`.

A task identity represents the requested unit of work.

Retries do not create a new task unless the requested work itself changes materially.

Example:

```text
task_id: task:01JABC...
attempt 1 → execution:01JA...
attempt 2 → execution:01JB...
```

Task identity and execution identity must remain distinct.

---

## 17. Execution Identity

Every material execution attempt must have an `execution_id`.

Execution identity supports:

- retries;
- failure analysis;
- worker attribution;
- timing;
- resource accounting;
- provenance.

A successful retry must not erase evidence that earlier attempts failed.

---

## 18. Engine Identity

Engine identity represents a logical responsibility domain.

Canonical engine identities should be functional rather than historical-number based.

Examples:

```text
engine:data-intake
engine:discovery
engine:research-director
engine:market-discovery
engine:decision
engine:learning-governance
```

Legacy labels such as Engine 08/09/10 are migration references only.

---

## 19. Worker Identity

A worker is a runtime execution unit.

Every active worker must have a unique runtime `worker_id`.

Worker identity must be distinct from engine identity.

Example:

```text
engine_id: engine:discovery
worker_id: worker:01JABC...
```

Worker identity may be short-lived.

Material execution records referencing it may be durable.

---

## 20. Schema Identity

Every governed schema must have:

```text
schema_id
schema_version
```

Example:

```text
schema_id: mts.finding
schema_version: 1
```

A schema version is immutable after publication.

Breaking changes require a new governed version.

---

## 21. Policy Identity

Material decisions and lifecycle actions must reference the exact policy version that governed them.

A policy should therefore have:

```text
policy_id
policy_version
```

When a material runtime decision uses policy, the Nexus should preserve or resolve the exact applicable policy snapshot.

---

## 22. Research Identity

Research state must be durable and referenceable.

Examples:

```text
research_question_id
research_plan_id
research_need_id
campaign_id
hypothesis_id
```

Research state must not be identified only by an engine-local directory.

This allows a Research Director implementation to change without losing research continuity.

---

## 23. Relationship Identity

Relationships between governed objects must themselves be representable and auditable.

A relationship should capture:

```text
source_ref
relationship_type
target_ref
created_at
producer
metadata
```

Examples:

```text
DERIVED_FROM
SUPPORTS
CONTRADICTS
SUPERSEDES
DEPENDS_ON
ANSWERS
GENERATED_BY
USED_IN_DECISION
PRODUCED_OUTCOME
```

The relationship vocabulary belongs in artifact governance.

---

## 24. Provenance Identity

Every durable artifact must be able to identify its producer.

Producer identity may include:

```text
engine_id
worker_id
execution_id
software_version
model_version
human_actor_id where applicable
```

The system must distinguish:

- who/what produced the artifact;
- what inputs were used;
- what execution created it.

---

## 25. Lifecycle and Identity

Lifecycle transition does not normally change artifact identity.

Example:

```text
artifact:01JABC
DRAFT
→ VALIDATED
→ CURRENT
→ SUPERSEDED
→ RETIRED
```

The logical identity remains the same.

A new scientific conclusion with materially different meaning should receive a new artifact identity rather than abusing lifecycle state.

---

## 26. Supersession

Supersession must be explicit.

A newer artifact or version may reference:

```text
supersedes
```

The superseded object must remain resolvable.

Supersession does not imply physical deletion.

---

## 27. Immutability After Publication

Once an immutable durable artifact version is published, its identity-to-content binding must not change silently.

If correction is necessary:

```text
old version remains
new version is published
relationship records correction/supersession
```

This requirement supports reproducibility and auditability.

---

## 28. Identity Allocation Authority

Identity generation must occur through governed shared identity services or libraries.

Components must not invent incompatible local ID schemes without explicit governance approval.

The identity mechanism should support concurrent allocation without coordination bottlenecks.

---

## 29. Identity Collision

A detected identifier collision is a system integrity error.

The system must:

- stop publication;
- preserve diagnostics;
- not overwrite the existing object;
- resolve the collision through governed recovery.

Silent collision resolution is prohibited.

---

## 30. Duplicate Submission

Duplicate submission and identity collision are different.

If an artifact with the same logical identity/version already exists:

- identical content may yield an idempotent no-change result;
- differing content must fail or create a governed new version;
- silent overwrite is prohibited.

---

## 31. Identity Resolution

The Research Nexus must provide a canonical identity-resolution mechanism.

Conceptually:

```text
resolve(artifact_id, version)
```

returns the current governed descriptor and available representation locators.

Clients should not reconstruct physical paths from identifier strings.

---

## 32. Identity Discovery

MTS must support discovery by metadata in addition to direct identity lookup.

Examples:

- instrument;
- date range;
- artifact type;
- campaign;
- producer;
- lifecycle state;
- tag;
- feature;
- event family;
- upstream/downstream relationship.

Discovery returns governed identities.

---

## 33. Temporary Identity

Class III runtime objects may use temporary identifiers.

Examples:

- local scratch job;
- in-memory buffer;
- lock;
- reconstructable materialization.

If such an object becomes durable or scientifically significant, it must receive a governed durable identity before publication.

---

## 34. Migration Identity

v1 assets migrated into v2 must receive v2 governed identity.

Migration metadata should preserve:

```text
legacy_system
legacy_path
legacy_identifier
migration_timestamp
migration_execution_ref
```

Legacy paths may be retained as provenance.

They must not become the new canonical identity.

---

## 35. Identity and Git

Class I Git assets may use repository paths as source-control locations.

However, when a governed document or schema is referenced by durable scientific state, the reference should identify the logical document/schema version, not depend solely on the repository path.

Git commit hashes may be preserved as implementation provenance.

---

## 36. Identity and Backup

Backup copies must retain the same logical artifact identity as the canonical artifact.

A backup is not a new scientific artifact merely because it is physically copied elsewhere.

Backup metadata may identify:

```text
backup_id
artifact_ref
backup_location
backup_timestamp
verification_hash
verification_status
```

---

## 37. Identity and Cache

A cache entry should retain a reference to the durable artifact(s) from which it was created.

Deleting a cache must not delete or invalidate the durable identities it references.

---

## 38. Identity and Explainability

Material Decision artifacts must preserve exact references to the identities of:

- current-state artifacts;
- knowledge;
- contradictory evidence where applicable;
- policies;
- portfolio state;
- execution/version context.

Explainability must be grounded in resolvable identities.

---

## 39. Prohibited Practices

The following are prohibited for canonical durable identity:

- user-specific absolute paths;
- mutable filenames;
- directory position;
- array indexes;
- database auto-increment IDs exposed as enterprise identity without governance;
- process IDs;
- timestamps alone;
- ticker symbols alone;
- hashes alone where semantic identity is required;
- engine-local private IDs that cannot be resolved enterprise-wide.

---

## 40. Initial v2 Implementation

The first implementation should provide a small shared identity module capable of generating and validating at least:

```text
artifact_id
task_id
execution_id
worker_id
research_plan_id
research_need_id
decision_id
outcome_id
```

It should also support registered stable identities for:

```text
engine_id
schema_id
policy_id
instrument_id
```

The initial implementation may use one process.

The generated identities must remain valid under future concurrent server execution.

---

## 41. Testing Requirements

Identity tests must include:

- uniqueness under repeated generation;
- concurrent generation;
- format validation;
- non-reuse;
- stable logical identity across relocation;
- distinction between task and execution identity;
- distinction between logical identity and content hash;
- duplicate publication behavior;
- collision failure behavior;
- supersession references;
- resolution after backend relocation.

---

## 42. Conformance Requirements

A component conforms when it:

1. uses governed identity domains;
2. separates logical identity from location;
3. separates logical artifact identity from version identity;
4. separates task identity from execution identity;
5. separates engine identity from worker identity;
6. does not use ticker symbols as permanent instrument identity;
7. does not silently reuse retired identifiers;
8. does not overwrite immutable published versions;
9. preserves identity across storage migration;
10. uses governed cross-component references;
11. preserves provenance identities;
12. resolves durable objects through canonical identity services;
13. supports concurrent future deployment without identity redesign.

---

## 43. Companion Governance

This standard is implemented in conjunction with:

```text
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/CONFIGURATION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 44. Closing Principle

MTS must always be able to answer:

> **What exact logical object is this, which version is it, who produced it, what does it reference, and can I still resolve that identity after moving the entire system to another machine or storage backend?**

If the answer depends on a local path, a filename, or a particular engine implementation, the identity is not sufficiently governed.
