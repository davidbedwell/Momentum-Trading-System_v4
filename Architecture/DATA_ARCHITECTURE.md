# Momentum Trading System — Data Architecture

**Status:** Canonical  
**Authority:** Governing data architecture subordinate to `CHARTER.md`, `Architecture/SYSTEM_ARCHITECTURE.md`, `Architecture/RESEARCH_NEXUS_ARCHITECTURE.md`, and `Architecture/ENGINE_ARCHITECTURE.md`

---

## 1. Purpose

This document defines the enduring data architecture of the Momentum Trading System (MTS).

It governs:

- data meaning and classification;
- source, observation, measurement, evidence, finding, knowledge, decision, and outcome distinctions;
- the three persistence classes;
- metadata requirements;
- provenance and lineage;
- validation boundaries;
- cache and staging behavior;
- backup and retention;
- data movement through the Research Nexus;
- governed adoption of imported or preexisting data;
- portability from local development to external storage and server deployment.

This architecture intentionally avoids prescribing exact directory trees, file formats, database engines, object stores, partition strategies, or vendor-specific implementations. Those belong in technical design.

---

## 2. Governing Principle

> **Meaning is independent of storage. Persistence is independent of semantics. Provenance is mandatory.**

MTS must always distinguish:

1. **What an artifact means**
2. **How long it must be kept**
3. **Where its representation currently lives**
4. **What evidence and transformations produced it**

No filename, folder, database table, or storage device may substitute for semantic identity.

---

## 3. Design With the End in Mind

MTS data architecture SHALL be designed for the known mature system from the beginning.

The architecture must support:

- large historical datasets;
- live-market data;
- many concurrent research campaigns;
- repeated reuse of canonical evidence;
- scalable server-side storage;
- distributed or multi-worker processing;
- durable provenance;
- selective backup;
- automated cache retirement;
- future data classes not yet known;
- high-volume discovery and retrieval;
- migration across storage technologies.

A smaller initial deployment may use a single external volume and simple file-backed storage.

That implementation must preserve the same identity, lifecycle, metadata, and contract model intended for the mature server environment.

---

## 4. Semantic Data Hierarchy

MTS distinguishes the following semantic layers.

### 4.1 Source Data

Data acquired from an external or internal source before scientific interpretation.

Examples:

- historical OHLCV;
- live quotes;
- options data;
- block activity;
- dark-pool data;
- insider activity;
- fundamentals;
- market/sector context;
- economic data;
- reference tables.

Source data must preserve enough information to identify:

- source/provider;
- retrieval time;
- requested scope;
- source version if known;
- raw representation hash;
- transformations applied after acquisition.

### 4.2 Normalized Data

Source data transformed into a governed common representation without adding scientific interpretation.

Examples:

- normalized timestamps;
- standardized symbols;
- consistent units;
- harmonized field names;
- corporate-action adjusted price history where policy allows.

Normalization must be explicit and reproducible.

### 4.3 Observations

Direct observations about data.

Examples:

- daily return;
- gap size;
- closing range location;
- volume ratio;
- realized volatility;
- spread;
- options volume;
- block size.

An observation may be measured directly or deterministically derived.

Observation does not imply evidence.

### 4.4 Measurements / Features

Governed quantitative representations used for scientific analysis.

Examples:

- relative volume;
- volatility measures;
- momentum measures;
- moving averages;
- event descriptors;
- option-flow measurements;
- liquidity measurements;
- fundamental ratios.

Measurements must identify:

- definition;
- units;
- lookback;
- transformation logic;
- parameterization;
- version;
- source dependencies.

### 4.5 Evidence

Governed analytical material that bears on a research question or claim.

Evidence can:

- support;
- contradict;
- qualify;
- fail to resolve;
- demonstrate instability.

Evidence is contextual.

A measurement is not evidence merely because it exists.

### 4.6 Findings

Reproducible analytical conclusions drawn from evidence.

Examples:

- a relationship exists;
- no meaningful relationship detected;
- effect appears conditional;
- effect changes over time;
- effect fails out-of-sample;
- contradiction exists;
- evidence is insufficient.

### 4.7 Knowledge

Governed evidence-supported conclusions that have met the required lifecycle and promotion criteria.

