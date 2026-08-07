# Momentum Trading System — Research Policy

**Status:** Canonical
**Authority:** Governing policy subordinate to `CHARTER.md`, the canonical MTS architecture set, and applicable MTS Standards, Contracts, and Schemas.

---

## 1. Purpose

This policy defines the current operational rules by which MTS research:

- begins;
- is prioritized;
- continues;
- requests additional evidence or capability;
- converges or closes unresolved;
- creates Knowledge Candidates;
- qualifies candidates for lifecycle promotion;
- and consumes bounded resources.

This policy does not define schemas, engine interfaces, storage formats, or trading decisions.

---

## 2. Governing Objective

MTS research exists to improve the system's ability to create long-term wealth through more accurate, consistent, explainable, reproducible, and generalizable market knowledge.

Research is not rewarded for producing more questions, more artifacts, more features, or more complexity.

A research action is justified when its expected contribution to knowledge or future decision quality is worth its scientific, computational, data, time, and opportunity cost.

Scientific validity and economic usefulness are distinct dimensions. Neither substitutes for the other.

---

## 3. Research Authority Boundary

The Research Director owns research intent and progression.

It may:

- formulate and refine questions;
- formulate hypotheses;
- create and version proposed Research Plans;
- identify evidence requirements;
- respond to Accountability gate outcomes;
- request governed work after required Research Admission;
- identify contradictions and gaps;
- evaluate returned evidence;
- generate evidence-dependent next questions;
- determine convergence under this policy;
- close questions as unresolved;
- create Knowledge Candidates.

It may not:

- independently admit its own Research Plan across the Research Admission gate;
- independently pass the Knowledge Promotion gate for its own Knowledge Candidate;
- schedule workers directly;
- bypass Data Intake governance;
- fabricate evidence;
- convert execution failure into a scientific result;
- change this policy;
- silently alter historical research state.

The Accountability Engine independently controls the Research Admission and
Knowledge Promotion gates by applying the objective criteria defined in this
policy and related governance. It does not author scientific conclusions,
schedule workers, own canonical knowledge, make investment Decisions, or
approve individual trades.

---

## 4. Research Eligibility Requirements

A question may enter governed execution only when it is sufficiently defined to identify:

1. the proposition or uncertainty being investigated;
2. the relevant subject, population, context, or market scope;
3. evidence capable of bearing on the question;
4. the method or capability required to obtain that evidence;
5. what would constitute insufficient evidence;
6. what evidence could materially change the current conclusion;
7. initial stopping or convergence criteria.

A vague idea may be preserved as a Research Need or refined into a Research Question, but it must not consume governed execution resources indefinitely without becoming testable.

---

## 5. Exploratory and Confirmatory Research

MTS must distinguish exploratory from confirmatory work.

Exploratory research may:

- search for relationships;
- discover interactions;
- identify candidate event families;
- generate hypotheses;
- identify unexpected contexts.

Confirmatory research claiming validation must preserve the hypothesis, material method, evaluation criteria, and protected evidence boundary before examining the evidence intended to provide confirmation.

Exploratory evidence may motivate a hypothesis. It must not be relabeled after the fact as independent confirmation of that same hypothesis.

---


## 6. Research Admission Gate

A proposed Research Plan must receive the required Accountability Research
Admission verdict before governed research execution begins.

Accountability evaluates whether the plan:

1. plausibly advances the Charter objective directly or through a necessary
   scientific/infrastructure dependency;
2. is testable;
3. is not materially duplicative of existing SoK or Active Research State
   without a justified replication/revalidation purpose;
4. identifies evidence capable of changing the conclusion;
5. defines stopping criteria;
6. preserves applicable scientific-integrity safeguards;
7. uses available or explicitly approved capabilities;
8. requests resources proportionate to expected information/Decision value;
9. complies with applicable authority and policy.

Allowed verdict semantics are:

```text
RP_ADMITTED
RP_ADMITTED_WITH_LIMITS
RP_REVISION_REQUIRED
RP_DUPLICATIVE
RP_DEFERRED
RP_REJECTED
```

A negative or limited verdict must identify the failed criterion, reason, and
required correction where correction is possible.

Research Director may revise and resubmit. It may not override the gate.

## 7. Research Plan Requirement

Every governed execution sequence must be attributable to a Research Plan or equivalent governed research state.

A Research Plan must define, as applicable:

