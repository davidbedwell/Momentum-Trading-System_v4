# Momentum Trading System — Learning and Governance Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, and all applicable MTS governance standards, contracts, schemas, and policies.

---

## 1. Purpose

This standard defines how Momentum Trading System (MTS) learns from research, decisions, outcomes, and operational experience without corrupting historical truth or allowing uncontrolled self-modification.

It governs:

- Decision/outcome evaluation;
- performance attribution;
- knowledge re-evaluation;
- knowledge ranking inputs;
- instability and drift detection;
- research generation;
- policy/model recommendations;
- promotion and retirement recommendations;
- controlled adaptation;
- historical immutability;
- governance approval boundaries.

---

## 2. Governing Principle

> **MTS may learn from what happened, but it may not rewrite what it knew, decided, or observed before the outcome was known.**

Learning creates new governed state.

It does not edit history to make prior decisions appear better informed.

---

## 3. Role of Learning & Governance

Learning & Governance evaluates the performance of the system over time.

It may:

- compare Decisions with Outcomes;
- evaluate knowledge usefulness;
- identify instability;
- detect drift;
- identify systematic decision errors;
- identify missed opportunities;
- identify repeated `NO_ACTION` behavior;
- identify research gaps;
- recommend research;
- recommend knowledge lifecycle changes;
- recommend ranking changes;
- recommend model or policy changes;
- evaluate whether prior changes improved performance.

It does not unilaterally rewrite canonical historical artifacts.

---

## 4. Learning Is Not Research

Learning & Governance and Research Director have related but distinct responsibilities.

Learning & Governance asks:

> **What did MTS performance reveal about the system itself?**

Research Director asks:

> **What scientific question should be investigated next, and what evidence is needed?**

Learning may generate a governed Research Need.

Research Director determines the research process.

---

## 5. Learning Is Not Decision

Learning & Governance does not make the live investment decision merely because it evaluates prior outcomes.

It improves the knowledge, models, rankings, policies, or research agenda that future Decisions may use after governed promotion.

---

## 6. Historical Immutability

The following historical artifacts must not be rewritten because later outcomes became known:

- source observations;
- evidence;
- Findings;
- point-in-time SoK state;
- Decisions;
- execution records;
- Outcomes;
- policy snapshots;
- material configuration snapshots.

Corrections are represented through new versions, supersession, or correction records with lineage.

---

## 7. Decision–Outcome Pair

Learning begins with a governed relationship between a frozen Decision and its later Outcome.

Conceptually:

```text
Decision
   ↓
Execution, if applicable
   ↓
Outcome
   ↓
Evaluation
```

The evaluation must preserve the versions and timestamps of all relevant artifacts.

---

## 8. Outcome

An Outcome is an observation of what occurred after a Decision.

It may include:

- realized return;
- maximum favorable excursion;
- maximum adverse excursion;
- holding duration;
- target/stop behavior;
- slippage;
- transaction cost;
- fill quality;
- opportunity expiration;
- relevant counterfactual measures where governed.

Outcome is evidence.

It is not by itself proof that the Decision process was good or bad.

---

## 9. Outcome Horizon

Outcome evaluation must use a governed horizon appropriate to the original Decision.

MTS must not choose whichever later horizon makes the Decision look best.

Alternative horizons may be analyzed as separate governed evaluations.

---

## 10. Decision Quality vs Outcome Luck

A profitable outcome does not automatically prove a high-quality Decision.

A losing outcome does not automatically prove a poor Decision.

Evaluation should distinguish, where possible:

- decision-process quality;
- expected-value quality;
- risk discipline;
- implementation quality;
- stochastic outcome.

---

## 11. Evaluation Artifact

A material evaluation should be a governed artifact.

It should identify, as applicable:

```text
evaluation_id
decision_ref
outcome_ref
evaluation_policy_ref
metrics
attribution
knowledge_refs
model_refs
policy_refs
findings
recommendations
created_at
execution_ref
```

