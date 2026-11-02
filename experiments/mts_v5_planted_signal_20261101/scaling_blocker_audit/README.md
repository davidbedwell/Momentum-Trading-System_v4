# Scaling blocker audit — completed, local synthetic diagnostics

**Root cause: the 2% per-trade loss allowance is incorrectly reused as a shared portfolio risk budget for scaled ADDs.** Ordinary entries use a per-position rule. The manager and kernel impose an additional aggregate restriction only on evidence-based scaling. This contradicts the specified per-trade rule; raising concentration limits alone cannot fix it.

All production sources and Stage2 inputs are unchanged (SHA-256 in report.json). No GA, fitting, search, evidence relaxation, or production patch application. Completed within the 15-minute work limit. Twelve seeds are 1101–1112; 252 sessions, 24 synthetic assets, same fixed tapes. These are invented SYN tickers and synthetic callbacks, not historical stock evidence or native learned alpha.

The 72 unchanged-policy instrumented replays reproduce all recorded Stage2_fix 15/20% metrics to 1e-10 across all three qualities. First-seed decisions also match saved audit JSON exactly after stripping added diagnostic fields. The prior artifacts did **not** retain full decision/risk data for all 12 seeds; this audit regenerates them and verifies the recorded summaries, rather than claiming missing logs existed. Saved full replays: `original_decision_risk.jsonl.gz`. Per-opportunity decomposition and queue predecessors: `unique_opportunities.jsonl.gz`.

## Actual execution path and intended rule

1. The Stage1 base callback emits ENTER/HOLD/EXIT, never ADD. The Stage2 scaling wrapper converts a held HOLD with positive net EV and weight below target into an ADD. Thus “native ADD” in this experiment means a synthetic wrapper request, not independently validated native-model scaling. See [synthetic ADD generation](/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/stage2_fix/support.py:28) and [underlying callback](/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/run.py:188).
2. The manager computes current weight from marked holdings/NAV, obtains causal evidence, and sums **all other funded positions** at `weight * (max(stop, gap) + round_trip_cost)`. See [evidence and other-position risk](/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/stage2_fix/functional_niche_manager.py:353). Even positions scheduled to exit still enter this close-time sum.
3. Evidence approval occurs before settled cash reservation. `allowed_target` is called without other risk here, so its default is zero. The manager then independently sets `remaining_risk=max(0, .02-other_equity_risk-reserved_loss)` and clips the candidate's **total target**, before funding the increment. See [reservation and wrong aggregate gate](/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/stage2_fix/functional_niche_manager.py:447).
4. At the next open, the kernel sorts pending signals again and calls `allowed_target` with `max(signal.other_equity_risk,reserved_risk)`. This retains the stale close-time floor and adds a second aggregate constraint. Kernel reservation occurs before actual cash fills and does not include the cost allowance at that stage. See [execution aggregate floor](/opt/Momentum-Trading-System_v5-alpha/engines/portfolio_replay/kernel.py:103).
5. A separate mandatory gate already constrains each candidate: `target_weight * (max(stop,gap) + round_trip_cost) <= .02`. It applies to ordinary and scaled increases, uses opening NAV, and retains existing exposure if drift already exceeds the limit. The minimal correction keeps this gate, evidence, cash, fees, settlement, MDD latch and native exits. See [mandatory per-position gate](/opt/Momentum-Trading-System_v5-alpha/engines/portfolio_replay/kernel.py:128).

The conservative interpretation used here treats the entire scaled position as the candidate trade. It does not grant a fresh 2% allowance to every incremental ADD. An **optional portfolio aggregate guard** must have its own explicit configuration/limit and coherent holdings/queued-order accounting; it must not silently reuse the mandatory 2% per-trade value.

There is no blanket literal double-count. In the manager, other-position risk covers existing holdings and `reserved_loss` generally covers distinct funded increments, including ordinary entrants. The kernel uses `max`, not `other + reserved`. The semantic defect is applying a common budget; the two stages both enforce it without multiplying it by two. Stale risk floors and pre-fill reservations can be additionally conservative. Candidate current weight is already part of its total target; it is not subtracted again as another holding. The eight showcased failures have `reserved_loss=0`, proving queue-risk double-count is unnecessary to produce the defect.

