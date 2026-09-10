# ADR — AI Scientific Appeal Authority

**Date:** 2026-09-10  
**Status:** Approved restoration of omitted v2 authority behavior  
**Scope:** MTS v4 Research Director provider routing and objective-contract repair escalation

## Decision

MTS v4 retains a provider-neutral two-level AI scientific authority path.

The normal/local AI Research Director is the primary scientific reasoning provider. When a Research Director decision repeatedly fails an objective deterministic execution contract, the local AI receives up to three repair attempts. If the third local repair attempt still does not resolve the objective contract defect, the next repair is escalated to the explicitly authorized appellate AI provider.

For the current implementation:

- primary/local provider: Qwen;
- appellate provider: OpenAI GPT-5.6 Sol;
- local repair attempts before appeal: three;
- appellate scope: the unresolved scientific/execution-contract decision that triggered escalation.

The provider identities are implementation choices. The authority relationship is provider-neutral.

## Authority Rule

The appellate AI is the superior scientific authority for the adjudicated appeal scope. Its valid scientific disposition controls that scope and may affirm, revise, replace, or close the primary AI's decision.

The primary Research Director may not overrule a valid appellate disposition for the same adjudicated scope. Deterministic code may not act as a scientific appeals court over either AI provider.

## Deterministic Boundary

Deterministic code may:

- count objective-contract repair attempts;
- detect that the configured local repair limit has been exhausted;
- route the current governed context, exact objective defects, and failed local repair sequence to the authorized appellate provider;
- validate the appellate provider's returned decision against the same objective execution and representation contracts;
- stop with an objective error if the appellate return itself remains mechanically invalid.

Deterministic code may not:

- select a scientific answer for the appeal;
- rewrite scientific questions, hypotheses, methods, parameters, interpretations, or findings;
- resolve scientific disagreement between primary and appellate AI;
- weaken or replace a valid appellate scientific disposition.

## Appeal Context

The appeal receives the current governed scientific context and a mechanical record of the failed local repair sequence. That record is provenance and context, not deterministic scientific interpretation.

## Relationship to Existing v4 Authority

This ADR restores the omitted escalation behavior while preserving the existing v4 rule that AI owns scientific reasoning and deterministic code is limited to objective execution, representation, identity, lineage, temporal, permission, reproducibility, and resource-safety contracts.

It does not alter the Research Nexus data-retention boundary, Analysis payload lifecycle, restart/recovery design, scientific method catalog, or campaign state.

## Current Execution Policy

The AAPL live E2E runner configures four total objective-contract repair opportunities in the mechanical orchestrator: three primary-Qwen repairs followed, if still necessary, by one Sol appeal. A mechanically invalid Sol appeal is not silently returned to Qwen and does not receive deterministic scientific correction; the run stops with the objective contract error.
