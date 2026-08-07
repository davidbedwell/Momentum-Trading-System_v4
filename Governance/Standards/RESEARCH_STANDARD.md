# Momentum Trading System — Research Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, `IDENTITY_STANDARD.md`, `ARTIFACT_GOVERNANCE_STANDARD.md`, `SCHEMA_STANDARD.md`, `STORAGE_RETENTION_STANDARD.md`, `ENGINE_INTERFACE_STANDARD.md`, `TASK_MANAGEMENT_STANDARD.md`, and `DATA_QUALITY_STANDARD.md`.

---

## 1. Purpose

This standard defines how Momentum Trading System (MTS) conducts governed research.

It governs:

- research questions;
- hypotheses;
- Research Plans;
- iterative questioning;
- evidence requirements;
- Discovery interaction;
- Data Intake requests;
- missing capability;
- insufficient evidence;
- contradiction;
- replication;
- convergence;
- findings;
- knowledge candidates;
- research campaigns;
- State of Knowledge interaction.

The purpose of MTS research is not to produce persuasive prose. It is to produce traceable, testable, decision-relevant knowledge from evidence.

---

## 2. Governing Principle

> **Research is an iterative process of asking answerable questions, obtaining governed evidence, evaluating what that evidence establishes, and deciding objectively what must be asked next.**

One analysis pass is not presumed to constitute research completion.

---

## 3. Research Serves the MTS Mission

MTS research exists to improve the system's ability to identify and act on profitable opportunities under governed risk.

Research is not an end in itself.

Scientific rigor is required because unreliable knowledge cannot support reliable decisions.

---

## 4. Research and Decision Boundary

Research determines what evidence supports.

Decision determines what action, if any, should be taken given:

- current state;
- validated knowledge;
- uncertainty;
- risk;
- implementation constraints;
- portfolio context;
- policy.

Research must not silently become Decision.

Decision must not invent research conclusions.

---

## 5. Research Director Role

The Research Director owns research intent and research progression.

It may:

- formulate questions;
- formulate hypotheses;
- construct Research Plans;
- identify evidence requirements;
- identify contradictions;
- request additional data or analysis;
- create research needs;
- evaluate whether evidence is sufficient;
- determine whether another research iteration is warranted;
- determine convergence according to governed criteria;
- propose knowledge candidates.

It does not own worker scheduling.

---

## 6. Accountability Role

The Accountability Engine independently controls two research gates under policy:

1. Research Admission for proposed Research Plans;
2. Knowledge Promotion for Knowledge Candidates.

It evaluates whether required objective criteria have been demonstrated. It
does not author the scientific conclusion, schedule workers, or approve
individual investment Decisions.

## 7. Task Manager Role

The Task Manager owns execution coordination.

The Research Director expresses admitted research intent through governed Task
Requests and dependencies.

Conceptually:

```text
Research Director
      ↓
Proposed Research Plan
      ↓
Accountability — Research Admission
      ↓
Task Manager
      ↓
eligible engines/workers
      ↓
evidence/findings
      ↓
Research Director
      ↓
Knowledge Candidate
      ↓
Accountability — Knowledge Promotion
```

This boundary separates scientific authorship, independent gatekeeping, and infrastructure scheduling.

---

## 8. Discovery Role

Discovery performs governed measurement, comparison, pattern search, relationship analysis, and other empirical work within its declared capabilities.

Discovery does not determine by itself that a measured relationship is durable knowledge.

Discovery produces evidence and findings for governed evaluation.

---

## 9. Data Intake Role

Data Intake acquires, validates, normalizes, and publishes governed data required by research.

When research requires unavailable data, the Research Director may generate a governed request that ultimately routes to Data Intake.

Research Director must not privately acquire data in a way that bypasses Intake governance.

---

## 10. Research Campaign

A Research Campaign is a durable grouping of related research work.

A campaign may investigate:

- a feature;
- an event family;
- a market behavior;
- an interaction;
- a decision hypothesis;
- a contradiction;
- a newly observed live-market pattern;
- a missing knowledge area.

Campaign identity must survive multiple questions and executions.

---

## 11. Research Question

A Research Question is a governed artifact.

It should identify:

```text
question_id
campaign_ref
question_type
question
scope
motivation
required_evidence
created_at
producer
status
```

Exact schema belongs in Governance/Schemas.

---

## 12. Question Types

Initial research-question taxonomy may include:

```text
DISCOVERY
RELATIONSHIP
TEMPORAL
CONTEXT
ECONOMIC_VALUE
CONTRADICTION
MISSING_EVIDENCE
CONVERGENCE
```

