# Momentum Trading System — Security and Authority Standard

**Status:** Canonical

## 1. Purpose

This standard defines how Momentum Trading System (MTS) protects credentials, controls authority, constrains automation, governs destructive actions, and separates technical capability from permission.

It governs:

- identities and actors;
- authorization;
- credentials and secrets;
- least privilege;
- human vs automated authority;
- engine permissions;
- Decision authority;
- trade-execution authority;
- governance-change authority;
- model/policy promotion authority;
- destructive operations;
- storage access;
- audit requirements;
- emergency controls;
- future server and multi-user deployment.

Its purpose is to ensure that no component gains more authority merely because it is technically capable of performing an action.

## 2. Governing Principle

> **Capability does not imply authority. Authority must be explicit, scoped, governed, and auditable.**

## 3. Actor Types

MTS should distinguish actor classes such as:

```text
HUMAN
ENGINE
SERVICE
AUTOMATION
SYSTEM
EXTERNAL_PROVIDER
```

An actor type does not itself determine permission.

## 4. Actor Identity

Every material governed action must be attributable to a resolvable actor identity.

Examples may include:

```text
human:<user>
engine:research-director
engine:decision
service:task-manager
automation:daily-intake
```

Exact identity format belongs in Governance/Schemas.

## 5. Authentication

Where multiple users, services, or remote components exist, MTS must authenticate actors before granting protected access.

Authentication mechanism is implementation detail.

Identity semantics and required assurance are governance concerns.

## 6. Authorization

Authorization determines what an authenticated actor may do.

Authorization should be based on explicit permissions, roles, policies, or capability grants.

MTS must not infer authority solely from:

- process location;
- engine name;
- filesystem ownership;
- network location;
- possession of a file path.

## 7. Least Privilege

Actors should receive only the permissions required for their governed function.

Examples:

- Discovery may read approved research inputs and publish findings, but may not approve knowledge promotion.
- Research Director may propose research but may not schedule workers directly or independently pass the Accountability gate for its own proposal/output.
- Accountability may issue research gate verdicts but may not alter its own gate criteria, schedule workers, own canonical knowledge, or approve individual trades.
- Task Manager may coordinate work but may not change scientific conclusions.
- Decision may produce Decision artifacts but may not silently modify research knowledge.
- Learning & Governance may recommend changes but may not silently deploy production changes.
- backup service may read durable state and write backup destinations but may not alter canonical research artifacts.

## 8. Engine Authority Boundaries

Engine permissions must align with canonical engine responsibilities.

No engine may gain broader authority simply by importing a shared library or obtaining filesystem access.

Authority should be enforceable at service/interface boundaries where practical.

## 9. Research Director Authority

Research Director may:

- inspect governed research state;
- formulate questions;
- create Research Plans;
- request tasks;
- create Research Needs;
- propose knowledge candidates.

Research Director may not, solely by its own authority:

- declare its own proposal canonical knowledge;
- change governance standards;
- alter hard risk policy;
- execute live trades;
- delete permanent evidence;
- expand its own permissions.

## 10. Accountability Authority

Accountability Engine may:

- evaluate proposed Research Plans at Research Admission;
- evaluate Knowledge Candidates at Knowledge Promotion;
- inspect evidence required by applicable gate policy;
- issue structured gate verdicts and limits.

Accountability Engine may not:

- author the scientific conclusion it gates;
- alter the Charter, Standards, or Policies defining its criteria;
- expand its own authority;
- schedule workers;
- own canonical knowledge;
- make investment Decisions;
- approve or reject individual trades.

The same Accountability Engine may control both research gates because the
function is consistent enforcement of Charter-derived criteria. The two gate
verdicts remain distinct governed actions.

## 11. Decision Authority

Decision Engine may create governed Decision artifacts within applicable policy.

Decision authority does not automatically include:

- broker order submission;
- portfolio transfer authority;
- policy modification;
- model promotion;
- deletion of historical Decisions;
- research truth authority.

## 12. Trade Execution Authority

If a broker/execution capability is introduced, it must be treated as a separate high-authority capability.

Execution authority must define:

- permitted accounts;
- permitted instruments;
- order types;
- maximum notional/exposure;
- permitted hours;
- approval requirements;
- kill-switch behavior;
- audit requirements.

Decision output alone must not automatically grant unrestricted brokerage access.

## 13. Human Approval

Some actions may require explicit human approval.

Initial v2 should require human approval for material changes to:

