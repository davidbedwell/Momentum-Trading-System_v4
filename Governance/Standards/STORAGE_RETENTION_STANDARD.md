# Momentum Trading System — Storage and Retention Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, `IDENTITY_STANDARD.md`, `ARTIFACT_GOVERNANCE_STANDARD.md`, and `SCHEMA_STANDARD.md`.

---

## 1. Purpose

This standard defines how Momentum Trading System (MTS) assets are classified for storage, retention, backup, deletion, recovery, and physical relocation.

It establishes the boundary between:

- Git-governed system definition;
- durable Research Nexus state;
- transient/reconstructable runtime state.

It also governs the distinction between:

- permanent;
- semi-permanent;
- cached/transient data.

---

## 2. Governing Principle

> **Semantic importance, persistence duration, backup requirement, and physical location are separate properties.**

MTS must not decide retention merely from:

- filename;
- directory;
- artifact type;
- current disk location;
- frequency of use;
- file size.

Storage behavior must be governed by metadata and policy.

---

## 3. Three Persistence Classes

Every material MTS asset must belong to one of three persistence classes.

```text
CLASS_I
CLASS_II
CLASS_III
```

These classes govern the asset's relationship to Git, the Research Nexus, backup, and deletion.

---

## 4. Class I — System Definition

Class I contains the assets that define how MTS is built and governed.

Examples include:

- source code;
- canonical architecture;
- Charter;
- standards;
- policies;
- contracts;
- schemas;
- configuration templates;
- database migrations;
- test code;
- small synthetic test fixtures;
- operational utilities intended to be source controlled.

Primary persistence mechanism:

```text
Git
```

Class I assets are normally committed to the repository.

---

## 5. Class I Exclusions

Class I does not include large scientific or operational state merely because the data is important.

The following normally do not belong in Git:

- raw historical market datasets;
- normalized market datasets at scale;
- derived research datasets;
- evidence payloads;
- knowledge stores;
- task/execution history at scale;
- decisions/outcomes at scale;
- caches;
- logs at scale;
- secrets.

Git is not the Research Nexus.

---

## 6. Class II — Durable Research Nexus State

Class II contains durable scientific and operational state that MTS must preserve beyond a single runtime.

Examples include:

- canonical raw source data admitted to research;
- normalized durable datasets;
- durable evidence;
- findings;
- knowledge;
- research questions and plans;
- research needs;
- durable task/dependency state;
- material execution provenance;
- decisions;
- outcomes;
- Nexus catalogs and relationship state;
- scientific audit records;
- policy snapshots used in material decisions.

Primary persistence mechanism:

```text
Research Nexus
```

Class II assets are not normally committed to Git.

---

## 7. Class II Permanent

Class II Permanent assets are intended to remain part of the durable MTS scientific or operational record.

Examples may include:

- irreplaceable or authoritative raw source data;
- promoted knowledge;
- material evidence required for reproducibility;
- decisions and outcomes;
- provenance required to explain material conclusions;
- permanent Nexus registry state.

Class II Permanent assets require independent verified backup.

---

## 8. Class II Semi-Permanent

Class II Semi-Permanent assets are durable enough to survive runtime/restart and remain governed, but may eventually be retired or reconstructed.

Examples may include:

- reproducible normalized datasets;
- expensive derived datasets;
- intermediate scientific material worth retaining;
- durable task state after its active usefulness has ended;
- research material whose authoritative upstream sources remain available.

A Semi-Permanent asset must have an explicit recovery policy.

It may be:

```text
BACKUP_REQUIRED
```

or:

```text
RECOVERABLE_FROM_SOURCE
```

The choice must consider:

- reacquisition cost;
- recomputation cost;
- source availability;
- source licensing;
- scientific reproducibility;
- operational impact;
- retention value.

---

## 9. Class III — Transient / Reconstructable State

Class III contains state that may be deleted because it is temporary or reconstructable.

Examples include:

- caches;
- scratch files;
- staging files;
- decompressed working copies;
- temporary joins;
- temporary materializations;
- live-market buffers;
- temporary Research Director context;
- worker-local caches;
- scheduler queue representations reconstructable from durable task state;
- locks;
- temporary test/runtime data.

Class III is not automatically backed up.

Deletion must still respect active dependencies.

---

## 10. Persistence Class Is Metadata

Persistence class must be represented explicitly in governed metadata.

Example:

```text
persistence_class: CLASS_II
retention_class: PERMANENT
backup_requirement: REQUIRED
```

or:

```text
persistence_class: CLASS_III
retention_class: CACHE
backup_requirement: NONE
```

A directory name alone must not determine lifecycle.

---

## 11. Retention Classes

Within persistence classes, MTS may use governed retention classes such as:

```text
PERMANENT
SEMI_PERMANENT
CACHE
SESSION
TIME_LIMITED
POLICY_CONTROLLED
```