Knowledge may be:

- candidate;
- validated;
- canonical;
- constrained;
- contradicted;
- superseded;
- retired.

### 4.8 Research State

Data describing active or completed scientific inquiry.

Examples:

- questions;
- hypotheses;
- research plans;
- campaigns;
- dependencies;
- missing-capability reports;
- unresolved questions;
- conclusions.

### 4.9 Decisions

Governed outputs of Decision Intelligence.

### 4.10 Outcomes

Observed results associated with decisions, monitored opportunities, or knowledge application.

### 4.11 Policies and Provenance

Operational policy snapshots and provenance records required to interpret or reproduce material system behavior.

---

## 5. The Three Persistence Classes

Every managed artifact must have a governed persistence class.

### 5.1 Class I — Source-Controlled System Assets

Canonical home: Git repository.

Examples:

- source code;
- Charter;
- architecture;
- standards;
- contracts;
- schemas;
- authored policies;
- tests;
- utilities;
- configuration templates;
- small deliberate fixtures.

Policy:

- Git: required;
- GitHub/off-machine source control: required;
- Research Nexus: not the primary home;
- retention: permanent through source history unless deliberately removed;
- backup: Git/off-machine source control is the primary protection mechanism.

### 5.2 Class II — Durable Research Nexus Assets

Canonical home: Research Nexus.

Examples:

- accepted source datasets;
- normalized datasets;
- evidence;
- findings;
- knowledge;
- research state;
- decisions;
- outcomes;
- policy snapshots;
- provenance.

Policy:

- Git: prohibited except intentionally reduced fixtures/examples;
- backup: required according to retention/recoverability policy;
- retention: semi-permanent or permanent.

#### Semi-Permanent

Retained while scientifically, operationally, or reproducibly useful.

Examples:

- accepted raw source history;
- normalized datasets;
- evidence supporting retained findings;
- completed campaigns;
- intermediate scientific data required for reproducibility;
- expensive-to-reacquire vendor data.

#### Permanent

Durable intellectual and decision history.

Examples:

- canonical knowledge;
- material supporting findings;
- critical provenance;
- promotion/supersession/retirement history;
- decisions;
- outcomes;
- critical research conclusions;
- operational policy snapshots governing material actions.

### 5.3 Class III — Transient / Cached Working Data

Examples:

- scratch;
- staging;
- decompressed working copies;
- temporary joins;
- query materializations;
- live buffers;
- temporary feature tables;
- temporary model outputs;
- worker-local context;
- test caches;
- reconstructable scheduler queue representations and locks.

Governed Task Requests, dependency records, and material execution
records required for recovery or provenance are Class II Research Nexus
state, not Class III queue data.

Policy:

- Git: prohibited;
- durable backup: normally prohibited;
- retention: temporary;
- deletion: automated by governed lifecycle rules.

---

## 6. Persistence Class Is Not Semantic Type

The system must not conflate:

```text
WHAT IS IT?
source data
measurement
evidence
finding
knowledge
decision
outcome
```

with:

```text
HOW IS IT PRESERVED?
Class I
Class II semi-permanent
Class II permanent
Class III transient
```

Example:

```text
artifact_type: EVIDENCE
storage_class: DURABLE_NEXUS
retention_class: SEMI_PERMANENT
lifecycle_state: VALIDATED
```

Another:

```text
artifact_type: MATERIALIZED_QUERY
storage_class: TRANSIENT_CACHE
retention_class: TEMPORARY
lifecycle_state: ACTIVE
```

These are independent classification axes.

---

## 7. Mandatory Data Metadata

