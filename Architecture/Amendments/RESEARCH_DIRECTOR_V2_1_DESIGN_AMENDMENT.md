# Research Director v2.1 — Design Amendment Summary

This amendment preserves the v2 core and adds the intelligence layers needed to
reach the target design capability across all previously assessed categories.

## Preserved from v2 Core

- evidence-triggered Question lineage;
- Research Campaign / Question / Plan / Need;
- missing-evidence semantics;
- missing-capability semantics;
- Tool Coverage Review;
- deterministic guardrail inquiry;
- objective stopping;
- Nexus durability;
- authority separation.

## Recovered and Improved from Legacy Engine 10

| Legacy Strength | v2.1 Form |
|---|---|
| broad question generation | Candidate Question Generator driven by current evidence |
| question clusters | semantic clusters + uncertainty dimensions |
| portfolio score | inspectable multi-dimensional Research Value Evaluation |
| question diversity | Portfolio Diversity Controller |
| knowledge claims | non-canonical Working Hypotheses |
| proposal ancestry | full reasoning lineage and state fingerprints |

## New Capabilities

- Research State Model;
- Evidence Change Record;
- Uncertainty Decomposer;
- Working Hypothesis lifecycle;
- Cross-Campaign Research Retrieval;
- Candidate Question Set;
- Candidate Research Evaluation;
- Question Selection Record;
- AI reasoning adapter behind governed contracts;
- deterministic fallback;
- cross-research learning;
- explicit Knowledge Candidate builder boundary.

## Critical Rule

The Director never selects Question 2 merely because a static branch says
"contradiction → ask temporal question."

The deterministic branch remains a safe fallback.

Normal target operation is:

```text
evidence
→ state
→ uncertainty
→ hypotheses
→ related prior research
→ candidate questions
→ evaluation
→ diversity control
→ selected question
```

All steps remain auditable.
