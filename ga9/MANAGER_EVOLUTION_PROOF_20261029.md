# GA9 bounded synthetic manager evolution — executed

Completed 100 population × 25 generations in **284.253 seconds** (4m44s), stopping at the generation cap. One serial worker, numerical threads capped at one, `nice -n 10`. GA8 files/processes were not modified or stopped. No autonomous manager was deployed.

Scope: explicitly synthetic six-stock, 1,260-session fixture (five trading years at 252 sessions/year), seed 91029; first 756 sessions train, final 504 sessions untouched holdout. Static stock niches, price-derived causal momentum/trend/rank signals, six fixed specialists (two per niche). Holdout has a predeclared negative drift shift. Synthetic membership/screens are always eligible. This is an engineering pilot, not historical certification or realistic market calibration. Idle capital is zero-yield cash; SGOV execution/returns are not modeled. No fitted signal models or strategy genomes were evolved.

| Replay | Net CAGR | Benchmark CAGR | Final NAV | MDD | Fills | Costs |
|---|---:|---:|---:|---:|---:|---:|
| Baseline train | 2.872% | 2.377% | $108,865.68 | 1.228% | 1,068 | $4,408.32 |
| Evolved train | 4.037% | 2.377% | $112,607.78 | 0.391% | 217 | $777.23 |
| Baseline holdout | 3.604% | 0.703% | $107,338.31 | 0.616% | 692 | $2,866.12 |
| Evolved holdout | 3.039% | 0.703% | $106,170.30 | 0.543% | 185 | $628.84 |

The winner beats the synthetic benchmark on holdout, but **underperforms the baseline holdout CAGR by 0.565 percentage points**. Training return improvement did not generalize against the baseline. The holdout penalized objective improves from −0.014033 to +0.005195 because costs, concentration and drawdown decrease. This supports functional evolution and a risk/cost tradeoff, not a general return advantage or deployment approval.

Fitness = net portfolio CAGR − benchmark CAGR − 2 × MDD − costs/100,000 − 0.1 × mean equity-position HHI. Infeasible candidates additionally lose 10 + 100 × excess drawdown over 8%. Net NAV already includes costs; the explicit cost term further discourages churn. The benchmark is synthetic equal-weight buy-and-hold, same first executable open and entry slippage/fee, residual shares marked daily. Both holdout accounts restart at $100,000; this is a frozen-policy independent holdout test, not one continuous five-year account.

Manager chromosomes evolve niche biases, individual specialist biases, entry floor, competitive size scale/score sizing, slots, cash reserve, correlation/risk/sector limits, replacement threshold, add permission, reduction threshold and discretionary exit threshold. Specialist routing still precedes generalist fallback. Native membership, loss, trailing, time and strategy exits retain priority over manager discretionary exits. Orders use next-open fills, shared settled cash, T+2 sale settlement, 5bp slippage and 1bp fee per side. No NAV clipping or synthetic risk-ceiling guarantee: the 8% limit is a feasibility acceptance criterion; price gaps can breach it. All candidates in this mild fixture were feasible, so this run does not stress the rejection boundary.

Actual GA: initial baseline, cash/NO_TRADE control and mutated policies; top-ten parent selection; five elites; uniform manager-field crossover plus mutation. 2,500 candidate slots, 2,380 unique evaluations. Best fitness improves from −0.009021217 in generation 1 to −0.000008005 in generation 25; median from −0.044927271 to −0.015802441. Each generation has 100 distinct genomes and 60–93 distinct executed-trade fingerprints. This demonstrates decision diversity and improvement beyond the initial population, while the holdout exposes limited return generalization.

Proof checks: **31 tests passed**. Persisted winner training replay reproduces exactly. Destructively changing all holdout prices/signals leaves training replay identical. Restoring baseline ranking controls, allocation controls, or position-management controls individually changes winner fills. Winner train actions: 82 entries, 19 adds, 37 reductions, 79 exits; holdout: 68 entries, 16 adds, 34 reductions, 67 exits. Daily ledgers preserve ranked specialist candidates, orders, NO_TRADE events, cash, holdings, NAV, drawdown and benchmark NAV.

Artifacts are in [manager_evolution_synthetic_20261029](artifacts/manager_evolution_synthetic_20261029):

- `report.json`: full metrics, winner genome, per-generation best/median/diversity/feasible counts and runtime.
- `generations.csv`, `generation_01.json` … `generation_25.json`: all population chromosomes and candidate metrics/signatures.
- `baseline_train.json`, `baseline_holdout.json`, `winner_train.json`, `winner_holdout.json`: full replay ledgers.
- `fixture.npz`: exact synthetic inputs; `checkpoint.json`: population, evaluation cache, RNG state, completed generation and elapsed runtime, atomically saved each generation.
- `verification.json`, `tests.log`, `run.log`, `sha256.json`: exact checks, execution log and hashes.

Reproduce in a fresh output directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 10 /opt/mts/.venv/bin/python -m ga9.manager_pilot --output /tmp/ga9-manager-pilot-new
OPENBLAS_NUM_THREADS=1 /opt/mts/.venv/bin/python -m ga9.verify_manager_pilot /tmp/ga9-manager-pilot-new
OPENBLAS_NUM_THREADS=1 /opt/mts/.venv/bin/python -m unittest ga9.test_manager_pilot ga9.test_functionality_fixture ga9.test_execution ga9.test_first_replay ga9.test_benchmarks -q
```

The same run command resumes an existing checkpoint. The runner checkpoints and returns if a generation completes after 30 minutes in an invocation; this run finished well below that threshold. Full generation checkpoints bound interruption loss to at most the current population evaluation. No historical broad-universe or autonomous deployment claims follow from this synthetic proof.
