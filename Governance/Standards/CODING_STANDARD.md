# Momentum Trading System — Coding Standard

**Status:** Canonical

## 1. Purpose

This standard governs implementation practices that protect MTS architecture, scientific integrity, maintainability, testability, and future scalability.

It is intentionally focused on consequential engineering rules rather than cosmetic style preferences.

## 2. Governing Principle

> Code must implement the architecture; the architecture must not gradually become whatever the code happened to do.

## 3. Architecture First

When implementation convenience conflicts with a canonical contract, standard, or architecture decision, the implementation changes.

Do not weaken architecture merely to make an old implementation pass.

## 4. No Legacy-by-Default

MTS v2 is a clean architecture.

Legacy behavior, import paths, file layouts, compatibility aliases, adapters, or duplicated interfaces must not be retained unless there is an explicit current requirement for them.

“Something might still use it” is not sufficient justification.

## 5. Dependency Direction

Dependencies must follow canonical architectural boundaries.

Engines may depend on governed Core services and interfaces.

They must not depend on another engine's private implementation.

## 6. Engine Independence

An engine must not:

- import another engine's private modules;
- read another engine's private files;
- infer another engine's directory layout;
- manipulate another engine's runtime state.

Cross-engine interaction occurs through governed contracts and shared infrastructure.

## 7. Core

`Core/` contains system-wide infrastructure/capabilities that genuinely serve multiple components.

Do not move domain logic into Core merely to avoid designing a proper interface.

## 8. Shared Utilities

A utility belongs in shared infrastructure only when its semantics are genuinely shared.

Copying similar helper code across engines should trigger review for a canonical shared capability.

Premature generic abstraction is also discouraged.

## 9. Repository Root

Repository-root resolution must use the canonical shared mechanism.

No engine may implement its own chain of `parents[n]`, hard-coded directory assumptions, or developer-specific repository path.

## 10. Filesystem Access

Filesystem access must use governed logical roles and interfaces where applicable.

Do not hard-code:

```text
/Users/...
/Volumes/...
Warehouse/...
Research/...
```

or other physical deployment paths into scientific/domain logic.

## 11. Research Nexus Access

Durable Class II state must be read and written through canonical Research Nexus interfaces.

Direct arbitrary writes into Nexus storage are prohibited.

## 12. Git State vs Durable State

Class I code/governance assets may live in Git.

Research data, evidence, Decisions, Outcomes, task state, and other Class II durable state must not be treated as repository files merely because filesystem storage is convenient.

## 13. Cache Access

Class III cached/transient state must be clearly separated from canonical durable state.

Code must remain correct if cache content disappears.

## 14. Configuration

Material operational values belong in governed configuration.

Do not embed worker counts, storage roots, provider endpoints, retry counts, scientific thresholds, or environment assumptions as unexplained literals in domain code.

## 15. Constants

True semantic constants may be defined in code.

Configurable policy, deployment settings, and experimental parameters are not constants merely because they currently have one value.

## 16. Secrets

Secrets must never be embedded in source code, committed configuration, test fixtures, logs, or error messages.

## 17. Contracts

Public component boundaries must use explicit governed contracts.

Avoid passing loosely structured dictionaries across major boundaries when a governed schema/model exists.

## 18. Schemas

Schema validation should occur at trust boundaries.

Internal code may rely on validated typed representations rather than repeatedly revalidating every field.

## 19. Types

Use type annotations for public interfaces and material domain structures.

Types should clarify semantics, not merely satisfy a checker.

Prefer specific domain types/enums over ambiguous strings where practical.

## 20. Domain Models

Material concepts should have explicit models.

Examples:

```text
Task Request
Execution Record
Research Question
Research Plan
Finding
Knowledge Candidate
Decision
Outcome
Evaluation
```

Do not reduce important domain concepts to anonymous dictionaries scattered across the codebase.

## 21. Identity

Canonical identities must be generated and handled through governed identity mechanisms.

Do not invent local ad hoc ID formats inside individual engines.

## 22. Time

Use explicit timestamps with governed timezone semantics.

Do not rely on local-machine timezone for scientific meaning.

Historical availability time and observation time must remain distinguishable where required.

## 23. Money and Numeric Precision

Use numeric representations appropriate to the scientific/financial calculation.

Do not introduce rounding merely for display into canonical calculations.

Display formatting and stored/calculated values are separate concerns.

## 24. Functions

Functions should have one coherent responsibility.

Large functions that combine:

- acquisition;
- transformation;
- scientific interpretation;
- persistence;
- reporting;

should normally be decomposed.

## 25. Modules

Modules should correspond to coherent responsibilities.

