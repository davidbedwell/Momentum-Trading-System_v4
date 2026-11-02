# Phase 8 engineering report

2026-10-28; `codex/first-year-manager`; starting commit `84fd73a`.

**BLOCKED / NOT FOUR-FAMILY LAUNCH READY.** This phase completes a bounded
fixed-integer-order execution boundary and two independent research consumers.
It does not complete native endogenous execution parity or four-family policy
integration. All prior launch gates and the 867-session proof seal remain.

## Implementation and exact scope

- `discovery/competitive_ga/share_order_contract.py`: frozen versioned Tape,
  Order, Open, Position, Receivable and Event records; full-tape prevalidation.
  Orders specify immediately preceding decision and next-open execution session,
  explicit owner/ticker/side/absolute integer shares. Initial state includes
  settled cash, raw entry, fee basis, age, peak and dated owner receivables.
- `discovery/competitive_ga/FIXED_SHARE_CONTRACT.md`: exact calendar, priority,
  money, fees, T+1, opening mark, capacity, state-age, coverage and rejection
  semantics. No sector/risk/utility policy is implicitly introduced. Share-count
  capacity is a declared test constraint, not native sector/stop capacity.
- `discovery/competitive_ga/native_style_share_executor.py`: explicitly labeled
  independent native-style integer reference. Native replay_requests still has
  no external-order/opening-state API; this is not that authentic engine.
- `discovery/competitive_ga/funded_share_executor.py`: independent fixed-share
  funded-shadow bridge with its own row-based state and execution calculations.
  It leaves legacy fractional target-weight FundedShadow unchanged. Each tape
  has one funded bank; owner attribution does not create additional cash.
- `discovery/competitive_ga/test_share_order_execution.py`: 52 new cases.

Both consumers take the same immutable tape, preserve order quantities and
priority, and journal ordered fills/rejections, settlements, cash, receivables,
owner positions and open-marked NAV. They independently calculate fees, cash,
settlement, basis, inventory, age/peak and NAV. Shared code only validates inputs
and formats immutable output; neither implementation calls the other, uses a
native fill as oracle, or sizes a request. No existing GA6/GA7 policy was changed.

Invalid dates, negative/nonfinite cash, malformed owners, noninteger shares,
unsupported actions/settlement/version, missing/duplicate prices, noncausal
observation labels, incomplete held/event coverage and declared corporate actions
are rejected before either consumer creates mutable state. Insufficient cash,
owner inventory or aggregate share capacity is an all-or-none order rejection;
partial execution is deliberately unsupported. Explicit no-action coverage is a
caller assertion, not certified event provenance. Open labels cannot prove
actual source availability. This boundary must remain downstream of existing
eligibility, causality and risk gates.

## Independent evidence

The hand-calculated constant-$10 fixture starts at $100, buys four shares for
GA6 and two for GA7 with 1% fees, adds one GA6 share, reduces two, then exits both
owners. Opening MARK cash is $39.40, $29.30, $49.10; NAV is $99.40, $99.10,
$98.60. Terminal positions are empty with $49.50 still receivable and $1.40 total
fees. Both independently reproduce those dollar oracles and identical journals.

Other tests exercise existing raw/basis/age/peak state, a preexisting receivable,
T+1 settlement, rejection of same-open sale-proceeds funding, capacity smaller
than requested quantity, cash/inventory rejection, reversed priority, overlapping
owners, add/reduce/exit, changing opening prices, weighted basis, caller
immutability, and per-MARK cashflow conservation. Adversarial late-session event
or price failures reject the whole tape before execution. Test values are
fixtures, not synthetic research observations or invented market controls.

No new real-prefix common-tape diagnostic was run. Phase 7's observed orders
were endogenous to different holdings, priority and sizing; treating either
engine's fills as the shared independent request oracle would not resolve that
problem. Certified event coverage and upstream control provenance remain
unavailable. No market/proof values were newly decoded by this work; existing
bounded source tests retain their previous cutoffs.

The observed shadow-minus-native marked NAV difference remains
**-$2,758.3122922965413**. Fixed-share fixture parity establishes accounting under
this explicit contract only. It does not attribute that original discrepancy,
prove equal endogenous strategies, or show native sector/stop sizing equivalence.

## Validation

Required full bounded command:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
git diff --check
```

Final full-suite result: **475 passed**, no failures or skips. Read-only elevated
access was required for existing archive imports. The ordinary-sandbox attempt
had 471 passes, three known archive-access/import failures and one access-driven
skip; no test was weakened or bypassed. Final diff check passed. The cloud runtime
skill was read; its environment-status tool remains unavailable. No network or
credential discovery was needed.

## Remaining blockers and next bounded integration

1. Add a versioned external-share-order/opening-state seam to the authentic native
   replay, preserving its endogenous mode; obtain authentic ordered fill/state
   exports. Compare that implementation against both references on nonempty
   positions and T+1 fixtures before any actual market comparison. Native
   endogenous parity remains explicitly blocked until then.
2. Keep sizing, utility ordering, integer rounding, stop budgets and portfolio/
   sector capacity upstream. Freeze an independently specified common request
   tape only after governing these policies; fixed-tape accounting parity cannot
   substitute for recomputing endogenous held decisions.
3. Obtain certified corporate-action/security identity, adjustment, event/pay-date
   and settlement contracts. v1 deliberately rejects actions; it cannot certify
   an unknown or partial event tape.
4. Supply synthetic dated PIT membership/earnings absence/publication coverage,
   niche mapping and verified model training cutoffs, plus causal risk/defense,
   gap/stop and stress-group inputs. Existing gates remain unchanged.
5. Obtain approved frozen-bank-linked GA4 held exits and jointly compatible
   Horizons stress/publication/normalization inputs. No exits, trajectories or
   historical-to-synthetic stress mappings were invented.
6. Independently mature ADD/REDUCE utility and fold evidence; then run the
   existing gated bounded manager with authentic four-family inputs and frozen
   validation. No full GA or proof evaluation is authorized by this phase.

Changes and this report are committed locally on the requested feature branch.
No push, merge, main change, brokerage operation, external service, credential
access, purchase or write under /opt/mts occurred.
