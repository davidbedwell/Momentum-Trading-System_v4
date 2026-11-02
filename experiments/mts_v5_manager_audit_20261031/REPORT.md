# MTS v5 competitive manager audit

Audit executed 2026-11-01 UTC; requested artifact label 20261031. **Verdict: functional research components, incomplete end-to-end manager; BLOCKED for promotion.** No live deployment, historical-data changes, heldout outcome reads, GA search, broker calls, or package installation. Passing component tests are not evidence of integrated functionality.

## Checkout and controlling design

Actual checkout: `/opt/Momentum-Trading-System_v5-alpha`; origin `git@github.com:davidbedwell/Momentum-Trading-System_v5-alpha.git`; HEAD `1a1be890b41e1470cdef19ff8efb266f4dad7134`. The starting workspace is a different sector research repository. V5 has four tracked modifications and substantial untracked manager work; `source_git_status.txt` records it. Audited the **working tree**, not merely HEAD. No AGENTS.md was found in v5.

All v5 Python and associated local documents were copied into `v5_snapshot/` before tests. `source_hashes.json` records source Python SHA256 values. Source checkout and its dirty files were left unchanged.

Controlling requirements inspected:

- V5 `ARCHITECTURE_RECOVERY_RULES.md`: governed Nexus, separate discovery/execution, no execution claims without tests.
- `TRADING_ENGINE_PORTFOLIO3_CHARTER.md`: shared $100k, next-open, costs/actions, T+1, defense matching benchmark, owner-native management, symbol/sector/correlation and 2% risk limits, frozen validation.
- `CHROMOSOME_MANAGER_COMPLETION_TASK.md`: daily PIT controlling niche; comparable net EV/reliability/marginal contribution; specialists → related → transferable → NO_TRADE; incumbent rules preserved; SGOV/cash; CAGR objective subject to 20% MDD. Authentic archive/evaluator parity is a separate required milestone.
- `FUNCTIONAL_SLICE_REPORT.md` and `PHASE9_ENGINEERING_REPORT.md`: useful scope history, independently checked against executable behavior rather than accepted as certification.
- Older v4 `Architecture/DECISION_ARCHITECTURE.md`, available in `/opt/mts/ga6-git-backup`: finite portfolio state and separation of execution/global portfolio risk. Original `/opt/mts/thunder-migration` is permission denied; inspected accessible backup and research implementations, not an assumed complete live v4 installation.

V5 source references below are relative to the actual checkout and preserved in `v5_snapshot/`. No external web research was needed for this local-code audit.

## Functionality matrix and executable evidence