- Charter;
- architecture;
- governance standards;
- hard risk policy;
- production Decision authority;
- production model promotion;
- destructive permanent-data deletion;
- connection of live brokerage authority.

This boundary may evolve only through explicit governance.


### Live Paper to Live Authority Boundary

Live Paper Validation and live brokerage authority are separate authority
states.

A `PASS` from a Live Paper Validation campaign:

- may establish eligibility for live-authorization review;
- does not connect brokerage credentials;
- does not enable live order submission;
- does not expand Decision authority;
- does not waive risk or automation requirements.

Paper execution must fail closed when execution destination is absent,
ambiguous, invalid, or inconsistent with the active authority profile.

Live brokerage authority requires separate affirmative governed enablement.

## 14. Automation Authority

Automation may perform only actions explicitly granted by policy.

Examples of lower-risk automation may include:

- scheduled data intake;
- cache retirement;
- integrity checks;
- research task submission;
- backup verification;
- retrieval ranking updates where approved.

Automation does not inherit all authority of the human who configured it.

## 15. Self-Modification

No engine or automated service may silently modify:

- source code;
- governance documents;
- architecture;
- schemas;
- hard policy;
- permissions;
- production model state;
- production Decision thresholds.

Such changes require governed change/promotion processes.

## 16. Privilege Escalation

An actor must not be able to expand its own permissions through ordinary configuration or artifact publication.

Privilege changes require separate authority.

## 17. Separation of Duties

High-impact workflows should separate proposal from approval where practical.

Examples:

```text
Research proposes knowledge
→ governed validation
→ authorized promotion
```

```text
Learning recommends policy change
→ review/approval
→ effective policy
```

```text
Decision proposes action
→ execution capability applies execution controls
```

The same component should not silently become proposer, validator, approver, and executor for high-risk actions unless explicitly governed.

## 18. Secrets

Secrets include:

- API keys;
- access tokens;
- passwords;
- private keys;
- brokerage credentials;
- database credentials;
- signing keys.

Secrets must not be stored in:

- Git;
- canonical scientific artifacts;
- ordinary logs;
- reports;
- task payloads unless specifically protected;
- filenames.

## 19. Secret References

Configuration should reference secrets through approved secret mechanisms.

Code should consume resolved secret values only at the boundary where needed.

## 20. Secret Rotation

Credential systems should support rotation without rewriting scientific logic.

Rotation should not change artifact identity or scientific provenance unless provider/account semantics change.

## 21. Secret Leakage

Telemetry, exceptions, debugging output, and crash reports must avoid emitting secrets.

Redaction should occur before protected data leaves the owning boundary.

## 22. Provider Credentials

Provider credentials should be scoped to the minimum required service/data family where possible.

A Data Intake credential should not automatically grant unrelated administrative capability.

## 23. Brokerage Credentials

Brokerage credentials are high-risk secrets.

They should be:

- strongly protected;
- minimally scoped;
- inaccessible to components that do not execute orders;
- excluded from development/test environments unless explicitly required;
- auditable when used.

## 24. Environment Separation

Development, test, staging, and production-like environments must have distinct authority boundaries where practical.

Test code must not accidentally acquire production credentials or write production durable state.

## 25. Test Safety

Tests must use:

- isolated Nexus roots;
- fake/mock providers where practical;
- non-production accounts;
- synthetic or approved fixtures.

A test must never submit a live order merely because a credential exists on the machine.

## 26. Storage Permissions

Class II durable state should be protected against unauthorized mutation and deletion.

Where practical:

- readers should not receive write permission;
- publishers should have artifact-scoped write authority;
- delete authority should be tightly controlled;
- backup destinations should be protected from ordinary engine mutation.

## 27. Research Nexus Authority

Research Nexus interfaces should enforce authorization for:

- publication;
- mutation/correction;
- lifecycle transition;
- archive;
- deletion;
- policy/state changes.

Direct filesystem access must not become a bypass around Nexus authority.

## 28. Artifact Publication Authority

An actor may publish only artifact types it is authorized to create.

Examples:

- Data Intake publishes data/quality artifacts;
- Discovery publishes evidence/findings;
- Research Director publishes research state/proposals;
- Decision publishes Decision artifacts;
- Learning & Governance publishes evaluations/recommendations.

## 29. Lifecycle Authority

Publication, promotion, supersession, retirement, archival, and deletion are distinct permissions.

Possession of publication authority does not imply lifecycle authority.

## 30. Knowledge Promotion Authority

Knowledge promotion requires the objective criteria defined by governance and the authority defined by policy.

