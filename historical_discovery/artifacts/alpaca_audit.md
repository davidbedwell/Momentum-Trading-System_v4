# Alpaca capability and credential-presence audit

Audit date: 2026-10-30 UTC. Scope: audit only, following ALPACA_DATA_DIRECTIVE.md and the user's narrower instruction. This report is the only file written by this audit. No acquisition implementation, SDK installation, account mutation, universe download, or backtest was performed. No 2010–2011 outcome labels were accessed.

## Decision

**Alpaca is not a validated source for point-in-time 2005–2011 issuer financial statements.** No income-statement, balance-sheet, cash-flow, or historical filing/release-timestamp endpoint was identified in the current official documentation reviewed. Its documented market-data capabilities include bars, trades, quotes, corporate actions, and news. Bars and news must not be classified as financial statements.

This is a documentation-based capability finding, not a successful authenticated account test. Actual account authorization, subscription, special entitlements, and historical response coverage remain **unverified** because credentials were not loaded and direct API probes failed at the transport layer. Do not interpret transport failure as an empty dataset, invalid credentials, or empirical proof that a private endpoint cannot exist.

## Credential presence and runtime

| Check | Observation | Limit |
| --- | --- | --- |
| Process environment names containing ALPACA or APCA | None present | Does not exclude credentials elsewhere or proxy injection |
| Repository-root `.env`, `.env.local`, `.env.alpaca` | Absent | No broad secret-file search performed |
| Default credential selector in `ga9/alpaca_repair.py` | `/root/.config/mts/alpaca.env` | Existing code inspected read-only; not executed or imported |
| That default credential file | Present, checked by filesystem metadata only | Contents were not read; individual key/secret presence, nonemptiness, and validity unverified |
| Credential names recognized by existing loader | `APCA_API_KEY_ID` / `ALPACA_API_KEY`; `APCA_API_SECRET_KEY` / `ALPACA_SECRET_KEY` | Names only; no values inspected or exposed |
| Python packages in current `python3` interpreter | `requests` available; `alpaca` and `alpaca_trade_api` absent | Other environments not inspected; standard-library HTTP remains possible |
| Managed runtime readiness | `environment_status` tool unavailable; `/etc/codex/network-policy.json` absent | Current network policy and managed secret readiness could not be established |

No secret values, account identifiers, headers, response bodies, or environment dumps were printed or saved. The credential file's existence must not be reported as confirmation of a usable credential pair.

## Empirical API probe ledger

Three unauthenticated, read-only GET probes used the inherited networking settings and TLS verification, with a 15-second timeout each. No credentials were transmitted and no response bodies were retained.

| Host and endpoint | Bounded request | Result |
| --- | --- | --- |
| `data.alpaca.markets/v2/stocks/bars` | AAPL, daily IEX bars, 2005-01-03 through 2005-01-04 UTC, limit 1 | `URLError`; no HTTP status |
| `data.alpaca.markets/v1/corporate-actions` | AAPL, limit 1 | `URLError`; no HTTP status |
| `data.alpaca.markets/v1beta1/news` | AAPL, limit 1 | `URLError`; no HTTP status |

One additional unauthenticated bars connectivity diagnostic (AAPL, daily, limit 1; 10-second timeout) isolated `socket.gaierror`, errno `-3`: DNS resolution failed. Exception strings were not logged. Four total direct API attempts; zero successful HTTP responses or downloaded records. No 2010–2011 dates were queried. Public documentation was accessible through the separate web research tool; that does not establish executor-to-API connectivity. No network bypass was attempted.

## Official capability evidence

Sources accessed 2026-10-30; documentation claims are distinct from account observations.

| Capability | Official evidence | Implication for requested financials |
| --- | --- | --- |
| Historical equities | [Market Data API overview](https://docs.alpaca.markets/us/docs/about-market-data-api) lists equity historical coverage since 2016 for Basic and Algo Trader Plus | Documented equity history does not cover 2005–2011; account coverage not measured |
| Stock bars | [Historical bars](https://docs.alpaca.markets/us/reference/stockbars), GET `/v2/stocks/bars`, provides price/volume aggregates with feed, adjustment, date and pagination controls | These are market observations, not issuer accounting statements. Its `asof` parameter governs symbol/entity mapping, not historical financial-statement availability or restatement versions |
| Corporate actions | [Corporate actions](https://docs.alpaca.markets/us/reference/corporateactions-1), GET `/v1/corporate-actions`, provides splits, dividends, mergers and other events | Event data is not a statement collection. Documentation warns of provider/processing delays and gives no creation-time guarantee; event dates alone do not prove point-in-time availability. 2005–2011 coverage unverified |
| News | [Historical News Data](https://docs.alpaca.markets/us/docs/historical-news-data) documents symbol/date filtering, pagination, source and article timestamps | Earnings coverage is not structured income, balance-sheet or cash-flow history. Target-year coverage and account access unverified |
| Financial-statement API discovery | Reviewed [official US documentation index](https://docs.alpaca.markets/us/llms.txt), market-data overview and endpoint references; no issuer-financial-statement endpoint identified | No supported statement endpoint available to validate or sample in this audit |

An [Alpaca support overview](https://alpaca.markets/support/which-apis-does-alpaca-offer) uses the broad term “fundamentals.” That wording does not establish a callable statement endpoint, 2005–2011 coverage, or point-in-time filing/release timestamps. It is insufficient evidence to authorize a fundamentals acquisition pipeline.

## Separate fundamentals requirement and next validation gate

A distinct fundamentals source is required unless Alpaca supplies a concrete, documented statement API and demonstrates the requested coverage. The source must supply income statements, balance sheets and cash flows for 2005–2011; fiscal period and currency/units; original filing or earnings-release availability timestamps; stable issuer identifiers and delisted-company coverage; and original versus amended/restated versions with provenance. Fiscal period end is not an availability timestamp. A modern restated statement must not be used as though known at a historical decision date.

Any later acquisition should first validate a small, explicitly admitted sample, retain endpoint/parameters/retrieval time and source hashes, report per-year/per-statement coverage and missing timestamps, enforce decision-time availability and version selection, and obey observed rate limits with bounded retries. Outcome labels must remain inaccessible. Alpaca can separately be evaluated for its documented market-data and corporate-action capabilities after connectivity and credential readiness are established; neither downloading nor implementation is authorized by this audit-only run.
