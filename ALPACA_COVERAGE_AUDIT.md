# Alpaca earnings coverage verification — 2026-10-30

## Finding
Alpaca's documented Historical API supports stocks, crypto, options and news; the Corporate Actions API supports splits, dividends, mergers, reorganizations and related capital events. No documented historical quarterly earnings actual/consensus EPS, earnings surprise, or management guidance endpoint was identified.

## Implications
- Alpaca: eligible for stock OHLCV, market and sector-relative returns, available news, and supported corporate actions.
- Not established from Alpaca: historical earnings dates, actual-vs-estimated EPS, revenue surprise, guidance revisions, historical GICS memberships.
- Earnings-related hypothesis testing is BLOCKED until a documented provider with point-in-time coverage is validated.
- Do not mistake dividend corporate actions for earnings.
- Do not query or modify protected MTS DEV banks.
- Do not unblind holdout years to determine provider coverage.
- Historical years must be four non-crash research and four different non-crash blind years; year selection pending.
- No authenticated Alpaca endpoint test has been completed; no credential available in the current shell environment.

## Primary source references
https://docs.alpaca.markets/us/docs/historical-api
https://docs.alpaca.markets/us/reference/corporateactions-1
