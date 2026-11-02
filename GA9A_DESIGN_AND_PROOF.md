# GA9-A actionable stock opportunity engine — design and bounded proof

2026-10-29. **Functional synthetic demonstration; portfolio target failed.** Passing tests is not evidence of profitability. No live trading, deployment, GA8 edits, long evolution, or production certification was performed.

## Implementation and use

New modules:

- `ga9/opportunity.py`: daily PIT eligibility and rolling discovery, strategy genome, stock-policy outcome simulation, chronological empirical calibration, opportunity records, GA9-B adapter.
- `ga9/opportunity_proof.py`: two-generation search and chronological synthetic account replay.
- `ga9/test_opportunity.py`: causal boundary, missing support, execution and gap regressions.

Run from repository root with an unused output directory:

```bash
/opt/mts/.venv/bin/python -m ga9.opportunity_proof --output ga9/artifacts/ga9a_reproduction
/opt/mts/.venv/bin/python -m pytest ga9 -q
```

Default inputs live outside this repository, read-only, under `/opt/mts/synthetic-market-lab/runs/causal_native_features`. `--root` overrides that directory. Source paths and SHA256 hashes are recorded in the proof report. Reproduction requires those existing files; they are not bundled here.

## Daily data and discovery

The existing scenario contains **500 stocks × 1,260 business sessions**, 2021-12-29 through 2026-10-27. `universe_1_eight_family.parquet` supplies raw open, close and volume; `universe_1_ga4_native.parquet` supplies dated synthetic eligibility and sector IDs. Other numbered files are parallel five-year scenarios, not subsequent years; they are not concatenated.

Features are rebuilt causally from raw prices. Every close refreshes the top **150** eligible names using the mean percentile of trailing 20/60/120-session returns. At most 150 enter the discovery pool, after the 120-session warmup; deterministic symbol-order ties apply. The score is a discovery filter, not the delivered stock forecast or a portfolio weight. New entries require decision-day eligibility and pool membership; fills also check execution-day eligibility. Incumbents remain forecastable outside the discovery pool and can exit on membership loss. Synthetic daily eligibility is treated as known at the close; this is not independently audited real-world membership history. No niche partition is required.

## Strategy and forecast contract

Each genome evolves signal family, raw entry threshold, horizon (5/20/60 sessions), add/reduce thresholds and trailing stop. Uniform crossover, mutation and elite survival operate on **stock strategies**, while GA9-B parameters remain fixed. Search is two generations × six candidates, nine distinct evaluations in the recorded run, single process. No further evolution was launched in response to the forward result.

Stock-policy labels simulate next-open entry, one add, one half reduction, loss/trailing/membership exits, and horizon expiry at the following open. Two thirds of committed sleeve capital enters initially; one third is reserved for an add. Returns include 5 bp slippage and 1 bp fees on each traded side. Downside is the worst marked sleeve return over intervening closes and execution opens. Overnight gap losses are retained. Horizon counts from decision close to final decision close, with liquidation at the following open.

An opportunity record includes:

- ticker, as-of close, next-open execution convention and strategy parameters;
- net expected return as a **fraction of committed stock sleeve capital**;
- horizon in sessions, empirical 10th percentile of path-minimum return (`downside_p10`);
- empirical probability of positive net stock-policy outcome;
- confidence/support, calibration dates, sample count, supported flag, and entry eligibility;
- actionable entry/hold/add/reduce/exit policy descriptions.

Fixed score bins avoid full-sample quantile fitting. Training bin means are updated using a separate later calibration interval, shrunk by calibration-date support. Downside quantiles and positive-outcome frequencies use matured training/calibration labels. Unsupported bins abstain. `confidence` is **date support**, capped at one after three horizon lengths of calibration dates; it is neither a statistically calibrated confidence interval nor a probability of profit. Correlated stocks and overlapping horizons preclude treating the row count as independent observations.

## Chronology and GA9-B boundary

Predeclared index intervals are half-open:

| Purpose | Sessions | Use |
|---|---:|---|
| Training | 0–504 | Initial conditional outcome estimates |
| Calibration | 504–756 | Later empirical calibration; endpoints strictly before 756 |
| Strategy selection | 756–1008 | Funded portfolio comparison only |
| External forward | 1008–1260 | Frozen winner; never used to choose a genome |

Training labels must mature before 504; calibration decision dates begin at 504 and mature before 756. The frozen model cutoff is 2024-11-21. No future membership, returns, ranks, fitted quantiles, or label endpoints enter a close-time decision. The winner is serialized before forward replay. Selection first favors observed MDD below 8%, then excess CAGR relative to the +20 percentage-point ambition, then lower drawdown. This is selection, not a guarantee.

`allocate()` bridges A to the existing `ga9.execution.replay` competitive allocator. Expected positive net return per session feeds its `signal` tensor; the sunk-entry-cost adjustment feeds `hold_signal`. GA9-B owns shared settled cash, sizing, competing candidates/incumbents, correlation, sector limits, reserve, fills and settlement. Parameters here: 10 slots, 10% reserve, 0.8 correlation threshold, 0.008 nominal loss-risk budget, 30% sector entry cap, 6% initial requested size and up to 9% after add. Cash earns zero. Sale proceeds use the allocator's conservative T+2 settlement. There is no GA8 import or mutation.

