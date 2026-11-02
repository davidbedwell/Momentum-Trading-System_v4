"""Render report from saved counts; no replays."""
import json,hashlib,datetime
from pathlib import Path
OUT=Path(__file__).resolve().parent
r=json.loads((OUT/'report.json').read_text())
r['tests']=dict(passing_tests=7,passing_test_invocations=2,initial_fixture_errors=2,final_regression_portfolio_replays=11,initial_regression_portfolio_attempts=9,total_regression_portfolio_attempts=20,corrected_regression_portfolio_attempts=14,partial_instrumentation_setup_portfolio_attempts=1,logs=['tests.log','initial_test_fixture_failures.log','initial_instrumentation_failure.log','initial_analysis_key_failure.log'])
r['run_accounting']=dict(original_comparison_replays=72,corrected_comparison_replays=36,corrected_including_all_regression_attempts=50,regression_attempts=20,partial_setup_attempts=1,total_portfolio_attempts=129,extra_analysis_replays=0)
r['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
r['citations']={
 'manager_other_risk':'../stage2_fix/functional_niche_manager.py:377-381',
 'manager_aggregate_gate':'../stage2_fix/functional_niche_manager.py:451-480',
 'kernel_aggregate_gate':'/opt/Momentum-Trading-System_v5-alpha/engines/portfolio_replay/kernel.py:103-124',
 'kernel_per_trade_gate':'/opt/Momentum-Trading-System_v5-alpha/engines/portfolio_replay/kernel.py:128-150',
 'scale_evidence_thresholds':'/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/progressive_scaling.py:24-35',
 'synthetic_adds':'../stage2_fix/support.py:28-38',
 'evidence_generator':'../stage2_fix/support.py:44-56',
 'partial_exit_counts':'/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/position_fill_book.py:40-47',
 'alternate_evidence_book':'/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/causal_scaling_evidence.py:36-56'}
r['category_definitions']={
 'A':'No native ADD on a positive-EV incumbent stock-date. Zero in scaling variants; denominator must include opportunities, because an ADD-only denominator cannot contain missing ADDs.',
 'B':'Full requested evidence tier not passed; exact failed fields stored. A 20% failure may still permit 15%. Independent_confirmation=False is NOT a failure under current 15/20 policy.',
 'C':'Full target violates either standalone candidate risk, other holdings plus candidate risk, or prior queued modeled losses. Subcategories mutually partition these tests in that order.',
 'D':'Requested concentration exceeds evidence-approved tier (10/15/20). Overlaps B; not an independent reason to remove evidence gates.',
 'E':'Initial settled cash cannot cover standalone-safe requested increment with execution costs. Split into settlement-only shortfall and insufficient cash even including receivables.',
 'F':'Prior ranked commitments reduce cash and leave less than standalone-safe requested increment. Overlaps E when both initial cash shortage and queue consumption apply; queue-risk subtype reported under C.'}
r['source_unchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in r['original_sources_sha256'].items())
assert r['source_unchanged']
(OUT/'report.json').write_text(json.dumps(r,indent=2))
base='/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101/'
def src(label,path,line):return f'[{label}]({path}:{line})'
mgr=base+'stage2_fix/functional_niche_manager.py';support=base+'stage2_fix/support.py';kernel='/opt/Momentum-Trading-System_v5-alpha/engines/portfolio_replay/kernel.py';policy='/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/progressive_scaling.py'
text=f'''# Scaling blocker audit — completed, local synthetic diagnostics

**Root cause: the 2% per-trade loss allowance is incorrectly reused as a shared portfolio risk budget for scaled ADDs.** Ordinary entries use a per-position rule. The manager and kernel impose an additional aggregate restriction only on evidence-based scaling. This contradicts the specified per-trade rule; raising concentration limits alone cannot fix it.

All production sources and Stage2 inputs are unchanged (SHA-256 in report.json). No GA, fitting, search, evidence relaxation, or production patch application. Completed within the 15-minute work limit. Twelve seeds are 1101–1112; 252 sessions, 24 synthetic assets, same fixed tapes. These are invented SYN tickers and synthetic callbacks, not historical stock evidence or native learned alpha.

The 72 unchanged-policy instrumented replays reproduce all recorded Stage2_fix 15/20% metrics to 1e-10 across all three qualities. First-seed decisions also match saved audit JSON exactly after stripping added diagnostic fields. The prior artifacts did **not** retain full decision/risk data for all 12 seeds; this audit regenerates them and verifies the recorded summaries, rather than claiming missing logs existed. Saved full replays: `original_decision_risk.jsonl.gz`. Per-opportunity decomposition and queue predecessors: `unique_opportunities.jsonl.gz`.

## Actual execution path and intended rule

1. The Stage1 base callback emits ENTER/HOLD/EXIT, never ADD. The Stage2 scaling wrapper converts a held HOLD with positive net EV and weight below target into an ADD. Thus “native ADD” in this experiment means a synthetic wrapper request, not independently validated native-model scaling. See {src('synthetic ADD generation',support,28)} and {src('underlying callback',base+'run.py',188)}.
2. The manager computes current weight from marked holdings/NAV, obtains causal evidence, and sums **all other funded positions** at `weight * (max(stop, gap) + round_trip_cost)`. See {src('evidence and other-position risk',mgr,353)}. Even positions scheduled to exit still enter this close-time sum.
3. Evidence approval occurs before settled cash reservation. `allowed_target` is called without other risk here, so its default is zero. The manager then independently sets `remaining_risk=max(0, .02-other_equity_risk-reserved_loss)` and clips the candidate's **total target**, before funding the increment. See {src('reservation and wrong aggregate gate',mgr,447)}.
4. At the next open, the kernel sorts pending signals again and calls `allowed_target` with `max(signal.other_equity_risk,reserved_risk)`. This retains the stale close-time floor and adds a second aggregate constraint. Kernel reservation occurs before actual cash fills and does not include the cost allowance at that stage. See {src('execution aggregate floor',kernel,103)}.
5. A separate mandatory gate already constrains each candidate: `target_weight * (max(stop,gap) + round_trip_cost) <= .02`. It applies to ordinary and scaled increases, uses opening NAV, and retains existing exposure if drift already exceeds the limit. The minimal correction keeps this gate, evidence, cash, fees, settlement, MDD latch and native exits. See {src('mandatory per-position gate',kernel,128)}.

The conservative interpretation used here treats the entire scaled position as the candidate trade. It does not grant a fresh 2% allowance to every incremental ADD. An **optional portfolio aggregate guard** must have its own explicit configuration/limit and coherent holdings/queued-order accounting; it must not silently reuse the mandatory 2% per-trade value.

There is no blanket literal double-count. In the manager, other-position risk covers existing holdings and `reserved_loss` generally covers distinct funded increments, including ordinary entrants. The kernel uses `max`, not `other + reserved`. The semantic defect is applying a common budget; the two stages both enforce it without multiplying it by two. Stale risk floors and pre-fill reservations can be additionally conservative. Candidate current weight is already part of its total target; it is not subtracted again as another holding. The eight showcased failures have `reserved_loss=0`, proving queue-risk double-count is unnecessary to produce the defect.

At 80% invested entirely in the lowest modeled risk assets, modeled aggregate loss is already 80% × 3.3% = 2.64%. Seven other 10% holdings alone consume 2.31%, so even an individually safe candidate can receive zero incremental budget.

## Distinct blockers and overlaps

Each row is counted once per `(seed, quality, variant, ticker, decision date)`, not once per rejection flag or kernel attempt. These are simultaneous **full-target counterfactual constraints**, not mutually exclusive causes. Category C is partitioned below; actual stage-reached denial counts are also in report.json.

A = positive-EV incumbent lacked ADD; B = failed evidence tier; C = modeled risk; D = evidence-approved concentration cap; E = initial settled cash shortage; F = earlier queue commitments consume cash. A is zero for all positive-EV incumbent dates in these scaling tapes because the wrapper explicitly converts them all. An ADD-only denominator cannot logically contain A. Across all incumbent dates, many HOLD/EXIT decisions do not request ADD: these are recorded in `native_incumbent_action_counts`, and predominantly have nonpositive EV. The 10% baseline callback requests no ADD by construction.

| Quality / target | Unique ADDs | A | B | C | D | E | F |
|---|---:|---:|---:|---:|---:|---:|---:|
'''
for key,g in r['groups'].items():
 c=g['categories'];text+='| '+key+' | '+str(g['unique_native_add_stock_dates'])+' | '+' | '.join(str(c.get(k,0)) for k in 'ABCDEF')+' |\n'
text+='''
B and D overlap exactly at the full-target level here: failed prerequisites lower the concentration tier. They are separate questions about evidence and sizing, not additive blocker populations. The 20% tier may fail while 15% remains admissible. No separate arbitrary 10% hard cap blocks an evidence-approved scale.

| Quality / target | Candidate alone >2% | Other holdings block standalone-safe target | Queue risk only | Evidence passes full tier | Evidence passes + other block + initial cash sufficient |
|---|---:|---:|---:|---:|---:|
'''
for key,g in r['groups'].items():text+=f"| {key} | {g['standalone_exceeds']} | {g['other_exhausts']} | {g['queue_risk_exhausts']} | {g['evidence_valid_adds']} | {g['evidence_valid_other_blocked_cash_sufficient']} |\n"
g=r['groups']['strong_scale15']
text+=f'''
For strong/15%, other holdings **alone** already exceed 2% on {g['other_risk_alone_at_least_2pct']:,} of {g['unique_native_add_stock_dates']:,} requests. The aggregate gate denies **any** otherwise standalone-safe increment after evidence allows an increment on {g['aggregate_denies_any_standalone_safe_increment']:,} dates. This differs from full-target constraints, where partial funding could still be possible.

For strong/15%, cash category E splits into {g['settlement_alone_covers_cash_shortfall']:,} dates where receivables would cover the shortfall if spendable, and {g['insufficient_cash_even_including_receivables']:,} dates where even cash plus receivables is insufficient. Sales are never credited to the current close budget. Receivables are NAV assets but cannot fund purchases until T+1. Kernel sells before buys, but sale proceeds are added to unsettled cash after purchases. See {src('settlement and NAV',kernel,90)} and {src('sale, cash and funding order',kernel,159)}. Close queue order is descending marginal net EV, then ticker/family/chromosome; execution uses score/ticker/chromosome (all families here are GA7). F measures the cash committed to higher-ranked requests, not a claim that reordering improves returns.

Full exact overlap histograms are saved per group in `report.json`. Strong/15% overlap:

| Simultaneous categories | Unique ADDs |
|---|---:|
'''
for key,n in g['exact_overlap'].items():text+=f'| {key} | {n} |\n'
text+='''
Collapsing the 15/20 variants gives 36,055 unique `(seed, quality, ticker, date)` opportunities; category membership is the union across requested targets, not a claim that target-specific requirements are identical. The report saves these union counts separately; primary tables preserve requested target.

## Exact evidence failures and independence

| Quality / target | matured_trades | position_profitable | positive_net_ev | forward_folds | current_signal_confirmed | historical_mdd | evidence missing |
|---|---:|---:|---:|---:|---:|---:|---:|
'''
for key,g in r['groups'].items():
 c=g['evidence_failed_fields'];text+=f'| {key} | '+' | '.join(str(c.get(k,0)) for k in ('matured_trades','position_profitable','positive_net_ev','forward_folds','current_signal_confirmed','historical_mdd','scaling_evidence_missing'))+' |\n'
text+=f'''
The 15% tier requires 30 matured records, positive historical net return, profitable current position and confirmed signal. The 20% tier requires 50, two positive completed folds, and historical MDD <=20% in addition. The 30% exceptional tier requires 100/three folds/MDD <=15%/**independent_confirmation**, but Stage2 manager clips initial requests at 20%, so it is outside this audit. See {src('exact policy predicates',policy,24)}.

**30/50 are not independent trade counts in this implementation.** The evidence callback pools `len(realized)` across every funded stock and owner, partitions exit dates into fixed 63-session blocks, counts only positive blocks preceding the current partial block, and uses a mean return across realized records. It uses portfolio NAV history for MDD, hard-codes `current_signal_confirmed=True`, checks current close against entry plus fee, and hard-codes `independent_confirmation=False`. It does not use the stricter `EvidenceBook`, per-owner provenance or nonoverlapping validation records. See {src('actual evidence generator',support,44)} and {src('alternative provenance-aware book','/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/causal_scaling_evidence.py',36)}.

`FillBook.realized` appends a record for every SELL, including partial exits; it does not guarantee one independent completed trade per record. See {src('realized-record creation','/opt/Momentum-Trading-System_v5-alpha/discovery/competitive_ga/position_fill_book.py',40)}. Across the 72 saved audit replays there are 52 exits below 0.01 share (variants included); record counts can include numerical/small partial exits. This is a separate evidence-quality issue, not the cause of valid-policy ADDs receiving zero risk budget. Do not cure it by inventing independent observations or lowering thresholds. A production evidence repair should deduplicate completed trade episodes, preserve owner/provenance and validate independence separately.

## Eight isolated high-EV, high-return blocked positions

All below pass the **current 15% evidence policy**, have target standalone modeled loss below 2%, enough settled cash for the incremental trade including costs, queue rank 1, and zero prior reserved loss. Every other-risk floor exceeds 2%; manager `risk_cap=0`, `approved=current`, `funded=0`, no ADD sent to the kernel, hence no corresponding next-open ADD risk admission/fill. They are isolated category-C failures. Some holdings drift above 10% through price appreciation; that is not executed scaling.

EV is the causal decision-time predicted one-session net return. Future return is measured from next open to the execution of the next native EXIT, only after all replays; it is diagnostic selection, not input to any policy. NAV/cash and evidence fields for every case are in report.json. Even a large later return does not establish that scaling would have been forecastably beneficial in real markets.

| Seed / stock / decision | Net EV % | Current % | Candidate 15% modeled loss % | Other holdings loss % | Settled cash / NAV % | Later exit return % |
|---|---:|---:|---:|---:|---:|---:|
'''
for z in r['cases']:text+=f"| {z['seed']} / {z['ticker']} / {z['date']} | {z['net_ev']*100:.4f} | {z['current']*100:.4f} | {z['standalone_target_loss']*100:.3f} | {z['other_equity_risk']*100:.3f} | {z['cash']/z['nav']*100:.3f} | {z['diagnostic_forward_return_to_next_native_exit']*100:.3f} |\n"
text+='\nCase-by-case decision traces (all numeric values are fractions unless stated):\n\n'
for z in r['cases']:
 e=z['evidence'];dd=z['reservation_detail'];res=z['reservation'];text+=f"- **{z['seed']} {z['ticker']} {z['date']}**: native ADD 0.15; evidence n={e['matured_trades']}, folds={e['forward_folds']}, EV/signal/profitable=True, MDD={e['historical_mdd']:.6f}, independent=False (not required for 15%). NAV=${z['nav']:.2f}, cash=${z['cash']:.2f}; current={z['current']:.8f}, per-dollar loss={z['per_dollar_loss']:.3f}; allowed_target/cap_target={res['cap_target']:.2f}. Other risk={z['other_equity_risk']:.8f}, reserved_loss=0 -> risk_cap={dd['risk_cap']:.1f}, approved={res['approved']:.8f}, funded=0. Rank 1; no preceding cash commitments; no next-open ADD risk record/fill. Diagnostic exit executes {z['diagnostic_next_exit']}.\n"
text+=f'''
## Minimal correction and bounded results

`source.patch` removes the manager's aggregate subtraction and passes zero other-position risk to the kernel scaling gate. The mandatory cost-inclusive per-position gate remains active at both reservation and execution. The generic `allowed_target` function retains its optional `other_equity_risk` argument for other callers; this patch fixes the Stage2 replay path, not all repository callers. Dead aggregate bookkeeping remains diagnostic to keep the patch small; it no longer constrains admission.

Patch bases are **Stage2_fix's local manager** plus the unchanged actual kernel. `audit.py:prepare` copies those exact baselines into a temporary tree, applies `patch -p1`, and asserts byte equality with `corrected_manager.py` / `corrected_kernel.py`. Thus this is an incremental experiment patch, not a patch to apply directly to the production manager. Exact reconstruction output: `reconstruction.log`. Instrumented managers differ only by additional snapshot/audit fields; equality checks prove original decisions unchanged. Corrected functional edits are fully represented by source.patch.

Only calibrated strong tapes were rerun under the correction: same 12 seeds × 10/15/20% = **36 corrected comparisons**. Weak/misnull receive audit only; no speculative tuning. Corrected 10% baselines match recorded Stage2_fix baselines exactly. No independent-evidence claim is made: this rerun diagnoses the risk-semantics change under unchanged, imperfect evidence.

| Target | Mean synthetic CAGR % | Mean MDD % | Mean exposure % | Mean turnover × | >10% incumbent BUY fills | Full requested fills |
|---|---:|---:|---:|---:|---:|---:|
'''
for z in r['corrected_strong_aggregates']:text+=f"| {z['variant']} | {z['cagr']*100:.4f} | {z['mdd']*100:.4f} | {z['exposure']*100:.4f} | {z['turnover']:.4f} | {z['scaled_fills']} | {z['full_target_fills']} |\n"
text+='''
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
'''
(OUT/'README.md').write_text(text)
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name not in ('manifest.json','run.log')}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('README/report/manifest complete; source hashes unchanged')