Every governed durable data artifact must provide or inherit, as applicable:

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
source_provider
source_refs
parent_refs
dependency_refs
content_hash
validation_status
backup_requirement
backup_status
campaign_id
research_plan_id
decision_id
policy_refs
supersedes
superseded_by
tags
provenance
```

Exact required combinations belong in schemas and standards.

---

## 8. Time Semantics

Time handling must be explicit.

Artifacts should distinguish as appropriate:

- event time;
- market time;
- source timestamp;
- ingestion time;
- processing time;
- publication time;
- decision time;
- outcome observation time.

Time zones and market calendars must not be inferred ambiguously.

Where future information leakage matters, the system must be able to establish what information was available at the relevant decision or observation time.

---

## 9. Instrument Identity

Ticker symbols are not sufficient as permanent identity.

The data architecture must support a stable instrument identity model capable of handling:

- ticker changes;
- corporate actions;
- delistings;
- mergers;
- multiple listings;
- share classes;
- options contracts;
- futures/derivatives;
- ETFs and funds;
- future asset types.

Human-readable symbols remain discovery attributes.

Stable instrument identity belongs in governed metadata and reference data.

---

## 10. Source Provenance

Every accepted source artifact must preserve enough provenance to reconstruct its origin.

At minimum, provenance should support:

- provider/source;
- retrieval method;
- retrieval timestamp;
- request parameters;
- source scope;
- raw content hash;
- source filename or external identifier when useful;
- licensing/usage constraints if applicable;
- ingestion software version.

If a source is later normalized or transformed, the original source reference must remain recoverable.

---

## 11. Transformation Provenance

Every material transformation must be explicit.

A derived artifact should identify:

- input artifact refs;
- transformation identity;
- transformation version;
- parameterization;
- execution version;
- resulting content hash;
- validation status.

MTS must be able to distinguish between:

- raw acquisition;
- normalization;
- deterministic measurement;
- analytical transformation;
- evidence production;
- knowledge formation.

---

## 12. Data Quality and Validation

Structural validity, source quality, and scientific validity are distinct.

### Structural Validation

Examples:

- schema compliance;
- required fields;
- types;
- units;
- timestamp validity;
- referential integrity.

### Source / Data Quality Validation

Examples:

- missingness;
- duplicates;
- impossible values;
- stale data;
- continuity;
- corporate-action consistency;
- provider mismatch;
- outlier anomalies.

### Scientific Validation

Determines whether analytical conclusions are supported.

The Research Nexus records validation outcomes but does not confuse these levels.

---

## 13. Data Intake Boundary

External data does not become durable scientific data merely because it was downloaded.

Conceptually:

```text
External Source
      ↓
Acquisition / Staging
      ↓
Source Characterization
      ↓
Normalization
      ↓
QA
      ↓
Validation
      ↓
Accepted Publication
      ↓
