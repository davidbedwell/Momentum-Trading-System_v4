# MTS v5 manager repair — 20261031

Executed 2026-11-01 UTC. **54 targeted synthetic tests pass in a writable copy of the actual dirty v5 source. Applying the repairs to the actual checkout is BLOCKED by this session's filesystem policy. This is not a completed in-place repair or a launch certification.**

## Delivery and preservation

Actual source: `/opt/Momentum-Trading-System_v5-alpha`, branch `codex/first-year-manager`, HEAD recorded in `source_head.txt`. Read the previous audit and actual architecture/recovery rules, Portfolio 3 charter, chromosome-manager assignment, functionality report, phase 9 engineering report and phase 4 readiness declaration.

Before code work, captured `source_git_status.txt`, `source_dirty.patch` and `source_head.txt`. The source has four tracked modifications and many untracked manager files. Captured hashes and copied 398 Python/document/configuration files, including the dirty and untracked source, into `v5_working_copy/`. No market datasets were copied or decoded. The copy is not a new engine: it contains the existing v5 manager and kernel, edited at their existing interfaces.

The session permits writes only under `/opt/mts/sector-leadership-independent` and `/tmp`; approval escalation is disabled. User authorization does not change this filesystem boundary. Asked for a writable actual checkout or writable-copy arrangement using the asynchronous question tool; no answer had arrived when this report was written. No attempt was made to bypass permissions. No branch/worktree/commit was created, and the actual v5 source remains unchanged. **The user-requested actual-checkout implementation remains outstanding.**

`preservation_check.json` verifies unchanged source git status, byte-identical tracked diff, and unchanged hashes for all 398 captured files. `repair.patch` contains only this repair's changes against the captured dirty tree, rather than a patch against HEAD that would absorb user changes. `changed_files.json` supplies baseline and repaired hashes. `git apply --check` against the actual source passes. This checks applicability without applying it; it is not deployment.

## Functional changes in the staged source

| File | Implemented behavior |
| --- | --- |
| `discovery/competitive_ga/functional_niche_manager.py` | Screen qualifying controlling-niche specialists, explicitly supplied related niche matches, then transferable candidates under the same eligibility and positive-net-EV rules. Choose the best viable tier per ticker; globally rank all resulting entries and native ADDs by supplied comparable marginal net EV. Reserve only settled cash including execution allowances. No raw GA6/GA7 score comparison. Missing/zero/negative EV produces abstention; nonfinite EV is rejected. Cache each estimate once per candidate/ticker/cutoff. Reject the old unpriced selector hook explicitly. Propagate stop/gap inputs to fills; report risk, costs, drawdown and safe cash state. Correct the closing NAV defense flag while preserving following-open liquidation. |
| `engines/portfolio_replay/kernel.py` | Mandatory ordinary-entry and ADD prefill loss sizing, in addition to existing scaling/snapshot controls. Size against execution-opening equity using `max(stop_distance, gap_risk) + round_trip_cost`, with modeled loss at most 2% of equity. Missing risk information assumes total loss. Retain native reductions/exits and existing exposure; refuse further increases when limits bind. Add proportional spread, slippage and impact scenario allowances to opening fill prices and actual cash/fee accounting. Monitor opening and closing NAV against initial capital/high-water mark, record MDD, and permanently halt new risk at a 20% drawdown breach. |
| `engines/portfolio_selector/shared_selector_engine_contract_20261025.py` | Reject nonfinite scores/weights; exclude zero/nonpositive ENTER proposals. Preserve ownership checks. |
| `engines/portfolio_selector/shared_selector_competition_20261025.py` | Reject nonfinite proposal/capital inputs; preserve zero-weight abstention and shared-capital ranking. Archived `legacy_reference` and external GA6 source remain untouched. |
| `tests/test_manager_repair_end_to_end.py` | 26 new bounded synthetic cases, parameterizations included. |
| `tests/test_functional_niche_manager.py`, `tests/test_mixed_ga6_ga7_functional.py`, `tests/test_paired_defense_functional.py` | Migrate synthetic fixtures to explicit net EV/gap assumptions and related-niche screening. Retain lifecycle, shared-bank, next-open, ownership, accounting and prefix assertions. |

For the related tier, the manager uses only noncontrolling identities explicitly present in the supplied native qualifying matches. It does not invent a center graph or historical niche identity mapping. The caller still owns the authenticity and chronology of classifier outputs and eligibility.

The EV callback contract is now explicit: comparable marginal net return per dollar over a common horizon, after execution costs, reliability and risk adjustments. This patch does not manufacture calibrated estimates. Without such estimates the funded manager abstains. Existing unpriced research callers therefore require migration. Selection genes can filter/rank within the winning niche tier; shared cash allocation follows the supplied marginal net EV. The linear per-dollar ranking does not optimize arbitrary nonlinear impact curves.