Exact schema belongs in Governance/Schemas.

---

## 12. Performance Dimensions

Evaluation may consider:

- realized return;
- expectancy;
- risk-adjusted return;
- drawdown;
- adverse excursion;
- favorable excursion;
- calibration;
- hit rate;
- payoff ratio;
- opportunity capture;
- false-positive cost;
- false-negative/missed-opportunity cost;
- `NO_ACTION` quality;
- execution quality;
- capital efficiency.

No single metric is assumed sufficient.

---

## 13. Win Rate

Win rate is descriptive, not the objective of MTS.

A strategy with lower win rate may be economically superior if payoff distribution is better.

Learning must not optimize win rate at the expense of expectancy or risk-adjusted economic value.

---

## 14. Attribution

Learning should attempt to identify which components materially influenced a Decision.

Potential attribution targets include:

- knowledge propositions;
- features;
- event classifications;
- current-state observations;
- model outputs;
- policy constraints;
- instrument choice;
- entry;
- scaling;
- exit;
- portfolio constraints.

Attribution must acknowledge uncertainty where causal contribution cannot be established.

---

## 15. Knowledge Usefulness

Knowledge usefulness may be evaluated from repeated Decision contexts.

Useful knowledge may:

- improve opportunity discrimination;
- improve expected return;
- reduce adverse excursion;
- improve timing;
- improve risk/reward;
- improve `NO_ACTION` decisions;
- improve instrument selection.

Usefulness is distinct from scientific validity.

---

## 16. Scientific Validity vs Decision Utility

A scientifically valid relationship may have little practical decision utility.

A frequently useful heuristic may still lack sufficient scientific validation.

Learning must preserve these as separate dimensions.

It must never promote scientific status merely because a proposition was profitable recently.

---

## 17. Knowledge Ranking

Learning & Governance may produce inputs to knowledge retrieval ranking.

Ranking may consider:

- applicability;
- decision utility;
- recency;
- replication strength;
- uncertainty;
- usage frequency;
- retrieval cost;
- stability.

Ranking affects retrieval priority.

It does not alter historical evidence.

---

## 18. Usage Frequency

Usage frequency may help optimize retrieval and identify important research areas.

It must not serve as evidence that a proposition is true.

Frequently used knowledge can be wrong.

Rarely used knowledge can be highly valid.

---

## 19. Instability

Learning should detect when previously useful relationships become unstable.

Possible indicators include:

- effect-size deterioration;
- sign reversal;
- increased variance;
- context dependence;
- calibration failure;
- worsening economic outcomes;
- repeated contradiction.

Instability should trigger governed evaluation rather than immediate silent deletion.

---

## 20. Drift

MTS should support detection of change in:

- market behavior;
- feature distributions;
- event frequencies;
- model performance;
- data-source behavior;
- Decision performance.

Drift may create:

- a Research Need;
- revalidation request;
- knowledge lifecycle recommendation;
- model review;
- policy review.

---

## 21. Regime Dependence

A relationship that fails globally may remain useful within a context.

Learning should test whether apparent deterioration reflects:

- genuine invalidation;
- regime change;
- scope mismatch;
- data quality;
- implementation change.

Knowledge should be narrowed when evidence supports conditional applicability rather than simply discarded.

---

## 22. Contradiction

New outcomes or research may contradict existing knowledge.

A material contradiction must be linked to the affected knowledge while it is unresolved. The contradiction itself is research state, not canonical knowledge. After resolution, bulky contradictory material should expire unless objective retention criteria require it; a compact durable resolution record should normally preserve the material consequence.

Possible responses include:

```text
RESEARCH_REQUIRED
REVALIDATE
NARROW_APPLICABILITY
REDUCE_DECISION_ELIGIBILITY
SUPERSEDE
RETIRE
NO_CHANGE
```

The response must be based on objective criteria.

---

## 23. Promotion Recommendation

Learning & Governance may recommend that a Knowledge Candidate be promoted.

