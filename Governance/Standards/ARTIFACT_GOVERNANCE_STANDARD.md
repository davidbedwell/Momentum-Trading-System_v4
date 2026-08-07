# Momentum Trading System — Artifact Governance Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, and `IDENTITY_STANDARD.md`.

---

## 1. Purpose

This standard defines what constitutes a governed MTS artifact and how artifacts are created, classified, validated, published, related, promoted, superseded, retained, archived, and retired.

It applies to durable and governed objects including:

- source datasets;
- normalized datasets;
- derived datasets;
- observations;
- measurements;
- evidence;
- findings;
- knowledge objects;
- research questions;
- hypotheses;
- research plans;
- research needs;
- task requests and material execution records;
- State of Knowledge inputs;
- decisions;
- outcomes;
- policy snapshots;
- model and feature evaluation artifacts;
- reports when they carry governed scientific or operational meaning;
- future artifact families registered with MTS.

This standard governs artifact semantics and lifecycle. Physical storage and retention details are governed separately.

---

## 2. Governing Principle

> **MTS preserves evidence and history; it promotes conclusions only when explicit criteria are satisfied.**

An artifact becoming available does not automatically make it:

- valid;
- accepted;
- current;
- decision-eligible;
- permanent.

Those meanings require explicit governed state.

---

## 3. Objective Scientific Acceptance State

MTS SHALL NOT use undefined confidence language as a scientific acceptance criterion.

Artifact status must instead be based on observable and auditable properties such as:

- provenance completeness;
- schema validity;
- data-quality results;
- sample sufficiency;
- validation results;
- holdout performance;
- replication;
- contradiction state;
- applicability scope;
- recency;
- policy compliance;
- outcome evidence.

A human-readable interface may summarize these properties, but the underlying governance decision must remain objective and inspectable.

---

## 4. Artifact Families

Every governed artifact must declare an `artifact_type`.

Initial families include:

```text
SOURCE_DATA
NORMALIZED_DATASET
DERIVED_DATASET
OBSERVATION
MEASUREMENT
EVIDENCE
FINDING
KNOWLEDGE
RESEARCH_QUESTION
HYPOTHESIS
RESEARCH_PLAN
RESEARCH_NEED
TASK_REQUEST
EXECUTION_RECORD
DECISION
OUTCOME
POLICY_SNAPSHOT
MODEL_EVALUATION
FEATURE_EVALUATION
REPORT
```

This vocabulary may expand through governed schema change.

Artifact type is semantic. It is independent of persistence class.

---

## 5. Artifact Type Is Not Persistence Class

MTS uses separate dimensions for:

1. **what an artifact means**; and
2. **how long / where it should persist**.

For example, a dataset may be:

- Class II Permanent;
- Class II Semi-Permanent;
- Class III Cache.

A report may be:

- a durable governed research artifact;
- or a disposable human-readable rendering.

The semantic type alone must not determine Git, backup, or deletion behavior.

---

## 6. Mandatory Metadata

Every durable governed artifact must carry metadata sufficient to answer:

```text
What is it?
Which version is it?
Who/what produced it?
When was it produced?
From what inputs?
Under what schema?
Under what policy/context?
What is its lifecycle state?
What persistence class applies?
What may depend on it?
```

