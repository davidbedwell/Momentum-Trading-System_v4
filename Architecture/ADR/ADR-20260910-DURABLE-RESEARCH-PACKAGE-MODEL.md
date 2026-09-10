# ADR — Durable Research Package Model

Date: 2026-09-10
Status: Accepted for implementation

## Decision

MTS v4 will preserve each coherent AI-directed research line as a durable Research Package (RP). Creating or activating a later RP must never overwrite, reuse, or erase an earlier RP.

An RP is a mechanical persistence container for AI-authored scientific work. It is not a deterministic scientific actor, hypothesis generator, question selector, method selector, significance evaluator, or convergence engine.

The AI Research Director owns all scientific relationships recorded in an RP, including whether a question is a follow-up to another question, whether a materially distinct line of inquiry warrants a child RP, what hypotheses or interpretations apply, what findings are significant, what remains unresolved, and why the RP is closed.

Deterministic code may validate identifiers, parent/child references, subject/campaign consistency, lineage existence, record shape, append/version mechanics, and immutable-history rules. It may not infer scientific relationships that the AI Research Director did not author.

## Persistence Semantics

Each RP has a stable unique identity. An RP may accumulate additional AI-authored questions, analyses, interpretations, findings, unresolved issues, and state transitions while active. Those additions extend the historical record; they do not replace prior history.

Once an RP is closed, its scientific history is frozen. Later research may reference, challenge, extend, or supersede the RP, but it must not rewrite the original record.

A new RP is always a new durable object. It never overwrites the prior RP. A child RP may reference a parent RP when the AI Research Director explicitly declares the relationship.

## Research Package Contents

The durable RP record supports the following mechanical structure:

- `rp_id`: stable unique research-package identity;
- `subject_id`: subject under investigation;
- `campaign_id`: campaign that originated the RP;
- `parent_rp_id`: optional AI-authored parent RP relationship;
- originating scientific question and rationale;
- AI-authored hypotheses/propositions and scientific state;
- question lineage with stable question IDs and optional parent-question IDs;
- Analysis request/result lineage tied to the question that caused the Analysis;
- AI interpretation of Analysis results;
- findings promoted by the AI Research Director and their supporting lineage;
- unresolved scientific issues and unavailable-resource records authored by the AI Research Director;
- explicit open/closed state, close reason, and final AI assessment;
- operational timestamps/version metadata used only for persistence and audit.

Follow-up questions remain bundled under the originating RP unless the AI Research Director explicitly creates a distinct child RP.

## Relationship to Research Nexus

The Research Nexus remains durable research memory rather than a raw-data warehouse. RPs are durable structured research records that the Nexus may index and relate across subjects, findings, hypotheses, unresolved issues, and later RPs.

Raw or otherwise reproducible evidence rows and reusable derived datasets remain outside RP/Nexus durable storage under the existing temporary-data boundary. RPs store only identities, lineage, AI-authored scientific statements/state, and compact non-row result references needed to reconstruct the research history.

## Relationship to RD Decision Journal

The RP record and the exact RD decision transcript are distinct concerns.

- The RP is the structured scientific record of a coherent research line.
- An append-only RD decision journal is the forensic/audit transcript of complete AI decisions.

The RP model does not eliminate the need for an exact decision journal. Conversely, a decision journal alone is not a substitute for structured RP scientific memory.

## Non-Goals

This decision does not authorize deterministic scientific cognition, deterministic RP creation from semantic similarity, automatic question grouping, deterministic significance ranking, deterministic closure, or migration of abandoned B-series scientific-authority mechanisms.

Historical pre-v4 RP implementations may later be inspected only as a source of mechanical persistence or lineage techniques. They are not authoritative for this design.