Where current governance requires independent Accountability review, a
recommendation does not replace the Knowledge Promotion gate verdict. Learning
may evaluate whether Accountability's admission/promotion gates are themselves
producing stable, useful, resource-efficient outcomes and may recommend policy
changes.

Promotion requires the objective criteria defined by artifact/research governance.

Learning cannot bypass those gates because a recent trade was successful.

---

## 24. Retirement Recommendation

Learning & Governance may recommend retirement when governed criteria are met.

Possible reasons:

- failed replication;
- sustained instability;
- methodological defect;
- superseding evidence;
- persistent lack of decision utility where policy requires utility;
- obsolete applicability.

Retirement does not delete historical knowledge.

---

## 25. Supersession

When new knowledge replaces old knowledge, the relationship must be explicit.

The prior artifact remains resolvable so MTS can reconstruct Decisions made under the older SoK.

---

## 26. Policy Recommendations

Learning may recommend policy changes.

Examples:

- minimum liquidity;
- risk limits;
- position-sizing constraints;
- eligibility thresholds;
- research promotion criteria;
- retry/resource policies.

Recommendations do not become policy merely because an engine produced them.

---

## 27. Model Recommendations

Learning may recommend:

- retraining;
- recalibration;
- feature changes;
- model replacement;
- threshold changes;
- ensemble changes.

A model change must pass the applicable validation and promotion process before influencing governed Decisions.

---

## 28. No Uncontrolled Self-Modification

Production Decision behavior must not silently change because Learning edited:

- source code;
- model weights;
- thresholds;
- policy;
- schemas;
- configuration.

Adaptive behavior must occur through governed artifacts and explicit promotion mechanisms.

---

## 29. Adaptive Models

MTS may eventually support online or adaptive models.

Such models must still preserve:

- model identity/version/state;
- update event;
- data used for update;
- update time;
- prior model state;
- validation/policy;
- Decisions made under each state.

“Adaptive” is not an exemption from provenance.

---

## 30. Feedback Loop

The governed feedback loop is:

```text
Decision
   ↓
Outcome
   ↓
Learning & Governance
   ↓
Evaluation / Research Need / Recommendation
   ↓
Research and/or validation
   ↓
governed promotion
   ↓
future SoK / policy / model state
   ↓
future Decision
```

There is no direct ungoverned shortcut from one trade outcome to changed Decision logic.

---

## 31. Sample Size

Learning must not infer broad system changes from inadequate samples.

Required sample size/evidence depends on the claim.

One outcome may justify investigation.

It rarely justifies broad promotion or retirement by itself.

---

## 32. Recency

Recent performance may matter because markets change.

Recency must not erase longer-term evidence automatically.

Evaluation should distinguish:

- recent behavior;
- long-run behavior;
- context-specific behavior.

---

## 33. Multiple Comparisons

Learning across many features, strategies, thresholds, or Decision variants creates false-discovery risk.

Promising post-hoc patterns should generate research/validation rather than immediate policy changes.

---

## 34. Counterfactual Evaluation

Where methodologically valid, MTS may evaluate alternatives such as:

- what happened after `NO_ACTION`;
- alternative exit timing;
- alternative implementation;
- rejected candidate outcomes.

Counterfactual evaluation must be clearly labeled and must not rewrite the actual Decision.

---

## 35. `NO_ACTION` Learning

MTS must learn from decisions not to trade.

A `NO_ACTION` may be:

- correct avoidance;
- missed opportunity;
- appropriately uncertain;
- blocked by policy;
- blocked by missing capability/data.

Ignoring `NO_ACTION` outcomes would bias learning toward executed trades.

---

## 36. Missed Opportunities

Market Discovery candidates that were rejected may be evaluated when governed outcome data exists.

This helps distinguish:

- appropriate filtering;
- excessive conservatism;
- knowledge gaps;
- implementation constraints.

---

## 37. Selection Bias

