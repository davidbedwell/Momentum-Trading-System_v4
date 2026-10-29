# Knowledge Lifecycle Policy Harmonization Audit

## Scope

This audit records the design basis for `KNOWLEDGE_LIFECYCLE_POLICY.md` and the
canonical harmonization required before committing the policy.

## Source Audit

Policy design was grounded in `MTS_KNOWLEDGE_LIFECYCLE_AUDIT.txt`.

The source audit shows that existing MTS governance already establishes:

- publication is distinct from promotion;
- Accountability controls the required Knowledge Promotion gate;
- canonical lifecycle includes promoted/current, superseded, retired,
  invalidated, and archived concepts;
- retirement is not erasure;
- scientific validity and retrieval priority are separate;
- usage frequency alone must not determine scientific validity;
- SoK is a governed point-in-time view of relevant canonical knowledge rather
  than the entire Research Nexus;
- Decision knowledge must satisfy objective Decision-eligibility criteria;
- unresolved contradiction belongs to research state rather than ordinary
  canonical Decision SoK;
- Learning & Governance may recommend revalidation/retirement but does not
  replace required promotion authority;
- cache/temporary material has explicit retirement/deletion concepts.

## Policy Addition

The policy does not create a parallel knowledge model.

It operationalizes the existing model and adds explicit governance for:

- active utility;
- relevant-access measurement;
- applicable-opportunity exposure;
- utility demotion;
- hot/normal/cold retrieval treatment;
- anti-bloat behavior;
- objective revalidation triggers/outcomes;
- separation of lifecycle, scientific status, Decision eligibility, retrieval
  priority, and physical retention;
- rare-but-important knowledge protection;
- negative/avoidance knowledge utility;
- anti-feedback-loop safeguards for cold knowledge.

## Central Anti-Bloat Rule

Persistent non-use across a sufficient number of genuinely applicable
opportunities is evidence of low demonstrated utility.

It may lower retrieval/storage priority and initiate utility or retirement
review.

It does not by itself invalidate scientific knowledge.

## Required Harmonization Review

Before commit, compare the new policy against:

- `Architecture/RESEARCH_NEXUS_ARCHITECTURE.md`
- `Architecture/SYSTEM_ARCHITECTURE.md`
- `Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md`
- `Governance/Standards/RESEARCH_STANDARD.md`
- `Governance/Standards/LEARNING_GOVERNANCE_STANDARD.md`
- `Governance/Standards/DECISION_STANDARD.md`
- `Governance/Standards/SECURITY_AND_AUTHORITY_STANDARD.md`
- `Governance/Standards/STORAGE_RETENTION_STANDARD.md`

Only actual semantic gaps should be patched. Existing canonical language should
not be duplicated merely to mention the new policy.

## Authority Preservation

The policy does not give Learning & Governance unilateral authority to promote
knowledge.

It does not make retrieval ranking a scientific authority.

It does not give storage/cache management authority to change Decision
eligibility.

It does not allow age, access frequency, or disk pressure to erase canonical
scientific history.

## Active Utility Harmonization Result

The conformance audit showed that the existing architecture and standards were
already aligned on lifecycle, scientific status, Decision eligibility,
contradiction, supersession, retirement, archival, and retention.

The material gap was narrower: the new policy's active-utility model was more
explicit than the older canonical architecture/standards.

Harmonization therefore adds only:

- active utility as a distinct operational dimension;
- relevant-access semantics;
- applicable-opportunity exposure;
- non-use as evidence of low utility rather than scientific invalidity;
- hot/normal/cold retrieval treatment;
- protection for rare-context knowledge;
- an explicit distinction between `COLD` retrieval and `ARCHIVED` storage;
- anti-feedback-loop retrieval for low-ranked/cold knowledge.

No new scientific authority or lifecycle authority is created.

No existing canonical lifecycle state is replaced.

The harmonization intentionally avoids adding a complex utility scoring
algorithm. Initial implementation should use objective, inspectable metrics and
rules.

