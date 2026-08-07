# Momentum Trading System — Configuration Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, and all applicable MTS governance standards, contracts, schemas, and policies.

---

## 1. Purpose

This standard defines how Momentum Trading System (MTS) configuration is represented, validated, resolved, versioned, overridden, secured, and preserved.

It governs configuration for:

- deployment;
- storage;
- Research Nexus locations;
- cache/staging/log locations;
- worker counts;
- engine capability settings;
- Task Manager limits;
- provider/source settings;
- quality profiles;
- research parameters;
- Decision parameters;
- policy references;
- feature flags;
- environment-specific values;
- future server deployment.

The goal is to ensure MTS behavior can change appropriately across environments without editing scientific or engine source code.

---

## 2. Governing Principle

> **Environment and policy differences belong in governed configuration, not hidden code.**

A change such as:

- moving storage;
- increasing workers;
- changing provider endpoints;
- changing cache locations;
- adjusting resource limits;

must not require rewriting engine scientific logic.

---

## 3. Design With the End in Mind

Configuration must support the known deployment progression:

```text
MacBook development
→ direct-attached storage
→ server deployment
→ multiple workers/services
→ future distributed infrastructure
```

Initial local convenience must not become permanent architectural coupling.

---

## 4. Configuration Domains

MTS distinguishes configuration domains.

Initial domains include:

```text
DEPLOYMENT
STORAGE
TASK_MANAGER
ENGINE
DATA_PROVIDER
DATA_QUALITY
RESEARCH
DECISION
LEARNING_GOVERNANCE
OBSERVABILITY
SECURITY
TEST
```

Each domain may have its own schema while sharing common resolution rules.

---

## 5. Configuration Is Not Policy

Configuration and policy are related but distinct.

Configuration describes values needed to operate a deployment.

Policy governs what is permitted or required.

Examples:

```text
configuration:
max_workers = 4

policy:
live Decision tasks have higher priority than background research
```

A hard risk limit belongs in policy, even if represented in a machine-readable file.

---

## 6. Configuration Is Not Scientific Evidence

A configuration value does not become evidence merely because an engine uses it.

Scientific parameters that materially affect a result must be preserved in provenance.

---

## 7. Canonical Configuration Location

Git-governed configuration templates and schemas belong under governed repository locations such as:

```text
Core/configuration/
Governance/Schemas/
Governance/Policies/
```

Runtime-resolved local configuration may exist outside Git where appropriate.

Secrets must not be committed.

---

## 8. Configuration Schema

Machine-consumed configuration must conform to governed schemas where incorrect structure could materially affect behavior.

A configuration schema should define:

- field names;
- types;
- required/optional status;
- allowed values;
- defaults;
- units;
- validation constraints;
- environment override behavior.

---

## 9. Explicit Resolution Order

Configuration resolution order must be deterministic and documented.

A typical pattern may be:

```text
explicit runtime argument
→ approved environment-specific configuration
→ canonical project configuration
→ governed default
```

The exact hierarchy must be defined per domain.

Hidden fallback behavior is prohibited.

---

## 10. No Silent Default for Material Settings

A missing material configuration value must not silently receive a scientifically consequential default unless that default is explicitly governed.

Examples include:

- Decision risk threshold;
- Research horizon;
- provider identity;
- storage root;
- market timezone.

---

## 11. Storage Configuration

Physical storage locations must be resolved through logical storage roles.

Examples:

```text
nexus_primary
nexus_backup
cache_root
staging_root
logs_root
temporary_root
```

Engines should not contain device-specific paths.

---

## 12. Storage Role Mapping

A deployment may map roles like:

```text
nexus_primary = /Volumes/...
```

or:

```text
nexus_primary = /srv/mts/nexus
```

or a future non-filesystem backend.

The role is stable.

The locator may change.

---

## 13. No Repository-Derived Durable Storage

Durable Research Nexus storage must not be inferred from the Git repository location.

