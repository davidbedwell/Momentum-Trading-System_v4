# Momentum-Trading-System_v5-alpha — Approved Architecture
Status: Architecture approved; implementation not yet integrated or certified.
Location: /opt/Momentum-Trading-System_v5-alpha
Date: 2026-10-27

## Mission
Build an extensible scientific trading platform that converts validated, independent genetic-algorithm (GA) trade discoveries into portfolio-level decisions. Chromosomes propose trades; the selector owns shared capital; portfolio results determine success. This document records the approved target architecture, not a claim of completed implementation.

## Architecture and responsibilities
1. **Input Engine** — Point-in-time historical/live market data, constituent membership, earnings calendars, corporate actions, brokerage/account state, quality controls, timestamps and lineage.
2. **Research Nexus** — The single governed information repository, replacing Warehouse. Stores ticker Parquet data, research evidence, datasets, knowledge, lineage and publication/retrieval interfaces.
3. **Analysis Engine** — Causal indicators, market breadth, volatility, technical features, daily niche identification, cross-sectional features, regime analysis, and defensive A/B/B1/C with R-1 recovery. No future data at decision time.
3. **Extensible Discovery Ecosystem** — GA4/Horizons, GA6, GA7, **GA-HP (formerly GA6-H)**, and future GAs for NAS100, other exchanges, and new trade behaviors. GA-HP specializes in high-performing stocks and is architecturally independent of GA6. Each GA evolves/evaluates trade behavior, not independent portfolio allocation targets.
4. **Versioned Chromosome/Strategy Repository** — Persist immutable genome definitions, family, market/universe scope, signal/exit interfaces, trade-level evidence, lineage, validation eligibility, execution assumptions, provenance and de-duplication. Admit new GAs via standardized adapter, not a rewrite of MTS.
5. **Opportunity Engine** — Generate dated, executable entry/exit/scale/hold proposals from eligible chromosomes with estimated payoff, risk, confidence, signal timestamp, eligibility and ownership; evaluate all eligible proposals in shadow.
6. **Portfolio Selector and Counterfactual Learner** — One shared bankroll across all strategies. Rank competing opportunities and decide allocations, replacement, holds, scaling, cash/SGOV, and concentration/correlation constraints. Record accepted/rejected candidates and feasible alternatives; replay counterfactual portfolios under identical cash, position, costs, timing, and execution constraints. Learn only after outcomes mature; use chronological walk-forward folds and untouched proof sets. Marginal portfolio contribution is evaluated here, not used as a chromosome discovery gate.
7. **Risk, Decision and Execution Engines** — Defense veto/liquidation and recovery, portfolio and trade risk budgets, position ownership, next-open fills, realistic fees/slippage, earnings embargo, point-in-time membership, settlement, corporate actions, broker reconciliation, emergency stop, paper trading before live trading.
8. **Portfolio Ledger and Accountability** — Immutable decisions, signals, orders, fills, NAV, realized and shadow outcomes, alternative decisions, cash, costs, drawdown, benchmark, audit/replay lineage, alerts and failure handling.
9. **Scientific Researcher + AI Research & Intelligence Council** — Independent hypothesis generation, anomaly detection, cross-market/GA relationships, critical review, adversarial checks, experiments, reproducibility, evidence grading and persistent hypothesis memory. Potential reviewers: ChatGPT, Claude, Astra, Grok, others. Research cannot silently alter live rules; promotion requires governance, tests and rollback.
10. **Governance / Control Center** — Configuration versions, evidence gates, experiment isolation, approved promotion/rollback, monitoring, operator visibility and access control.

## Portfolio performance objectives
- CAGR > 1.5 × absolute maximum drawdown (both expressed in matching percentage units).
- Annualized MTS CAGR target: greater of an **absolute threshold awaiting clarification** (user said 3%, possibly 35%) and SPY CAGR + 20 percentage points, evaluated over identical periods and with realistic costs.
- Report CAGR, MDD, Calmar, turnover, capital utilization, tail risk, regime/fold stability, and SPY-relative returns. Objectives are research targets, not promises.
- GA-level selection remains trade-quality/diversity based; do not impose portfolio CAGR/MDD gates on chromosome discovery.

## Implementation boundaries and preservation
- Preserve existing v4 Input/Analysis/Discovery/Decision/Research-Director/Learning-Governance/Accountability architecture where useful, after interface and behavior audit.
- Reuse GA6 counterfactuals.py, portfolio_counterfactuals.py, shadow ledger, shared selector contract and existing MTS daily selector as candidate foundations; existing research prototypes are **not** certified execution-equivalent portfolio replay.
- Preserve GA6, GA7 and GA-HP research and their frozen evidence; do not rename or mutate original GA6-H artifacts in place. Use GA-HP as forward-facing canonical identity with alias GA6-H for provenance.
- NAS100 and other exchange discovery must support historical constituent membership and out-of-sample testing; OmniFunds reconstruction (OF-RE) is a distinct research experiment.
- No real brokerage orders until certified replay, paper-trading parity, risk controls and explicit operator approval.
- Separate development from live operations; no unapproved AI-generated trading changes.

## Initial build sequence
A. Inventory and map existing v4 and GA modules to target interfaces; document reuse/gaps.
B. Establish isolated versioned v5-alpha project and GA-HP alias/adapter contract.
C. Integrate opportunity proposals, shared-capital simulator, full shadow ledger and feasible portfolio counterfactuals.
D. Test causal replay, execution parity, risk, earnings/membership and defensive controls.
E. Walk-forward compare selector against transparent allocation baselines, with untouched proof evaluation.
F. Paper-trading integration and broker reconciliation; live trading only after explicit authorization.

## Naming
Project: Momentum-Trading-System_v5-alpha.
High-performer discovery GA: GA-HP (formerly GA6-H).
GA6 and GA7 remain independent strategy-discovery families; future GA names remain open.
