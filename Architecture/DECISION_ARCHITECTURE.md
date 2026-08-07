# Momentum Trading System — Decision Architecture

**Status:** Canonical
**Authority:** Governing decision architecture subordinate to `CHARTER.md`, `Architecture/SYSTEM_ARCHITECTURE.md`, `Architecture/RESEARCH_NEXUS_ARCHITECTURE.md`, `Architecture/ENGINE_ARCHITECTURE.md`, and `Architecture/DATA_ARCHITECTURE.md`

---

## 1. Purpose

This document defines the enduring architecture of MTS Decision Intelligence.

It governs:

- the boundary between research and decision-making;
- the inputs required for a decision;
- the role of current market state;
- use of the State of Knowledge (SoK);
- decision authority and constraints;
- uncertainty handling;
- risk and scalability;
- instrument selection;
- entry, management, and exit;
- decision provenance and explainability;
- research feedback when knowledge is insufficient;
- outcome capture and learning;
- human control and automation;
- extensibility to future execution and portfolio capabilities.

This architecture intentionally does not prescribe trading strategies, numerical thresholds, brokerage APIs, order-routing technology, or specific model implementations. Those belong in governed policy, contracts, and technical design.

---

## 2. Governing Principle

> **Research determines what MTS has evidence to believe. Decision Intelligence determines what MTS should do now.**

Research and decision-making are related but distinct.

The Decision Engine may consume knowledge, evidence, uncertainty, current market state, portfolio context, and policy.

Research Accountability gates do not approve individual investment Decisions. The Decision Engine may exercise trade authority already granted by applicable Decision, Risk, and Automation policy.

It may not silently create new scientific conclusions while deciding.

When the State of Knowledge is insufficient, the Decision Engine creates a governed Research Need.

---

## 3. Design With the End in Mind

Decision architecture SHALL be designed for the known mature system from the beginning.

The architecture must support:

- live-market operation;
- many simultaneous candidate opportunities;
- portfolio-level constraints;
- multiple instruments;
- long and short decisions;
- stocks and derivatives;
- position sizing;
- scalability;
- risk controls;
- trade management;
- exits;
- automated and human-approved workflows;
- future brokerage/execution integration;
- server-side concurrent decision workloads;
- continuous learning from outcomes.

An initial implementation may only evaluate one ticker and produce a non-executable decision record.

That is an implementation limit, not an architectural limit.

---

## 4. Decision Engine Role

The Decision Engine converts governed knowledge and current state into an actionable judgment.

Its responsibilities may include:

- determine whether action is warranted;
- choose long, short, or no position;
- choose instrument type;
- choose position size;
- assess scalability;
- evaluate expected reward and risk;
- identify invalidation conditions;
- define management rules;
- define exit conditions;
- determine whether execution should be blocked;
- identify when available knowledge is insufficient.

The Decision Engine does not own the Research Nexus, Task Manager, portfolio ledger, or execution infrastructure.

---

## 5. Research / Decision Boundary

The boundary is explicit.

### Research asks:

- What relationships exist?
- Under what conditions?
- How strong are they?
- How stable are they?
- What contradicts them?
- What remains unknown?

### Decision Intelligence asks:

- Does the current market state match an applicable knowledge context?
- Is the opportunity actionable now?
- What action best fits the available evidence, uncertainty, risk, and constraints?
- Is the opportunity scalable?
- What instrument and size are appropriate?
- What would invalidate the decision?
- What should cause exit or reassessment?

The Decision Engine may identify a missing knowledge dependency.

It must not resolve that dependency by inventing ungoverned research.

---

## 6. Decision Inputs

A governed decision may consume:

- current/live market state;
- applicable canonical or validated knowledge;
- supporting findings;
- uncertainty metadata;
- contradictory evidence;
- applicability conditions;
- market regime/context;
- instrument metadata;
- liquidity information;
- volatility information;
- options/institutional/fundamental information when available;
- portfolio state;
- existing exposure;
- capital constraints;
- risk policy;
- decision policy;
- execution constraints;
- freshness requirements;
- human override state.

All material inputs should be referenceable through governed identity.

---

## 7. State of Knowledge Use

The Decision Engine must query the SoK in a way that preserves:

- knowledge identity;
- lifecycle state;
- applicability;
- evidence strength;
- contradictions;
- uncertainty;
- recency;
- limitations;
- known gaps.

