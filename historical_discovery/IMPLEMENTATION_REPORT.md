# Implementation report — 2026-10-30

Implemented an isolated discovery audit and fixture-tested pipeline in `historical_discovery/`. Existing GA8/GA9 code and results were neither imported nor modified. No historical data payloads, prior result payloads, or 2010/2011 labels were opened. No real 2005 demonstration was attempted because defensible data coverage was not established.

## Audit and feasibility

`artifacts/data_audit.json` records the initial presence-only inventory. `artifacts/data_audit_reproducible.json` repeats it with the shipped audit module and a slightly expanded list of credential variable names. Local roots contain 910 source files (~198 MB), six result files (~3.85 MB), and 204 files (~6.27 MB) under the Research symlink. These are metadata counts, **not** verified datasets. No values were printed and no credentials were discovered in the checked environment variable names or checked credential file paths. Other credential locations and provider entitlements remain unknown. Cloud runtime status tooling was unavailable; no provider access was attempted.

| Requirement | Verified local status | Next-stage acceptance evidence |
| --- | --- | --- |
| 2005–2011 historical common-stock membership | Unknown | Permanent IDs, effective dated NYSE/NASDAQ listings, security types, IPOs, symbol changes and delistings; no current-symbol sampling. |
| Adjusted OHLCV and corporate actions | Unknown | Actual exchange calendar, full listing-session coverage, adjustment methodology, action reconciliation, terminal recovery returns and source versions. |
| Original PIT annual financials | Unknown | Public filing timestamps or conservative date precision, original vendor-version availability, as-reported values, period ends and explicit restatement policy. |
| Optional market cap and benchmark | Unknown | Historically available shares/prices or archived capitalization with availability timestamps; documented benchmark history. |
| Credentials, license, cost | Checked names/paths absent; entitlement unverified | Supplier/account confirmation of historical and delisted coverage, permitted research/export use, storage terms, and written price quote. |

The precise acquisition recommendation is a **custodian-prepared, discovery-only 2005 partition** matching schema v1 before purchasing or importing a full panel. Request all eligible listings, not a winner sample, with complete bars/actions/terminal losses, annual original financials covering the prior two fiscal years, availability timestamps, benchmark and exchange sessions. Require a manifest documenting coverage denominators, exclusions, missing financials and reconciliations. Verify a split, dividend, IPO, ticker change, delisting loss, date-only filing, and restatement against original records. Then stage 2006–2009 in separate partitions. Keep 2010/2011 sealed outside the development workspace; a separate future evaluation release requires a new explicit protocol and exposure audit.

A current-symbol price API or latest-restated financial dump is not an acceptable substitution. Full-market historical membership, delisting returns and archived PIT fundamentals may require separate licenses or paid products. Cost is unquoted and cannot be inferred from file presence; no data was purchased and no paid request made. Supplier selection and a binding cost/coverage assessment require verified entitlements or supplier documentation. This engineering stage is feasible and functional on fixtures; real-data feasibility remains conditional on that delivery.

## Delivered and verified

The adapter protocol and schema, dated universe reconstruction, two winner definitions, terminal failures, PIT features, fixed model candidates, three-arm intersection comparison, broad chart coverage, naive baselines, chronological folds, prediction-before-label artifacts, holdout rejection and hash verification are implemented. Freeze and run commands are documented in `README.md`.

Tests cover deterministic end-to-end folds, current-future label isolation, point-in-time financial versions and timestamps, missing fundamentals, IPO/delisting membership, exclusion types, strictly chronological extrema, coverage/duplicate/nonfinite rejection, JSON admission before payload access, reconciled-action contract, hand-calculated metrics, tampered freezes, config mismatch, and no-overwrite behavior. Fixtures and their rankings are entirely invented. No claim of investment performance, causal value or pristine historical validation is made.

Artifacts in `artifacts/fixture_run/` include `freeze.json`, per-year frozen predictions and evaluations for synthetic 2005–2009, and `summary.json`. The package does not offer an evaluation unlock. A malformed or dishonest external manifest remains a supplier trust boundary; see README before admitting real data.

Next-stage ETA: allow roughly 1–2 engineering days **after** a compliant discovery-only 2005 delivery to reconcile it, run the small real-data demonstration and report coverage. Supplier access, licensing, procurement and repairs have no defensible ETA yet. This estimate does not include full-panel modeling or evaluation release.

Pre-existing worktree changes at task start: `ga9/run.py`, `ga9/screening.py`, untracked charter and `claude_review/`. These were left untouched. New work is entirely under `historical_discovery/`; no commit was created.

## Additional Alpaca directive audit

`ALPACA_DATA_DIRECTIVE.md` appeared during implementation and was read without modification. The additional presence-only check in `artifacts/alpaca_capability_audit.json` found no checked Alpaca key/secret pair, OAuth token, connection manifest or available Alpaca connector. Authenticated account endpoint probing and the conditional sampled download therefore could not be performed; this is an explicit blocker, not evidence of an account entitlement failure. Zero payloads were downloaded. No endpoint was invented or substituted for financial statements.

Alpaca's current [market-data documentation](https://docs.alpaca.markets/us/docs/about-market-data-api) advertises stock history from 2016, which does not cover the charter's 2005–2011 period. Its [historical API overview](https://docs.alpaca.markets/us/docs/historical-api) lists stocks, crypto, options and news; the documented [corporate-actions endpoint](https://docs.alpaca.markets/us/reference/corporateactions-1) provides corporate actions. No documented PIT income-statement, balance-sheet or cash-flow endpoint was found in this review. The absence of such an endpoint in the reviewed public documentation is not an authenticated account-specific capability test. Alpaca bars/actions must never be labeled financial statements, and its documented stock-history coverage cannot satisfy this project. A separate licensed fundamentals delivery with original statements and public/version availability timestamps is required unless a supplier demonstrates otherwise. Alpaca can remain a bars/actions source for separately authorized, supported date ranges; downloading those would not advance this historical task.

Final validation: **22 tests passed** with standard-library unittest; compile check and `git diff --check` passed. Frozen synthetic outputs cover only 2005–2009. Final git status additionally includes the externally added untracked `ALPACA_DATA_DIRECTIVE.md`; it was not created or changed by this implementation.
