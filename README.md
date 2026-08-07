# Momentum Trading System v2

Momentum Trading System (MTS) v2 is the clean implementation of the Momentum Trading System architecture.

The authoritative statement of the project's purpose, mission, vision, and governing principles is:

**[CHARTER.md](CHARTER.md)**

## Architectural Model

MTS is organized around three fundamental responsibilities:

**Engines perform work.**

**The Research Nexus preserves and connects durable state.**

**The Task Manager schedules, routes, and supervises work.**

No individual engine owns the Research Nexus.

## Planned Core Components

- Data Intake Engine
- Discovery Engine
- Research Director
- Market Discovery Engine
- Decision Engine
- Learning & Governance
- Research Nexus
- Task Manager

These component names describe the current architectural direction. Detailed responsibilities and contracts are governed by the architecture rather than this README.

## Repository Organization

- `Architecture/` — system structure, component architecture, and architectural decisions
- `Governance/` — standards, contracts, schemas, policies, project management, and utilities
- `Core/` — shared MTS software including Research Nexus services, task management, configuration, messaging, and observability
- `Engines/` — independently bounded work-performing components
- `Tests/` — unit, contract, integration, and end-to-end validation
- `Control-Center/` — operational control and system visibility
- `Documentation/` — explanatory and supporting documentation

## Research Nexus

The Research Nexus is the canonical persistent system of record and exchange for MTS data, evidence, findings, knowledge, research state, decisions, outcomes, policies, and provenance.

Research Nexus durable data does **not** live inside the Git repository.

Its physical location is deployment configuration.

This allows the same MTS software to operate with locally attached storage, external storage such as Drobo, network storage, or future server infrastructure without redesigning the engines.
