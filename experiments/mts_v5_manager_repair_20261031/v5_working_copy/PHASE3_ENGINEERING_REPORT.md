# Phase 3 engineering report

Date: 2026-10-28. Branch: `codex/first-year-manager`.

**Readiness remains BLOCKED / NOT LAUNCH READY.** Real input validation,
feature adapters, native earnings gates and funded shadow accounting were added.
No complete authentic four-family experiment, performance claim or launch
certification is made. Missing source contracts are represented as blockers,
not substitute data or trading rules.

## Implementation

- `first_year_manifest.py`: strict ISO session calendar, separate training,
  validation, embargo and sealed proof dates; full rectangular 500-identity
  prefix validation; source file SHA256 verification; per-day observed-input snapshot hashes,
  next-open dates,
  entry eligibility counts and family-specific blockers. Duplicate, missing,
  foreign and future rows fail. Missing dated controls report unknown counts,
  not 500 eligible tickers. Archive hashes never establish training cutoffs.
- `first_year_daily_feed.py`: checks the proof seal and native contract gates
  before invoking a cutoff-aware loader. Validates all family prefixes and
  daily PIT controls, applies finite-feature warmup eligibility and disallows
  skipped/repeated sessions. This supplies daily family panels; it does not
  invent missing GA4 compilers, model lineages or stress series.
- `first_year_parity.py`: invokes authentic GA5/GA6 eight-family calculations,
  combines them with original tanh GA4 aliases, enumerates candidate features
  through the native LEGACY mapping and validates values plus NaN warmup masks
  across every date and all 500 tickers. In particular `momentum_5` maps to the
  native recursive feature, not a substituted five-day return.
- Strengthened original GA4 feature construction to require 500 tickers on
  every date outside explicitly requested smoke subsets. GA7 rank adapter
  rejects string/integer eligibility flags rather than converting them to true.
  GA7 niche-group selection now reaches native signal evaluation, including
  signal-decay exits when an incumbent loses its controlling niche.
- `first_year_earnings.py`: calls the selected authentic immutable GA5
  one-session or versioned GA6 future-study two-session embargo implementation.
  Nontrading report dates use native next-session mapping. Published future
  schedules are usable; unpublished events cannot retrospectively embargo a
  prior decision. Empty events require explicit, timely forward schedule/absence
  coverage. A selected version and matching native source hash are required.
  Neither version is silently substituted for an archived policy.
- `first_year_horizons.py`: rejects historical-date overlap as synthetic stress
  linkage. Requires explicit joint-scenario identity, mapping, normalization and
  publication contracts and finite exact-date stress coverage before invoking
  the existing reconstruction/normalization code. No compatible data was created.
- `funded_shadow.py`: optional replacement for proportional-unit shadows using
  the existing replay callback interface. Each GA6/GA7/Horizons owner has its
  own bankroll, settled cash, dated-session receivables, fee basis, raw entry,
  peak and executed holdings. Supports ENTER/ADD/REDUCE/EXIT and non-rebalancing
  HOLD, splits/dividends, partial realizations and full-exit maturity. Close
  weights derive from executed shares and each owner's NAV. Proceeds cannot
  fund same-open buys or another owner. An explicit research T+0/1/2 convention
  controls later session availability (even T+0 is conservatively unavailable
  within that opening batch). Every open reconciles owner NAV against fees.
  GA4 funding remains disabled pending an executable native exit contract.

Funding is a research convention, not authentic native portfolio/broker parity.
There is no new claim of certified aggregate risk, pay-date dividends, security
identity/corporate-action parity or independently validated ADD/REDUCE utility.
The existing replay can consume the funded book; it is not enabled as a launch
default. Supplied synthetic OHLCV alone does not certify daily entry eligibility.

## Native contract research

Inspected `/opt/mts` sources read-only, including native feature registry,
LEGACY aliases, eight-family formulas, GA7 runner/ranks, earnings implementations,
GA4 horizon contract and additional exit research.

- `ga4_horizon_contract.py` explicitly distinguishes observation horizons from
  fixed holding exits.
- `/opt/mts/mts_exit_policy_v1.py` is a versioned overlay with a HORIZON_EXIT
  branch. It does not establish an approved policy linked to the frozen GA4 bank.
- `/opt/mts/ga4_exit_ga_infrastructure_v1.py` defines time/stop/trailing exit
  chromosomes and labels itself infrastructure only.
- `/opt/mts/ga4_adaptive_exit_evolution_batch2_v1.py` contains real adaptive
  absent-signal/trailing behavior, but writes a `DIAGNOSTIC_NOT_CERTIFIED`
  manifest, provisional 3% sizing and incomplete corporate-action/PIT controls.
  None of those policies was relabeled as the bank's authentic native exit.
- Horizons requires VIX/VVIX/funding/credit, publication chronology and original
  normalization. The recovered historical archive and the fictional simulation
  have no justified joint path provenance. No historical series was joined to
  synthetic prices, no missing stress was zero-filled, and complete Horizons
  feature parity remains blocked.

