# Momentum Trading System — Knowledge Lifecycle Policy

**Status:** Canonical
**Authority:** Subordinate to `CHARTER.md`, canonical Architecture, and Governance Standards

---

## 1. Purpose

This policy governs the operational lifecycle of MTS knowledge after research
produces a Knowledge Candidate and throughout the period in which that knowledge
may be retained, retrieved, applied to Decisions, revalidated, constrained,
superseded, retired, invalidated, or archived.

The policy exists to keep the Research Nexus scientifically defensible,
decision-relevant, computationally efficient, and resistant to uncontrolled
accumulation.

---

## 2. Governing Principle

MTS must not collapse distinct knowledge dimensions into one score or state.

At minimum, the following dimensions are governed separately:

1. **knowledge authority / lifecycle standing** — what governed standing the
   artifact possesses;
2. **current scientific status** — whether the proposition remains supported
   within its declared scope;
3. **Decision eligibility** — whether and how the knowledge may influence a
   particular Decision context;
4. **retrieval priority / active utility** — how strongly the knowledge should
   be surfaced for current work;
5. **physical retention / storage tier** — where and how the underlying artifact
   is retained.

A change in one dimension must not silently change another.

---

## 3. Publication Is Not Promotion

Publication makes an artifact available through governed Research Nexus
interfaces according to artifact type and lifecycle state.

Publication does not make a finding canonical knowledge.

A Knowledge Candidate becomes higher-authority canonical knowledge only after
satisfying the applicable objective promotion criteria and receiving the
required Accountability Knowledge Promotion verdict.

No component may promote its own output merely because it generated, used, or
ranked that output highly.

---

## 4. Canonical Lifecycle States

The canonical artifact lifecycle vocabulary remains governed by Artifact
Governance and Research Nexus architecture.

Knowledge lifecycle handling must support, as applicable:

```text
CANDIDATE
PROMOTED / CURRENT
CONTRADICTED
SUPERSEDED
RETIRED
INVALIDATED
ARCHIVED
```

Implementations may represent additional machine states where standards permit,
but must not create an alternate semantic authority model.

---

## 5. Current Scientific Status

Canonical knowledge must carry enough current status information to determine
whether its proposition remains scientifically supportable within its declared
scope.

Current scientific status may include, as applicable:

```text
CURRENT
CURRENT_SCOPED
REVALIDATION_REQUIRED
CONTRADICTION_UNDER_INVESTIGATION
DEGRADED
SUPERSEDED
RETIRED
INVALIDATED
```

These statuses describe present scientific/lifecycle condition. They do not by
themselves define retrieval rank or physical deletion.

---

## 6. Decision Eligibility

Canonical knowledge is not automatically eligible for every Decision.

Decision eligibility must consider at least:

- declared population and instrument scope;
- market/context/regime applicability where material;
- time or horizon applicability;
- current scientific status;
- unresolved material contradiction;
- required revalidation state;
- relevant Decision policy;
- any explicit scope constraint;
- whether extrapolation is permitted and disclosed.

The State of Knowledge supplied to Decision must be assembled from knowledge
eligible and relevant to the defined subject, time, and use.

Historical Decisions retain the point-in-time knowledge state that was available
and valid when the Decision was made. Later lifecycle changes must not rewrite
historical Decision evidence.

---

## 7. Scientific Validity Is Not Retrieval Priority

Scientifically valid knowledge may be rarely useful.

Frequently retrieved knowledge may be weakly useful.

Usage frequency, recency, ranking, popularity, or repeated engine access must
not determine scientific validity or independently authorize lifecycle
promotion.

Retrieval ranking exists to allocate attention and computational resources.

---

## 8. Active Utility

MTS may maintain an **active utility** assessment for canonical knowledge.

Active utility estimates the demonstrated operational value of keeping a
knowledge artifact close to the ordinary Decision/research retrieval path.

Active utility may consider objective dimensions such as:

- frequency of relevant retrieval;
- material use in Decisions;
- material use in research;
- incremental effect on candidate ranking;
- incremental effect on enter/watch/hold/no-action judgment;
- incremental effect on sizing, risk, timing, or exit;
- frequency of applicable market opportunities;
- time since last relevant access;
- eligible opportunities since last material use;
- redundancy with other current knowledge;
- computational/storage cost;
- economic relevance to MTS objectives.

Active utility is not scientific validity.

---

## 9. Relevant Access

A maintenance read, index scan, backup, integrity check, migration, or automated
touch must not reset utility-aging metrics.

Where technically practical, MTS should distinguish:

```text
last_access
last_relevant_access
last_material_decision_use
last_material_research_use
```

`last_relevant_access` means the artifact was retrieved because it was
applicable to the actual question, research context, or Decision context.

