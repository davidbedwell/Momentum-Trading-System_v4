# Alpaca repair audit — 2026-10-29

**BLOCKED_NOT_PIT_CERTIFIED. Zero bars recovered or integrated.** GA8 was not
edited, executed or stopped. No GA9 evolution or strategy replay ran. No new
EODHD acquisition was attempted. Credentials were never printed.

## Observed access and coverage

The existing `/root/.config/mts/alpaca.env` configuration was located using prior
MTS Alpaca scripts. The credential pair could be loaded into request headers;
this does **not** establish that the keys are valid. No Alpaca credentials were
present in the process environment. The cloud runtime skill's environment-status
tool and `/etc/codex/network-policy.json` were unavailable. No proxy environment
variables were present; no network policy or routing changes were made.

Two authenticated safe probes, each for **QQQ, January 3–5, 2022, daily raw SIP,
asof=2022-01-03**, failed with `URLError`, underlying `gaierror`, errno **-3**.
No HTTP response was received. A separate unauthenticated connectivity diagnostic
also failed DNS resolution. This is an executor DNS/access blocker, not evidence
of a 401, 403, invalid key, SIP entitlement failure or an empty historical series.
The initial and final probe directories are retained separately.

| Year | Baseline diagnostic gaps | Raw recovered | Certified recovered | Remaining |
|---|---:|---:|---:|---:|
| 2022 | 1,891 | 0 | 0 | 1,891 |
| 2023 | 1,249 | 0 | 0 | 1,249 |
| 2024 | 1,109 | 0 | 0 | 1,109 |
| 2025 | 1,257 | 0 | 0 | 1,257 |
| Total | 5,506 | 0 | 0 | 5,506 |

All gap symbols are in the existing unresolved identity/quarantine evidence:
APP, ARM, ATVI, BKNG, FB, FISV, GOOGL, SPLK, TSLA, WBA, WDC, XLNX.
These are **not all direct protected symbols**. The implementation conservatively
excludes both the frozen protected partition/known aliases and every identity
candidate with `allow_in_backtest=false`. Network restoration alone therefore
will not make these gaps eligible. No exclusion was loosened. QQQ is acquired
separately as a benchmark and was never added to stock membership.

## Implementation and limits

`alpaca_repair.py` implements a new-output-directory acquisition workflow bounded
to 2022–2025, at most 500 requests and 30 gap symbols (defaults 240/20), four pages
per query and 20-second HTTP timeouts. Missing security-session groups are ranked
by gap count, with requests restricted to their symbol/year date envelopes.
Envelopes can contain existing bars, retained for reconciliation rather than
silently overwriting archive data. Full QQQ calendar years follow gap work within
the same budget. It stops on failed initial access and on 401/403/429 during work;
there are no retry loops or automatic feed downgrades.

