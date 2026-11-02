# GA10 RSI-only evolutionary research

Status: completed generation budget; frozen evaluation complete. Completed generations: 1000; consecutive stagnant: 7; runtime: 163.1 seconds.

Training: DEV79 2009–2013 only. Evaluation: 2014–2018 after search frozen. Eight worker processes; population 64; maximum 1000 completed generations, early stop at 100 consecutive generations without meaningful best feasible CAGR or frontier improvement. Seed 1010. No GA6/GA7 code or results used.

Fixed screen: prior-session Wilder-style RSI14 bottom floor(20% × eligible count), at least one, stable ticker ties, refreshed monthly. Eligible means finite positive prior adjusted close and finite RSI; no MA20/acceleration eligibility. MA20, acceleration, momentum and volatility remain causal optional policy inputs. Only new positions require screen membership; held stocks can be added/reduced/exited offscreen.

Five evolved action/allocation heads; eight control genes include position cap, exposure, risk stop, cooldown 1–63 sessions, volatility sizing. A stop liquidates and temporarily blocks purchases; cooldown expiry resets the risk reference so cash can re-enter. Daily performance high-water mark never resets. Reduce has priority over add and below exit.

Net returns include 10 bp on each actual buy/sell side. Signals at prior close, executions at next adjusted open. Daily MDD is close-to-close including initial capital; open/close MDD is also reported for saved paths. Initial capital 1, fractional shares, zero cash interest; final holdings marked without liquidation fees.

Meaningful improvement requires feasible CAGR gain >0.0001 (one annual basis point) or a new nondominated point that is not epsilon-covered by the meaningful archive (CAGR 0.0001, MDD 0.0001, Calmar 0.001). Pareto directions: CAGR up, absolute daily MDD down, Calmar up. All exact nondominated points saved, including infeasible MDD ≥25%. Champion selection maximizes CAGR among MDD <25%; all-result maximum CAGR and maximum Calmar also retained.

Adjusted historical archive and retrospective membership are not certified point-in-time. No survivorship-free claim. The 2014–2018 period was examined in prior research and is not pristine validation. Evaluation never selects or modifies genomes. DEV87 is a separate frozen stock transfer, also retrospective.

Latest generation: `{"generation":1000,"seconds":0.1642410711,"elapsed_seconds":163.0969823152,"stagnant":7,"meaningful_improvement":false,"frontier_size":103,"best_feasible_cagr":0.6020453928,"champion_mdd":0.1213036455,"champion_calmar":4.963126956,"max_cagr":0.6020453928}`.

See generations.csv, candidates.csv, frontier.csv/json, champions.json, checkpoint.json, freeze.json, tests.log, smoke/, provenance.json and terminal metrics.csv.

|Universe/split|Policy|CAGR|Daily MDD|Calmar|Feasible <25%|
|---|---|---:|---:|---:|---|
|dev79_train|feasible_cagr|60.20%|12.13%|4.963|True|
|dev79_train|max_cagr|60.20%|12.13%|4.963|True|
|dev79_train|max_calmar|0.02%|0.00%|25120287.336|True|
|dev79_train|monthly_rsi_buy_hold|35.82%|29.74%|1.204|False|
|dev79_train|cash|0.00%|0.00%|0.000|True|
|dev79_evaluation|feasible_cagr|1.35%|10.39%|0.130|True|
|dev79_evaluation|max_cagr|1.35%|10.39%|0.130|True|
|dev79_evaluation|max_calmar|0.00%|0.00%|0.000|True|
|dev79_evaluation|monthly_rsi_buy_hold|11.82%|26.56%|0.445|False|
|dev79_evaluation|cash|0.00%|0.00%|0.000|True|
|dev87_train|feasible_cagr|15.92%|14.70%|1.083|True|
|dev87_train|max_cagr|15.92%|14.70%|1.083|True|
|dev87_train|max_calmar|0.00%|0.00%|0.961|True|
|dev87_train|monthly_rsi_buy_hold|26.79%|41.96%|0.638|False|
|dev87_train|cash|0.00%|0.00%|0.000|True|
|dev87_evaluation|feasible_cagr|-0.83%|6.51%|-0.128|True|
|dev87_evaluation|max_cagr|-0.83%|6.51%|-0.128|True|
|dev87_evaluation|max_calmar|-0.03%|6.01%|-0.005|True|
|dev87_evaluation|monthly_rsi_buy_hold|20.14%|18.52%|1.088|True|
|dev87_evaluation|cash|0.00%|0.00%|0.000|True|

