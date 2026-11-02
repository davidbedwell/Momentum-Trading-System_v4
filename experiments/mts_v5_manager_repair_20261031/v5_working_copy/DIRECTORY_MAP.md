# v5-alpha Directory Map

This tree mirrors ARCHITECTURE.md. Directories without implementation are intentional placeholders, not completed engines.

- engines/input — PIT data intake, earnings, corporate actions and account feeds
- engines/analysis — causal features, niches, regime and crash/recovery
- discovery/ga4_horizons, ga6, ga7, ga_hp, future — independent GA strategy discovery; GA-HP is the forward-facing name for GA6-H
- repository/chromosomes, adapters, schemas — versioned chromosome library and common proposal interfaces
- engines/opportunity — eligible proposals and shadow opportunities
- engines/portfolio_selector — shared-capital ranking and allocation
- engines/counterfactual_learning — feasible alternative portfolio replay and matured learning
- engines/risk, decision, execution — risk controls, order decisions and execution
- engines/accountability — portfolio ledger, NAV, benchmark and audit
- scientific_researcher/ai_council, experiments, hypotheses, validation — independent AI review and scientific testing
- governance — promotion, versioning, access and rollback
- control_center — operator visibility and monitoring
- research/archive/ga6_counterfactual_recovery — unmodified recovered GA6 research source files
- tests — original recovered GA6 counterfactual tests

The files under engines/*/legacy_reference are COPIES of original GA6 prototypes for component-level mapping. They are not yet native v5 modules; some still import ga6 and reference /opt/mts. Do not deploy or treat them as certified. Source archive is retained for provenance.

Baseline recovered tests: 3 passed against original ga6 imports. They do not yet validate the isolated v5 component copies.

- research_nexus — sole governed information repository (replaces Warehouse); Parquet, evidence, research and data contracts.
