# Momentum Trading System — Implementation Roadmap

**Status:** Project Roadmap  
**Location:** Repository root  
**Authority:** This roadmap does not override `CHARTER.md`, canonical Architecture, Governance Standards, Policies, Contracts, or Schemas. It defines the preferred implementation sequence for building MTS from the governed architecture toward the finished operating system.

---

## 1. Purpose

MTS must be built with the finished system in mind.

The goal is not to create a collection of independent engines. The goal is to create one continuously operating system in which:

```text
market/data observations
→ governed evidence
→ governed research
→ knowledge
→ current opportunity recognition
→ Decisions
→ execution
→ outcomes
→ learning
→ improved knowledge and future Decisions
```

Every implementation milestone should therefore be chosen because a later system capability demonstrably depends on it.

The development method is:

> **End state → dependency → smallest complete implementation → real vertical test → harden → next dependency.**

MTS should not build infrastructure merely because the architecture mentions it. Each layer should first be implemented to the minimum depth necessary to support a real downstream consumer, then expanded through tested vertical slices.

---

## 2. End-State Design Principle

The completed MTS is expected to contain, at minimum:

- governed data intake;
- Research Nexus;
- shared Core services;
- Task Manager;
- engine runtime and interface substrate;
- Analysis;
- Accountability;
- Research Director;
- Learning & Governance;
- Market Discovery;
- Decision;
- portfolio and risk state;
- execution capability;
- Live Paper Validation;
- trader-facing graphical interface;
- separately governed real-money execution capability.

These components do not share the same authority.

The finished system must preserve the canonical separation that:

- engines perform bounded work;
- Task Manager schedules, routes, and supervises work;
- Research Nexus preserves durable governed state;
- Research Director proposes and iterates research;
- Accountability controls required Research Admission and Knowledge Promotion gates;
- Learning & Governance evaluates outcomes and recommends governed changes;
- Decision determines investment intent within granted authority;
- Execution implements authorized Decisions within explicit bounds;
- trader-facing interfaces project canonical state rather than creating parallel trading logic;
- real-money authority is separately granted and never inferred from paper success.

---

## 3. Construction Rule

Each phase must satisfy four conditions before the next dependent phase becomes the primary development target:

1. **Contract exists** — interfaces, identities, schemas, authority boundaries, and lifecycle rules are defined sufficiently for implementation.
2. **Implementation exists** — the smallest useful operational capability is present.
3. **Vertical test exists** — the capability has been exercised by a real upstream/downstream interaction rather than only isolated unit tests.
4. **Regression protection exists** — the behavior that was proved is protected by automated tests or an equivalent governed verification mechanism.

A phase does not need every mature feature before development can proceed.

MTS should prefer an incomplete but vertically integrated system over a collection of independently sophisticated components that do not operate together.

---

# Phase 0 — Governance Freeze for Implementation

## 4. Final Cross-Policy Conformance

Before beginning major implementation, complete the current Architecture / Standards / Policies harmonization cycle.

Required work:

- rerun the cross-policy conformance audit after dynamic-concurrency harmonization;
- repair only genuine authority, lifecycle, terminology, or contract conflicts;
- verify prohibited historical terminology remains absent;
- verify repository status is clean;
- commit and push the final harmonization milestone.

After this point, Architecture, Standards, and Policies become the implementation contract.

They may still change when implementation or empirical evidence reveals a real defect, but they should not be casually redesigned during coding.

### Exit condition

```text
cross-policy conformance acceptable
git diff --check clean
working tree clean
canonical authority boundaries coherent
```

---

# Phase 1 — Research Nexus

## 5. Build the Research Nexus First

The Research Nexus is the central durable state and knowledge substrate of MTS.

It should be the first major operational component because nearly every later element depends on:

- durable identity;
- artifact publication;
- immutable versions;
- provenance;
- relationships and lineage;
- lifecycle state;
- promotion state;
- current scientific status;
- Decision eligibility;
- retention classification;
- point-in-time retrieval;
- State of Knowledge assembly;
- active research state;
- historical research lineage;
- active utility / retrieval treatment;
- auditability;
- policy/schema/version preservation;
- restart and recovery.

The first Nexus implementation must remain physically replaceable. Engines and clients must not depend on its filesystem layout or storage backend.

## 6. Minimum Nexus Vertical Slice

The first implementation should support:

```text
publish artifact
get artifact by identity/version
query artifacts by governed criteria
record relationships
record provenance
record lifecycle state
record policy/schema/software version metadata
record retention class
record Decision eligibility
record current scientific status
assemble scoped point-in-time State of Knowledge
distinguish canonical / active research / historical lineage / cache state
```

It should also provide the minimum active-utility metadata required by current governance, even if sophisticated ranking is deferred.

Examples include:

```text
last_relevant_access
decision_use_count
eligible_opportunities_since_use
retrieval_tier
utility_review_status
```

### Do not build yet

Do not begin with:

- distributed databases;
- elaborate ranking models;
- vector infrastructure merely because it may later be useful;
- large-scale caching systems;
- complex event buses;
- speculative performance optimizations.

First prove the canonical semantics.

---

# Phase 2 — Minimum Core Under the Nexus

## 7. Core Is Built as a Dependency, Not as a Separate Product

Core should grow underneath the Nexus as required.

The first Core implementation should include only shared mechanisms with an immediate consumer.

Likely initial Core capabilities:

- canonical identity generation/resolution;
- artifact/version identity;
- schema identity/version handling;
- schema validation;
- timestamps and effective-time primitives;
- point-in-time semantics;
- configuration resolution;
- content hashing / immutable identity support;
- result/error envelopes;
- audit-event primitives;
- provenance primitives;
- storage abstraction;
- clock abstraction where deterministic testing requires it.

Core must not become a monolithic framework containing business logic owned by engines or governance components.

---

# Phase 3 — Nexus Hardening

## 8. Prove the Nexus Before Allowing High-Volume Producers

Before engines begin generating significant research state, prove:

- immutable publication;
- idempotent resubmission;
- identity/version resolution;
- relationship traversal;
- upstream/downstream lineage;
- point-in-time retrieval;
- scoped SoK assembly;
- supersession;
- retirement without erasure;
- contradiction linkage;
- active vs historical vs transient separation;
- HOT / NORMAL / COLD retrieval semantics if implemented;
- `COLD != ARCHIVED`;
- cache retirement;
- policy/version reconstruction;
- restart/recovery;
- backend independence.

### Exit condition

A material artifact must remain understandable without knowing:

- the producer's local filesystem;
- a developer's terminal history;
- a process's memory;
- an engine's private storage conventions.

---

# Phase 4 — Task Manager

## 9. Build Task Manager Against Durable Nexus State

Task Manager should be implemented after the Nexus can durably represent the task state required for recovery and audit.

Task Manager owns execution coordination, including:

- task creation/acceptance;
- readiness;
- dependencies;
- priority;
- routing;
- worker eligibility;
- worker assignment;
- leases/ownership;
- retries;
- cancellation;
- stale-work handling;
- failure classification;
- resource discovery;
- safe and efficient concurrency;
- restart/recovery.

Workers are execution instances dynamically allocated as needed.

Task Manager must determine safe and efficient concurrency according to runtime resource capacity, task characteristics, dependencies, exclusivity, safety constraints, and configured ceilings/reservations/overrides where present.

A CPU core is a resource, not a worker identity.

A constrained machine may result in effective concurrency of one. That is a runtime result, not a fixed architecture.

---

# Phase 5 — Engine Runtime and Interface Substrate

## 10. Make Engines Plug Into the System

Before building sophisticated engine behavior, implement the shared engine execution substrate.

Required capabilities should include:

- canonical engine identity;
- worker identity;
- capability registration;
- supported contract versions;
- supported schema versions;
- health/heartbeat state;
- task request contract;
- task result contract;
- execution provenance;
- bounded engine authority;
- publication through governed Nexus interfaces;
- Task Manager routing;
- failure semantics.

An engine should be a bounded capability.

It must not own:

- enterprise durable state;
- private canonical queues;
- a competing artifact authority;
- a competing Task Manager;
- a competing Nexus.

---

# Phase 6 — Data Intake

## 11. First Real Engine

Data Intake should be the first production-quality engine because all later scientific work depends on valid inputs.

Initial vertical slice:

```text
external/source data
→ Data Intake
→ data-quality validation
→ canonical data/observation artifact
→ Research Nexus
```

Prove:

- source identity;
- acquisition metadata;
- point-in-time availability;
- timestamps/timezones;
- symbol/instrument identity;
- schema validation;
- data-quality status;
- immutable publication;
- duplicate handling;
- lineage;
- restart behavior.

Do not ask downstream research to compensate for ambiguous source data.

---

# Phase 7 — Analysis

## 12. Convert Governed Data Into Evidence-Producing Analysis

Analysis should consume Nexus-resolved inputs through governed tasks and publish measurable findings.

Initial capabilities may include:

- feature computation;
- price/volume relationships;
- volatility measurements;
- liquidity measurements;
- return/path behavior;
- event/phenomenon detection;
- pattern candidates;
- cross-sectional relationships;
- temporal relationships;
- statistical summaries;
- evidence findings.

This phase proves the first important reusable engine pattern:

```text
Task Manager
→ eligible worker
→ Nexus inputs
→ bounded computation
→ governed artifact
→ Nexus publication
```

No private storage handoff should be required.

---

# Phase 8 — Accountability

## 13. Implement Independent Gates Before Autonomous Research

Accountability should be operational before Research Director is allowed to generate autonomous research at scale.

Initial Accountability should be intentionally simple and objective.

### Gate 1 — Research Admission

Input:

```text
Proposed Research Plan
```

Output:

```text
admit
admit with scope/conditions
return for revision
reject/block
insufficient evidence/capability
```

### Gate 2 — Knowledge Promotion

Input:

```text
Knowledge Candidate
evidence package
validation state
scope
uncertainty
promotion criteria/version
```

Output:

```text
promotion passed
promotion passed with scope
promotion blocked
additional evidence required
```

Accountability must publish inspectable verdict artifacts.

It does not:

- author the scientific conclusion;
- schedule workers;
- own canonical knowledge;
- approve individual trades.

---

# Phase 9 — Research Director

## 14. Build the Iterative Research Intelligence Layer

Only after Nexus, Task Manager, Data Intake, Analysis, and Accountability exist should Research Director become autonomous.

Required loop:

```text
question / gap
→ query SoK + Active Research State
→ Proposed Research Plan
→ Accountability Research Admission
→ Task Manager
→ Data Intake / Analysis
→ Evidence / Findings
→ Research Director evaluation
→ follow-up question OR convergence
→ Knowledge Candidate
→ Accountability Knowledge Promotion
→ governed lifecycle transition
→ Research Nexus / SoK
```

Research Director must support genuine iteration rather than a scripted list of questions.

Valid outcomes include:

- supported finding;
- contradiction;
- narrowed scope;
- unresolved question;
- insufficient evidence;
- insufficient tools;
- convergence without positive finding;
- new Research Plan.

Research Director may author candidates but cannot certify its own promotion.

---

# Phase 10 — Learning & Knowledge Lifecycle Operationalization

## 15. Activate the Outcome and Utility Loop

Once MTS has actual usage and outcomes, operationalize the governed knowledge lifecycle.

Capabilities should include:

- current scientific status;
- Decision eligibility;
- active utility;
- relevant access;
- applicable-opportunity exposure;
- utility ranking;
- HOT / NORMAL / COLD retrieval treatment;
- contradiction investigation;
- scope narrowing;
- revalidation;
- degradation;
- supersession;
- retirement;
- invalidation;
- redundancy review;
- archival;
- cache expiration;
- historical lineage preservation.

Do not create opaque utility models before sufficient real usage data exists.

Begin with objective, inspectable rules.

A knowledge artifact may remain scientifically valid while being demoted from ordinary retrieval because it demonstrates little operational utility.

Rare-condition knowledge must remain target-retrievable when its applicable context returns.

---

# Phase 11 — First Complete Historical Scientific Loop

## 16. Prove MTS Can Learn

Before building a live opportunity scanner or relying on Decision, prove one complete scientific loop over real historical data.

Use a representative sample of instruments and include:

- successful relationships;
- failed relationships;
- contradictions;
- null findings;
- insufficient evidence;
- scope restrictions.

Required proof:

```text
Data Intake
→ Nexus
→ Task Manager
→ Analysis
→ Nexus
→ Research Director
→ Accountability
→ Task Manager
→ additional analysis
→ Knowledge Candidate
→ Accountability
→ promoted/scoped/rejected knowledge state
→ SoK
→ later revalidation/learning
```

This is the first major proof that MTS is capable of governed learning rather than merely executing scripts.

### Deterministic Measurement Convergence Campaign

As part of the first historical scientific loop, MTS shall run the governed Deterministic Measurement Convergence Campaign.

The campaign uses repeated five-ticker cohorts to evaluate and rerank the shared deterministic measurement universe. Research Director performs a Measurement Convergence Assessment after each cohort and continues the campaign until sufficient convergence is established by stable successive rankings/classifications and the absence of important recurring analytical tool-coverage deficiencies.

The campaign does not impose a fixed ticker-count endpoint and does not remove lower-ranked measurements from the shared governed computation library.

Canonical campaign procedure:

`Documentation/Campaigns/DETERMINISTIC_MEASUREMENT_CONVERGENCE_CAMPAIGN.md`

---

# Phase 12 — Market Discovery

## 17. Add Continuous Current-Market Observation

Market Discovery should be built after the historical knowledge machinery works.

Its job is to search current/live market state for:

- known patterns;
- known conditions;
- new anomalies;
- emerging phenomena;
- candidate opportunities;
- research-worthy observations.

Market Discovery publishes candidates/phenomena to the Nexus.

It may route them toward:

- Decision, when sufficient current knowledge already exists;
- Research Director, when the observation requires research;
- both, when policy permits parallel handling.

Market Discovery does not decide trades.

---

# Phase 13 — Decision Engine

## 18. Convert Knowledge and Current State Into Investment Intent

Decision should be built after it has a mature SoK and current-market candidate stream to consume.

Decision must evaluate, as applicable:

- current market state;
- scoped SoK;
- knowledge applicability;
- uncertainty;
- portfolio state;
- risk constraints;
- instrument selection;
- long vs short;
- stock vs derivative instrument;
- entry;
- watch/no-action;
- hold;
- scaling;
- exit;
- horizon;
- expected economic value.

Decision must be able to publish a Research Need when the SoK is insufficient.

Decision does not own:

- the Nexus;
- Task Manager;
- research gates;
- broker execution;
- portfolio ledger.

---

# Phase 14 — Portfolio and Risk State

## 19. Build Finite Capital State Before Execution

Execution cannot be scientifically or economically realistic without portfolio state.

Implement a canonical portfolio ledger capable of representing:

- cash;
- available buying power;
- committed capital;
- positions;
- cost basis;
- realized P/L;
- unrealized P/L;
- pending orders;
- concentration;
- instrument exposure;
- directional exposure;
- portfolio-level risk;
- relevant limits;
- reserved capital.

Decision must consume the actual current portfolio state rather than evaluating every opportunity as though full capital remains unused.

---

# Phase 15 — Paper Execution Capability

