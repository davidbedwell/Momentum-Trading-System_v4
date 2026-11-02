# GA9 bounded pilot

Command: `/opt/mts/.venv/bin/python -m ga9.run --output ga9/artifacts/pilot_market_primary_override --universe-profile broad_us --benchmark-data /opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet --generations 1 --population 4 --budget 20 --seed 90079`

Primary benchmark: SPY buy-and-hold for declared broad_us universe, frozen before training/test.
Secondary diagnostic: equal-weight buy-and-hold of the complete 79-stock PIT research universe; never the selected subset.
PIT eligibility, $100,000 initial capital, 5bp slippage and 1bp commission per side.
Secondary sleeves remain cash until listing; GEV regular-way listing is 2024-04-02.
Portfolio hard acceptance gate: absolute daily close MDD <=8.00%, including initial capital.
Success additionally requires positive net excess CAGR. No Calmar admission gate.

Configured horizon sessions: [5, 20, 60, 120]; explicit swing cap: None.
Each new position samples its planned expiry from the frozen evolved mixture using a deterministic
date/symbol/genome hash. Native stops and opportunity-cost exits can close it sooner.

Sample: 79 fixed research stocks: ACN, AMGN, ARE, ATO, BEN, BG, BLDR, BNY, CBOE, CDNS, CDW, CFG, CME, COF, COIN, COST, CRM, CTSH, DECK, DELL, DIS, DLTR, ELV, ETN, EVRG, FANG, FCX, FITB, GE, GEV, GILD, GLW, GPC, HD, HPE, HSY, HWM, INTC, IRM, ITW, JNJ, KDP, KKR, KMI, LYB, LYV, MCO, MPC, NFLX, NUE, OMC, PEG, PFG, PPG, RL, ROK, RSG, SBAC, SCHW, SNPS, SO, SPG, STLD, SYF, SYK, T, TECH, TRGP, TRV, ULTA, UPS, V, VRSK, VRSN, WAB, WSM, XEL, XOM, ZTS.

| Year | Phase/control | CAGR % | Primary % | Excess pp | Full EW % | EW excess pp | MDD % | Calmar | Turnover | Exposure % | Closed trades / fills | Max stock % | Max sector % | Pass |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 2023 | training_refit_in_sample | 0.00 | -18.99 | 18.99 | -7.14 | 7.14 | 0.00 | 0.00 | 0.00 | 0.0 | 0 / 0 | 0.0 | 0.0 | yes |
| 2023 | forward_frozen | 0.00 | 25.93 | -25.93 | 28.27 | -28.27 | 0.00 | 0.00 | 0.00 | 0.0 | 0 / 0 | 0.0 | 0.0 | no |
| 2023 | ga8_seed_control | 23.70 | 25.93 | -2.22 | 28.27 | -4.56 | 8.33 | 2.85 | 44.93 | 62.8 | 294 / 862 | 10.8 | 89.6 | no |
| 2023 | momentum_control | 11.95 | 25.93 | -13.98 | 28.27 | -16.32 | 13.35 | 0.89 | 45.83 | 62.1 | 299 / 891 | 10.8 | 86.4 | no |
| 2024 | training_refit_in_sample | -5.29 | 0.91 | -6.20 | 6.26 | -11.55 | 14.50 | -0.36 | 58.64 | 27.1 | 662 / 1730 | 10.3 | 31.1 | no |
| 2024 | forward_frozen | 7.72 | 26.01 | -18.29 | 20.70 | -12.97 | 3.78 | 2.04 | 22.93 | 28.7 | 278 / 761 | 11.6 | 33.7 | no |
| 2024 | ga8_seed_control | 18.47 | 26.01 | -7.54 | 20.70 | -2.23 | 4.05 | 4.56 | 43.74 | 63.8 | 288 / 831 | 11.0 | 85.5 | no |
| 2024 | momentum_control | 14.52 | 26.01 | -11.49 | 20.70 | -6.18 | 3.65 | 3.98 | 46.34 | 62.4 | 305 / 880 | 11.9 | 87.7 | no |
| 2025 | training_refit_in_sample | -0.02 | 8.16 | -8.18 | 10.81 | -10.83 | 14.68 | -0.00 | 89.06 | 27.8 | 1024 / 2647 | 12.0 | 33.0 | no |
| 2025 | forward_frozen | -1.44 | 17.38 | -18.82 | 13.66 | -15.10 | 7.81 | -0.18 | 29.89 | 28.4 | 347 / 904 | 10.1 | 31.0 | no |
| 2025 | ga8_seed_control | 2.85 | 17.38 | -14.53 | 13.66 | -10.81 | 14.39 | 0.20 | 47.55 | 62.9 | 313 / 903 | 10.5 | 84.0 | no |
| 2025 | momentum_control | -1.98 | 17.38 | -19.37 | 13.66 | -15.65 | 15.92 | -0.12 | 50.61 | 58.8 | 346 / 973 | 10.7 | 82.5 | no |