The proposing component must not self-certify unless governance explicitly grants that authority.

## 31. Decision Eligibility Authority

Changing whether knowledge is eligible for Decision use is a material governed action.

It must be attributable and auditable.

## 32. Model Promotion Authority

A model may be trained or evaluated without being production-eligible.

Promotion to production Decision use requires:

- validation;
- governed approval;
- effective time;
- version identity;
- rollback capability where appropriate.

## 33. Policy Change Authority

Policy changes require explicit authority.

Runtime configuration must not silently override a hard policy.

## 34. Configuration Authority

Configuration changes should be scoped by domain.

An operator who may change log verbosity should not necessarily be able to alter Decision risk limits.

## 35. Task Submission Authority

Not every actor may submit every Task type.

The Task Manager must enforce submission authority where material.

Examples:

- Research Director may request research work;
- maintenance service may request integrity checks;
- ordinary engines may not submit unrestricted destructive deletion tasks.

## 36. Task Override Authority

Administrative actions such as:

- force retry;
- cancel;
- reprioritize;
- unblock manually;
- bypass a dependency;

must be permission-controlled and auditable.

## 37. Destructive Actions

Destructive actions include:

- permanent deletion;
- destructive migration;
- irreversible archive pruning;
- credential revocation affecting critical services;
- model/policy rollback affecting production behavior.

These actions require stronger controls than ordinary read/write operations.

## 38. Deletion Authority

Permanent or material Class II deletion requires:

- explicit authority;
- retention eligibility;
- dependency check;
- backup/recovery check where applicable;
- reason;
- audit record.

An engine must not delete durable evidence merely because it no longer needs it locally.

## 39. Contradictory Research Deletion

Contradictory working material is default-to-expire only after the governing Research Plan is resolved and retention criteria are satisfied.

The authority to retire/delete it remains governed by retention policy.

This prevents both infinite retention and premature deletion.

## 40. Emergency Stop

Future live-trading deployment should include an explicit emergency stop/kill capability.

The kill capability should be able to:

- block new order execution;
- cancel eligible open orders where supported;
- preserve audit state;
- leave research/data systems operational unless broader shutdown is required.

## 41. Emergency Authority

Emergency-stop authority should be narrowly assigned and highly visible.

Use of emergency controls must create durable audit records.

## 42. Fail-Safe Behavior

When authority cannot be verified, high-risk actions must fail closed.

Examples:

- unknown execution permission → do not trade;
- missing deletion approval → do not delete;
- invalid policy signature/version → do not activate;
- missing production credential → do not substitute another account.

## 43. Read-Only Degradation

Where possible, systems should degrade to read-only or no-action modes rather than taking unauthorized fallback actions.

## 44. Security Events

Security-relevant events may include:

- failed authentication;
- denied authorization;
- privilege-change attempt;
- secret access failure;
- unexpected credential use;
- unauthorized delete attempt;
- unauthorized model/policy promotion;
- integrity mismatch in protected governance/configuration.

Material events should be auditable.

## 45. Security Logging

Security logs must preserve useful context without exposing secrets.

They should identify:

- actor;
- attempted action;
- protected object;
- decision;
- reason;
- timestamp;
- correlation IDs where applicable.

## 46. Audit Requirement

Material authority decisions must be auditable.

The system should be able to answer:

- who/what requested the action;
- what permission was evaluated;
- what policy governed the decision;
- whether the action was allowed or denied;
- what changed.

## 47. Approval Records

Approval should be represented as structured governed state where material.

A chat message, terminal note, or memory of approval is not sufficient for production-like authority changes.

## 48. Effective Time

Authority, policy, and model changes should have effective times.

Actions before and after the change must remain attributable to the governing state then in force.

## 49. Expiring Authority

Temporary permissions should support expiration.

Examples:

- temporary provider access;
- maintenance window;
- temporary elevated operator privilege.

Expired permissions must not remain active silently.

## 50. Revocation

Permissions and credentials should support revocation.

Revocation state should propagate to affected components promptly enough for the risk involved.

## 51. Service Identity

Future server deployment should assign service identities to independent services/workers where practical.

Workers should not all share one unrestricted identity merely for convenience.

## 52. Multi-User Deployment

If multiple human users are introduced, MTS should support distinct identities and permissions.

Shared generic administrator accounts should be avoided for material governance actions.

## 53. Network Boundaries

Remote services should expose only required interfaces.

Internal service availability must not be treated as authorization.

Network placement is an additional control, not the primary authority model.

## 54. External Integrations

External systems translate/provide information or execute authorized services.

