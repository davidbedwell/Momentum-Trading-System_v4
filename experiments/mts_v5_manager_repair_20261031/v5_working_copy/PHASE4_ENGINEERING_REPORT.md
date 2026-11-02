# Phase 4 engineering report

2026-10-28 · branch `codex/first-year-manager` · starting commit `f008b87`.

**BLOCKED / NOT AUTHENTIC FOUR-FAMILY LAUNCH READY.** The bounded four-family
feed/producer/shared-bank/funded-shadow integration is implemented and fixture
tested. Actual GA6/GA7 source calls, native action comparisons and independently
funded diagnostic shadows were executed. A complete authenticated four-family
market replay was **not** executed: required source contracts remain missing.
No performance, edge, GA4/Horizons readiness or broker parity is claimed.

## Calendar coverage and immutable seal

Read the first-year, Phase 2 and Phase 3 reports and Phase 3 manifest, repository
modules, and relevant native sources before implementation. The existing Phase 3
calendar seals prices from **2023-07-03**. That seal was preserved; a request to
extend an audit is not authority to open an existing sealed proof interval.
The calendar remains an engineering partition, not an approved research split.

Streaming Date/Ticker-only inspection establishes exactly **1,260 sessions**,
2021-12-29–2026-10-27, with all **500 tickers on every date** (630,000 keys).
The value audit remains **393 sessions**, 2021-12-29–2023-06-30 (196,500 rows).
The remaining **867 sessions are sealed**, rather than asserted audited.
The extended action diagnostic reuses the already-open Phase 3 engineering
validation prefix; it reads no forward-outcome columns, performs no fitting,
selects no identity or parameter, and opens no sealed research outcomes.
The bounded portfolio smoke uses training dates only.

`streaming_first_year.chunks` can process up to 1,260 authorized sessions without
the original adapter's 504-session ceiling. It validates the supplied calendar
**before** cache/source I/O, reads OHLCV with ticker/cutoff predicates, validates
prices/sectors/rectangular identities, and caches each ticker's entire native
stock-local history. It deliberately retains recursive history instead of
truncating at the nominal longest rolling window. Native cross-sectional work
uses 32-session chunks with 20 earlier observations for percentile changes.
Caches reside under `/tmp/mts_phase4_stream`, keyed by source/implementation
hashes, dates and universe; each local file has a verified content hash.
No legacy dataset or native implementation was modified.

The streamed output matches the hash-verified Phase 3 native full-history build
for **142 columns** (71 original predictors plus 71 tanh aliases), **27,903,000
cells**: 22,544,000 finite and 5,359,000 warmup cells. Original features and their
aliases are counted separately, not represented as independent predictors.
Daily hashes and next-open dates are in `PHASE4_INPUT_MANIFEST.json`; raw daily
input snapshots and GA6/GA7 feature parity remain in the source-verified Phase 3
manifest. Missing eligibility remains unknown, never promoted to 500 eligible.

An independent **263-session** native rebuild through 2022-12-30, using
**47-session** chunks, matched every daily feature hash in the longer 393-session
build. This tests history-prefix and chunk-boundary invariance across all names,
including recursive history, warmup masks and cross-sectional lag boundaries.
It does not certify features on the unopened 867 dates.

| Measured operation | Wall seconds | Process CPU seconds | Peak RSS MiB |
| --- | ---: | ---: | ---: |
| Cold 393-session streamed feature parity | 239.56 | 312.68 | 921.43 |
| Verified-cache repeat, same 393 dates | 83.73 | 137.25 | 965.12 |
| Independent 263-session prefix, different chunks | 142.90 | 186.14 | 401.25 |
| 32-session native diagnostic + funded shadows | 3.63 | 3.98 | 997.57 |
| 393-session native action audit + same bounded smoke | 27.92 | 28.37 | 2,335.37 |

These are observed single-process peaks, including Arrow/native allocations;
CPU can exceed wall time because underlying libraries use threads. No claim is
made that warm-cache RSS is lower or that the 1,260-date value workload has been
benchmarked. The extended action audit materializes the permitted feature/row
maps and is less memory efficient than the streamed feature audit.

## Integrated execution and accounting

