# Momentum Trading System v4 — System Architecture

## Purpose

MTS v4 is a positive-admission reconstruction of MTS. It exists to discover reproducible market conditions that identify subsequent price movements with sufficient magnitude, directionality, timing, and path quality to be practically exploitable as trades.

The v4 architecture is governed by `ChatGPT.md`. This document translates those authority boundaries into a concrete software structure.

## Core authority model

Scientific authority belongs to the AI Research Director. Deterministic code owns execution contracts, safety, lineage, representation, persistence mechanics, and resource governance. Deterministic code may reject an invalid execution contract; it may not overrule a valid scientific judgment.

## Research flow

```text
External source
    |
    v
Intake Engine
    |
    v
Temporary Research Cache  <------------------------------+
    |                                                     |
    v                                                     |
AI Research Director                                     |
    |  explicit scientific request                       |
    v                                                     |
Objective Contract Validator                              |
    | valid request                                       |
    v                                                     |
Analysis Engine                                            |
    | governed analysis result                             |
    v                                                     |
AI Research Director -------------------------------------+
    |
    | promote only scientifically significant durable memory
    v
Research Nexus
```

When an RD request fails an objective execution contract, the validator returns a precise defect to RD. RD, not deterministic code, chooses the scientific repair.

## Components

### Intake Engine

Intake acquires and prepares evidence. It owns source identity, provenance, coverage, schema validation, normalization, neutral source semantics, and safe staging into temporary campaign storage. Intake does not interpret evidence scientifically.

### Temporary Research Cache

The cache holds raw or otherwise reproducible campaign evidence while active research needs it. It is intentionally distinct from Nexus. Cache entries are governed by explicit lifecycle state and may be discarded when no active research requires them and durable findings have been promoted.

### AI Research Director

RD is the first scientific actor. It chooses questions, hypotheses, methods, scientifically meaningful parameters, interpretation, next actions, significance, and research termination/continuation. RD may use Qwen, Sol, or another approved reasoning provider.

### Objective Contract Validator

The validator checks only mechanically decidable requirements: method existence, parameter presence/type/shape/cardinality, compatible artifact type, sample requirements, temporal mode, lineage references, permissions, and resource bounds. It cannot rank methods, invent missing scientific values, or determine scientific importance.

### Analysis Engine

Analysis exposes methods and executes the exact method requested by RD after objective validation. Analysis does not substitute a different method based on deterministic suitability judgments.

### Research Nexus

Nexus is durable research memory. It stores primarily ticker/subject metadata, significant RD-promoted findings, durable hypotheses/research state where needed, and lineage/relationships needed to understand those findings. Nexus shall not warehouse raw or otherwise reproducible market datasets.

### Orchestrator

The orchestrator is mechanical. It moves governed objects between components, requests RD repairs after objective validation defects, executes approved analysis, and publishes only RD-promoted durable memory. It does not select scientific direction.

## Durable versus temporary information

Temporary research cache may contain OHLCV, off-exchange prints, block-equity data, options data, normalized source tables, and analysis-ready derivative tables that are reproducible from source.

Nexus may contain subject identity, evidence metadata, provenance references, coverage summaries, significant findings, hypothesis state, applicability boundaries, contradiction state, research relationships, and compact lineage sufficient to understand/reacquire evidence.

A reproducibility recipe or source reference may be durable; the reproducible dataset itself is not.

## B-series disposition

RD-B1 through RD-B13 are historical experiments, not v4 architecture. No B-series module is admitted by lineage. Isolated code may be reused only when independently justified under v4 governance. Deterministic scientific cognition is not admitted.

## Initial v4 package

The new implementation lives under `MTS_V4/` while the historical v2 tree remains available for forensic comparison. This keeps the reconstruction auditable and makes a later move into a dedicated v4 repository straightforward.

The initial package provides:

- immutable governed research contracts;
- method-catalog and objective contract validation;
- temporary cache lifecycle;
- a narrow Nexus interface and in-memory reference implementation;
- AI Research Director provider protocol;
- analysis executor protocol;
- a mechanical research-loop orchestrator;
- authority-boundary tests.

Later migration of Intake, Analysis methods, Nexus persistence, provider integrations, and production orchestration must conform to these interfaces rather than importing old B-series scientific authority.
