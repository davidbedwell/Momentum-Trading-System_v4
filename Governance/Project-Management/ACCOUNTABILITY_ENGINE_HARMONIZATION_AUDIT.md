# Accountability Engine Architecture Harmonization Audit

## Scope

This audit records the introduction of the Accountability Engine into current
MTS architecture and governance.

Historical design discussion is documented here; active canonical architecture
describes only the resulting current design.

## Architectural Change

MTS now separates:

- scientific authorship/proposal — Research Director;
- independent research gatekeeping — Accountability Engine;
- execution coordination — Task Manager;
- durable state/lifecycle record — Research Nexus;
- investment judgment/execution initiation — Decision Engine;
- outcome/lifecycle evaluation — Learning & Governance.

## Gate 1 — Research Admission

Before governed research execution, Accountability evaluates a proposed Research
Plan for Charter alignment, testability, duplication, scientific safeguards,
resource proportionality, and applicable policy.

## Gate 2 — Knowledge Promotion

Before a Knowledge Candidate crosses a knowledge-authority boundary requiring
independent review, Accountability evaluates the required objective promotion
criteria.

## Decision Boundary

Accountability does not approve individual trades.

Decision Engine retains authority to initiate and manage trades within authority
already granted by Decision, Risk, and Automation policy.

## Repository

`Engines/Accountability/` was added as an organizational implementation
location. The directory does not define component identity or authority.

## Research Policy

`RESEARCH_POLICY.md` was revised so Research Director prepares the scientific
case while Accountability independently evaluates Research Admission and
Knowledge Promotion gates.