Repository and durable state must be independently movable.

---

## 14. Repository Root Resolution

Runtime code may need to resolve the repository for Class I assets.

Repository discovery must use a canonical shared mechanism.

Each engine must not invent its own repo-root detection logic.

Repository root resolution is distinct from Research Nexus root resolution.

---

## 15. Current Working Directory

MTS must not require execution from a particular current working directory.

Commands should behave consistently from:

- repository root;
- nested directory;
- user home;
- automation/service environment.

---

## 16. User-Specific Paths

Canonical code/config templates must not hard-code:

```text
/Users/<developer>/...
```

User-specific paths may exist in local deployment configuration excluded from Git.

---

## 17. Environment Variables

Environment variables may be used for:

- deployment-specific values;
- secret references;
- runtime overrides.

Their names and semantics must be governed.

Environment variables must not create an undocumented alternate configuration system.

---

## 18. Secrets

Secrets include:

- API keys;
- passwords;
- tokens;
- private keys;
- brokerage credentials.

Secrets must not be stored in Git-governed plain-text configuration.

Configuration should reference secrets through an approved secret mechanism.

---

## 19. `.env` Files

Local `.env` files may be permitted for development when excluded from Git.

They are not the canonical source of governance.

Required variable names and meanings should be documented in templates or schemas.

---

## 20. Provider Configuration

External data-provider configuration should distinguish:

- provider identity;
- endpoint/environment;
- account/credential reference;
- requested product/data family;
- rate/quota constraints;
- timeout/retry settings.

Downstream scientific schemas remain provider-neutral where appropriate.

---

## 21. Provider Switching

Changing providers should primarily affect Data Intake/provider adapters and configuration.

It should not require rewriting Discovery, Research, or Decision logic that consumes normalized governed data.

---

## 22. Worker Configuration

Worker counts and resource limits are deployment configuration.

Examples:

```text
max_workers
max_discovery_workers
max_decision_workers
memory_limit
CPU concurrency
```

The initial deployment may use one worker.

The architecture must remain multi-worker capable.

---

## 23. Task Manager Configuration

Task Manager configuration may include:

- worker limits;
- queue polling interval;
- retry/backoff parameters;
- heartbeat interval;
- lease duration;
- task aging parameters;
- maintenance cadence;
- resource quotas.

Material behavioral rules should remain policy where appropriate.

---

## 24. Temporary Resource Constraints

Temporary limits imposed by current hardware must be clearly identifiable as deployment constraints.

Example:

```text
max_new_intake_items_per_day = 1
```

Such limits must not become embedded in engine code.

---

## 25. Engine Configuration

Engine-specific configuration may include:

- enabled capabilities;
- resource limits;
- algorithm parameters;
- supported schema/interface versions;
- temporary implementation switches.

Configuration must not expand engine authority beyond governance.

---

## 26. Scientific Parameters

Scientific parameters materially affecting research results must be:

- explicit;
- validated;
- preserved in provenance;
- versioned or snapshotted where material.

Examples:

- lookback windows;
- event thresholds;
- overlap rules;
- minimum sample size;
- feature definitions.

---

## 27. Research Configuration

Research configuration may define operational bounds such as:

- maximum iterations;
- maximum concurrent plans;
- compute budgets;
- campaign limits.

Scientific convergence criteria should remain governed under Research policy/standards rather than hidden configuration only.

---

## 28. Decision Configuration

Decision configuration may define deployment or implementation parameters.

Hard investment/risk authority must remain policy-controlled.

The Decision Engine must not gain broader permission because a local configuration value was edited.

---

## 29. Quality Configuration

Data Quality profiles should use governed configuration/schema definitions.

Quality thresholds must be identifiable by version.

---

## 30. Observability Configuration

Logging and metrics configuration may include:

- log level;
- sink;
- retention;
- structured format;
- metrics endpoint.

Changing observability settings must not alter scientific behavior.