**Boundary limitations:** B currently consumes the expected-return projection, not the complete downside/confidence distribution. Its loss-risk budget uses a fixed 2% loss proxy rather than A's downside quantile. Holding forecasts reuse the original conditional distribution with a sunk-cost adjustment, rather than calibrating remaining horizon conditional on position age, gain and prior actions. Stock-label sleeves reserve their own add capital and do not model shared-account settlement, competition, or opportunity-cost exits. B may therefore reject or alter an A action. These differences are explicit blockers to claiming fully calibrated funded strategy returns. Native close-observed stops cannot guarantee an 8% portfolio ceiling across gaps. Weight and sector caps are order-time controls; price drift can exceed them between executions.

## Recorded evidence

Canonical artifacts: `ga9/artifacts/ga9a_final_proof/`:

- `report.json`: source hashes, split, every evaluated genome, validation/forward metrics, calibration and execution checks;
- `frozen_model.json`: selected momentum strategy, 60-session horizon, 0.8% add, −0.8% reduce, 5% trailing;
- `opportunities.jsonl`: daily pool and incumbent forecasts, including unsupported/negative cases;
- `decisions.jsonl`: proposed orders, explicit incumbent HOLD decisions, competition and discovery context;
- `fills.jsonl`: actual execution dates, decision dates, quantities, raw opens, execution prices and costs;
- `daily_ledger.jsonl`: all 252 forward sessions, settled/unsettled cash, holdings, NAV, drawdown and position detail.

| Final forward measure | Observed |
|---|---:|
| Strategy CAGR | **1.01%** |
| Broad synthetic market proxy CAGR | **48.23%** |
| Excess CAGR | **−47.23 percentage points** |
| Maximum drawdown | **22.41%** |
| Final NAV from $100,000 | $101,005.24 |
| Execution costs | $3,238.29 |
| Mean exposure | 37.56% |
| Actual fills | 1,172 |
| Entry / add / reduce / exit fills | 444 / 213 / 78 / 437 |
| Hold decisions | 730 |
| Residual positions | 7, marked without fictitious terminal liquidation |

The market proxy is fixed equal-weight buy-and-hold sleeves in all 500 synthetic stocks, cash on the first decision day, entry at the same first executable open with the same entry costs. It is not an ETF or real-market benchmark. Strategy and proxy both mark residual positions without terminal exit costs. The proxy does not represent tradable PIT reconstitution. Validation CAGR was 23.58% with 7.79% MDD; final forward MDD failed despite validation feasibility. No forward tuning was performed.

Out-of-sample calibration uses only fully matured forward stock-policy labels (not funded portfolio returns):

| Score bin | Outcomes | Predicted / realized mean | Predicted / observed P(positive) | Downside P10 coverage |
|---|---:|---:|---:|---:|
| 2 | 2,567 | 0.036% / 0.271% | 25.40% / 26.30% | 88.43% |
| 4 | 6,520 | 0.136% / 0.265% | 25.28% / 24.56% | 89.89% |
| 5 | 12,281 | 0.185% / 0.633% | 25.01% / 26.19% | 91.11% |

The nominal downside coverage is 90%. These are empirical diagnostics with overlap and cross-stock dependence, not statistical certification. Mean errors and the funded return mismatch remain material.

Artifact assertions verify next-session fills, exact raw-open matching, PIT discovery gating for entries, NAV identity and the pool cap. Maximum account reconciliation error was approximately $8.73e−11. All **73 GA9 tests passed**, including four new GA9-A regressions. The final bounded search/replay ran in approximately 20 seconds. Tests demonstrate mechanics and causality, not profitability. Existing GA8 working-tree edits predate this work and were left untouched.

## Blockers and next steps

1. **Portfolio target is unmet.** The required market CAGR +20 percentage points and MDD below 8% both failed. No deployment or profitability claim is warranted.
2. Extend B's contract to consume downside and support explicitly; replace the fixed stop-distance risk proxy with scenario/gap-aware sizing. Report breaches rather than presenting an absolute ceiling as enforceable.
3. Calibrate state-dependent hold/add/reduce/exit counterfactuals with portfolio-equivalent execution, settlement and opportunity-cost rules. Keep return denominators consistent between committed sleeve capital and funded initial size.
4. Evaluate untouched parallel synthetic scenarios without selecting on this forward slice. Add date-block uncertainty and benchmark calibration controls before interpreting confidence statistically.
5. Before real-data use, require historical eligibility publication timestamps, delisting/corporate-action outcomes, missing-open handling, point-in-time sector history and a declared investable market benchmark.

This delivery stops at the requested bounded functional proof. The implementation is actionable through the existing allocator; the economic objective and full distribution-aware allocation remain unproven.