This taxonomy is extensible.

Question type guides method; it does not predetermine the answer.

---

## 13. Questions Must Be Testable

A governed research question must be sufficiently precise that MTS can determine:

- what evidence would bear on it;
- what population/context is relevant;
- what measurement is required;
- what would count as insufficient evidence;
- what result would justify another question.

Vague curiosity may initiate question formation, but must be refined before governed execution.

---

## 14. Hypothesis

Where appropriate, a question may include one or more hypotheses.

Hypotheses must be recorded before examining the evidence intended to test them when confirmatory inference is claimed.

Exploratory discovery may generate hypotheses for later testing.

MTS must distinguish exploratory from confirmatory work.

---

## 15. Research Plan

A Research Plan translates a question into executable evidence requirements.

It should identify, as applicable:

```text
research_plan_id
question_ref
method
required_inputs
required_capabilities
tasks
dependencies
evaluation criteria
stopping criteria
limitations
```

The Research Plan is not the execution queue.

After required Research Admission, the Task Manager converts/runs its work through governed tasks.

---

## 16. Research Plan Versioning

A materially changed Research Plan must be versioned or superseded.

MTS must preserve what plan produced prior evidence.

Research history must not be rewritten to make later methodology appear to have been planned from the beginning.

---

## 17. Iterative Research

After evidence returns, the Research Director must evaluate what was learned and what remains unresolved.

Possible next states include:

```text
ANSWER_SUPPORTED
ANSWER_NOT_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
MORE_RESEARCH_REQUIRED
MISSING_CAPABILITY
CONVERGED
```

Exact vocabulary belongs in schemas.

---

## 18. Next-Question Generation

A new question should arise from an identifiable research reason.

Examples:

- unexplained variance;
- conditional relationship;
- contradictory evidence;
- temporal instability;
- subgroup difference;
- missing data;
- alternative explanation;
- economic significance uncertainty;
- robustness concern;
- newly discovered interaction.

The Research Director must preserve the link from the new question to the evidence that motivated it.

---

## 19. No Infinite Question Loop

Iterative questioning must have governed stopping criteria.

The Research Director must not continue generating questions merely because another question is imaginable.

Research continues when expected information value justifies additional work under policy/resource constraints.

---

## 20. Convergence

Convergence means the governed research objective has reached a state where additional permitted research is not expected to materially change the current conclusion enough to justify its cost or delay.

Convergence is not “the AI feels confident.”

It must be based on objective evidence criteria.

---

## 21. Convergence Criteria

Depending on the research family, criteria may include:

- required evidence obtained;
- required independent tests completed;
- effect direction stable;
- effect magnitude sufficiently bounded;
- contradiction resolved or characterized;
- required contexts evaluated;
- holdout/replication criteria met;
- marginal value of another iteration below governed threshold;
- remaining uncertainty explicitly characterized.

Criteria must be defined before a research workflow can claim convergence.

---

## 22. Insufficient Evidence

`INSUFFICIENT_EVIDENCE` is a legitimate research result.

It means the required conclusion cannot be supported or rejected with the available valid evidence.

It is not:

- task failure;
- permission to fabricate;
- automatic evidence against the hypothesis.

The Research Director may request more research or close the question as unresolved.

---

## 23. Missing Capability

`MISSING_CAPABILITY` means MTS lacks a required tool, data source, method, engine capability, or interface necessary to answer the question validly.

The Research Director should create a governed Research Need describing:

- what is missing;
- why it is required;
- what question depends on it;
- whether an alternative valid method exists.

Then it proceeds according to campaign policy rather than blocking indefinitely.

---

## 24. Research Need

A Research Need is a durable request for capability or evidence not currently available.

Examples:

```text
new data field
new vendor/source
new analytical method
new Discovery capability
additional historical coverage
new event detector
```

A Research Need is not automatically approved implementation work.

It enters governance/prioritization.

---

## 25. Evidence

Evidence is governed material bearing on a research question.

Evidence must be traceable to:

- source data;
- method;
- execution;
- configuration;
- applicable quality results.

Evidence must not exist only as prose inside a report.

---

## 26. Finding

A Finding is a structured interpretation of measured evidence within a defined scope.

It should support:

- relationship;
- direction;
- magnitude/effect size;
- sample/context;
- uncertainty;
- limitations;
- evidence references;
- validation status;
- contradiction references.

A Finding is not automatically durable knowledge.

---

## 27. Negative Findings

