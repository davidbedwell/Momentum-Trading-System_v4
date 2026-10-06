# MTS v4 — Held-Out 50 Four-Era $100K Walk-Forward Protocol

**Frozen:** 2026-10-02
**Scientific boundary:** Discovery research bank only
**Primary cohort:** the 50 tickers already frozen in MTS_HELDOUT_TICKER_WALKFORWARD_COHORT_20261002.json
**Reserve:** 186 unused Discovery tickers remain unopened for later replication

## Objective

Test whether the frozen MTS selector, capital allocator, and trade-management architecture generalizes economically to unseen tickers under chronological, finite-account execution, and determine whether performance materially varies by market era.

This is a held-out-ticker generalization study with causal execution. It is not represented as a historical claim that the current genome library existed at the beginning of the replay.

## Evidence conservation

The same frozen 50 tickers are used across their full available historical span. No alternate 50-stock cohort is opened merely to test another time window. Their held-out role is consumed once by this full-history experiment. The remaining 186 unused Discovery tickers remain available as independent replication banks.

## Era design

Use four non-overlapping chronological five-year episodes spanning approximately the final 20 years available through the frozen 2026-09-15 research as-of boundary.

The implementation must derive exact trading-session boundaries from available causal data and report them explicitly. Intended eras are approximately:

1. 20-to-15 years before the as-of boundary
2. 15-to-10 years before the as-of boundary
3. 10-to-5 years before the as-of boundary
4. 5 years before the as-of boundary through present/as-of

Each era is a separate paper-account experiment and begins with exactly **$100,000 cash**. Equity, positions, or gains/losses do not carry across era boundaries.

## Daily simulation contract

For each simulated market session:
1. expose only predictor/market information available by that session close;
2. screen all 50 frozen tickers using the frozen portable MTS candidate architecture;
3. preserve all eligible signals, selected or not;
4. calculate selector/ranking information using no future outcomes from the held-out 50;
5. rank simultaneous opportunities;
6. allocate only capital actually available under the frozen $100K-account portfolio rules;
7. submit entries for the next trading session;
8. simulate entries/exits using only prices that would then have become available;
9. update cash, positions, equity, realized/unrealized P&L, and exposure;
10. compound subsequent allocations from the account's actual current equity/cash.

No future held-out price or outcome may affect candidate eligibility, ranking, sizing, entry, management, or exit.

## Genome portability control

The portable genome/catalog selection rule must be frozen using only the already-consumed 67-ticker Discovery research evidence before held-out 50 outcomes are inspected. The new 50 may not be used to choose which genomes are portable.

## Required reporting

For each era independently report at minimum:
- exact start/end sessions and data coverage;
- starting and ending equity;
- total return and CAGR;
- max drawdown;
- CVaR/tail loss;
- number of eligible signals and executed trades;
- win rate and payoff distribution;
- gross/net exposure and cash utilization;
- skipped opportunities due to finite capital;
- ticker/family/genome breadth and concentration;
- transaction-cost assumptions;
- comparison with appropriate equal/baseline controls.

Also report cross-era consistency and heterogeneity. Do not optimize an era-specific rule after observing its results.

## Limitations

The frozen cohort is drawn from the current-S&P calibration universe and therefore carries survivorship bias. The current MTS genome library was developed using other Discovery stocks through 2026, so this is not a literal time-machine reconstruction of what could have been known in each historical year. It tests cross-ticker generalization and causal portfolio execution on unseen ticker histories.

Verification A and Verification B are not accessed by this study.
