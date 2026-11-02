# First-year manager engineering report

Date: 2026-10-28. Branch: `codex/first-year-manager` (already present on entry).

**Readiness: BLOCKED / NOT LAUNCH READY.** No four-family first-year performance,
edge, profitability, or execution certification is claimed. A complete runnable
four-family manager was not achieved. The launch preflight intentionally exits 2.

## Architecture and dependency inspection

Read the approved architecture, implementation audit, native producer contracts,
portfolio kernel, calibration, ownership, shadow accounting and evolutionary
modules before implementation. Inspected authentic external GA4 factory,
GA5/GA6 decision implementations, GA7 request replay, frozen catalogue records,
and synthetic Parquet schemas. External sources were read directly, not copied
or replaced. SQLite inspection used `mode=ro`.

Actual environment: Python 3.12 virtual environment at `/opt/mts/.venv/bin/python`;
numpy 2.5.4, pandas 3.0.6, pyarrow 26.0.0, pytest 9.1.1. The source audit found
250,110 GA4_DIAGNOSTIC records, 31,750 HORIZONS records and 261,958 GA6
chromosomes. Counts establish availability, not eligibility or quality. No
chromosomes were fabricated, selected on synthetic future returns or evolved
in an external research run.

`FIRST_YEAR_PREFLIGHT.json` contains exact dependency paths, sizes, counts and
remaining gates. Ordinary sandbox access cannot traverse
`/opt/mts/thunder-migration`; authorized read-only elevated execution resolved
that access issue. No permissions, credentials or source files were changed.
Git metadata is also read-only in the ordinary sandbox, so local commits used
authorized elevated execution.

## Completed changes

- Added `first_year_features.build`: reads only a bounded OHLCV/sector prefix
  before invoking the authentic GA4 stock-local and cross-sectional factory.
  Preserves original feature definitions and existing tanh aliases; excludes
  simulator regime labels; rejects invalid prices, duplicates, changing sector
  mappings and requests exceeding 504 sessions or 500 tickers. This is a
  synthetic research adapter, not historical PIT certification. Ticker subsets
  are explicitly smoke inputs, not full-universe research panels.
- Added bounded manager evolution over the causal shared-capital replay:
  2–16 genomes, 1–5 generations, at most 252 replay sessions. Fitness uses
  observed NAV growth and negative maximum drawdown, including initial $100k.
  Only training fitness selects the winner; validation freezes that genome,
  carries the replay prefix forward, scores the later interval and rejects
  changes to prefix decisions, fills or NAV. Reports indistinguishable fitness
  honestly. Each evaluation requires a fresh caller-supplied factory/book.
  No four-family evolutionary experiment was run.
- Prevented calibrated rival chromosomes from managing an incumbent position.
  Horizons now obtains previous weights from its own executed holdings.
- Extended independent shadow accounting through ENTER/ADD/REDUCE/EXIT,
  including fees, weighted average basis, capital from additions, partial
  realizations, split adjustments and dividends. Outcomes mature only on full
  liquidation. Shadow targets represent proportional units and returns on
  cumulative invested capital; they do not reproduce shared-capital feasibility.
- Allowed HOLD/REDUCE on appreciated exposure up to 100%, while preserving
  the 30% order contract for new risk. GA7 no longer fails or trims merely
  because appreciation carries a holding above the order cap. Shared replay
  retains its $100k bankroll and 10% initial entry cap; increases above 10%
  still require existing evidence/risk gates, not fabricated permission.
- Reconciled split-adjusted filled shares and fee-inclusive basis in the manager
  book. Rejected nonfinite market prices/dividends/splits and invalid fees.
- Deferred native GA6 imports until evaluation so pure policy and injected
  evaluator tests do not require legacy archive access.
- Added an executable read-only preflight with explicit blocking status, local
  output restriction, authentic source checks and dependency versions.

## Validation and failures

Final full bounded suite:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest \
  --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
```

**297 passed in 2.50 seconds**, with read-only elevated access to external
research imports. Earlier ordinary-sandbox runs failed during GA6 schema import
with PermissionError and then had one legacy Nexus import failure. These were
access failures; the final elevated suite passed without bypassing those tests.

Added regression checks for ownership, fee cashflow identity across shadow
adds/reductions/exits, split attribution, appreciated holdings, nonfinite
prices, initial-capital drawdown and chronological validation integrity.
Accounting/genome fixtures are explicitly test inputs, not research evidence.

Authentic feature smoke: actual `STK_0000` and `STK_0001` bars from the supplied
synthetic dataset; six-session prefix versus eight-session build. The 12 prefix
rows matched exactly, with 149 output columns. This small-prefix check passes;
it does not establish long-lookback or 500-ticker parity. No portfolio smoke
performance or differentiated manager fitness is claimed.

Elevated launch preflight completed with the **expected exit code 2** and wrote
`FIRST_YEAR_PREFLIGHT.json`. That is a blocked readiness check, not success of
a manager launch.

## Blocking dependencies and unfinished engineering

1. The supplied synthetic market index has Date/OHLCV/Volatility/Regime/Quarter,
   without VIX, VVIX, funding or credit observations/publication timestamps.
   Existing Horizons reconstruction explicitly requires those dated inputs.
   Inventing or zero-filling them would violate the research contract. A governed
   compatible stress input dataset or an explicitly validated alternative
   research contract is needed before the four-family launch can be honest.
2. GA4 daily code emits entries only; authentic held-position exit/horizon
   behavior must still be connected. Entry predicates cannot stand in for exits.
3. GA6 authentic candidate/position bridge is not connected to a complete
   synthetic four-family daily stream. GA7 needs archived genome loading and
   feature-definition/scaling parity against the selected native implementation.
4. Rejected candidates need independent native shadow held-state decisions.
   Calling native producers only with actual portfolio holdings cannot generate
   their genuine shadow exits; the enhanced accounting book alone does not
   solve calibration bootstrap. The existing replay also calibrates action
   proposals from entry-context returns; these are not independently validated
   incremental action utilities.
5. Certified settlement/available-cash accounting, causal defense event timing,
   PIT eligibility and earnings controls, aggregate risk/correlation controls,
   corporate-action parity and independent full-ledger reconciliation remain
   required. Passing component tests do not certify these controls.
6. A complete dated source manifest, full-universe/long-history feature parity,
   differentiating four-family fitness, frozen chronological validation and
   untouched proof evaluation have not been produced. No sealed proof set was
   opened. The evolution API is tested integration scaffolding, not a supplied
   authentic launch dataset or full four-family runner.

## Launch command

The available executable command is the readiness preflight:

```bash
cd /opt/Momentum-Trading-System_v5-alpha
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.first_year_launch \
  --output FIRST_YEAR_PREFLIGHT.json
```

It requires read access to the authentic archives and intentionally exits 2.
**There is no valid full manager launch command yet.** Do not treat the
preflight or generic evolution API as a launch-ready manager.

All changes are local. No push, merge, full-scale experiment, external cost,
secret modification, brokerage action or live-system change was performed.
Original datasets, source modules and GA runs under `/opt/mts` were preserved;
external imports ran with bytecode writes disabled. No external research
scripts with default output paths were executed.

Local implementation commits:

- `1d9916d` — causal manager evolution, shadow additions and filled ownership.
- `ec5b699` — authentic feature build, blocked launch preflight and accounting/
  chronological regression checks.

This report and the captured preflight are committed in the subsequent local
documentation commit. No approval to push or merge has been requested or used.
