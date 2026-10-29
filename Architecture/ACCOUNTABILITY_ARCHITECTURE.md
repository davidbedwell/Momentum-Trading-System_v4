# Momentum Trading System — Accountability Engine Architecture

**Status:** Canonical
**Authority:** Governing component architecture subordinate to `CHARTER.md` and `Architecture/SYSTEM_ARCHITECTURE.md`

---

## 1. Purpose

The Accountability Engine provides independent, Charter-derived gatekeeping
around the research lifecycle.

It exists because the component that proposes research or authors a scientific
conclusion must not be the only component deciding whether that proposal may
consume governed resources or whether that conclusion has earned higher
knowledge authority.

---

## 2. Governing Principle

> **Research proposes. Accountability gates. Task Management executes admitted work. The Research Nexus records governed state. Decision independently exercises granted investment authority.**

---

## 3. Prime-Directive Alignment

Every Accountability gate evaluates the proposal against the MTS Charter.

The engine asks whether the proposed use of research resources or knowledge
authority plausibly advances MTS's enduring objective through improved:

- opportunity discovery;
- predictive understanding;
- risk characterization;
- Decision quality;
- implementation quality;
- explainability;
- reproducibility;
- system reliability or research integrity required to support those goals.

"Interesting" is not sufficient.

Charter alignment does not require every research question to have an immediate
trade attached to it. Foundational research may be admitted when it creates a
necessary dependency for future economic or scientific capability.

---

## 4. Gate 1 — Research Admission

A proposed Research Plan must pass Research Admission before the Task Manager
executes its governed research work, except for explicitly exempt maintenance,
validation, or emergency work defined by policy.

Research Admission evaluates:

- Charter alignment;
- testability;
- expected information value;
- expected Decision/scientific relevance;
- duplication against existing SoK and Active Research State;
- scientific-integrity safeguards;
- evidence availability;
- required capability availability;
- resource proportionality;
- defined stopping criteria;
- authority/policy compliance.

Allowed verdict semantics include:

```text
RP_ADMITTED
RP_ADMITTED_WITH_LIMITS
RP_REVISION_REQUIRED
RP_DUPLICATIVE
RP_DEFERRED
RP_REJECTED
```

A negative verdict must state which objective criterion was not met.

---

## 5. Gate 2 — Knowledge Promotion

A Knowledge Candidate must pass Knowledge Promotion review before crossing a
knowledge-authority boundary that policy subjects to independent Accountability.

Knowledge Promotion evaluates:

- provenance completeness;
- data-quality status;
- reproducibility;
- validation independence;
- holdout integrity;
- replication requirements;
- robustness;
- applicability scope;
- uncertainty;
- contradiction characterization;
- search/multiple-testing context where applicable;
- economic/Decision relevance where required;
- policy-specific lifecycle criteria.

Allowed verdict semantics include:

```text
PROMOTION_GATES_PASSED
PROMOTION_GATES_PASSED_WITH_SCOPE
MORE_RESEARCH_REQUIRED
INSUFFICIENT_EVIDENCE
PROMOTION_BLOCKED
```

A gate verdict is not the scientific conclusion. It states whether the required
case for a governed lifecycle transition was demonstrated.

---

## 6. Interested-Proposer Separation

A research-level component may create work or scientific output within its
authority.

It may not independently cross a knowledge-authority boundary for its own
output when current governance requires independent Accountability review.

This rule applies to the gated research lifecycle. It does not prohibit the
Decision Engine from exercising investment authority already granted by
Decision, Risk, and Automation policy.

---

## 7. Relationship to Research Director

Research Director owns:

- question formation;
- hypothesis formation;
- scientific design;
- Research Plan authorship;
- evidence interpretation;
- evidence-dependent iteration;
- convergence proposal;
- Knowledge Candidate authorship.

Accountability owns:

- Research Admission verdict;
- Knowledge Promotion gate verdict.

Accountability may return a plan/candidate for revision or more evidence. It
must not rewrite the scientific conclusion as its own.

---

## 8. Relationship to Task Manager

Task Manager owns scheduling, routing, worker selection, retries, concurrency,
and execution supervision.

For research task classes requiring Research Admission, Task Manager must verify
a valid current admission verdict before releasing work.

Accountability never selects workers or maintains a competing queue.

---

## 9. Relationship to Research Nexus

Research Nexus preserves:

- proposed Research Plans;
- Accountability gate verdicts;
- evidence referenced by the verdict;
- policy/criteria versions;
- resulting lifecycle transitions;
- audit/provenance lineage.

Research Nexus does not decide whether a gate passed merely because the verdict
artifact was stored.

---

## 10. Relationship to Decision Engine

Accountability does not approve individual trades.

Decision Engine may initiate and manage trades within authority already granted
by applicable Decision, Risk, and Automation policy.

Accountability may later support audit of whether governed knowledge and policy
requirements were satisfied, but it must not become a second investment
Decision Engine.

---

## 11. Relationship to Learning & Governance

Learning & Governance may evaluate whether Accountability itself is helping MTS.

Examples include:

- admitted-RP yield;
- duplicated-work avoidance;
- percentage of admitted research that produces material knowledge;
- false blocking or premature admission patterns;
- promoted-knowledge stability;
- Decision utility of promoted knowledge;
- resource efficiency.

Learning may recommend gate-policy changes. Accountability cannot change its own
criteria because it dislikes those evaluations.

---

## 12. Deterministic and Judgmental Criteria

Accountability should use deterministic checks wherever objective evidence
permits, including:

- required field presence;
- policy version validity;
- validation-state presence;
- provenance completeness;
- holdout status;
- resource limits;
- duplicate identifiers/known equivalent work;
- required approvals.

Some criteria require bounded evaluation, such as expected information value or
Charter relevance.

Those evaluations must still produce structured reasons and may not rely on
undefined confidence language.

---

## 13. Gate Criteria Versioning

Every verdict must reference the exact criteria/policy version used.

Changing criteria must not retroactively rewrite historical verdicts.

A candidate may be reevaluated under a newer policy only through an explicit
new gate evaluation.

---

## 14. Failure Behavior

If Accountability cannot validly evaluate a required gate because evidence,
policy, schema, or capability is missing, it must fail closed for that gate.

Valid outcomes include:

```text
REVISION_REQUIRED
DEFERRED
INSUFFICIENT_EVIDENCE
BLOCKED
```

It must not fabricate a passing verdict.

---

## 15. Auditability

For each verdict, MTS must be able to reconstruct:

```text
proposal/candidate
→ applicable Charter/policy criteria
→ evidence inspected
→ criterion-by-criterion result
→ verdict
→ limits/reasons
→ resulting task or lifecycle action
```

---

## 16. Initial Implementation

The initial Accountability Engine should prove:

1. Research Plan admission against machine-inspectable criteria;
2. rejection of a duplicative or non-testable RP with reasons;
3. admission with resource limits;
4. Knowledge Candidate gate review;
5. blocking promotion when a mandatory validation gate is absent;
6. passing a candidate when all required gates are independently evidenced;
7. durable verdict publication;
8. Task Manager refusal to execute gated research without admission;
9. no interference with individual Decision Engine trade authority.

---

## 17. Repository Organization

The implementation may be organized under:

```text
Engines/Accountability/
```

This path is organizational only.

Identity, routing, authority, dependency, and workflow derive from governed
component identity, capabilities, contracts, tasks, and policy—not from the
directory name or physical repository position.

---

## 18. Closing Principle

> **Accountability does not decide what MTS should believe or trade. It verifies whether MTS has demonstrated the governed right to spend research resources and to elevate research output into higher knowledge authority.**