Exact controlled vocabulary belongs in Governance/Schemas.

---

## 12. Backup Requirement

Every Class II artifact must carry an explicit backup requirement.

Initial conceptual values:

```text
REQUIRED
RECOVERABLE_FROM_SOURCE
NONE
```

`NONE` should be unusual for Class II and must be justified by policy.

Class II Permanent requires:

```text
REQUIRED
```

---

## 13. Independent Backup

A backup is independent only when loss of the primary storage system does not also destroy the backup.

A second directory on the same physical device is not an independent backup.

A second logical volume on the same failing storage enclosure is not necessarily an independent backup.

Backup design must consider correlated failure.

---

## 14. Backup Verification

A backup is not considered reliable merely because a copy operation reported success.

Backup processes should support:

- copy completion status;
- content/integrity verification;
- timestamp;
- source identity;
- destination;
- verification result;
- recovery testing where appropriate.

Material permanent data should have periodic recovery validation.

---

## 15. Primary Storage vs Backup

The primary Research Nexus and its backup are distinct roles.

MTS must not treat a backup directory as an active primary store unless a governed recovery/failover process promotes it.

Likewise, mirroring or RAID redundancy does not by itself replace independent backup.

---

## 16. RAID / Device Redundancy

Device redundancy protects availability against some hardware failures.

It does not protect against all forms of:

- filesystem corruption;
- accidental deletion;
- software error;
- malware;
- enclosure/controller failure;
- catastrophic device loss;
- operator error.

Therefore, redundant storage does not eliminate Class II backup requirements.

---

## 17. Physical Storage Independence

The canonical architecture must not depend on a particular physical Research Nexus location.

Possible deployment stages may include:

```text
local SSD
direct-attached storage
NAS
server filesystem
database
object storage
hybrid storage
```

Moving between these must be primarily a configuration/migration operation rather than an engine redesign.

---

## 18. No User-Specific Paths in Semantics

Canonical scientific identity and contracts must not depend on paths such as:

```text
/Users/<name>/...
/Volumes/Drobo/...
```

Deployment configuration may resolve logical storage roles to such paths.

The path is a locator, not identity.

---

## 19. Storage Roles

MTS should configure logical storage roles rather than teaching engines physical directories.

Illustrative roles:

```text
nexus_primary
nexus_backup
cache_root
staging_root
logs_root
temporary_root
```

Engines and services should use governed interfaces/configuration to resolve these roles.

---

## 20. No Silent Fallback Storage

If the configured durable Research Nexus is unavailable, MTS must not silently write permanent scientific state to another arbitrary location.

For example:

```text
configured Nexus unavailable
→ silently write to repository
```

is prohibited.

The operation must:

- fail explicitly;
- queue safely where governed;
- or use an explicitly configured failover policy.

---

## 21. Repository Independence

The Research Nexus physical root must not be derived implicitly from the Git repository root.

The repository may move without moving durable data.

Durable data may move without moving the repository.

This separation is mandatory for eventual server deployment.

---

## 22. Engine Storage Boundary

Engines must not own canonical physical storage paths.

Engines produce or consume governed artifacts through Research Nexus interfaces.

A compliant engine should not need code changes because the Nexus moves from:

```text
Mac internal SSD
```

to:

```text
Drobo
```

to:

```text
server storage
```

---

## 23. Raw Data

Canonical raw source data admitted to the Research Nexus is normally Class II.

Its retention class depends on:

- reacquisition feasibility;
- licensing;
- historical availability;
- transformation reproducibility;
- scientific importance.

Raw data should not be mutated in place.

---

## 24. Normalized Data

Normalized data may be:

```text
Class II Permanent
Class II Semi-Permanent
Class III
```

depending on whether it is:

- authoritative durable research input;
- expensive but reproducible;
- merely a temporary materialization.

Normalization does not automatically determine retention.

---

## 25. Derived Data

Derived data retention depends on scientific value and reconstruction cost.

A large derived dataset may be Semi-Permanent and recoverable from source.

A small but critical derived artifact required to reproduce a material decision may be Permanent.

---

## 26. Knowledge

Promoted durable knowledge is normally Class II Permanent.

Superseded or contradicted knowledge does not automatically become deletable.

Historical knowledge may remain necessary for:

- decision explainability;
- scientific audit;
- understanding evolution of SoK;
- outcome evaluation.

---

## 27. Research State

Active research questions, plans, dependencies, and research needs required for continuity are Class II.

Ephemeral scratch reasoning that can be safely regenerated may be Class III.

Contradictory and negative working material is default-to-expire after the governing Research Plan is resolved. During active investigation it may be Class III when safely reproducible, or Class II Semi-Permanent when required for restart, expensive to reacquire, or necessary to protect scientific integrity.

