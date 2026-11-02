# DEV79 real-data feasibility audit

Decision: **blocked; no predictor or portfolio fabricated, no pilot run**. This is a bounded local provenance audit authorized on 2026-11-01. Real-stock predictive edge remains untested. Only this directory was written. No production, GA, monitoring, or external fetch was initiated. The managed-environment status tool was unavailable; no remote readiness is assumed.

## Located panel and constituents

Three matching 79-symbol panels were inventoried directly, without executing their builders or strategy code:

| File | Rows | Columns | Coverage |
|---|---:|---:|---|
| `/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet` | 394,795 | 11 | 2004-09-01–2026-09-14 |
| `/opt/mts/ga5_redesign/exploratory79_features.parquet` | 394,795 | 19 | 2004-09-01–2026-09-14 |
| `/opt/mts/ga6/data/ga6d_defensive_features.parquet` | 394,795 | 95 | 2004-09-01–2026-09-14 |

See `data_inventory.json` for authoritative column lists/counts, SHA-256 hashes and coverage. Each panel has 5,543 distinct dates and no duplicate date/symbol rows. Coverage is ragged, not 79 securities throughout. The archived 2009–2018 gate covers 179,265 rows, 2,516 dates and **77** symbols; COIN and GEV are absent. Original runner filtering is 2005-09-14–2026-09-14, distinct from full source coverage and the archived audit window. No window was selected by performance.

Exact symbols, common to all three panels:

ACN, AMGN, ARE, ATO, BEN, BG, BLDR, BNY, CBOE, CDNS, CDW, CFG, CME, COF, COIN, COST, CRM, CTSH, DECK, DELL, DIS, DLTR, ELV, ETN, EVRG, FANG, FCX, FITB, GE, GEV, GILD, GLW, GPC, HD, HPE, HSY, HWM, INTC, IRM, ITW, JNJ, KDP, KKR, KMI, LYB, LYV, MCO, MPC, NFLX, NUE, OMC, PEG, PFG, PPG, RL, ROK, RSG, SBAC, SCHW, SNPS, SO, SPG, STLD, SYF, SYK, T, TECH, TRGP, TRV, ULTA, UPS, V, VRSK, VRSN, WAB, WSM, XEL, XOM, ZTS.

The three `*_constituents.csv` files preserve each symbol's first/last dates, row count and observed security IDs. These are file identities, not verified issuer histories or historical index membership. BNY and other historical aliases require dated identity evidence. No DEV87 panel was accessed.

## Corporate actions, feature lineage and provenance gates

Each panel carries `dividends`, `stock_splits` and `security_id`: 4,918 nonzero dividend rows and 48 nonzero split rows, with no nulls in those two action columns. Presence is not correctness certification. No release/availability/vintage/revision/payment-date columns matching the audit scan were found. Correct execution-price adjustment basis, split accounting, spin-offs, delisted terminal prices, payment dates, and historical publication vintages are not established by this inventory. Price value validity and complete action reconciliation were not certified.

The raw hash and exploratory feature hash match the archived assumptions. `launch_exploratory_79.py` joins raw bars to a legacy `dev80_predictors.parquet` by date/ticker/security ID to obtain a **static** sector map, then calls `canonical_engine.prepare` / `ga5_feature_families.compute`. Its original predictor path is under `/opt/mts/thunder-migration/.../ga4_dev80_checkpoint/dev80_predictors.parquet`; the enclosing tree was permission-denied during discovery, so its original schema and vintages are unverified here. This legacy predictor is not evidence of a real-stock five-tier sensor.

Read gates: `/opt/mts/ga7-deploy/current/ga7/RESEARCH_CONTRACT.md`, `ga7/runner.py`, `canonical_engine.validate_science`, and archived `ga6_ga7_dev79_provenance_gate_20261028.json` (copied here). The archived status is `CERTIFICATION_BLOCKED_INPUT_PROVENANCE`:

- Membership equals observed price-bar presence; all 179,265 historical rows are eligible. Independent historical membership fails.
- Sectors are retrospective static labels, without verified time-t sector history.
- Earnings dates are retrospective EODHD report dates without historical knowledge timestamps.
- Niche training chronology passes, but niche input-feature provenance fails.
- Dividend payment dates and historical cash yield fail; risk veto is uniformly permissive.

The runner requires action/identity columns, exactly 79 symbols, no duplicate bars, membership entries, defense tape and veto dates. These structural checks do not establish PIT provenance; it fills missing actions with zero. The contract explicitly requires failing closed on incomplete inputs and describes the runner as an uncertified prototype. No runner or canonical simulator was executed.

