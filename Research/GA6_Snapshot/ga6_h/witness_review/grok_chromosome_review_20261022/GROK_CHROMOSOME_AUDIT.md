# GA6-H Independent Adversarial Review (Grok)

**Role:** Independent quantitative software reviewer. Challenge the chromosome spec/implementation, Claude’s audit, and ChatGPT’s evaluation. Prefer code-backed defects over narrative. Fast experiment first; no multi-week engineering. Synthetic/diagnostic metrics are **not** trade EV.

---

## 1. Executive disagreements (spec, Claude, ChatGPT)

| Claim | Verdict | Why |
|---|---|---|
| Spec “aim ≥35% CAGR” as search north star | **Reject as fitness** | Spec itself says do not equate fitness with CAGR. Keep as post-hoc portfolio report only. |
| Claude: map rank-IC → `net_ev` | **Reject** | Agrees with ChatGPT. IC is auxiliary. Calling IC “net_ev” falsifies the fitness contract and the user’s rule. |
| Claude: top-k − bottom-k spread as discovery fitness | **Reject as primary** | Not executable long-only net EV under cash, next-open, costs, stops, 40-session cap. |
| Claude: stagnation = infinite reset-and-continue | **Reject** | Conflicts with bounded CPU / fast experiment. ChatGPT is right: bounded restarts or stop-and-report. |
| Claude: `nondominated` “will crash on duplicate metrics” | **Speculation until repro** | Possible with identical metric vectors; not demonstrated. Treat as QUICK WIN harden, not proven blocker. |
| Claude: path-corruption in `tree_crossover` root/leaf | **Real but low severity** | Code-backed inconsistency; masked by retries. |
| ChatGPT: only full executable path P&L counts as `net_ev` | **Agree in principle** | Correct semantics. For *first* scientific run, allow a **minimal executable proxy** (next-open, costs, hold/exit genes) on a tiny cached panel — still not certification EV. |
| Spec/grammar: lag + missing_policy in leaf | **Spec/code drift** | Absent in code; fail-closed missing is fine for v0. Document; don’t block. |
| GA6-H as GA6 niche clone | **Correctly avoided** in code (no niche in identity). Keep. |
| Survivor-only universe | **Disclosed limitation** | Not a silent bug. Every discovery report must carry the conditional-universe disclaimer. Not proof of live historical CAGR. |

**Hard rule for this review:** Do **not** assert diagnostic IC, leaf-count, or hold-session toys as trade EV. `discovery_fitness.OBJECTIVES` may stay namespaced as discovery metrics only if the evaluator docstring and `evaluator_id` state they are **not** executable portfolio EV.

---

## 2. Code-backed bugs vs speculation

### 2.1 Real bugs / defects (code-backed)

**B1 — Fitness is non-empirical (blocker for “discovery”)**  
`evolution_engine.diagnostic_evaluator`:

```python
'net_ev': 1/(1+abs(genome.hold_sessions-15)),
'ev_per_session': 1/(1+genome.hold_sessions),
'reliability': 1-genome.stop_loss,
...
'opportunity_coverage': leaves/8
```

Pure function of genes. No prices, ranks, fills, or costs. Any archive from this evaluator is infrastructure-only. **MUST BEFORE REAL DISCOVERY.**

**B2 — Two crossovers; flat crossover destroys nesting**  
`context_free_genome.crossover` always rebuilds a flat `{'op', 'children': ...}`.  
`genetic_operators.tree_crossover` preserves subtrees.  
`breed()` uses `tree_crossover` then `structural_mutation` — good.  
But `context_free_genome.crossover` remains a foot-gun if imported. Nested depth is not exercised by the flat path. **QUICK WIN:** make `tree_crossover` the only public breed crossover; demote/remove flat crossover or test it does not run in `breed`.

**B3 — `tree_crossover` root donor filter**  
```python
donor_candidates=[n for p,n in nodes(b.tree) if target or 'children' in n]
if not target: tree=donor
```
`bool(())` is False, so root replace requires donor with `'children'`. Leaf-as-root donor excluded. Retries usually mask it. **QUICK WIN** (explicit `target == ()`).

