# Phase 5 engineering report

2026-10-28; branch `codex/first-year-manager`.

**BLOCKED / NOT AUTHENTIC FOUR-FAMILY LAUNCH READY.** All four families and
existing proof/input/ownership/scaling gates remain. The 867-session proof seal
from 2023-07-03 remains closed. No GA experiment, brokerage access, push, merge,
or research-source modification occurred.

## Executable changes

`engines/portfolio_replay/risk.py` supplies an explicit immutable close-dated
RiskSnapshot: per-name stop and gap loss fractions, correlated group, reference
close, portfolio loss budget, group weight cap, gross cap and maximum opening
gap. The shared kernel includes ALL incumbent weights, applies requested
reductions before reserving additions in deterministic priority order, and clips
new exposure to aggregate limits. Loss is the conservative sum of weight times
max(stop,gap); correlated exposure is a caller-declared common-stress group,
not an estimated covariance matrix. No missing market estimates are invented.
Missing incumbent risk fails closed; missing new-name risk/reference blocks
that increase. Splits adjust the reference used to assess opening gaps.

`chronological_manager_replay.run` and `first_year_manager.bounded_replay` accept
risk_provider(date,session,bars,holdings). It must return that close's snapshot;
the kernel requires its date to precede execution and uses next-open prices,
never next-close prices, for feasibility. risk_audit exposes rejected/clipped
targets. Settled cash and fees still constrain fills, and sale proceeds cannot
fund same-open purchases. Invalid/nonfinite/duplicate pending targets fail.
Limits constrain increases; they do not force liquidation of appreciated or
over-budget incumbents. Mandatory exits and defense remain intact. The provider
is optional for legacy research calls; its absence is NOT certification or an
authentic risk input contract. Existing input gates were not relaxed.

`action_utility.paired` independently evaluates a funded held-state intervention
against HOLD with identical opening state and later close mark. It accounts for
fees and cash feasibility, rejects nonchronological/out-of-training maturities,
and returns action-specific utility outcomes. ADD/REDUCE/EXIT calibration now
requires FAMILY_UTILITY/action context, separately from FAMILY_ENTRY. Entry
returns alone cannot authorize ADD. Existing positive scaling fixtures now
explicitly supply separate utility evidence; fold gates remain required. Native
mandatory risk exits/reductions still bypass utility ranking as before.

`phase5_diagnostics` executes native GA7 replay_requests and the independent
funded shadow on the same fixed open training prefix and checkpoint, with no
identity search or tuning. It also probes held interventions against HOLD and
contrasts them with the unweighted next-open-to-close entry-only price return.
Those metrics have different denominators by design; they are not interchangeable
estimates. Utility probes isolate each position at its observed exposure using
a complementary cash balance; they are not jointly fundable portfolio actions.
There is no fitted model, significance claim, or supplied profitable calibration.

## Actual bounded diagnostic

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m discovery.competitive_ga.phase5_diagnostics
```

Output: `PHASE5_DIAGNOSTICS.json`. Market columns are predicate-bounded through
2022-12-30, with the last 32 training sessions (2022-11-17–2022-12-30), 500 names.
The full feature cache content hash is checked; raw-file hashing is byte identity,
not sealed price decoding. No proof price/outcome values are loaded. The existing
Phase 3 cache and native installation are dependencies.

- Native GA7: 15,500 requests; terminal NAV 98,606.18180919687;
  independent native cashflow residual -1.4551915228366852e-11.
- Funded shadow: 601 fills; marked NAV 95,856.81920838593.
- Shadow minus native terminal NAV: -2,749.3626008109422. This is an explicit
  discrepancy, NOT native-funded ledger parity or a shared-bank result.
- Action observations: ENTER 8,990; EXIT 272; HOLD 301; REDUCE 52.
- Mature next-session REDUCE probes: 50; mean incremental NAV utility
  0.000047283989139355114; entry-only price return mean -0.0053530356213912535.
- Mature EXIT probes: 264; mean incremental NAV utility
  -0.0002761252743737223; entry-only price return mean 0.006900177375301853.
- ADD probes: **0**, utility unknown. The implementation is adversarially tested,
  but ADD utility is not empirically validated by this window.

The comparison explicitly preserves differences: native integer versus fractional
shares, capacity and three-per-sector constraints, incremental .03 native ADD
versus target weights, integer-half native REDUCE versus next-open target sizing,
native risk sizing, and native terminal close liquidation versus retained shadow
holdings. Both use .001 fees and T+1 proceeds; native cash yield is disabled.
No complete independent replica of the native ledger is asserted. All-true
eligibility is diagnostic, training lineage is unknown and event defaults are
uncertified. Overlapping probes are not independent statistical samples.

## Read-only provenance and GA4 exit investigation

Re-read actual sources with elevated read-only archive access:

```bash
rg -n 'Horizon observation|diagnostic|archive|bank|provenance|publication|CHRONOLOGY' \
 /opt/mts/thunder-migration/mts-layered-run-20261007/Core/layered_ga/ga4_horizon_contract.py \
 /opt/mts/ga7-deploy/ga7_unbounded/niche_pit_manifest.json
rg --files /opt/mts/thunder-migration/mts-layered-run-20261007/Core | rg 'exit|provenance'
rg -n 'exit|diagnostic|bank|archive' \
 /opt/mts/thunder-migration/mts-layered-run-20261007/Core/layered_ga/gen1_sequential_exit.py
```

GA4 horizon contract line 3 explicitly says horizon observation does not imply a
fixed holding-period exit. Discovered `gen1_sequential_exit.py` is a deterministic
counterfactual trade-path evaluator accepting a caller exit_policy, with forced
original-horizon final exit (lines 7–10, 26–29). This is executable infrastructure,
not an approved daily policy linked to the frozen bank. No new approved linkage
was established. PIT manifest still reports
CHRONOLOGY_VERIFIED_FEATURE_PROVENANCE_PENDING, annual expanding 13 centers,
18 models and 329,406 rows from exploratory79_ga4_enriched.parquet; it explicitly
says source PIT provenance is not independently certified. No synthetic identity
mapping, publication timestamp contract or archive training cutoff was recovered.
These findings confirm blockers, not certification.

## Validation and remaining blockers

Final command (read-only elevated native archive access, bytecode disabled):

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest \
 --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
git diff --check
```

**398 passed in 5.38 seconds**; diff check passed. New tests exercise aggregate
incumbents/correlated exposures, opening-gap rejection with exits preserved,
missing/same-date risk, split references, next-close-independent fill parity,
nonfinite targets, independent dollar cashflow oracles, training/maturity bounds,
and entry-evidence rejection for ADD. Initial sandbox full run had three archive
access failures and three expected old ADD-fixture failures; these were resolved
by authorized read-only execution and separate utility fixtures, respectively.
No skips or failures remain in the final full run.

Actual synthetic risk/gap/group inputs are still missing; no authentic capital
was forced through the gates. Native-funded comparison exposes differences rather
than eliminating them. Independent ADD research evidence, long-horizon/fold utility
validation and corporate-action/settlement convention parity remain incomplete.
GA4 approved exit linkage, jointly compatible Horizons stress, PIT eligibility,
earnings, publication dates and verified model lineage still block all-family
launch. Phase 4 readiness evidence is preserved unchanged; no new certification
or proof authorization is implied. All implementation and evidence are committed
locally on the requested branch.