## 20. Execution Implements, It Does Not Decide

Build Execution initially with PAPER destinations only.

Required capabilities:

- authorized Decision intake;
- execution-bound validation;
- order intent;
- bounded execution discretion;
- submission;
- acknowledgement;
- partial fills;
- fills;
- rejection;
- cancellation;
- replacement;
- reconciliation;
- idempotency;
- retry safety;
- portfolio-ledger update;
- execution audit.

The system must distinguish:

```text
Decision
order submitted
order acknowledged
partial fill
fill
position
```

Paper execution must never be routable to a live destination by default or fallback.

---

# Phase 16 — Broad Historical Decision Evaluation

## 21. Test Decision Before Prospective Paper Trading

Before the final live-market paper campaign, evaluate Decision behavior across a broad universe or sufficiently large representative sample of historical opportunities.

Strict point-in-time restrictions apply.

Process:

```text
freeze historical input state
→ provide point-in-time SoK
→ Decision
→ freeze Decision artifact
→ reveal later outcome
→ evaluate Decision and economic result
→ Learning & Governance
```

Evaluate:

- profitable trades;
- losing trades;
- no-action decisions;
- missed opportunities;
- false positives;
- false negatives;
- risk behavior;
- sizing;
- timing;
- exit;
- calibration;
- economic value.

A winning trade does not prove a good Decision.

A losing trade does not automatically prove a bad Decision or invalid knowledge.

The goal is repeatable economic Decision quality.

---

# Phase 17 — Live Paper Validation

## 22. Final Pre-Live Qualification

After broad historical Decision evaluation and evaluation of both successful and failed outcomes, run the governed Live Paper Validation campaign.

Initial development profile:

```text
starting equity: $10,000 simulated
market inputs: live/current
execution mode: PAPER
portfolio: finite and stateful
```

The Decision Engine must operate against actual simulated account state.

The campaign must prevent:

- cherry-picking;
- resetting capital between trades;
- retrospective entry selection;
- future-information leakage;
- unrealistic fill assumptions;
- hidden transaction costs;
- accidental live routing.

Passing the campaign establishes eligibility for a separate live-authorization process.

It does not grant live authority.

---

# Phase 18 — Trader Interface

## 23. Build the Full Trader-Facing GUI After Contracts Stabilize

Operational/debug interfaces may be created earlier.

The mature trader-facing GUI should be built after Nexus, Market Discovery, Decision, portfolio state, and paper execution interfaces are stable.

Initial trader-facing target:

- six active candidate charts;
- historical candlesticks;
- currently forming live candlestick;
- current price/volume/market state;
- prospective entry region;
- current Decision status;
- `ENTER / WATCH / HOLD / EXIT / NO_ACTION` state as applicable;
- relevant knowledge/evidence;
- uncertainty;
- risk;
- current portfolio impact;
- active position state;
- execution state.

The GUI is a projection and authorized control surface.

It must not:

- derive alternate trading logic;
- become a second Decision Engine;
- become an alternate system of record;
- silently change canonical state outside governed commands.

---

# Phase 19 — Real-Money Execution

## 24. Live Authority Is Last

Real-money execution is introduced only after:

- required historical evaluation;
- required Live Paper Validation;
- objective qualification criteria;
- separate live-authorization review;
- production security controls;
- production observability/audit;
- emergency controls;
- brokerage reconciliation;
- credential governance;
- explicit live execution authority.

Live brokerage credentials are high-risk capabilities.

The existence of execution code does not imply authority to use it.

Paper success does not imply live authority.

---

# Phase 20 — Scale and Optimization

## 25. Scale Only After Correctness

After the complete system works vertically, scale it.

Potential mature improvements include:

- distributed workers;
- server deployment;
- accelerated feature computation;
- large-universe Market Discovery;
- specialized indexes;
- richer caches;
- event streams;
- database/storage backend evolution;
- faster SoK retrieval;
- active-utility optimization;
- parallel research campaigns;
- parallel historical testing;
- higher-frequency current-market processing;
- more sophisticated UI.