At 80% invested entirely in the lowest modeled risk assets, modeled aggregate loss is already 80% × 3.3% = 2.64%. Seven other 10% holdings alone consume 2.31%, so even an individually safe candidate can receive zero incremental budget.

## Distinct blockers and overlaps

Each row is counted once per `(seed, quality, variant, ticker, decision date)`, not once per rejection flag or kernel attempt. These are simultaneous **full-target counterfactual constraints**, not mutually exclusive causes. Category C is partitioned below; actual stage-reached denial counts are also in report.json.

A = positive-EV incumbent lacked ADD; B = failed evidence tier; C = modeled risk; D = evidence-approved concentration cap; E = initial settled cash shortage; F = earlier queue commitments consume cash. A is zero for all positive-EV incumbent dates in these scaling tapes because the wrapper explicitly converts them all. An ADD-only denominator cannot logically contain A. Across all incumbent dates, many HOLD/EXIT decisions do not request ADD: these are recorded in `native_incumbent_action_counts`, and predominantly have nonpositive EV. The 10% baseline callback requests no ADD by construction.

| Quality / target | Unique ADDs | A | B | C | D | E | F |
|---|---:|---:|---:|---:|---:|---:|---:|
| strong_scale15 | 16996 | 0 | 5523 | 16996 | 5523 | 4864 | 2095 |
| strong_scale20 | 16996 | 0 | 10292 | 16996 | 10292 | 6653 | 2307 |
| weak_scale15 | 1750 | 0 | 1543 | 1704 | 1543 | 145 | 14 |
| weak_scale20 | 1750 | 0 | 1749 | 1714 | 1749 | 200 | 19 |
| misnull_scale15 | 17309 | 0 | 12217 | 17305 | 12217 | 5074 | 2181 |
| misnull_scale20 | 17309 | 0 | 14853 | 17306 | 14853 | 6792 | 2396 |

B and D overlap exactly at the full-target level here: failed prerequisites lower the concentration tier. They are separate questions about evidence and sizing, not additive blocker populations. The 20% tier may fail while 15% remains admissible. No separate arbitrary 10% hard cap blocks an evidence-approved scale.

| Quality / target | Candidate alone >2% | Other holdings block standalone-safe target | Queue risk only | Evidence passes full tier | Evidence passes + other block + initial cash sufficient |
|---|---:|---:|---:|---:|---:|
| strong_scale15 | 4418 | 12578 | 0 | 11473 | 5465 |
| strong_scale20 | 8510 | 8486 | 0 | 6704 | 1578 |
| weak_scale15 | 362 | 1339 | 3 | 207 | 130 |
| weak_scale20 | 843 | 870 | 1 | 1 | 0 |
| misnull_scale15 | 3963 | 13341 | 1 | 5092 | 2509 |
| misnull_scale20 | 8309 | 8997 | 0 | 2456 | 614 |

For strong/15%, other holdings **alone** already exceed 2% on 16,981 of 16,996 requests. The aggregate gate denies **any** otherwise standalone-safe increment after evidence allows an increment on 8,367 dates. This differs from full-target constraints, where partial funding could still be possible.

For strong/15%, cash category E splits into 2,670 dates where receivables would cover the shortfall if spendable, and 2,194 dates where even cash plus receivables is insufficient. Sales are never credited to the current close budget. Receivables are NAV assets but cannot fund purchases until T+1. Kernel sells before buys, but sale proceeds are added to unsettled cash after purchases. See [settlement and NAV](/opt/Momentum-Trading-System_v5-alpha/engines/portfolio_replay/kernel.py:90) and [sale, cash and funding order](/opt/Momentum-Trading-System_v5-alpha/engines/portfolio_replay/kernel.py:159). Close queue order is descending marginal net EV, then ticker/family/chromosome; execution uses score/ticker/chromosome (all families here are GA7). F measures the cash committed to higher-ranked requests, not a claim that reordering improves returns.

Full exact overlap histograms are saved per group in `report.json`. Strong/15% overlap:

| Simultaneous categories | Unique ADDs |
|---|---:|
| B+C+D | 3321 |
| B+C+D+F | 543 |
| B+C+D+E | 1449 |
| B+C+D+E+F | 210 |
| C | 7307 |
| C+E | 2824 |
| C+F | 961 |
| C+E+F | 381 |

