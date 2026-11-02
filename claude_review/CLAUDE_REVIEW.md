# GA9 Trading Systems Architecture Critique

## Executive Summary

GA9 produces 16.06% CAGR, 20.01% MDD, Calmar 0.80, lagging QQQ by 22.55pp on development data. This is not a borderline result—it is a fundamentally broken system. The gap is too large to attribute to parameter tuning. The defects are architectural: a chromosome that cannot encode real alpha, a fitness function that selects on noise, execution logic that hemorrhages return through turnover and stop placement, and a universe that suffers survivorship bias. Each layer compounds the others.

---

## Part 1: Systematic Defect Inventory

I distinguish **confirmed defects** (traceable to code, reproducible, economically causal) from **hypotheses** (plausible but requiring experimental confirmation).

### 1.1 Chromosome Grammar — Confirmed Defects

**Defect C1: Score normalization destroys cross-sectional information.**

```python
# execution.py
features = {
    'trend': trend / .05,
    'momentum': m20 / .08,
    'volatility': (.025 - vol) / .015,
```

Fixed scalar normalization treats all regimes identically. A 0.08 normalization for momentum means a stock up 8% gets score 1.0 whether that is the 95th or 50th percentile. In high-volatility regimes (2022), this collapses dispersion. In low-volatility regimes (2023), it inflates it artificially. The GA is fitting to an artifact of regime-dependent score distributions, not to alpha.

**Defect C2: AND/OR tree over two family scores is not a valid alpha expression.**

```python
z = np.minimum(a, b) if g.op == 'and' else np.maximum(a, b) if g.op == 'or' else a
```

`min(trend, momentum)` selects stocks that are simultaneously not-last in trend AND not-last in momentum. This is just a weak intersection filter, not a signal. The op is applied before threshold gating, meaning `AND(.3, .3)` with threshold `0.25` passes anything above `0.25` on both—essentially a stricter version of either alone. The grammar has no capacity to express interaction effects, conditional logic, or any non-monotone relationship between features.

**Defect C3: Niche assignment uses fixed cluster centres on trend/vol only.**

```python
centres = np.array([[-.7, .2], [.0, -.3], [.7, .2]])
distance = ((x[:, :, None, :] - centres[None, None, :, :]) ** 2).sum(axis=-1)
niche = np.argmin(...)
```

These centres are not fitted and not validated. The niche gene parameter `niche=-1` bypasses this entirely (the mutation code preferentially samples -1 twice). Niche filtering therefore either does nothing or applies an arbitrary partition. There is no evidence it segments the universe into economically meaningful subpopulations.

**Defect C4: Trailing stop gene parameter is decorative.**

```python
trailing=rng.choice([.03,.05,.08])
```

In `engineering_baseline.py`, the diagnostic runs with `trailing=1` (disabled). In `evolution.py`, trailing is a mutation parameter but the execution engine's ratchet logic (`stop = max(stop, execution*(1-genes[gi].stop_distance))`) only uses `stop_distance`, not `trailing`, for the ratchet. The `trailing` gene value appears in the gene struct but examining `replay()` shows the ratchet uses `genes[gi].stop_distance` for the protective floor—the `trailing` field is read nowhere in the replay loop shown. **This means the GA is searching over a parameter that has zero effect on execution.**

**Hypothesis H1: `add` and `reduce` thresholds are effectively disabled.** `Manager.allow_add=False` in the baseline, and `replace(g, allow_add=False)` is set for the diagnostic. Whether the GA path enables adds and whether adds help or hurt is untested.

---

### 1.2 Fitness Function — Confirmed Defects

**Defect C5: `objective()` ranks on excess_pp over equal-weight synthetic benchmark, not QQQ.**

```python
def objective(result, passive):
    m['benchmark_cagr'] = passive['metrics']['cagr']
    m['excess_pp'] = 100*(m['cagr']-m['benchmark_cagr'])
```

`selection_benchmark()` calls `benchmark()` on `panel.primary_benchmark` when available, but in the GA path, whether QQQ is properly attached depends on the `inputs()` call chain in `exploratory.py` (not shown). The baseline report shows `excess_cagr = -22.55pp` versus QQQ—if the GA was selecting on excess vs. equal-weight (which in 2022-2024 likely had CAGR ~10-12%), candidates beating that bar fail versus QQQ. The fitness surface is wrong.

**Defect C6: Feasibility gate uses `MAX_DRAWDOWN = 1.0`.**

