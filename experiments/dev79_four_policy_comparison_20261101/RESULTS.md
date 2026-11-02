# DEV79 four-policy historical comparison

**Completed real portfolio replays. Reconstructed Claude, Gemini and Grok policies are approximations, not source-exact runs. Actual user-supplied Claude/Grok scripts are not staged on this server.**

2009-01-02–2026-09-14; 4,451 identical sessions; $100,000 initial cash each. Price returns only. All signals use information through the current close and execute at the next global session open. No GA, optimization, monitoring, production edits or downloads.

| Policy | Final NAV | Return | CAGR | Max DD | Sharpe (0 RF) | Mean exposure | Fills | Fees | Slippage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| manager | $95,981.99 | -4.02% | -0.23% | 23.86% | 0.011 | 46.33% | 18,944 | $36,601.42 | $36,601.43 |
| claude_approx | $322,734.44 | 222.73% | 6.86% | 34.35% | 0.535 | 67.48% | 46,061 | $74,863.92 | $74,863.96 |
| gemini_approx | $948,380.90 | 848.38% | 13.58% | 30.43% | 0.821 | 96.10% | 157,562 | $67,566.99 | $67,567.01 |
| grok_dev79_approx | $1,240,500.44 | 1140.50% | 15.32% | 38.36% | 0.906 | 91.90% | 15,521 | $2,568.52 | $2,568.50 |

Comparisons measure these implementations under shared assumptions, with different policy exposure and turnover by design. They do not establish model/vendor superiority, alpha, out-of-sample performance or a historically investable universe. Fees/slippage are already deducted in NAV. Fill counts are not completed round trips.

## Shared execution and accounting

- Fractional long-only shares, zero leverage/cash yield/tax. Adverse slippage 5 bps and fee 5 bps per side; fee charged on slipped notional. No calibrated impact or volume participation limit.
- Close dollar targets are frozen before the next session. Next-open quantities use actual open prices. Sells execute first, then alphabetical buys. Sale proceeds settle at the next session, so cannot fund same-session buys. Cash and policy admission caps can clip buys, giving alphabetical priority when cash constrained. This scenario is applied across the full history, rather than reconstructing historical T+2/T+3 settlement.
- Manager keeps its original max($25, 0.5% NAV) drift threshold and unconditional deselection exits. Other arms trade target differences above $0.01; this preserves their requested rebalancing intent but makes daily reweighting costs material. Admission caps apply at opens, not hard drift limits: later gaps can exceed them.
- Missing next open cancels the order; a later close can issue a new order. Missing held closes use last observed close for valuation only and are logged. No price backfill. Missing signal windows block entries. Final NAV marks to close, without liquidation; last-close orders are explicitly unexecuted.

## Policy definitions and deviations

1. **Existing completed manager:** original OHLCV features, ranks, top ten selection, volatility sizing, breadth throttle, drawdown throttle and rebalance threshold retained. Its open caps remain 10% per name / 90% gross. Every daily value, fill, order, position and decision matches the prior completed run within numerical tolerance; this is a replay of the existing manager, not a new fit.
2. **Claude approximation:** positive 126-session close momentum, close above 200-session SMA; rank momentum descending, ticker tie-break, top ten. ATR is a 14-session simple average of true range, with missing previous close invalidating the value. A 2-ATR trailing stop is evaluated at close against the prior stop, then raised from the current close; liquidation occurs next open. The 2-ATR multiplier, ATR window/smoothing and close-stop treatment are reconstruction choices, not supplied-source facts. Initial stop is set from decision close. Stopped names are excluded that decision, but can reenter later. Risk weight min(10%, 2% NAV / (2 ATR / close)), then scale all weights to at most 70% gross. Stops are sizing assumptions, not guaranteed 2% losses; overnight gaps and costs can exceed risk. At 15% close drawdown from risk high-water mark, target cash for 20 decision-session intervals; resume at interval 20 and reset that risk anchor. Threshold, duration and reset are explicit defaults because halt details were unspecified. The reporting drawdown high-water mark never resets. No intraday stops or optimization.
3. **Gemini approximation:** long whenever SMA20 > SMA50, with complete trailing windows; daily equal weight across all active signals, target 100% gross, otherwise cash. This uses signal state rather than crossover-only order events. Daily reweighting, 100% budget and fractional shares are explicit interpretation choices. Sells are processed before buys; shared T+1 settlement prevents reuse of same-day sale proceeds. This avoids reproducing ambiguous native buy/sell sequencing and possible cash/order artifacts. No source-exact Gemini run claimed.
4. **Grok approximation, DEV79 adaptation:** target 98% / 79 per symbol, rebalance after the first observed session close of each calendar month (including sample start); execute next open. All 79 get identical target weights, replacing any source-specific subset. Unlisted/unavailable symbols retain their allocation slot as cash; available stocks are not renormalized. New listings enter at a later monthly rebalance. Corrects the described same-close execution to causal next-open execution. Monthly schedule, fractional shares and missing-listing handling are reconstruction choices. No source-exact run claimed.

## Corporate actions and universe

The fixed archive is `/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet`. Features use only OHLCV, with all available pre-2009 observations providing causal warmup. Raw volume is used, not the enriched signed/transformed volume feature. Hashes, exact archive/enriched price and identity reconciliation, 79-symbol coverage and split continuity are in artifacts/input_audit.json and split_continuity.csv.

Prices are treated as split-adjusted, supported by existing audit and empirical continuity (35 of 35 major split events favor adjustment). Holdings are not multiplied again by split factors. This is not independent vendor certification, and restated historical adjustment factors may use future information. Dividends are excluded for every policy because payment dates and adjusted per-share cash basis are unverified; these are not total returns. No independent merger/delisting cashflow reconstruction is available.

DEV79 is a retrospective fixed-survivor universe, not a point-in-time membership roster. Later listings, survivor selection, vendor collection and historical revision bias remain. No earnings/sector/GA or synthetic signals enter this replay. Shared execution makes the policy comparison consistent; it cannot remove these source limitations.

## Verification and reproduction

Independent per-policy reconstruction checks cash, T+1 unsettled proceeds, shares, NAV, fee/slippage arithmetic, chronological sell/buy order and every archived next-session open. Manager parity and future-mutation indicator tests passed; controlled missing-open, settlement, signal, sizing, stop and halt checks passed. See artifacts/verification.json and verification.log.

Maximum independent NAV/cash error: $1.16415e-09. Runtime: elapsed_seconds=46.49 peak_rss_kb=848680 cpu=99%.

Run from repository root: `bash experiments/dev79_four_policy_comparison_20261101/run.sh`. Each policy directory contains decisions, orders including cancellations/terminal pending orders, fills, positions, daily cash/unsettled/NAV/PnL and stale marks. Common features are in features.csv.gz; metrics.json and summary.csv use identical formulas. CAGR uses 252 sessions/year, daily-return Sharpe uses zero risk-free rate, turnover is total traded open notional / initial cash. No terminal liquidation costs are charged.

All newly written files are confined to this experiment folder. Original files and pre-existing workspace changes were preserved. Source and result hashes are in checksums.json.
