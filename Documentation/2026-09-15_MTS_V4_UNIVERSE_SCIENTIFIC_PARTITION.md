# MTS v4 Universe Scientific Partition and Compact Transfer Boundary

Status: HUMAN-APPROVED — 2026-09-15

## Decision

The Nexus-owned derived market store may contain the complete eligible universe. Scientific access to historical outcomes must remain partitioned so universe research does not consume every member as a future blind-verification subject.

Contemporaneous predictor-time market context may use the complete universe for ranks, percentiles, breadth, sector state, volatility state, and other point-in-time measurements. Context contribution alone is not historical outcome exposure.

Before historical universe outcomes are supplied to an AI Research Director, stable security identities must be assigned once to exact-size cohorts using a frozen deterministic partition. Cohort sizes are explicit human governance inputs. Deterministic code has no default allocation and does not rank securities scientifically.

The initial roles are:

- `DISCOVERY`: historical outcomes may be used during EXPLORATION;
- `VERIFICATION_A`: reserved for a later locked-hypothesis blind-verification path;
- `VERIFICATION_B`: reserved for a later independent or materially revised-hypothesis verification path.

The existing universe discovery runner may expose only `DISCOVERY` outcomes. It must fail closed when historical outcomes are requested without a frozen partition manifest. It cannot expose either verification cohort.

Campaign exposure is recorded separately as:

- `CONTEXT_ONLY`;
- `DISCOVERY_OUTCOME_EXPOSED`;
- `BLIND_VERIFICATION_EXPOSED`;
- `SUBJECT_RESEARCHED`.

No administrative label may preserve a security as historically unseen after its outcome contributed to hypothesis formation. Conversely, a security does not become outcome-exposed merely because its predictor-time value contributed to a market denominator, rank, or breadth statistic.

## Compact local transfer

The complete derived market store remains on the server and is not transferred into the local Nexus at campaign closeout.

The compact campaign export may contain:

- Research Nexus scientific metadata and findings;
- Research Packages;
- compact Analysis batch reports and AI decisions;
- scientific context and lineage;
- scientific exposure ledger;
- run and spend summaries.

The export mechanically excludes:

- derived-market Parquet files and store manifests;
- raw or reacquirable market data;
- campaign Analysis cache datasets;
- AI transport telemetry and replay envelopes.

The server-derived store remains independently maintainable and reusable. Local Nexus preserves what MTS learned and the metadata necessary to interpret that learning, not the complete market-state corpus used to produce it.

## Remaining verification work

This change reserves verification capacity; it does not fabricate a blind-verification runner. Before either verification cohort is opened, a separate path must prove that the hypothesis and success definition were locked before hidden outcomes became accessible, consume only the authorized cohort, record that exposure durably, and prevent reuse as an unseen cohort.
