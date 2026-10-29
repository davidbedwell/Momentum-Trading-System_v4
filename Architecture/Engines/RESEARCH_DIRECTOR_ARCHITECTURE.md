# Momentum Trading System — Research Director Architecture v2.1

**Status:** Proposed — Amended Design
**Component:** Research Director
**Primary Role:** Evidence-driven autonomous research intent, inquiry, prioritization, progression, convergence, and Knowledge Candidate authorship
**Supersedes Design:** Research Director Core v2 architecture only after governed adoption
**Preserves:** Evidence-triggered iteration, Research Need handling, Tool Coverage Review, durable lineage, authority separation, explicit stopping criteria

---

## 1. Design Objective

Research Director v2.1 combines the scientific governance and evidence lineage of
the v2 core with the strongest useful ideas from legacy Engine 10:

- broad candidate-question generation;
- portfolio diversity;
- question clustering;
- proposal ancestry;
- semantic claim formation.

The amendment does not restore legacy storage, proposal schemas, private Engine 10
knowledge bases, filesystem coupling, or fixed question-generation behavior.

The target behavior is:

```text
governed research state
    ↓
what changed?
    ↓
what remains uncertain?
    ↓
what explanations are plausible?
    ↓
what prior research is relevant?
    ↓
what questions could resolve the uncertainty?
    ↓
which question has the highest governed research value?
    ↓
Research Question
    ↓
Research Plan
    ↓
execution through governed system
    ↓
returned Evidence / Findings
    ↓
repeat until objective convergence or explicit unresolved state
```

---

## 2. Non-Negotiable Scientific Principle

The next Research Question must depend materially on returned governed evidence.

A fixed sequence of questions, a static checklist, or a candidate-question bank
alone does not demonstrate iterative research.

Every selected next question SHALL preserve:

- parent Question identity;
- triggering Evidence/Finding references;
- triggering research-state fingerprint;
- explicit unresolved uncertainty;
- Working Hypothesis or gap that motivated the question;
- candidate alternatives considered;
- selection rationale;
- applicable stopping/resource state.

---

## 3. Research Director Internal Architecture

```text
Research Nexus / State of Knowledge / Active Research State
                         ↓
                Research State Assembler
                         ↓
                  Research State Model
                         ↓
                Evidence Change Detector
                         ↓
                 Uncertainty Decomposer
                         ↓
              Working Hypothesis Manager
                         ↓
        Cross-Campaign Research Retrieval
                         ↓
             Candidate Question Generator
                         ↓
           Candidate Research Evaluator
                         ↓
      Diversity / Redundancy Portfolio Control
                         ↓
              Question Selection Reasoner
                         ↓
                 Research Question
                         ↓
                  Research Plan
                         ↓
     Accountability → Task Manager → Intake/Analysis
                         ↓
                 governed results
                         ↺
```

The deterministic inquiry kernel remains available beneath this stack as a
minimum safe fallback and conformance guard.

---

## 4. Research State Model

Before deciding what to ask next, Research Director SHALL construct a governed
Research State Model sufficient to understand the current investigation.

The model includes, where available:

```text
campaign
subject / instrument
research objective
current Question
current Plan
prior Questions / Plans
input artifact references
historical coverage
available data sources
available measurements
available deterministic computations
available analytical methods
methods actually used
measurements actually used
Evidence
Findings
effect magnitudes
uncertainty
negative findings
contradictions
instability
generalization failures
missing evidence
missing capability
Tool Coverage Review
Working Hypotheses
State of Knowledge relevant to the subject
related cross-campaign research
resource / cost state
stopping criteria
holdout / temporal constraints
```

The Research Director must not rely on ticker name alone to infer sufficiency.

---

## 5. Evidence Change Detector

After every material return, Research Director determines what changed relative
to the prior research state.

Change categories include:

- newly supported proposition;
- newly unsupported proposition;
- contradiction;
- instability;
- subgroup/context dependence;
- temporal dependence;
- newly discovered interaction;
- missing evidence;
- missing capability;
- newly available capability;
- changed effect magnitude;
- failure of robustness/generalization;
- unexpected null result;
- newly plausible alternative explanation;
- changed economic relevance;
- change in applicability.

