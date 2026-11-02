# Momentum Trading System — Research Nexus Relationship Contract

**Status:** Initial Canonical Contract  
**Contract ID:** `mts.contract.research-nexus-relationship`  
**Version:** 1

## Purpose

Defines governed relationship registration and traversal across MTS identity domains.

## Governing Rule

> Relationships connect governed identities. Filesystem proximity never implies lineage, support, contradiction, dependency, applicability, or authority.

## Relationship Record

A relationship conforms to `mts.relationship` v1 and contains:

- `source_ref`;
- `relationship_type`;
- `target_ref`;
- `created_at`;
- `producer`.

Endpoints use `mts.governed-reference`, so valid edges may connect artifacts to artifacts or, where the relationship meaning requires it, to tasks, executions, instruments, capabilities, policies, and other governed identity domains.

## Vocabulary

Initial types are `DERIVED_FROM`, `SUPPORTS`, `CONTRADICTS`, `SUPERSEDES`, `INVALIDATES`, `DEPENDS_ON`, `ANSWERS`, `TESTS`, `GENERATED_BY`, `REQUESTED_BY`, `USED_IN_DECISION`, `PRODUCED_OUTCOME`, `APPLIES_TO`, and `REQUIRES_CAPABILITY`.

New meanings require governed vocabulary/schema evolution rather than ad hoc strings.

## Endpoint Integrity and Traversal

Both endpoints must be valid governed references and resolvable when the applicable contract requires resolution. The Nexus supports traversal in both directions. A graph database is not required.

## Dependency Protection

`DEPENDS_ON` and provenance-relevant relationships participate in retention/deletion checks. Required durable dependencies cannot be deleted merely because they are cold, low-ranked, or inconvenient to retain.

## Audit

Material relationship changes are auditable. Corrections do not silently rewrite historical relationship meaning.