Learning must account for the fact that executed trades are a selected subset of all evaluated opportunities.

Performance evaluation limited to executed trades can misrepresent Decision quality.

---

## 38. Execution Quality

Where a broker/execution layer exists, Learning should separate:

```text
Decision quality
from
execution quality
```

A good Decision with poor fill/slippage should not automatically be blamed on research knowledge.

---

## 39. Data Quality Effects

Performance deterioration may arise from data-quality changes.

Learning should check relevant quality artifacts before concluding that market relationships changed.

---

## 40. Provider Effects

Changes in provider definitions or coverage may mimic scientific drift.

Learning should preserve source/version context in evaluations.

---

## 41. Research Need Generation

Learning may create a Research Need when evaluation exposes a material unresolved question.

Examples:

- Why did a previously stable feature reverse?
- Why are short opportunities failing in a specific regime?
- Does options implementation improve this opportunity family?
- Is a Market Discovery pattern genuinely predictive?
- Is `NO_ACTION` rejecting economically valuable candidates?

Research Director receives the need and determines the research plan.

---

## 42. Priority Recommendation

Learning may recommend research priority based on expected system value.

Priority signals may include:

- frequency;
- economic impact;
- uncertainty;
- repeated failure;
- repeated missed opportunity;
- broad Decision dependence.

Task Manager remains responsible for scheduling.

---

## 43. Learning Campaign

Related evaluations may be grouped into a durable Learning Campaign.

Examples:

- monthly Decision performance;
- feature stability;
- market-regime drift;
- exit-policy performance;
- options implementation.

Campaign grouping must not hide individual evidence.

---

## 44. Periodic Evaluation

Some learning tasks may run periodically.

Examples:

- daily operational review;
- weekly performance aggregation;
- monthly knowledge stability review.

Cadence belongs in policy/configuration and may evolve without architecture changes.

---

## 45. Event-Triggered Evaluation

Learning may also be triggered by governed conditions such as:

- threshold performance deterioration;
- contradiction count;
- data-source change;
- model calibration failure;
- unusual loss cluster;
- repeated missing capability.

Triggers must be explicit.

---

## 46. Objective Thresholds

Promotion, retirement, revalidation, and escalation criteria must use objective thresholds or explicit rule sets.

Terms such as:

```text
trusted
good
bad
important
strong
```

are insufficient unless operationally defined.

---

## 47. Recommendation State

Recommendations should have governed states such as:

```text
PROPOSED
UNDER_REVIEW
APPROVED
REJECTED
IMPLEMENTED
SUPERSEDED
```

Exact vocabulary belongs in Governance/Schemas.

A proposal must not masquerade as implemented policy.

---

## 48. Human Governance

Certain classes of change may require human approval.

Initial v2 should require explicit approval for material changes to:

- Charter;
- architecture;
- governance standards;
- hard risk policy;
- Decision authority;
- production model promotion;
- destructive retention policy.

Future automation may be expanded only through explicit governance.

---

## 49. Machine-Approved Changes

Lower-risk changes may eventually be machine-approved if objective policy permits.

Examples could include:

- retrieval ranking updates;
- cache tuning;
- revalidation scheduling.

The approval class itself must be governed.

---

## 50. Audit Trail

Learning and governance actions must preserve:

```text
what was evaluated
what evidence was used
what recommendation was made
what rule/threshold applied
who/what approved it
when it became effective
what it superseded
```

---

## 51. Effective Time

A newly approved policy/model/knowledge state must have an effective time.

Decisions before that time remain associated with the prior state.

---

## 52. Rollback

Material promoted changes should support rollback where technically appropriate.

Rollback creates a new governed state transition.

It does not erase the failed change from history.

---

## 53. Change Evaluation

After a material change is promoted, MTS should evaluate whether it achieved its intended effect.

This creates a closed governance loop rather than assuming every approved change was beneficial.

---

## 54. Learning Data Retention

Decision, Outcome, Evaluation, and material recommendation artifacts are Class II durable state.