Performance optimization may not weaken:

- identity;
- provenance;
- scientific validity;
- authority boundaries;
- point-in-time correctness;
- Decision reconstruction;
- lifecycle rules;
- auditability.

---

# 26. Major Program Milestones

## Milestone A — Governance Ready for Implementation

```text
Architecture + Standards + Policies conformed
dynamic concurrency harmonized
working tree clean
```

## Milestone B — Nexus Alive

```text
publish
retrieve
version
lineage
lifecycle
SoK
restart
```

## Milestone C — Execution Substrate Alive

```text
Task Manager
worker registration
task contracts
dynamic concurrency
recovery
```

## Milestone D — First Engine Loop

```text
Data Intake
→ Nexus
→ Task Manager
→ Analysis
→ Nexus
```

## Milestone E — Scientific Research Loop

```text
Research Director
→ Accountability
→ Task Manager
→ analysis
→ Knowledge Candidate
→ Accountability
→ SoK
```

## Milestone E2 — Deterministic Measurement Convergence

```text
complete applicable deterministic measurement universe
→ five-ticker cohort
→ Analysis
→ Research Director convergence assessment
→ reranking + retrospective tool-coverage review
→ repeat until sufficient convergence
→ evidence-based routine Intake measurement set
```

Campaign:

`Documentation/Campaigns/DETERMINISTIC_MEASUREMENT_CONVERGENCE_CAMPAIGN.md`

## Milestone F — Historical Learning Proof

```text
multiple instruments
successful + failed research
contradictions
promotion
revalidation
```

## Milestone G — Current-Market Intelligence

```text
Market Discovery
→ Nexus
→ Research and/or Decision
```

## Milestone H — Decision Intelligence

```text
SoK + current state + portfolio
→ governed Decision
```

## Milestone I — Economic Simulation

```text
Decision
→ paper Execution
→ portfolio state
→ outcome
→ Learning
```

## Milestone J — $10,000 Live Paper Validation

```text
live market information
finite simulated account
objective campaign
PASS / FAIL / INVALID / INSUFFICIENT_SAMPLE
```

## Milestone K — Trader Interface

```text
six candidate charts
live candle
Decision state
entry/watch/hold/exit
risk + portfolio + execution projection
```

## Milestone L — Live Eligibility

```text
paper PASS
→ separate live authorization
→ explicitly governed real-money capability
```

---

# 27. First Implementation Target

After final cross-policy conformance, begin with:

> **Research Nexus — minimum durable vertical slice.**

The first development objective is not to complete the entire Nexus architecture.

It is to make the following real and tested:

```text
create canonical artifact
→ assign identity/version
→ validate schema
→ publish durably
→ retrieve by identity
→ query by governed metadata
→ create relationship/lineage
→ change governed lifecycle state without rewriting history
→ assemble a small scoped point-in-time SoK
→ restart the process
→ retrieve the same governed state
```

Once that works, build the minimum Task Manager path required to drive Data Intake through the Nexus.

---

# 28. Development Discipline

For every implementation session, ask:

1. What later system capability is this work enabling?
2. What canonical contract governs it?
3. What is the smallest useful vertical implementation?
4. How will we prove it works end to end?
5. How will we detect regression?
6. Does this introduce a second source of truth?
7. Does this accidentally transfer authority?
8. Does this rely on a filesystem path or machine-specific assumption?
9. Can the resulting material state be reconstructed after restart?
10. Are we preserving point-in-time truth?

If those questions cannot be answered, implementation should stop long enough to resolve the missing contract rather than patch around it.

---

# 29. Closing Principle

> **Build MTS from the finished system backward. Build each dependency only deeply enough to support the next real capability, prove it through a vertical path, and preserve the governed boundaries that allow the whole system to remain scientifically valid, economically useful, scalable, auditable, and safe.**