All three GA9 forward folds pass: False. Elapsed: 31.5s.

Selection uses an internal chronological half-year validation segment within each training period.
Benchmark profile, symbol, source hash and complete-universe membership are predeclared in the manifest.
The selected genome is then refit through December and frozen before the next year is loaded.
Training-refit metrics are in-sample diagnostics; internal validation is selection-used.
Forward results never feed model, horizon, or manager selection. Each fold starts a new account;
residual positions are marked, with no fictitious terminal liquidation. No continuous stitched-return claim.

GA8 seed control replays the three source seed genes and manager; it is not the running GA8 champion
or an equal-budget search comparison. Momentum control uses native momentum entry/lifecycle.
Per-gene funded ablations compare full and removed-gene accounts under identical cash/cost constraints.
Predictive discrimination is a separate post-freeze label diagnostic, never a live feature.

Unknown sectors share one conservative sector bucket capped at entry; market drift/gaps can exceed
allocation caps. Verified historical sector classifications and SGOV execution bars are unavailable.
Cash/NO_TRADE is implemented; SGOV remains disabled rather than receiving invented returns.
Dividend receivables are not spendable without payment dates. Data is vendor split-normalized.
Fixed DEV79 membership is not evidence of a historically survivorship-free universe.
GA9 forward folds are protected from GA9 selection, but were previously accessed in GA8 research.
Prior GA9 engineering forward runs disclosed in manifest: ['/opt/mts/ga8/Momentum-Trading-System_v4-ga8/ga9/artifacts/pilot_8pct_same_universe', '/opt/mts/ga8/Momentum-Trading-System_v4-ga8/ga9/artifacts/pilot_8pct_delivery', '/opt/mts/ga8/Momentum-Trading-System_v4-ga8/ga9/artifacts/pilot_8pct_final'].
An observed risk breach is rejected, never clipped; next-open gaps prevent any guarantee of an 8% live cap.

Artifacts: manifest.json, fold_YYYY/frozen.json, selection.json, rejected_risk.json,
training_rejected_risk.json, forward_rejected_risk.json, primary benchmark.json and secondary_full_universe.json,
training_refit/forward_frozen/control JSON and daily CSV ledgers, contribution.json,
discrimination.json, results.json and status.json. Stop via this output directory’s STOP file.
Budget checks occur between candidates; a candidate/refit/reporting task finishes atomically.
No GA8 process, source, output or checkpoint is written by this runner.

The prior same-universe-only report is superseded and archived under `history/`.
This is a one-generation, four-candidate functionality pilot, not a benchmark-tuning
comparison with earlier runs. QQQ is covered by synthetic end-to-end tests only. A
real Nasdaq invocation without QQQ data fails explicitly; see
`artifacts/nasdaq_primary_missing_data/failure.json`. Training-refit risk rejections
are recorded separately and cannot pass acceptance even if forward drawdown is lower.
