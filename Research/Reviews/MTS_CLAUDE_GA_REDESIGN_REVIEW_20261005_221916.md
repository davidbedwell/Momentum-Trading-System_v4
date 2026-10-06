# MTS GA Redesign: Independent Review and Implementation Instruction Set

**Reviewer role:** independent senior quantitative-research architect
**Governing authority:** the packet's frozen specification (Section 1) and governance override (Section 8)
**Sealed-evidence status:** DV25, A25, A75 and B100 are untouched, unread and not recommended for opening. Nothing below requires or implies access to them.

---

## 0. Executive Verdict

1. **The executed runner materially changed the research question.** The approved question was whether a hierarchical, state-conditioned, horizon-free capital-competition system (market → sector → stock → strategy → ranking → allocation, with SAFE competing) can reach a desirable CAGR/MDD frontier. The executed question was whether one global sparse linear score, converted to a daily cross-sectional rank and quantile-thresholded, can do so. The DEV117 result is a valid negative result for that second question only. It is **not** a test of the approved architecture.

2. **The most consequential defect is probably structural, not parametric.**
   - Each day, every market/R1 feature has the same value for every stock.
   - In a linear score, such a feature adds the same constant to every stock's score on that date.
   - Cross-sectional ranking is invariant to adding a per-date constant.
   - Therefore all 20 market/R1 inputs were very likely mathematically inert for selection.
   - Thresholding a rank also fixes the qualifying fraction of the universe every day, so exposure cannot depend on market state.

   This one mechanism plausibly explains three observations together: near-zero SAFE usage, no crash-defense behavior, and the absence of any candidate at ≤10% MDD. It must be confirmed by test (K, PF-02/PF-03), but it is the leading hypothesis.

3. **There is a probable metric or degeneracy bug.**
   - 0.0001988 ≈ 1/5,030, which is about the number of sessions in 20 years.
   - Training turnover and SAFE fraction share that exact value.
   - That pattern indicates either (a) both metrics count only the initial session, or (b) training genomes bought a basket on day one and never traded.
   - If (b), training fitness rewarded a day-one static basket. The GA could tune weights so the first-day ranking picks training stocks that later did well. That is a hindsight ticker-identity proxy.
   - Neither interpretation may be left unresolved.

4. **The blind diagnostics show no selection skill.**
   - Selected-minus-unselected next-session returns were negative for every candidate below the ~40% DD band.
   - For the ~20% candidate, blind CAGR (8.85%) exceeded training CAGR (4.95%).
   - Together these indicate the positive blind CAGR came mostly from equity drift and exposure in the blind partition, not from the evolved logic.

5. **DV25 must remain sealed.** Nothing here supports opening it.

6. **A further limitation must be stated plainly.**
   - All DEV117 folds, DV25 and A25 share one 2006–2026 market path.
   - Cross-stock transport validates stock-selection generalization.
   - It does **not** independently validate market-timing or crash-defense logic, which is effectively in-sample on a handful of episodes in every partition.
   - The redesign must account for crash-defense evidence by episode count, not session count, and must not present stock-split blindness as temporal validation.

### Question-to-Section Map

| Q | Topic | Answered in |
|---|---|---|
| 1 | Research question altered? | 0, A.1 |
| 2–3 | Alpha/crash suppressors; harmless vs consequential | A.2, A.4 |
| 4 | Linear rank chromosome too weak? | A.2 (D1), C.1 |
| 5–6 | First-class modules; non-Cartesian conditional search | C, H |
| 7 | Horizon-free lifecycle | E |
| 8 | SAFE competition | B.7, E, F |
| 9–10 | Soft layers; discoverable R1 | B, C.3, D |
| 11–12 | Objective design; Pareto vs guards vs diagnostics | G |
| 13 | Costs in evolution vs finalists | G.4, J |
| 14 | Effective independent evidence | G.6 |
| 15 | Fold use without leakage | I |
| 16–17 | Pre-DV25 freeze; DV25 burn criteria | I.6, L |
| 18 | Preflight tests | K |

---

## A. Root-Cause Assessment

### A.1 Did the runner alter the research question?

Yes, materially. The approved hypothesis space contained:
- conditional, state-dependent strategy applicability;
- sector context;
- absolute (time-varying) opportunity levels;
- SAFE as an economic competitor;
- four allocation modes.

The executed hypothesis space was a strict, much smaller subset:
- one unconditional linear cross-sectional ranker;
- rank-quantile qualification;
- three allocation modes.

It also had a likely defect that removed market/R1 information entirely from selection. Nearly every approved scientific mechanism for crash preservation (state-dependent exposure, SAFE competition, regime-conditioned strategies, sector rotation) was either absent or structurally disabled.

### A.2 Discrepancies, ranked by expected scientific consequence

| ID | Discrepancy | Category | Rank | Why it matters |
|---|---|---|---|---|
| D1 | Global linear score converted to a per-date cross-sectional rank. Market/R1 features add a per-date constant and vanish under ranking. Rank-quantile qualification fixes the qualifying count. | Implementation (design-translation) defect | **CRITICAL** | Removes all regime information from selection. Makes exposure state-independent. Disables R1 discovery and crash defense. Probable cause of SAFE ≈ 0 and the empty ≤10% band. 20 of 28 inputs were likely dead genome capacity. |
| D2 | No sector layer: no sector genes, no sector features, no stock-vs-sector features. | Implementation omission | **CRITICAL** | Sector rotation, sector-relative strength, sector stress and sector leadership are unrepresentable. A frozen layer is absent. |
| D3 | No strategy-family modules, applicability logic or conditional structure. | Implementation omission | **CRITICAL** | Cannot express "family X under state A, family Y under state B." The approved discovery architecture became a single unconditional model. |
| D4 | SAFE not a genuine competitor: rank units have no absolute level, and the qualifying fraction is fixed. | Consequence of D1 plus scoring design | **CRITICAL** | Structural bias toward continuous investment. Observed SAFE fraction ≈ 1/T, which is an initialization artifact, not a decision. |
| D5 | Training turnover = SAFE fraction ≈ 1/5,030. Training turnover ≪ blind turnover (0.03–0.07). | Probable bug or degeneracy | **CRITICAL until resolved** | Either the metrics are wrong, or training fitness rewarded a hindsight day-one basket. Either way, no training metric can be trusted until this is resolved. |
| D6 | Stock features are cross-sectional ranks only; no time-series or absolute state. | Implementation reduction | **HIGH** | Ranks average 0.5 every day, so conviction cannot vary over time. Combined with D1, the model cannot decide how much to own, only which names. |
| D7 | `spy = np.nanmean(ret, axis=1)` labeled as SPY. | Reporting defect | **HIGH** | Decline reporting, benchmark comparisons and decline-episode definitions are invalid. If `ret` spans DEV117, the "comparator" also mixes the training and blind partitions. |
| D8 | Flat 5 bps hard-coded. No 0/5/10/20 sensitivity, no regulatory fees, no borrow. | Implementation omission | **HIGH** | Required finalist analysis is missing. Shorts were unpriced. With training turnover ≈ 0, cost pressure never shaped evolution. |
| D9 | Shorts as a Boolean plus inverse rank below a threshold. | Implementation reduction | **MEDIUM-HIGH** | When enabled, there is an always-on short book with no state-conditioned applicability and no borrow economics. Drawdown control came from a quasi-hedged book, not from discovered defense. |
| D10 | Finalists shown as a blind frontier, implying candidate choice by blind band. | Governance/process defect | **MEDIUM-HIGH** | Choosing among genomes by blind result turns blind37 into a selection set. All displayed blind numbers are optimistically biased. |
| D11 | Provenance of market-level features (mret, mdd, breadth) unverified. | Unknown, potential leakage | **MEDIUM-HIGH** | If computed from the DEV117 matrix, blind-partition prices entered training features. If computed from a broader universe, sealed tickers may have been read. Must be audited. |
| D12 | "Equal" allocation omitted. | Specification violation | **MEDIUM** | Removes a robust baseline mode. The governance breach exists regardless of scientific consequence. |
| D13 | 8–12 features treated as a permanent ceiling. | Implementation reduction | **MEDIUM** | The spec says initial size, not limit. The ceiling was compounded by inert features consuming slots. |
| D14 | Required diagnostics unverified (CVaR5, drawdown velocity, worst 5/10/20-session loss, time to recovery, effective N, era/fold stability, full decline table). | Unknown | **MEDIUM** | A 313-line runner cannot plausibly implement all of these to definition. Treat as missing until tested. |
| D15 | Search budget (~32k unique evaluations per fold, 200 generations). | Engineering | **LOW** | Adequate for the reduced genome. Not a root cause, and more compute on D1–D4 would not fix anything. |
| D16 | Causal percentile transforms of market features; shifted and forward-filled OFR series; predetermined folds; DV25 untouched. | Correct engineering | **LOW (retain)** | These were done correctly and should be kept. |