Negative findings may be scientifically useful and must not be suppressed merely because they are not actionable.

Retention is proportional to value. Material negative findings that prevent repeated waste, alter current knowledge, or are required for reproducibility may be retained durably. Routine, duplicate, or cheaply reproducible negative working results may expire under retention policy after the Research Plan is resolved.

---

## 28. Contradictory Evidence

Contradictory evidence initiates or informs Active Research State; it is not promoted as contradictory “knowledge.”

While unresolved and material, the contradiction must remain linked to the affected knowledge/candidate and may lead to:

- scope refinement;
- conditional knowledge;
- additional research;
- reduced uncertainty/confidence qualification;
- reduced decision eligibility;
- retirement/supersession of knowledge.

After resolution, contradictory working material is default-to-expire. Preserve durably only the minimum evidence or compact resolution record required to explain, reproduce, challenge, or improve a materially relevant knowledge or Decision state.

---

## 29. Replication

Important findings should be replicated when required by policy.

Replication should vary relevant dimensions where appropriate, such as:

- instrument;
- sector;
- market regime;
- time period;
- data source;
- holdout sample.

Repeating the same computation on the same data is not independent replication.

---

## 30. Robustness

Research should evaluate whether a finding depends excessively on:

- one ticker;
- one period;
- one parameter;
- one outlier;
- one regime;
- one data source;
- one arbitrary threshold.

Robustness requirements should scale with the importance of the conclusion.

---

## 31. Generalization

MTS must distinguish:

```text
observed in this sample
replicated in related samples
generalized across defined scope
```

A finding from AAPL does not automatically become universal equity knowledge.

Applicability must be explicit.

---

## 32. Context

Research should test whether relationships vary by context.

Examples:

- volatility;
- liquidity;
- market regime;
- sector;
- capitalization;
- event type;
- duration;
- magnitude;
- instrument;
- broader market state.

Context can be part of the edge rather than noise to eliminate.

---

## 33. Temporal Stability

A relationship may change over time.

Research should evaluate temporal stability when relevant.

Knowledge must be capable of representing:

- stable;
- regime-dependent;
- decaying;
- recently strengthened;
- unstable;
- insufficiently tested.

---

## 34. Economic Value

Statistical relationship alone is not enough for decision relevance.

Research should evaluate economic value where applicable, considering:

- magnitude;
- achievable return;
- adverse excursion;
- time horizon;
- transaction cost;
- liquidity;
- implementation constraints;
- risk/reward.

Research evaluates these properties; Decision determines whether to act.

---

## 35. Tradable Directional Opportunity

Research must not require bull/bear labels as its primary conceptual framework.

MTS may study tradable directional opportunities across:

```text
LONG
SHORT
```

with duration, magnitude, risk/reward, context, and implementation characteristics represented explicitly.

---

## 36. Opportunity Definitions Are Researchable

Thresholds for:

- return;
- holding period;
- risk/reward;
- event magnitude;

must be treated as hypotheses/parameters subject to empirical evaluation rather than eternal constants unless governance explicitly fixes them for a particular experiment.

---

## 37. Event Research

MTS treats “event” as a broad extensible category.

Research may investigate event families such as:

```text
directional price
volatility
liquidity
relative strength
derivatives
fundamental
market structure
future discovered families
```

No current event taxonomy is assumed complete.

---

## 38. New Pattern Discovery

Discovery or Market Discovery may surface a pattern not represented in current knowledge.

The pattern should be recorded as an observation/candidate and, where warranted, generate a Research Question or Research Need.

It must not become knowledge merely because it was detected repeatedly in a short live window.

---

## 39. Feature Research

Feature research should determine not merely whether a feature correlates with an outcome, but:

- incremental contribution;
- redundancy;
- interaction;
- stability;
- temporal behavior;
- context dependence;
- economic relevance.

---

## 40. Feature Classification

Where useful, feature research may classify features using governed categories such as:

```text
CORE_CONTRIBUTOR
CONDITIONAL_CONTRIBUTOR
INTERACTION_ONLY
REDUNDANT
LOW_CONTRIBUTION
UNSTABLE
INSUFFICIENT_EVIDENCE
RETIRED_FOR_CURRENT_CAMPAIGN
```

Classification criteria must be objective and versioned.

---

## 41. Interaction Research

A feature with weak standalone contribution may still be important in interaction.

MTS must not discard features solely because univariate tests are weak.

Interaction evidence must be evaluated separately.

---

## 42. Redundancy

Redundant features may remain scientifically valid while offering little incremental decision value.