Collapsing the 15/20 variants gives 36,055 unique `(seed, quality, ticker, date)` opportunities; category membership is the union across requested targets, not a claim that target-specific requirements are identical. The report saves these union counts separately; primary tables preserve requested target.

## Exact evidence failures and independence

| Quality / target | matured_trades | position_profitable | positive_net_ev | forward_folds | current_signal_confirmed | historical_mdd | evidence missing |
|---|---:|---:|---:|---:|---:|---:|---:|
| strong_scale15 | 2670 | 3441 | 286 | 0 | 0 | 0 | 0 |
| strong_scale20 | 4498 | 3441 | 286 | 8626 | 0 | 0 | 0 |
| weak_scale15 | 1322 | 732 | 303 | 0 | 0 | 0 | 0 |
| weak_scale20 | 1745 | 732 | 303 | 1011 | 0 | 0 | 0 |
| misnull_scale15 | 2666 | 9365 | 4558 | 0 | 0 | 0 | 0 |
| misnull_scale20 | 4364 | 9365 | 4558 | 11140 | 0 | 0 | 0 |

The 15% tier requires 30 matured records, positive historical net return, profitable current position and confirmed signal. The 20% tier requires 50, two positive completed folds, and historical MDD <=20% in addition. The 30% exceptional tier requires 100/three folds/MDD <=15%/**independent_confirmation**, but Stage2 manager clips initial requests at 20%, so it is outside this audit. See [exact policy predicates](/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/progressive_scaling.py:24).

**30/50 are not independent trade counts in this implementation.** The evidence callback pools `len(realized)` across every funded stock and owner, partitions exit dates into fixed 63-session blocks, counts only positive blocks preceding the current partial block, and uses a mean return across realized records. It uses portfolio NAV history for MDD, hard-codes `current_signal_confirmed=True`, checks current close against entry plus fee, and hard-codes `independent_confirmation=False`. It does not use the stricter `EvidenceBook`, per-owner provenance or nonoverlapping validation records. See [actual evidence generator](/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/stage2_fix/support.py:44) and [alternative provenance-aware book](/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/causal_scaling_evidence.py:36).

`FillBook.realized` appends a record for every SELL, including partial exits; it does not guarantee one independent completed trade per record. See [realized-record creation](/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/position_fill_book.py:40). Across the 72 saved audit replays there are 52 exits below 0.01 share (variants included); record counts can include numerical/small partial exits. This is a separate evidence-quality issue, not the cause of valid-policy ADDs receiving zero risk budget. Do not cure it by inventing independent observations or lowering thresholds. A production evidence repair should deduplicate completed trade episodes, preserve owner/provenance and validate independence separately.

## Eight isolated high-EV, high-return blocked positions

All below pass the **current 15% evidence policy**, have target standalone modeled loss below 2%, enough settled cash for the incremental trade including costs, queue rank 1, and zero prior reserved loss. Every other-risk floor exceeds 2%; manager `risk_cap=0`, `approved=current`, `funded=0`, no ADD sent to the kernel, hence no corresponding next-open ADD risk admission/fill. They are isolated category-C failures. Some holdings drift above 10% through price appreciation; that is not executed scaling.

EV is the causal decision-time predicted one-session net return. Future return is measured from next open to the execution of the next native EXIT, only after all replays; it is diagnostic selection, not input to any policy. NAV/cash and evidence fields for every case are in report.json. Even a large later return does not establish that scaling would have been forecastably beneficial in real markets.

| Seed / stock / decision | Net EV % | Current % | Candidate 15% modeled loss % | Other holdings loss % | Settled cash / NAV % | Later exit return % |
|---|---:|---:|---:|---:|---:|---:|
| 1111 / SYN02 / 2030-06-26 | 1.9330 | 10.0201 | 1.845 | 8.791 | 9.363 | 15.010 |
| 1101 / SYN18 / 2030-05-28 | 1.5502 | 9.4548 | 1.845 | 5.716 | 51.013 | 4.327 |
| 1110 / SYN01 / 2030-07-03 | 1.4847 | 10.3149 | 0.945 | 2.555 | 54.811 | 52.137 |
| 1101 / SYN13 / 2030-08-08 | 1.4682 | 9.6857 | 0.945 | 5.144 | 40.532 | 4.706 |
| 1106 / SYN04 / 2030-09-20 | 1.4308 | 10.8837 | 0.495 | 7.089 | 36.355 | 4.917 |
| 1104 / SYN00 / 2030-10-24 | 1.3772 | 10.2624 | 0.495 | 8.927 | 24.135 | 9.753 |
| 1104 / SYN12 / 2030-07-30 | 1.3206 | 10.0051 | 0.495 | 9.628 | 9.951 | 39.971 |
| 1103 / SYN14 / 2030-04-11 | 1.3108 | 9.8896 | 1.845 | 7.722 | 10.072 | 3.411 |

Case-by-case decision traces (all numeric values are fractions unless stated):

- **1111 SYN02 2030-06-26**: native ADD 0.15; evidence n=109, folds=1, EV/signal/profitable=True, MDD=0.006642, independent=False (not required for 15%). NAV=$156248.11, cash=$14629.43; current=0.10020106, per-dollar loss=0.123; allowed_target/cap_target=0.15. Other risk=0.08791089, reserved_loss=0 -> risk_cap=0.0, approved=0.10020106, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-07-26.
- **1101 SYN18 2030-05-28**: native ADD 0.15; evidence n=72, folds=1, EV/signal/profitable=True, MDD=0.005475, independent=False (not required for 15%). NAV=$142586.72, cash=$72738.44; current=0.09454844, per-dollar loss=0.123; allowed_target/cap_target=0.15. Other risk=0.05715586, reserved_loss=0 -> risk_cap=0.0, approved=0.09454844, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-06-18.
- **1110 SYN01 2030-07-03**: native ADD 0.15; evidence n=109, folds=2, EV/signal/profitable=True, MDD=0.003011, independent=False (not required for 15%). NAV=$167790.45, cash=$91966.95; current=0.10314886, per-dollar loss=0.063; allowed_target/cap_target=0.15. Other risk=0.02554594, reserved_loss=0 -> risk_cap=0.0, approved=0.10314886, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-08-21.
- **1101 SYN13 2030-08-08**: native ADD 0.15; evidence n=116, folds=2, EV/signal/profitable=True, MDD=0.014187, independent=False (not required for 15%). NAV=$170229.22, cash=$68997.99; current=0.09685691, per-dollar loss=0.063; allowed_target/cap_target=0.15. Other risk=0.05144089, reserved_loss=0 -> risk_cap=0.0, approved=0.09685691, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-09-09.
- **1106 SYN04 2030-09-20**: native ADD 0.15; evidence n=148, folds=2, EV/signal/profitable=True, MDD=0.010166, independent=False (not required for 15%). NAV=$193414.18, cash=$70315.73; current=0.10883722, per-dollar loss=0.033; allowed_target/cap_target=0.15. Other risk=0.07089191, reserved_loss=0 -> risk_cap=0.0, approved=0.10883722, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-10-14.
- **1104 SYN00 2030-10-24**: native ADD 0.15; evidence n=153, folds=3, EV/signal/profitable=True, MDD=0.006335, independent=False (not required for 15%). NAV=$242224.09, cash=$58460.41; current=0.10262416, per-dollar loss=0.033; allowed_target/cap_target=0.15. Other risk=0.08926903, reserved_loss=0 -> risk_cap=0.0, approved=0.10262416, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-11-14.
- **1104 SYN12 2030-07-30**: native ADD 0.15; evidence n=102, folds=2, EV/signal/profitable=True, MDD=0.004532, independent=False (not required for 15%). NAV=$185118.71, cash=$18420.62; current=0.10005133, per-dollar loss=0.033; allowed_target/cap_target=0.15. Other risk=0.09628133, reserved_loss=0 -> risk_cap=0.0, approved=0.10005133, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-09-10.
- **1103 SYN14 2030-04-11**: native ADD 0.15; evidence n=57, folds=1, EV/signal/profitable=True, MDD=0.005345, independent=False (not required for 15%). NAV=$130926.10, cash=$13187.16; current=0.09889626, per-dollar loss=0.123; allowed_target/cap_target=0.15. Other risk=0.07722488, reserved_loss=0 -> risk_cap=0.0, approved=0.09889626, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes 2030-05-03.

## Minimal correction and bounded results

`source.patch` removes the manager's aggregate subtraction and passes zero other-position risk to the kernel scaling gate. The mandatory cost-inclusive per-position gate remains active at both reservation and execution. The generic `allowed_target` function retains its optional `other_equity_risk` argument for other callers; this patch fixes the Stage2 replay path, not all repository callers. Dead aggregate bookkeeping remains diagnostic to keep the patch small; it no longer constrains admission.

Patch bases are **Stage2_fix's local manager** plus the unchanged actual kernel. `audit.py:prepare` copies those exact baselines into a temporary tree, applies `patch -p1`, and asserts byte equality with `corrected_manager.py` / `corrected_kernel.py`. Thus this is an incremental experiment patch, not a patch to apply directly to the production manager. Exact reconstruction output: `reconstruction.log`. Instrumented managers differ only by additional snapshot/audit fields; equality checks prove original decisions unchanged. Corrected functional edits are fully represented by source.patch.

Only calibrated strong tapes were rerun under the correction: same 12 seeds × 10/15/20% = **36 corrected comparisons**. Weak/misnull receive audit only; no speculative tuning. Corrected 10% baselines match recorded Stage2_fix baselines exactly. No independent-evidence claim is made: this rerun diagnoses the risk-semantics change under unchanged, imperfect evidence.

| Target | Mean synthetic CAGR % | Mean MDD % | Mean exposure % | Mean turnover × | >10% incumbent BUY fills | Full requested fills |
|---|---:|---:|---:|---:|---:|---:|
| ev | 145.4874 | 1.0063 | 78.9948 | 33.4333 | 0 | 0 |
| scale15 | 179.7559 | 1.0079 | 83.8546 | 33.1584 | 1019 | 776 |
| scale20 | 184.5204 | 1.0227 | 84.4228 | 32.8226 | 988 | 204 |

Original Stage2_fix strong scaling produced one >10% ADD per variant and zero full targets across twelve seeds. Corrected runs now reach both 15% and 20%, demonstrating the aggregate restriction was material. The synthetic CAGR changes are descriptive diagnostics, not historical-alpha or investment-performance validation. Evidence, candidate gap risk and cash can still block individual adds: at gap=12%, the cost-inclusive standalone cap is 2%/12.3%=16.2602%; at gap=24%, it is 8.23045%, so these cannot support full 20% and above-10% scaling respectively. This is intended per-trade risk clipping, not a defect.

Seven bounded regression tests pass: unrelated holdings cannot consume candidate budget; entire candidate loss includes costs; crowded 15/20% requests fail before and fill after correction; exact 29/30 and 49/50 evidence boundaries plus profitability/fold failure; denied evidence releases cash to entrants; T+1 proceeds remain unavailable; MDD latch blocks entries and preserves exits. Each replay uses independent ledger/NAV/cash checks where applicable. `tests.log` records the first six passing tests plus the additional reservation test. Two initial test fixture errors (starting above the candidate risk ceiling, and missing high_water on a zero-cash holdings fixture) were corrected without altering the functional patch; their logs remain. An initial module-class adaptation error and an analysis key mismatch are also retained transparently.

Run accounting: 72 original audit comparisons + 36 corrected comparisons = 108 comparison portfolios; 20 short regression attempts (including initial fixtures) + one partially initialized audit attempt = 129 total portfolio attempts. **Corrected comparisons plus every corrected regression attempt total 50**, below the 108 corrected-run cap. No hidden broad reruns or GA. `audit.py` has a 600-second internal replay bound; replay comparisons completed in about a minute. All later processing reads saved outputs.

Reproduce from this directory (starts new bounded executions):

```bash
python3 audit.py > execution.log 2>&1
python3 summarize.py > analysis.log 2>&1
python3 -m unittest test_regression -v > tests.log 2>&1
python3 write_report.py
```

`report.json` is machine-readable; `corrected_runs.csv` contains all 36 corrected metrics; compressed replay/stock-date files retain raw decisions, risk, holdings, NAV, settled/unsettled cash, prices through the original fixed generator, evidence, queue predecessors and diagnostic returns. `manifest.json` hashes final artifacts. No production source was changed.
