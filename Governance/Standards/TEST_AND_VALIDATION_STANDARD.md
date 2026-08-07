# Momentum Trading System — Test and Validation Standard

**Status:** Canonical

## 1. Purpose

This standard defines how MTS proves that software, contracts, data flows, research behavior, decision behavior, recovery behavior, and governance controls work as intended before they are relied upon.

## 2. Governing Principle

> A passing test proves only the claim the test was designed to prove.

MTS must therefore define explicit validation claims, acceptance criteria, fixtures, evidence, and failure semantics.

## 3. Validation Layers

MTS validation includes:

- unit tests;
- schema tests;
- contract tests;
- integration tests;
- end-to-end tests;
- scientific validation;
- temporal-integrity tests;
- recovery tests;
- migration tests;
- performance/resource tests;
- acceptance tests.

These layers are complementary, not interchangeable.

## 4. Test Organization

Canonical test families belong under the repository `Tests/` hierarchy, including:

```text
Tests/unit/
Tests/contracts/
Tests/integration/
Tests/end_to_end/
```

Additional governed test families may be added without changing this principle.

## 5. Objective Acceptance Criteria

Tests must evaluate explicit criteria.

Terms such as “works,” “looks right,” “seems reasonable,” and “trusted” are not sufficient acceptance criteria unless operationally defined.

## 6. Unit Tests

Unit tests validate bounded behavior of a component in isolation.

They should be fast, deterministic where practical, and independent of production services.

## 7. Schema Tests

Schema tests verify:

- required fields;
- types;
- controlled vocabularies;
- compatibility rules;
- rejection of invalid structures;
- version behavior.

Schema-valid does not imply scientifically valid.

## 8. Contract Tests

Contract tests verify behavior at component boundaries.

They must validate both producer and consumer expectations, including:

- request shape;
- response shape;
- semantic result handling;
- error handling;
- artifact publication;
- version compatibility.

## 9. Integration Tests

Integration tests validate that real MTS components interact correctly through governed interfaces.

They must not bypass the interface merely to make the test easier.

## 10. End-to-End Tests

End-to-end tests validate meaningful workflows across system boundaries.

An E2E test should prove the intended chain rather than merely prove that processes can launch.

## 11. Scientific Validation

Scientific validation is distinct from software correctness.

A mathematically correct implementation can produce an invalid scientific conclusion if:

- data leaks from the future;
- the sample is biased;
- the holdout is contaminated;
- the methodology is inappropriate;
- the result is unstable.

Scientific claims require scientific validation criteria.

## 12. Temporal Integrity

Historical research and Decision simulation must explicitly test that only information available at the simulated time is consumed.

Future-information leakage is a test failure.

## 13. Holdout Integrity

Holdout data must remain unseen by the process being evaluated until the governed evaluation point.

Repeated adaptation to the same holdout invalidates its status as unseen evaluation data.

## 14. Data Quality Validation

Tests must cover representative valid and invalid data, including:

- missing fields;
- duplicates;
- invalid OHLC relationships;
- temporal gaps;
- corporate actions;
- instrument mapping;
- source limitations;
- stale live data.

## 15. Research Director Validation

Research validation must prove genuine evidence-dependent iteration.

A valid test includes:

```text
Question
→ Research Plan
→ returned evidence
→ next question determined from that evidence
→ further evidence
→ objective convergence or explicit unresolved state
```

A fixed scripted sequence does not prove adaptive research.

## 16. Convergence Validation

Tests must verify that convergence is caused by governed stopping criteria.

They must also test failure to converge within resource or iteration limits.

## 17. Decision Validation

Decision tests must freeze the information set before revealing outcomes.

A canonical proof pattern is:

```text
historical learning/research
→ point-in-time knowledge frozen
→ unseen decision context
→ Decision frozen
→ future outcome revealed
→ Outcome evaluation
```

## 18. `NO_ACTION`

Tests must treat `NO_ACTION` as a valid semantic result.

MTS should test both:

- correct avoidance;
- missed opportunity.

## 19. Long and Short

Decision validation must include both long and short opportunities.

The test architecture must not encode long-only assumptions.

## 20. Execution Failure vs Domain Result

Tests must prove the system distinguishes:

```text
software failure
provider failure
timeout
INSUFFICIENT_EVIDENCE
MISSING_CAPABILITY
NO_ACTION
RESEARCH_REQUIRED
```

These are not interchangeable.

## 21. Task Manager Validation

Task tests must include:

- identity;
- execution attempts;
- dependencies;
- priority;
- routing;
- retries;
- terminal failures;
- cancellation;
- timeout;
- expiration;
- restart recovery;
- lost worker;
- idempotency;
- downstream release.