**B4 — `validate_tree` / mutation can waste budget on invalid ungroup**  
`ungroup` can produce `<2` children; `validate_tree` rejects; `except: continue`. No crash; burns the 80-attempt loop. **QUICK WIN** guard.

**B5 — Stagnation terminates; no bounded restart**  
```python
while generation<generations and generation-last_improvement<patience:
...
stop_reason': 'stagnation' if ...
```
Spec prose about “stagnation reset” is **not** implemented. Claude oversells “silent fail”; it **stops**, it does not corrupt the archive. For fast experiments, **stop-and-report is acceptable**. Optional: `max_restarts: int = 1..2` only. **QUICK WIN / policy choice**, not a correctness bug.

**B6 — Archive stores identity string only**  
```python
{'genome': g.identity(), 'metrics': validate(m)}
```
Resume cannot rehydrate elite genomes from archive alone (checkpoint `members` can). **QUICK WIN** store `asdict(genome)` + identity.

**B7 — Simulator realism gaps (optimistic if over-read)**  
`daily_simulator.simulate`:
- No split/dividend cashflows (docstring admits diagnostic).
- Forced exit by `hold_sessions` only in the pending path shown; genome `stop_loss` / `trailing_stop` / `replace_threshold` **not applied** in simulator.
- Buys ignore rank **threshold** / score gap; any finite score can queue buy until `max_positions`.
- `entry_threshold` lives on genome / `context_scoring`, not wired into `simulate`.
- No corporate-action adjustment assertion.

These are **real integration gaps**. Using simulator CAGR as discovery fitness **today** would be false precision. **MUST BEFORE REAL DISCOVERY** if fitness claims executable net EV; else keep simulator as separate portfolio harness.

**B8 — `score_tree` vs ranking semantics**  
Expression returns (bool, margin). Ranking methods `weighted|count|margin` on `Genome` are **not used** in `context_scoring.score_tree` / `evaluate_contexts`. Rank method gene is mostly inert. **MUST wire or drop from identity** before claiming ranking evolution.

**B9 — Embargo fail-closed**  
`entry_allowed`: missing verified schedule → False. Correct per spec. Risk is operational (zero buys if `verified_tickers` empty), not leakage. **Document; fixture test.**

**B10 — Process pool chunksize**  
Already `max(1, ...)`. Claude correctly notes no bug.

### 2.2 Spec/code drifts (not silent runtime crashes)

- Leaf `lag`, `missing_policy` in spec; absent in code (fail-closed missing).
- Repeated **family** allowed if leaf tuples differ — matches GA6-H intent; GA6 structural forbid **not** inherited. Claude right that this is OK; add test.
- `hold_sessions` gene vs “predicted horizon ≠ executable hold”: simulator uses hold as executable cap segment; mandatory 40 cap not applied as `min(hold,40)` beyond gene validate max 40. Gene already ≤40. OK.
- Pareto objectives name `net_ev` while diagnostic is synthetic → **naming hazard**. Rename diagnostic keys or mandate `evaluator_id` prefix forever.

### 2.3 Speculation / overreach to downgrade

| Claim | Classification |
|---|---|
| Pareto crash on duplicate fitness | Harden if cheap; need unit test. Not blocker. |
| EPS 0.0001 “archive never stagnates” | Plausible with real noisy EV; irrelevant under diagnostic evaluator. Calibrate **after** real metrics exist. |
| Price-adjustment flag = verification | ChatGPT right: flag ≠ proof. |
| Date-range parameter on evaluator | Good hygiene; not a present leakage bug in diagnostic path. |
| Raise inner mutation attempts 80→200 | Optional; not root-cause of non-discovery. |
| Full PIT delist universe before first run | **REJECT** for fast path (spec already defers). |
| Sobol thresholds | **REJECT** now. |
| Jaccard diversity logging | Nice; not required for first scientific signal. |

---

## 3. Fitness semantics: IC vs executable net EV (central fight)

**Contract in `discovery_fitness.py`:** maximized `net_ev`, `ev_per_session`, `reliability`, `training_consistency`, `opportunity_coverage`. Comments: no CAGR/MDD/held-out.

**Correct scientific layering:**

