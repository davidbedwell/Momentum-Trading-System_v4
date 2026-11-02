# GA9 bounded pilot

Command: `/opt/mts/.venv/bin/python -m ga9.run --output ga9/artifacts/pilot_8pct_delivery --generations 2 --population 4 --budget 20 --seed 90079`

Sole benchmark: equal-weight buy-and-hold of the exact evaluated sample, identical dates,
PIT eligibility, $100,000 initial capital, 5bp slippage and 1bp commission per side.
Fixed sleeves remain cash until listing; GEV regular-way listing is 2024-04-02.
Portfolio hard acceptance gate: absolute daily close MDD <=8.00%, including initial capital.
Success additionally requires positive net excess CAGR. No Calmar admission gate.

Configured horizon sessions: (5, 20, 60, 120); explicit swing cap: None.
Each new position samples its planned expiry from the frozen evolved mixture using a deterministic
date/symbol/genome hash. Native stops and opportunity-cost exits can close it sooner.

Sample: 79 fixed research stocks: ACN, AMGN, ARE, ATO, BEN, BG, BLDR, BNY, CBOE, CDNS, CDW, CFG, CME, COF, COIN, COST, CRM, CTSH, DECK, DELL, DIS, DLTR, ELV, ETN, EVRG, FANG, FCX, FITB, GE, GEV, GILD, GLW, GPC, HD, HPE, HSY, HWM, INTC, IRM, ITW, JNJ, KDP, KKR, KMI, LYB, LYV, MCO, MPC, NFLX, NUE, OMC, PEG, PFG, PPG, RL, ROK, RSG, SBAC, SCHW, SNPS, SO, SPG, STLD, SYF, SYK, T, TECH, TRGP, TRV, ULTA, UPS, V, VRSK, VRSN, WAB, WSM, XEL, XOM, ZTS.

| Year | Phase/control | CAGR % | Benchmark % | Excess pp | MDD % | Calmar | Turnover | Exposure % | Closed trades / fills | Max stock % | Max sector % | Pass |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 2023 | training_refit_in_sample | 0.49 | -7.14 | 7.63 | 0.75 | 0.65 | 8.28 | 1.7 | 69 / 139 | 6.3 | 12.4 | yes |
| 2023 | forward_frozen | 1.18 | 28.27 | -27.08 | 0.52 | 2.29 | 7.21 | 1.4 | 60 / 120 | 6.2 | 18.2 | no |
| 2023 | ga8_seed_control | 23.70 | 28.27 | -4.56 | 8.33 | 2.85 | 44.93 | 62.8 | 294 / 862 | 10.8 | 89.6 | no |
| 2023 | momentum_control | 11.95 | 28.27 | -16.32 | 13.35 | 0.89 | 45.83 | 62.1 | 299 / 891 | 10.8 | 86.4 | no |
| 2024 | training_refit_in_sample | 1.70 | 6.26 | -4.56 | 1.90 | 0.89 | 9.23 | 2.2 | 110 / 241 | 7.6 | 16.1 | no |
| 2024 | forward_frozen | 1.14 | 20.70 | -19.56 | 1.48 | 0.77 | 5.64 | 2.7 | 68 / 149 | 6.4 | 14.2 | no |
| 2024 | ga8_seed_control | 18.47 | 20.70 | -2.23 | 4.05 | 4.56 | 43.74 | 63.8 | 288 / 831 | 11.0 | 85.5 | no |
| 2024 | momentum_control | 14.52 | 20.70 | -6.18 | 3.65 | 3.98 | 46.34 | 62.4 | 305 / 880 | 11.9 | 87.7 | no |
| 2025 | training_refit_in_sample | 1.09 | 10.81 | -9.72 | 7.58 | 0.14 | 64.78 | 21.9 | 657 / 1705 | 10.2 | 26.5 | no |
| 2025 | forward_frozen | -0.31 | 13.66 | -13.98 | 5.55 | -0.06 | 21.23 | 22.9 | 212 / 566 | 10.1 | 25.9 | no |
| 2025 | ga8_seed_control | 2.85 | 13.66 | -10.81 | 14.39 | 0.20 | 47.55 | 62.9 | 313 / 903 | 10.5 | 84.0 | no |
| 2025 | momentum_control | -1.98 | 13.66 | -15.65 | 15.92 | -0.12 | 50.61 | 58.8 | 346 / 973 | 10.7 | 82.5 | no |

All three GA9 forward folds pass: False. Elapsed: 29.4s.

Selection uses an internal chronological half-year validation segment within each training period.
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
Prior GA9 engineering forward runs disclosed in manifest: ['/opt/mts/ga8/Momentum-Trading-System_v4-ga8/ga9/artifacts/pilot_8pct_same_universe', '/opt/mts/ga8/Momentum-Trading-System_v4-ga8/ga9/artifacts/pilot_8pct_final'].
An observed risk breach is rejected, never clipped; next-open gaps prevent any guarantee of an 8% live cap.

Artifacts: manifest.json, fold_YYYY/frozen.json, selection.json, rejected_risk.json,
forward_rejected_risk.json, training_refit/forward_frozen/control JSON and daily CSV ledgers, contribution.json,
discrimination.json, results.json and status.json. Stop via this output directory’s STOP file.
Budget checks occur between candidates; a candidate/refit/reporting task finishes atomically.
No GA8 process, source, output or checkpoint is written by this runner.

Engineering record: the first pilot's rejected 2025 8.66% MDD account is preserved
in `rejected_research.json`. A second attempt stopped on constant-rank diagnostic
serialization; its `failure.json` is retained. The delivered run fixes that diagnostic
without changing seed, search budget or horizon grid. These are engineering reruns,
not untouched global forward evidence. The verifier accepts floating point summation
error below 1e-8 dollars in initial sleeve capital; the 8% risk gate has no relaxed tolerance.