- question;
- method;
- required inputs;
- required capabilities;
- dependencies;
- evaluation criteria;
- stopping criteria;
- expected evidence;
- known limitations;
- resource envelope.

A materially changed plan must be versioned or superseded. Prior evidence remains attributable to the plan that produced it.

---

## 8. Evidence-Dependent Iteration

After material evidence returns, the Research Director must evaluate what changed before generating the next question.

A next question is permitted only when an identifiable evidence-based reason exists, such as:

- unresolved contradiction;
- unexplained variance;
- scope dependence;
- temporal instability;
- subgroup difference;
- missing evidence;
- robustness concern;
- alternative explanation;
- uncertain economic significance;
- newly discovered interaction;
- failure of a required validation condition.

A fixed prewritten sequence may be used as a method when scientifically appropriate, but it does not by itself demonstrate adaptive iterative research.

---

## 9. Research Outcome States

A research iteration must end in an explicit governed outcome rather than ambiguous prose.

At minimum, MTS must be able to represent the semantic equivalents of:

```text
ANSWER_SUPPORTED
ANSWER_NOT_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
MORE_RESEARCH_REQUIRED
MISSING_CAPABILITY
CONVERGED
```

Exact machine vocabulary belongs in Schemas.

An execution failure is not a research outcome.

---

## 10. Insufficient Evidence

`INSUFFICIENT_EVIDENCE` is a valid scientific result when available valid evidence cannot support or reject the required conclusion.

It must identify why evidence is insufficient, such as:

- inadequate observations;
- inadequate historical coverage;
- unavailable data;
- inadequate validation;
- unresolved contradiction;
- unsupported inference;
- question outside supported scope.

Insufficient evidence does not count as evidence against a hypothesis unless the research design makes that inference valid.

---

## 11. Missing Capability

When valid resolution requires a capability MTS does not possess, the Research Director must create a governed Research Need identifying:

- the missing capability;
- the question it blocks;
- why the capability is required;
- whether a valid alternative exists;
- expected value of resolving the gap where estimable.

A missing capability must not cause indefinite blocking.

The campaign may:

- proceed through a valid alternative;
- defer the blocked branch;
- close the question as unresolved;
- or await separately approved capability work.

A Research Need is not automatic authorization to build or purchase the capability.

---

## 12. Contradiction Policy

Contradiction is a research condition, not canonical knowledge merely because it exists.

While a contradiction is active, MTS must preserve enough governed state to:

- identify the affected proposition;
- identify conflicting evidence;
- identify relevant differences in sample, context, method, time, or data;
- prevent unjustified certainty;
- support resolution.

A contradiction may result in:

```text
MORE_RESEARCH_REQUIRED
NARROW_APPLICABILITY
REDUCED_ELIGIBILITY
SUPERSESSION
RETIREMENT
NO_CHANGE
```

After resolution, contradictory working material is default-to-expire under retention policy unless durable preservation is justified by reproducibility, audit, scientific lineage, or material effect on knowledge or Decisions.

Contradiction must not be resolved by deleting inconvenient evidence.

---

## 13. Negative Findings

A valid negative finding is a scientific result.

Negative findings that materially:

- prevent repeated research waste;
- constrain applicability;
- reject an important hypothesis;
- explain a material Decision or knowledge state;
- or are required for reproducibility

may be retained durably under retention policy.

Routine, duplicate, or cheaply reproducible negative working material need not be retained permanently.

---

## 14. Replication Policy

Replication is required before a Knowledge Candidate may become decision-eligible canonical knowledge when the proposition is materially predictive, economically consequential, or intended to generalize beyond the evidence on which it was discovered.

At least one validation must use evidence not used to discover or tune the proposition.

Where the claim asserts generalization across a dimension, validation must test that dimension where data permits. Relevant dimensions may include:

- unseen instruments;
- unseen time periods;
- unseen market regimes;
- sectors or industries;
- independent data sources;
- protected holdout samples.

Repeating the same computation on the same evidence is reproducibility, not independent replication.

A narrowly scoped descriptive fact may be exempt from independent replication when its scope makes generalization irrelevant, but the exemption and reason must be explicit.

---

## 15. Holdout and Look-Ahead Policy

Evidence used for discovery, tuning, threshold selection, or model selection must not masquerade as protected validation evidence.

Historical research must not use information unavailable at the historical decision or observation time when making claims about contemporaneous knowledge or prediction.

If protected holdout evidence is exposed and subsequently influences method selection, it is no longer a valid untouched holdout for that method.

---

