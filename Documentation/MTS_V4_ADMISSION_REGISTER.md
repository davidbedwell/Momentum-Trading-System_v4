# MTS v4 Positive-Admission Register

This register records what is allowed into v4 and why. It is intentionally organized by responsibility rather than RD-B revision number.

## Admitted foundation

### Governance and architecture
- `ChatGPT.md` — authoritative v4 governance.
- `Architecture/MTS_V4_SYSTEM_ARCHITECTURE.md` — concrete authority-preserving architecture.

### New v4 implementation
- `MTS_V4/contracts.py` — governed immutable research contracts.
- `MTS_V4/method_catalog.py` — objective method existence/execution metadata only.
- `MTS_V4/validation.py` — objective contract validation; no scientific ranking or substitution.
- `MTS_V4/cache.py` — temporary reproducible-evidence storage boundary.
- `MTS_V4/nexus.py` — narrow durable research-memory interface; no raw-dataset publication API.
- `MTS_V4/interfaces.py` — AI RD scientific-authority and exact Analysis execution protocols.
- `MTS_V4/orchestrator.py` — mechanical RD → validate → Analysis → RD loop.

## Historical v2 components approved in principle for later inspection/adaptation

These are not yet transplanted merely because they are listed here.

- Intake acquisition, provenance, schema, normalization, and neutral evidence semantics.
- Analysis scientific/mathematical implementations.
- Analysis method catalog metadata that describes objective execution contracts.
- Research Nexus persistence mechanics for metadata/findings/lineage, provided reproducible datasets are excluded.
- task scheduling and orchestration that is purely mechanical.
- canonicalization, hashing, immutable IDs, provenance, lineage, temporal-integrity enforcement.
- cache/resource lifecycle machinery.
- OpenAI-compatible/Qwen provider transport and parsing infrastructure, provided scientific authority remains with AI.
- durable restart/reconstruction mechanics for research memory, provided deterministic cognition is not reconstructed as authority.

## Explicitly not admitted

The following concepts do not enter v4 as scientific authority:

- deterministic salience or scientific relevance judgments;
- deterministic hypothesis generation;
- deterministic candidate-question generation;
- deterministic scientific-value scoring;
- deterministic question ranking/selection;
- deterministic method suitability/ranking/selection;
- deterministic scientific critics;
- deterministic convergence/evidence-sufficiency judgments;
- deterministic scientific specification resolution/refinement/discrimination;
- deterministic scientific continuation or parent-resume decisions;
- any mechanism that changes what science RD asked to perform because deterministic code prefers another scientific choice.

## Nexus admission boundary

Admit durable ticker/subject metadata, significant AI-RD-promoted findings, durable hypothesis/research state where useful, lineage, provenance references, relationships, applicability/exception information, and unresolved issues that materially affect later research.

Do not admit raw or otherwise reproducible market datasets as durable Nexus content. A source identity or reproducibility recipe may be durable; the dataset itself belongs in temporary research storage.

## Admission test

For every candidate component, answer:

1. Does it support the v4 mission?
2. Is its authority objective/mechanical, or does it make a scientific judgment?
3. If it makes a scientific judgment, is that judgment authored by the AI Research Director?
4. Does it preserve the temporary-data versus durable-Nexus boundary?
5. Can its behavior be proved with an authority-boundary test?

A historical component failing these tests is not transplanted. If it contains useful mechanics, extract only those mechanics behind a v4 interface.
