# Breadth GA decision pilot

**NO-GA warranted.** No evolutionary optimization was launched; zero genomes were evaluated. Available evidence does not establish an economically useful, repeatable breadth gate. This is a null eligibility result, not proof that every breadth function has zero edge.

The user objective, original archival report, replay report source, trade ledger, selection, fold splits, correlations, bootstrap and previous decision results were reviewed. The replay directory has no generated REPORT.md; its report.py contains the intended report text and was read without executing it or changing prior artifacts.

The strongest prior economic warning is GA6: the earlier training-selected median filter raises average trade return from 2.514% to 2.850%, yet retains only 104,670.83 of 135,843.93 in closed-trade net PnL, for an arithmetic opportunity cost of 31,173.09. GA7 retains 349.86 versus -1,150.40, but evidence is dominated by F2: F1 has no trades and F3 has four. These are sums of separate hypothetical chromosome accounts, **not investable combined portfolios**. Prior kept-versus-skipped return intervals include zero for both families; those intervals are not uncertainty intervals for portfolio uplift. GA6 MA50 Pearson correlation changes from -0.055 to -0.312 to +0.070 across F1/F2/F3. GA8 winners differ each year and have no corresponding multi-year chromosome training sample.

## Objective stop and independent support

PROTOCOL.md defines a conjunctive stop: require validated cash-constrained counterfactual accounting, at least 20 separated market events, at least two materially active chronological evaluation folds, repeatable net benefit on those folds, and uncertainty supporting incremental net benefit before any search. These are conservative research screening choices made after reviewing the existing evidence, not preregistration or calibrated significance tests. The economic and accounting failures independently stop this phase. No threshold search, MA search, slope interaction, nonlinear fit, population or random seed was run. No automated future launch path is included.

Event support merges overlapping holding intervals across chromosomes and requires a 63-business-day gap to start another cluster. event_support.csv reports this deliberately conservative support proxy, not a claim of statistical independence. Trade counts and entry dates are also shown. Changing genomes or duplicated holdings does not create independent market episodes. Sparse GA7 slots remain in fold_support.csv.

## Comparisons and opportunity cost

trade_comparisons.csv compares each original chromosome/fold and entry year with (1) unchanged baseline, (2) fixed MA50 breadth <=50% gate, and (3) the **previous study's** earlier-training-selected median rule, with its original frozen MA/direction/threshold. The third comparator is not evolved and is unavailable for GA8. The fixed rule is a descriptive comparator chosen in this phase, informed by prior weak-breadth findings; it is not a newly validated holdout result. Evolved-model results are **not run**, rather than invented or replaced by the earlier rule. No test-period threshold was optimized.

Each gate keeps or skips whole original episodes, including their original adds, partial reductions, costs and exits in original net PnL. Missing breadth fails closed. Positive skipped PnL is opportunity cost; negative skipped PnL is avoided loss. Net uplift equals avoided loss minus skipped winners. Acquisition retention and acquisition-cost times inclusive calendar holding-day retention are turnover/capital-duration proxies, **not daily marked portfolio exposure**; partial exits/adds prevent interpreting them as actual exposure. GA6/7 closed-trade PnL and entry/exit sessions reconcile to all ten selected original ledgers (ledger_checks.csv). GA8 uses the already reconstructed original-cost episode records; its fills are not independently rebuilt here.

Aggregate separate-account bookkeeping (currency units; no allocation or compounding implied):

```text
                                            base_pnl   retained_pnl    uplift_pnl  skipped_winner_pnl  avoided_loss_pnl
system model                                                                                                           
GA6    baseline                        135843.926091  135843.926091      0.000000            0.000000          0.000000
       fixed_b50_le_0.5                135843.926091   43705.857032 -92138.069059       247618.931572     155480.862513
       prior_training_selected_median  135843.926091  104670.832175 -31173.093916        84286.018400      53112.924484
GA7    baseline                         -1150.401963   -1150.401963      0.000000            0.000000          0.000000
       fixed_b50_le_0.5                 -1150.401963    4303.289362   5453.691325        10942.764164      16396.455490
       prior_training_selected_median   -1150.401963     349.855966   1500.257929         3828.618545       5328.876475
```

## Portfolio metrics and chronology

CAGR, MDD and Calmar are **unavailable for this counterfactual comparison** and blank in output. Original full-account NAV exists, but filtered completed trades do not supply a validated cash-constrained marked portfolio. Reusing original baseline NAV as filtered NAV would be wrong. Fills contain partial sizing, dividends and settlement effects; freeing cash changes order competition and strategy state. This pilot does not simulate new replacement trades or leverage. It does not concatenate chromosomes, reset fold cash, compound per-trade returns or turn realized-only PnL into equity. Original NAV could describe its own original account, but cannot provide the requested comparable filtered-account metrics. A portfolio objective cannot be satisfied by optimizing these trade-level sums; this is an independent reason to stop.

Original folds are training from 2009 to strictly before 2012/2014/2016, with evaluations [2012,2014), [2014,2016), [2016,2018). All model choices in the inherited median-rule comparator used earlier completed trades. Selected chromosome identities vary by fold. Current diagnostics perform no fitting. Both entry and exit must lie within each evaluation window; 71 boundary trades are excluded in the inherited ledger, and carried-in positions are absent. This completed-trade censoring limits all results; no independent cash-reset portfolio is claimed. GA8 covers completed 2023/2024/2025 episodes, excluding 11 open positions.

All periods have already been inspected. They are chronological retrospective evaluation, **not pristine OOS**. Chromosomes and DEV79 universe were discovered retrospectively; survivor, universe and prior-search bias persist. DEV79 breadth is a market proxy, not validated point-in-time S&P 500 membership breadth. Entry features precede entries; MA horizons 10/20/50/100/200 and slopes are available but no evidence-based permission to evolve them arose. Earlier correlation significance, isolated year effects and untested nonlinear possibilities do not establish tradable incremental value.

## Reproduction and checks

From repository root:

```sh
/opt/mts/.venv/bin/python experiments/breadth_ga_decision_pilot_20261031/pilot.py
/opt/mts/.venv/bin/python -m unittest discover -s experiments/breadth_ga_decision_pilot_20261031 -p 'test_*.py' -v
```

The deterministic audit takes seconds and hashes all consumed inputs and selected ledgers in decision.json. Tests cover economic opportunity-cost identity, whole-episode gate accounting, shared-event support, future-evidence inability to bypass the portfolio stop, causal feature timing and inherited fold cutoff constraints. No live GA/MTS source, database or configuration was changed. Any future search requires new economic support and validated portfolio accounting; no deployment is recommended.