Retention must preserve enough history to evaluate long-term behavior and reconstruct governance decisions.

---

## 55. SoK Interaction

Learning may influence:

- retrieval ranking;
- decision eligibility recommendations;
- revalidation status;
- retirement/supersession recommendations.

The SoK remains a governed view assembled from canonical Nexus state.

Learning does not maintain a separate private truth store.

---

## 56. Research Nexus Interaction

All durable learning artifacts must be published through governed Research Nexus interfaces.

Private engine state may be used for temporary computation only.

---

## 57. Task Manager Interaction

Learning tasks and resulting research/revalidation requests use the common Task Manager.

Learning & Governance must not maintain a private scheduler.

---

## 58. Restart Continuity

Active learning campaigns, evaluations, recommendations, and approvals required for continuity must survive restart as Class II state.

---

## 59. Initial v2 Implementation

The first Learning & Governance implementation should support:

1. Decision–Outcome linkage;
2. Evaluation artifact;
3. basic economic/performance metrics;
4. `NO_ACTION` evaluation;
5. knowledge-use references;
6. instability signal;
7. Research Need generation;
8. knowledge revalidation recommendation;
9. ranking recommendation;
10. immutable history;
11. explicit approval state;
12. effective-time tracking.

Automatic production policy/model modification is not required initially.

---

## 60. Initial Proof

A valid proof should demonstrate:

```text
Decision A frozen
   ↓
Outcome A observed
   ↓
Evaluation A
   ↓
specific weakness/strength identified
   ↓
Research Need or recommendation
   ↓
governed research/validation
   ↓
approved new knowledge/model/policy state
   ↓
future Decision B uses new state
```

The record must still show exactly why Decision A was made under the old state.

---

## 61. Testing Requirements

Tests should include:

- winning Decision;
- losing Decision;
- good Decision/bad stochastic outcome;
- poor Decision/lucky outcome;
- `NO_ACTION` correct avoidance;
- `NO_ACTION` missed opportunity;
- instability detection;
- drift signal;
- contradiction escalation;
- insufficient sample;
- research need generation;
- recommendation approval/rejection;
- effective-time boundary;
- rollback;
- historical Decision immutability;
- restart/resume.

---

## 62. Prohibited Practices

The following are prohibited:

- rewriting prior Decisions after outcomes;
- deleting losing evidence;
- promoting knowledge because one trade won;
- retiring knowledge because one trade lost;
- equating usage frequency with scientific validity;
- silent source-code/model/policy self-modification;
- learning only from executed trades;
- ignoring `NO_ACTION`;
- conflating execution quality with Decision quality;
- treating recommendations as approved changes;
- changing historical effective dates;
- private Learning truth stores or schedulers.

---

## 63. Conformance

A Learning & Governance implementation conforms when it:

1. preserves historical immutability;
2. links Decisions to Outcomes explicitly;
3. evaluates multiple performance dimensions;
4. separates Decision quality from outcome luck and execution quality;
5. evaluates `NO_ACTION` and selection bias;
6. distinguishes scientific validity from utility/ranking;
7. detects instability/drift without silent deletion;
8. routes unanswered questions to Research;
9. uses objective promotion/retirement/escalation criteria;
10. prevents uncontrolled self-modification;
11. preserves recommendation/approval/effective-time history;
12. publishes durable state through the Research Nexus;
13. uses the common Task Manager;
14. supports rollback and post-change evaluation.

---

## 64. Companion Governance

This standard operates with:

```text
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/RESEARCH_STANDARD.md
Governance/Standards/DECISION_STANDARD.md
Governance/Standards/DATA_QUALITY_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/CONFIGURATION_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 65. Closing Principle

MTS must always be able to answer:

> **What did the system know when it acted, what happened afterward, what did we learn from the difference, and through what governed process did that learning change future behavior?**

If later knowledge can silently rewrite earlier truth, MTS cannot genuinely measure whether it is learning.