## 16. Robustness Requirement

A materially predictive Knowledge Candidate must be evaluated for excessive dependence on applicable factors such as:

- one instrument;
- one period;
- one regime;
- one parameter choice;
- one outlier;
- one data source;
- one arbitrary threshold.

A discovered dependence does not automatically invalidate the candidate.

When supported by evidence, MTS should narrow applicability rather than falsely generalize or unnecessarily discard a useful conditional relationship.

---

## 17. Convergence

Research may claim `CONVERGED` only when the Research Plan's required criteria have been evaluated and additional permitted research is not expected to materially change the current conclusion enough to justify its cost or delay.

Convergence requires all applicable conditions below:

1. required evidence defined by the current Research Plan has been obtained or explicitly determined unavailable;
2. required validation/replication has been completed or explicitly determined inapplicable;
3. material contradictions are resolved or characterized;
4. applicability is defined to the level supported by evidence;
5. material uncertainty and limitations are recorded;
6. no unresolved evidence gap is expected to materially reverse or materially alter the conclusion within the supported scope;
7. the expected marginal information value of another currently available iteration does not justify its cost or delay.

Convergence is not a confidence score and must not be inferred from fluent reasoning, repeated agreement, or number of completed tasks.

---

## 18. Mandatory Stop Conditions

A research branch must stop or defer when any of the following applies:

- the governed objective has converged;
- the question has been answered sufficiently for its intended use;
- required evidence is unavailable and no valid alternative exists;
- required capability is unavailable and not currently authorized;
- the remaining question is outside campaign scope;
- further work would repeat equivalent evidence without material new information;
- the resource envelope is exhausted;
- continuing would violate a holdout, authority, data-quality, or scientific-integrity rule;
- the expected marginal information value no longer justifies cost or delay.

Stopping does not require a positive answer.

---

## 19. Research Priority

When multiple valid research items compete for resources, priority should be determined from explicit dimensions rather than arrival order or component identity.

Priority may consider:

1. expected contribution to Decision quality or economic value;
2. whether the work blocks a material downstream dependency;
3. severity of unresolved contradiction affecting current knowledge;
4. importance of the knowledge gap;
5. frequency/applicability of the phenomenon;
6. expected uncertainty reduction;
7. urgency/freshness;
8. expected research cost.

Scientific validity must not be altered by priority.

Priority determines what MTS studies first, not what MTS concludes.

---

## 20. Resource Policy

Every autonomous Research Plan must have a finite resource envelope.

The envelope must be expressible through one or more governed limits appropriate to the work, such as:

- maximum iterations;
- maximum task count;
- compute allocation;
- provider/data quota;
- elapsed-time limit;
- monetary/data-acquisition limit;
- storage allowance.

Exact values may be supplied by governed configuration where this policy permits.

Exhausting a resource envelope produces a controlled unresolved/convergence evaluation. It must not produce an infinite question loop.

Expansion of a material resource envelope requires authorized policy/configuration action.

---

## 21. Initial Resource Defaults

Until research-family-specific limits are approved, autonomous research uses conservative defaults:

```text
max_material_iterations_per_question: 12
max_child_questions_per_question: 8
max_consecutive_iterations_without_material_information_gain: 2
```

These limits are safety ceilings, not scientific convergence thresholds.

Reaching a ceiling requires the Research Director to:

1. evaluate current evidence;
2. record the unresolved issue;
3. either converge, close unresolved, create a Research Need, or request authorized expansion.

A materially new evidence branch may justify a new Research Plan rather than silently resetting counters on the existing plan.

---

## 22. Material Information Gain

For continuation purposes, an iteration has material information gain when it does at least one of the following:

- materially changes support for the proposition;
- materially narrows or expands applicability;
- materially changes estimated effect magnitude or uncertainty;
- resolves or creates a material contradiction;
- eliminates a plausible alternative explanation;
- establishes or fails a required validation condition;
- identifies a material new dependency or capability gap;
- materially changes expected decision relevance.

Producing another artifact, another narrative, or another statistically similar restatement is not material information gain.

---

## 23. Knowledge Candidate Gate

A Finding or synthesis may become a Knowledge Candidate only when it has:

- a precise proposition;
- governed evidence references;
- defined scope/applicability;
- uncertainty representation;
- known limitations;
- contradiction state;
- validation/replication state;
- complete provenance sufficient to reproduce or challenge the claim.

Candidate status does not imply decision eligibility.

---