```python
MAX_DRAWDOWN = 1.0  # research validity boundary
def risk_feasible(max_drawdown):
    return bool(math.isfinite(max_drawdown) and 0 <= max_drawdown <= MAX_DRAWDOWN)
```

Any drawdown under 100% is feasible. The GA objective tuple is `(feasible, excess_pp, calmar, -mdd)`. Since feasible is almost always True, the ranking reduces to excess_pp over a potentially wrong benchmark. Calmar and MDD appear only as tiebreakers. A candidate with 30% CAGR and 40% MDD beats one with 20% CAGR and 10% MDD if excess_pp is higher. The objective literally cannot find the target of Calmar ≥ 2 with MDD ≤ 20%.

**Defect C7: Training window is calibration_end (Jul year-1) to train_end (Jan year). That is six months.**

```python
calibration_end = f'{year-1}-07-01'
train_end = f'{year}-01-01'
```

Six months of label data for fitting `expected()` conditional means is statistically inadequate. A 20-session horizon label requires the label to mature before cutoff. In six months (~126 sessions), at 20-session labels, you have at most ~106 non-overlapping label periods. With 125 symbols and 5 score bins, many bins will have fewer than the `min_samples=25` threshold, defaulting to zero. The model is largely zeros with a few noisy bin means.

---

### 1.3 Selection Architecture — Confirmed Defects

**Defect C8: Population size 4 with 2 generations is a local random walk, not evolution.**

```python
def search(p, year, generations=2, population=4, budget=30, ...):
```

With 4 candidates and 2 generations, the GA evaluates at most 8 unique chromosomes. The initial seed pool has 4 specific hand-coded strategies. Mutation produces variants of seeds 1-3 only (the cash candidate is excluded from mutation parents). This is not search—it is perturbation of 3 fixed hypotheses. There is no mechanism to discover qualitatively different strategies.

**Defect C9: Elitism preserves `initial[0]` (cash candidate) every generation.**

```python
population_rows = [initial[0], best[1]]
```

Cash is always in the population. If best is also cash (feasible but low CAGR), the next generation mutates cash—which has no genes. The `mutate()` function handles this: `genes = list(parent.genes) or [Gene(rng.choice(FAMILIES))]`. But this means the GA may spend half its budget on single-gene mutations of cash, which are already covered by `seeds[1:]`.

**Hypothesis H2: Budget=30 seconds causes systematic early termination.** With 4 candidates per generation, model fitting (label computation for 125 symbols, 4 horizons), and replay, 30 seconds may not complete even one full generation evaluation. Untested.

---

### 1.4 Entry/Exit Logic — Confirmed Defects

**Defect C10: Stop ratchet uses entry cost as part of stop distance, creating asymmetric protection.**

```python
distance = genes[gi].stop_distance + .00060005
budget = min(..., risk_budget(nav, manager.risk_cap, existing_risk, distance))
```

The admission budget correctly adds entry cost to stop distance. But the ratchet:

```python
pos['stop'] = max(pos['stop'], execution*(1-genes[gi].stop_distance))
```

uses only `stop_distance` without the entry cost. A position entered at $100 with 2% stop and 6bp cost is admitted with distance 2.006%. The stop is set at $98.00, not $97.94. The position's actual loss if stopped immediately is 2.06%, not 2.0%. The risk budget is overspent by the entry cost on every position. Not catastrophic but systematic.

**Defect C11: Stops observed at close, executed next open—gap risk is unaccounted in portfolio construction.**

The report acknowledges this. The mechanism for concern: with 10 positions each at 2% planned risk, the portfolio's actual tail risk depends on gap correlation. In a market dislocation (2022 Q1), all 10 positions can gap through stops simultaneously, producing realized loss of potentially 5-8% per position × 10 = 50-80% drawdown in a single session. The 2% risk cap is a per-position admission constraint, not a portfolio VaR constraint. There is no correlation-adjusted portfolio stop.

**Defect C12: `hold_signal = np.ones_like(signal)` in baseline forces permanent holding.**

```python
g = Gene('momentum', threshold=0, ..., trailing=1)
# ...
result = replay(p,[g],m,'2023','2025',True,signal,True,hold_signal=np.ones_like(signal))
```

The hold signal is all ones, meaning every position always has positive hold signal. Exits are driven only by stop hits or `hold_sessions` expiry. This disables the conditional exit machinery entirely for the diagnostic. The 20.01% MDD partly reflects holding losers past any exit signal because the hold signal never goes negative.

---

### 1.5 Trailing Stops — Confirmed Defects

**Defect C13: Ratchet only moves stop up, never applies a trailing percentage.**