1. **Discovery signal quality (fast, cached):** cross-sectional score at close‑t → **auxiliary** rank-IC / hit-rate to forward **simple** returns at multiple horizons — **never named net_ev**.
2. **Discovery executable proxy (minimum scientific bar for `net_ev`):**  
   long-only, next-open entry, cost bps, apply **entry threshold**, **hold_sessions** (1–40), optional simple stop if gene present, cash/position caps; metric = mean net PnL per completed episode (and per session), reliability across folds, coverage of tradable episodes. Still **not** sealed-blind certification and **not** survivor-free live CAGR.
3. **Portfolio OOS report:** CAGR, MDD, Calmar, fees, hit rate, avg/max hold — **outside** genetic objective.
4. **Sealed blind / paper:** untouched.

**Disagreement with Claude:** IC→`net_ev` mapping is disallowed.  
**Agreement with ChatGPT:** executable semantics for anything called EV.  
**Disagreement with ChatGPT only on sequencing:** a **bounded** executable proxy on a **small cached panel** is enough to start search; full production simulator parity is certification (G2/G7), not day-0 blocker if labeled `discovery_proxy_v1`.

**Do not** optimize portfolio CAGR inside the GA loop for the fast experiment.

---

## 4. Grammar / operators

- Nested AND/OR + leaf schema: basically sound; complexity cap 8 leaves; duplicate identical leaves rejected.
- Policy genes: hold, stops, replace, entry, weight, rank_method — several **unevaluated** by current simulator/scorer.
- **Preserve** full genome surface in serialization/identity; don’t strip genes “for speed.” Instead, **wire the minimum** that affects proxy EV: tree score → rank → entry_threshold → hold_sessions → costs; stops as phase-1.5 if cheap.
- Primary operator: `tree_crossover` + `structural_mutation` (already in `breed`). Remove or isolate flat `crossover`.
- Repeated multi-window same family: **keep** (ablation later).

---

## 5. Pareto, stagnation, restarts

- ε-archive cell idea is fine; EPS must be **recalibrated on empirical proxy metric scales**, not Claude’s asserted constants as universal truth.
- Improvement = new non-dominated ε-cell — OK.
- Stagnation: **prefer stop after patience with clear `stop_reason`** for fast budget. Optional `max_restarts≤2` re-seed population, **keep archive**, decrement budget. Indefinite reset **REJECT**.
- Store full genomes in archive (**QUICK WIN**).
- `breed` elite fraction + novelty attempts: OK for v0.
- Crowding + identity tie-break: deterministic; OK.

---

## 6. Leakage / universe / embargo

- Next-open + decision_at close semantics in simulator: directionally correct.
- Embargo fail-closed: correct; may zero-trade if schedules missing — treat zero-trade metrics as zeros, not successes.
- Features must be PIT / decision-time only — **contract on feature cache builder**, not inside `score_tree`.
- Survivor-only universe: disclosed; **forbid** marketing as deployable historical CAGR.
- Contaminated 2025–2026: config denylist for discovery evaluator windows — **QUICK WIN**.
- No sealed-blind touch: enforce by separate roots / date asserts — **QUICK WIN**, not full transport framework.

---

## 7. Discovery vs OOS vs sealed blind

| Lane | Allowed now | Code enforcement needed |
|---|---|---|
| Discovery walk-forward on declared train/purge windows | Yes | `evaluator_id` + `window_id` + hash of dates in metrics side-channel or summary JSON |
| Transport / stock-disjoint | After proxy works | DEFER CERTIFICATION |
| Sealed blind | No peek | DEFER; path deny-list |
| Portfolio CAGR in fitness | No | Keep out of `OBJECTIVES` |

Claude’s “evaluator must return date_range” is directionally right; implement as **lightweight metadata** in result JSON, not a heavy framework.

---

## 8. 1–40 session swing objective

- Gene `hold_sessions` ∈ [1,40] validated — OK.
- Fitness must **not** fix label horizon at 20 while gene varies (Claude’s IC sketch fails here). Proxy episodes should exit at `min(hold_sessions, 40)` or stop — **path-dependent genes need path metrics**.
- “Predicted horizon ≠ hold” — OK: don’t add separate horizon gene until proxy works.
- Report avg **and** max hold on portfolio evaluation — simulator history can support later.