### A.3 Likely bugs that must be repaired or root-caused before redesign results are trusted

**BUG-1 (D5), turnover/SAFE identity.** Test each hypothesis by dumping the daily weight matrix for the training path of each displayed finalist:
- **H1, metric artifact.** Turnover or SAFE fraction is computed on the wrong array or axis, or only the initial allocation is counted.
- **H2, degenerate static basket.** The evolved replace margin was unreachable in training, so the genome bought at the first eligible session and never traded. One full entry (turnover 1.0) divided by about 5,030 sessions gives 1/T. SAFE was held only on session 0, also 1/T. This fits the numbers exactly.
- **H3, code-path divergence.** Training and blind metrics are produced by different functions or cached states.

The required test: run the same genome on the same universe through both the training and blind code paths. Metrics must be identical. Count the sessions with non-zero turnover. If H2 is confirmed, reclassify the training results as hindsight-basket fitting. The redesign must then include start-date-jitter robustness (G.3, guard G7).

**BUG-2 (D1), rank cancellation.** Perturb any market feature by +k on all stocks for a date. Confirm whether weights change. Under the described mechanics they will not.

**BUG-3 (D7), comparator alias.** Rename the variable, load actual SPY, and confirm the equal-weight series was never used in any feature, decline-episode definition, or fitness term.

**BUG-4 (D11), market-feature provenance.** Trace the source universe for breadth20, breadth200, mret5/20 and mdd. Certify that they read no sealed tickers and no blind-partition prices during training.

### A.4 Research-design defects vs implementation defects vs disappointing results

**Implementation defects:** D1–D14. These alone invalidate the run as a test of the approved architecture.

**Specification gaps in the approved design.** These are not errors, but they left room for silent substitution. Each must be resolved explicitly and frozen with user approval, never filled in silently by an implementer:

| Gap | Issue | Proposal (requires user ratification) |
|---|---|---|
| S-1 | No numeric economic target for "acceptable." | L.2 floors |
| S-2 | Units in which SAFE competes are undefined. | Excess-return numeraire (B.7) |
| S-3 | Friction is one-time but opportunity is a rate; how to compare without a horizon. | Friction exchange coefficient κ (E.4) |
| S-4 | Market-feature source universe. | External market data or a certified disjoint universe (D.3) |
| S-5 | Finalist-selection rule and DV25 candidate set. | I.4, I.6 |
| S-6 | Execution timing. | Decide on close T, execute at T+1 open (J.5) |
| S-7 | Short collateral and rebate treatment. | No rebate baseline (J.4) |
| S-8 | Point-in-time sector taxonomy. | D.2 |
| S-9 | Data availability (earnings, VVIX before 2007, later-launched sector ETFs). | D.5 |
| S-10 | DEV117 survivorship and selection method. | J.6 |
| S-11 | Meaning of the "0/5/10/20 bps one-way" levels. | Total one-way spread+slippage levels, plus a realistic liquidity model column (J.3) |
| S-12 | Guard thresholds. | G.3 |

**Inherent research-design limitation (S-13).**
- All partitions share one market path.
- R1 composites were developed from prior studies of the same 2008–2009/2020 episodes, so they carry hindsight about those episodes.
- Stock-split validation cannot test this.
- Mitigations: provide primitive constituents separately; document composite provenance; use episode-level evidence accounting and leave-one-episode-out diagnostics; state that only forward time can validate market-timing logic.

**Disappointing results.**
- The frontier (8.85% at −19.86% MDD up to 16.55% at −39.63%) is a genuine negative result for the reduced runner.
- It is economically unacceptable and fails the proposed L criteria at every band.
- It must not be used to calibrate the new thresholds, and it is not evidence against the approved architecture, which was never run.

### A.5 OmniFunds comparison: what it does and does not imply

**Arithmetic checks.**
- The Market Leaders figures are internally consistent: 1.708 × 1.090 ≈ 1.862, i.e. +86.2% YTD.
- But ~82% of the YTD log-return is pre-release backtest.
- The live evidence is about 5 weeks (~24 sessions) with a 3.9% MDD. That is statistically negligible and says nothing about crash behavior.

**The "10–11% per month" claim (unverified).**
- It implies 1.10¹² − 1 ≈ **+214%/yr** to 1.11¹² − 1 ≈ **+250%/yr**.
- Over 20 years that compounds to roughly 10¹⁰ times starting capital.
- That is not plausible as a durable, capacity-bearing, cost-inclusive result. It could at most describe a short window or a backtest.
- A fair comparison would require all of the following:
  - audited daily NAV;
  - the exact release date and frozen-rule hash;
  - a separate live record;
  - point-in-time universe membership;
  - fill-level costs;
  - complete drawdown history;
  - identical measurement windows.

**Model 2** is the GA-relevant comparison, but:
- "+40% since release" has no stated release date and cannot be annualized.
- Its demonstration uses a **five-day fixed exit**, which is a forbidden mechanism in MTS. It cannot be imported.