The change record is durable research lineage.

---

## 6. Uncertainty Decomposer

Research Director SHALL decompose remaining uncertainty rather than treating
"more research needed" as one undifferentiated state.

Examples:

```text
causal/explanatory uncertainty
measurement uncertainty
sampling uncertainty
temporal uncertainty
context/regime uncertainty
generalization uncertainty
economic-value uncertainty
contradiction uncertainty
tool-coverage uncertainty
data-coverage uncertainty
interaction uncertainty
model/specification uncertainty
```

Each material uncertainty may generate zero or more Working Hypotheses and
candidate questions.

---

## 7. Working Hypothesis Model

Research Director v2.1 introduces a governed but non-canonical Working Hypothesis.

A Working Hypothesis is NOT Knowledge.

It represents a temporary explanatory proposition used to organize research.

Required semantics include:

```text
hypothesis_id
campaign_id
subject_scope
statement
originating evidence refs
supporting evidence refs
contradictory evidence refs
alternative_hypothesis_ids
status
applicability
uncertainty_dimensions
required_tests
created_from_question_id
supersedes_hypothesis_id
```

Possible states:

```text
PROPOSED
ACTIVE
SUPPORTED_BY_CURRENT_EVIDENCE
WEAKENED
CONTRADICTED
UNRESOLVED
RETIRED
READY_FOR_KNOWLEDGE_CANDIDATE_REVIEW
```

A Working Hypothesis must never be exposed as canonical knowledge merely because
it is frequently used or repeatedly retrieved.

---

## 8. Cross-Campaign Research Retrieval

Before generating new questions, Research Director SHOULD retrieve materially
related governed research.

Retrieval may consider:

- same instrument;
- same measurement;
- same event family;
- same market/sector context;
- same hypothesis concept;
- same contradiction;
- same analytical method;
- similar applicability conditions;
- prior failed or unresolved attempts.

The retrieval layer returns relevant:

```text
State of Knowledge
Working Hypotheses
prior Findings
contradictions
Research Needs
prior Questions
prior Plans
tool gaps
resolved tool gaps
```

Research Director uses this to avoid:

- rediscovering already answered questions;
- repeating failed investigations without new evidence;
- treating one-instrument behavior as novel when it has already generalized;
- ignoring known contradictions.

Cross-campaign retrieval must not silently import stale conclusions as current
truth. Applicability, recency, validation, and contradiction state remain visible.

---

## 9. Candidate Question Generator

Research Director SHALL generate multiple candidate next questions when more than
one scientifically plausible path exists.

Candidate generation sources include:

1. unresolved contradiction;
2. unexplained variance;
3. temporal instability;
4. subgroup/context dependence;
5. Working Hypothesis discrimination;
6. alternative explanations;
7. missing evidence;
8. missing capability alternatives;
9. robustness/generalization requirements;
10. Tool Coverage Review;
11. cross-campaign analogies;
12. unexpected null/negative results;
13. newly discovered interactions;
14. economic significance;
15. applicability boundaries;
16. State of Knowledge gaps.

Candidate generation may use AI reasoning, deterministic templates, or both.

AI generation remains constrained by governed state. It may not invent unavailable
facts, silently introduce future information, or bypass tool/data capability checks.

---

## 10. Candidate Research Evaluation

Every candidate question receives separate, inspectable evaluation dimensions.

There is no single scientifically authoritative opaque score.

Dimensions include:

```text
expected uncertainty reduction
expected decision/economic value
contradiction-resolution value
knowledge-gap importance
dependency-blocking value
generalization value
novelty
expected information gain
ability to discriminate competing hypotheses
evidence availability
capability availability
sample feasibility
temporal/holdout feasibility
estimated compute cost
estimated provider/data cost
expected runtime
redundancy with prior questions
redundancy with other current candidates
urgency / recency sensitivity
risk of ambiguous result
```

A selection policy may combine dimensions for operational ranking, but the
underlying dimensions and policy version remain visible.

Scientific validity is never determined by the ranking score.

---

## 11. Question Portfolio and Diversity Control