---

## 10. Applicable-Opportunity Exposure

Elapsed time alone is insufficient evidence of low utility.

MTS should evaluate non-use relative to the number and quality of opportunities
in which the knowledge reasonably could have mattered.

Where measurable, lifecycle/utility evaluation should track:

```text
eligible_opportunities_since_use
applicable_context_count
decision_use_count
material_decision_use_count
research_use_count
incremental_utility_evidence
```

Knowledge designed for rare conditions must not be penalized merely because
those conditions have not occurred.

A crash-regime relationship, rare liquidity event, unusual derivative
structure, or other low-frequency but economically material knowledge may
remain valuable despite long periods without access.

---

## 11. Utility Demotion

Persistent lack of relevant use across a sufficient number of applicable
opportunities is objective evidence of low demonstrated utility.

Low demonstrated utility may cause:

- lower retrieval rank;
- removal from hot indexes;
- movement to a cold canonical retrieval tier;
- less frequent proactive retrieval;
- utility review;
- redundancy review;
- revalidation request where scientifically justified;
- retirement review where objective criteria are met.

Low demonstrated utility alone must not:

- invalidate knowledge;
- erase provenance;
- rewrite scientific history;
- silently remove required Decision eligibility;
- physically delete protected canonical knowledge.

---

## 12. Hot, Normal, and Cold Retrieval Tiers

Implementations may optimize canonical retrieval using tiers such as:

```text
HOT
NORMAL
COLD
```

These are operational retrieval/storage classifications, not scientific
authority states.

### HOT

Appropriate for knowledge with strong current relevance, frequent material use,
or high expected economic importance.

### NORMAL

Appropriate for ordinary current canonical knowledge without a demonstrated
need for hot-path treatment.

### COLD

Appropriate for valid but infrequently useful, low-priority, redundant, or
rare-context knowledge that should remain historically/scientifically
resolvable without burdening ordinary retrieval.

Cold knowledge remains discoverable through governed targeted retrieval.

---

## 13. Anti-Bloat Principle

The Research Nexus is a curated economic knowledge system, not an unlimited
collection of every artifact MTS has ever produced.

MTS should minimize the active working set while preserving the scientific
evidence and lineage required by governance.

The system should preferentially:

1. keep high-utility current knowledge close to ordinary retrieval;
2. move valid but low-utility knowledge to cheaper/cold retrieval paths;
3. retire knowledge that no longer warrants ordinary active use when objective
   criteria are met;
4. expire reproducible research debris and temporary contradiction material
   when retention criteria no longer justify it;
5. preserve compact durable lineage where required;
6. avoid duplicate canonical representations of materially equivalent
   knowledge.

Disk pressure alone is not lifecycle authority.

---

## 14. Revalidation Triggers

Knowledge must be considered for revalidation when objective evidence indicates
that its current scientific status, scope, or Decision eligibility may no longer
be justified.

Triggers may include:

- material contradictory evidence;
- material degradation in observed behavior;
- statistically/economically material drift;
- regime change relevant to applicability;
- scope violation;
- new evidence outside the original population or context;
- material data-quality defect;
- provider-definition or coverage change that may affect the finding;
- methodological defect;
- reproducibility failure;
- superseding research;
- defined temporal-validity boundary;
- material unexplained Decision/outcome divergence;
- material change in the economic mechanism on which applicability depended.

Revalidation must not be triggered solely because a calendar interval elapsed
unless temporal aging is itself an objective part of the applicable rule.

---

## 15. Revalidation Outcomes

A governed revalidation process should produce an explicit result such as:

```text
RETAIN
RETAIN_WITH_SCOPE
REVALIDATE_AGAIN
CONSTRAIN
DEGRADE
CONTRADICT
SUPERSEDE
RETIRE
INVALIDATE
```

The result must identify:

- knowledge identity/version;
- evidence evaluated;
- applicable scope;
- objective criteria applied;
- uncertainty;
- effective time;
- resulting Decision eligibility;
- required follow-up;
- authority/verdict required for any higher-authority lifecycle transition.

---

## 16. Contradiction

Contradictory evidence is not automatically canonical knowledge.

Unresolved contradiction belongs to Active Research State and must remain
linked to affected canonical knowledge when material.

A material contradiction may temporarily constrain Decision eligibility or
trigger revalidation according to objective rules without rewriting prior
history.

After resolution, contradictory working material is default-to-expire unless
durable retention is justified.

Where contradiction materially changes knowledge, applicability, uncertainty,
Decision eligibility, supersession, retirement, or a material historical
Decision, MTS must preserve the minimum necessary evidence and compact durable
resolution/lineage record required by governance.

---

## 17. Scope Narrowing