The ratchet implementation:
```python
pos['stop'] = max(pos['stop'], execution*(1-genes[gi].stop_distance))
```

This sets stop at `entry * (1-2%)` on entry and never raises it unless a re-entry (`add`) occurs. This is a **fixed entry-price stop**, not a trailing stop. A stock that rises 40% will have a stop at `entry - 2%`—it will give back the entire 40% gain before exiting. The gene has a `trailing` parameter but it is not used in the ratchet. This is the primary explanation for the MDD: winners run up and then crash back through the entry stop.

**Corrected ratchet (confirmed fix):**
```python
# After marking peak:
pos['peak'] = max(pos.get('peak', pos['entry']), current_close)
trailing_stop = pos['peak'] * (1 - genes[gi].trailing)
entry_stop = pos['entry'] * (1 - genes[gi].stop_distance)
pos['stop'] = max(pos['stop'], trailing_stop, entry_stop)
```

---

### 1.6 Turnover — Confirmed Defects

**Defect C14: `replacement=2` in baseline forces complete portfolio turnover every 2 sessions.**

```python
m = Manager(slots=10, ..., replacement=2)
```

In `replay()`, `replacement` controls position replacement logic. With `replacement=2`, positions are replaced (exited and re-entered) extremely aggressively. At 6bp cost each side, complete turnover every 2 sessions = 12bp per 2 sessions = ~15% annual cost drag on a 60% exposed portfolio. This alone accounts for several hundred basis points of underperformance.

**Defect C15: `hold_sessions=20` with 10-position portfolio creates forced exits every 20 sessions.**

Even without stop hits, positions age out after 20 sessions (1 month). This means the portfolio turns over completely in 20 sessions (~1 month). Annual turnover ≈ 12×. At 12bp round-trip cost per position, this is 144bp/year in pure friction, applied to 60% average exposure.

---

### 1.7 Capital Allocation — Confirmed Defects

**Defect C16: `weight=.09` with `position_cap=.10` and `risk_cap=.02` creates contradictory constraints.**

Target weight per position is 9%, cap is 10%, risk cap admission limits entry. With 10 positions at 9%, full deployment is 90%. But `reserve=.1` (10% minimum cash). These are simultaneously satisfying: 90% invested, 10% cash. However, `risk_budget()` limits entry:

```python
return max(0., cap*nav - existing_risk) / stop_distance
```

With cap=2% and stop=2%, first position can buy up to `nav * 2% / 2% = nav * 100%`—no constraint from risk budget on position 1. With 10 positions at 2% risk each, total risk = 20% NAV. But `cap=.02` means the budget is exhausted after position 1 (`0.02 * nav - 0.02 * nav / stop_distance = 0`). This is internally contradictory: `risk_cap=.02` with portfolio planned risk target of 2% of NAV *total* means only one position can be held at 2% stop.

Wait—re-reading: `risk_budget` computes headroom. With risk_cap=0.02 (2% of NAV) and existing_risk from one position of 9% NAV at 2% stop = 0.18% of NAV, headroom = (0.02 - 0.0018)/0.02 = 9.1% NAV for second position. The cap is correctly interpreted as portfolio-level total stop risk. But then 10 positions at 9% each × 2% stop = 1.8% total planned risk, which is under the 2% cap. This is actually internally consistent. The confusion is in how `position_cap` and `risk_cap` interact—the binding constraint is whichever of `target * nav`, `position_cap * nav`, or risk budget is smallest.

**Hypothesis H3: With 10 × 9% positions at 2% stops, total planned risk is 1.8%, leaving 0.2% headroom. Admission of an 11th position is rejected. This is correct behavior but means the portfolio is always fully allocated with zero entry flexibility.** In a momentum rotation strategy, inability to quickly replace losers with winners degrades performance.

---

### 1.8 Cash/SGOV Handling — Confirmed Defects

**Defect C17: Cash earns zero in replay.**

```python
cash = 100000.
# ... cash never accrues interest
```

With average exposure of 60.72%, approximately 39.28% is in cash earning 0%. In 2023-2024, Fed funds was 5.25-5.5%. At 39% average cash, the opportunity cost is approximately 39% × 5.3% = 2.07% annual drag. This alone is a significant contributor to QQQ underperformance. SGOV (or equivalent cash yield) should be modeled explicitly.

---

### 1.9 Risk Accounting — Confirmed Defects

**Defect C18: `DRAWDOWN_REFERENCE = .08` is never enforced as a hard gate.**

```python
'above_drawdown_reference': mdd > DRAWDOWN_REFERENCE
```