The useful portfolio concept from legacy Engine 10 is retained and strengthened.

Research Director should avoid selecting many semantically redundant questions.

Diversity may be evaluated across:

- Question Type;
- hypothesis cluster;
- measurement family;
- time horizon;
- market context;
- analytical method;
- uncertainty dimension;
- evidence source;
- subject/instrument.

Portfolio diversity is an efficiency principle, not a scientific validity rule.

When one question is selected for immediate execution, high-value alternatives
may remain durable queued research candidates rather than being discarded.

---

## 12. Question Selection Reasoning

The selected next question SHALL have a durable Question Selection Record.

It identifies:

```text
selected_question_id
candidate_question_ids
research_state_fingerprint
evidence_trigger_refs
working_hypothesis_refs
cross_campaign_refs_considered
evaluation dimensions per candidate
selection policy/version
redundancy/diversity adjustment
selected candidate
selection rationale
rejected/deferred candidate reasons
resource envelope
```

This record makes it possible to audit not only what Research Director asked,
but why it asked that question instead of another plausible question.

---

## 13. Tool Sufficiency and Retrospective Tool Coverage

A successful Analysis result does not prove tool sufficiency.

When required for closure, Research Director SHALL require a Tool Coverage Review.

The review includes:

- governed capabilities available;
- governed measurements available;
- capabilities used;
- measurements used;
- available-but-unused capabilities;
- available-but-unused measurements;
- material untested alternatives;
- missing evidence;
- missing capability;
- scientifically valid alternatives;
- whether the unused capability could materially challenge the conclusion.

Non-use alone is not negative evidence about a tool.

Repeated evidence that a tool is materially useful may later support Tool Library
or Intake-baseline review through separate governance.

---

## 14. Contradiction Reasoning

Contradictions are first-class research state.

Research Director SHALL:

1. preserve both sides;
2. identify scope/context/time differences;
3. generate competing Working Hypotheses;
4. select discriminating questions;
5. maintain contradiction lineage;
6. prevent convergence while a material blocking contradiction remains unless
   stopping policy explicitly permits bounded unresolved status.

Contradictory evidence must not be deleted to improve apparent consistency.

---

## 15. Missing Evidence and Missing Capability

The v2 core semantics remain authoritative.

Missing evidence generates a governed evidence-acquisition/refinement question
when possible.

Missing capability generates a Research Need identifying:

```text
missing capability
blocked question
why required
scientific consequence
valid alternatives
expected value of filling the gap
evidence lineage
```

Research Director may proceed through a valid alternative, defer the branch,
close it explicitly unresolved, or await separately governed capability work.

It must never silently substitute a materially different method.

---

## 16. Research Priority

Research priority is distinct from scientific validity.

Priority may consider:

- uncertainty reduction;
- decision value;
- contradiction burden;
- knowledge gap;
- dependency blocking;
- generalization potential;
- urgency;
- cost;
- resource availability;
- recency sensitivity.

Priority policy is versioned and auditable.

---

## 17. Objective Stopping and Convergence

Research Director does not stop because results "look convincing."

Stopping criteria are explicit in the Research Plan or governed research policy.

Criteria may include:

- minimum completed iterations;
- required contradiction resolution;
- Tool Coverage Review complete;
- no material missing evidence;
- no blocking missing capability;
- no material untested alternative;
- robustness requirement;
- replication requirement;
- holdout requirement;
- stability bounds;
- generalization requirement;
- economic-significance requirement;
- resource ceilings.

Possible outcomes:

```text
ANSWER_SUPPORTED
ANSWER_NOT_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
MORE_RESEARCH_REQUIRED
MISSING_CAPABILITY
CONVERGED
CONVERGED_WITH_BOUNDED_UNRESOLVED_STATE
RESOURCE_CEILING_REACHED
```

Resource ceilings do not manufacture scientific convergence.

---

## 18. Cross-Research Learning

Research Director SHALL learn structurally across campaigns without rewriting
scientific history.

Examples:

- recurring Working Hypothesis across instruments;
- recurring missing capability;
- recurring contradiction;
- measurement useful only in specific contexts;
- research method consistently high-information;
- repeated null result;
- repeated generalization success/failure.