**Legitimate architectural questions raised (as hypotheses, not imports):**
1. Concentration in leaders: MTS already permits it, but the reduced runner's quantile spread likely diluted conviction.
2. A state-dependent move toward cash: in MTS this must emerge through SAFE competition, not a hard-coded brake.
3. Sector leadership: requires the missing sector layer.
4. Concentration tail risk: the reported ~95% semiconductor exposure followed by a ~14% one-day giveback shows MTS must measure sector concentration and worst-day loss.

**What OmniFunds does not license:**
- changing MTS universes;
- adopting fixed holds;
- setting MTS thresholds from OmniFunds figures;
- inferring that similar performance exists in DEV117.

There is also a universe-selection coincidence to note: an "AI leaders" NASDAQ-100 strategy, named and released in 2026, evaluated on 2026 YTD.

---

## B. Research Architecture

All layers are **soft information levels**. No layer may veto, force, or cap any action. Each produces measurements or graded context values that downstream evolved logic may use, ignore, or combine.

### B.1 Market layer
- **Inputs:** market-level causal measurements (D.3), including each of the seven R1 dimensions as separate primitives plus temporal derivatives.
- **Output:** a vector m(T) of raw market features plus 0..M evolved context units (C.3). Each context unit is a soft membership value in [0,1].
- **Role:** may modulate strategy applicability, the opportunity level, risk appetite τ, the friction coefficient κ, and short applicability. It never prescribes long, short or SAFE.
- **Constraint:** market quantities must reach decisions through paths that are not cancelled by cross-sectional normalization. Specifically: absolute opportunity levels, risk appetite, and the SAFE hurdle.

### B.2 Sector layer
- **Inputs:** a point-in-time sector map and sector-level measurements (D.2).
- **Output:** a per-sector vector s_g(T) plus 0..S evolved sector context units.
- **Role:** informs the opportunity, uncertainty and downside of member stocks, and may enable sector rotation through sector-relative signals. It never limits sector count or weight.
- **Constraint:** the sector label is a grouping key, not a predictive one-hot input. With ~80 stocks, a one-hot sector label can act as near-identity.

### B.3 Stock layer
- **Inputs:** per-stock causal state x_i(T), in both cross-sectional and time-series normalized forms (D.1, D.4), plus stock-vs-sector and stock-vs-market relative features.
- **Constraint:** no ticker identity, and no entry-anchored or position-age state.

### B.4 Strategy/applicability layer
- **Structure:** 1..N evolved strategy modules (C.2). Each module has:
  - an **applicability gate** a_ik ∈ [0,1], a function of (m, s_g(i), x_i);
  - a **signed signal** z_ik;
  - **uncertainty** u_ik ≥ 0;
  - **downside** d_ik ≥ 0.
- **Families:** strategy families seed the initial population and label niches. They are not cages. Modules may mix primitives across families.

### B.5 Opportunity-ranking layer
- **Aggregation:** module opinions are aggregated (evolved aggregator) into an absolute opportunity O_i(T).
- **Mapping:** O_i is mapped to an estimated incremental excess return per session over SAFE, E_i(T) (C.2, OpportunityMap).
- **Ranking:** a reporting and ordering convenience only. Qualification is never rank-quantile based.

### B.6 Portfolio/allocation layer
- **Target weights:** derived from claims built from value-adjusted opportunity under one of the four approved modes (equal, strength, uncertainty-adjusted, downside-adjusted).
- **Risk appetite:** scaled by an evolved state-dependent risk appetite τ.
- **Gross exposure:** capped at Σ|w| ≤ 1. The residual goes to SAFE.

### B.7 Incumbent/challenger/SAFE competition
- **Numeraire:** SAFE is the numeraire, with value 0, cost 0 and uncertainty 0.
- **Common units:** every risky position, held or candidate, is valued in the same units as excess return over SAFE, net of carrying costs.
- **Capital movement:** capital moves between any two assets, including SAFE, only when the value difference exceeds friction and uncertainty (E.4).

### B.8 Long/short behavior
- Long and short are both outputs of the same valuation.
- Shorts require a negative expected excess return large enough to overcome borrow, forgone SAFE yield on encumbered equity, and friction (E.5).
- Short permission and short applicability are evolved and state-conditionable.

### B.9 No leverage, no options
- Σ_i |w_i| ≤ 1 at all times. Short notional consumes equity one-for-one.
- No derivatives.

---

## C. Genetic Representation

### C.1 Design principles
1. **Typed, modular, grammar-constrained genome.** A strict superset of the reduced runner: a linear ranker is expressible as a one-module, ungated special case (nesting test PF-26).
2. **Soft conditionality.** Implemented by gates and soft-if operators, not by enumerating a Cartesian product of regimes × families × sectors.
3. **Growable complexity.** NEAT-style innovation IDs, speciation protection, insertion/deletion operators.
4. **Engineering bounds are generous and monitored.** If they bind, execution stops and requests approval. Bounds are never a silent hypothesis restriction.

### C.2 Chromosome structure (schema `MTS-GA-G2`)

```
Genome := {
  schema_version,
  genome_innovation_ids,
  MarketContexts : [CtxUnit<Market>]  (0..M_max, engineering bound default 12)
  SectorContexts : [CtxUnit<Sector>]  (0..S_max, default 8)
  StockStates    : [StateUnit<Stock>] (0..K_max, default 12)   # reusable derived stock states
  Modules        : [StrategyModule]   (1..N_max, default 16)
  Aggregator     : AggGene
  OpportunityMap : OppMapGene
  Lifecycle      : LifecycleGene
  Allocation     : AllocGene
  ShortPolicy    : ShortGene
}

CtxUnit<T> := { innov_id, expr: Expr<T-Scalar>, squash ∈ {sigmoid(a,b), tanh01, causal_ts_pct} } → [0,1]
StateUnit<Stock> := { innov_id, expr: Expr<Stock-Scalar> } → ℝ

StrategyModule := {
  innov_id,
  family_tag ∈ FamilyLibrary,                       # descriptive + niche label, not a constraint
  applicability : Expr<Gate>  → [0,1]               # may reference Market, Sector, Stock scalars, ctx units
  signal        : Expr<Stock-Scalar> → ℝ (signed)   # MUST contain ≥1 stock-varying leaf
  side_mode     ∈ {long_only, short_only, both}
  weight        w_k ≥ 0
  uncertainty   : Expr<Stock-Scalar≥0> | family default estimator
  downside      : Expr<Stock-Scalar≥0> | family default estimator
}

AggGene := { mode ∈ {appl_weighted_sum, appl_weighted_mean, softmax(temp), max_confidence}, params }

OppMapGene := {
  mode ∈ { affine: E = α(ctx)·O + β(ctx)                # α, β are Expr<Market> (α ≥ 0)
         , causal_calibrated: E = Cal_T(O)                # online map fit on (O, realized next-session excess)
                                                          # pairs from the CURRENT tradable universe, data ≤ T−1,
                                                          # method ∈ {linear, monotone_binned}, halflife h ∈ registry }
}

LifecycleGene := { κ: Expr<Market|Stock-uncertainty> ≥ 0,   # friction exchange coefficient (E.4)
                   λ_u ≥ 0,                                  # uncertainty margin coefficient
                   q: Expr<Market> (qualification margin in E units, may be ≤ 0 or > 0) }

AllocGene := { mode ∈ {equal, strength, uncertainty, downside},   # all four MUST be reachable
               τ: Expr<Market[, Portfolio*]> ≥ 0,                  # risk appetite (Portfolio* only if E1 approved)
               γ ∈ [0.5, 4]   (sharpness; ignored for equal),
               η ∈ (0,1]      (equal-mode unit claim) }

ShortGene := { enabled: bool, applicability: Expr<Gate>, extra_hurdle ≥ 0 }
```