## Bounded actual-source evidence

The executable `phase3_input_audit.py` uses actual supplied universe-1 OHLCV,
all 500 tickers and a price filter through 2023-06-30. It compares the adapter
against direct authentic factory calls, including eight-family native GA6
formulas, and performs a second shorter all-ticker rebuild for chronology.
GA7 rank comparison is explicitly an all-true rank diagnostic, not a certified
PIT universe. Horizons remains blocked before reconstruction.

The date partition in this audit is an **engineering-only seal**, not an
approved training/validation/proof research plan. No fitted genome or research
result is selected using it. The raw source file is hashed in full for identity;
prices after the cutoff are not decoded or evaluated. Existing sealed research
proof sets were not opened. Missing membership, earnings coverage, corporate
identity/actions, risk/defense and GA7 niche sources remain explicit daily gates.

Final evidence is in `PHASE3_INPUT_MANIFEST.json`, which remains **BLOCKED**.
It inventories 393 daily sessions, all 500 identities on every date, seven
hashed source/implementation files, per-session raw input hashes, next-open
dates and explicit unknown eligibility counts. The observed period is
2021-12-29 through 2023-06-30.

| Check | Rows / sessions | Features | Result |
| --- | --- | --- | --- |
| Original GA4 factory vs adapter | 196,500 / 393 | 71 | Pass; 11,272,000 finite and 2,679,500 warmup cells |
| Native eight-family GA6 plus GA4 aliases | 196,500 / 393 | 79 | Pass; 12,765,000 finite and 2,758,500 warmup cells |
| Independently rebuilt shorter prefix vs longer build | 186,500 / 373 | 142 originals and aliases | Pass; values and warmup masks unchanged |
| Native GA7 eligible-rank implementation vs adapter | 196,500 / 393 | 16 | Pass; 3,144,000 cells including warmup |
| Complete Horizons feature/normalization stream | Not attempted | — | Blocked by compatible stress/publication contract |

GA7 comparison used an all-true **diagnostic** ranking universe for the supplied
500 names. It does not establish actual membership, earnings, risk or niche
eligibility. Tests separately verify filtering, tied ranks (existing suite),
missing metadata, niche selection and held signal-decay behavior.

The explicit Phase 2 GA6 identity
`000040b4691c2c84a9bea15a1b3a17a6d489a616480782c5fffddad2d267ea97`
requires eight mapped features; none is missing and all are finite for all 500
tickers on the last audited session. Direct native flat-state evaluation returns
**500 NO_ENTRY** decisions. No alternative identity was searched for to improve
that diagnostic. Training lineage, PIT eligibility and held-state long-history
parity are not established by it.

The first long audit exposed a real adapter integration failure: original GA4
predictor rows omit raw `close`, so feeding them directly to GA7 failed. The
corrected path joins the validated raw price through the GA6/native panel.
A new regression uses actual two-ticker source bars to reproduce that schema
boundary. The successful final audit then completed, and a provenance-checked
cache replay extended GA7 comparison to every dated cross section and checked
the explicit GA6 identity. Intermediate Parquet caches are under
`/tmp/mts_phase3_feature_audit`, with source and content hashes; they are not
committed or written under `/opt/mts`.

## Final validation

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest \
  --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
```

**359 passed in 3.15 seconds**: 309 prior tests plus 50 Phase 3 regressions.
Incremental component checks passed before the full run. Authentic imports used
read-only elevated access with bytecode writes disabled. `git diff --check`
passed. Accounting and policy fixtures are tests, not fabricated research data.

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.phase3_input_audit \
  --output PHASE3_INPUT_MANIFEST.json
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.first_year_launch \
  --output FIRST_YEAR_PREFLIGHT.json
```

Both commands complete with **expected exit code 2**, recording blocked
readiness. Neither command runs evolution, chooses a winning manager or claims
launch success. There is still no valid full four-family launch command.
The final implementation, regression tests, manifest, refreshed preflight and
this report are committed locally on the feature branch.

## Next priorities

1. Supply governed synthetic PIT membership, security/corporate-action identity,
   earnings schedule/absence coverage, dated defense/risk controls and a signed
   research calendar with independent chromosome training lineage.
2. Obtain an approved executable GA4 held-position policy with frozen-bank
   linkage; preserve the observation/exit distinction.
3. Obtain stress jointly compatible with each synthetic scenario, including
   release times and approved normalization; validate full Horizons parity.
4. Supply/validate chronological GA7 niche models/distances for synthetic names;
   audit every selected GA6/GA7 candidate's finite required features and native
   decisions across the full eligible 500-name universe.
5. Reconcile funded shadow execution against selected authentic native ledgers,
   corporate-action conventions and aggregate risk; validate action utilities.
6. Only after those gates, run bounded authentic training and frozen validation
   with an approved untouched proof boundary. No costly full GA run is warranted
   by the present component results.

No merge, push, trading, purchase or external research-source write was performed.