Research Nexus
```

Rejected or invalid data may be retained temporarily for audit/diagnostics according to policy.

Accepted durable data receives governed identity, metadata, and provenance.

---

## 14. Cache and Staging Architecture

Staging and cache are operational mechanisms, not semantic categories.

### Staging

Used while an artifact is awaiting:

- validation;
- normalization;
- publication;
- reconciliation.

### Cache

Used to avoid repeated computation or repeated retrieval.

Examples:

- daily vendor snapshots;
- decompressed datasets;
- reusable materializations;
- feature tables;
- reference lookups.

Class III data must not accumulate indefinitely.

---

## 15. Cache Retirement

Cache retirement must be objective and metadata-driven.

A cache may become deletion-eligible when all applicable criteria are satisfied:

1. no active task depends on it;
2. no open research dependency requires it;
3. no decision/runtime dependency requires it;
4. required durable publication is verified;
5. required provenance is preserved;
6. re-materialization or recovery source is known where applicable;
7. retention policy permits deletion;
8. backup is not required or required promotion occurred first.

Deletion eligibility and deletion execution are separate states.

The system may mark an artifact eligible before an automated cleanup task actually removes it.

---

## 16. Daily and Short-Lived Market Data

MTS may ingest data whose operational value decays quickly.

Examples:

- live-market snapshots;
- intraday temporary buffers;
- daily scans;
- short-lived vendor responses.

Such data may remain Class III when:

- it is fully reproducible or reacquirable;
- it is not required to support a durable finding;
- it is not part of a material decision record;
- policy allows expiration.

If short-lived data becomes evidence for a material finding or decision, the required representation must be durably published or preserved by reference before cache retirement.

---

## 17. Rebuildable Data

Rebuildability is a governed property.

An artifact may be classified as rebuildable when:

- the original source remains accessible;
- deterministic regeneration is possible;
- required code/version is preserved;
- required source inputs remain available;
- recovery cost/time is acceptable.

Rebuildable does not automatically mean disposable.

Large historical vendor data may be semi-permanent if reacquisition is slow, costly, rate-limited, or uncertain.

---

## 18. Backup Architecture

Backup requirements must be driven by metadata and policy.

### Class I

Protected through Git and off-machine source control.

### Class II

Every Class II artifact carries an explicit backup requirement.
Permanent Class II assets require independent verified backup.
Semi-permanent Class II assets are independently backed up or designated
recoverable-from-source according to retention, reacquisition cost, and
recoverability policy.

### Class III

Normally excluded from durable backup.

The backup system must eventually select artifacts by metadata rather than directory names.

A governed backup should record:

- artifact identity;
- backup destination;
- backup timestamp;
- content hash or equivalent verification;
- verification status;
- recovery source;
- retention requirement.

Copying without verification is not a completed governed backup.

---

## 19. Backup Priority

Not all Class II artifacts require identical backup treatment.

Higher-priority protection should apply to:

- canonical knowledge;
- unique findings;
- irreplaceable evidence;
- research conclusions;
- provenance;
- decisions;
- outcomes;
- policy snapshots;
- expensive/non-recoverable source data.

Lower-priority or optional backup may apply to:

- easily reacquirable market files;
- deterministically regenerable measurements;
- reproducible intermediate datasets.

Exact policy belongs in `STORAGE_RETENTION_STANDARD.md` and related backup policy.

---

## 20. Data Deduplication

MTS should store canonical content once when practical.

Deduplication may use content hashes or equivalent identity mechanisms.

However, semantic identity and content identity are distinct.

Two artifacts may have identical bytes but different meaning or provenance.

Deduplication must not destroy:

- logical identity;
- provenance;
- lifecycle;
- relationships;
- policy distinctions.

---

## 21. Dataset Packaging

A governed dataset may consist of multiple related representations or files.

The architecture must support:

- package identity;
- member identity;
- package manifest;
- member hashes;
- schema declarations;
- lineage;
- atomic publication semantics.

The exact packaging format belongs in technical design.

---

## 22. Partitioning and Scale

The mature system will require scalable partitioning.

Potential partition dimensions may include:

- instrument;
- date/time;
- source;
- artifact type;
- event family;
- campaign;
- lifecycle state.

Architecture does not mandate a partitioning scheme.

Any scheme must preserve logical identity and allow backend changes without changing engine contracts.

---

## 23. Data Discovery

Clients must be able to discover data by meaning.

Queries may include:

- artifact ID;
- instrument;
- date/time;
- provider;
- artifact type;
- lifecycle state;
- validation state;
- research campaign;
- feature;
- event family;
- tags;
- upstream/downstream lineage;
- knowledge relationship;
- decision/outcome relationship.

Path traversal is not the canonical discovery mechanism.

---

## 24. Data Freshness

Freshness requirements depend on use.

Historical research may tolerate slower updates.

Live market and Decision Intelligence may require strict freshness.

Artifacts should carry enough metadata to evaluate staleness.

A consumer must not silently treat stale data as current when freshness is material to the task.

---

## 25. Live vs Historical Data

Historical and live data share semantic identity principles but may use different operational paths.

### Historical

Optimized for:

- reproducibility;
- batch research;
- large scans;
- long time horizons.

### Live

Optimized for:

- latency;
- freshness;
- streaming or frequent updates;
- short-lived state.

Material live observations that support durable decisions or research must eventually enter the Research Nexus with governed provenance.

Low-latency paths may not create a second hidden system of record.

---

## 26. Data Access Patterns

Engines should consume data through governed APIs or adapters.

They should not assume:

- physical directory location;
- local filesystem;
- specific database product;
- specific storage backend;
- vendor-specific layout.

The same logical query should remain valid when deployment changes from:

```text
Mac + external storage
```

to:

```text
server + managed storage
```

---

## 27. Data Locality and Performance

Performance may require local caches or data locality.

The Task Manager may consider data locality when scheduling workers.

Examples:

- run a worker near a large dataset;
- reuse a local materialization;
- avoid unnecessary network transfer.

These optimizations must not change artifact identity or canonical ownership.

---

## 28. Data Security and Access

Data access authority must be explicit.

Potential controls include:

- read permissions;
- publish permissions;
- lifecycle transition permissions;
- deletion permissions;
- migration permissions;
- policy-sensitive data restrictions.

Exact access-control technology belongs in technical design.

---

## 29. Data Deletion

Physical deletion is governed.

No component may delete durable data merely because:

- storage is low;
- a filename looks old;
- a newer artifact exists;
- a cache resembles a duplicate.

Deletion requires retention/lifecycle authority.

Permanent durable artifacts are normally retired, superseded, or archived rather than erased.

---

## 30. Adoption of Imported and Preexisting Data

Data adoption must preserve meaning and provenance, not source folder structure.

The source remains intact until governed adoption and verification are complete.

Migration flow:

```text
Inventory
   ↓
