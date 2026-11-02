# GA10 RSI-only evolutionary research

Status: completed generation budget. Completed generations: 2; consecutive stagnant: 0; runtime: 6.2 seconds.

Training: DEV79 2009–2013 only. Evaluation: 2014–2018 after search frozen. Eight worker processes; population 64; maximum 1000 completed generations, early stop at 100 consecutive generations without meaningful best feasible CAGR or frontier improvement. Seed 1010. No GA6/GA7 code or results used.

Fixed screen: prior-session Wilder-style RSI14 bottom floor(20% × eligible count), at least one, stable ticker ties, refreshed monthly. Eligible means finite positive prior adjusted close and finite RSI; no MA20/acceleration eligibility. MA20, acceleration, momentum and volatility remain causal optional policy inputs. Only new positions require screen membership; held stocks can be added/reduced/exited offscreen.

Five evolved action/allocation heads; eight control genes include position cap, exposure, risk stop, cooldown 1–63 sessions, volatility sizing. A stop liquidates and temporarily blocks purchases; cooldown expiry resets the risk reference so cash can re-enter. Daily performance high-water mark never resets. Reduce has priority over add and below exit.

Net returns include 10 bp on each actual buy/sell side. Signals at prior close, executions at next adjusted open. Daily MDD is close-to-close including initial capital; open/close MDD is also reported for saved paths. Initial capital 1, fractional shares, zero cash interest; final holdings marked without liquidation fees.

Meaningful improvement requires feasible CAGR gain >0.0001 (one annual basis point) or a new nondominated point that is not epsilon-covered by the meaningful archive (CAGR 0.0001, MDD 0.0001, Calmar 0.001). Pareto directions: CAGR up, absolute daily MDD down, Calmar up. All exact nondominated points saved, including infeasible MDD ≥25%. Champion selection maximizes CAGR among MDD <25%; all-result maximum CAGR and maximum Calmar also retained.

Adjusted historical archive and retrospective membership are not certified point-in-time. No survivorship-free claim. The 2014–2018 period was examined in prior research and is not pristine validation. Evaluation never selects or modifies genomes. DEV87 is a separate frozen stock transfer, also retrospective.

Latest generation: `{"generation":2,"seconds":0.012459429,"elapsed_seconds":6.1949614701,"stagnant":0,"meaningful_improvement":true,"frontier_size":14,"best_feasible_cagr":0.306999002,"champion_mdd":0.0899027061,"champion_calmar":3.4147915608,"max_cagr":0.306999002}`.

See generations.csv, candidates.csv, frontier.csv/json, champions.json, checkpoint.json, freeze.json, tests.log, smoke/, provenance.json and terminal metrics.csv.
