# Momentum Trading System — Research Nexus Retrieval Contract

**Status:** Initial Canonical Contract  
**Contract ID:** `mts.contract.research-nexus-retrieval`  
**Version:** 1

## Purpose

Defines identity resolution and governed discovery for the first Research Nexus implementation.

## Governing Rule

> Retrieval resolves governed identity and meaning. Clients do not reconstruct canonical state from directories or backend keys.

## Direct Resolution

`get(artifact_id, artifact_version)` or equivalent resolves one governed artifact version and returns its governed descriptor/reference and available representations as authorized.

Clients do not need payload directories, database row IDs, SQLite keys, filesystem shards, or backend object keys.

## Governed Query

The initial `query(...)` surface supports the predicates actually required by the vertical slice, including artifact identity/type, lifecycle, persistence/retention class, producer, schema identity/version, governed instrument/context references, validation state when implemented, tags, and creation time.

Query returns governed references/descriptors, never raw storage rows as the domain contract.

## Selective Retrieval

Potentially large evidence/finding collections must support bounded predicate-based retrieval as index capability is implemented. Consumers must not be forced to materialize complete large publications to inspect matching records. Unbounded result surfaces require deterministic bounds and pagination/cursor semantics.

## Temporal and Lifecycle Semantics

Retrieval preserves current vs superseded, publication vs promotion, lifecycle vs ranking, and scientific status vs access priority. Retained historical versions remain directly resolvable.

## Backend Independence and Failure

Changing catalog, index, or payload backend does not change logical identity or public retrieval semantics. Retrieval distinguishes not-found, incompatible descriptor/schema, missing representation, integrity failure, and storage unavailable. Missing/corrupt canonical state never silently falls back to an ungoverned location.