## 22. Recovery Testing

MTS must deliberately test interruption.

Examples:

- kill Task Manager during active work;
- restart Research Director mid-campaign;
- interrupt publication;
- lose a worker heartbeat;
- restart after queued work exists.

Successful recovery must be demonstrated, not assumed.

## 23. Research Nexus Validation

Nexus tests must verify:

- artifact identity;
- immutability where required;
- provenance;
- metadata;
- retrieval;
- lifecycle class;
- integrity checks;
- backup/recovery behavior where applicable.

## 24. Storage Validation

A mounted device is not proof of healthy storage.

Storage qualification may include:

- filesystem integrity;
- read/write verification;
- capacity;
- performance appropriate to role;
- backup independence;
- restore test.

## 25. Backup Validation

Backup success is not established merely because a copy command returned zero.

MTS should periodically verify that backed-up durable state can actually be restored and validated.

## 26. Migration Tests

Migration must prove preservation of:

- artifact identity;
- content;
- provenance;
- metadata;
- relationships;
- lifecycle semantics.

Source data should remain available until migration acceptance criteria are satisfied.

## 27. Configuration Tests

Tests must prove:

- configuration validation;
- override precedence;
- CWD independence;
- repository relocation;
- Nexus relocation;
- environment separation;
- secret handling;
- effective configuration reproducibility.

## 28. Engine Interface Tests

Every engine must pass common interface tests appropriate to its capabilities.

These should verify:

- declared capability;
- accepted request versions;
- output contract;
- error semantics;
- no private durable-state dependency;
- Task Manager compatibility.

## 29. Regression Tests

Every corrected defect that could recur should normally gain a regression test.

A patch is incomplete when the system cannot subsequently detect reintroduction of the same defect.

## 30. No Patch-Fix Architecture

Tests must protect architectural contracts, not merely preserve accidental legacy behavior.

When a defect reveals an architectural violation, correct the architecture and test the intended contract rather than accumulating compatibility hacks.

## 31. Determinism

Where deterministic behavior is expected, tests must verify repeatability.

Where stochastic behavior is intentional, tests should control seeds or validate statistical properties as appropriate.

## 32. Test Fixtures

Fixtures must be:

- identifiable;
- reproducible;
- appropriately small where possible;
- representative of important edge cases;
- isolated from production durable state.

## 33. Synthetic Data

Synthetic data is useful for software and edge-case testing.

It must not be presented as empirical validation of real-market behavior.

## 34. Real Historical Data

Scientific validation should eventually include governed real historical data.

The exact source, period, instrument set, and point-in-time constraints must be preserved.

## 35. Golden Fixtures

Stable canonical fixtures may be used to verify transformations and contracts.

Golden outputs must be intentionally reviewed when changed.

Tests must not automatically rewrite expected outputs to make failures disappear.

## 36. Test Isolation

Tests must not:

- write into production Nexus state;
- consume production secrets unnecessarily;
- mutate production configuration;
- depend on developer-specific filesystem state.

## 37. Temporary State

Test-generated Class II-like artifacts should use isolated temporary/test Nexus roots and be removed according to test policy.

## 38. Failure Evidence

A failed validation should preserve enough evidence to diagnose:

- claim tested;
- expected result;
- actual result;
- relevant configuration;
- execution identity;
- diagnostics.

## 39. Test Evidence

Material acceptance runs may produce governed validation artifacts.

These may include:

```text
validation_run_id
software_version
test_suite
configuration_ref
started_at
completed_at
results
failures
acceptance_status
```

## 40. Promotion Gates

Components must not be promoted to a more authoritative role until required validation gates pass.

Examples:

```text
experimental → validated
validated → decision-eligible
migration candidate → accepted
new model → production-eligible
```

Promotion criteria must be objective.

## 41. Known Failures

Known failures must not be hidden by blanket test exclusions.

Temporary skips should include:

- reason;
- owner;
- condition for removal.

## 42. Flaky Tests

Flaky tests are defects.

Repeatedly rerunning a failing test until it passes is not validation.

## 43. Performance Tests

Performance tests should evaluate relevant constraints such as:

- throughput;
- latency;
- memory;
- CPU;
- storage I/O;
- queue delay.

Performance thresholds should reflect the workload class.

## 44. Scalability Tests

Even when v2 initially runs one worker, tests should simulate or validate the contracts needed for multiple workers.

This protects the design-with-the-end-in-mind requirement.

## 45. Concurrency Tests

Concurrency testing should include:

- duplicate assignment prevention;
- idempotency;
- shared-resource limits;
- dependency release;
- portfolio coordination where applicable.

## 46. Security Tests

Where applicable, tests should verify:

- secrets are not logged;
- unauthorized task types are rejected;
- invalid configuration cannot widen authority;
- sensitive credentials are not committed.

## 47. Governance Tests

Some governance requirements should be machine-enforced.

Examples:

- prohibited legacy paths;
- missing required metadata;
- invalid artifact class;
- unsupported schema versions;
- forbidden imports/coupling;
- missing policy references.

## 48. Repository Hygiene Tests

Automated checks may verify:

- no generated durable data committed;
- no secret files;
- no forbidden legacy hierarchy references;
- canonical directory rules;
- required governance files.

## 49. Canonical Test Runner

MTS should provide one canonical entry point for routine validation.

Conceptually:

```text
mts test
mts test unit
mts test contracts
mts test integration
mts test end-to-end
```

The exact CLI may evolve.

## 50. Local vs Full Validation

Fast local validation may be a subset of full acceptance validation.

The distinction must be explicit.

Passing a fast developer suite must not be represented as passing the full system acceptance suite.

## 51. Continuous Integration

Git-hosted CI should validate Class I software/governance assets where practical.

CI must not require permanent Research Nexus data to be committed to Git.

## 52. Pre-Commit Validation

Lightweight checks may run before commit.

They should remain fast enough that developers do not routinely bypass them.

## 53. Acceptance Before Commit

Not every working-tree change requires full E2E testing before every commit.

However, commits intended as stable milestones should have the applicable validation status known.

## 54. Acceptance Before Production Use

Production-like Decision or autonomous operation requires all applicable critical validation gates to pass.

## 55. Version Traceability

Validation evidence must identify the exact software revision tested.

A test result from one commit must not be silently attributed to another.

## 56. Revalidation

Revalidation is required when material changes affect:

- interfaces;
- schemas;
- scientific methods;
- storage behavior;
- Decision logic;
- policy;
- model;
- provider semantics.

## 57. Test Maintenance

Tests are governed software assets.

Obsolete tests should be retired deliberately rather than allowed to accumulate indefinitely.

## 58. Initial v2 Validation Baseline

Before substantive engine migration/implementation, v2 should establish tests for:

1. repository-root independence;
2. configuration loading;
3. Task Request lifecycle;
4. Research Nexus publication/retrieval;
5. engine interface contract;
6. data quality gate;
7. evidence-dependent Research iteration;
8. point-in-time Decision;
9. Decision–Outcome separation;
10. restart recovery.

## 59. Minimum Engine Acceptance

Before an engine is considered integrated, it should prove:

```text
Task Manager request
→ engine capability invocation
→ governed output
→ Nexus publication
→ terminal Task result
```

and failure semantics.

## 60. End-to-End Acceptance

A meaningful MTS v2 E2E proof should eventually demonstrate:

```text
Data Intake
→ quality acceptance
→ Discovery
→ Research Director iteration
→ knowledge candidate / SoK
→ Market Discovery candidate
→ Decision
→ Outcome
→ Learning & Governance
→ new Research Need or governed recommendation
```

Not every early milestone must implement the entire chain, but the architecture and test plan must target it.

## 61. Prohibited Practices

The following are prohibited:

- declaring success because a process exited zero;
- manually inspecting output as the sole acceptance test;
- future leakage in historical validation;
- repeatedly adapting to the same holdout;
- silently skipping failing tests;
- testing against production durable state;
- auto-updating golden outputs to suppress failures;
- patching tests to preserve obsolete architecture;
- calling synthetic-data success proof of market edge;
- attributing test results to untested code revisions.

## 62. Conformance

A validation system conforms when it:

1. defines objective claims and acceptance criteria;
2. separates software correctness from scientific validity;
3. tests contracts and integration boundaries;
4. protects temporal and holdout integrity;
5. validates recovery and restart behavior;
6. preserves diagnostic evidence;
7. isolates test state;
8. guards against regression;
9. validates exact software/configuration versions;
10. supports future concurrency and scale;
11. provides a canonical test entry point;
12. uses promotion gates for authoritative behavior.

## 63. Companion Governance

This standard operates with all MTS governance standards, especially:

```text
DATA_QUALITY_STANDARD.md
ENGINE_INTERFACE_STANDARD.md
TASK_MANAGEMENT_STANDARD.md
RESEARCH_STANDARD.md
DECISION_STANDARD.md
LEARNING_GOVERNANCE_STANDARD.md
CONFIGURATION_STANDARD.md
ARTIFACT_GOVERNANCE_STANDARD.md
STORAGE_RETENTION_STANDARD.md
```

## 64. Closing Principle

MTS must always be able to answer:

> **What exactly did this test prove, against which version and configuration, and what important claim remains unproven?**

A green test suite is useful only when MTS knows what the green actually means.
