# GA6-v3 to live-capable chronological learning backtester: independent code review

## Goal (binding)
Build a historical training backtester for a machine that can later trade live with the SAME decision logic. Starting shared simulated capital $100,000. Each historical time t screens eligible securities, recognizes contemporaneous niches/regimes, chooses among 400 existing GA6-v3 chromosomes, decides entry and planned risk (at most 2% of portfolio per position, acknowledging gap risk), manages scale in/out and exit within 40 trading sessions, and learns from every decision only when outcomes mature. Prioritize individual decision/trade quality: opportunity selection, chromosome choice, entry timing, size, scaling, exit, opportunity cost, costs, risk calibration. CAGR and MDD are secondary portfolio safety checks. Monthly AI review of accumulated decision evidence, not automatic arbitrary strategy rewrites. No new GA evolution now.

## Existing implementation: READ CODE, DO NOT ASSUME FRAMEWORK ONLY
- `ga6/structural_independent_v2_20261022/structural_portfolio_evaluator.py`: original evaluator; structural chromosome decisions, next-open, position risk, settlement, 40-session cap.
- `ga6/structural_independent_v2_20261022/structural_decision.py`, `family_logic.py`: chromosome decision grammar.
- `ga6/position_equity_risk_20261021.py`: entry-equity risk accounting.
- `ga5_redesign/settlement_ledger.py`, `mts_next_open_ledger_v1.py`: canonical ledger/fill primitives.
- `ga6_h/selection_engine/niche_signal_adapter.py`, `research_niche_recognizer.py`: candidate signals and niches.
- `ga6_h/selection_engine/chronological_selector.py`, `risk_allocator.py`, `selector_core.py`: past-only learning and capital allocation.
- `ga6_h/selection_engine/learning_ledger.py`: decision/outcome maturity ledger.
- `ga6_h/selection_engine/shared_capital_execution.py`: separate execution orchestration reusing GA6 accounting primitives.
- `ga6_h/selection_engine/shadow_replay.py`, `policy_shadow_runner.py`, `real_label_portfolio_replay.py`: research shadow labels, integration replay.
- `ga6_h/selection_engine/defense_policy_v3.py`: prior-close A-v2/B/B1/C/R1 defensive permission, obsolete arbitrary veto excluded.
- `ga6_h/selection_engine/verification_pipeline.py`: fail-closed test/certification gates.
- `ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json`: 269 generations, 400 chromosomes; DO NOT MODIFY.

## Known verified deficiencies
1. Historical replay assigns all stocks `UNVERIFIED_SECTOR`; available Yahoo 2026 sectors explicitly NOT PIT. Do not relabel historical sectors without genuine provenance.
2. Shadow replay is simplified single-symbol accounting, not full evaluator parity; labels may bias learning.
3. No executed reference-vs-shared-capital parity harness. The current certification pipeline correctly blocks on missing harness and provenance.
4. Research niche centers fitted retrospectively, not guaranteed causal. Require freeze/fit on prior training data or strictly causal online update.
5. Current portfolio replay consumes ENTER proposals but does not fully preserve chromosome-specific exit/scale instructions.
6. Original GA6-v3 evolution ANDed old arbitrary risk veto with prior-close defense, constraining training. Do not silently rewrite historical checkpoint; selector should use correct prior-close defense.
7. Avoid full-universe replay for every development iteration; begin with small deterministic, chronological fixtures and expand after parity.

## Review questions: evidence and engineering, not brainstorming
A. Audit actual module interfaces and identify exact code-path divergences that would make training outcomes differ from future live decisions.
B. Specify minimum implementable chronological learning loop with real selected-trade and counterfactual labels; prevent lookahead, survivorship bias, self-selection bias, and outcome-maturity leakage.
C. Propose robust trade-level metrics, paired controls, and an explicit learning-vs-frozen baseline to prove improved decision quality rather than lucky return.
D. Clarify per-position 2% planned loss accounting across gaps, adds, sector/correlation clusters, and shared portfolio constraints.
E. Design minimal deterministic parity fixtures with expected fills, inventory, realized P&L, NAV, splits, dividends, T+1, earnings embargo, defensive exits, 40-session cap, scaling.
F. Identify what can reuse existing code, what MUST change, and what can be deferred. Prefer minimum edits, no duplicate engines, no neural network unless justified by measured advantage.
G. Give a ranked, bounded implementation plan with concrete acceptance tests, rough complexity and runtime. No multi-week research detour, no GA6-H evolution, no modification of untouched validation/blind partitions.
H. Explain what should go in the monthly AI audit and which proposed changes need frozen evaluation before promotion.

## Deliverable
Code-grounded findings with file/function references, severity, specific fixes and tests. Distinguish verified from inferred. Challenge our assumptions and identify any fatal flaws. Keep solution economical and executable. Do not claim scientific certification based on existing smoke tests.