SGOV uses the expressly permitted **safe cash fallback**: no SGOV orders or invented Treasury yield, zero cash yield, and explicit mode/reason/settled/unsettled balances. Verified SGOV prices, distribution/pay dates and settlement are still required to enable invested SGOV. Existing sale receivables remain T+1 and cannot finance same-open purchases.

## Executed evidence

Reproduce with:

```bash
bash experiments/mts_v5_manager_repair_20261031/reproduce.sh
```

Uses the existing `/opt/mts/.venv/bin/python`; installed nothing. Final `regression_tests.log`: **54 passed, 0 failed**, comprising 26 new cases and 28 existing targeted regressions. No historical or native-source diagnostic was launched.

Hand-authored scenarios demonstrate:

- Higher-EV `ZZZ` executes first despite ten alphabetically earlier candidates; all buys together consume at most the one settled bankroll including fees. Entries and native additions share the global funding order.
- Specialist, related, transferable and NO_TRADE outcomes under identical positive-EV gates; unavailable and nonfinite estimates are handled explicitly.
- An ordinary request for 10% weight with 80% modeled downside is reduced to approximately `0.02 / 0.802` of opening equity under default fees. Missing gap inputs instead use `0.02 / 1.002`. Opening equity is recomputed when incumbent marks change.
- A gap larger than the declared model produces more than 2% realized equity loss despite passing modeled-risk admission. Gap stress is explicitly labeled unguaranteed. No synthetic stop overrides native HOLD.
- Current-close defense flags are correct; defense liquidation occurs at the following open, and proceeds remain receivable until settlement.
- With full spread .002, slippage .002 and impact .001, buy/sell prices are respectively `open * 1.004` and `open * .996`; independent cashflow, fees, realized P&L and terminal NAV reconcile.
- More than 20% portfolio drawdown latches admission before pending buys execute on an opening crash; later recovery does not reset it. Native HOLD/EXIT decisions retain ownership and timing. The policy reports the breach as infeasible.
- Owner-native ENTER/HOLD/ADD/REDUCE/EXIT survives entry-eligibility loss; prefix replay decisions/fills/NAV match. Sale proceeds cannot fund same-open purchases.
- Explicit cash fallback creates neither trades nor yield. GA6 zero proposals create no position; NaN/infinite proposals fail closed.

Initial new tests: 20 passed (`end_to_end_tests.log`). Initial regression run: 22 passed, 6 failed (`regression_tests_initial.log`), because old fixtures expected unpriced entries or excluded related matches. Migrated those fixtures to the new explicit input contract without removing their behavioral/accounting assertions. Final augmented run: 54 passed. The initial failures remain retained as evidence. The full repository suite was not run; no claim is made that every legacy unpriced research caller has migrated.

## Unresolved issues and next milestones

1. **Apply to the actual checkout.** Requires a filesystem configuration allowing writes there, or an agreed writable actual working copy. Recheck every baseline hash and git status immediately before applying; rerun the bounded command there. Preserve dirty files and do not reset/clean. Only commit these eight files if safely separable and authorized by the writable environment. This is the immediate delivery blocker, not a trading-code readiness conclusion.
2. **Authentic provenance/native parity remains BLOCKED.** No historical PIT niche labels, archived training lineage, GA6/7 native sizing/accounting parity, membership, earnings or action provenance was fabricated. The audit's missing original niche metadata and evaluator differences remain. Do not promote or start long GA work on synthetic test evidence.
3. **Risk certification remains separate.** A 2% modeled-loss gate cannot guarantee losses across arbitrary gaps; the total-loss stress is reported. A 20% MDD admission halt cannot undo a gap or guarantee a realized drawdown ceiling. The policy deliberately preserves native exits; a breach disqualifies feasibility rather than inventing a liquidation policy. Aggregate incumbent risk, sector/correlation and earnings gates still require dated inputs and unified integration.
4. **Costs/liquidity.** Configurable spread/slippage/impact are deterministic scenario allowances, not fitted liquidity/volume estimates. Caller-supplied EV must reflect those same assumptions; no authentic cost calibration is claimed. Existing native-shadow replay is not newly certified for these execution allowances. Implement verified SGOV lifecycle only after its data and accounting contract is supplied; safe cash is the current executable behavior.
5. **Compatibility and validation.** Migrate remaining synthetic experiment callers that relied on unpriced rotation; run additional relevant bounded tests as each caller is migrated. Then perform governed authentic bounded native comparison only when provenance gates pass. No launch date is defensible before those dependencies are resolved.

No live orders, deployments, network calls, long GA runs, package installation, historical-data edits, or sealed-holdout reads occurred.
