# MTS v4 → v5-alpha Architecture Audit (Initial)
Date: 2026-10-27
Source: /opt/mts/thunder-migration/Momentum-Trading-System_v4
Status: Document/structure audit, not code-parity or operational certification.

## Source documents inspected
CHARTER.md, README.md, Architecture/SYSTEM_ARCHITECTURE.md, MTS_V4_SYSTEM_ARCHITECTURE.md, ENGINE_ARCHITECTURE.md, DECISION_ARCHITECTURE.md, DATA_ARCHITECTURE.md, ACCOUNTABILITY_ARCHITECTURE.md, Engines/RESEARCH_DIRECTOR_ARCHITECTURE.md, ANALYSIS_ENGINE_ARCHITECTURE.md, DATA_INTAKE_ENGINE_ARCHITECTURE.md (headings and selected content); Core/research_nexus/facade.py and bootstrap.py inspected earlier. Further full-text and implementation audit required.

## Component disposition
| V4 component | V5 disposition | Rationale |
| --- | --- | --- |
| Research Nexus | KEEP / REINTEGRATE | Sole persistent governed information system; replaces former Warehouse. Maintain publish/retrieve/query/verify and provenance. |
| Data Intake | KEEP / ADAPT | PIT, source quality, normalization, earnings, corporate actions, broker data; publish through Nexus. |
| Analysis Engine | KEEP / REFOCUS | Deterministic feature/market/regime analysis, statistical validation and shared computation; GA discovery consumes analysis, does not replace it. |
| Discovery / Market Discovery | EVOLVE | GA4/Horizons, GA6, GA7, GA-HP and future market/exchange GAs; pluggable discovery providers with shared interfaces. |
| AI Research Director | REDEFINE | Scientific Researcher + AI Council: hypotheses, anomalies, adversarial review, cross-GA/market connections; no unilateral promotion or live trade authority. |
| Research objective validator / Accountability | KEEP / EXPAND | Admission, reproducibility, lineage, validation gates and performance auditing; independent from proposer. |
| Decision Engine | EXPAND | Opportunity generation, shared portfolio selection, counterfactual learning, risk and execution boundaries. |
| Learning & Governance | KEEP / SEPARATE | Causal matured outcome learning vs immutable research/promotion rules and operator approval. |
| Task Manager / Orchestrator | RESTORE | Durable scheduling, dependency tracking, retries, concurrency, recovery and engine routing; must not become a trading decision-maker. |
| Control Center / observability | KEEP / EXPAND | Research and production visibility, data freshness, safety, deployment and performance. |
| Research cache | KEEP TRANSIENT | Explicitly nonauthoritative, rebuildable, not parallel durable data warehouse. |

## V5-specific missing responsibilities
- Strategy/chromosome repository and versioned adapters.
- Shared bankroll portfolio selector with competition, replacement and capital feasibility.
- Execution-equivalent portfolio counterfactuals, matured shadow outcomes and causal selector training.
- Defense controller, broker/order lifecycle, settlement and reconciliation.
- Paper/live separation, kill switch, permissions and versioned promotion.
- Extensible future GAs and AI reviewer model adapters.

## Architectural invariants to preserve
- Engines perform work; Research Nexus stores durable data/evidence/decisions/outcomes; Task Manager coordinates work.
- Nexus storage physical path independent of software Git checkout.
- Source-controlled code, durable Nexus data and transient caches are distinct persistence classes.
- Data has provenance, timestamps, point-in-time constraints, identity and validation state.
- Research, validation, production and human authorization are distinct boundaries.
- Scientific claims and real trading performance must be reproducible.

## Open audit work
- Read full original contracts and compare v4 code behavior, tests and service wiring.
- Inventory current GA6, GA7, GA-HP and selector dependencies and stores.
- Decide the canonical v5 package layout and service interfaces before moving implementations.
- Test Nexus publication/retrieval and Task Manager in an isolated v5 runtime.
- Resolve absolute CAGR target ambiguity (3% versus 35%).

## Decision status
This is a preliminary architectural audit and proposed disposition, not a final approved replacement architecture. Preserve current v5 modules and source archives while design is reviewed.