---

## 31. Test Configuration

Tests must use isolated configuration.

Test settings should ensure:

- temporary Nexus roots;
- test providers/fakes;
- bounded resources;
- no production credentials;
- deterministic behavior where expected.

---

## 32. Environment Profiles

MTS may support named environment profiles such as:

```text
development
test
staging
production
```

Profiles must not become ambiguous collections of undocumented differences.

Each profile should be governed and inspectable.

---

## 33. Local Development Profile

A development profile may permit:

- one worker;
- local SSD;
- synthetic fixtures;
- non-production provider endpoints;
- verbose logging.

Scientific semantics must remain compatible with production contracts.

---

## 34. Production Profile

A production-like profile may require stricter controls for:

- immutable source state;
- committed software version;
- approved policies;
- verified Nexus;
- backup;
- observability;
- credentials;
- worker health.

---

## 35. Configuration Validation

Configuration must be validated before starting material services/tasks.

Invalid configuration must fail explicitly.

Examples:

- missing Nexus root;
- invalid worker count;
- unsupported provider;
- incompatible schema version;
- invalid timeout;
- conflicting storage roles.

---

## 36. Cross-Field Validation

Some configuration errors involve combinations of values.

Examples:

- backup location equals primary storage;
- Decision enabled but required policy missing;
- live mode enabled without freshness thresholds;
- worker count exceeds resource policy.

Cross-field validation must be supported.

---

## 37. Configuration Snapshot

Material executions should preserve the effective configuration that influenced them.

This may be:

- exact snapshot;
- immutable config artifact reference;
- content hash + versioned source reference.

It must be sufficient for reproducibility.

---

## 38. Effective Configuration

MTS must be able to display the resolved effective configuration after all approved overrides.

This helps answer:

> **What settings is the system actually using right now?**

The answer must not require mentally merging multiple files and environment variables.

---

## 39. Configuration Diff

Operational tooling should support comparing effective configurations between:

- environments;
- executions;
- deployments;
- time periods.

This is useful for diagnosing behavior changes.

---

## 40. Configuration Changes

Material configuration changes should be reviewable.

Changes to Class I configuration templates belong in Git.

Local deployment-specific changes should be auditable where they materially affect system behavior.

---

## 41. Hot Reload

Hot reload may be supported for safe configuration families.

Material scientific, risk, or authority settings should not hot-reload silently unless governance explicitly allows it.

A running task should normally retain the configuration snapshot with which it began.

---

## 42. Restart Requirements

Some configuration changes may require service restart.

The applicable component should state this clearly.

A changed file that a process has not reloaded must not be presented as active configuration.

---

## 43. Feature Flags

Feature flags may support gradual deployment.

Flags must have:

- defined purpose;
- owner;
- default;
- scope;
- removal criteria.

Permanent hidden forks in behavior through stale flags are prohibited.

---

## 44. Experimental Configuration

Experimental parameters must be labeled as such.

Experimental configuration must not silently influence production Decision behavior without approval.

---

## 45. Configuration and Provenance

Where configuration affects scientific results or Decisions, the corresponding execution/artifact must reference it.

Operationally irrelevant settings such as UI formatting need not contaminate scientific provenance.

---

## 46. Configuration and SoK

SoK scientific meaning must not depend on undocumented local configuration.

Any configuration affecting eligibility/ranking must be governed and attributable.

---

## 47. Configuration and Migration

Storage or server migrations should primarily update deployment configuration.

Artifact identity and scientific contracts remain unchanged.

---

## 48. Failover Configuration

If failover storage/services are supported, failover must be explicitly configured.

Silent arbitrary fallback is prohibited.

---

## 49. Backup Configuration

Backup topology should identify:

- primary role;
- backup role;
- schedule;
- verification behavior;
- retention;
- recovery expectations.

Backup configuration must satisfy Storage and Retention policy.

---

## 50. Portable Configuration