`first_year_manager.bounded_replay` connects `DailyFeed` to all four native
producer families, actual executed owner state, the chronological shared bank
and independent `FundedShadow` books. It requires 2–64 contiguous permitted
sessions, checks missing native contracts before market loading, applies all
family entry gates to ENTER/ADD, preserves held management, and routes family
source/training metadata separately. A family cannot be silently omitted from
this four-family runner. GA7 can call authentic native signal/strength functions.
Missing metadata is not replaced by a fabricated model training date.

The integrated runner accepts authentic compilers, genomes, Horizons panels,
dated controls and cutoff-aware loaders from governed callers. Those dependencies
are unavailable for the supplied synthetic market. The tested integration uses
**explicit fixtures**, including mocked family decisions; that test is not an
actual native four-family research run. The source diagnostic is separate and
never passes diagnostic actions through the authenticated proposal boundary.

The shared kernel now has an explicit opt-in research T+1/T+2 receivable book;
T+0 compatibility remains the default for existing callers. Sales never fund
same-open purchases. Equity includes unsettled receivables while new purchases
use settled cash. The first-year bounded runner explicitly uses T+1 by default.
Close decisions continue to execute at the next open, and a defense observation
cannot cancel an earlier order at the same day's open.

Every shared session reconciles cash, receivables, filled shares, fees, splits,
dividends and NAV. Per-owner cumulative cashflow plus marked shares measures
that owner's **P&L contribution**, not a fictitious segregated allocation of the
common bankroll; $100,000 plus those contributions must equal portfolio NAV.
Independent funded books have their own bankroll, settled cash, receivables,
executed holdings and per-owner NAV, without cross-owner funding.

`ledger_audit.funded_shadow` independently reconstructs owner portfolios solely
from public fill/NAV journals, session bars and the stated funding convention.
It checks fill prices, fees, available cash, shares, settlements, corporate
actions and close NAV. The real diagnostic reconciled **64 owner-sessions and
601 fills**, maximum residual **1.0186340659856796e-10**. Tests deliberately
corrupt fees, NAV and splits to verify detection. Other fixtures prove shared
BUY/SELL flows, T+1/T+2 timing, fee-inclusive versus raw entry, defense timing,
owner attribution, and rejection by shared capital while shadows still trade.

Dividend ex-date cash credit, fractional shares, fee rate and split convention
are explicit research assumptions. Native GA7 uses integer sizing, sector and
capacity constraints and its own adjusted-price/settlement conventions. The
shadow journal is not claimed to reproduce those native funded portfolios.
Aggregate incumbent risk/correlation, gap controls, pay-date dividends, corporate
identity and native full-ledger equivalence remain uncertified. Entry-context
calibration is still not certified incremental ADD/REDUCE utility.

## Native source and action evidence

The explicit Phase 2 GA6 identity and GA7 identity were reused unchanged:

- GA6: `000040b4691c2c84a9bea15a1b3a17a6d489a616480782c5fffddad2d267ea97`.
- GA7: `5633a66d50bdadc95dab`.

Both are restored read-only. Their archive hashes identify bytes, not training
cutoffs. Raw decision functions were separated from authenticated proposal
wrappers so diagnostics can compare native decisions without inventing lineage.
Actual source and local adapter hashes are retained in both native manifests.

Across **393 dates × 500 names × 3 states**, GA6 compared its production adapter
against direct authentic `native_action` output and amount semantics. The three
states are flat and two hypothetical held-entry states, **not observed native
historical portfolios**. Warmup NO_DATA is preserved; held warmup fails closed.
There were 125,500 NO_DATA and 70,992 NO_ENTRY flat probes, plus eight native
ENTER probes. Held probes covered ADD/HOLD/REDUCE. No identities were searched
for to change these counts. The audit plus bounded shadow evaluation made
**1,195,000 direct/native-adapter GA6 calls**.

GA7 uses authentic `runner.passes` and `request_replay.score_signal`; held actions
were independently compared against authentic `request_replay.replay_requests`
on actual consecutive three-session windows, with known first-entry integer
holdings. The long audit made **195,500 native request replay calls** and
112,500 calls each to native passes/score. It compared **391 interior dates**,
2021-12-30–2023-06-29, over 500 names, including 12 ADD, 26,644 EXIT, 26,612 HOLD
and 4,140 REDUCE held decisions. Warmup eligibility requires both selected
features to be finite before a native entry can occur.