Terminal audit and runtime:

Completed 1000 generations (64,000 candidate evaluations); search runtime 163.10 seconds, full invocation including compilation, smoke and frozen evaluation 175.56 seconds. Stop reason: completed generation budget; frozen evaluation complete. Terminal stagnation count: 7. Checkpoint includes next population, RNG state, exact frontier and meaningful-improvement archive.

Final training frontier: 103 points, 103 feasible and 0 infeasible. All 839 infeasible candidate results remain in candidates.csv. Best infeasible CAGR result:

Generation 821, candidate 49: CAGR 42.41%, daily MDD 26.26%, Calmar 1.615.

Training Pareto extremes:

|Extreme|CAGR|Daily MDD|Calmar|
|---|---:|---:|---:|
|Maximum CAGR|60.20%|12.13%|4.963|
|Minimum MDD|4.51%|0.00%|0.000|
|Maximum Calmar|0.02%|0.00%|25120287.336|

The entire exact training Pareto set is in [frontier.csv](frontier.csv); every frozen point is evaluated in the `dev79_*_frozen_frontier.csv` and `dev87_*_frozen_frontier.csv` files without reselection. Training champion history including genomes is in [champion_history.csv](champion_history.csv).

Frozen feasible-CAGR champion versus benchmarks:

dev79_train: CAGR difference versus monthly RSI buy/hold +24.39%; daily MDD difference -17.61%. Risk preference met. Cash benchmark CAGR/MDD/Calmar 0/0/0 (Calmar defined as zero for the flat path).

dev79_evaluation: CAGR difference versus monthly RSI buy/hold -10.47%; daily MDD difference -16.16%. Risk preference met. Cash benchmark CAGR/MDD/Calmar 0/0/0 (Calmar defined as zero for the flat path).

dev87_train: CAGR difference versus monthly RSI buy/hold -10.87%; daily MDD difference -27.26%. Risk preference met. Cash benchmark CAGR/MDD/Calmar 0/0/0 (Calmar defined as zero for the flat path).

dev87_evaluation: CAGR difference versus monthly RSI buy/hold -20.98%; daily MDD difference -12.00%. Risk preference met. Cash benchmark CAGR/MDD/Calmar 0/0/0 (Calmar defined as zero for the flat path).

Interpretation: the selected training champion did not generalize. DEV79 evaluation CAGR was 1.35% versus 11.82% for monthly RSI buy/hold; DEV87 evaluation CAGR was -0.83% versus 20.14%. The evolved strategy met the drawdown preference in these evaluations but sacrificed return. No evaluation-based retuning or replacement occurred.

Calmar pathology: the maximum-Calmar training genome earned only 0.0159% annual CAGR with approximately 0.000000000631% daily MDD, producing a ratio around 25 million. This near-cash denominator artifact is retained transparently in the frontier and champion table; it is not evidence of a useful high-return strategy. Zero or extremely tiny MDD makes Calmar unstable.

The selected CAGR champion executed all action branches in training: 13 entries, 748 adds, 196 reductions, 12 exits and 3186 held-position days. Evaluation also includes executed reductions. The forced crash test independently proved stop liquidation followed by cash re-entry; re-entry remains an evolved choice, not a promised recovery.

Accounting and integrity audit passed: independent baseline NAV parity, eligible entries with missing optional predictors, contiguous completed-generation counts, exact stagnation counter reconstruction, all final frontier genomes replayed, nondominance, maximum feasible training CAGR champion, all new entries screened, exposure bounds and source hash. See [verification.json](verification.json).

A preliminary search was stopped before evaluation when an inherited optional-feature finite gate was found. That gate was removed; the study restarted from the original seed. Discarded artifacts and explanation are preserved under `aborted_finite_feature_gate/` and did not seed this search.

Checkpoint resume was separately tested in a temporary copy: saved RNG and next population were preserved and an uncommitted extra generation-log row was trimmed. See resume_verification.json.

No production files were changed. Reproduce or resume with `bash experiments/ga10_rsi_only_evolution_20261101/run.sh`; after completion run `verify.py` and `finalize.py` with `/opt/mts/.venv/bin/python`. An exception stops the study and creates ERROR_AUDIT.txt; no exception triggers an automatic continuation.