Queries explicitly request SIP, raw/split/dividend/all adjustments, and a
historical `asof` equal to the interval start. An unmapped `asof=-` comparison
checks returned price/volume consistency. This cannot prove historical identity:
Alpaca can fall back to literal-symbol behavior when a symbol is unknown at the
requested asof date. No aliases are stitched or historical stable IDs invented.
See [Alpaca bars semantics](https://docs.alpaca.markets/us/reference/stockbars).

Every successful response is stored byte-for-byte with request parameters,
retrieval timestamp and SHA-256; failures record sanitized types/status only.
Pagination incompleteness, unexpected symbols, out-of-window dates, invalid
OHLCV and duplicates fail closed. Adjustment variants produce date-aligned price
and split-volume factors. `reconcile_declared_actions` checks normalized declared
split ratios against both price and volume changes, and cash dividends against
adjacent factor changes. Missing event provenance stays unresolved.

**Live corporate-action schema normalization and event-completeness reconciliation
remain blocked by access.** The runner preserves corporate-action endpoint pages
and counts, but does not claim numeric factor consistency proves complete
split/dividend accounting. Normalized-action checks have synthetic unit coverage,
not live vendor validation. Multiple same-day events, currency, mergers, spin-offs,
special distributions and event boundary context need explicit reconciliation
before admission to a return panel. No zero dividends, split factors or adjusted
closes are manufactured. Alpaca warns that corporate-action availability may be
delayed; current API retrieval time is not historical announcement knowledge.
See [Alpaca corporate actions](https://docs.alpaca.markets/us/reference/corporateactions-1).

`nasdaq_archive.load_alpaca_diagnostics` is the integration entrypoint for verified
**vendor raw diagnostics only**. It rechecks source hashes, request feed/adjustment,
symbol, quarantine, session dates and actual response values rather than trusting
candidate certification labels. It leaves identity, adjusted close, dividends and
splits unknown. The final accepted file is empty and the adapter returns no rows.
`require_replay_inputs` still rejects all replay authorization manifests.

## Membership findings

The archived [jmccarrell/n100tickers](https://github.com/jmccarrell/n100tickers)
annual baselines and event ledger were compared with the archived
[thuningxu/sp500nq100](https://github.com/thuningxu/sp500nq100) CSV at the union
of baseline/change dates in 2022–2025. **25 of 26 dates agree.** At 2025-07-17,
primary still includes ANSS while secondary excludes it; primary removes ANSS
on 2025-07-28 when adding TRI. That interval needs official event investigation.
Agreement between these secondary sources is not independent PIT certification.
Their archive files and the curated notice facts are hashed in the comparison.
No new remote repository revision was downloaded or represented as an update.

Selected official annual notices were checked for all four years, with effective
and publication dates kept separately in `official_notice_facts_20261029.json`:

- [2022 notice](https://www.nasdaq.com/press-release/annual-changes-to-the-nasdaq-100-index-2022-12-09): published December 9 at 20:00 EST; effective December 19. All six additions and seven removals match the primary ledger.
- [2023 initial notice](https://www.nasdaq.com/press-release/annual-changes-to-the-nasdaq-100-indexr-2023-12-08): published December 8 at 20:00 EST; effective December 18. Its six additions and six removals match.
- [2023 amendment](https://www.nasdaq.com/press-release/update%3A-annual-changes-to-the-nasdaq-100r-index-2023-12-12): published December 12 at 18:00 EST; specifies TTWO addition/SGEN removal effective December 18. The archived primary places these on **December 14**, as does the secondary roster. Preserve this conflict; do not infer index effectiveness from acquisition closing dates. Later superseding official evidence has not been established.
- [2024 notice](https://www.nasdaq.com/press-release/annual-changes-nasdaq-100-indexr-2024-12-13): published December 13 at 20:00 EST; effective December 23. All three additions/removals match.
- [2025 notice](https://ir.nasdaq.com/news-releases/news-release-details/annual-changes-nasdaq-100-indexr-2): published December 12; effective December 22. All six additions/removals match. Exact publication time was unavailable in the inspected page, so `known_at` remains null rather than assuming midnight.

These are selected notice checks, not certification of the starting roster,
interim changes or protected security lineage. No historical membership rows were
promoted to runnable inputs. A notice timestamp describes observed publication,
not proof that a particular historical data subscriber had received it.

## Next actions and reproducibility

1. Restore supported executor DNS/egress for `data.alpaca.markets`; repeat the safe QQQ probe. Establish actual HTTP response before diagnosing key validity or SIP entitlement. Never paste keys into logs.
2. Resolve stable security/issuer identities and historical effective symbol intervals using independently sourced evidence. Keep protected issuers and share-class aliases excluded. Validate records individually; do not flip quarantine globally.
3. Rerun bounded acquisition into a new directory. Validate corporate-action schemas and complete event windows before invoking normalized split/dividend reconciliation. Acquire preceding/ex-date context where it falls within the authorized 2022–2025 bounds; keep boundary events unresolved when context is missing.
4. Resolve ANSS July 2025 and SGEN/TTWO December 2023 against superseding official notices. Certify the starting roster and complete interim event chain, with knowledge timestamps and stable IDs.
5. Only after those gates pass, certify independent sessions, warmup/exit coverage and the QQQ total-return benchmark policy. Keep long evolution disabled until then.

```bash
/opt/mts/.venv/bin/python -m ga9.alpaca_repair \
  --archive /tmp/ga9_nasdaq_archive \
  --gaps ga9/artifacts/nasdaq_archive_audit_final_20261029/missing_projected_bars.csv \
  --output ga9/artifacts/NEW_ALPACA_REPAIR --max-requests 240 --max-symbols 20

/opt/mts/.venv/bin/python -m ga9.membership_crosscheck \
  --archive /tmp/ga9_nasdaq_archive --output ga9/artifacts/NEW_MEMBERSHIP_CHECK

/opt/mts/.venv/bin/python -m unittest ga9.test_alpaca_repair \
  ga9.test_nasdaq_archive ga9.test_screening ga9.test_benchmarks \
  ga9.test_objective ga9.test_execution
```

Acquisition exit **2** means replay remains blocked, including after successful
raw downloads. The comparison CLI exits zero when diagnostics complete, without
certifying membership. Final evidence:
[access/coverage ledger](artifacts/alpaca_repair_final_20261029/report.json),
[accepted raw records](artifacts/alpaca_repair_final_20261029/accepted_raw.json),
[membership conflicts and provenance](artifacts/membership_crosscheck_final_20261029/crosscheck.json).

Validation: **47 tests passed** across the six modules above. New checks cover
request/window bounds, sanitized DNS errors, repeated pagination, mapping and
variant mismatches, split price/volume agreement, dividend factors, unknown event
provenance, empty adapter integration and quarantine rejection. Live price/action
success paths remain unvalidated because the executor could not resolve Alpaca.