Current independent-repository `manifest.json` remains uncertified: PIT membership/GICS, identities, calendar, delisted terminal prices and as-filed source coverage are incomplete; 2019/2020 are contaminated. Available 2019 identity/membership/technical studies, SPY/breadth features and sector ETF panels are different inputs/hypotheses. ETF schemas and hashes are in `independent_data_inventory.json`; none verifies the needed stock sensor. No sealed-stage outcomes were evaluated.

## Original five-tier predictor and frozen 8B-Cal

The dependency chain is `iteration8b_calibration_validation/engine.py` → `iteration8_four_arm/corrected/engine.py` → `discrimination_iteration6/engine.py` → `discrimination_iteration5/experiment.py`. The wrapper resolves live dependency locations rather than exclusively its archived copies; current source hashes are recorded in `source_hashes.json` without importing these modules.

The iteration5 generator draws latent class `z` in 0…4, then creates noisy channels `x=z+N(0,.30)` and `v=z+N(0,.50)` (independent class in the null scenario). It rounds/clips their precision-weighted combination into sensor cell 0…4. Reversals invert cells. The generator also plants class-conditional returns. Those channels have no real-stock measurement definitions, units, data sources or historical availability contract.

Inference itself does not read latent truth: it fits per-cell forward net-return means and lag-price slopes, calibration uncertainty and tier intervals from prices plus the supplied sensor. Tier boundaries are −0.006, −0.002, +0.002, +0.006; insufficient support or uncertainty causes UNKNOWN. This separation does **not** make the sensor computable on real stocks. Prices alone are insufficient to reproduce its inputs. Mapping momentum ranks, sectors, GA4 features, realized returns or ticker IDs to these cells would invent a different predictor.

8B-Cal is an empirical CUSUM abstention layer over that classifier, not an independent stock predictor. Its frozen thresholds are **0.027659290213926383** and **0.055015578352069085**. The calibration file hash matches the threshold lock (`dc43b9acf256c1b512015a4c6c58244485a3ddfaf6e83fdec03e4e5bad98314d`). It estimates the training cell-4-minus-cell-0 outcome contrast, accumulates adverse changes with drifts .018/√4 and .018/√16, and latches all labels to UNKNOWN after threshold crossing. There is no anytime-valid false-alarm guarantee or demonstrated real-market calibration.

The implementation hardcodes 24 assets, requires at least two assets in each extreme cell for a contrast, and uses fixed index windows: train 0…399, calibration 403…602, test 606…731. Outcomes enter at signal index+3; execution is index+1 to index+2, with .003 round-trip modeled friction. These synthetic conventions are not verified real-stock open/close availability, costs or execution. Generalizing to 79 ragged histories is an explicit adapter change requiring validation, not a harmless relabeling.

## Blocking gaps and smallest actionable step

The decisive gap is the missing real-stock sensor definition. No amount of additional historical bars can recover that definition from synthetic latent truth. **Stop before preregistration or portfolio replay.** Zero comparative returns, edge estimates or buy-and-hold metrics were calculated.

Smallest next deliverable: freeze a real-stock feature contract and a small provenance-backed historical sample. For each channel specify economic meaning, formula, units, symbol/security identity, source URI/hash, event/release/available/decision timestamps, revision/vintage, missing-value handling, and any train-only cell construction. Require availability ≤ decision time and chronological outcome maturity. If no real measurement counterpart exists, explicitly register a new predictor hypothesis rather than claiming to port the synthetic predictor.

After that contract is verified, resolve identity/action/price-basis and required PIT inputs; validate a ragged-universe adapter while retaining frozen CUSUM parameters. Only then preregister chronological train/calibration/test folds, embargo/maturity rules, missing data and IPO/delisting handling, one unchanged real predictor with/without 8B-Cal, and equal-weight DEV79 initial buy-and-hold. Specify initial capital, shared next-session execution, friction/slippage, settlements, dividends, split handling, terminal liquidation, sparse-cell behavior, and all inspected periods before evaluation. Buy-and-hold must explicitly handle absent pre-IPO constituents without retrospective reweighting. No runnable experiment is preregistered here because these definitions are unresolved.

Reproduce the inventory with `/opt/mts/.venv/bin/python experiments/mts_v5_planted_signal_20261101/dev79_real_data_pilot/audit.py`. It pins one CPU, caps CPU use at 1,200 seconds, reads existing local files and writes only this directory. The inventory finished in a few seconds; the entire audit stayed within the requested 1,200-second timebox. `report.json` is the machine-readable stop decision.