They do not define MTS authority semantics.

Provider-side permissions and MTS-side permissions should both be respected.

## 55. Integrity of Governance Assets

Class I governance and architecture assets should be protected by source-control history and review.

Material changes should be traceable to a specific Git revision.

## 56. Integrity of Runtime Policy

Production-like active policy/model/configuration state should be verifiable by version/hash/reference where material.

Unexpected mismatch should block or degrade high-risk actions according to policy.

## 57. Supply-Chain Awareness

External dependencies and packages may introduce security risk.

Dependency management should support:

- known provenance;
- reproducible versions;
- controlled updates;
- vulnerability review appropriate to risk.

## 58. Command Execution

Code must not execute untrusted strings as shell commands.

Subprocess invocation should use argument-safe mechanisms where practical.

## 59. File Input Safety

External files should be treated as untrusted input until validated.

File names and paths must not be trusted as authority or identity.

## 60. Data Provider Input Safety

Provider data may be malformed, corrupted, or semantically changed.

Security/integrity validation and Data Quality validation are distinct and both may apply.

## 61. Denial Is a Valid Result

Authorization denial is a legitimate system result.

It must not be converted into:

- silent success;
- alternative unapproved path;
- fabricated output.

## 62. Initial v2 Authority Model

Initial v2 should implement at least:

1. actor identity for services/engines;
2. explicit engine publication authority;
3. Task submission authority;
4. human approval for material governance/risk/model changes;
5. secrets outside Git;
6. environment separation;
7. audit of authority decisions;
8. governed deletion authorization;
9. fail-closed behavior for high-risk actions;
10. no live execution authority unless explicitly introduced.

## 63. Initial v2 Security Scope

Initial v2 need not begin with a complex enterprise IAM platform.

A simple local implementation is acceptable if the contracts preserve:

- explicit actor identity;
- explicit permission checks;
- least privilege;
- auditable decisions;
- future service/multi-user expansion.

## 64. Initial Proof

A valid initial proof should demonstrate:

```text
authorized engine
→ allowed artifact publication
```

and:

```text
unauthorized engine
→ publication denied
→ denial audited
```

and:

```text
operator requests destructive action
→ permission + retention conditions evaluated
→ explicit approval required
→ action audited
```

## 65. Testing Requirements

Tests should include:

- authorized action;
- unauthorized action;
- expired permission;
- revoked permission;
- incorrect environment;
- missing secret;
- secret redaction;
- unauthorized artifact publication;
- unauthorized task submission;
- unauthorized lifecycle transition;
- destructive deletion approval;
- fail-closed execution;
- authority audit record;
- production credential unavailable in test.

## 66. Prohibited Practices

The following are prohibited:

- secrets committed to Git;
- one unrestricted identity for all components;
- filesystem access treated as authority;
- engine capability treated as permission;
- runtime configuration silently widening hard authority;
- automated self-promotion of permissions;
- Research Director independently passing the required Accountability promotion gate for its own Knowledge Candidate;
- Decision Engine directly acquiring unrestricted brokerage credentials;
- unaudited destructive deletion;
- unauthorized fallback accounts/providers;
- live-order submission from ordinary tests;
- silent security/authorization failure.

## 67. Conformance

A component conforms when it:

1. has explicit actor identity;
2. enforces least privilege;
3. separates capability from authority;
4. protects secrets;
5. respects engine/lifecycle boundaries;
6. requires appropriate approval for high-impact changes;
7. fails closed for high-risk authorization uncertainty;
8. audits material authority decisions;
9. prevents configuration from bypassing policy;
10. supports future multi-user/service expansion without redesign.

## 68. Companion Governance

This standard operates with:

```text
ARTIFACT_GOVERNANCE_STANDARD.md
STORAGE_RETENTION_STANDARD.md
ENGINE_INTERFACE_STANDARD.md
TASK_MANAGEMENT_STANDARD.md
CONFIGURATION_STANDARD.md
DECISION_STANDARD.md
LEARNING_GOVERNANCE_STANDARD.md
OBSERVABILITY_AND_AUDIT_STANDARD.md
TEST_AND_VALIDATION_STANDARD.md
CODING_STANDARD.md
```

and applicable Contracts, Schemas, and Policies.

## 69. Closing Principle

MTS must always be able to answer:

> **Who or what is attempting this action, what authority permits it, what limits apply, and what durable record proves the action was allowed or denied?**

If a component can perform a high-impact action merely because it can reach the code or filesystem that implements it, authority is not sufficiently governed.