When evidence supports a relationship only in a narrower population, regime,
instrument class, horizon, or context, MTS should constrain applicability rather
than falsely generalize or unnecessarily discard useful conditional knowledge.

Scope narrowing must be explicit and versioned where required.

A narrower current proposition must preserve lineage to the broader prior
proposition it constrains or supersedes.

---

## 18. Supersession

Supersession means a later governed artifact replaces an earlier artifact for a
defined current use or scope.

Supersession must identify:

- superseding artifact;
- superseded artifact;
- scope of replacement;
- effective time;
- reason/evidence;
- Decision-eligibility effect.

The superseded artifact remains historically resolvable.

Supersession is not physical deletion.

---

## 19. Retirement

Retirement means knowledge is removed from ordinary active use according to
objective governed criteria.

Retirement may be justified by combinations of:

- persistent low demonstrated utility across sufficient applicable
  opportunities;
- redundancy;
- superseding knowledge;
- loss of economic relevance;
- material degradation;
- persistent inability to satisfy current Decision-eligibility requirements;
- obsolete scope;
- objective lifecycle criteria defined elsewhere in governance.

A single losing trade, a single period of non-use, or mere age is insufficient
to retire knowledge.

Retirement does not erase historical knowledge.

---

## 20. Invalidation

Invalidation is stronger than retirement.

Knowledge should be invalidated only when objective evidence establishes that
the proposition/artifact cannot retain its prior scientific standing within the
relevant scope, for example because of a material methodological defect,
falsified provenance, unrecoverable data-quality failure, or decisive
contradictory evidence under applicable criteria.

Invalidated artifacts remain historically resolvable where retention governance
requires them.

---

## 21. Archival

Archival is a retention/access condition and must not be used as an ambiguous
substitute for scientific status.

An artifact may be archived because it is:

- retired;
- superseded;
- invalidated;
- historically important;
- rarely accessed;
- expensive to keep in active storage.

Archival must preserve required identity, lineage, provenance, and retrieval
metadata.

---

## 22. Physical Retention

Physical retention follows Storage Retention and Artifact Governance.

Knowledge lifecycle status alone does not grant deletion authority.

At minimum, MTS must distinguish:

```text
canonical durable knowledge
active research state
historical research lineage
cache / transient working data
```

Protected canonical knowledge must not be deleted merely to reduce storage
pressure or because retrieval rank is low.

---

## 23. Cache and Working Data

Cache and temporary working data should expire under objective retention rules.

A cache object that becomes scientifically or operationally valuable must be
published/reclassified through the governed artifact path before its disposable
cache copy is treated as protected.

Temporary data must not acquire canonical status merely because it is retained
for a long time.

---

## 24. Redundancy

MTS should detect materially redundant canonical knowledge.

Redundancy review should consider whether multiple artifacts:

- express materially equivalent propositions;
- differ only in obsolete representation;
- provide independent evidence that must remain distinct;
- apply to meaningfully different scopes;
- preserve required historical lineage.

Redundancy may justify retrieval demotion, consolidation through a new governed
artifact, supersession, or retirement.

It must not cause silent deletion of scientifically distinct evidence.

---

## 25. Decision SoK Assembly

Ordinary Decision SoK assembly should preferentially retrieve:

1. Decision-eligible knowledge;
2. relevant knowledge for the subject/time/use;
3. higher-active-utility knowledge where relevance is otherwise comparable;
4. necessary contradictory/uncertainty status attached to that knowledge;
5. sufficient provenance/status metadata to explain why the knowledge is
   current and applicable.

The SoK must not indiscriminately ingest the entire Research Nexus.

Cold canonical knowledge remains available for targeted retrieval when the
current context makes it relevant.

---

## 26. Utility Metrics Must Not Become Self-Fulfilling

Retrieval ranking must not create a feedback loop in which low-ranked knowledge
can never demonstrate usefulness because it is never eligible to be retrieved.

Implementations should preserve mechanisms for:

- context-triggered retrieval of cold knowledge;
- exploration where scientifically/economically justified;
- periodic utility review;
- detection of newly relevant regimes/contexts;
- research queries that intentionally search beyond the hot working set.

Utility optimization must not blind MTS to rare but important knowledge.

---

## 27. Economic Objective

Knowledge lifecycle management must support the MTS objective rather than
optimize storage metrics for their own sake.

Utility evaluation should ask whether knowledge contributes, directly or
indirectly, to:

- opportunity identification;
- better investment Decisions;
- improved risk-adjusted economic outcomes;
- avoidance of bad Decisions;
- better sizing/timing/exit;
- identification of material uncertainty;
- efficient research allocation;
- prevention of repeated failed inquiry.

Knowledge may have economic value by preventing action as well as by causing
action.

---

## 28. Negative Knowledge