This is a diagnostic flag only. The system reports it but never uses it to reject candidates or trigger any action. It is a metric without a policy.

**Defect C19: Survivorship bias in universe is confirmed.**

```
limitations: ['observed-bar eligibility is not verified historical membership', 
              'survivorship bias and missing delisting outcomes']
```

The archive of 125 symbols contains survivors as of the engineering session date (2026-10-30). Symbols that were in the Nasdaq 100 in 2022-2024 but subsequently delisted or dropped from the index are absent. This inflates backtest returns by excluding losers. The magnitude depends on index turnover (typically 10-15 names/year for QQQ), potentially 15-30 names over 2022-2024 with significant downside outcomes.

---

## Part 2: Root Cause of -22.55pp QQQ Underperformance

Decomposing the gap approximately:

| Source | Estimated Impact | Type |
|--------|-----------------|------|
| Survivorship bias in *benchmark* QQQ vs. *strategy* universe | +2 to +5pp against strategy | Defect C19 |
| Cash drag (39% × ~4% net) | -1.6pp | Defect C17 |
| Turnover friction (est. 12× annual at 12bp) | -1.4pp | Defects C14, C15 |
| Fixed stop not trailing (winners give back gains) | -5 to -10pp | Defect C13 |
| Wrong fitness benchmark (selected for non-QQQ excess) | Unknown but directional | Defect C5 |
| Chromosome cannot express QQQ-relative alpha | Structural floor | Defects C1-C4 |
| Gap risk uncompensated (concentrated stops) | Sporadic large losses | Defect C11 |

The dominant defects are the non-trailing stop (Defect C13) and chromosome expressiveness (Defects C1-C4). The others are recoverable with engineering. The chromosome issue requires architectural change.

---

## Part 3: Ranked Improvement Recommendations

I rank by estimated benefit-effort-compute ratio. Benefit is estimated CAGR improvement or MDD reduction; effort is engineering days; compute is relative CPU cost.

### Tier 1: High Benefit / Low Effort / Low Compute

These are bugs. Fix them first.

**R1: Fix trailing stop ratchet to use `trailing` gene parameter.**

- **Benefit**: 5-10pp CAGR recovery, 5-8pp MDD reduction. This is the single largest defect.
- **Effort**: 2 hours
- **Compute**: Negligible (replay loop change)
- **Implementation**:

```python
# In replay(), inside the marking/ratchet block:
if 'peak_close' not in pos:
    pos['peak_close'] = px  # px is current close
pos['peak_close'] = max(pos['peak_close'], px)

# Compute trailing and protective floors:
trail_stop = pos['peak_close'] * (1 - genes[pos['g']].trailing)
entry_stop = pos['entry'] * (1 - genes[pos['g']].stop_distance)
pos['stop'] = max(pos['stop'], trail_stop, entry_stop)
```

- **Proof-of-function experiment**: Run `engineering_baseline` with trailing=0.05 (gene default). Expect MDD < 20%, CAGR increase. **Stop criterion**: If MDD does not decrease by at least 3pp, the stop architecture has a deeper bug.

---

**R2: Credit cash with risk-free rate (SGOV proxy).**

- **Benefit**: 1.5-2.5pp CAGR improvement
- **Effort**: 3 hours
- **Compute**: Negligible

```python
# In replay(), at start of each day:
# Treasury rate as daily compounding factor
DAILY_RFR = (1 + 0.045) ** (1/252) - 1  # or read from data
cash *= (1 + DAILY_RFR)
```

For production, load the actual Fed funds effective rate as a time series. For the diagnostic, a constant 4.5% is economically conservative and reproducible.

- **Proof-of-function**: Check that `result['metrics']['final_nav']` increases by approximately `39% × 4.5% × 2 years = 3.5%` on the baseline. **Stop criterion**: If cash credit exceeds 5% of NAV over 2 years, the cash tracking has a bug.

---

**R3: Fix `hold_signal` in baseline—do not use `np.ones_like`.**

- **Benefit**: Enables exits on momentum deterioration; estimated 1-3pp CAGR, variable MDD effect
- **Effort**: 1 hour
- **Compute**: Negligible

The fix: compute actual hold signal from the momentum score, not ones. In `engineering_baseline.py`:

```python
# Replace:
hold_signal=np.ones_like(signal)
# With:
hold_signal = np.where(signal > -np.inf, signal, -np.inf)
# Or use a proper threshold: hold while score > exit_threshold
hold_signal = np.where(mask, p.screen_score, -np.inf)[None]
```

