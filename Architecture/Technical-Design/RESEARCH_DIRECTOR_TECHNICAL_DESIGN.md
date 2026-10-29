# Momentum Trading System — Research Director Technical Design v2.1

**Status:** Proposed — Amended Design
**Component:** Research Director
**Design Goal:** Implement the v2.1 architecture without weakening deterministic governance

---

## 1. Package Structure

```text
Engines/ResearchDirector/
    __init__.py
    models.py
    inquiry.py
    state.py
    change_detection.py
    uncertainty.py
    hypotheses.py
    retrieval.py
    candidate_questions.py
    evaluation.py
    portfolio.py
    selection.py
    convergence.py
    knowledge_candidate.py
    publication.py
    reasoning/
        base.py
        deterministic.py
        ai_adapter.py
```

Existing `models.py`, `inquiry.py`, and `publication.py` are retained and evolved.

---

## 2. New Governed Models

### 2.1 ResearchState

```text
research_state_id
campaign_ref
subject_context
active_question_ref
active_plan_ref
prior_question_refs
prior_plan_refs
finding_refs
evidence_refs
working_hypothesis_refs
research_need_refs
tool_coverage_review_refs
contradiction_refs
relevant_sok_refs
cross_campaign_research_refs
available_capabilities
available_measurements
used_capabilities
used_measurements
stopping_state
resource_state
temporal_integrity_state
state_fingerprint
```

### 2.2 EvidenceChangeRecord

```text
change_id
prior_state_fingerprint
new_state_fingerprint
trigger_refs
new_support
new_negative_evidence
new_contradictions
new_instability
new_context_dependence
new_interactions
new_missing_evidence
new_missing_capability
changed_effects
changed_applicability
```

### 2.3 WorkingHypothesis

See architecture contract.

### 2.4 CandidateQuestion

```text
candidate_question_id
campaign_id
parent_question_id
question_type
question
working_hypothesis_refs
uncertainty_dimensions
trigger_refs
required_evidence
required_capabilities
expected_discriminating_value
semantic_cluster
```

### 2.5 CandidateQuestionEvaluation

Separate fields:

```text
expected_uncertainty_reduction
expected_decision_value
contradiction_resolution_value
knowledge_gap_value
dependency_blocking_value
generalization_value
novelty
information_gain
hypothesis_discrimination_value
evidence_availability
capability_availability
sample_feasibility
temporal_feasibility
compute_cost
data_cost
runtime_cost
redundancy
urgency
ambiguity_risk
```

### 2.6 QuestionSelectionRecord

See architecture contract.

---

## 3. Research State Assembly

`ResearchStateAssembler` receives only governed references / Nexus retrieval.

Pseudo-flow:

```python
state = assembler.build(
    campaign_ref=...,
    active_question_ref=...,
    active_plan_ref=...,
    subject_scope=...,
)
```

The assembler queries:

```text
Research Nexus
State of Knowledge view
Active Research State
Tool/Method registries
prior campaign lineage
```

It does not read private Analysis cache or legacy Engine 10 directories.

---

## 4. Evidence Change Detection

`EvidenceChangeDetector.compare(previous_state, current_state)` returns a durable
change record.

Tests must prove:

- same state → no material change;
- contradiction added → contradiction change;
- new tool gap → missing-capability change;
- effect reversal → changed-effect/contradiction change;
- applicability restriction → context-dependence change.

---

## 5. Uncertainty Decomposition

Interface:

```python
uncertainties = decomposer.decompose(
    state=state,
    change_record=change,
)
```

Each uncertainty has:

```text
uncertainty_id
type
description
materiality
evidence_refs
blocking
resolvable_with_current_capability
```

AI may propose uncertainty objects, but schema validation and evidence references
are mandatory.

---

## 6. Working Hypothesis Generation

`WorkingHypothesisManager` may:

- create;
- update;
- weaken;
- contradict;
- supersede;
- retire.

Hypothesis identity should be semantic and stable enough to relate similar
hypotheses across iterations.

A hypothesis update does not overwrite prior versions.

---

## 7. Cross-Campaign Retrieval

`ResearchRetrievalService` uses Nexus retrieval and ranking.

Query features may include:

```text
subject
sector/theme
measurement names
event family
hypothesis concepts
question type
contradiction concepts
method
context/regime
```

Returned results preserve:

```text
scientific status
applicability
validation
recency
contradiction burden
source campaign
```

Retrieval rank affects attention, not validity.

---

## 8. Candidate Question Generation

Two generators operate together:

### Deterministic generator

Guaranteed coverage for:

- missing evidence;
- missing capability;
- contradiction;
- instability;
- tool coverage;
- robustness;
- convergence requirements.

### AI generator

Produces richer:

- alternative explanations;
- interaction hypotheses;
- context/regime questions;
- generalization questions;
- economic-value questions;
- cross-campaign analogies;
- discriminating tests between Working Hypotheses.

The union is deduplicated semantically.

---

## 9. Candidate Evaluation

No single hard-coded scientific score.

Operational selection policy can compute a priority value, but stores all raw
dimensions.

Example policy interface:

```python
evaluation = evaluator.evaluate(candidate, state)
priority = policy.rank(evaluation)
```

Policy is versioned.