Redundancy is not equivalent to falsehood.

Research should identify what information is duplicated and under what contexts.

---

## 43. Data Snooping

Exploratory search across many features, thresholds, horizons, or patterns increases false-discovery risk.

MTS must record search scope and apply appropriate validation/holdout/replication before promoting discoveries.

---

## 44. Holdout Integrity

Holdout data must remain unavailable to the process whose performance it is intended to evaluate.

A model/research process must not adapt repeatedly to the same nominal holdout and continue calling it unseen.

---

## 45. Forward-Looking Integrity

When evaluating Decision-like behavior historically, MTS must restrict the simulated decision to information available at the decision timestamp.

Future outcomes may be used only for later evaluation.

---

## 46. Overlap

Research involving opportunities or events must define overlap rules.

If overlapping opportunities are excluded, the exclusion algorithm must be deterministic and preserved in methodology/provenance.

---

## 47. Sample Construction

Research must preserve how samples were selected.

A result must be able to answer:

- what universe was eligible;
- what was excluded;
- why;
- what date range applied;
- what event definition applied;
- whether selection used future information.

---

## 48. Research Reproducibility

A material research result should be reproducible from:

- governed input identities/versions;
- Research Plan/version;
- method/version;
- configuration;
- software/model version;
- random seed where applicable.

---

## 49. Research Reports

Human-readable research reports are views of governed research artifacts.

A report may summarize:

- question;
- method;
- evidence;
- findings;
- limitations;
- next questions.

The report itself must not be the only location of canonical findings.

---

## 50. Knowledge Candidate

A sufficiently supported Finding or synthesis may become a Knowledge Candidate.

A candidate must identify:

- proposition;
- supporting evidence;
- contradictory evidence;
- applicability;
- uncertainty;
- replication/validation state;
- limitations.

Candidate status does not itself make it decision-eligible.

The Research Director may author a Knowledge Candidate but may not independently pass the Accountability gate governing promotion of its own candidate.

---

## 51. Knowledge Promotion

Promotion from Knowledge Candidate to a knowledge-authority state requiring independent review must satisfy objective criteria defined by artifact governance/policy and receive the required Accountability Knowledge Promotion verdict.

Possible criteria may include:

- evidence quality gates passed;
- required replication completed;
- holdout requirements satisfied;
- contradiction characterized;
- applicability defined;
- uncertainty recorded;
- provenance complete.

Promotion criteria must be inspectable.

---

## 52. Scientific Validity vs Retrieval Priority

Scientific validity and retrieval priority are separate.

Knowledge may be scientifically valid but rarely useful.

Knowledge may be frequently accessed but weakly supported.

Usage frequency must not determine scientific validity.

---

## 53. Knowledge Ranking

Knowledge ranking may consider dimensions such as:

- decision relevance;
- recency;
- applicability;
- replication strength;
- uncertainty;
- usage;
- retrieval cost.

Ranking is for retrieval/attention.

It must not rewrite the underlying evidence status.

---

## 54. State of Knowledge

The State of Knowledge (SoK) is a governed point-in-time logical view over current relevant canonical knowledge.

It is not a separate truth database and it is not the entire Research Nexus.

SoK assembly may consider:

- current validity;
- applicability;
- uncertainty/confidence qualification;
- supersession;
- material limitations produced by resolved contradiction;
- recency;
- decision eligibility;
- retrieval ranking.

Active contradictions, unresolved questions, rejected hypotheses, and bulky research working material remain outside the ordinary Decision SoK. Research may query those states explicitly when investigating what remains unresolved.

---

## 55. SoK Query

A SoK query should be scoped to the question/decision being addressed.

The system should not indiscriminately load all accumulated knowledge into every reasoning context.

Relevant knowledge should be retrieved through governed indexing/ranking.

---

## 56. Supersession

New research may supersede prior knowledge.

Superseded knowledge remains preserved for:

- historical decision reconstruction;
- audit;
- learning;
- scientific lineage.

Supersession does not mean deletion.

---

## 57. Knowledge Retirement

Knowledge may be retired from current decision eligibility when objective criteria indicate:

- instability;
- failed replication;
- regime expiration;
- contradiction;
- methodological defect;
- superseding evidence.

Retirement status and reason must be explicit.

---

## 58. Research Cost

Research consumes:

- compute;
- data/provider quota;
- storage;
- time;
- opportunity cost.

Research planning may consider cost when selecting the next question.

Cheap but low-value questions should not crowd out high-information research indefinitely.

---

