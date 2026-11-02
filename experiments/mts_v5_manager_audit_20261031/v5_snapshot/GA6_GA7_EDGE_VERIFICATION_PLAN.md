# GA6/GA7 Edge Verification — MTS v5 Trading Engine
Date: 2026-10-27
Status: Evaluation plan; no production deployment authorized.

## Central falsifiable question
Do GA6 or GA7 contain a repeatable net trading edge that survives matched execution, shared capital, costs, risk controls and independent validation? If not, stop rather than expanding platform engineering.

## Existing evidence (not certification)
GA7 final gen518 report: 12,431 recoverable unique chromosomes replayed on DEV79 2009–2018; 142 preliminary portfolio-risk survivors, 0 meeting CAGR >=35% and MDD <=20%; max portfolio CAGR 17.79%; missing checkpoints generations 1–9; DEV87 not used. GA6/GA7 selector research summary: 400 GA6 chromosomes, best reported CAGR 24.13%; GA6 EV entry-equity fractional return and GA7 EV R-multiple not directly comparable. GA7 portfolio replay not certified against GA6 execution parity.

## Minimal trading engine required before edge verdict
1. Immutable standardized chromosome signal adapter with symbol, signal timestamp, order earliest-next-open, direction, horizon, exits, sizing, provenance and eligibility.
2. Causal market/earnings/defense state inputs with PIT and timestamp audit.
3. Common daily event-driven replay for both GAs, using identical price basis, fills, slippage, commissions, cash, ownership, mark-to-market NAV, corporate actions, defense and earnings restrictions.
4. Feasible one-bankroll selector with position caps (10% symbol during learning), risk-per-trade (1–2%), sector/correlation exposure, cash/SGOV option, hold/add/reduce/exit and competing opportunities.
5. Trade-level and portfolio-level ledger, benchmark, exposure, concentration, drawdown attribution, statistical confidence and reproducibility manifests.
6. Causal counterfactuals and shadow outcomes, trained only after maturation; no tuning on proof.

## Sequential stop/go gates
A. **Integrity:** independently verify data coverage, PIT, chronology, fills, cash/NAV and exact signal replay parity. Failed integrity -> fix before inference.
B. **Discovery evidence:** deduplicate behaviors; positive net expectancy with uncertainty and sample adequacy; no future leakage; evaluate stability by regime, ticker, time and costs. Failure -> no validation promotion.
C. **Matched portfolio:** replay predeclared GA6/GA7 candidates with identical constraints and benchmarks. Determine edge vs market, SGOV and simple momentum baseline; attribute edge to signals vs capital/market exposure.
D. **Freeze:** choose candidates and selector rules using discovery only, hash code/data/config, then run untouched DEV87 once. Never select or tune using DEV87.
E. **Decision:** GO only for independently supported risk-adjusted, cost-adjusted edge with feasible turnover/exposure. CONDITIONAL for promising but uncertain. STOP for no positive transferable edge; preserve negative findings in Nexus.

## Immediate engineering sequence
- Inventory existing GA6 and GA7 chromosome definitions, event ledgers, source data and report schemas.
- Build/verify adapter and common event replay contract.
- Validate replay on a small deterministic fixture and reconcile to both GA accounting conventions.
- Run discovery-only matched comparison, then decide if independent proof is warranted.

No modification of active GA6/GA7 runs or heldout data is authorized by this plan.

## Governing benchmark decision (2026-10-27)
The primary investment alternative is $100,000 invested in SPY at the same starting date and held through the identical ending date with distributions reinvested. MTS starts with $100,000, has one shared bankroll and is marked to market daily. Account for realistic fees, slippage, dividends, corporate actions, idle cash/SGOV, and financing assumptions consistently. Use identical price calendars and report terminal wealth, CAGR, MDD, volatility, exposure, and excess return over SPY. The primary economic test is net ending wealth above SPY; risk-adjusted performance and statistical stability are essential secondary decision criteria. Do not force a 35% CAGR as the discovery gate. No result counts as a validated edge until chronological independent out-of-sample proof, after candidate/rule freeze. If MTS loses to SPY, retain that as a valid scientific outcome and stop unnecessary platform expansion.

## Third benchmark: SPY with crash defense (2026-10-27)
Add a distinct portfolio: $100,000 invested in SPY under Normal regime; apply the existing A_v2/B/B1/C defense controller and R-1 recovery controller without GA entry/exit signals. When any defense trigger activates, exit SPY no earlier than the next executable open; hold cash/SGOV according to the original controller and account for yield and trading costs; reenter at next executable open on R-1 recovery. Preserve the exact defense state-machine semantics and version its configuration; do not silently reimplement a simplified proxy. Replay alongside (1) SPY buy-and-hold and (2) GA6/GA7 MTS portfolios with identical date range, starting capital, price basis, transaction cost assumptions and daily NAV accounting. Report the incremental economic value of defense versus passive SPY, and of active MTS signals versus defense-only SPY. Audit lookahead and trigger/transition timing before treating outcomes as evidence. Do not touch untouched validation data before freeze.

## Clarification: Defense applies to BOTH active and defense-only portfolios
Portfolio 1: SPY buy-and-hold, no defense.
Portfolio 2: SPY with A_v2/B/B1/C + R-1 defense, no GA stock-selection signals.
Portfolio 3: MTS GA6/GA7 active trading WITH the SAME A_v2/B/B1/C + R-1 defense controller and transition/execution rules as portfolio 2.
This is essential to isolate the incremental value of GA selection/portfolio management beyond defense. Both defended portfolios must share identical historical defense-state timeline and capital parking assumptions, except where differences are inherent in their holdings. Report 3-2 as incremental active-trading value; 2-1 as defense value; 3-1 as total MTS value. No defenseless MTS in the primary three-way comparison.
