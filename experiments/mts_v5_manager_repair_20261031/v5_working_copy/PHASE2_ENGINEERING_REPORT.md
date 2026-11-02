# Phase 2 engineering report

Date: 2026-10-28. Branch: `codex/first-year-manager`.

**Readiness: BLOCKED / NOT LAUNCH READY.** This continuation implements feasible
native bridges and accounting safeguards. It does not establish an authentic
complete four-family synthetic manager, performance, or brokerage parity.

## Implemented

- GA6 daily producer calls the authentic `native_position_decision_adapter`
  against restored candidates and causal rows. Filled shares, raw average entry,
  peak and entry session determine held state. Native ADD is an additional
  weight; REDUCE is a retained fraction. HOLD preserves exposure. Missing held
  features fail closed. Orchestrator accepts dated GA6 specs/rows/session.
- Explicit bounded GA6 SQLite restoration uses `mode=ro`, parameterized identity
  queries and at most 16 identities. GA7 restores explicit identities from a
  bounded checkpoint and validates genomes against the native grammar. No
  performance ranking selects records. File digest is not a training cutoff.
- GA7 feature adapter invokes the native eligible-universe percentile-rank
  implementation, including average ties and ineligible exclusion. Input must
  be one dated cross section with explicit eligibility. Existing GA7 daily
  native thresholds and actions now receive raw average execution entry,
  separately from fee-inclusive accounting basis. Appreciated holdings remain
  valid through 100% in the fill-state bridge.
- Fill book preserves raw entry, fee basis, peak, entry session and ownership;
  split adjustments update both price conventions. Adds average each basis
  correctly; realized accounting retains fees.
- Independent shadow producer callback runs after shadow open fills, using
  states keyed by family/chromosome/ticker. Several chromosomes can independently
  own the same ticker. Their native decisions no longer need actual manager
  holdings. The orchestrator routes each owner's GA6/GA7/Horizons state.
  Regression demonstrates rejection by the capital book while an independent
  shadow enters, exits and matures. Shadow weights still use proportional units;
  this is not independently funded native portfolio parity.
- Defense supplied in each replay tuple is explicitly a **close observation**.
  It cannot cancel a prior-close order at the same day's open. Liquidation occurs
  at the following open. Every session independently reconstructs cash and NAV
  from prior cash/shares, splits, dividends, fills and fees and checks identity.
  This is algebraic research-ledger reconciliation, not an independent broker
  engine. Existing kernel prevents same-open reuse of sale proceeds.
- GA4 owner state reaches the producer, which fails closed when a holding lacks
  an explicit exit producer. An exit-policy hook validates complete held-ticker
  coverage and owner/date/action identity; no default exit rule was invented.
- Preflight now inventories recovered stress files and GA7 checkpoint and keeps
  explicit blocked status. Original first-year report is preserved.

## Horizons source investigation

The configured stress root was
`/opt/mts/thunder-migration/Momentum-Trading-System_v4/Research/Data`.
Read-only filename discovery found authentic files instead under
`/opt/mts/thunder-migration/mts-v4-recovery-integration-20261004/Research/Data`:

| Relative file | Observations | First | Last |
| --- | ---: | --- | --- |
| `CrashMultiMarketV1/VIX_History.csv` | 9,286 | 1990-01-02 | 2026-10-02 |
| `CrashMultiMarketV1/VVIX_History.csv` | 5,117 | 2006-03-06 | 2026-10-02 |
| `CrashCausalPackV1/ofr_fsi_raw_20261004.csv` | 6,770 | 2000-01-03 | 2026-09-30 |

Loader now accepts an explicit root; it does not silently substitute an archive.
It retains the original two-observation OFR lag and refuses post-coverage dates.
Sparse requested dates now align against the complete source calendar before
forward filling, so prior observations are not lost. Dates before sufficient
lagged coverage still fail. Availability timestamps remain uncertified.

Read-only smoke at 2020-01-02 returned VIX 12.47, VVIX 89.67, lagged Funding
-0.398 and Credit -0.552. Common source end is 2026-09-30; requested 2026-10-01
was excluded. Supplied synthetic index spans 2021-12-29 through 2026-10-27.
Historical dates overlapping a fictional simulation do **not** establish a
compatible stress trajectory. No historical series was spliced onto fictional
paths, no source was zero-filled, and no observation was fabricated.

## Native GA4 investigation and unresolved contracts

Authentic source
`/opt/mts/thunder-migration/mts-layered-run-20261007/Core/layered_ga/ga4_horizon_contract.py`
explicitly says: “Horizon observation does not imply a fixed holding-period exit.”
`stage2_path_v3.py` describes hypothetical T+1 entry and T+1+h outcome exits.
The inspected resolved GA4 bank record contains boolean chromosome definitions
and horizon `63`, not a native live held-position policy. Consequently a 63-day
liquidation or entry-predicate inversion cannot honestly be labeled native GA4.
An approved executable exit policy with archive linkage remains necessary.
The hook is integration plumbing, not completion of that missing policy.

Other remaining gates:

- Governed Horizons stress input compatible with fictional paths, full coverage,
  normalization parity and publication-time contract.
- Full-universe and long-history feature parity for all families, GA7 niche/PIT
  eligibility and earnings controls, and independently verified training cutoffs.
  Archive existence and restored identities establish none of those properties.
- Independently funded shadow native portfolios and validated incremental action
  utility. Entry-context matured returns are not certified ADD/REDUCE utilities.
- Certified settlement/available cash, aggregate incumbent risk/correlation,
  gap estimates, corporate-action convention parity and full native-ledger
  comparisons. Current caller-supplied risk estimates are not certification.
- A complete governed daily synthetic input manifest and four-family feed,
  differentiated training fitness, frozen chronological validation and untouched
  proof evaluation. No sealed proof set was opened.

## Validation

Full bounded command (bytecode disabled; elevated read access for authentic
external imports):

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest \
  --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
```

Final result: **309 passed in 2.69 seconds**. Preflight returned the expected
exit code 2 and refreshed `FIRST_YEAR_PREFLIGHT.json` with blocked status. New tests exercise native GA6
amount semantics, raw-entry/fee-basis separation, rejected independent shadows,
causal defense timing, sparse stress alignment, fail-closed GA4 holdings and
actual archive restoration/native action comparison.

Bounded authentic smoke restored GA6 identity
`000040b4691c2c84a9bea15a1b3a17a6d489a616480782c5fffddad2d267ea97`:
fixture direct native ADD 0.0375 became target 0.1375 from held 0.10.
This numerical fixture is not a synthetic experiment or research evidence.
GA7 checkpoint identity `5633a66d50bdadc95dab` restored from
`/opt/mts/ga7-deploy/ga7_unbounded/runs/preflight_16/checkpoint.json`, SHA256
`8e70569141a33597449dbcbec81340dc9cb96e33d3f229d8319ce636ebf0f812`.
Native rank fixture produced 1/3, 5/6, 5/6; no profitability claim follows.

No push, merge, large experiment, research-data modification or brokerage
operation occurred. All implementation and report changes are committed locally.