| Requirement | Status in active niche-manager path | Evidence |
| --- | --- | --- |
| PIT controlling niche | Partial | `functional_niche_manager.py:25–45` checks observation date, earlier model training, finite distances and deterministic overlap/controller. Caller supplies classifier/eligibility/native feature provenance. `causal_niche_classifier.py` explicitly uses synthetic fixed centers. Prefix tests pass; authentic input PIT is not established. |
| Eligible specialist and fallback | Partial | `functional_niche_manager.py:215–272`: entry eligibility and positive conditional EV; specialist priority works; general GA6 fallback works; nonpositive EV abstains. `hierarchical_search.py:19–26` rejects other named niches before EV ranking, so related-niche fallback is missing. Default without `conditional_ev` uses rotation, not profitable/risk-adjusted ranking. |
| ENTER/HOLD/ADD/REDUCE/EXIT | Implemented in bounded fixture | `functional_niche_manager.py:208–240,325–371`; owner retains management after eligibility/niche loss. GA7 native daily producer fixture executes all five decisions and four actual fills. GA6/GA7 mixed fixture competes on one bank, but does not establish original evaluator parity. |
| Cash, settlement, ownership | Implemented research baseline | `kernel.py:51–57,105–139`; settled cash only, buy fees, T+1 sale receivables in manager; `position_fill_book.py` tracks owner/basis/shares. Independent session-by-session cash + receivable + inventory reconciliation passed. Final receivables and pending orders stay visible. |
| Portfolio capital competition | Partial / defective global rank | `functional_niche_manager.py:185–186,325–352,373–411`: ticker-sorted allocation, optional evidence-based incumbent release. Existing mixed release tests pass; superior late ticker receives no funding when earlier low-EV names exhaust cash. No unified global marginal opportunity rank. Released proceeds remain settlement deferred, correctly. |
| Risk ≤2% equity per trade | **Not enforced on ordinary active path** | `Candidate.stop` constrained ≤.02, but this is a price-stop fraction, not equity-at-risk enforcement. Manager emits `Signal` without risk inputs and never installs `RiskSnapshot`. `kernel.py:77–103` applies explicit risk sizing only on evidence-based scaling or optional snapshot. Ordinary entry accepts .8 stop/gap inputs at .10 weight: modeled risk .08 equity. Separate `risk.py` tests pass but do not make it active. |
| Costs / next-open | Partial / implemented respectively | Kernel charges .001 each side and uses following open. It has no independent spread, impact, liquidity or variable slippage model. Synthetic independent fee/NAV identities pass; realistic cost certification remains missing. |
| SGOV | Missing integration | `liquidity_policy.py:18–34` returns targets only; no SGOV order/accrual call from `run_slice`. Idle $100k remains $100k. Existing standalone policy tests do not prove invested SGOV, yield, or sale settlement. |
| Defense | Partial | `defense_replay_adapter.py`, `streaming_defense.py`: external causal detector criteria feed persistence/recovery machine. Fixture parity with GA6 state controller passes. `run_slice` blocks entries and queues next-open exits. It calls `bank.day(date,bars)` without a defense flag: NAV tuples all report false even while defensive decisions/exits occur. Authentic detector features and paired defended-SPY parity remain uncertified. |
| NAV / MDD | NAV implemented; MDD control missing | `kernel.py:140–144` marks settled cash, receivables, holdings; fixture reconciles. `run_slice` returns NAV, not portfolio MDD monitoring/admission logic. Audit computes MDD including initial capital. Multi-name crash continues beyond 20%; no active MDD policy intervention or feasibility verdict. |
| Matured/shadow learning | Partial | Separate calibration, causal ledger and native shadow components have passing tests. Optional callbacks and shadow modes do not prove comparable, funded, after-cost incumbent/candidate/SGOV outcomes across original families. |

A stop model cannot guarantee a realized 2% loss ceiling across market gaps. Two distinct observations matter: the **modeled-risk gate bypass** above is an implementation defect; a 50% overnight gap also demonstrates that a configured 2% price stop cannot guarantee 2% realized equity loss. In the callback-HOLD fixture the manager adds no independent forced stop, consistent with preserving native decisions, so native protection must be authenticated and its risk budget enforced separately.

## Executed results

All tests ran on isolated copies; no GA was launched. `audit_smoke.py` uses at most 11 tickers and six sessions per scenario. Inputs are explicitly synthetic, including hand-authored GA7 genome and native proposal callbacks; none is represented as a learned archive.