The Decision Engine must not flatten the SoK into a simple "true/false" lookup.

Multiple applicable knowledge objects may:

- reinforce;
- conflict;
- apply to different regimes;
- have different freshness;
- have different evidence quality;
- imply different actions.

The decision process must preserve those distinctions.

---

## 8. Current Market State

Current state is not knowledge.

It is the live or recent condition being evaluated against knowledge.

Current-state data may include:

- price;
- volume;
- volatility;
- liquidity;
- relative strength;
- options activity;
- institutional activity;
- sector context;
- broader market context;
- event state;
- portfolio exposure.

Freshness requirements must be explicit.

Stale current-state data must not silently be treated as current.

---

## 9. Decision Request

A decision begins with a governed Decision Request.

Illustrative metadata:

```text
decision_request_id
instrument_ref
requested_at
requested_by
market_state_ref
knowledge_scope
policy_refs
portfolio_context_ref
freshness_requirement
deadline
priority
```

The exact contract belongs in governance.

Decision Requests may originate from:

- Market Discovery Engine;
- human operator;
- scheduled portfolio review;
- another authorized component;
- future execution/portfolio systems.

---

## 10. Decision Output

A governed Decision artifact should be able to represent:

```text
NO_ACTION
ENTER_LONG
ENTER_SHORT
HOLD
SCALE_IN
SCALE_OUT
EXIT
REJECT
DEFER
RESEARCH_REQUIRED
```

The exact vocabulary is governed.

A Decision artifact should preserve, as applicable:

- decision identity;
- request identity;
- instrument;
- action;
- instrument type;
- direction;
- size;
- scalability;
- entry conditions;
- risk controls;
- management plan;
- exit conditions;
- confidence/uncertainty;
- applicable knowledge refs;
- contradictory knowledge refs;
- current-state refs;
- policy refs;
- engine/model version;
- reasoning references;
- timestamp;
- freshness horizon;
- Research Need if unresolved.

### 10.1 Trader Interface Projection Requirements

Decision outputs must expose sufficient structured information for a future
trader-facing graphical interface to render the highest-ranked active Decision
candidates without recreating Decision logic in the frontend.

The initial interface target is simultaneous presentation of the six
highest-ranked active candidates.

For each candidate, Decision output and associated current-state contracts must
make available, when applicable:

- instrument identity;
- candidate rank;
- current Decision state;
- current price/market timestamp;
- historical and live-forming candlestick state through the appropriate
  market-data interface;
- prospective entry level or zone;
- prospective scaling/add conditions;
- stop, invalidation, reduce, and exit conditions or levels;
- expected holding horizon;
- expected return/risk-reward information used by Decision;
- liquidity/scalability constraints;
- material applicable knowledge references;
- material current-state evidence;
- uncertainty and confidence representation;
- blocking conditions preventing entry or additional action;
- conditions capable of changing the current Decision state.

The interface may visualize this information but must not derive an alternate
Decision from it.

A trader-facing state such as `WATCH`, `ENTER`, `HOLD`, `ADD`, `REDUCE`,
`EXIT`, or `NO_ACTION` must resolve to governed Decision semantics rather than
frontend-specific interpretation.

Exact schema fields belong in Governance/Schemas and exact transport contracts
belong in Governance/Contracts.

---

## 11. No-Action Is a First-Class Decision

MTS must not be biased toward producing trades.

`NO_ACTION` is a valid and often desirable decision.

Reasons may include:

- insufficient expected value;
- excessive uncertainty;
- poor liquidity;
- unfavorable risk/reward;
- stale data;
- policy restriction;
- conflicting knowledge;
- insufficient scalability;
- portfolio constraint;
- insufficient evidence;
- missing capability.

Decision quality is more important than decision frequency.

---

## 12. Long / Short Symmetry

Decision architecture must support both long and short opportunities.

The system must not assume that upward movement is the default or primary opportunity class.

Direction is a decision output derived from evidence and current conditions.

---

## 13. Instrument Selection

The Decision Engine may choose among eligible instruments.

Examples:

- common stock;
- ETF;
- option;
- option spread;
- future supported instrument types.

Instrument selection must consider:

- liquidity;
- leverage;
- volatility;
- time horizon;
- expected move;
- transaction costs;
- slippage;
- execution feasibility;
- portfolio exposure;
- policy constraints.

Instrument selection is distinct from directional judgment.

---

## 14. Scalability

Scalability is a first-class decision property.

A theoretically profitable opportunity may be unsuitable at a given capital size.

Decision Intelligence should be able to consider:

- average dollar volume;
- bid/ask spread;
- market depth when available;
- options open interest;
- options volume;
- position size relative to market liquidity;
- expected slippage;
- capacity constraints.

Scalability should be recorded explicitly rather than assumed.

---

## 15. Risk Architecture

Risk is governed by policy, not improvised independently by the Decision Engine.

Risk considerations may include:

- maximum loss;
- risk/reward;
- portfolio concentration;
- sector concentration;
- correlation;
- volatility;
- gap risk;
- event risk;
- liquidity risk;
- options-specific risks;
- time decay;
- assignment/exercise risk;
- exposure duration.

The architecture does not prescribe specific thresholds.

---

## 16. Opportunity Horizon

MTS must support multiple opportunity horizons without requiring separate architectures.

Examples may include:

- very short-duration moves;
- multi-day moves;
- multi-week moves;
- longer-duration opportunities.

The Decision Engine should evaluate the opportunity using the horizon appropriate to the applicable knowledge and current state.

Horizon is metadata, not a hard-coded system identity.

---

## 17. Entry Architecture

An entry decision should identify, as applicable:

- trigger;
- timing condition;
- allowable price range;
- invalidation;
- expected horizon;
- expected reward;
- expected risk;
- liquidity requirements;
- size constraints;
- execution constraints.

The exact mechanics belong in decision policy and strategy-specific contracts.

---

## 18. Trade Management Architecture

A decision may include a management plan.

Examples:

- hold while conditions remain valid;
- scale in;
- scale out;
- adjust risk;
- tighten invalidation;
- respond to new evidence;
- time-based reassessment;
- event-based reassessment.

Management behavior must remain governed and explainable.

---

## 19. Exit Architecture

Exit is a decision function, not an afterthought.

Exit may be triggered by:

- target achieved;
- invalidation;
- risk limit;
- evidence deterioration;
- contradiction;
- time expiration;
- volatility/liquidity change;
- portfolio constraint;
- new market event;
- superior opportunity;
- policy requirement.

Exit decisions should be recorded with provenance just like entries.

---

## 20. Uncertainty

Uncertainty must be preserved explicitly.

The Decision Engine must distinguish:

- strong evidence;
- weak evidence;
- contradictory evidence;
- missing evidence;
- stale evidence;
- regime mismatch;
- insufficient sample;
- unknown applicability.

The system must not turn uncertainty into false confidence.

---

## 21. Research Need Feedback

When Decision Intelligence cannot make a defensible judgment because knowledge is missing, it should publish a governed Research Need.

Conceptually:

```text
Decision Engine
      ↓
"Current SoK is insufficient because X"
      ↓
Research Need
      ↓
Research Nexus
      ↓
Task Manager
      ↓
Research Director
      ↓
Research Plan
```

The Research Need should identify:

- what is unknown;
- why it matters to the decision;
- required freshness;
- relevant instrument/context;
- existing knowledge consulted;
- decision deadline if applicable.

---

## 22. Market Discovery / Decision Boundary

Market Discovery answers:

> **Where is something happening?**

Decision Intelligence answers:

> **What should MTS do about it?**

A Market Discovery candidate does not become a trade merely because it was detected.

It becomes a Decision Request.

This separation permits:

- broad scanning;
- high candidate volume;
- independent decision standards;
- future replacement or scaling of either component.

---

## 23. Task Manager Interaction

Decision work is scheduled and supervised by the Task Manager.

The Task Manager may:

- prioritize live decisions;
- enforce freshness deadlines;
- route to eligible Decision workers;
- retry safe failures;
- cancel stale work;
- track execution.

The Task Manager does not decide the trade.

---

## 24. Research Nexus Interaction

The Research Nexus preserves:

- Decision Requests;
- material current-state references;
- Decision artifacts;
- knowledge refs;
- policy refs;
- reasoning/provenance refs;
- Research Needs;
- outcomes;
- later evaluations.

Decision artifacts must be discoverable by:

- instrument;
- date/time;
- action;
- knowledge used;
- policy;
- outcome;
- engine version;
- campaign/context.

---

## 25. Explainability

Every material decision must be explainable after the fact.

Explainability should answer:

- What did MTS decide?
- What current conditions mattered?
- What knowledge applied?
- What contradicted the decision?
- What risk constraints applied?
- What policy governed the decision?
- Why was this instrument chosen?
- Why this size?
- What would invalidate the decision?
- Why was no action taken, if applicable?

Explainability is not merely a generated narrative.

It must be grounded in durable references.

---

## 26. Reproducibility

MTS should be able to reconstruct a historical decision using:

- exact market-state refs;
- exact knowledge refs;
- policy refs;
- engine/model version;
- portfolio context;
- parameters;
- timing;
- decision logic/version.

Perfect replay may not always be possible for live external systems.

The architecture must preserve enough information to reproduce the decision process to the degree technically feasible.

---

## 27. Outcome Architecture

A Decision is not evaluated only at entry.

Outcomes must capture what happened after the decision.

Potential outcome data includes:

- realized return;
- maximum favorable excursion;
- maximum adverse excursion;
- holding period;
- slippage;
- transaction costs;
- execution quality;
- exit reason;
- missed-opportunity data for `NO_ACTION` where useful;
- comparison with expected horizon/reward/risk.

Outcome definitions belong in governance.

---

## 28. Learning Loop

Decision outcomes feed Learning & Governance.

Conceptually:

```text
Decision
   ↓
Outcome
   ↓
Learning & Governance
   ↓
Knowledge / Policy Evaluation
   ↓
Research Nexus
```

Learning & Governance may identify:

- knowledge performing as expected;
- knowledge decay;
- calibration error;
- decision-policy weakness;
- regime limitation;
- contradiction;
- overconfidence;
- missed opportunity.

This may produce:

- lifecycle review;
- Research Need;
- policy-review request;
- knowledge degradation/supersession proposal.

---

## 29. Knowledge vs Decision Performance

Poor trade outcome does not automatically invalidate knowledge.

Good trade outcome does not automatically validate knowledge.

Evaluation must distinguish:

- knowledge quality;
- decision quality;
- execution quality;
- randomness;
- policy quality;
- market regime;
- portfolio constraints.

The outcome architecture must preserve enough detail to make those distinctions.

---

## 30. Human Authority

Human control must remain explicit.

Governed policy must define which actions require human approval.

Potential stages include:

```text
research-only
decision recommendation
paper-trade authorization
human-approved live execution
bounded autonomous execution
```

Progression between stages is governed.

The architecture supports increasing automation without requiring a redesign.

---


### 30.1 Pre-Live Validation Progression

The canonical development progression toward real-money execution is:

```text
broad-universe / representative Decision evaluation
        ↓
successful + failed outcomes evaluated
        ↓
governed Learning / validation
        ↓
Live Paper Validation
$10,000 finite simulated portfolio
live market conditions
        ↓
objective qualification result
        ↓
PASS → eligible for live-authorization review
        ↓
separately granted live authority
        ↓
real-money execution
```

Live Paper Validation is an integrated prospective Decision/execution test, not
an additional research gate and not a per-trade Accountability approval.

The Decision Engine must operate against the current finite paper-account state,
including capital already committed to open positions, reserved capital,
realized gains/losses, concentration, and buying power.

Paper-trading success does not automatically authorize live execution.

## 31. Execution Boundary

Execution is distinct from Decision Intelligence.

The Decision Engine decides what action is appropriate.

A future Execution capability handles:

- broker interaction;
- order construction;
- submission;
- order state;
- fills;
- cancellations;
- execution errors.

This separation prevents brokerage mechanics from becoming decision logic.

A future Execution Engine may be added without redesigning the Decision Engine.

---

## 32. Portfolio / Risk Boundary

Portfolio-level risk may eventually justify a dedicated Portfolio/Risk Engine.

Decision architecture must therefore avoid embedding global portfolio authority deeply into a single-instrument decision implementation.

The Decision Engine may consume portfolio/risk constraints through governed interfaces.

A future Portfolio/Risk Engine may provide:

- capital availability;
- exposure limits;
- concentration constraints;
- correlation risk;
- portfolio-level sizing limits.

---

## 33. Live Decision Concurrency