Classify
   ↓
Determine semantic type
   ↓
Determine persistence class
   ↓
Verify provenance
   ↓
Assign v2 identity
   ↓
Assign metadata
   ↓
Validate
   ↓
Publish to Research Nexus
   ↓
Verify durable publication
   ↓
Record migration audit
```

### Eligible Adoption Candidates

Examples:

- raw historical source data;
- accepted datasets;
- canonical evidence;
- reproducible findings;
- valuable knowledge;
- research conclusions;
- material provenance;
- decision/outcome history where valid.

### Not Automatically Migrated

Examples:

- caches;
- scratch output;
- duplicate payloads;
- temporary POC artifacts;
- stale compatibility files;
- obsolete generated reports;
- unknown/unclassified files.

---

## 31. Initial v2 Data Proof

The initial proof should use a narrow real dataset, such as AAPL, and demonstrate:

1. source acquisition/import;
2. source metadata;
3. validation;
4. durable publication;
5. retrieval;
6. deterministic measurement generation;
7. evidence production;
8. lineage traversal;
9. storage-class assignment;
10. backup classification;
11. cache creation;
12. cache retirement eligibility;
13. relocation of the Research Nexus root without engine code change.

Only after this passes should broad data adoption begin.

---

## 32. Repository and Data Boundary

The Git repository contains system definition.

The Research Nexus contains durable scientific/operational data.

The runtime/cache area contains transient work.

Conceptually:

```text
Git Repository
  → code / architecture / governance / schemas / tests

Research Nexus
  → durable source data / evidence / findings / knowledge / decisions / outcomes / provenance

Runtime / Cache
  → temporary staging / scratch / materializations / live buffers
```

These boundaries must remain explicit.

---

## 33. Path Resolution

Production code must not embed user-specific absolute paths.

Configuration must resolve:

- repository root;
- Research Nexus root;
- cache/runtime root;
- external provider configuration.

A path locates a representation.

It does not define semantic identity.

---

## 34. Data Architecture Conformance

An implementation conforms when it:

1. distinguishes semantic type from persistence class;
2. assigns governed metadata;
3. preserves stable identity;
4. preserves source and transformation provenance;
5. separates source, observation, measurement, evidence, finding, knowledge, decision, and outcome;
6. keeps Class II data out of Git;
7. keeps Class III data out of Git and durable backup unless reclassified;
8. supports semi-permanent and permanent retention;
9. performs metadata-driven cache retirement;
10. supports verified backup;
11. preserves live/historical semantics without creating duplicate systems of record;
12. supports backend relocation without engine changes;
13. prevents ungoverned deletion;
14. supports deliberate governed data adoption;
15. remains scalable to the mature server model.

---

## 35. Companion Governance

This architecture should be supported by canonical unversioned companion documents including:

```text
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/DATA_QUALITY_STANDARD.md

Governance/Contracts/DATASET_CONTRACT.md
Governance/Contracts/EVIDENCE_CONTRACT.md
Governance/Contracts/FINDING_CONTRACT.md

Governance/Schemas/
Governance/Policies/
```

---

## 36. Closing Principle

MTS data must never become an unmanaged accumulation of files.

The system must always be able to answer:

> **What is this data, where did it come from, what transformations produced it, what does it mean, how long must it be kept, is it backed up, what depends on it, and can it safely be deleted?**

If those questions cannot be answered, the data is not adequately governed.
