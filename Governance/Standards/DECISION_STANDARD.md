# Momentum Trading System — Decision Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, and all applicable MTS governance standards, contracts, schemas, and policies.

---

## 1. Purpose

This standard defines how Momentum Trading System (MTS) converts governed knowledge and current state into an investment decision.

It governs:

- Decision Engine authority;
- decision requests;
- State of Knowledge consumption;
- current-market context;
- long/short direction;
- stock/options/other future implementation choice;
- entry;
- scaling;
- exit;
- risk/reward;
- uncertainty;
- `NO_ACTION`;
- research escalation;
- temporal integrity;
- decision provenance;
- separation of decisions from later outcomes.

The Decision Engine is where MTS answers:

> **Given what was knowable now, what should MTS do?**

---

## 2. Governing Principle

> **A decision is a time-bounded action judgment based only on information available at the decision time, under explicit policy and risk constraints.**

A decision must never be reconstructed later using information that was not then available.

---

## 3. Mission Alignment

MTS exists first to make money through disciplined use of historical and feature analysis, research, discovery, and governed decision-making.

The Decision Engine therefore optimizes neither:

- prediction accuracy alone;
- number of trades;
- research elegance;
- directional labels;
- confidence for its own sake.

Its purpose is to select actions expected to improve risk-adjusted economic outcomes under policy.

---

## 4. Decision and Research Boundary

Research establishes what evidence supports.

Decision applies relevant knowledge to current conditions.

Decision may determine:

```text
LONG
SHORT
NO_ACTION
RESEARCH_REQUIRED
```

or another governed result.

Decision must not fabricate missing scientific knowledge.

If a material knowledge gap prevents a valid decision, it may generate a governed research need/request through the Task Manager/Research Director path.

---

## 5. Decision Engine Authority

The Decision Engine may determine, within policy:

- whether an actionable opportunity exists;
- long or short direction;
- implementation/instrument type;
- entry intent;
- scaling intent;
- exit intent;
- time horizon;
- risk/reward acceptability;
- position intent;
- whether to take no action;
- whether additional research is required.

Trade execution/broker interaction, if later added, is a separate capability unless explicitly governed otherwise.

---

## 6. Inputs

A Decision Request should identify governed references to the information required for the decision.

Inputs may include:

```text
instrument
current market state
Market Discovery candidate/event
State of Knowledge
applicable findings/evidence
portfolio state
risk state
liquidity state
policy
configuration
open-position state
execution constraints
```

Inputs must be versioned or time-resolved sufficiently to reconstruct the decision.

---

## 7. Decision Time

Every Decision artifact must have a defined decision timestamp.

All inputs must satisfy availability-time constraints relative to that timestamp.

Future data is prohibited.

---

## 8. Point-in-Time Knowledge

The Decision Engine must consume the SoK as it existed or was valid at decision time.

Later knowledge promotion, contradiction, or retirement must not retroactively alter the historical Decision artifact.

---

## 9. State of Knowledge

The SoK supplied to Decision is a governed logical view of relevant knowledge.

It should include, as appropriate:

- applicable knowledge;
- scientific status;
- uncertainty;
- contradictions;
- applicability constraints;
- recency;
- decision eligibility;
- provenance references.

Decision should retrieve relevant knowledge rather than indiscriminately ingest the entire Nexus.

---

## 10. Current State

Decision must distinguish durable knowledge from current state.

Current state may include:

- price;
- volume;
- volatility;
- liquidity;
- event state;
- derivatives state;
- market/sector context;
- portfolio exposure;
- open position state.

Current state may be transient but must satisfy required quality/freshness criteria.

---

## 11. Freshness

Decision inputs that depend on current market conditions must declare freshness requirements.

A technically valid but stale observation may be invalid for Decision use.

If required state is stale, Decision must not pretend it is current.

---

## 12. Decision Result

A Decision result must be structured.

Illustrative semantic outcomes include:

```text
ENTER
SCALE_IN
SCALE_OUT
EXIT
HOLD
NO_ACTION
RESEARCH_REQUIRED
INSUFFICIENT_CURRENT_DATA
```

Exact vocabulary belongs in Governance/Schemas.

Direction and action are separate fields.

---

## 13. Direction

Direction should be explicit:

```text
LONG
SHORT
NONE
```

MTS does not require bull/bear classification as a prerequisite to action.

Direction is a property of the proposed trade.

---

## 14. Instrument / Implementation Choice

Decision may choose among implementation forms supported by current capability and policy.

Examples:

```text
STOCK
OPTION
future supported instrument
```