The mature system may evaluate many opportunities concurrently.

Decision workers must therefore avoid:

- global mutable state;
- implicit single-position assumptions;
- unscoped temporary files;
- non-atomic writes.

The Task Manager coordinates concurrency.

The Research Nexus preserves durable decision state.

---

## 34. Freshness and Expiration

Decision work may expire.

A Decision Request should be able to define:

- maximum acceptable data age;
- maximum acceptable knowledge age where policy requires;
- deadline;
- expiration condition.

The Task Manager may cancel stale work.

A Decision artifact should indicate if it was created from data approaching a freshness limit.

---

## 35. Failure Semantics

Decision work must fail explicitly.

MTS distinguishes **task-execution state** from **semantic Decision
result**.

A Decision task may execute successfully while producing a semantic
result such as:

```text
NO_ACTION
ENTER_LONG
ENTER_SHORT
HOLD
SCALE_IN
SCALE_OUT
EXIT
REJECT
DEFER
RESEARCH_REQUIRED
```

Task-execution states may include:

```text
SUCCEEDED
STALE_INPUT
POLICY_BLOCKED
MISSING_CAPABILITY
FAILED_RETRYABLE
FAILED_TERMINAL
CANCELLED
TIMED_OUT
```

A failed decision task must not silently become `NO_ACTION`, and a
`NO_ACTION` decision must not be reported as an execution failure.

Exact controlled vocabularies belong in governance.

---

## 36. Decision Policy

Decision behavior is governed by explicit policy.

Potential policies include:

- capital allocation;
- maximum risk;
- instrument eligibility;
- liquidity minimums;
- portfolio concentration;
- option-selection constraints;
- live execution permission;
- human approval requirements;
- freshness requirements.

Policies are authored in Governance.

Operational policy versions used in material decisions are preserved in the Research Nexus.

---

## 37. Initial v2 Decision Proof

The initial Decision proof should be intentionally narrow but architecturally complete.

Recommended flow:

```text
Historical/current AAPL state
        ↓
Applicable SoK
        ↓
Decision Request
        ↓
Task Manager
        ↓
Decision Engine
        ↓
Decision artifact
        ↓
Research Nexus
```

The first proof may produce only:

```text
ENTER_LONG
ENTER_SHORT
NO_ACTION
RESEARCH_REQUIRED
```

with no live broker execution.

It should nevertheless demonstrate:

- governed input refs;
- explicit knowledge refs;
- current-state refs;
- policy refs;
- provenance;
- explainability;
- uncertainty;
- Research Need creation;
- durable Decision publication.

---

## 38. Conformance Requirements

A Decision implementation conforms when it:

1. keeps research and decision authority distinct;
2. consumes governed SoK/current-state inputs;
3. preserves uncertainty and contradiction;
4. supports `NO_ACTION`;
5. supports long and short;
6. supports extensible instrument selection;
7. treats scalability as explicit;
8. applies governed risk/decision policy;
9. records entry/management/exit logic where applicable;
10. creates Research Needs instead of silently inventing research;
11. uses the Task Manager for scheduled execution;
12. publishes durable Decision artifacts to the Research Nexus;
13. preserves explainability and provenance;
14. supports outcome linkage;
15. supports future execution and portfolio components without redesign;
16. remains compatible with concurrent server-scale operation.

---

## 39. Companion Governance

This architecture should be supported by canonical unversioned documents such as:

```text
Governance/Standards/DECISION_STANDARD.md
Governance/Standards/EXPLAINABILITY_STANDARD.md
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md

Governance/Contracts/DECISION_REQUEST_CONTRACT.md
Governance/Contracts/DECISION_RESULT_CONTRACT.md
Governance/Contracts/RESEARCH_NEED_CONTRACT.md
Governance/Contracts/OUTCOME_CONTRACT.md

Governance/Policies/DECISION_POLICY.md
Governance/Policies/RISK_POLICY.md
Governance/Policies/AUTOMATION_AUTHORITY_POLICY.md

Governance/Schemas/
```

---

## 40. Closing Principle

Decision Intelligence exists to convert evidence-supported knowledge into disciplined action without pretending uncertainty does not exist.

> **Research determines what MTS has evidence to believe. Decision Intelligence determines what MTS should do. Outcomes determine what MTS needs to learn next.**
