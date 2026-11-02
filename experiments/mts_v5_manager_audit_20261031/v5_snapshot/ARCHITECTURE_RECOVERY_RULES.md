# Architecture Recovery Rules — MTS v5-alpha
Date: 2026-10-27
Status: Approved direction; recovery in progress, not a certified integrated system.

## Non-negotiable boundaries
1. **Research Nexus replaces Warehouse.** It is the sole governed information repository for raw ticker Parquet files, datasets, measurements, evidence, knowledge, validation, registry and archive; its API publishes, retrieves, queries and verifies artifacts. No separate Warehouse. Engines use Nexus contracts.
3. **Strategy Repository** stores immutable versioned chromosome definitions, adapters and eligibility metadata; not raw ticker Parquet data. GA4/Horizons, GA6, GA7, GA-HP (formerly GA6-H) and future GAs publish through the common interface.
4. **Engines** own their logic: input, analysis, opportunity, portfolio selector, counterfactual learning, risk, decision, execution, accountability. Do not put executable modules in root, research/archive, or the data repository.
5. **Scientific Researcher / AI Council** maintains hypotheses, experiments, critical review and reproducible evidence; cannot silently change live rules.
6. **Governance** controls promotion, freeze, rollback, PIT and walk-forward boundaries. Production is isolated from discovery.
7. **Data migration** is inventory -> compare hashes, dates, schema, coverage and PIT quality -> select authority -> register/alias -> verify consumers -> deprecate redundant stores. Do not bulk copy 4,967 ticker files without this process.
8. **No execution claims without tests.** Existing GA6 research modules are not a complete portfolio replay or certified broker execution.

## Recovery progress
- Project tree and component ownership established.
- GA6 counterfactual/selector modules imported into corresponding v5 engines, with source copies archived.
- Research Nexus is the sole information repository; the erroneous empty Warehouse tree was removed.
- Original v4 Research Nexus architecture, technical design and publication/retrieval/relationship contracts recovered under research_nexus/contracts.
- Original v4 Nexus code still exists at /opt/mts/thunder-migration/Momentum-Trading-System_v4/Core/research_nexus; not yet ported or integrated.
- Existing GA-HP Parquet store: /opt/mts/ga6_h/data/prices (4,967 files observed).
- Reconstructed v4 Parquet store: /opt/mts/thunder-migration/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance (503 files observed).
- No dataset has yet been declared authoritative.

## Required next gate
Inventory source stores and current consumers; recover Nexus implementation and contract tests in isolation; build a canonical dataset registry with checksums and provenance; connect Input Engine and a single read path; verify parity before changing GA6, GA7 or GA-HP workflows.