Instrument choice must consider the characteristics of the opportunity rather than being hard-coded by direction.

---

## 15. Options

If options are supported, Decision should consider factors such as:

- expiration;
- strike;
- liquidity;
- spread;
- implied volatility;
- Greeks/exposure;
- expected move;
- time horizon;
- assignment/exercise characteristics;
- implementation cost.

Options must not be chosen merely because leverage is available.

---

## 16. Entry

Entry logic should specify the condition or intent under which exposure is initiated.

It may include:

- immediate entry;
- limit/threshold;
- confirmation condition;
- staged entry;
- event-dependent entry;
- expiration of entry intent.

Entry rules must be reconstructable.

---

## 17. Scaling

Scaling decisions must be explicit.

A Decision artifact should distinguish:

```text
initial entry
add
reduce
exit
```

Scaling must consider existing exposure and portfolio/risk policy.

---

## 18. Exit

Exit logic may be based on:

- target;
- stop/risk limit;
- time;
- event invalidation;
- knowledge/context invalidation;
- trailing logic;
- portfolio constraint;
- updated Decision.

The reason for exit must be preserved.

---

## 19. Holding Horizon

A proposed action should identify an intended or bounded horizon where relevant.

Horizon may be expressed in:

- time;
- bars;
- event duration;
- governed category.

Horizon must be consistent with the research supporting the decision.

---

## 20. Risk / Reward

Decision should evaluate expected reward relative to risk.

Risk/reward is not one eternal threshold.

Acceptability may depend on:

- horizon;
- probability/uncertainty;
- volatility;
- liquidity;
- drawdown characteristics;
- implementation;
- portfolio state.

Thresholds belong in policy/research rather than hidden engine constants.

---

## 21. Return

Expected return should be represented separately from risk/reward.

Decision must not collapse:

- expected return;
- maximum favorable excursion;
- risk/reward;
- probability;
- confidence;

into one field.

---

## 22. Risk

Risk may include:

- expected adverse movement;
- stop distance;
- volatility;
- gap risk;
- liquidity risk;
- options-specific risk;
- portfolio concentration;
- correlation;
- event risk;
- model/knowledge uncertainty.

Risk policy defines which measures are mandatory.

---

## 23. Portfolio Context

Decision must eventually consider the portfolio, not merely an isolated ticker.

Relevant context may include:

- existing positions;
- gross/net exposure;
- sector concentration;
- correlated positions;
- cash/capital availability;
- risk budget;
- existing options exposure.

Initial POC implementations may use simplified portfolio state, but the interface must support the mature model.

---

## 24. Opportunity vs Decision

A detected opportunity is not automatically a trade.

Market Discovery may produce:

```text
candidate
pattern
event
opportunity observation
```

Decision determines whether the candidate merits action under knowledge, risk, portfolio, and policy.

---

## 25. `NO_ACTION`

`NO_ACTION` is a legitimate Decision result.

It may occur because:

- expected edge is insufficient;
- risk/reward is inadequate;
- evidence is conflicting;
- liquidity is inadequate;
- portfolio exposure is unsuitable;
- current data is stale;
- implementation is poor;
- opportunity has expired.

`NO_ACTION` is not task failure.

---

## 26. Research Required

If current conditions expose a knowledge gap material to the decision, Decision may return:

```text
RESEARCH_REQUIRED
```

and create/reference a governed research need.

Decision must not block indefinitely waiting for research if the opportunity will expire.

The original Decision Request retains its temporal context.

---

## 27. Missing Capability

If a valid decision cannot be implemented or evaluated because a required system capability is absent, the result must identify the missing capability explicitly.

Missing capability is not permission to substitute an unvalidated method.

---

## 28. Explanation

Every material Decision should contain a structured explanation sufficient to answer:

- what action was chosen;
- why;
- which knowledge mattered;
- which current observations mattered;
- what risks mattered;
- what alternatives were rejected;
- what uncertainty remained.

Explanation supplements structured references; it does not replace them.

---

## 29. Evidence Traceability

A Decision must reference the knowledge/evidence on which it materially relies.

This creates the lineage:

```text
data
→ evidence
→ finding
→ knowledge
→ SoK
→ decision
```

---

## 30. Policy Traceability

A Decision must identify the policy/configuration versions that materially constrained it.

This includes, where relevant:

- risk limits;
- portfolio limits;
- permitted instruments;
- minimum liquidity;
- required knowledge status;
- execution constraints.

---

## 31. Deterministic Rules vs Model Judgment

Decision may combine:

- deterministic policy rules;
- quantitative models;
- learned models;
- governed reasoning.

The source of each material constraint/judgment should remain distinguishable.

A model must not override a hard policy limit unless policy explicitly permits it.

---

## 32. Confidence

If Decision uses a confidence measure, it must have defined semantics.

“Confidence” must not become an uncalibrated substitute for evidence.

Where possible, use more specific concepts such as:

- probability;
- uncertainty interval;
- evidence strength;
- applicability;
- model calibration.

---

## 33. Objective Eligibility

Knowledge used for Decision must satisfy objective decision-eligibility criteria.

Frequency of use does not make knowledge eligible.

Popularity does not make evidence valid.

---

## 34. Contradictory Knowledge

Decision must not hide contradictory knowledge.

Applicable contradiction should affect:

- uncertainty;
- position intent;
- action eligibility;
- or `NO_ACTION`;

according to policy.

---

## 35. Applicability

Knowledge must be applied only within its supported scope unless the Decision explicitly records extrapolation and policy permits it.

A relationship learned on one instrument/context must not silently become universal.

---

## 36. Regime / Context

Decision may condition action on current context when research supports such conditioning.

Context may include:

- volatility regime;
- market trend/state;
- liquidity;
- sector behavior;
- event state;
- derivatives state.

Context is evidence, not a mandatory fixed taxonomy.

---

## 37. Long / Short Symmetry

The Decision architecture must support long and short opportunities symmetrically.

Policy may impose different constraints due to real-world implementation risk.

The schema and engine must not assume long is the default and short is an exception.

---

## 38. Multiple Candidate Actions

Decision may evaluate multiple feasible actions.

Example:

```text
long stock
long call
call spread
no action
```

or:

```text
short stock
put
put spread
no action
```

The selected action should be compared on governed economic/risk criteria.

---

## 39. Decision Expiration

A Decision may have an expiration time or invalidation condition.

A stale Decision must not remain actionable indefinitely.

---

## 40. Re-evaluation

New current-state information may trigger a new Decision.

The new Decision receives a new identity.

It may reference/supersede the prior Decision but must not overwrite it.

---

## 41. Decision Version / Supersession

A material change in action intent is represented by a new Decision artifact or governed version.

Historical Decision state remains immutable.

---

## 42. Execution Separation

Decision and trade execution are separate concepts.

Decision says what MTS intends to do.

A future Execution capability records what order was actually submitted/filled.

This distinction permits analysis of:

- decision quality;
- implementation quality;
- slippage;
- missed fills.

---

## 43. Outcome Separation

Outcome is recorded after the fact.

Outcome must never be written into the historical Decision as though it was known beforehand.

Conceptually:

```text
Decision
   ↓
Execution
   ↓
Outcome
   ↓
Learning & Governance
```

---

## 44. Outcome Evaluation

Outcome evaluation may include:

- realized return;
- maximum favorable excursion;
- maximum adverse excursion;
- holding duration;
- slippage;
- transaction cost;
- target/stop behavior;
- counterfactual metrics where governed.

Outcome does not retroactively change the Decision.

---

## 45. Learning Boundary

Learning & Governance may evaluate whether prior Decision logic performed well.

It may recommend:

- knowledge re-evaluation;
- ranking changes;
- policy changes;
- new research;
- model changes.

It must not silently rewrite prior Decision artifacts.

---

## 46. No Outcome Leakage

Decision development and historical simulation must prevent outcome information from leaking into the decision-time input set.

This applies to:

- feature construction;
- candidate selection;
- SoK retrieval;
- portfolio state;
- labels;
- thresholds learned from future data.

---

## 47. Historical Simulation

A historical Decision simulation must emulate:

```text
knowledge available then
+
data available then
+
policy/configuration then
=
decision then
```

Later outcomes are revealed only after the simulated decision is frozen.

---

## 48. Adaptation

MTS may adapt after outcomes are observed.

Adaptation occurs through governed Learning/Research processes.

The system must preserve which version of knowledge/model/policy produced each Decision.

---

## 49. Decision Metrics

Decision performance should be evaluated across multiple dimensions.

Examples:

- realized return;
- risk-adjusted return;
- win/loss;
- expectancy;
- drawdown;
- calibration;
- opportunity capture;
- false-positive cost;
- `NO_ACTION` quality;
- implementation efficiency.

Win rate alone is insufficient.

---

## 50. Scalability

Decision architecture must support evaluation of many candidates.

Scaling must not require loading the entire Research Nexus for every candidate.

SoK retrieval should be targeted and indexed.