The first/last dates **do not have this held-state oracle comparison**. Feature
parity remains 393 dates, but complete 393-date held-action/native-funded parity
is not asserted. The oracle isolates three-session portfolios, with terminal
liquidation confined to reference diagnostics; terminal liquidation is never
injected into the chronological manager or used as a native GA4 exit.

The actual funded diagnostic is **32 training sessions**,
2022-11-17–2022-12-30, all 500 names. Its all-true ranking gate is explicitly
**diagnostic**, not PIT evidence. It made 601 GA7 shadow fills, 264 completed
outcomes and 8,422 insufficient-cash/no-increase rejections. GA6 had no entries
or funded fills in this particular fixed window. Defaults of no supplied splits
or dividends are unverified diagnostic conventions, not a certified event tape.

The shared bank made **zero fills**, NAV stayed $100,000, because missing PIT and
training lineage correctly block capital. No positive calibration was fabricated
to force shared-bank activity. Repeated bounded runs and the extended audit
produce identical shadow fill/NAV/action digest:
`466c813200dd22a5d4b8ec418b62ff809f3bacf9563291f7a75463fba441113d`.
This is a determinism check, not a profitability result.

## Controls, GA4 exits and Horizons

Read-only inspection of authentic GA7 niche sources found **18 annual expanding
models**, **329,406 rows**, **79 historical identities**, 2009-01-02–2026-09-14.
Training dates precede evaluation dates, but the native manifest explicitly says
`CHRONOLOGY_VERIFIED_FEATURE_PROVENANCE_PENDING`; publication times are unknown.
There are **zero identities in common** with the 500 synthetic tickers. These
controls cannot simply be assigned to fictional securities. Metadata and hashes
are recorded in `PHASE4_CONTROL_DISCOVERY.json`; no historical price/outcome
columns or sealed evaluation outputs were inspected for this discovery.
Native membership/earnings/risk/defense loaders were read as source, not treated
as governed synthetic controls.

Directly reread the authentic GA4 horizon contract, exit infrastructure and
adaptive exit source. The contract still states that a horizon observation does
not imply a fixed holding-period exit. Existing adaptive research is explicitly
diagnostic and does not establish linkage to the frozen bank.
`ExperimentalExit` provides a versioned, caller-supplied HOLD/EXIT callback with
exact held coverage and no default rule. Its bound hook is marked experimental
and explicitly rejected by the authenticated four-family runner. No fixed
horizon, invented stop, or entry-inversion policy was selected or certified.
GA4 funded shadows remain unavailable pending an executable approved contract.

Horizons remains blocked by missing jointly compatible synthetic stress,
publication and normalization provenance. Its existing pluggable input boundary
remains available; no standalone proxy rule was selected because no governed
scenario mapping or experimental research approval was supplied. Historical
VIX/VVIX/OFR date overlap is not joint provenance. No historical stress was
spliced onto fictional prices, and missing stress was never zero-filled.

## Measurable readiness and remaining dependencies

`PHASE4_READINESS.json` reports **0/4 authentic families ready**, no stale source
hashes, and all missing contracts explicitly. The current measured matrix is:

| Gate | Evidence | Authentic status |
| --- | --- | --- |
| Source calendar and full daily identity coverage | 1,260 dates × 500 names | Metadata checked; 867 value dates sealed |
| GA4 / GA6 / GA7 features | 393 dates; streamed GA4/alias parity plus verified Phase 3 native family evidence | Engineering parity; PIT unknown |
| Prefix invariance | Independent 263-date full-universe rebuild | Pass within open prefix |
| GA6 native actions | 393 dates; three states per ticker/date | Diagnostic pass; training/eligibility unknown |
| GA7 native held oracle | 391 interior dates; 500 names | Diagnostic pass; boundaries and native funding incomplete |
| Four-family DailyFeed → shared/funded replay | Contiguous bounded runner; positive-fill accounting/control fixtures | Wired/tested; actual four-family run blocked |
| Native-funded diagnostic shadows | 32 dates, 601 fills, 264 completed; independently reconciled | Research only; authentic shared-bank fills 0 |
| GA4 held exits | Explicit experimental plugin; no approved bank linkage | Blocked |
| Horizons complete features/actions | No compatible stress trajectory | Blocked |
| Synthetic PIT/earnings/niche/model training lineage | No governed coverage | Unknown/blocking for all families |
| Aggregate risk, incremental utility, broker/native ledger parity | Partial controls and research identities | Uncertified/blocking |