**Expression grammar (typed).** Types are `Market-Scalar` (identical across stocks at T), `Sector-Scalar`, `Stock-Scalar` and `Gate` ([0,1]). Promotion rule: Market → Sector → Stock by broadcast. No demotion except through registered aggregations (sector mean, market mean), which must be causal and universe-certified.

| Category | Operators |
|---|---|
| Leaves | `Feature(f, transform)` from the feature registry. Transforms: `raw`, `ts_pct` (causal expanding/rolling percentile), `xs_pct` (cross-sectional within the current tradable universe), `zscore_ts`, `vol_scaled`. Also `Const(c)` and `CtxRef(id)`. |
| Temporal (lookbacks k from registry {1,2,3,5,10,20,40,60,120,252}) | `Delta(e,k)`, `Accel(e,k)`, `Persist(gate,k)` (fraction of last k sessions the gate exceeded 0.5), `RollMax/RollMin(e,k)`, `EMA(e,k)`, `Lag(e,k≥1)` |
| Arithmetic | `Add`, `Sub`, `Mul`, `SafeDiv`, `Neg`, `Abs`, `Min`, `Max`, `Clip` |
| Soft logic | `SoftThresh(e,θ,s)=σ((e−θ)/s)`, `AND`=product, `OR`=probabilistic sum, `NOT`=1−g |
| Soft conditional | `IfSoft(g,a,b) = g·a + (1−g)·b` |

Lookbacks are measurement windows on data, never holding periods.

**Active concept count.** This is the number of distinct feature leaves + modules + context units + state units. Initialization samples 8–12 active concepts. Growth is unrestricted up to the engineering bounds.

### C.3 How conditional relationships are represented
- **Regime-conditioned strategy:** a module whose applicability depends on market context units, e.g. `AND(Ctx_breadth_conversion, NOT(Ctx_stress))`.
- **Sector-conditioned behavior:** applicability or signal referencing sector scalars, e.g. sector relative strength or sector stress.
- **Interactions:** `Mul`, `IfSoft` and gated aggregation provide market × sector × stock interactions without enumeration.
- **R1 morphology:** each R1 dimension is a separate leaf. The GA may build persistence (`Persist`), velocity/acceleration (`Delta`/`Accel`) and soft conjunctions in any order. No R1 ordering or action is pre-wired.

### C.4 Strategy family library (seeds and niche labels)

Each family supplies 2–6 seed templates built from registry primitives. All templates are fully mutable after initialization.

| Family | Seed signal primitives |
|---|---|
| momentum | ts and xs ret20/60/120/252, residual momentum |
| breakout | distance to 52w/N-day high, channel break |
| trend | MA gap/slope geometry |
| mean reversion | price z vs MA, rsi14 |
| volatility | realized vol level/change, compression |
| volume/liquidity | relvol, dollar volume, Amihud |
| relative strength | vs market, vs sector |
| earnings | point-in-time event/surprise features; subject to data gate D.5 |
| regime structure | market-level ctx × stock beta |
| reversal | ret1–ret5 short-term reversal |
| pullback | pullback-within-uptrend composites |
| volatility breakout | range expansion after compression |
| composite breadth | breadth-conditioned beta/quality |
| sector-relative | stock-vs-sector residual |
| discovered | random grammar-generated |

The initial population must give every family at least 1/(2·n_families) representation.

### C.5 Mutation operators (adaptive rates, all reachable at all stages)
1. Constant perturbation: Gaussian with self-adaptive σ.
2. Leaf swap within type: feature, transform or lookback.
3. Operator swap within arity and type.
4. Subtree insert, delete or replace (type-safe).
5. Wrap/unwrap in `IfSoft`, `SoftThresh` or temporal operators.
6. Module add (from the family library or random), delete, or duplicate-and-mutate.
7. Applicability add/remove of a context reference.
8. Context-unit add, delete or rewire.
9. Policy-gene mutation: allocation mode (uniform over all four), OpportunityMap mode, κ/λ_u/q/τ expressions, γ, η.
10. Short-gene toggle and short-applicability mutation.
11. Simplification mutation: prune subtrees with negligible effect on the training probe set.

### C.6 Crossover operators
1. **Module-homologous crossover.** Align modules by innovation ID, exchange them, and inherit unmatched modules from either parent.
2. **Type-safe subtree crossover** within corresponding expression slots.
3. **Context-unit exchange**, re-binding references by innovation ID.
4. **Whole-layer swap:** Lifecycle, Allocation or ShortPolicy taken from the other parent.
5. **Uniform crossover** on scalar policy constants.

### C.7 Complexity growth and shrinkage
- Growth comes from insertion operators and module addition. Shrinkage comes from deletion, pruning and simplification.
- Speciation (compatibility distance on innovation sets plus structure) protects new structures for a few generations.
- Complexity enters selection **only** as a tie-breaker when candidates are within ε-dominance, where ε is the bootstrap standard error (G.5).
- **Bound-saturation monitor.** If more than 10% of any band's elite archive touches any engineering bound for 20 consecutive generations, execution STOPS and requests approval to raise the bound.

### C.8 Invalid-structure rejection (cheap checks before full simulation, reasons logged)
1. Schema and type check.
2. Forbidden-symbol check: ticker IDs, position age, entry date or entry price, hold counters, cooldowns, future-return horizons, slot or sector caps.
3. Causality check: every leaf's publication lag ≥ its registry lag; `Lag` k ≥ 1 where required.
4. Engineering bounds.
5. Probe evaluation on a fixed training-only probe calendar: finite outputs, and module signals not cross-sectionally constant on more than 95% of probe dates.
6. Feasibility: weights finite and gross ≤ 1 after scaling.

### C.9 Semantic duplicate caching
- **Exact cache:** canonicalize (sort commutative arguments, constant-fold, drop zero-weight terms and identity wrappers, quantize constants to a registered precision) → SHA-256 canonical hash → reuse fitness.
- **Behavioral fingerprint:** hash of the quantized target-weight matrix on the training probe calendar, which must include every major decline/recovery episode. Matches are near-duplicates: they count for niche crowding but do **not** skip evaluation unless the canonical hashes match.
- **Post-evaluation:** full-period weight-path hash for archive deduplication.

### C.10 No ticker identity
- Tickers never enter the genome, the feature tensors, or any hashable decision input.
- Stock columns are referenced by anonymous indices that are permuted per evaluation (PF-22).