---

## 9. Runtime efficiency / bounded CPU

**Fast experiment budget (proposed):**
- Panel: ~50–100 liquid survivors, ~2–4y daily bars, **precomputed feature cache** (parquet) for fixed windows {5,10,20,40,60,120,252} × families used.
- Pop: 32–64; generations: 50–100; patience: 25–40; workers: 2–4; **wall-clock target ≤ 1–3 hours** on existing hardware without starving GA6.
- Evaluator: vectorized numpy/pandas on cache; **no** per-genome full 503-name PIT download.
- Checkpoint every gen (already).
- Single `evaluator_id='exec_proxy_v1'`.

Reject concurrent full-scale + mass download.

---

## 10. Classification of all major proposals

### MUST BEFORE REAL DISCOVERY
1. Replace `diagnostic_evaluator` with **price-backed** evaluator; anything in archive labeled discovery must use it.  
2. If objective names stay `net_ev` / `ev_per_session`, compute them from **executable proxy** (next-open, costs, entry gate, hold/exit), **or rename** objectives to `proxy_net_pnl` etc. Never IC-as-EV.  
3. Feature cache + leakage contract: transforms fit on train folds only; score uses decision-time rows only.  
4. Wire `entry_threshold` + score → candidate set; define cross-sectional rank from tree margins (implement `rank_method` minimally).  
5. Zero-trade → explicit zero metrics (finite), not NaN; not “success.”  
6. Disclaimer flags: survivor-only; `evaluator_id`; non-certification.

### QUICK WIN (hours, not days)
1. Breed only via `tree_crossover`; quarantine flat crossover.  
2. Fix root `target == ()` donor selection.  
3. Archive stores full genome dict + id.  
4. Stagnation: stop-and-report (default); optional `max_restarts∈{0,1,2}`.  
5. `CONTAMINATED_PERIODS` deny-list assert in evaluator window builder.  
6. Guard `ungroup`; unit tests: validate_tree, crossover identity, embargo fail-closed, proxy finite metrics.  
7. EPS: set after measuring proxy metric MAD on smoke pop; don’t freeze Claude’s numbers as truth.  
8. Summary: log % zero-trade, mean episodes, mean hold used.  
9. Harden `nondominated` if empty next-front (defensive).

### DEFER CERTIFICATION
- Full stop/trail/replace parity in simulator vs genes.  
- Dividends/splits cash accounting + adjustment verification pipeline.  
- PIT membership / delist reconstitution.  
- Stock-disjoint transport, episode matrices, multiplicity-adjusted claims.  
- Lag gene, missing_policy gene, Sobol, sector neutralization richness.  
- Attribution A/B/C full matrix.  
- ≥35% CAGR as gate (report only).  
- Sealed blind / paper (G8).

### REJECT
- IC or top−bottom spread **named** as `net_ev`.  
- Indefinite stagnation resets.  
- Weeks of PIT before first proxy search.  
- Equating diagnostic run with discovery.  
- Simplifying away nested grammar “for speed.”  
- Touching GA6 production.  
- Claiming survivor-universe proxy CAGR as deployable EV.

---

## 11. Minimum viable scientific implementation (MVSI)

**Goal:** One bounded run that can honestly say: “under survivor panel P, proxy execution E, windows W, search found non-dominated chromosomes on **proxy** metrics,” with hashes — not certification.

### Components (reuse existing code)
1. **Freeze panel + cache** (offline, once): OHLCV, tradable flag, features keyed `(feature, window, transform)` per symbol/date; train-only scaler params per fold.  
2. **`exec_proxy_v1(genome)`** (new, ~100–150 LOC, not a second product):
   - For each decision date in discovery folds (purged gaps ≥ max hold): score all names via `score_tree`; build rank from margins/`rank_method`; apply `entry_threshold`.  
   - Paper-execute next open, `cost_bps=10` each side, size `target_weight` capped, `max_positions` small, exit at `hold_sessions` or simple stop if trivial to add.  
   - Metrics (all finite):  
     - `proxy_net_pnl` or honest `net_ev` **docstring = proxy**  
     - `ev_per_session` = pnl / session-in-market  
     - `reliability` = fraction of folds with pnl>0  
     - `training_consistency` = dispersion penalty or sign consistency of fold pnl (not IC-as-EV)  
     - `opportunity_coverage` = mean daily pass fraction  
   - Aux log only: Spearman IC — **not** in Pareto vector.  
