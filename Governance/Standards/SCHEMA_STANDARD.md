# Momentum Trading System — Schema Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, `IDENTITY_STANDARD.md`, and `ARTIFACT_GOVERNANCE_STANDARD.md`.

---

## 1. Purpose

This standard defines how machine-readable structures are specified, identified, validated, versioned, evolved, and used across the Momentum Trading System (MTS).

Schemas are contracts for meaning, not merely file layouts.

This standard applies to:

- Research Nexus artifacts;
- datasets and records;
- metadata;
- task requests;
- execution records;
- engine inputs and outputs;
- research questions and plans;
- findings and knowledge;
- decisions and outcomes;
- policies and configuration where governed structure is required;
- inter-component messages;
- manifests;
- indexes and registries;
- future structured MTS objects.

---

## 2. Governing Principle

> **If two components exchange or persist structured information, its meaning must be governed independently of the code that happens to read it today.**

A Python dataclass, database table, JSON object, Parquet file, or function signature does not by itself constitute the canonical schema.

The canonical schema defines the semantic contract.

---

## 3. Design With the End in Mind

Schemas must support the mature MTS architecture from the beginning.

They must not assume:

- one process;
- one machine;
- one storage backend;
- one engine implementation;
- one programming language;
- one serialization format;
- one consumer;
- one current directory layout.

A schema accepted during local development must remain interpretable when MTS operates concurrently on a server.

---

## 4. Canonical Schema Registry

Governed schemas belong under:

```text
Governance/Schemas/
```

Each published schema must have:

```text
schema_id
schema_version
status
```

The Research Nexus may maintain runtime/indexed representations of schema metadata, but Git-governed schema definitions remain Class I system-definition assets.

---

## 5. Schema Identity

Schema identity follows `IDENTITY_STANDARD.md`.

Example:

```text
schema_id: mts.finding
schema_version: 1
```

A schema version is immutable after publication.

Changing the meaning of a published schema requires governed evolution.

---

## 6. Schema vs Serialization

Schema and serialization are separate.

One logical schema may have representations such as:

```text
JSON
Parquet
SQLite
PostgreSQL
message payload
Python object
```

Serialization details must not redefine semantic meaning.

Where representation-specific constraints exist, they must be documented explicitly.

---

## 7. Required Schema Content

A governed schema should define, as applicable:

- field names;
- field meanings;
- data types;
- required/optional status;
- nullability;
- units;
- controlled vocabularies;
- identifier/reference semantics;
- temporal semantics;
- cardinality;
- validation constraints;
- default behavior;
- compatibility rules;
- extension points.

A field name without defined meaning is insufficient.

---

## 8. Required vs Optional Fields

Required fields must be required because the artifact cannot be safely interpreted or governed without them.

Optional fields must have defined absence semantics.

The system must distinguish when relevant:

```text
unknown
not measured
not applicable
not available
withheld
zero
false
empty
```

These meanings must not be collapsed into `null` without governance.

---

## 9. Units

Numeric scientific fields must define units when units are meaningful.

Examples:

```text
price_currency
volume_shares
dollar_volume_usd
return_fraction
return_percent
duration_seconds
holding_period_bars
volatility_annualized
```

A consumer must not have to infer whether `5` means:

```text
5%
0.05
$5
5 shares
5 days
5 bars
```

---

## 10. Temporal Semantics

Time-bearing fields must define:

- timestamp/date meaning;
- timezone where applicable;
- market/session context where applicable;
- observation time;
- availability time when materially different;
- effective-from/effective-to semantics;
- inclusive/exclusive interval boundaries.

This is essential to prevent look-ahead contamination.

---

## 11. Observation Time vs Availability Time

Where data may become known after the event it describes, schemas should distinguish:

```text
observed_at
available_at
```

or equivalent governed fields.

Example:

A corporate event may have an effective date different from the time MTS could actually have known about it.

Historical research must use availability semantics appropriate to the experiment.

---

## 12. Identity References

Cross-artifact references must use governed identities rather than paths or display names.

A schema may contain fields such as:

```text
artifact_ref
source_refs
task_ref
execution_ref
instrument_ref
schema_ref
policy_ref
decision_ref
outcome_ref
```