Configuration should use platform-neutral concepts where practical.

Mac-specific paths and shell conventions belong only in Mac deployment layers, not canonical engine contracts.

---

## 51. File Formats

Configuration may use formats such as:

```text
TOML
YAML
JSON
environment variables
database-backed config
```

The chosen format is implementation detail.

Schema and semantics are governing.

---

## 52. Configuration Ownership

Each configuration domain should have a defined owner.

Ownership includes responsibility for:

- schema;
- defaults;
- compatibility;
- documentation;
- validation.

---

## 53. Configuration Versioning

Material governed configuration definitions should be versioned.

Historical executions must remain interpretable after defaults change.

---

## 54. Default Changes

Changing a default is a behavioral change.

If a default materially affects scientific or Decision behavior, it must be governed and tested.

---

## 55. Deprecation

Deprecated configuration keys should have:

- replacement;
- warning period;
- removal version;
- migration instructions.

Unknown legacy keys must not be silently ignored if they could indicate intended behavior is not being applied.

---

## 56. Unknown Configuration

Strictness depends on domain.

For critical configuration, unknown fields should normally fail validation.

For extensible metadata, unknown fields may be tolerated if explicitly permitted.

---

## 57. CLI Overrides

CLI overrides may be useful for development and controlled execution.

Material overrides must be preserved in the effective configuration/provenance.

A CLI override must not bypass policy.

---

## 58. Human-Readable Status

The `mts` control interface should eventually support commands conceptually like:

```text
mts config show
mts config validate
mts config diff
```

Exact CLI design belongs in implementation.

---

## 59. Initial v2 Configuration Implementation

The first implementation should support:

1. canonical configuration loader;
2. schema validation;
3. logical storage roles;
4. repository-root resolution independent of CWD;
5. environment profile;
6. worker/resource limits;
7. provider configuration;
8. secrets by reference/environment;
9. effective configuration display;
10. configuration snapshot/hash for provenance;
11. isolated test configuration.

---

## 60. Testing Requirements

Tests should include:

- valid configuration;
- missing required setting;
- invalid type;
- unknown critical key;
- environment override;
- CLI override;
- CWD independence;
- repository move;
- Nexus move;
- primary/backup collision;
- one-worker development profile;
- multi-worker server profile;
- secret absent;
- configuration snapshot reproducibility.

---

## 61. Prohibited Practices

The following are prohibited:

- hard-coded developer paths in canonical code;
- engine-specific repo-root discovery logic;
- durable storage inferred from repo root;
- silent fallback storage;
- secrets committed to Git;
- scientifically material hidden defaults;
- configuration changes that silently alter running tasks;
- local configuration expanding policy authority;
- undocumented environment-variable behavior;
- production behavior controlled by stale experimental flags.

---

## 62. Conformance

A component conforms when it:

1. uses governed configuration;
2. validates effective configuration before material work;
3. separates deployment configuration from policy;
4. avoids user-specific hard-coded paths;
5. resolves logical storage roles;
6. works independently of current working directory;
7. preserves material scientific configuration in provenance;
8. keeps secrets out of Git;
9. exposes effective configuration;
10. supports environment-specific deployment without engine redesign;
11. preserves historical interpretability after defaults change.

---

## 63. Companion Governance

This standard operates with:

```text
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/DATA_QUALITY_STANDARD.md
Governance/Standards/RESEARCH_STANDARD.md
Governance/Standards/DECISION_STANDARD.md
Governance/Standards/LEARNING_GOVERNANCE_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md
Governance/Standards/CODING_STANDARD.md

Governance/Policies/
Governance/Schemas/
Core/configuration/
```

---

## 64. Closing Principle

MTS must always be able to answer:

> **What configuration is actually in effect, where did each material value come from, and can I move the system to a different machine or storage environment without editing engine logic?**

If deployment behavior depends on a developer remembering which line of source code to change, configuration is not sufficiently governed.