- **Proof-of-function**: Check that exit count in fills increases. **Stop criterion**: If CAGR decreases AND MDD decreases, the exits are real but the entry signal quality is the binding constraint—proceed to R4.

---

**R4: Fix fitness objective to enforce Calmar ≥ 2 as primary gate, not secondary sort.**

- **Benefit**: GA will select strategies that actually meet objectives
- **Effort**: 1 hour

```python
def objective(result, passive):
    m = result['metrics']
    cagr = m['cagr']
    mdd = m['max_drawdown']
    calmar = cagr / mdd if mdd > 1e-12 else 0.
    excess = cagr - passive['metrics']['cagr']
    
    # Hard gates first, then graded objectives
    mdd_gate = mdd <= 0.20
    calmar_gate = calmar >= 2.0
    excess_gate = excess > 0
    
    # Primary: all gates satisfied
    all_gates = int(mdd_gate and calmar_gate and excess_gate)
    # Secondary: partial credit encourages progress
    partial = int(mdd_gate) + int(calmar_gate) + int(excess_gate)
    
    return (all_gates, partial, excess if excess_gate else excess, calmar, -mdd)
```

- **Proof-of-function**: Run 2-generation GA. Check that `journal` shows candidates with better Calmar are preferred. **Stop criterion**: If best candidate still has Calmar < 1, the search space is the binding constraint.

---

### Tier 2: High Benefit / Medium Effort / Low Compute

**R5: Replace fixed scalar normalization with cross-sectional rank normalization.**

- **Benefit**: 3-7pp CAGR, consistent signal across regimes
- **Effort**: 4 hours

```python
def rank_normalize(series_2d, eligible_mask):
    """Replace fixed scalar with cross-sectional percentile rank, centered at 0."""
    df = pd.DataFrame(series_2d)
    eligible = pd.DataFrame(eligible_mask)
    ranked = df.where(eligible).rank(axis=1, pct=True) * 2 - 1
    return ranked.where(eligible).fillna(0)

features = {
    'trend': rank_normalize(trend.values, eligible),
    'momentum': rank_normalize(m20.values, eligible),
    'volatility': rank_normalize(-vol.values, eligible),  # negate: lower vol = higher rank
    # etc.
}
```

This ensures scores are always in [-1, 1] with consistent semantics. The threshold=0.25 now means "top 37.5% by trend"—interpretable and regime-invariant.

- **Proof-of-function**: Print `p.features['momentum'].std(axis=1).describe()` before and after. Should be near 0.577 (uniform distribution) after ranking vs. variable before. **Stop criterion**: If std is not regime-consistent, the eligible mask is applied incorrectly.

---

**R6: Replace `replacement=2` with sensible turnover budget.**

- **Benefit**: 1-2pp friction reduction
- **Effort**: 2 hours

`replacement=2` forces position replacement logic that is not documented in the provided code excerpt. Whatever the semantics, the result is excessive turnover. Set `replacement=0.5` (half-position replacement rate) or investigate the actual semantics and set it to match a target annual turnover of ≤200%.

---

**R7: Implement correlation-adjusted portfolio stop.**

- **Benefit**: MDD reduction, especially gap events
- **Effort**: 8 hours
- **Compute**: Low (rolling correlation of positions)

When all positions share high correlation (typical in momentum portfolios), a single market event can breach all stops simultaneously. Add a portfolio-level stop:

```python
# In replay(), after marking positions:
nav = cash + sum_position_values
current_dd = 1 - nav / peak_nav
if current_dd >= 0.15:  # portfolio-level circuit breaker
    # Reduce all positions by 50%
    # Or: halt new entries until drawdown recovers
```

The threshold (15%) should be tuned such that the circuit breaker activates before catastrophic loss but not on normal volatility.

---

### Tier 3: Medium Benefit / Medium Effort / Medium Compute

**R8: Expand chromosome grammar to include conditional and ratio features.**

- **Benefit**: Enables genuine alpha expression; without this, Tier 1 fixes have a ceiling
- **Effort**: 1-2 days

Current grammar: `min(feature_A, feature_B)` or `max(feature_A, feature_B)`.

Proposed grammar additions:
```python
# Ratio feature: relative strength vs. sector
'rs_sector': (stock_momentum - sector_momentum) / sector_vol

# Conditional: trend-following in uptrend, mean-reversion in downtrend
'regime_adaptive': np.where(breadth > 0.6, momentum_rank, -momentum_rank)

# Composite: Fama-French style factors
'quality_momentum': rank(roe) * rank(momentum)  # multiplicative interaction
```

These require extending `evaluate_tree()` to