Reference format must be consistent with the Identity Standard.

---

## 13. Provenance Fields

Artifact schemas must include or reference sufficient provenance.

Provenance structure should support:

- producer;
- execution;
- source identities;
- transformation lineage;
- software/model version;
- configuration/policy context.

Artifact-specific schemas may embed provenance or reference a common provenance schema.

---

## 14. Common Metadata Envelope

Durable Research Nexus artifacts should share a common governed metadata envelope rather than independently redefining core metadata.

The common envelope should include at least:

```text
artifact_id
artifact_version
artifact_type
schema_id
schema_version
created_at
producer
lifecycle_state
persistence_class
retention_class
backup_requirement
provenance
```

Artifact-specific payload schemas extend this envelope.

---

## 15. Controlled Vocabularies

Fields representing governed states or categories must use controlled vocabularies.

Examples:

```text
lifecycle_state
artifact_type
task_state
decision_result
direction
persistence_class
backup_requirement
relationship_type
```

Free text must not replace a controlled value when machine behavior depends on that value.

---

## 16. Extensible Taxonomies

MTS must avoid treating today's known categories as the complete future universe.

For extensible concepts such as:

- event families;
- feature families;
- instrument types;
- research question types;
- discovery types;

schemas should permit governed extension without redesigning unrelated components.

Extension must still be explicit and versioned.

---

## 17. Event Taxonomy

Event-related schemas must represent event families and subtypes without assuming one particular event pattern is the entire concept of an event.

An event schema should be capable of supporting families such as:

```text
directional price
volatility
liquidity
relative strength
derivatives
fundamental
market structure
future governed families
```

Duration, magnitude, direction, and context should be attributes where appropriate rather than being encoded solely into hard-coded event names.

---

## 18. Directional Symmetry

Schemas used for tradable directional research should support both long and short direction unless the artifact's scientific scope explicitly restricts direction.

A schema must not encode “bullish” as the default universal interpretation of price opportunity.

---

## 19. Instrument Generality

Instrument-related schemas should support future instruments without assuming all assets are common stocks.

Where relevant, structure should allow:

- equity;
- ETF;
- option;
- index;
- future supported instrument classes.

Instrument-specific fields should be isolated rather than contaminating universal schemas.

---

## 20. Data Vendor Neutrality

Canonical schemas should normalize semantic meaning independently of provider-specific field names.

Provider-specific raw schemas may be preserved for source fidelity.

Normalized schemas must not require every downstream engine to understand each vendor's naming conventions.

---

## 21. Raw Schema Preservation

Raw source data may retain provider-native schema where required for fidelity.

MTS should preserve:

- source schema/version when known;
- provider field names;
- acquisition metadata;
- source identity.

Normalization creates a new governed artifact rather than silently rewriting the raw source.

---

## 22. Schema Validation

Structured artifacts must be validated against the declared schema before governed publication where the artifact contract requires it.

Validation must detect, as applicable:

- missing required fields;
- invalid types;
- invalid controlled values;
- invalid references;
- invalid units;
- range violations;
- structural corruption;
- incompatible schema versions.

Validation results must be explicit.

---

## 23. Semantic Validation

Schema validation and scientific/data-quality validation are different.

Example:

```text
price = -42.00
```

may be syntactically numeric but scientifically invalid for a conventional equity price.

Schemas may encode obvious semantic constraints, but deeper quality rules belong in `DATA_QUALITY_STANDARD.md`.

---

## 24. Schema Versioning

Schema versions must be monotonic within a schema identity.

Published versions are immutable.

A new version is required when governed structure or meaning changes.

Version numbering format may be simple integer or semantic versioning where appropriate, but the chosen method must be consistent for the schema family.

---

## 25. Compatible Changes

Potentially compatible changes may include:

- adding an optional field with defined absence behavior;
- adding a new controlled vocabulary value where consumers are required to tolerate extensions;
- relaxing a non-semantic constraint.

Compatibility must be evaluated against actual governed consumers.

“Optional” does not automatically mean “compatible.”

---

## 26. Breaking Changes

Breaking changes include changes such as:

- removing a required field;
- changing field meaning;
- changing units;
- changing identifier semantics;
- changing temporal meaning;
- changing a type incompatibly;
- changing null semantics;
- narrowing a controlled vocabulary in a way that invalidates existing artifacts.

Breaking changes require:

- a new schema version;
- affected-consumer analysis;
- migration/compatibility plan;
- regression tests.

---

## 27. No Silent Semantic Change

A field must not retain the same name/version while changing meaning.

Example:

```text
return
```

cannot silently change from:

```text
fractional return
```

to:

```text
percentage points
```

without a schema change.

---

## 28. Deprecation

Schema elements may be deprecated before removal.

Deprecation metadata should identify:

- deprecated field/version;
- replacement;
- effective date/version;
- consumer migration expectations.

Deprecated data must remain interpretable for historical artifacts.

---

## 29. Forward and Backward Compatibility

Where interfaces require mixed-version operation, the contract must define:

- which producer versions a consumer accepts;
- which unknown fields may be ignored;
- which missing fields may be defaulted;
- whether downgrade is permitted;
- how incompatibility fails.

Compatibility behavior must not be guessed at runtime.

---

## 30. Schema Negotiation

For distributed/server operation, messages and persisted artifacts must declare their schema identity/version.

Consumers must reject unsupported incompatible versions explicitly.

They must not attempt heuristic interpretation of unknown payloads.

---

## 31. Defaults

Defaults must be used cautiously.

A default is acceptable only when its meaning is unambiguous and scientifically safe.

Defaults must not hide missing evidence or configuration.

For example, absent direction must not silently become `LONG`.

---

## 32. Unknown Fields

Whether consumers may ignore unknown fields must be defined per schema/interface family.

Extensible metadata may permit unknown fields.

Critical task, decision, policy, or identity structures may require strict validation.

---

## 33. Null and Missing Data

Schemas must define the distinction between:

- field absent;
- field present with null;
- field present with sentinel/controlled missing reason.

Scientific datasets should preserve missingness semantics when they affect analysis.

---

## 34. Numeric Precision

Schemas involving financial values must define precision expectations where rounding could affect results.

Where exact decimal representation is required, binary floating-point must not be assumed adequate without analysis.

Examples include:

- currency/accounting amounts;
- exact execution prices where precision matters;
- fees.

Analytical measurements may use floating point where scientifically appropriate.

---

## 35. Content Hash Canonicalization

If content hashes are calculated over structured data, the canonicalization method must be defined.

Equivalent semantic objects must not produce unstable hashes merely because of:

- dictionary ordering;
- whitespace;
- serialization formatting;
- non-semantic metadata ordering.

Representation hashes and semantic hashes should be distinguished when both are used.

---

## 36. Relationship Schema

Relationships between artifacts should use a common governed structure.

At minimum:

```text
source_ref
relationship_type
target_ref
created_at
producer
```

Additional relationship-specific metadata may be included.

---

## 37. Task Schema

Task requests must be governed structures, not ad hoc dictionaries.

The Task schema should eventually include:

```text
task_id
task_type
requested_capability
inputs
dependencies
priority
created_at
requester
policy/context
state
```

Execution attempts use a separate execution schema.

---

## 38. Execution Schema

Material execution records should include:

```text
execution_id
task_ref
engine_id
worker_id
started_at
completed_at
execution_state
software_version
input_refs
output_refs
diagnostics_refs
```

Retry attempts must remain distinguishable.

---

## 39. Research Schema

Research structures should support iterative work.

Examples include:

```text
question
hypothesis
research_plan
research_need
evidence_requirement
convergence_state
```

Research state must not depend on engine-local directory naming.

---

## 40. Finding Schema

Finding schemas should support:

- measured relationship;
- direction;
- magnitude/effect size;
- sample context;
- applicability;
- uncertainty;
- limitations;
- validation state;
- evidence references;
- contradiction references where applicable.

A finding must not be reduced to prose only.

---

## 41. Knowledge Schema

Knowledge schemas should support:

- proposition/conclusion;
- supporting findings/evidence;
- contradictory evidence;
- applicability;
- uncertainty;
- validation/replication state;
- recency;
- scientific status;
- decision eligibility;
- supersession.

