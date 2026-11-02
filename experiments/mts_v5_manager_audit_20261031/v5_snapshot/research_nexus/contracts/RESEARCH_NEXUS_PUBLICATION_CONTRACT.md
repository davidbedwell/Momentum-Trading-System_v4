# Momentum Trading System — Research Nexus Publication Contract

**Status:** Initial Canonical Contract  
**Contract ID:** `mts.contract.research-nexus-publication`  
**Version:** 1

## Purpose

Defines the minimum client-visible semantics of governed Research Nexus publication without prescribing database tables, filesystem paths, serialization, or engine implementation.

## Governing Rule

> Publication admits a governed artifact into the Research Nexus. It does not certify scientific truth, promotion, currency, ranking, or Decision eligibility.

## Semantic Input

A publication request supplies:

- proposed artifact metadata conforming to `mts.artifact-envelope` v1;
- an artifact payload/representation when required by the artifact-specific schema;
- a resolvable artifact-specific schema identity/version;
- provenance sufficient for that artifact type;
- producer identity sufficient for authority evaluation;
- any required governed relationships.

The envelope and payload are **composed semantic parts**, not an inheritance hierarchy. The payload schema does not redefine common envelope fields.

Server-managed representation facts such as physical locator and computed content hash are not client semantic identity and are registered by publication/integrity services.

## Required Behavior

From the client perspective publication SHALL:

1. validate identity and producer authority;
2. validate envelope and artifact-specific payload schema;
3. validate required provenance/references;
4. stage/serialize the representation where applicable;
5. compute representation content hash;
6. reconcile existing identity/version for idempotency/conflict;
7. persist the durable representation;
8. atomically register canonical metadata, representation, and required relationships;
9. verify the committed publication;
10. return a stable artifact reference.

An incomplete publication MUST NOT become visible as successfully published.

## Idempotency and Conflict

For one artifact identity/version:

- identical immutable content MAY reconcile to the existing publication;
- conflicting immutable content MUST fail closed;
- materially new meaning/content requires governed new version/identity/supersession;
- silent overwrite is prohibited.

Retry after ambiguous completion MUST reconcile before creating anything new.

## Authorization

A producer may publish only artifact types authorized by its governed capability/engine contract. Technical write access is not authority.

## Output

Successful publication returns at least:

- `artifact_id`;
- `artifact_version`.

Backend row IDs, filesystem paths, filenames, and physical object keys are excluded from semantic identity.

## Audit and Failure

Material publication results are append-auditable. Publication fails explicitly for unresolved schema, invalid structure, missing required provenance, unauthorized producer/type, immutable conflict, invalid controlled vocabulary, unavailable durable storage, or failed integrity verification. Failure MUST NOT create or use a silent alternate canonical store.