---

## 51. Concurrency

Future Decision workers may evaluate independent candidates concurrently.

Decision identity, current-state snapshots, and portfolio coordination must prevent race conditions.

Portfolio-wide constraints may require coordinated reservation/serialization.

---

## 52. Resource Priority

Live Decision work may receive higher Task Manager priority than background research when freshness demands it.

Priority is an operational policy and must not alter scientific validity.

---

## 53. Failure Semantics

Examples:

```text
Decision task crashes → execution failure
required data stale → semantic result
no eligible trade → NO_ACTION
knowledge gap → RESEARCH_REQUIRED
broker unavailable → execution-layer issue, not Decision conclusion
```

These must remain distinct.

---

## 54. Decision Artifact

A governed Decision artifact should include, as applicable:

```text
decision_id
decision_request_ref
instrument_ref
decision_at
action
direction
implementation_type
entry_intent
scaling_intent
exit_intent
time_horizon
expected_return
risk/reward context
risk context
portfolio_state_ref
market_state_refs
SoK/knowledge_refs
evidence_refs
policy_refs
uncertainty
explanation
expiration/invalidation
execution_ref
```

Exact schema belongs in Governance/Schemas.

---

## 55. Persistence

Material Decision artifacts are Class II Permanent.

They must remain available for:

- outcome evaluation;
- learning;
- audit;
- historical reconstruction;
- scientific validation.

---

## 56. Initial v2 Implementation

The first Decision implementation should support:

1. governed Decision Request;
2. point-in-time SoK retrieval;
3. point-in-time current-state inputs;
4. `LONG`, `SHORT`, and `NONE`;
5. `ENTER` and `NO_ACTION`;
6. explicit horizon;
7. expected return;
8. risk/reward representation;
9. knowledge/evidence references;
10. explanation;
11. `RESEARCH_REQUIRED`;
12. immutable Decision artifact;
13. later Outcome linkage.

Stock may be the first implementation form while the interface remains capable of options/future instruments.

---

## 57. Initial Decision Proof

A valid proof should:

1. train/research using governed historical data;
2. freeze the resulting point-in-time knowledge;
3. present an unseen evaluation instrument/time without future data;
4. generate a Decision;
5. freeze that Decision;
6. reveal the future outcome afterward;
7. evaluate the Decision;
8. permit Learning/Research to adapt only after the outcome is revealed.

This tests whether MTS can use learned knowledge rather than merely describe historical patterns.

---

## 58. Testing Requirements

Decision tests should include:

- long opportunity;
- short opportunity;
- no action;
- stale current data;
- conflicting knowledge;
- insufficient applicable knowledge;
- research required;
- instrument choice;
- entry expiration;
- portfolio constraint;
- policy rejection;
- point-in-time SoK;
- no future leakage;
- decision supersession;
- outcome linkage;
- deterministic replay where expected.

---

## 59. Prohibited Practices

The following are prohibited:

- using future outcomes to construct a historical Decision;
- rewriting Decision artifacts after outcomes;
- treating every detected pattern as a trade;
- assuming long direction by default;
- hiding contradictory knowledge;
- using stale current data as current;
- inventing knowledge when research is insufficient;
- storing canonical Decision rationale only in prose;
- using win rate alone as the definition of success;
- conflating Decision with broker execution;
- allowing learned/model judgment to silently override hard policy.

---

## 60. Conformance

A Decision implementation conforms when it:

1. uses only point-in-time available information;
2. consumes governed SoK/current state;
3. separates research from action;
4. supports long, short, and no action;
5. records implementation, entry, scaling, exit, and horizon as applicable;
6. evaluates risk/reward and portfolio context;
7. preserves evidence and policy lineage;
8. treats `NO_ACTION` as legitimate;
9. escalates material knowledge gaps through governed research;
10. freezes Decision before outcome;
11. preserves Decision permanently;
12. separates Decision, execution, outcome, and learning;
13. supports future instruments and concurrent evaluation without redesign.

---

## 61. Companion Governance

This standard operates with:

```text
Governance/Standards/RESEARCH_STANDARD.md
Governance/Standards/DATA_QUALITY_STANDARD.md
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/LEARNING_GOVERNANCE_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md
Governance/Standards/CONFIGURATION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 62. Closing Principle

MTS must always be able to answer:

> **Given only what MTS actually knew at that moment, why did it choose this action—or choose not to act—and what evidence, uncertainty, risk, and policy produced that decision?**

If the explanation requires knowledge learned from what happened afterward, the Decision was not validly reconstructed.