- `targeted_tests_research_env.log`: **33 passed**, including lifecycle, PIT prefix/validation, eligibility loss, shared-bank funding, mixed families, competition/release, risk and liquidity components, native daily integration and residual shares.
- `additional_tests_corrected.log`: **16 passed**, defense state-controller comparison, defense adapter, calibrated priority, chronological manager integrity, causal ledger, shadow-learning interface.
- `reference_tests.log`: **11 passed, 2 deselected**, GA7 compiled synthetic replay and GA8 synthetic accounting/grammar. Real-data causality test was excluded. No real panel or final validation was read.
- `native_ga7_tests.log`: **5 passed**, original GA7 request replay entry/exit, reduction, defense, multileg cashflow and dividends. This tests native evaluator functionality; it does not compare native and v5 funded policies.
- `smoke_results.json`: audit probes completed, including expected defect demonstrations. Lifecycle NAV **$99,700.79156292375**, MDD **0.487599%**, four fills, fees **$13.72387543836**, final unsettled **$3,598.24265345167**. Independent accounting identity passes at every fixture session; realized P&L reconciles terminal NAV.
- Higher-EV `ZZZ` (.9 estimate) unfunded while ten alphabetically earlier stocks (.01 estimates) consume bankroll. Shared cash stays nonnegative; this is ranking failure, not money creation.
- Related-only positive-EV candidate produces no fills; specialist/general fallback and nonpositive-EV abstention behave as described above.
- Single-position gap/HOLD scenario finishes **$94,990**, MDD **5.01%**. Ordinary kernel entry separately accepts modeled **8%** equity risk versus **2%** limit.
- Defense exit executes following open; NAV defense flag remains false; flat-price round trip finishes **$99,980** with **$20** fees.
- Multi-name crash exceeds 20% MDD and replay continues; exact values saved in `smoke_results.json`.
- `legacy_smoke_results.json`: GA6 zero target becomes 3% entry; NaN score accepted; SCALE_IN ignored. Shared competition self-test passes. Older v4 tail-risk sizing returns $20k allocation, $2k estimated loss against $2k budget.

Initial workspace Python lacked NumPy, causing collection failure (`targeted_tests.log`). Reused existing `/opt/mts/.venv/bin/python`; installed nothing. One additional-test command named a nonexistent test file and ran no tests (`additional_tests.log`); corrected command produced the 16 passes above. These failed attempts are retained and excluded from pass totals. Total successful component tests: **65**; audit probe successes mean expected behavior/defect reproduction, not 65 assertions of system readiness.

## GA6, GA7/8 and older v4 comparison

1. `/opt/mts/ga6/shared_selector_allocation_20261025.py:4–26` is only an ENTER allocator: raw score sort, 3–10% weights, duplicate held-ticker exclusion, defense returns empty. No add/reduce/exit execution, risk denominator, fees, open prices, SGOV, NAV/MDD or classifier. `CandidateDecision.validate` checks action/weight/date/fold but not score finiteness; zero target is raised to the minimum allocation. Its neighboring `shared_selector_competition_20261025.py` permits arbitrary requested weights within capital and is likewise not a replay. These are not sufficient v5 managers.
2. GA7 has multiple distinct engines. `/opt/mts/ga7-deploy/ga7_unbounded/ga7/compiled_portfolio.py:11–123` uses integer shares, fixed capacity/three-per-sector, next-open signals, 10bp fee, cash yield proxy 2.97%, and immediate sale cash; it forces terminal liquidation. `/ga7/request_replay.py:33–247` has original endogenous native entry/add/reduce/exit sizing, T+1 sales, native ownership/account outcomes, cash yield, stop budgets and independent journal reconciliation. The latter is a more relevant native-parity target than treating compiled metrics or extracted arithmetic as equivalent.
3. V5 `PHASE9_ENGINEERING_REPORT.md:17–58` and `ga7_native_kernels.py` document hash-locked AST extraction of native arithmetic, excluding native endogenous sizing and richer outcome state. Reading actual `request_replay.py:132–154` confirms native opening-equity sizing, integer quantities and stop budgets differ from v5 fractional target weights/10% caps. Passing native fixtures cannot erase this mismatch.
4. `/opt/mts/ga8/Momentum-Trading-System_v4-ga8/ga8/engine.py:137–319` implements a separate funded portfolio replay with native gene exits/adds, costs, T+2 and dividend receivables, metrics and risk diagnostics. Synthetic accounting tests execute successfully. Its README explicitly disables SGOV, named defense, SPY, sector/earnings features without verified inputs. `GA8_LONG_EVOLUTION_SPEC.md` is a search requirement, not evidence those integrations work; no evolution was run. GA8 is not an admitted family in v5 `Candidate` validation.
5. Older v4 research `/opt/mts/mts_competitive_allocator_v1.py` and `mts_horizon_competitive_allocator_v2.py` apply cash/cost hurdles and risk/downside sizing to target weights; they do not supply complete execution. `mts_risk_sizing_v1.py:23–35` correctly sizes against equity loss estimates in the synthetic probe. Accessible backup `Research/GA6_Snapshot/selection_engine/risk_allocator.py` supplies PIT correlation/sector/cash proposals, explicitly PROPOSALS_ONLY. `mts_next_open_ledger_v1.py` is a separate cash-funded execution prototype with immediate sale cash, not complete T+1 parity. None should be silently substituted for a native v5 engine.