---

## D. Feature Substrate

All features are **derived measurements**: deterministic functions of data published at or before T, with no action semantics. **Trading rules** (anything mapping state to positions) exist only inside evolved genomes.

Every feature must have a registry entry with:
- name;
- source;
- universe;
- inputs;
- lookback;
- publication lag;
- normalization;
- first valid date;
- missing-data handling;
- provenance note (especially for hindsight-informed composites);
- causal test ID.

### D.1 Retained stock features (each in both `xs_pct` and time-series normalized form)
- ret5, ret20, sma20, range20, rsi14, relvol, dd252, rvpct.
- **Mandatory addition:** time-series-normalized and vol-scaled versions of each, so absolute stock state can vary through time. This fixes D6.

### D.2 Required sector features
- **Taxonomy:** point-in-time sector classification. GICS changes, such as the 2018 Communication Services creation, must be applied as of their effective dates.
- **Sector proxy series:** primary source is SPDR sector ETFs (total return).
  - Sectors whose ETF launched later (e.g. Real Estate, Communication Services) need a registered pre-launch proxy, such as an external index or a constituent-based series from a certified non-sealed source.
  - If no conforming proxy exists: **STOP** and request approval.
- **Sector-level measurements:**
  - ret5/20/60/120;
  - drawdown from 252d high;
  - realized vol and vol change;
  - MA gap/slope geometry;
  - sector relative strength vs SPY (level, Δ, accel);
  - cross-sector rank of relative strength;
  - sector-vs-market correlation (60d);
  - sector stress (drawdown × vol percentile);
  - sector breadth (from a certified external or disjoint constituent source).
- **Stock-vs-sector measurements:**
  - stock return minus sector return (5/20/60);
  - residual momentum vs sector;
  - stock beta to sector;
  - stock vol relative to sector vol;
  - stock percentile within sector peers present in the current tradable universe, with a peer-count reliability feature.

### D.3 Market / R1 features (retained, with provenance repair)

**Retained:** mret5, mret20, mdd, breadth200, breadth20, mrv, breadth_vel5, breadth_vel10, breadth_accel, breadth_persist, prior_destruction, price_impulse, failed_rebound_reduction, short_trend_repair, vix, vvix, funding, credit, stress_norm, recovery_retention.

**Provenance rule (fixes D11):**
- Market returns and drawdown must come from actual market series (SPY total return, broad indices).
- Breadth must come from either:
  1. an external published breadth series; or
  2. a constituent universe certified disjoint from DV25, A25, A75 and B100 and from the fold's blind partition.
- Use of DEV117 partition stocks for market features requires explicit user approval.

**R1 constituents must be supplied as separate primitives.** The GFC adversarial evidence separated true from false recoveries on these, and the spec requires the GA to receive the dimensions separately:
- market-level positive20;
- breadth20 and breadth200 Δ over 5/10;
- failed-rebound count and Δ;
- gap20, gap50 (price vs MA);
- slope20, slope50;
- bounce magnitude.

Composites are retained as derived measurements but flagged in the registry as hindsight-informed (S-13). An ablation diagnostic is run with composites removed.

### D.4 Additional causal features to calculate

**Stock level:**
- MA geometry (gap/slope 20/50/200);
- distance to N-day high/low; Donchian position;
- ATR/vol compression (vol5/vol60);
- beta to SPY; idiosyncratic vol;
- residual momentum;
- positive-day fraction (20);
- stock-level failed-rebound count;
- max single-day return (20);
- skewness (60);
- dollar volume and Amihud illiquidity;
- overnight vs intraday return split (if open prices are available);
- short-term reversal (ret1);
- earnings: sessions since last earnings event, last surprise, pre/post-event flags (subject to D.5).

Sessions since an earnings event is stock state, not position age, and is permitted.

**Market level:**
- VIX term structure, where available;
- 3M T-bill level and Δ;
- 10y−3m slope;
- cross-sectional dispersion;
- average pairwise correlation (60d, certified universe);
- sessions since causal running-trough. This is a market-morphology clock, permitted because it is not position age.

