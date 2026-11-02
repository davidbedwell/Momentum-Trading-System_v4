# Phase 6 engineering report

2026-10-28; branch `codex/first-year-manager`.

**BLOCKED / NOT FOUR-FAMILY LAUNCH READY.** The 867-session proof remains sealed.
This phase completed a scoped native accounting bridge, corrected an aggregate
risk execution defect, and exercised two-family shared-bank held actions. It did
not reconcile the original native/funded-shadow strategy paths or certify any
family. No full GA, push, merge, brokerage action, credential change or write to
`/opt/mts` occurred.

## Accounting bridge and observed evidence

`ga7_ledger_bridge.replay` independently executes the frozen single-genome native
request ledger. It does not call the native fill/accounting/priority code. It
returns daily settled cash, receivables, holdings, marked NAV, fills, rejections,
cash journal and terminal fees, with independent fill-based cashflow identities
before and after terminal liquidation. Native requests remain the policy input;
this is an accounting comparison, not an independent policy oracle.

The opening contract is identical: $100,000 settled cash, no holdings or
receivables, .001 fees, T+1 sale settlement, zero cash yield. Native priority,
integer shares, integer-half REDUCE (one share fully exits), incremental INCREASE,
stop-based sizing, per-genome capacity, three-per-sector capacity, eligibility
and prior/current defense gates are reproduced. Sizing deliberately excludes
unsettled proceeds, as native does; proceeds remain assets for marked NAV. Sales
cannot fund purchases at the same open. No defect in native cash accounting was
established by this comparison.