## 24. Knowledge Promotion Gate

The Accountability Engine independently evaluates the Knowledge Promotion gate.

Research Director supplies the Knowledge Candidate, evidence, applicability,
uncertainty, limitations, and required promotion package. Accountability
verifies whether the applicable objective gates were demonstrated.

A Knowledge Candidate may advance to a knowledge-authority state governed by
this gate only when all applicable objective gates pass:

### 23.1 Integrity Gates — Mandatory

```text
PASS provenance complete
PASS input/data quality acceptable for the claim
PASS method/version/configuration identifiable
PASS result reproducible within governed tolerance
PASS no known look-ahead or protected-holdout violation
PASS proposition and applicability explicitly defined
PASS uncertainty and limitations explicitly represented
PASS material contradiction state characterized
```

Failure of any mandatory integrity gate blocks promotion.

### 23.2 Validation Gates — Mandatory for Predictive/Generalizable Claims

```text
PASS protected or otherwise independent validation
PASS required replication
PASS robustness appropriate to the claimed scope
PASS effect direction not dependent on a known methodological defect
PASS evidence sufficient for the claimed population/context
```

A candidate may be narrowed to a smaller supported scope and reevaluated rather than rejected globally.

### 23.3 Economic/Decision-Value Gate

For knowledge intended to influence investment Decisions, at least one of the following must be demonstrated on valid evaluation evidence:

```text
A. measurable incremental predictive information;
B. measurable improvement in risk characterization;
C. measurable improvement in opportunity selection/ranking;
D. measurable improvement in entry, scaling, exit, or implementation judgment;
E. measurable reduction of a material error, false action, or missed opportunity;
F. material explanatory/context value that improves Decision interpretation without being treated as predictive evidence.
```

Statistical significance alone does not satisfy this gate.

Win rate alone does not satisfy this gate.

Usage frequency does not satisfy this gate.

### 23.4 Accountability Gate Result

Knowledge Promotion evaluation must produce an inspectable Accountability
verdict:

```text
PROMOTION_GATES_PASSED
PROMOTION_GATES_PASSED_WITH_SCOPE
MORE_RESEARCH_REQUIRED
INSUFFICIENT_EVIDENCE
PROMOTION_BLOCKED
```

The verdict must identify which gates passed, failed, were inapplicable, or
remain unresolved.

A passing verdict authorizes the governed lifecycle mechanism to perform the
permitted transition. Accountability does not become the owner of the resulting
knowledge merely because it issued the gate verdict.

---

## 25. No Universal Arbitrary Statistical Threshold

This policy does not impose one universal p-value, effect size, sample count, win-rate threshold, or return threshold across all research families.

The appropriate quantitative acceptance criteria depend on:

- research question;
- outcome distribution;
- sample structure;
- multiple-testing burden;
- economic use;
- applicable risk;
- market context;
- method.

Research Plans or research-family policy profiles must define applicable quantitative thresholds before confirmatory evaluation.

Threshold selection must itself be traceable and must not be chosen after seeing protected validation results merely to obtain promotion.

---

## 26. Decision Eligibility Is Separate

Canonical knowledge is not automatically eligible for every Decision.

Decision eligibility depends on:

- supported applicability;
- freshness;
- current validity;
- uncertainty;
- relevant risk/Decision policy;
- supersession/retirement state.

Research establishes what evidence supports.

Decision Policy governs whether and how that knowledge may influence an action.

---

## 27. Promotion, Supersession, and Retirement Authority

The Research Director may propose lifecycle changes.

It must not silently grant itself final authority where governance requires independent approval.

Knowledge lifecycle actions must be explicit, versioned, and auditable.

New evidence may cause existing knowledge to be:

```text
UNCHANGED
NARROWED
REVALIDATION_REQUIRED
SUPERSEDED
RETIRED
```

Supersession or retirement does not erase historical identity or material lineage.

Detailed lifecycle thresholds shared across Research, Decision, and Learning may be further governed by `KNOWLEDGE_LIFECYCLE_POLICY.md`.

---

## 28. Human Intervention

Authorized humans may:

- initiate research;
- stop a campaign;
- provide context;
- approve capability acquisition;
- approve material resource expansion;
- approve lifecycle actions where required.

Human intervention must be recorded when it materially changes governed research state.

Human preference does not substitute for evidence and must not rewrite prior research history.

---

## 29. Autonomous Research

Autonomous research is permitted only within:

- an active governed Research Plan;
- explicit authority;
- finite resource limits;
- applicable data and method constraints;
- stopping criteria;
- audit/provenance requirements.

Autonomy means MTS may select evidence-dependent next questions without human prompting.

It does not mean unlimited scope, unlimited resources, self-authorized capability expansion, or self-modification of governance.

---

## 30. Research Restart and Recovery

Active campaign state required to resume research must be durable.

After restart, the Research Director must recover governed:

- campaign identity;
- active question;
- Research Plan/version;
- completed evidence dependencies;
- unresolved dependencies;
- iteration/resource state;
- current research outcome state.

Conversation memory, terminal history, filenames, directory order, or process memory must not be required to reconstruct research progression.

---

## 31. Research Ranking vs Scientific Status

Retrieval ranking, usage frequency, recency, and decision relevance may affect what knowledge or research MTS accesses first.

They do not change whether a proposition is scientifically supported.

Frequently used knowledge can be weak.

Rarely used knowledge can be strong.

Scientific status changes only through governed evidence and lifecycle evaluation.

---

## 32. Policy Review Triggers

This policy should be reviewed when evidence shows that its operational rules systematically:

- waste material research resources;
- terminate valuable inquiry prematurely;
- permit recurring low-value research loops;
- block useful generalizable knowledge;
- promote unstable knowledge;
- fail to protect holdouts or reproducibility;
- impair MTS Decision quality or long-term economic objective.

Learning & Governance may recommend revisions.

Recommendations do not become policy until authorized.

---

## 33. Required Auditability

For a material research conclusion, MTS must be able to reconstruct:

```text
question
→ Research Plan/version
→ tasks/executions
→ evidence
→ findings
→ evidence-dependent next questions
→ convergence/unresolved state
→ Knowledge Candidate
→ promotion evaluation
```

The system must also be able to identify the policy version governing the research.

---

## 34. Prohibited Practices

The following are prohibited:

- research continuation merely because another question can be imagined;
- fixed scripted question chains represented as adaptive inquiry;
- hidden look-ahead;
- post-hoc relabeling of exploratory evidence as independent confirmation;
- promotion based on narrative confidence or persuasive wording;
- promotion based on usage frequency;
- promotion based solely on statistical significance;
- promotion based solely on win rate;
- treating execution success as scientific validation;
- treating execution failure as negative evidence;
- treating insufficient evidence as task failure;
- deleting evidence merely because it contradicts a preferred conclusion;
- permanently retaining every contradictory or negative working artifact without governed justification;
- silently widening a claim beyond tested applicability;
- Research Director private worker scheduling;
- unbounded autonomous research;
- resetting resource counters merely to evade limits;
- canonical findings existing only in prose reports;
- Research Director manufacturing or bypassing the independent Accountability verdict required for its own plan/candidate;
- Accountability rewriting scientific conclusions, scheduling workers, or approving individual trades.

---

## 35. Conformance

Research conforms to this policy when it:

1. begins from a testable governed question;
2. uses a versioned Research Plan;
3. preserves exploratory/confirmatory distinction;
4. generates next questions from returned evidence;
5. preserves evidence lineage;
6. distinguishes execution failure from research result;
7. treats insufficient evidence and missing capability explicitly;
8. handles contradiction without fabricated certainty or infinite retention;
9. uses finite resource limits;
10. applies objective convergence criteria;
11. applies inspectable Knowledge Candidate and promotion gates;
12. protects holdout and look-ahead boundaries;
13. separates scientific status from ranking/usage;
14. preserves research/Decision separation;
15. remains auditable and restartable.

---

## 36. Companion Governance

This policy operates with:

```text
RESEARCH_STANDARD.md
ARTIFACT_GOVERNANCE_STANDARD.md
DATA_QUALITY_STANDARD.md
STORAGE_RETENTION_STANDARD.md
TASK_MANAGEMENT_STANDARD.md
SECURITY_AND_AUTHORITY_STANDARD.md
DECISION_STANDARD.md
LEARNING_GOVERNANCE_STANDARD.md
KNOWLEDGE_LIFECYCLE_POLICY.md
TASK_EXECUTION_POLICY.md
```

and applicable Contracts and Schemas.

---

## 37. Closing Rule

> **MTS admits research only when independent Accountability review establishes that the proposed work justifies governed resources; it continues research only while the expected value of learning justifies another governed iteration; and it promotes knowledge only when independent, inspectable evidence gates justify the lifecycle change.**
