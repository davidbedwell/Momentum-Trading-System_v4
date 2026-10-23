# GA6 Counterfactual Learning — Claude Adversarial Review Package (2026-10-23)

## Reviewer instructions
Act as an adversarial quantitative researcher and trading-systems engineer. Target ~14,000–16,000 output tokens, maximum 20,000 if supported. Inspect the source files linked below, not merely this description. Distinguish verified defects from plausible concerns; give file/function-level evidence, severity, scientific validity impact, expected profitability impact, minimal fix, test, and engineering effort. Prioritize fatal leakage or invalid comparisons over optional features. Explicitly disclose files you could not inspect. If output is truncated, continue rather than claiming completion.

## Objective
Learn decisions that improve *shared-capital* net portfolio profitability under risk constraints, not merely rank chromosomes. Evaluate (a) entry/decline/wait, (b) scale in, (c) scale out, (d) exit/hold, (e) opportunity cost of capital. Fixed genome owns an actual position from entry through exit; alternatives are shadow evaluated. Only outcomes fully matured strictly before the decision date may affect selection. Portfolio goals: >=35% CAGR aspirational, <=20% MDD hard ceiling, Calmar >2 desired; 40-session maximum hold; 1–2% trade risk, mandatory exit by -2%; 3–10% normal allocations, up to 30% for winners, ~10 diversified positions, SGOV cash, 10 bps transaction fee, next-open fills, settled cash, PIT membership, earnings +/-2 sessions, A/B/B1/C crash defense and R-1 recovery.

## Source repository and branch
https://github.com/davidbedwell/Momentum-Trading-System_v4/tree/ga6v3-counterfactual-learning
Source files under ga6/learning:
- COUNTERFACTUAL_EXECUTION_CONTRACT.md
- counterfactual_events.py; reference_fill_capture.py; reference_decision_capture.py
- position_lifecycle.py; reconciled_shadow.py; shadow_learning_bridge.py
- counterfactual_comparison.py; reference_bank_runner.py; divergence_audit.py
- chronological_shadow_learning.py; chronological_choice.py
- shared_position_ownership.py; trial_rating.py
- associated test_*.py files
Frozen reference evaluator is server-only at /opt/mts/ga6/structural_independent_v2_20261022/structural_portfolio_evaluator.py, NOT in this GitHub branch. The reviewer MUST NOT assume it has inspected this evaluator without obtaining the source. Also server-only: /opt/mts/ga6/claude_selective_20261023/selection_engine/{learning_ledger.py,chronological_selector.py,risk_allocator.py,causal_score.py}. A complete review requires these sources to be provided separately or committed after audit.

## What was actually implemented
Frozen reference fills and signals captured independently with metric parity checks; position lifecycle reconstructed; time-matured outcomes filtered; chronological shadow scores and proposed choices built; owner lock and tests; descriptive divergence categories; matched-trade research-only ratings. These are NOT a functioning adaptive shared-capital portfolio engine. Current 'shadow' portfolios each have independent $100k capital, hence rankings are not causal portfolio-profit improvements. The latest rating audit's realized PnL/gross purchases is numerically equal to net trade return for this data, so does NOT independently evaluate scaling.

## Actual first trial
Jan–Jun 2025 decisions, matured through Aug 2025, exploratory79 enriched stock data; three NICHE-0001 genomes differing only in weights:
- base
- smaller_weight: base_weight .03 max_weight .10
- larger_weight: base_weight .10 max_weight .25
Independent six-month reference portfolios starting $100,000:
base final NAV $105,076.77, +5.08% 6m, CAGR diagnostic 10.63%, MDD -21.34%, Calmar .50, 398 fills;
smaller_weight $106,241.53, +6.24%, CAGR 13.15%, MDD -16.56%, Calmar .79, 838 fills;
larger_weight $106,095.56, +6.10%, CAGR 12.83%, MDD -20.18%, Calmar .64, 215 fills.
These are independently funded portfolios, NOT an adaptive strategy.
Matched matured opportunity audit: 42 groups, base 36 matched trades, average net return -0.5475%, 21 best/tied, regret 0.259 percentage points; smaller 41, -0.5237%, 27 best/tied, regret 0.394 pp; larger 23, -0.5713%, 17 best/tied, regret 0.377 pp. Differing denominators and ties preclude direct win-count ranking. 8,310 stock/date signal-or-execution opportunities with largely incomplete mature executed coverage. Do not equate a non-execution with deliberate abstention.
The first rating implementation is committed as ga6/learning/trial_rating.py (commit 36a236bca78aea14ac5708f82de28a90ed0c6785).

## Proposed architecture corrections — NOT YET IMPLEMENTED
1. Decision ledger: record genuine time-t feasible action set, portfolio state, candidate signals, market regime, niche, sector, earnings/defense vetoes, cash/settlement, provenance, action taken and reasons.
2. Decision-centered counterfactuals for enter/wait/decline, scale-in/no-scale/scale-out, hold/exit. Distinguish genuine declined signals from constraints or absent fill. Shadow paths should use next-open, realistic costs and cash constraints, without claiming independently funded outcomes are jointly executable.
3. Measure incremental scaling value against same-entry no-scale control: incremental realized/net PnL, additional dollar-days, MAE/MFE and tail exposure; avoid using total trade return as scaling score.
4. Entry and exit value relative to feasible alternatives, evaluated after maturity and never included before decision time. Explicitly account for censoring and opportunity selection.
5. Aggregate conservative, uncertainty-adjusted decision quality into chromosome-level scores with niche/regime conditioning and minimum evidence; suspend consistently irrelevant chromosomes without deletion; keep shadow exploration controlled.
6. Integrate one shared settled-cash ledger with immutable position owner, risk/defense/earnings/PIT/corporate action parity, and correlation/sector limits. Verify one-genome exact fill/NAV parity with frozen evaluator before adaptive test.
7. Training and validation separation: same-period Jan–Jun 2025 is engineering parity/control only; Jul–Dec 2025 is NOT pristine because Jul–Aug outcomes were previously inspected. Reserve truly untouched blind period/BLIND17 for final certification.

## Specific questions requiring adversarial answers
1. Which current claims or metrics are scientifically invalid? Provide code-level proof.
2. How to identify the feasible action set at time t, including zero-trade choices and capital conflicts?
3. What minimal incremental scaling counterfactual properly measures profitability and risk, without hindsight leakage?
4. How should exits be compared without artificially rewarding longer holds or hidden capital costs?
5. What are appropriate statistical units, clustered uncertainty, selection bias corrections, and stopping criteria?
6. How to score entry, scaling, and exit without double counting PnL or letting hindsight dictate future actions?
7. How to prove one-genome evaluator parity and portfolio-level benefit vs fixed-genome baseline?
8. Which engineering changes are MUST-FIX before a valid second run, which are optional, and which should be rejected as needless complexity?
9. What is the minimal viable experimental protocol and go/no-go criteria, including fees, NAV, MDD, Calmar, turnover, drawdown tails and exposure?
10. Critique the 20k-token request itself if the available source material is insufficient.

## Important transparency
The requested corrected architecture and controlled rerun have NOT been completed. Do not imply a before/after result exists. This package is a preliminary engineering/adversarial review request, not a completed post-correction report. Do not recommend promoting a chromosome based on these observations.