## 59. Research Priority

Research priority may consider:

- expected decision value;
- unresolved contradiction;
- frequency of relevant market occurrence;
- knowledge gap;
- dependency blocking;
- cost;
- urgency;
- uncertainty reduction.

Priority is governed separately from scientific validity.

---

## 60. Autonomous Research

MTS may perform autonomous research within governed limits.

Autonomy must still preserve:

- task identity;
- Research Plan;
- evidence lineage;
- resource limits;
- stopping criteria;
- authority boundaries.

“Autonomous” does not mean unbounded.

---

## 61. Research Continuation After Restart

Active campaigns, questions, plans, and dependencies required for continuation are durable Class II state.

The Research Director must be able to resume without relying on conversational/in-memory memory alone.

---

## 62. Research Failure

Software/execution failure is distinct from research outcome.

Examples:

```text
provider unavailable → execution failure
invalid schema → execution failure
no measurable relationship → research result
insufficient sample → research result
missing required capability → research result/capability need
```

---

## 63. Research Audit

MTS should be able to reconstruct:

```text
question
→ plan
→ tasks
→ executions
→ evidence
→ findings
→ next question
→ convergence/promotion
```

This chain is part of scientific provenance.

---

## 64. Human Intervention

Human researchers may:

- initiate questions;
- modify/approve plans where policy requires;
- stop campaigns;
- supply context;
- approve new capabilities.

Human intervention must not silently rewrite prior research history.

---

## 65. Initial v2 Research Implementation

The first implementation should support:

1. Research Campaign;
2. Research Question;
3. Research Plan;
4. Research Need;
5. iterative next-question generation;
6. Accountability Research Admission;
7. Task Manager submission;
8. Finding;
9. `INSUFFICIENT_EVIDENCE`;
10. `MISSING_CAPABILITY`;
11. contradiction links;
12. objective stopping/convergence criteria;
13. Knowledge Candidate;
14. Accountability Knowledge Promotion gate;
13. full question-to-evidence lineage.

It need not begin with every advanced statistical method.

---

## 66. Initial Proof of Concept

A valid v2 Research Director proof should demonstrate:

```text
Question 1
   ↓
Research Plan
   ↓
Discovery work
   ↓
Finding
   ↓
Research Director evaluates gap
   ↓
Question 2
   ↓
additional work
   ↓
Finding
   ↓
objective convergence or explicit unresolved result
```

A single prewritten chain of fixed questions does not prove iterative research.

The next question must depend on returned evidence.

---

## 67. Testing Requirements

Research tests should include:

- answerable question;
- invalid/vague question refinement;
- plan creation;
- evidence-driven next question;
- contradiction;
- insufficient evidence;
- missing capability;
- negative finding;
- convergence;
- failure to converge within resource policy;
- restart/resume;
- holdout protection;
- look-ahead prevention;
- knowledge candidate promotion gate;
- supersession lineage.

---

## 68. Prohibited Practices

The following are prohibited:

- treating one analysis pass as automatically complete research;
- fixed scripted question chains presented as adaptive research;
- deleting material contradictory/negative evidence before governed resolution or required lineage is preserved;
- using future information in historical reasoning;
- promoting knowledge based on usage frequency;
- calling an execution failure a scientific result;
- calling insufficient evidence a failed task;
- infinite autonomous questioning;
- Research Director private worker scheduling;
- canonical findings stored only in prose reports;
- silently rewriting old research after methodology changes.

---

## 69. Conformance

A research system conforms when it:

1. uses governed questions and plans;
2. preserves evidence lineage;
3. generates subsequent questions from returned evidence;
4. distinguishes exploration from confirmation where material;
5. preserves material negative/contradictory evidence through resolution and retains only justified durable lineage afterward;
6. protects temporal/holdout integrity;
7. uses objective convergence criteria;
8. supports insufficient evidence and missing capability;
9. separates Research Director intent from Task Manager scheduling;
10. promotes knowledge through objective gates;
11. separates scientific validity from ranking/usage;
12. preserves historical research lineage;
13. survives restart through durable state.

---

## 70. Companion Governance

This standard operates with:

```text
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/DATA_QUALITY_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/DECISION_STANDARD.md
Governance/Standards/LEARNING_GOVERNANCE_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 71. Closing Principle

MTS must always be able to answer:

> **What question were we trying to answer, what evidence did we obtain, what did that evidence actually establish, why did we ask the next question, and what objective condition caused us to stop?**

If the answer is merely “the model decided it was done,” the research process is not sufficiently governed.