A negative finding or knowledge proposition may remain valuable when it
reliably prevents MTS from pursuing an unproductive hypothesis, invalid setup,
unsafe extrapolation, or low-value opportunity.

Low action frequency must therefore not be confused with low utility.

Where practical, utility measurement should recognize avoided work and avoided
bad Decisions.

---

## 29. Learning & Governance Responsibilities

Learning & Governance may evaluate and recommend:

- retrieval ranking changes;
- utility demotion/promotion;
- revalidation;
- scope constraint;
- contradiction investigation;
- supersession;
- retirement;
- redundancy review.

Its recommendation does not replace any independent authority/verdict required
by policy for a lifecycle transition.

Learning tasks and resulting revalidation/research requests use the common Task
Manager.

---

## 30. Accountability Boundary

Accountability controls the Knowledge Promotion gate where required by policy.

This policy does not give Accountability ownership of ordinary retrieval
ranking, caching, or routine storage optimization.

Where a later lifecycle transition requires independent authority under
governance, the applicable verdict must exist before the Research Nexus records
that higher-authority transition.

No component may authorize its own promotion of knowledge authority.

---

## 31. Research Nexus Responsibilities

The Research Nexus must preserve enough governed state to:

- identify current lifecycle/scientific status;
- assemble point-in-time SoK views;
- apply retrieval rank without rewriting lifecycle;
- distinguish hot/normal/cold retrieval treatment where implemented;
- preserve scope/applicability;
- preserve supersession/retirement/invalidation lineage;
- link unresolved material contradictions;
- preserve required provenance;
- support historical reconstruction;
- enforce retention/deletion eligibility.

The Nexus records governed state. It does not invent scientific authority.

---

## 32. Task Manager Responsibilities

Lifecycle work requiring execution must be represented as governed tasks.

Examples include:

- revalidation;
- contradiction investigation;
- redundancy review;
- cache retirement;
- archival;
- retrieval-index maintenance;
- utility review.

Task scheduling priority must not alter scientific validity.

---

## 33. Observability

MTS should expose lifecycle metrics sufficient to detect knowledge bloat and
knowledge neglect without confusing those metrics with scientific evidence.

Useful operational metrics may include:

- canonical knowledge count by lifecycle state;
- hot/normal/cold counts;
- retrieval distribution;
- last relevant access age;
- eligible opportunities since material use;
- low-utility review backlog;
- revalidation backlog;
- contradiction backlog;
- supersession/retirement backlog;
- cache volume and retirement backlog;
- duplicate/redundancy candidates.

Operational metrics do not independently authorize scientific conclusions.

---

## 34. Auditability

For every material lifecycle transition, MTS must be able to reconstruct:

```text
prior knowledge state
→ trigger/evidence
→ evaluation
→ objective criteria
→ recommendation
→ required authority/verdict
→ resulting lifecycle/scientific status
→ Decision-eligibility effect
→ retrieval/storage effect
→ preserved lineage
```

---

## 35. Prohibited Behavior

MTS must not:

- equate age with irrelevance;
- equate non-use with invalidity;
- equate frequent use with scientific validity;
- promote knowledge because it is popular or frequently retrieved;
- retire knowledge because one trade lost;
- retain knowledge in the hot path merely because it is old/canonical;
- allow maintenance reads to masquerade as relevant use;
- delete protected canonical knowledge solely to recover disk space;
- let ranking silently mutate lifecycle;
- let storage tier silently mutate Decision eligibility;
- hide material contradiction from Decision;
- erase superseded/retired/invalidated lineage;
- keep reproducible temporary research debris indefinitely without retention
  justification;
- allow a component to authorize its own knowledge promotion.

---

## 36. Initial Implementation Requirements

The first implementation should prove the lifecycle with the smallest useful
vertical slice.

At minimum it should support:

1. canonical knowledge identity/version;
2. current lifecycle/scientific status;
3. Decision-eligibility metadata;
4. retrieval rank;
5. `last_relevant_access`;
6. `decision_use_count`;
7. `eligible_opportunities_since_use` where measurable;
8. hot/normal/cold retrieval treatment or equivalent;
9. revalidation request/result;
10. contradiction linkage;
11. supersession/retirement lineage;
12. retention classification;
13. point-in-time SoK reconstruction.

Sophisticated utility models are not required for the first implementation.
Objective, inspectable rules are preferred over opaque complexity.

---

## 37. Closing Principle

> **MTS preserves scientific truth and lineage without forcing every valid fact
> to remain in the active working set. Knowledge authority, scientific status,
> Decision eligibility, active utility, retrieval priority, and physical
> retention are governed separately so that useful knowledge stays accessible,
> rare knowledge is not forgotten, and low-value accumulation does not bloat the
> system.**