Avoid “utils.py” becoming an ungoverned dumping ground.

## 26. Side Effects

Side effects should be explicit and concentrated at appropriate boundaries.

Scientific transformations should be pure/deterministic where practical.

This improves testing and reproducibility.

## 27. Import-Time Behavior

Modules must not perform material work at import time.

Importing a module must not:

- create Nexus state;
- start workers;
- contact providers;
- mutate configuration;
- execute research.

## 28. Entry Points

Executable behavior should use explicit entry points.

Library modules should remain import-safe.

## 29. Errors

Errors must preserve semantic meaning.

Do not catch broad exceptions and convert every failure into a generic success/empty result.

## 30. Exception Handling

Catch exceptions where the code can:

- add useful context;
- translate into a governed error;
- retry according to policy;
- clean up safely.

Otherwise allow the failure to propagate to the appropriate boundary.

## 31. No Silent Failure

The following patterns are prohibited for material work:

```python
try:
    ...
except Exception:
    pass
```

and equivalent behavior that discards errors.

## 32. Domain Results vs Exceptions

Expected domain outcomes such as:

```text
NO_ACTION
INSUFFICIENT_EVIDENCE
MISSING_CAPABILITY
```

should be represented as governed semantic results, not exceptions.

Exceptions represent execution/software/infrastructure failures.

## 33. Logging

Use structured logging through canonical observability facilities.

Logs should identify relevant IDs such as:

```text
task_id
execution_id
artifact_id
campaign_id
decision_id
```

where applicable.

## 34. Logging Is Not State

Do not require log parsing to determine canonical task, research, or Decision state.

Logs are diagnostic evidence, not the system of record.

## 35. Print Statements

Ad hoc `print()` may be acceptable during local exploration.

Production/core execution should use canonical logging/status mechanisms.

## 36. Provenance

Material outputs must preserve provenance through canonical artifact interfaces.

Do not rely on filenames to encode all provenance.

## 37. Filenames

Filenames are human navigation aids.

They are not canonical identity.

Do not parse scientific meaning from a filename when governed metadata exists.

## 38. Mutability

Canonical historical artifacts should be treated as immutable where governance requires.

Updates should create new versions, state transitions, or supersession relationships rather than silently rewriting history.

## 39. DataFrames

DataFrames may be used internally for tabular computation.

They should not become an untyped substitute for domain contracts at major component boundaries.

## 40. Provider Adapters

Provider-specific formats and semantics belong behind Data Intake/provider adapters.

Do not leak vendor-specific field names throughout Discovery, Research, or Decision code when canonical normalized fields exist.

## 41. Scientific Calculations

Scientific calculations must explicitly define:

- inputs;
- units;
- windows;
- alignment;
- missing-data behavior;
- timing semantics.

Material formulas should be testable independently of I/O.

## 42. Look-Ahead Protection

Code performing historical research or simulation must make future-information access difficult by design, not merely by developer discipline.

Prefer point-in-time interfaces and bounded data views.

## 43. Randomness

When randomness affects reproducibility, use explicit controlled random generators/seeds and preserve relevant state/configuration.

## 44. Concurrency

Code must not assume it will always be the only worker.

Shared mutable state requires governed coordination.

Local globals are not an acceptable cross-worker coordination mechanism.

## 45. Idempotency

Task handlers should be idempotent where practical.

Retries must not create duplicate canonical artifacts or duplicate external effects unintentionally.

## 46. Transactions / Atomic Publication

Multi-part canonical publication should use atomic or transactionally represented mechanisms where required by contract.

Do not expose partially complete logical artifacts as complete.

## 47. Temporary Files

Temporary files must use designated temporary/staging locations.

They must not masquerade as canonical artifacts.

Cleanup should be safe after interruption.

## 48. Resource Management

Files, database connections, provider sessions, locks, and other resources should use deterministic cleanup patterns.

Prefer context managers or equivalent lifecycle constructs.

## 49. Performance

Correctness comes before micro-optimization.

When optimization is required, measure first and preserve the simpler correct implementation as the behavioral reference where practical.

## 50. Caching

Caching is an optimization.

Business/scientific correctness must not depend on cache survival.

Cache keys must account for inputs/versions sufficiently to prevent stale semantic collisions.

## 51. Comments

Comments should explain:

- why;
- invariants;
- scientific assumptions;
- non-obvious constraints.

Avoid comments that merely restate the code.

## 52. Docstrings

Public interfaces and non-obvious domain logic should have concise docstrings describing contract and semantics.

Do not use documentation to excuse unclear architecture.

## 53. Naming

Names should reflect domain meaning.

Prefer:

```text
research_plan
decision_request
available_at
```

over vague names such as:

```text
data2
thing
tmp_final
manager_new
```

## 54. Version Suffixes

Do not proliferate implementation filenames such as:

```text
engine_new.py
engine_final.py
engine_v2_fixed.py
```

Git provides software history.

Version identifiers belong where required by governed interfaces/artifacts, not as routine source-file naming.

## 55. Dead Code

Dead code should be removed.

Do not preserve large commented-out implementations “just in case.”

Git preserves history.

## 56. Compatibility Code

Compatibility layers require an identified compatibility requirement and planned retirement condition.

They must not become permanent because removing them feels risky.

## 57. Deprecation

When a live public interface must be deprecated, define:

- replacement;
- warning behavior;
- migration path;
- removal condition.

For v2 code not yet depended upon externally, prefer clean replacement over unnecessary deprecation machinery.

## 58. TODOs

TODOs should describe actionable unresolved work.

Critical architectural defects must not be hidden indefinitely behind TODO comments.

## 59. Testing

New material behavior must include appropriate tests under `Tests/`.

Bug fixes should normally include regression tests.

## 60. Testability

Design code so scientific logic can be tested without:

- live provider calls;
- production Nexus state;
- real broker access;
- developer-specific paths.

## 61. Dependency Injection

External dependencies such as storage, clocks, providers, and execution services should be injectable where doing so materially improves testability and architecture.

Avoid dependency-injection ceremony where no boundary benefit exists.

## 62. Clock Access

Time-sensitive domain logic should use a controllable clock abstraction where needed for deterministic historical and expiry testing.

## 63. Code Generation

Generated code, if introduced, must have a clear source-of-truth and regeneration process.

Do not manually edit generated artifacts without an explicit workflow.

## 64. External Libraries

New dependencies should be justified by capability and maintenance value.

Avoid adding a large framework for a small function that can be implemented safely and clearly.

## 65. Dependency Pinning

Runtime/build dependencies should be managed through a canonical dependency mechanism with reproducible versions appropriate to the deployment strategy.

## 66. Security

Validate untrusted external inputs at boundaries.

Do not execute provider/user-derived strings as code or shell commands.

Use safe subprocess argument handling rather than shell interpolation where practical.

## 67. Shell Commands

Canonical application logic should not depend on brittle shell pipelines when a reliable programmatic interface is appropriate.

Shell scripts remain useful for developer/control workflows.

## 68. CLI

The `mts` CLI is a control interface, not the domain implementation itself.

CLI commands should call canonical services rather than duplicate engine logic.

## 69. Human Output

Human-readable output should be generated from structured canonical state.

Do not make downstream machine behavior depend on parsing prose reports.

## 70. Code Review Questions

Material implementation review should ask:

1. Does this preserve architectural boundaries?
2. Does it use canonical identity/configuration/storage interfaces?
3. Could it leak future information?
4. Does it create hidden durable state?
5. Does it survive restart/retry?
6. Does it introduce legacy coupling?
7. Is the behavior objectively testable?
8. Will the same contract work on the future server?

## 71. Initial v2 Enforcement

Initial automated coding/governance checks should detect at least:

- hard-coded developer paths;
- legacy `Research/` or `Warehouse/` implementation references;
- forbidden cross-engine imports;
- obvious direct Nexus filesystem writes;
- committed secrets patterns where feasible;
- missing test coverage for critical contracts;
- duplicate repo-root implementations.

## 72. Conformance

Code conforms when it:

1. implements canonical architecture rather than bypassing it;
2. preserves engine independence;
3. uses governed configuration and storage roles;
4. keeps Class II state out of Git architecture;
5. uses explicit contracts/types for material boundaries;
6. separates domain results from execution failures;
7. preserves provenance and point-in-time integrity;
8. is restart/retry/concurrency aware;
9. avoids unnecessary legacy compatibility;
10. is objectively testable;
11. remains portable to the intended future deployment.

## 73. Companion Governance

This standard operates with all MTS standards, especially:

```text
ENGINE_INTERFACE_STANDARD.md
TASK_MANAGEMENT_STANDARD.md
CONFIGURATION_STANDARD.md
TEST_AND_VALIDATION_STANDARD.md
ARTIFACT_GOVERNANCE_STANDARD.md
DATA_QUALITY_STANDARD.md
RESEARCH_STANDARD.md
DECISION_STANDARD.md
LEARNING_GOVERNANCE_STANDARD.md
```

## 74. Closing Principle

> **The easiest implementation today must not quietly become the architectural limitation tomorrow.**

Write the simplest code that faithfully implements the system MTS is intended to become.