Exact next actions, in dependency order:

1. Obtain an approved calendar authority and input-access plan that preserves an
   independently untouched proof set. Do not silently move the 2023-07-03 seal.
   Only then extend the streamed value audit over remaining permitted dates;
   benchmark that actual workload and retain daily source/feature/next-open seals.
2. Supply 500-name dated security/membership mappings; selected native earnings
   policy version, schedules or explicit forward absence coverage; publication
   timestamps; corporate-action identity/adjustment/payment conventions; and
   dated synthetic defense/risk/gap/correlation inputs.
3. Establish independently verified pre-decision training cutoffs and immutable
   source/snapshot/feature contracts for every archived family identity. Hashes
   alone cannot satisfy this. Compile authentic GA4 daily entries using governed
   eligible cross sections and provide its approved archive-linked held exits.
   Then extend the funded-book GA4 allowlist with mandatory approved-exit
   ownership/state validation and route its matured outcomes into calibration;
   the current bounded runner has no authentic GA4 shadow bootstrap.
4. Provide jointly generated Horizons stress with approved mapping,
   normalization and publication chronology. If experimental alternatives are
   desired, select a separately versioned research contract before implementation;
   keep it excluded from authentic launch readiness.
5. Supply causal synthetic GA7 niche training data/models/distances with
   publication times. Complete boundary held-action oracles and independently
   reconcile full native funded ledgers, including actual corporate actions,
   capacity/sector controls, stops, settlement and integer sizing.
6. Implement and validate aggregate incumbent risk and incremental action
   utilities; compare native and shared execution conventions. Only then run
   the authenticated bounded four-family manager, authentic training and frozen
   validation. Preserve the proof seal and do not begin a large GA experiment.

## Commands and validation

From `/opt/Momentum-Trading-System_v5-alpha`, with read-only native archive
access and the existing Python environment:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest \
  --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
```

Final result: **384 passed in 4.73 seconds** (359 prior + 25 Phase 4 cases).
All full-suite tests ran with read-only native access and bytecode writes
suppressed. `git diff --check` passed. Source parity, source diagnostics and
prefix rebuilds are additional executions, not counted as unit tests.

Executable feature audit and independent prefix check:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.phase4_audit --output PHASE4_INPUT_MANIFEST.json
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.phase4_prefix_check --output PHASE4_PREFIX_CHECK.json
```

The audit returns **2 (blocked readiness)** after completing parity. The prefix
check returns 0 on invariance success. The existing hash-verified Phase 3 cache
under `/tmp/mts_phase3_feature_audit` is a required reference; these commands
fail rather than accept stale reference bytes. It is reproducible with the
existing Phase 3 audit, which also preserves the seal. Caches are not committed.

Executable actual-source diagnostic and extended action audit:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.phase4_native_smoke \
  --sessions 32 --output PHASE4_NATIVE_SMOKE.json
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.phase4_native_smoke --audit-prefix \
  --sessions 32 --output PHASE4_NATIVE_ACTION_AUDIT.json
```

Both return **2 (diagnostic only / blocked)**. `--audit-prefix` expands only raw
native action comparisons across the existing open prefix; the funded smoke
stays bounded to 32 training sessions. No evolution runs.

Executable readiness command:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python \
  -m discovery.competitive_ga.phase4_readiness --output PHASE4_READINESS.json
```

It verifies evidence hashes and returns **2 (BLOCKED)**. The callable authentic
integration is `first_year_manager.bounded_replay(...)`, requiring the governed
feed, loaders, controls, native settings and funding contract described above.
**There is no valid full authentic four-family launch command for the supplied
inputs.** Neither a fixture nor the source diagnostic is offered as that command.

Implementation commits are local: `edab83f` (streaming audit), `c14138d`
(integration/native decisions/accounting). Independent prefix/cache/control
artifacts, readiness checks/tests and this report form the final local increment.
No GitHub push/merge, main-branch change, external purchase, live trade, large
GA run, legacy-source write or sealed-proof evaluation occurred.