The schema should enable SoK assembly without parsing human prose.

---

## 42. Decision Schema

Decision structures must distinguish semantic decision result from task execution state.

Decision payloads should support:

```text
decision_id
instrument_ref
decision_result
direction
instrument/implementation choice
entry/exit/scaling intent
time horizon
risk/reward context
knowledge_refs
evidence_refs
policy_ref
portfolio_state_ref
explanation
created_at
execution_ref
```

Exact fields belong in the Decision contract/schema.

---

## 43. Outcome Schema

Outcome schemas must preserve realized results separately from the prior decision.

They should support objective evaluation without rewriting historical decision context.

---

## 44. Policy and Configuration Schemas

Machine-enforced policies and material runtime configuration should use governed schemas when incorrect structure could alter scientific or investment behavior.

Configuration schema should distinguish:

- deployment configuration;
- scientific configuration;
- policy configuration;
- secrets/references to secrets.

---

## 45. Storage Independence

Schemas must not encode a particular physical storage root as semantic identity.

Fields may contain governed locators, but path semantics must remain deployment-neutral.

Moving from local SSD to Drobo, NAS, server filesystem, object store, or database must not require scientific schema redesign.

---

## 46. Database Independence

Canonical semantic schemas must not be defined solely by a particular database's table layout.

Database schemas may implement canonical schemas.

The implementation must document any mapping.

This preserves the ability to change storage technology.

---

## 47. Schema Ownership

Each schema family must have a governance owner.

Ownership means responsibility for:

- semantic definition;
- compatibility decisions;
- version changes;
- migration requirements;
- tests.

An engine implementation does not unilaterally own a cross-system schema merely because it was the first producer.

---

## 48. Schema Change Process

A material schema change must:

1. identify the current schema/version;
2. define the proposed semantic change;
3. classify compatibility;
4. identify producers and consumers;
5. define migration if needed;
6. update tests;
7. publish the new immutable schema version;
8. preserve historical interpretability.

Architecture changes require architecture review rather than being hidden inside schema changes.

---

## 49. Test Fixtures

Every important schema should have small canonical fixtures covering:

- minimum valid object;
- representative valid object;
- invalid missing field;
- invalid type;
- invalid controlled vocabulary;
- compatibility cases where applicable.

Fixtures belong with tests or governed schema test resources, not in production data stores.

---

## 50. Machine Readability

Canonical schemas should be machine-validatable.

Human-readable Markdown documentation may explain the schema, but prose alone is insufficient for structures that software must enforce.

Appropriate formats may include:

- JSON Schema;
- typed schema definitions;
- Parquet/Arrow schema definitions;
- database migration definitions;
- other governed machine-readable formats.

Choice of technology must follow implementation needs without changing semantics.

---

## 51. Documentation

Every schema family should have enough human-readable documentation to explain:

- purpose;
- semantic meaning;
- lifecycle;
- key fields;
- compatibility policy;
- examples.

Generated documentation may supplement but not replace governed semantic definitions.

---

## 52. Initial v2 Schema Set

Before full engine implementation, MTS should define at least:

```text
artifact envelope
provenance
artifact relationship
instrument
dataset
task request
execution record
research question
research plan
research need
finding
knowledge
decision
outcome
```

Additional schemas should be introduced only when required by actual system capability.

---

## 53. Conformance

A component conforms when it:

1. declares governed schema identity/version for structured durable artifacts;
2. validates required structures;
3. does not silently change field meaning;
4. uses governed identity references;
5. defines units and temporal semantics where material;
6. distinguishes missingness correctly;
7. preserves raw-source fidelity;
8. separates semantic schema from serialization/storage implementation;
9. rejects unsupported breaking versions explicitly;
10. preserves historical interpretability;
11. follows governed schema-change procedures.

---

## 54. Companion Governance

This standard operates with:

```text
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/DATA_QUALITY_STANDARD.md
Governance/Standards/CONFIGURATION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 55. Closing Principle

MTS must always be able to answer:

> **What does this field mean, which schema defines that meaning, which version was used, and can another compliant component interpret it without knowing the producer's private implementation?**

If not, the structure is not yet a governed MTS contract.