Candidate with highest operational priority is not automatically scientifically
valid; it is only the preferred next research action among valid candidates.

---

## 10. Portfolio Diversity

`QuestionPortfolioController` groups candidate questions by:

```text
semantic cluster
question type
working hypothesis
uncertainty dimension
measurement family
method family
time horizon
context
```

It penalizes redundant candidates and may retain a small frontier of diverse
high-value alternatives.

This recovers the strongest legacy Engine 10 portfolio concept without restoring
legacy proposal logic.

---

## 11. Selection

`QuestionSelector.select(...)` returns:

```text
selected Question
QuestionSelectionRecord
deferred candidate refs
```

Selection must fail closed when:

- no candidate has adequate evidence/capability path;
- selection would violate temporal integrity;
- candidate requires prohibited authority;
- resource policy blocks all candidates.

In those cases the Director produces an explicit governed unresolved/blocked state.

---

## 12. Tool Coverage

Tool Coverage Review is generated by Analysis or a governed retrospective
Analysis task, not fabricated by Research Director.

Research Director evaluates the Review against:

```text
current Working Hypotheses
alternative explanations
used vs available tools
previous tool gaps
cross-campaign tool relevance
```

An unused tool becomes a follow-up only if there is a scientifically material
reason it could change interpretation.

---

## 13. Convergence

Convergence engine consumes:

```text
ResearchState
StoppingCriteria
ToolCoverageReview
contradiction state
Working Hypothesis state
replication/robustness state
holdout state
resource state
```

It emits explicit criterion-by-criterion results.

No narrative-confidence field may substitute for criteria.

---

## 14. Knowledge Candidate

`KnowledgeCandidateBuilder` consumes only research state that satisfies candidate
eligibility criteria.

The builder does not promote.

It preserves:

```text
claim
scope/applicability
supporting refs
contradictory refs
uncertainty
validation
replication
generalization
economic relevance
Working Hypothesis lineage
research campaign lineage
```

---

## 15. AI Adapter Contract

```python
class ResearchReasoningAdapter(Protocol):
    def decompose_uncertainty(self, state, change): ...
    def propose_hypotheses(self, state, uncertainties): ...
    def propose_questions(self, state, hypotheses, uncertainties, retrieved): ...
    def explain_selection(self, state, candidates, evaluations, selected): ...
```

The adapter returns structured proposals only.

All returned objects require:

- schema validation;
- evidence refs;
- state fingerprint;
- temporal validation;
- authority validation.

The AI adapter cannot directly call Task Manager or publication gates.

---

## 16. Deterministic Fallback

If AI reasoning fails:

```text
AI invalid/unavailable
    ↓
deterministic guardrail generator
    ↓
bounded valid Question / Research Need / unresolved outcome
```

Autonomous research may degrade in creativity but must not degrade in governance.

---

## 17. Tests Required for 10/10 Target

### Evidence lineage
- full question → plan → finding → state → next-question chain reconstructs.

### True iterative inquiry
- alter returned Finding and selected next question changes materially.

### Question creativity
- multiple plausible candidates generated from one complex Finding;
- candidates span distinct uncertainty dimensions.

### Scientific governance
- AI cannot bypass admission/promotion/scheduling boundaries.

### Missing evidence
- missing evidence produces targeted question and preserves insufficiency reason.

### Missing capability
- gap produces Research Need; valid alternative must be explicit.

### Tool sufficiency
- unused tool alone does not cause follow-up;
- materially relevant unused tool does.

### Prioritization
- higher information-value candidate can beat cheaper but redundant question;
- raw dimensions remain visible.

### Contradiction
- competing hypotheses generated;
- discriminating question selected.

### Objective stopping
- every criterion machine-evaluable;
- resource ceiling does not equal convergence.

### Cross-research learning
- prior related campaign changes candidate generation or priority;
- stale/inapplicable prior research does not dominate.

### Restart/auditability
- serialize all durable state;
- rebuild process produces same selected question from same governed state.

---

## 18. First Implementation Sequence

```text
Phase RD-B1  ResearchState + EvidenceChangeRecord
Phase RD-B2  WorkingHypothesis model/lifecycle
Phase RD-B3  Cross-campaign retrieval adapter
Phase RD-B4  CandidateQuestion generator
Phase RD-B5  Candidate evaluation dimensions
Phase RD-B6  Portfolio diversity + selection
Phase RD-B7  AI reasoning adapter behind contracts
Phase RD-B8  Single-ticker adaptive POC
Phase RD-B9  restart/replay proof
Phase RD-B10 Knowledge Candidate boundary proof
```

Do not initiate a multi-ticker convergence campaign before RD-B8 passes.

---

## 19. Acceptance Gate

Research Director v2.1 is not considered implementation-complete merely because
unit tests pass.

The minimum live acceptance test requires one real ticker and must show:

1. Question 1 is governed.
2. Analysis returns real Findings.
3. Research State is rebuilt.
4. multiple Working Hypotheses/candidate questions are generated.
5. candidates are evaluated.
6. one is selected with auditable rationale.
7. modifying Finding 1 changes the candidate frontier or selection.
8. Analysis answers selected Question 2.
9. Director either asks evidence-driven Question 3 or reaches an explicit governed
   convergence/unresolved state.
10. restart/replay reproduces the same state and decision from identical artifacts.