### D.5 Data-availability gates
- **VVIX** begins after the 2006-09-15 era start. Missing-data handling must be registered (feature unavailable flag; the genome's leaf evaluates to a neutral value with an availability indicator leaf).
- **Earnings:** if point-in-time event dates and surprises are unavailable for the full window, this is an incompatibility with the approved strategy universe. **STOP and request approval.** Do not silently drop the family.
- **Warm-up data:** must exist before 2006-09-15 so that feature values on the first decision date use the same formulas as later dates. The warm-up must be registered, and no feature may use data after T.

### D.6 Leakage prohibitions
- Forward outcomes and trajectories are permitted only as discovery labels on the training partition, and only in a separate namespace unreadable by the live-feature engine (PF-15).
- No feature may be computed from blind-partition prices during training evolution.
- Cross-sectional transforms are computed within the current tradable universe: training-80 during evolution, blind-37 during blind replay.

---

## E. Horizon-Free Position Lifecycle

### E.1 Timing (proposed, to be frozen at S-6)
Decisions use data through the close of session T. Orders execute at the T+1 open with modeled costs. Positions accrue returns from the T+1 open onward.

### E.2 Valuation each session (for every stock i in the tradable universe, held or not)
- E_i = OpportunityMap(Aggregate_k(a_ik, w_k, z_ik)): estimated excess return per session over SAFE.
- Long value: V_i^L = E_i − λ_u·u_i.
- Short value: V_i^S = −E_i − 2·r_s − b_i − λ_u·u_i − extra_hurdle, where:
  - r_s is the daily SAFE rate;
  - b_i is the daily borrow cost;
  - the 2·r_s term follows from the conservative no-rebate collateral convention in J.4 (short equity forgoes SAFE yield, and E_i is measured over SAFE).
- SAFE: V = 0, cost 0, uncertainty 0.
- **No term may depend on whether i is held,** except the friction actually avoided by not trading.

### E.3 Target weights
Computed per F.2. Valuations and targets are identical for incumbents and non-holders.

### E.4 Move ledger: the unified decision rule

Capital moves from source a to destination b (assets including SAFE) only if:

> V_b − V_a > κ · (c_a^exit + c_b^entry) + λ_u · (u_a + u_b)

Execution procedure:
1. Moves are executed greedily in descending net-gain order.
2. Each move is bounded by the amount needed to bring a and b toward their targets.
3. The gross ≤ 1 constraint holds after every move.
4. Moves stop when no remaining move clears the hurdle.

Properties of κ (the friction exchange coefficient):
- It is the minimal device required by the spec's "challenger must overcome friction and uncertainty."
- It converts one-time cost into the per-session value scale.
- It is evolved and may depend on market context and uncertainty.
- It is **not** a holding period: it is identical for a position held one session or 5,000, never references age, and never forces an exit.

### E.5 Decision semantics (logged per session per asset)

| Decision | Ledger meaning |
|---|---|
| **ENTER** | SAFE → i (long). |
| **CONTINUE** | Held position not removed. Resizing toward target, funded from or to SAFE, is logged as CONTINUE (resize). |
| **REPLACE** | Incumbent i → challenger j in the same session, because the move cleared the hurdle. |
| **EXIT_TO_SAFE** | i → SAFE. Full or partial. |
| **SHORT** | SAFE → short j (entry or increase). Covering is logged as EXIT_TO_SAFE, or REPLACE if funding another asset. Short positions are evaluated each session exactly like longs. |

### E.6 How persistence emerges
Durations arise only from:
1. persistence of the causal state that generates E_i (trend, breadth persistence, sector leadership);
2. friction actually saved by not trading (via κ);
3. uncertainty margins.

Forbidden:
- position-age terms;
- elapsed-time exits;
- entry-price or entry-date-anchored features (return since entry, max excursion since entry), which violate the "where should the next dollar go today" invariance;
- cooldowns;
- re-entry delays;
- minimum or maximum hold.

Re-entry the session after an exit is always permitted (PF-17).

---

## F. Portfolio Construction

### F.1 Capital competition
All assets, including SAFE and short candidates, compete through the same value scale (E.2) and the same move ledger (E.4).

### F.2 Target weights from claims

Claim function by allocation mode:

| Mode | Claim function g |
|---|---|
| equal | g_i = η · 1[V_i > q] |
| strength | g_i = max(V_i − q, 0)^γ |
| uncertainty | g_i = (max(V_i − q, 0) / u_i)^γ |
| downside | g_i = (max(V_i − q, 0) / d_i)^γ |

Procedure:
- Compute risky claims r_i = τ(m) · g_i, using the long or short V as applicable, with sign carried.
- Let G = Σ|r_i|. If G > 1, scale all r_i by 1/G. Otherwise use them as is.
- w_SAFE = 1 − Σ|w_i| (J.4 convention).

Because claims are in absolute units and need not sum to 1, SAFE receives capital whenever opportunities are weak, uncertain, or risk appetite τ is low. This is a decision, not a fallback.

### F.3 Concentration
- No position-count limit, no per-name cap, no per-sector cap.
- High γ or a single dominant V can place up to 100% in one name or one sector (PF-18).
- Measured each session: HHI, 1/HHI, max weight, sector HHI, max sector weight, beta, correlation-implied effective number of bets.
- **Allocation concentration is permitted. Evidence concentration** (dependence of results on very few stocks or episodes) is a guard (G.3).

### F.4 Gross exposure and leverage
Σ|w_i| ≤ 1 every session. No leverage. No options.

### F.5 Proposed extension E1 (requires explicit user approval; default OFF)
- Portfolio-composition state as inputs to τ and to the downside estimator (book concentration, book average correlation, net beta).
- Own-equity-path inputs (strategy drawdown) are excluded unless separately approved, because they create reflexive path dependence.
- The four approved allocation modes must remain exactly as defined whether or not E1 is approved.

---

## G. Fitness / Evolutionary Pressure

### G.1 Primary objectives (unchanged from frozen spec)
On the fold's training-80 continuous 2006-09-15 → 2026-09-14 run, at the baseline realistic cost model:
1. **Maximize CAGR.**
2. **Minimize |MDD|.**

Selection uses NSGA-II/III constrained domination plus band islands (H.3).

### G.2 Why CAGR/MDD remains primary
- It is frozen and economically meaningful.
- Its weaknesses are a single-path MDD dominated by the GFC, and insensitivity to time underwater.
- These are handled by guards and diagnostics, not by redefining the objective.

### G.3 Guards (feasibility constraints; constrained domination; violations summed so infeasible candidates can climb)

Values are **PROPOSED** and must be ratified and frozen before execution. They are derived from first principles, not from the current results. All are training-only.

| Guard | Definition | Proposed threshold |
|---|---|---|
| G1 Validity | gross ≤ 1, finite, causal | hard reject |
| G2 Beyond-SAFE | train CAGR − SAFE CAGR | ≥ +3 pp |
| G3 Exposure-matched skill | train CAGR − CAGR of passive mix (train EW-80 + SAFE) at the same average gross exposure | ≥ +1 pp |
| G4 Era floor | each of the 4 training reset eras: CAGR − era SAFE return | ≥ −2 pp |
| G5 Recovery burden | max time underwater | ≤ 756 sessions |
| G6 Evidence concentration | CAGR excluding the top-3 PnL-contributing stocks (re-simulated with them removed from the universe) | ≥ 50% of full |
| G7 Start-date and stock-resample robustness | 20th-percentile CAGR across 8 inner 64-of-80 sub-universes × 4 start offsets (0/21/42/63 sessions) | ≥ 50% of full CAGR |
| G8 Cost stress | CAGR at 10 bps one-way + regulatory + borrow | ≥ SAFE CAGR + 2 pp |

G7 neutralizes the day-one basket degeneracy.

Guard tightening may ramp from 50% to 100% of threshold over the first 100 generations if pre-registered. Final selection always applies 100%.

### G.4 Costs during evolution
- The realistic baseline model (J.3) applies to every evaluation.
- The 10 bps stress (G8) is computed for elites.
- The full 0/5/10/20 bps sensitivity is a finalist report.

### G.5 Uncertainty and complexity tie-break
- Stationary block bootstrap (block length selected by the Politis–White rule, reported) gives CAGR and MDD standard errors.
- ε-dominance uses ε = 1 SE.
- Within ε, prefer lower active-concept count.

### G.6 Effective independent evidence (reported for every elite and finalist)

| Measure | Purpose |
|---|---|
| Raw N | sessions, stock-sessions, trades |
| Effective N, sessions | HAC/Newey-West variance inflation; block-bootstrap-implied effective sample size |
| Effective N, cross-section | date-clustered standard errors for the selection diagnostic |
| Effective stocks | 1/Σ(PnL share²) |
| Effective bets | eigenvalue participation ratio of the holdings covariance |
| Sectors contributing | count of sectors with material PnL |
| Episodes | count of independent major market episodes in which the strategy's behavior materially changed outcomes (crash defense counted by episodes, not days) |
| Cross-era recurrence | sign and magnitude consistency of contributions across the 4 eras |
| Cross-stock transport | blind vs training (diagnostic only) |
| Trial multiplicity | effective number of independent strategies tried (behavioral clustering of evaluated genomes) used for deflated performance; CSCV probability of backtest overfitting on training |

### G.7 Diagnostics (computed for all finalists; not fitness)
- CVaR5;
- worst day;
- worst 5/10/20-session loss;
- drawdown velocity;
- time underwater; time to recovery;
- turnover; SAFE fraction; short share;
- concentration;
- fold and era stability;
- per-DD-band frontier;
- selected-minus-unselected next-session return (long and short legs);
- decline table (J.2);
- R1-episode behavior traces.

### G.8 Anti-exposure bias
- G3 requires beating exposure-matched passive.
- The behavior archive (H.3) preserves low-exposure and defensive niches.
- Initialization samples τ so a material share of random genomes average under 50% exposure (PF-20).

---

## H. Evolution Schedule

### H.1 Stages
Stages shape initialization and operator probabilities only. No gene type is frozen or removed at any stage.

| Stage | Generations | Emphasis |
|---|---|---|
| A | 0–100 | Family-seeded modules; 8–12 active concepts; context and structural operators at baseline rate |
| B | 100–250 | Context/applicability operators up-weighted; sector context up-weighted |
| C | 250–450 | Full lifecycle, allocation and short co-evolution |
| D | 450–500 | Robustness refinement; guards at 100%; archive consolidation |

### H.2 Population and budget (per fold)
- **9 islands × 250 individuals:**
  - 7 band islands (ε-constraint: maximize CAGR subject to train MDD ≤ 10/15/20/25/30/35/40%);
  - 1 global NSGA-III island;
  - 1 novelty/MAP-Elites island.
- **Base:** 500 generations.
- **Pre-registered extension:** +100 generations, up to a maximum of 800. Triggered only if training hypervolume improved by more than 1% over the last 50 generations.

### H.3 Niches and novelty
- **MAP-Elites archive descriptors:** average gross exposure, SAFE fraction, short share, turnover, holdings HHI, training GFC-episode return, training recovery capture.
- **Novelty island:** behavioral-distance novelty plus feasibility.
- **Migration:** ring migration of the top 5% every 25 generations, re-evaluated under the receiving island's constraints.

### H.4 Plateau rules
- First plateau (island training-hypervolume gain < 0.5% over 40 generations): inject 20% immigrants and up-weight structural mutation.
- Second consecutive plateau: freeze the island archive and reallocate its compute.

All of this is driven by training signals only.

### H.5 Determinism and checkpointing
- Seed for each (fold, island, generation) = SHA-256(master_seed‖fold‖island‖gen), truncated, feeding PCG64.
- Checkpoint every 10 generations: population, archive, cache, RNG states, metrics history, hashes.
- Resuming from a checkpoint must reproduce the next generation bit-for-bit.

### H.6 Parallelism and compute
- Embarrassingly parallel evaluation, keyed by canonical hash, with a deterministic reduction order.
- **Multi-fidelity screening is permitted only if:**
  1. the low-fidelity calendar includes every major decline and recovery episode;
  2. Spearman correlation with full fidelity is ≥ 0.9 on a validation batch;
  3. it never eliminates defensive-niche archive members.
- Compute may expand freely. It may never be reduced by narrowing the hypothesis space.

### H.7 Mandatory calibration runs (training-only, same machinery)
- **Null run:** the full GA on DEV117 data with predictability destroyed. Stock returns are replaced by block-permuted paths, preserving the cross-sectional factor structure and the market path, so that features carry no forward information. Every stage of the pipeline then runs as normal, through blind evaluation of the null-run finalists. The null blind frontier sets the chance bar used in L.4.
- **Planted-structure power run:** synthetic data with a planted regime-conditioned signal (e.g., momentum effective only when a breadth-persistence composite is high). The GA must recover the conditional structure (applicability references the planted context) in at least 3 of 4 seeds within the base budget. Failure indicates insufficient search power.

---

## I. DEV117 Validation Design

### I.1 Fold integrity
- Use the four predetermined 80/37 folds from the hash-registered fold file.
- Folds overlap: 4 × 37 = 148 > 117, so stocks recur in blind sets. Folds therefore provide fewer than four independent confirmations, and this is reported.

### I.2 What training sees (fold f)
- T_f stock features, returns and forward labels.
- Certified market and sector features.
- SAFE.
- Nothing derived from B_f. The data loader for evolution receives only T_f arrays (PF-11).

### I.3 What blind37 cannot influence
- Evolution, guards, caching, plateau decisions, compute extensions, finalist selection, threshold setting, and other folds' evolution.
- Blind results are written to a store unreadable by evolution processes (PF-12).

### I.4 Per-fold procedure
1. Run full evolution on T_f.
2. Select finalists with the pre-registered training-only rule. For each DD band b: the archive member with the maximum bootstrap lower-bound training CAGR (5th percentile), subject to train MDD ≤ b and all guards passing. Ties within ε go to lower complexity.
3. Hash and freeze the finalists in a per-fold freeze file.
4. **Complete steps 1–3 for all four folds before any blind evaluation is run.**
5. Run a single blind replay of each frozen finalist on B_f, using the identical engine. No re-selection, no re-running with changes.

### I.5 Cross-fold assessment (architecture-level go/no-go)
- Apply the L criteria to the pre-chosen finalists.
- **Structural recurrence (diagnostic):** frequency of modules, context references, families, allocation modes and R1 primitives across fold finalists.
- **Era and fold stability:** dispersion tables.

### I.6 Production of the DV25 candidate (pre-registered now)
- **Primary:** re-run the identical frozen procedure on all 117 DEV stocks with a pre-registered seed. Apply the same training-only selection rule. The DEV117 blind folds validated the procedure.
- **Candidate set:** at most 3 bands, with one designated primary band. Fixed before any redesigned blind result is viewed.
- **Secondary diagnostic (not a DV25 candidate unless pre-registered):** an equal-capital ensemble of the four fold finalists for the primary band.

### I.7 Diagnostic-only items
- Per-stock blind transport;
- selection diagnostic;
- era breakdown and decline tables;
- motif recurrence;
- composite-ablation;
- leave-one-episode-out.

These enter only the go/no-go gate. They never feed back into genome selection.

### I.8 Look budget
- The current reduced-runner DEV117 blind results have already been viewed, and this review was informed by them. DEV117 blind is therefore partially developmental.
- Pre-register a maximum of **two** further DEV117 blind "looks" for the redesigned architecture.
- If the architecture changes after a look, record it as a new version.
- After the budget is exhausted, DEV117 blind may not be cited as transport evidence for subsequent versions.

---

## J. Economic Realism

### J.1 Actual SPY comparator
- SPY total return (dividends reinvested), plus a price-only version for reference.
- Loaded from a hash-registered file and verified against independent checkpoint values.
- Return convention consistent with MTS stock returns.
- **Naming rule:** the identifier `spy` may bind only to the SPY loader. The equal-weight partition mean must be named `ew_partition_mean_<partition>` and labeled as such in all reports.

### J.2 Decline reporting (ex post, on actual SPY)
- **Episodes:** SPY peak-to-trough declines of at least 10% (correction) and at least 20% (bear). Ex-post definitions are permitted for reporting only.
- **Per episode:**
  - MTS return;
  - SPY return;
  - Treasury return;
  - MTS MDD within the episode;
  - worst day;
  - long, short and SAFE contributions;
  - sessions for MTS and SPY to recover their prior highs.
- **Aggregate:** MTS CAGR over all SPY-declining sessions, plus the recovery-phase capture ratio.

### J.3 Cost model
- **Commission:** 0.
- **Spread and slippage (realistic baseline):** stock-day half-spread from a registered high/low/close estimator, floored at 2 bps and capped at a registered maximum. Plus a size/ADV impact term. Impact is negligible at $100k but must be specified.
- **Regulatory:** SEC Section 31 fee on sales at the historical rate schedule; FINRA TAF on sales.
- **Finalist sensitivities:** total one-way spread+slippage at 0/5/10/20 bps, replacing the spread model while keeping regulatory and borrow costs. The realistic model is reported as a fifth column. This is the proposed resolution of S-11.

### J.4 Short economics
- Borrow fee accrues daily on short notional. Baseline: easy-to-borrow at 0.30%/yr. Sensitivities at 1% and 3%/yr.
- Shorts pay dividends (short return = −total return).
- SAFE accrues on (1 − L − S) of equity; no short-proceeds rebate in the baseline. A rebate sensitivity is reported.
- Locate/recall risk is reported qualitatively.

### J.5 Execution
- Decide at close T, execute at the T+1 open plus costs.
- Sensitivity: execute at the T+1 close.
- No intraday stops, no fills at unobserved prices.
- Halts, delistings and missing prices are handled by a registered rule. Delisting returns are included where available.

### J.6 Universe realism
- Document how DEV117 was selected, and whether it is point-in-time or contains survivors.
- If survivorship cannot be ruled out, report it as an upward bias on all absolute performance figures.

### J.7 SAFE (actual 3M Treasury)
- **Series:** registered secondary-market 3M bill series, using vintage/real-time data where available.
- **Publication timing:** value usable at T only if published at or before T (the H.15 next-business-day lag implies ≥ 1 session). Forward-fill after publication; never backfill.
- **Conversion:** discount yield to investment yield, accrued per calendar day between sessions.

---

## K. Preflight Conformance Gates

The runner's `main()` executes all gates. **Any FAIL exits non-zero before evolution starts.**

- There is no override flag.
- The only path past a failure is a signed user-approval file that names the specific requirement change. That file creates a new frozen specification version.
- An independent auditor (not the implementer) re-runs the gates and signs the conformance report.

| ID | Check | Pass condition |
|---|---|---|
| PF-00 | Traceability matrix | Every frozen requirement ID maps to a code location and a test ID. Any unmapped requirement fails. |
| PF-01 | Layer existence | Schema contains MarketContexts, SectorContexts, StockStates, Modules (with applicability), Aggregator/OpportunityMap, Allocation, Lifecycle, ShortPolicy. Random genomes instantiate each. |
| PF-02 | Layer influence | For each layer, there exists a valid genome where perturbing only that layer's inputs changes target weights. For market and sector layers, the perturbation must change **gross exposure**. |
| PF-03 | Rank-cancellation regression | A genome with signal = stock feature + market feature, and τ depending on a market feature, shows a different exposure when the market feature shifts. The reduced-runner mechanics reproduced in a fixture show zero change, confirming the test detects D1. |
| PF-04 | Sector context | Point-in-time sector map loaded with effective dates. All D.2 features computed with coverage reported. Sector-feature influence test passes. Sector label is absent as a direct predictive leaf. |
| PF-05 | Allocation modes | Exactly {equal, strength, uncertainty, downside} are present and each is reachable in initialization (> 0 frequency). Fixture weights match hand calculation for each mode. |
| PF-06 | Actual SPY | Hash matches registry. At least 20 checkpoint returns match independent values within tolerance. Correlation with `ew_partition_mean` < 0.999 and max absolute daily difference above a threshold. Static scan finds no `spy` identifier bound elsewhere. |
| PF-07 | Comparators not inputs | SPY or EW series reach genomes only via registered market features. Reporting arrays are unreachable from the feature engine. |
| PF-08 | Cost sensitivities | Engine runs at 0/5/10/20 bps plus realistic. Fixture net P&L matches hand calculation. Net return is monotone non-increasing in cost when turnover > 0. |
| PF-09 | Regulatory and borrow | Regulatory fees apply on sells only. Borrow accrues daily on short notional. Shorts pay dividends. Values match fixtures. |
| PF-10 | Sealed-data isolation | OS-level sandbox denies reads of DV25/A25/A75/B100 paths. Canary files are untouched (access log empty). Every loaded ticker list is checked against the deny-list. DEV117 universe hash matches. Market and breadth universes are certified external or disjoint. |
| PF-11 | Fold isolation | Fold-file hash matches. T_f ∩ B_f = ∅. The evolution loader for fold f contains no B_f arrays, and any access attempt raises. |
| PF-12 | Blind write-only and ordering | Blind store is unreadable by evolution. Blind replay refuses to run until all four fold freeze files exist and verify. |
| PF-13 | Time-travel causality | For ≥ 200 random T: features on data truncated at T equal full-data features bit-for-bit. Randomizing all data after T leaves every decision at or before T unchanged (full engine). |
| PF-14 | Publication lags | SAFE at T equals the latest published observation at or before T. OFR and earnings lags are verified. No backfill. |
| PF-15 | Label isolation | Forward labels sit in a separate namespace. Setting all labels to NaN leaves decisions unchanged. |
| PF-16 | No hold-time or entry-anchored state | Static scan for forbidden identifiers (age, held_days, min_hold, max_hold, horizon, cooldown, entry_price, entry_date) finds none in the decision path. Two portfolios that differ only in historical entry dates produce identical decisions. |
| PF-17 | No cooldown | A fixture whose signal flips immediately re-enters the next session. |
| PF-18 | No slot or sector caps | A one-dominant-opportunity fixture can reach a 100% single-name weight. An all-qualifiers-in-one-sector fixture can reach 100% sector weight. Static scan finds no top_n, max_positions or per_sector constructs. |
| PF-19 | No leverage, no options | Σ|w| ≤ 1 + 1e−9 on every session for 1,000 random genomes. Instrument set is equities and SAFE only. |
| PF-20 | SAFE is genuine | All-negative-E fixture → 100% SAFE. Mixed fixture → partial SAFE. Raising the SAFE rate never increases risky weight, other things equal. At least 10% of random initial genomes average > 30% SAFE. |
| PF-21 | Lifecycle semantics | Scripted scenarios produce the correct ENTER/CONTINUE/REPLACE/EXIT_TO_SAFE/SHORT labels. REPLACE occurs if and only if the hurdle is cleared. |
| PF-22 | Ticker identity | Permuting and renaming stock columns produces an identical portfolio up to the permutation. No ticker string reaches the feature or genome layers. |
| PF-23 | Metric definitions | Every G.6/G.7 metric matches hand-computed references. Training-path and blind-path evaluation of the same genome on the same universe produce identical metrics. Sentinel: FAIL if turnover = SAFE fraction = 1/T for any genome. |
| PF-24 | Eras and continuous run | Exact era dates, $100k reset per era, continuous run without reset. Calendar verified. |
| PF-25 | Determinism | Identical seeds produce bit-identical genomes, fitness and checkpoints, independent of worker count. Checkpoint resume reproduces bit-for-bit. |
| PF-26 | Nesting | The reduced runner's finalist genomes compile in