Corporate-action scope is deliberately narrow: adjusted prices and ex-date cash
dividends. Explicit non-unit raw split events are rejected; raw-split and dividend
pay-date equivalence are not asserted. The actual diagnostic panels have no
certified event tape; missing event fields use the existing native diagnostic
convention, not evidence of corporate-action absence. Dividend fixtures exercise
that convention independently; they do not certify synthetic-market events.

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m discovery.competitive_ga.phase6_diagnostics
```

`PHASE6_DIAGNOSTICS.json` records the same 32 sessions, 500 names and checkpoint
as Phase 5, 2022-11-17 through 2022-12-30. Source hashes are checked against Phase
5. `training_panels` was extracted without changing the bounded market-read
filters. Both raw prices and cached features are predicate-bounded through
2022-12-30; byte hashing verifies identity without decoding sealed observations.
There is no new calibration, selection, lineage certification or proof access.

| Prefix sessions | Native terminal NAV | Bridge terminal NAV | Difference |
| --- | ---: | ---: | ---: |
| 2 | 99,529.1102472906 | 99,529.1102472906 | 0 |
| 8 | 99,095.93825454182 | 99,095.93825454182 | 0 |
| 16 | 98,804.25531359027 | 98,804.25531359027 | 0 |
| 32 | 98,606.18180919687 | 98,606.18180919687 | 0 |

Maximum full-window independent cashflow residual: 2.91e-11. The bridge records
97 executions including terminal sells. Phase 5's separate funded shadow recorded
601 executions and retained terminal holdings; those counts are not identical
fill definitions. Native terminal fee is $8.9496914856. Comparing both at terminal
marked value changes the original shadow-minus-native difference from
-$2,749.3626008109 to **-$2,758.3122922965**. Terminal liquidation does not explain
the discrepancy.

One-change-at-a-time fixed-request sensitivities relative to native:

| Changed convention | Terminal NAV change |
| --- | ---: |
| Fractional shares and fractional-half reductions | +9.3872152477 |
| Remove portfolio/sector capacity limits | +6,673.7380438830 |
| Include receivables in sizing equity, still spend only settled cash | -144.1307938459 |
| Retain terminal holdings | +8.9496914856 |

The JSON also records an ordered cumulative waterfall. Its +$8,756.35 total
leaves -$11,505.72 versus the original shadow and is **not an attribution of the
original gap**. Interactions are large: receivable sizing alone and after removing
capacity even have different signs. Releasing capacity creates holdings absent
from the native policy state; their subsequent requests were never recomputed.
Those counterfactuals measure fixed-tape accounting sensitivity, not investable
strategy returns. Neither integer shares nor terminal liquidation alone explains
the gap; capacity and policy-state divergence require further investigation.

Remaining unallocated differences include endogenous held-state/actions,
alphabetical shadow versus native utility priority, target weights versus native
incremental/stop sizing, and their interactions. No equality of native and funded
shadow is claimed. The bridge does not cover niche banks, nonempty opening
portfolios, every native daily internal state, or certified corporate actions.

## Actual execution defect corrected

The aggregate risk limiter interpolated the **maximum** correlated-group weight.
That nonlinear metric cannot determine another group's available capacity. When
one group was at cap it could reject all of a feasible addition to a smaller
group; when an appreciated incumbent was over cap it could allow that smaller
group to exceed its own cap without increasing the global maximum.

`engines/portfolio_replay/risk.py` now bounds incremental loss, the affected
group's exposure and gross exposure directly. It preserves incumbents and
reductions and restricts additions. Regression cases exercise both a full and an
over-cap unrelated incumbent, with an independently specified 25% new-group cap.
This is a demonstrated execution defect, separate from native/shadow convention
differences; no claim is made that it caused the Phase 5 gap (that diagnostic did
not supply this risk control).

## Causal two-family execution and missing inputs

The eight-session shared-bank integration fixture invokes GA6 and GA7 native
producer adapters on executed owner state. GA7 uses its actual adapter thresholds;
GA6 uses an explicitly injected evaluator. Test prices, risk observations,
provenance labels and matured entry outcomes are **fixtures**, not observed
synthetic-market research evidence. Both owners enter the same $100k bank after
strictly earlier maturity, emit ADD on held profitable positions, and get no
additional fills from entry evidence alone. Native REDUCE/EXIT execute at the next
open, owners retain attribution, T+1 cash and owner P&L reconcile, and each close
supplies a dated risk snapshot. Missing new-name risk references block that name;
missing held GA7 features and incorrectly dated snapshots raise errors.

Adversarial bridge tests also cover native sector/priority parity, dividends,
REDUCE/EXIT, single-share reduction, same-open proceeds exclusion, next-close
independence of opening fills, terminal fee identity, missing held bars, duplicate
or out-of-range requests, nonfinite prices and unsupported raw splits.

The actual market diagnostic uses only observed synthetic OHLCV/features. No
risk/gap/group publications were recovered or invented. Thus an authentic dated
risk-controlled cross-family replay remains gated, rather than being represented
by the integration fixture. Separate incremental utility, fold evidence and
verified family model training cutoffs remain required for authentic ADD or
scaling. There is still no empirical ADD validation in the Phase 5 window.

## Authorized read-only provenance investigation

Re-read the GA4 horizon contract and `gen1_sequential_exit.py` under the native
archive with elevated **read-only** access after ordinary access was denied.
The contract still explicitly says horizon observation does not imply a fixed
holding-period exit. The evaluator still accepts a caller `exit_policy` and
forces original-horizon liquidation. Neither establishes an approved policy
linked to the frozen GA4 bank. The readable GA7 PIT manifest still reports
`CHRONOLOGY_VERIFIED_FEATURE_PROVENANCE_PENDING`.

A filename-only scan under
`/opt/mts/synthetic-market-lab/runs/five_iteration_inputs` found no filenames
matching stress/horizon/VIX/credit/funding/manifest. That bounded negative search
is not proof that no source exists elsewhere. Phase 4's documented missing joint
Horizons source/publication/normalization contract remains unresolved. No stress
proxy, identity mapping or exit policy was fabricated or substituted.

## Validation and remaining launch blockers

Final full bounded suite, using authorized read-only native imports:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest \
  --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
git diff --check
```

**411 passed in 5.35 seconds**, no skips or failures; diff check passed. Targeted
fixture development failures were corrected before this final run. The runtime
skill's environment-status tool was unavailable in the exposed tool catalogue;
no network or credential discovery was needed.

Unresolved blockers: original native/shadow endogenous ledger reconciliation;
certified corporate-action, pay-date and settlement contracts; actual dated
synthetic risk/defense inputs; PIT eligibility/earnings and publication coverage;
verified model lineage; approved GA4 exit linkage; jointly compatible Horizons
stress; complete authorized boundary/held action coverage; independently matured
ADD utility/fold evidence; frozen validation. Phase 4 readiness and Phase 5
captured evidence remain unchanged. The 867-session proof remains closed.

Changes and evidence are committed locally on the feature branch. The supervisor
retains push/merge responsibility.
