# GA6-H chromosome specification v0.2 — DESIGN FREEZE CANDIDATE
Date: 2026-10-22. Status: design only, not performance certification.
MISSION: independently discover daily ranked stock opportunities for 1–40 exchange sessions, optimize executable portfolio decisions. GA6-H is NOT a GA6 niche-portfolio clone.

## Frozen boundary
Chromosome controls predictive transformations, ranking, entry eligibility threshold, exit/replacement preference, and bounded sizing preference. Simulator alone controls chronological market data, order execution, cash, costs, corporate actions, 40-session absolute holding cap, embargo, portfolio risk ceilings, and validation folds. No chromosome can change data, fills, accounting, risk caps or validation periods.
Capital $100k; typical weight 3%, maximum 10%; cost benchmark 10bps per side; next-open fills; no shorts initially. Cash is a valid outcome. Quarterly earnings embargo 2 sessions before/after and event session; fail closed if schedule not verifiable, and measure coverage.

## Genetic grammar (candidate, subject to ablation)
1. Features: momentum and reversal (5/10/20/40/60/120/252); acceleration, trend and distance-to-MA; realized volatility/compression; volume/turnover and liquidity; sector-relative and market-relative strength; breadth and leadership; PIT earnings/revisions only if timestamp-verified. All transformations fit on historical training data only.
2. Leaf: (feature_id, lag>=0, window, transform, direction, threshold, missing_policy). No ticker IDs, outcome labels, future values or fixed historical winner flags.
3. Expression: nested AND, OR and grouped interactions plus continuous score aggregation. Start 1–8 distinct family leaves, allow repeated family with different windows only when independently tested; enforce complexity budget rather than arbitrary gene count cap. Mutations: threshold, window, transform, replace/add/remove leaf, operator, subgroup; crossover: subtree and aggregator. Retain valid unique identities.
4. Ranking: normalized per-session cross-sectional score; optional sector neutralization, volatility normalization, confidence and nonlinear weighting. Normalize only across historically eligible securities on decision date.
5. Entry: score threshold, score gap to alternatives, expected net edge over cash and no-entry, tradability/embargo preflight. All decisions close t, fill earliest t+1 open.
6. Hold/exit: max_hold gene 1–40 sessions; exit thresholds, deterioration, stop, trailing stop, profit capture, replacement threshold, reentry wait. Mandatory 40-session exit overrides all genes. A predicted forward horizon is NOT an executable hold.
7. Sizing: bounded preferred weight, signal confidence/volatility response; 3% reference and hard 10% cap, portfolio exposure/sector/correlation ceilings external. No fabricated free leverage.
8. Provenance: SHA-256 chromosome identity, lineage, parent hashes, mutation, seed, fold, code/data version, outcome; checkpoint and exact deterministic resume.

## Objective and selection
Pareto archive across net rank quality/top-k excess returns, cash-constrained net portfolio opportunity, tail risk, uncertainty/episode support, capacity, turnover and behavioral novelty. Penalize complexity and instability. Preserve exploratory/inconclusive chromosomes separately. Report portfolio CAGR, MDD, Calmar, fees, hit rate, average AND maximum holding sessions on chronological OOS; do not equate fitness with CAGR. Aim >=35% CAGR with controlled drawdown, not a pass-by-fiat objective.

## Attribution experiments (two distinct questions)
A. FIXED CHROMOSOME / POLICY EFFECT: identical entry signals, dates, positions, fills, and cash; change only exit/size/replacement/risk policy, then report paired delta CAGR, delta MDD, turnover and episode effects.
B. GENETIC SEARCH EFFECT: independently evolve populations with and without one gene family/operator/fitness component at equal evaluation counts, seeds, data, CPU budget and validation windows. Compare best heldout Pareto fronts and full distribution; account for multiplicity and paired market episodes. Do not call this causal until evaluated.
C. INTERACTIONS: prespecified two-way ablations (exit × replacement, sizing × risk, ranking × sector, AND/OR × feature count, entry threshold × cash). Follow up with sequential holdouts; no peeking at sealed blinds.

## Immediate specification-attribution ledger
- GA4: eight signal families, 1–8 logical combinations, horizons and stop-policy studies; historical 24.9–25% Normal CAGR is a prior user-reported research benchmark requiring exact run reconstruction.
- GA5: /opt/mts/ga5_chromosome_contract.py defines entry/hold/exit/regime/sizing/replace genes, stops, trailing stops, scale-in/out, risk budget, max_hold 1–252. Its crossover forbids crossing niches.
- GA6: /opt/mts/ga6/GA5_GA6_SCOPE_AUDIT.md adds EV-led fitness, 13 niche reporting, claimed cross-niche breeding, unrestricted entries, exit/reentry diagnostics; /opt/mts/ga6/structural_independent_v2_20261022/family_logic.py adds nested AND/OR trees with 2+ children and missing-data fail closed; structural_population.py uses random 2–8 families, Sobol threshold refinement, and niche-protected elites.
- Important source-level discrepancy: /opt/mts/ga5_chromosome_contract.py crossover rejects parents of different niches, while GA6 scope document claims cross-niche breeding. Verify actual active runner path before marking cross-niche recombination implemented.
- GA6 structural tree forbids repeated family within expression, potentially restricting useful multi-window combinations. GA6-H should test repeated-family expressions rather than silently inheriting prohibition.
- Current matched 26-row A_v2 experiment changes risk veto, not genome grammar; no GA4→GA6 causal attribution. Do not count zero-trade cash chromosomes as active strategy successes.
- Structural versus diversity best exploratory fitness is NOT CAGR. Pareto versus weighted generation-24 descriptive differences are NOT independent performance lift.

## Acceptance / release
G0 preserve artifacts, reconstruct exact GA4→GA6 change ledger and experimental evidence; G1 price/earnings PIT and delisted coverage or explicit non-certification; G2 full execution parity and forced exit queue; G3 simple rank baselines; G4 deterministic search and checkpoints; G5 ablations/interaction matrix; G6 purged chronological OOS and stock-disjoint transport; G7 portfolio benchmarks, 40-session invariant, tail-risk and episodes; G8 independent blind certification and paper trade. Do not touch GA6 production.