Permanent retention of contradiction requires objective justification. Normally MTS preserves a compact resolution/lineage record when the contradiction materially changed knowledge, applicability, uncertainty, decision eligibility, supersession, retirement, or a material historical Decision.

The Research Director must not depend on an in-memory-only state for work that must survive restart.

---

## 28. Task State

Governed Task Requests, dependency records, and execution records required for:

- restart recovery;
- provenance;
- downstream unblocking;
- audit;

are Class II.

Worker-local queues, scheduling caches, locks, and reconstructable dispatch structures are Class III.

---

## 29. Decisions and Outcomes

Material Decision and Outcome artifacts are Class II Permanent unless a specific policy defines otherwise.

They are required for:

- explainability;
- learning;
- performance evaluation;
- governance;
- historical reconstruction.

---

## 30. Logs

Logs are not one persistence class by definition.

Operational logs may be:

- Class III short-lived;
- Class II when required for material audit/provenance.

Important scientific facts must not exist only inside free-form logs.

---

## 31. Human-Readable Reports

Reports generated from canonical machine-readable artifacts are normally rebuildable.

They may therefore be Class III or Semi-Permanent.

A report becomes Class II Permanent only when policy explicitly makes the report itself part of the record.

The canonical scientific state must not depend on keeping a PDF or text rendering.

---

## 32. Cache Metadata

Cache entries should carry enough metadata to determine:

- what created them;
- what durable inputs they depend on;
- when they were created;
- expiration/retirement policy;
- whether active work still depends on them.

Caches should be intentionally disposable.

---

## 33. Cache Retirement

A cache may be retired when objective conditions are satisfied.

Possible criteria include:

- TTL exceeded;
- no active dependency;
- no pending task requires it;
- durable source remains available;
- recomputation is permitted;
- no policy hold applies.

Cache deletion must not be based solely on “oldest file first” when active scientific dependencies exist.

---

## 34. Daily / Live Data Cache

High-volume daily/live operational data may be cached when it can be reacquired or regenerated.

Examples may include:

- live quote buffers;
- transient scanner results;
- temporary market snapshots;
- materialized query results.

If the system discovers a scientifically meaningful observation from cached data, the relevant result and required supporting evidence must be promoted into Class II before cache retirement.

---

## 35. Promotion From Cache

Class III material cannot become durable merely by being left on disk.

Promotion to Class II requires:

- governed identity;
- schema validation;
- provenance;
- persistence metadata;
- retention class;
- backup requirement;
- publication through the Nexus.

---

## 36. Deletion Eligibility

Before deleting governed data, MTS must evaluate:

- persistence class;
- retention class;
- active dependencies;
- provenance requirements;
- reproducibility requirements;
- backup status;
- recovery source;
- policy/legal/licensing holds;
- pending research/task dependencies.

Deletion authorization must be explicit for Class II.

---

## 37. Permanent Means Durable Record, Not Infinite Active Storage

Permanent does not require every byte to remain forever on the fastest primary storage tier.

Permanent means the governed record must remain recoverable and resolvable.

Permanent data may move to archival storage if:

- identity remains resolvable;
- integrity is preserved;
- recovery is governed;
- required metadata remains online or discoverable;
- policy permits archival latency.

---

## 38. Archival

Archival is a storage-tier transition, not scientific deletion.

Archived artifacts remain:

- identified;
- discoverable;
- governed;
- recoverable.

Their locator and access latency may change.

---

## 39. Storage Tiering

Future MTS may use storage tiers such as:

```text
HOT
WARM
COLD
ARCHIVE
```

Tiering may consider:

- access frequency;
- size;
- recomputation cost;
- latency requirement;
- scientific importance.

Tier does not replace persistence class.

---

## 40. Recovery Source

An artifact marked `RECOVERABLE_FROM_SOURCE` must identify or resolve a governed recovery path.

Recovery assumptions must not depend on an undocumented vendor subscription or temporary URL.

If the recovery source becomes unavailable, the artifact's backup requirement must be re-evaluated.

---

## 41. Source Licensing

Retention policy must respect vendor and dataset licensing.

If a source cannot legally be backed up or retained indefinitely, metadata/policy must reflect that constraint.

MTS must not pretend a legally non-retainable source is permanently recoverable.

---

## 42. Integrity

Durable payloads should support integrity verification.

Content hashes may be used to detect corruption or unintended mutation.

Integrity verification does not replace semantic validation.

---

## 43. Corruption

If corruption is detected:

- the artifact must not be silently replaced;
- the affected identity/version must be flagged;
- backup/recovery status must be evaluated;
- dependents should be identified;
- recovery must preserve provenance.

---

## 44. Storage Health

MTS must distinguish storage availability from storage health.

A mounted filesystem is not automatically a verified healthy durable store.

Before a new device becomes an approved Class II primary location, it should pass the applicable storage qualification procedure.