Such patterns may trigger:

- broader generalization research;
- Tool Library review;
- new Research Need;
- Knowledge Candidate proposal;
- retirement of a Working Hypothesis.

---

## 19. Knowledge Candidate Boundary

Research Director may author a Knowledge Candidate only after governed stopping
criteria for the relevant research claim are met.

A Knowledge Candidate:

- references all material supporting evidence;
- references material contradictory evidence;
- states applicability;
- states uncertainty;
- states validation/generalization status;
- preserves Working Hypothesis lineage.

Research Director may not promote its own Knowledge Candidate.

Accountability remains the independent Knowledge Promotion gate.

---

## 20. Restart and Durable Research Memory

The following are durable Class II research state when required for continuation:

- Campaign;
- Question;
- Plan;
- Research Need;
- Working Hypothesis;
- Evidence Change Record;
- Candidate Question Set;
- Question Selection Record;
- Iteration Evaluation;
- Tool Coverage Review;
- unresolved contradictions;
- queued candidate questions;
- stopping/resource state.

A restarted Research Director reconstructs current research state from Research
Nexus and does not depend on conversational/in-memory history.

---

## 21. AI Reasoning Adapter

The final Research Director may use an AI reasoning adapter for:

- uncertainty decomposition;
- hypothesis generation;
- candidate question generation;
- semantic similarity;
- alternative explanation generation;
- question-selection explanation.

The AI adapter is not an authority boundary.

All AI-generated output must be converted into governed artifacts before execution.

The adapter cannot:

- directly schedule workers;
- bypass Research Admission;
- write canonical knowledge;
- fabricate data;
- redefine stopping criteria;
- hide rejected candidate questions;
- silently alter prior research.

---

## 22. Deterministic Guardrail Kernel

The deterministic v2 core remains required.

It provides guaranteed behaviors for:

```text
MISSING_CAPABILITY
MISSING_EVIDENCE
CONTRADICTION
UNSTABLE_RESULT
missing Tool Coverage Review
material untested alternative
robustness requirement
stopping criteria
```

If AI reasoning is unavailable, invalid, or fails validation, the deterministic
kernel can still produce a bounded governed research disposition.

---

## 23. Target Capability Matrix

The amended architecture targets maximum design completeness across the following
dimensions:

| Capability | v2.1 Design Target |
|---|---:|
| Evidence lineage | 10/10 |
| True iterative inquiry | 10/10 |
| Question creativity | 10/10 |
| Scientific governance | 10/10 |
| Missing-evidence reasoning | 10/10 |
| Missing-capability reasoning | 10/10 |
| Tool sufficiency | 10/10 |
| Question prioritization | 10/10 |
| Contradiction handling | 10/10 |
| Objective stopping | 10/10 |
| Cross-research learning | 10/10 |
| Restart/auditability | 10/10 |

These are architecture targets, not empirical performance claims. Implementation
must prove them through tests and live research POCs.

---

## 24. First Required Proof

The first v2.1 Research Director proof SHALL use one real ticker.

It must demonstrate:

```text
Question 1
→ Plan 1
→ Analysis Finding 1
→ Research State rebuild
→ Working Hypotheses generated
→ multiple candidate Question 2 options generated
→ candidates evaluated
→ Question 2 selected with preserved reason
→ Plan 2
→ Analysis Finding 2
→ Research State rebuild
→ Tool Coverage Review
→ further question OR objective convergence/unresolved outcome
```

Test invariant:

> materially changing Finding 1 must be capable of changing the Working
> Hypotheses, candidate questions, candidate evaluations, and selected Question 2.

Only after this single-ticker proof succeeds should a multi-ticker convergence
campaign begin.

---

## 25. Closing Principle

Research Director is not a question generator and not a scoring engine.

It is the governed scientific intelligence responsible for answering:

> Given what MTS intended to learn, what it already knew, what it just learned,
> what remains uncertain, what explanations remain plausible, what tools and data
> exist, what related research already exists, and what it costs to learn more:
> what is the highest-value scientifically valid question to ask next, and why?

That question must always be reconstructable from governed evidence.