## Blockers, changes and next steps

**Primary authentic-input/parity blocker:** original GA6 NICHE identities cannot currently be authenticated against chronological PIT-NICHE identities. Inspected `/opt/mts/ga7-deploy/ga7_unbounded/niche_pit_manifest.json`: `CHRONOLOGY_VERIFIED_FEATURE_PROVENANCE_PENDING`, explicitly says identities differ. `niche_pit_audit.json`: `CHRONOLOGY_CHECKS_PASSED_SOURCE_PIT_UNVERIFIED`, with adjusted-price provenance warning. Required `/opt/mts/ga5_redesign/stocks31_40_corrected_v2/checkpoint.json.pit.json` does not exist. The frozen cohort and GA6 catalogue exist, but existence does not resolve model training timestamps, center identity, feature-value parity or original endogenous execution parity. `native_ga7_integration_gate.py:58–83` identifies these exact failures; this audit checked metadata, did not launch its historical diagnostic or inspect heldout returns.

**Engineering blockers:** global opportunity ranking, related-niche eligibility, mandatory ordinary-entry risk gate, SGOV implementation, defense NAV state, unified risk/sector/earnings/correlation controls, and MDD policy/admission integrated with the same manager. Existing `chronological_manager_replay.py:155–162` has an optional risk-provider seam, but it is a different replay interface without the controlling-niche routing. Fragmented working components are not a complete engine.

Changes in this audit: new isolated snapshots, source hashes/status/commit, executable bounded probes, test logs, result JSON, this report and reproduction script. **No trading-code fixes applied.** Broad allocation/risk changes would require explicit policy integration and parity work; a cosmetic local fix would not resolve the blockers. Existing source dirtiness was preserved.

Suggested sequence and conditional engineering estimates (one engineer, working days; not launch promises):

| Step | Concrete deliverable / exit criterion | ETA |
| --- | --- | --- |
| 1 | Preserve working tree; add regression tests for reproduced defects; repair defense reporting and reject nonfinite/zero GA6 proposals in isolated branch | 0.5 day |
| 2 | One shared close-time candidate queue with specialist/related/general tiers, comparable net EV, global capital rank, explicit abstention and settled-cash reservation | 1–2 days |
| 3 | Mandatory pre-fill risk metadata/budget, sector/correlation/earnings gates; retain native protective logic and report gap stress; integrate SGOV orders/settlement and correct defense state | 1–2 days |
| 4 | Unified NAV/MDD/feasibility reporting and defended benchmark fixtures, cost scenarios, source-to-v5 native sizing/accounting reconciliation | 1–2 days |
| 5 | Authentic bounded replay only after original niche metadata/mapping and native feature/value provenance pass; freeze and evaluate parity | 1–3 days after validated artifacts are available |

A reproducible integrated **synthetic** repair milestone is approximately **3–5 working days** with overlap across steps. Authentic launch ETA remains **blocked / unestimable** until data/model provenance and evaluator parity are resolved. No long GA should precede these gates; no 2026 heldout outcomes are needed to repair the synthetic functionality defects.
