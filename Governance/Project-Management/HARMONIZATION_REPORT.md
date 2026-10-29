# MTS v2 Governance Harmonization Report

## Result

The existing 13 standards remain separate. No standard was deleted because each owns a distinct governing concern.

The harmonization establishes one-authority-per-concept and corrects the SoK/contradiction lifecycle.

## Canonical authority map

| Concern | Primary authority |
|---|---|
| identity | IDENTITY_STANDARD |
| artifact lifecycle/promotion | ARTIFACT_GOVERNANCE_STANDARD |
| schema structure/version compatibility | SCHEMA_STANDARD |
| storage/retention/backup classification | STORAGE_RETENTION_STANDARD |
| engine boundaries/capabilities | ENGINE_INTERFACE_STANDARD |
| scheduling/retry/dependency/recovery | TASK_MANAGEMENT_STANDARD |
| fitness/quality of data | DATA_QUALITY_STANDARD |
| questions/RPs/evidence/convergence | RESEARCH_STANDARD |
| action selection | DECISION_STANDARD |
| outcome feedback/adaptation governance | LEARNING_GOVERNANCE_STANDARD |
| deployment/runtime values | CONFIGURATION_STANDARD |
| proof/acceptance/regression | TEST_AND_VALIDATION_STANDARD |
| implementation discipline | CODING_STANDARD |

## Harmonized scientific-state model

1. **Research Nexus** — canonical body of durable MTS state.
2. **State of Knowledge (SoK)** — scoped, point-in-time view of current applicable canonical knowledge.
3. **Active Research State** — unresolved questions, contradictions, hypotheses, RPs, anomalies, gaps, and required working state.
4. **Historical Research Lineage** — minimum durable history justified by reproducibility, audit, learning, or material Decision reconstruction.

## Contradiction lifecycle

Contradiction is not canonical knowledge.

Default lifecycle:

`contradiction detected → active research state → RP/investigation → resolution → consequence incorporated into knowledge/uncertainty/eligibility → working contradiction expires`

Durable contradiction retention requires objective justification. Prefer compact resolution records over indefinite raw contradictory payload retention.

## Duplication rule

Secondary standards may state a boundary consequence, but must not redefine the primary authority's mechanism.

Examples:
- Research says it submits tasks; Task Management defines scheduling.
- Decision requires point-in-time inputs; Test & Validation defines how leakage is proven absent.
- Coding prohibits hard-coded storage; Configuration/Storage define the canonical mechanism.
- Learning may recommend promotion/retirement; Artifact Governance owns lifecycle transition semantics.

## Remaining missing standards

After harmonization, two cross-cutting standards remain justified:
- OBSERVABILITY_AND_AUDIT_STANDARD.md
- SECURITY_AND_AUTHORITY_STANDARD.md

Operational thresholds should be Policies, not additional Standards:
- knowledge promotion/retirement policy
- contradiction retention policy
- backup/recovery policy
- resource/priority policy

## Sequence

Harmonized Standards → Observability/Audit → Security/Authority → Policies → Contracts → Schemas → implementation.