At minimum, durable artifacts should support:

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
content_hash where applicable
```

Additional required fields are defined by artifact-specific schemas.

---

## 7. Provenance

Durable artifacts must preserve provenance sufficient to reconstruct their scientific or operational origin.

Provenance may include:

- source artifact references;
- parent artifact references;
- task and execution references;
- engine and worker identities;
- software version;
- model version;
- configuration snapshot;
- policy snapshot;
- parameters;
- time window;
- instrument universe;
- data vendor/source;
- transformation lineage.

Missing required provenance blocks publication.

---

## 8. Artifact Lifecycle

MTS distinguishes artifact lifecycle from scientific ranking.

A general lifecycle vocabulary is:

```text
DRAFT
VALIDATING
VALIDATED
PUBLISHED
CURRENT
SUPERSEDED
RETIRED
INVALIDATED
ARCHIVED
```

Not every artifact family must use every state.

Exact allowed transitions belong in artifact-specific schemas/contracts.

---

## 9. Creation

Creation establishes an artifact identity and initial metadata.

Creation does not imply validation or publication.

New artifacts normally begin as:

```text
DRAFT
```

or another explicitly defined pre-publication state.

---

## 10. Validation

Validation answers whether an artifact satisfies defined requirements.

Validation may include:

- schema validation;
- integrity checks;
- data-quality checks;
- scientific checks;
- reproducibility checks;
- policy checks;
- contract checks.

Validation must produce explicit machine-readable results.

Validation failure must not be converted into publication success.

---

## 11. Publication

Publication means an artifact is admitted to the governed Research Nexus for discoverable use according to its artifact type and lifecycle state.

Publication is distinct from:

- creation;
- validation;
- promotion;
- decision eligibility.

A published artifact may still be:

- preliminary;
- contradictory;
- insufficiently supported;
- not decision-eligible.

Publication preserves information. It does not certify truth.

---

## 12. Promotion

Promotion changes the governed standing of an artifact based on objective criteria.

Promotion criteria must be:

- explicit;
- machine-evaluable where practical;
- versioned;
- artifact-family specific;
- auditable.

Examples may include:

- minimum sample size;
- validation pass;
- holdout confirmation;
- replication count;
- acceptable instability bounds;
- absence or bounded level of unresolved contradiction;
- sufficient provenance;
- applicability definition;
- recency requirements;
- outcome evidence.

Narrative confidence, persuasive wording, and successful execution are not valid promotion criteria.

---


## 13. Independent Research Gate Artifacts

When policy requires independent Accountability review, Research Admission and
Knowledge Promotion verdicts are governed artifacts.

A gate artifact must identify:

- evaluated proposal/candidate;
- gate type;
- applicable policy/criteria version;
- evidence references;
- criterion results;
- verdict;
- limits or blocking reasons;
- producer;
- effective timestamp.

The interested research proposer may not manufacture the independent gate
artifact required to promote its own output.

## 14. Scientific Status

Scientific status is distinct from lifecycle status.

A finding or knowledge artifact may carry governed scientific properties such as:

```text
evidence_strength
validation_status
replication_status
contradiction_status
stability_status
applicability_status
recency_status
decision_eligibility
```

These properties should be measurable rather than collapsed prematurely into one opaque score.

---

## 15. Knowledge Ranking

MTS may rank knowledge for retrieval, prioritization, or decision context.

Ranking must not rewrite scientific history.

A ranking model may consider:

- relevance to current question;
- applicability to current market/instrument context;
- validation strength;
- replication;
- predictive or economic contribution;
- recency;
- contradiction burden;
- outcome history;
- retrieval frequency;
- computational cost.

Usage frequency alone must never determine scientific validity.

A rarely used but strongly supported artifact remains valid.

A frequently accessed artifact does not become valid merely through use.

---

## 16. Current State of Knowledge

The State of Knowledge (SoK) is a governed logical view assembled from Research Nexus artifacts.

SoK is not itself synonymous with “all stored knowledge.”

A SoK view contains the current governed knowledge relevant to a defined subject, time, and use.

It may include:

- current applicable knowledge;
- uncertainty or confidence qualification;
- applicability conditions;
- validation context;
- recency;
- material limitations;
- decision-eligibility state;
- references to supporting provenance when required.

Contradictory evidence, unresolved questions, rejected hypotheses, and research debris are not themselves canonical knowledge and are not loaded into the ordinary Decision SoK. They belong to Active Research State or Historical Research Lineage unless a scoped Research query explicitly requests them.

SoK assembly must preserve references to the underlying canonical knowledge identities and enough provenance to explain their current status.

---

## 17. Evidence Preservation

Evidence retention is selective and governed by scientific value, reproducibility, active dependency, and reconstruction cost.

MTS must preserve enough durable lineage to answer:

- why a current or historical material conclusion was reached;
- what evidence materially supported it;
- whether a material contradiction changed its applicability, uncertainty, eligibility, supersession, or retirement;
- when that change occurred;
- what superseded it.

MTS is not required to preserve every failed hypothesis, transient contradiction, duplicate analysis, or reproducible intermediate payload permanently.

---

## 18. Findings vs Knowledge

A `FINDING` is an observed or derived scientific result.

A `KNOWLEDGE` artifact is a governed interpretation or reusable conclusion derived from one or more findings/evidence objects.

Findings do not automatically become knowledge.

Knowledge must reference its supporting evidence/findings and applicability.

---

## 19. Observation Is Not Causation

Discovery and analysis artifacts must distinguish:

```text
observed association
conditional association
interaction
temporal relationship
predictive relationship
causal claim
```

A causal claim requires governance beyond ordinary observational discovery.

MTS must not silently promote correlation into causation.

---

## 20. Contradiction

Contradiction is a governed research condition, not a class of canonical knowledge.

When material artifacts conflict, MTS should record enough active state to identify:

- the affected knowledge or candidate;
- the context in which the conflict occurs;
- whether applicability differences may explain it;
- whether a Research Plan is required;
- whether current uncertainty or decision eligibility should change.

Contradictory working material is default-to-expire after resolution. Durable retention requires objective justification: the contradiction materially changed knowledge, applicability, uncertainty, decision eligibility, supersession/retirement, or is otherwise necessary for reproducibility or audit.

Resolved contradictions should normally leave a compact durable resolution record rather than an indefinite collection of bulky contradictory payloads.

---

## 21. Applicability

Knowledge and findings must define where they apply when applicability is material.

Applicability may include:

- instrument;
- asset class;
- liquidity range;
- volatility range;
- market regime;
- event family;
- direction;
- holding horizon;
- target/stop model;
- date range;
- feature availability;
- portfolio context.

An artifact cannot be assumed universal merely because applicability metadata is absent.

---

## 22. Uncertainty

Material research artifacts must represent uncertainty where scientifically relevant.

Uncertainty may include:

- confidence intervals;
- effect-size uncertainty;
- sample limitations;
- missing data;
- contradictory evidence;
- model uncertainty;
- regime uncertainty;
- external validity limits.

Uncertainty must not be hidden by a binary accepted/rejected label.

---

## 23. Insufficient Evidence

`INSUFFICIENT_EVIDENCE` is a legitimate research result.

It is not a software failure.

A research process may conclude that:

- sample size is inadequate;
- available features are insufficient;
- data coverage is incomplete;
- evidence conflicts;
- no stable relationship is supported.

Such results should be preserved when they prevent repeated unproductive research or inform future capability needs.

---

## 24. Missing Capability

A research or decision process may determine that MTS lacks the data, tool, feature, model, or engine capability required to answer a question.

This must be represented explicitly.

A missing capability may generate a governed `RESEARCH_NEED` or capability request.

It must not cause the system to fabricate a conclusion.

---

## 25. Supersession

Supersession preserves history.

A superseding artifact must explicitly reference the artifact/version it supersedes.

The prior artifact remains resolvable and may remain scientifically relevant for historical contexts.

Supersession does not imply deletion.

---

## 26. Invalidation

Invalidation is stronger than supersession.

An artifact may be invalidated when:

- corruption is discovered;
- provenance is materially false or incomplete;
- a methodological defect invalidates the result;
- the wrong source data was used;
- the artifact violates a governing contract.

Invalidation must record:

- reason;
- authority;
- timestamp;
- affected dependents where known;
- remediation status.

Invalidated artifacts must not silently disappear.

---

## 27. Retirement

Retirement means an artifact is no longer active/current for ordinary use.

Retirement may occur because it is:

- obsolete;
- no longer applicable;
- replaced;
- no longer worth retaining in active storage;
- outside current research scope.

Retirement must respect retention and dependency rules.

---

## 28. Deletion

Deletion is a storage lifecycle action, not a scientific status.

Permanent governed knowledge/evidence must not be deleted merely because it is:

- old;
- low-ranked;
- rarely accessed;
- contradicted;
- superseded.

Deletion eligibility is governed by persistence class, retention policy, dependencies, recoverability, legal/licensing constraints, and backup status.

---

## 29. Dependency Protection

An artifact must not be deleted while required by a durable dependent artifact unless the dependent can remain scientifically and operationally valid without it.

Dependency checks must consider:

- provenance chains;
- active research;
- pending tasks;
- decision explainability;
- reproducibility;
- backup/recovery;
- audit requirements.

---

## 30. Cache Promotion

Class III material may become scientifically significant.

Before a cache/scratch object is promoted into durable Nexus state it must receive:

- governed identity;
- artifact type;
- schema validation;
- provenance;
- persistence classification;
- retention metadata;
- backup requirement;
- lifecycle state.

A file does not become durable knowledge merely because someone decides not to delete it.

---

## 31. Raw Source Preservation

Canonical raw source data that is admitted as durable scientific input should be immutable.

Corrections should normally produce:

- a new source version;
- a corrected source artifact;
- explicit supersession/invalidation metadata.

Raw source mutation in place undermines reproducibility.

---

## 32. Derived Artifact Reproducibility

Derived artifacts should record enough information to reproduce them where practical.

This may include:

- input identities/versions;
- code/software version;
- configuration;
- schema version;
- transformation parameters;
- execution identity.

Whether the derived payload itself is permanent or rebuildable is a separate storage decision.

---

## 33. Decision Artifacts

Decision artifacts are durable when they materially affect or explain investment action.

A Decision artifact must reference:

- current-state inputs;
- relevant knowledge/evidence;
- policy snapshot;
- portfolio/exposure state where applicable;
- instrument identity;
- decision result;
- decision context;
- producing execution.

Decision artifacts must not rewrite the underlying research artifacts they consume.

---

## 34. Outcome Artifacts

Outcomes must be preserved separately from the decisions that preceded them.

An outcome may include:

- realized return;
- risk realized;
- time in trade;
- adverse/favorable excursion;
- execution quality;
- scalability observations;
- exit reason;
- policy compliance.

Outcomes feed Learning & Governance.

They do not retroactively alter what the Decision Engine knew at decision time.

---

## 35. Temporal Integrity

MTS must preserve what was knowable at the relevant time.

Backtests, simulations, and decision evaluation must distinguish:

- information available at decision time;
- information learned later.

Future information must not be silently inserted into historical decision context.

---

## 36. Relationship Governance

Artifacts may be connected using governed relationship types.

Initial conceptual relationships include:

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

Relationships must reference governed identities.

Relationship schemas and controlled vocabulary belong in Governance/Schemas.

---

## 37. Producer Authority

An engine may publish only artifact families authorized by its contract.

Examples:

- Data Intake may publish governed source/normalized datasets and intake QA;
- Discovery may publish observations, measurements, evidence, and findings;
- Research Director may publish questions, hypotheses, plans, research needs, and governed research conclusions within its authority;
- Decision may publish decisions;
- Learning & Governance may publish outcome evaluations and governance recommendations.

An engine must not acquire authority merely because it can technically write to the Nexus.

---

## 38. Publication Boundary

Engines should publish through governed Research Nexus interfaces.

Direct uncontrolled writes to canonical durable stores are prohibited.

The publication boundary must enforce:

- identity;
- schema;
- provenance;
- lifecycle;
- authorization;
- persistence metadata;
- collision/duplicate rules.

---

## 39. Idempotency

Repeated submission of the same governed artifact/version must not create uncontrolled duplicates.

Where identical submission is valid, publication should be idempotent.

Where content differs for the same immutable identity/version, publication must fail or require governed versioning.

Silent overwrite is prohibited.

---

## 40. Objective Promotion Records

Every promotion must be explainable.

A promotion record should identify:

```text
artifact_ref
prior_status
new_status
criteria_version
criterion_results
evaluation_execution_ref
timestamp
```

Human approval, when required, should also be recorded as an explicit governed input rather than an undocumented judgment.

---

## 41. Demotion and Re-evaluation

Scientific standing may decline when new evidence appears.

MTS must support governed:

- demotion;
- revalidation;
- contradiction escalation;
- loss of decision eligibility;
- supersession;
- retirement.

Prior promotion history remains preserved.

---

## 42. Ranking Is Not Lifecycle

Retrieval rank and lifecycle status are independent.

For example:

```text
CURRENT + low retrieval relevance
CURRENT + high retrieval relevance
SUPERSEDED + historically important
VALIDATED + not decision-eligible
```

A ranking engine must not silently mutate lifecycle.

---

## 43. Permanent vs Semi-Permanent Knowledge

Knowledge artifacts expected to remain part of the durable scientific record are Class II Permanent.

Rebuildable intermediate scientific assets may be Class II Semi-Permanent when:

- the authoritative inputs remain available;
- the transformation is reproducible;
- the reacquisition/recompute cost is acceptable;
- policy explicitly allows reconstruction instead of permanent backup.

The classification must be metadata-driven.

---

## 44. Artifact Registry

The Research Nexus must maintain a canonical catalog/registry capable of resolving:

- artifact identity;
- version;
- type;
- lifecycle;
- persistence class;
- schema;
- provenance;
- relationships;
- available representations;
- current locator(s).

The registry is authoritative for artifact metadata.

Physical directory enumeration is not an artifact registry.

---

## 45. Auditability

Material lifecycle actions must be auditable.

This includes:

- publication;
- validation;
- promotion;
- demotion;
- supersession;
- invalidation;
- retirement;
- deletion authorization;
- backup/recovery events where material.

Audit records should be append-oriented.

---

## 46. Human-Readable Reports

Human-readable reports are views unless explicitly registered as canonical artifacts.

The underlying machine-readable artifact remains authoritative.

A PDF, text file, dashboard, or UI rendering must not become the only copy of scientific state.

---

## 47. Git Boundary

Class I system-definition assets belong in Git according to repository policy.

Scientific/data artifacts do not belong in Git merely because they are important.

Examples normally outside Git:

- raw market datasets;
- derived research datasets;
- evidence payloads;
- knowledge stores;
- decisions/outcomes at scale;
- caches.

Git governs software and system definition.

The Research Nexus governs durable scientific/operational state.

---

## 48. Backup Boundary

Backup status is artifact metadata.

Every Class II artifact must have an explicit backup requirement.

Permanent Class II artifacts require independent verified backup.

Semi-Permanent Class II artifacts may be:

- independently backed up; or
- explicitly designated recoverable-from-source.

Backup policy does not change artifact identity.

---

## 49. Adoption of Imported or Preexisting Artifacts

Imported or preexisting artifacts must be adopted according to semantic meaning, not copied according to source directory structure.

Adoption should determine:

- artifact type;
- identity;
- provenance;
- lifecycle;
- persistence class;
- retention class;
- backup requirement;
- relationships;
- whether the asset remains scientifically useful.

Obsolete or noncanonical implementation artifacts need not be adopted merely because they exist.

---

## 50. Initial Implementation Requirements

The first Research Nexus implementation must support at least:

1. artifact registration;
2. artifact identity/version;
3. schema association;
4. provenance references;
5. lifecycle state;
6. persistence/retention metadata;
7. content hash where applicable;
8. relationship registration;
9. duplicate/collision protection;
10. lookup by identity;
11. metadata search;
12. append-oriented lifecycle audit.

It does not need every future artifact family before the architecture can operate.

---

## 51. Testing Requirements

Artifact governance tests must include:

- required metadata enforcement;
- invalid schema rejection;
- missing provenance rejection;
- duplicate idempotency;
- conflicting immutable publication rejection;
- lifecycle transition validation;
- supersession preservation;
- invalidation preservation;
- dependency-protected deletion;
- cache-to-durable promotion;
- backend relocation without identity change;
- relationship resolution;
- unauthorized producer rejection.

---

## 52. Conformance

A component conforms when it:

1. publishes only authorized artifact types;
2. uses governed identities;
3. preserves provenance;
4. validates against governed schemas;
5. distinguishes publication from promotion;
6. uses objective promotion criteria;
7. preserves contradictory/negative evidence;
8. represents insufficient evidence explicitly;
9. does not silently overwrite published artifacts;
10. preserves superseded/invalidated history;
11. separates lifecycle from ranking;
12. respects persistence and dependency rules;
13. uses governed Nexus publication interfaces.

---

## 53. Companion Governance

This standard operates with:

```text
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/DATA_QUALITY_STANDARD.md
Governance/Standards/RESEARCH_STANDARD.md
Governance/Standards/DECISION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 54. Closing Principle

MTS must never confuse:

> **stored** with **valid**,
> **valid** with **current**,
> **current** with **relevant**,
> **relevant** with **decision-eligible**,
> or **frequently used** with **scientifically supported**.

The Research Nexus preserves the scientific record. Governance determines how that record may be interpreted and used.