3. **Engine:** existing `run()` with `evaluator=exec_proxy_v1`, smaller pop/gen, patience, workers.  
4. **Tests:** genome round-trip; proxy on constant prices → ~−costs; missing feature → no entry; embargo blocks buy.  
5. **Report template:** evaluator_id, data hash, seed, survivor disclaimer, stop_reason, archive genomes, **no** “CAGR fitness,” **no** blind claims.

### Prioritized fix order (same day → next)
1. Feature cache + `exec_proxy_v1` wired to `run()`  
2. Rank/entry wiring + zero-trade handling  
3. Archive genome payload + crossover foot-gun removal + root fix  
4. Contaminated window deny-list + summary fields  
5. Optional simple stop in proxy  
6. EPS smoke calibration  
7. Only then longer generations

### Explicit non-goals for MVSI
PIT delists, full GA6 portfolio parity, sealed evaluation, niche breeding, Sobol, lag gene, multi-day engineering of attribution lab.

---

## 12. Challenging the chromosome spec (v0.2)

- Strengths: frozen boundary (chromosome vs simulator), fail-closed embargo, 40-session hard cap, provenance intent, Pareto-not-CAGR, attribution A/B split.  
- Weaknesses: objective text still dangles “≥35% CAGR”; leaf lag/missing_policy not in code; “net rank quality/top-k excess” vs executable portfolio EV tension unresolved in implementation; acceptance gates G0–G8 are fine as **roadmap**, not day-0 scope.  
- Universe v0.2 survivor-only is honest — keep honesty in every artifact filename/README line.  
- DESIGN_v0_1 discovery fitness list is broader than `discovery_fitness.OBJECTIVES` — align names to avoid IC smuggling.

---

## 13. Challenging Claude (summary)

| Claude | Grok |
|---|---|
| IC-based real evaluator as MUST with IC→net_ev | MUST price-backed **proxy EV**, IC auxiliary only |
| Stagnation must reset | Bounded stop preferred; reset optional capped |
| Duplicate Pareto crash MUST | Speculative; quick harden |
| EPS fixed constants MUST | Calibrate empirically later |
| Date-range API MUST heavy | Lightweight window hash enough now |
| 5-step path | Right urgency; wrong fitness semantics on step 1 |
| Repeated-family OK | Agree |
| Flat crossover demote | Agree |
| Diagnostic toy | Agree — blocker |

## 14. Challenging ChatGPT (summary)

| ChatGPT | Grok |
|---|---|
| Executable net EV for named EV | Agree |
| Validate bugs with tests | Agree |
| Preserve grammar | Agree |
| Indefinite reset bad | Agree |
| IC not EV | Agree |
| Full path-dependent production simulator before any search | **Qualify** — MVSI proxy sufficient if labeled; full parity = certification |
| Duplicate-fitness claim needs repro | Agree |
| EPS not universal constants | Agree |

---

## 15. Bottom line

The stack is a **credible skeleton** (grammar, embargo fail-closed, ε-Pareto, checkpoints, next-open simulator primitives) with a **non-discovering heart** (`diagnostic_evaluator`) and **policy genes only partially coupled** to execution. Claude correctly flags the toy fitness and operator foot-guns but **corrupts fitness language** by promoting IC-as-EV and over-prescribes stagnation reset. ChatGPT’s EV semantics and efficiency constraints are the right scientific frame; pair them with a **small executable proxy + cache + bounded CPU**, not a certification platform build.

**Ship order:** proxy evaluator + cache → wire entry/rank/hold/costs → quick operator/archive fixes → one bounded run → read Pareto as **proxy discovery only** under survivor panel. Everything else is DEFER or REJECT until that run exists.

**Artifacts must say:** proxy metrics ≠ certified trade EV ≠ live CAGR.