Storage qualification belongs in operational governance/utilities rather than engine code.

---

## 45. New Storage Qualification

Before using a new physical storage target for the Research Nexus, MTS should verify as appropriate:

- filesystem integrity;
- read/write operation;
- sustained accessibility;
- expected capacity;
- mount/configuration stability;
- permissions;
- backup destination independence;
- recovery procedure.

Failure of qualification blocks promotion to approved primary Nexus storage.

---

## 46. Backup Topology

The mature deployment should maintain an explicit topology such as:

```text
Research Nexus Primary
        ↓
Independent Backup
        ↓
optional additional archive/offsite protection
```

The exact topology is deployment configuration.

Permanent data must not depend on a single physical failure domain.

---

## 47. Local Development

During early local development, the Nexus may use internal SSD storage.

This does not change the architecture.

Local deployment must still use the same:

- logical storage roles;
- identity rules;
- publication interfaces;
- persistence metadata.

This prevents local convenience from becoming architectural coupling.

---

## 48. Direct-Attached Storage

A direct-attached device may serve as a Nexus storage target if it passes qualification and operational policy.

Its device name must remain deployment configuration.

No engine may contain special logic for a particular enclosure or volume name.

---

## 49. Server Migration

Migration to the eventual server must preserve:

- artifact identities;
- versions;
- metadata;
- provenance;
- relationships;
- integrity;
- lifecycle;
- retention classification;
- backup requirements.

Physical locators may change.

Engine scientific behavior should not.

---

## 50. Migration Verification

A storage migration is not complete until MTS verifies:

- expected artifact inventory;
- metadata integrity;
- content integrity where applicable;
- relationship resolution;
- identity resolution;
- backup topology;
- new primary availability.

The old primary should not be destroyed immediately after copy.

---

## 51. Test Storage

Tests must use isolated storage roots.

Tests must not write into:

- production Research Nexus;
- real raw-data stores;
- permanent backup stores.

Test storage should be disposable unless a fixture is intentionally committed as Class I.

---

## 52. Secrets

Secrets do not belong in:

- Git;
- scientific artifacts;
- ordinary logs;
- cache filenames.

Secret storage is governed separately by configuration/security policy.

---

## 53. `.gitignore`

The repository must ignore runtime-generated assets that do not belong in Class I.

Examples may include:

```text
cache/
logs/
runtime/
local Nexus data
temporary files
virtual environments
credentials
large generated outputs
```

`.gitignore` is a safeguard, not the primary storage governance mechanism.

---

## 54. Capacity Management

Capacity management should use actual physical/storage-backend capacity rather than misleading logical thin-provisioned volume sizes.

MTS should monitor:

- available physical capacity;
- growth rate;
- retention pressure;
- backup capacity;
- archive capacity.

Capacity pressure must not trigger uncontrolled deletion of governed Class II data.

---

## 55. Retention Evaluation

Retention decisions should be policy-driven and reproducible.

A retention evaluation should be able to explain:

```text
why this artifact is retained
why it is eligible for archive
why it is eligible for deletion
what dependencies were checked
what recovery source exists
what backup requirement applies
```

---

## 56. Retention Audit

Material Class II archive/deletion actions should create an audit record.

The record should include:

```text
artifact_ref
action
policy_version
reason
dependency_check
backup/recovery status
timestamp
execution_ref
```

---

## 57. Initial v2 Implementation

The first implementation should support:

1. logical storage-role configuration;
2. Class I/II/III metadata;
3. Permanent/Semi-Permanent/Cache distinction;
4. backup requirement metadata;
5. isolated cache/staging roots;
6. no silent fallback for Nexus writes;
7. dependency-aware deletion hooks;
8. content integrity metadata where applicable;
9. migration-friendly locators;
10. test-store isolation.

Sophisticated automatic tiering can come later without changing these foundations.

---

## 58. Conformance

A component conforms when it:

1. does not place scientific data in Git by convenience;
2. does not derive canonical Nexus storage from repository location;
3. uses logical storage roles;
4. does not silently fall back to arbitrary durable storage;
5. preserves identity across relocation;
6. explicitly classifies durable/transient state;
7. explicitly records Class II backup requirements;
8. protects Permanent Class II assets with independent verified backup;
9. protects active dependencies before cache/data deletion;
10. keeps tests isolated from production state;
11. treats RAID/device redundancy as distinct from backup;
12. supports future server migration without engine redesign.

---

## 59. Companion Governance

This standard operates with:

```text
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/CONFIGURATION_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md
```

---

## 60. Closing Principle

MTS must always be able to answer:

> **What is this asset, why are we keeping it, how long must it survive, what may depend on it, how is it recovered, and can we move it to different physical storage without changing its scientific identity?**

If those answers depend only on the directory in which a file happens to sit, storage is not yet governed.
