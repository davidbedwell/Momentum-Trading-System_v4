# MTS DEV117 Horizon-Free GA Study Freeze — 2026-10-05
Status: FROZEN BEFORE NEW GA OUTCOMES
Provenance: NEW_RESEARCH_POST_RECOVERY

## Objective
Discover a causal conditional strategy ecosystem that maximizes robust CAGR while minimizing drawdown, with special attention to behaviorally tolerable performance in downtrending markets. Retain the full CAGR/MDD Pareto frontier rather than choosing one scalar optimum.

## Evidence governance
- DEV117 = already-consumed DEV50 plus the already-consumed additional 67 development stocks. No virgin/protected stock may design this GA.
- Internal transport uses repeated deterministic 80-stock discovery / 37-stock blind-transport folds.
- Forward trajectories/outcomes MAY be used as labels and fitness inside each 80-stock discovery partition so GA can learn what preceded success/failure. They may never be live/deployable inputs.
- The 37-stock side of each fold is invisible to evolution, pruning, mutation, thresholds, tie-breaking and architecture changes until that fold is frozen.
- All qualifying stocks remain in portfolio simulation. Correlated same-sector/same-regime/same-session observations do not count as independent confirmations. Report phenomenon evidence, stock-selection evidence, portfolio evidence and effective-independent evidence separately.
- After DEV117 and finalist freeze: burn 25 virgin Discovery stocks once for external validation; only after passing, burn 25 Verification-A stocks once for blind proof. No post-blind repair.
- Preserved50 and TEST17 are consumed historical diagnostics and are forbidden for design/tuning of this new architecture.

## Daily decision architecture
Every causal market session ask: “Of everything I could own today, where should the next dollar of capital be allocated?”
Actions: ENTER, CONTINUE, REPLACE, EXIT_TO_SAFE, and SHORT when economically justified.
- No minimum/maximum/fixed holding period; no position-age gene or time exit. Holding duration is an outcome.
- No slot ceiling, stock-count target, or hard sector cap. Breadth emerges from qualification and marginal capital value.
- No leverage. Capital not justified by opportunities remains SAFE.
- Historical causal 3-month Treasury yield is the SAFE competitor; use only the latest observation available by that historical date and forward-fill after publication.
- Market/regime state is information, not a mandatory exposure answer. Individual/sector opportunities may prove themselves within adverse states.
- Strategies may specialize by causal market regime, sector behavior and stock behavior. Ticker identity and future regime labels are prohibited.
- Abstention is valid.
- Capital allocation itself may evolve; equal weight is available but not privileged.

## Opportunity/context search
Available behavioral families include momentum, breakout, trend, mean reversion, reversal, pullback, volatility, volatility breakout, volume/liquidity, relative/cross-sectional strength, causal earnings, market structure and composite breadth. These are ingredients, not forced strategy classes.
Market context may include trend, momentum, breadth, volatility/VIX structure, drawdown, liquidity/funding and dispersion.
Sector context may include trend, momentum, volatility, breadth, relative strength vs market, acceleration/deceleration, drawdown/recovery and dispersion.
Stock context may include momentum, trend, breakout/reversion, volatility level/change, volume/liquidity, relative strength vs sector/market, drawdown/recovery and price structure.
Prefer bounded continuous genes where computationally practical rather than arbitrary coarse grids.

## Recovered R1 evidence
R1 is causal recovery evidence, not a rigid calendar sequence and not a mandatory portfolio response.
Six recovered evidence dimensions:
1. extreme prior destruction
2. initial price impulse
3. delayed/explosive breadth conversion
4. breadth persistence
5. continued failed-rebound reduction
6. stress normalization while retaining price recovery
Short-trend/EMA20-50 repair remains a supporting morphology descriptor, not an invented seventh required gate.
Ordering/timing may vary; recovered multi-recovery work covers 2009, 2011, 2015/16, 2018, 2020 and 2022.
Authoritative supporting corpus: R1 2009/2020 morphology; multi-recovery morphology; GFC false-vs-true; GFC divergence; adversarial false-rally; cross-sectional state reversal; causal re-entry state machine.

## Optimization and behavioral choice
Primary output is the full Pareto frontier: CAGR up, maximum drawdown down.
Behavioral DD bands 10/15/20/25/30/35/40% are reporting/choice bands, NOT fitness cliffs.
For every relevant finalist report drawdown velocity, time underwater, recovery time, worst 1/5/10/20-session loss, crash-specific loss, and continuous-run maximum dollar peak-to-trough loss.
Credibility is reported separately from economic fitness: blind transport, effective independent episodes, cross-stock/sector/era transport and uncertainty.
Absolute CAGR and Treasury excess return remain visible so near-all-SAFE inactivity cannot win through a ratio.
When candidates are economically indistinguishable within uncertainty, simpler/more stable is the deterministic tie-breaker; complexity is not a primary objective.

## Five standardized performance views
Use four predetermined ~5-year eras, each independently reset to $100,000, plus one continuous ~20-year run starting at $100,000 with no reset.
Report CAGR, MDD%, terminal wealth, continuous dollar MDD, drawdown velocity, underwater/recovery duration, worst 1/5/10/20-session loss, turnover, SAFE fraction, concentration, long/short/SAFE contribution, Treasury excess return and SPY comparison.
All open positions are marked to market daily; unrealized losses count immediately.

## Economics
Equity commission = 0. Baseline stock/ETF spread+slippage proxy = 5 bps one-way. Finalists receive zero-friction, baseline and stressed-friction replay.
Shorts must include borrow cost when reasonably available/modelable, adverse moves, gaps and realistic execution. Options excluded.

## Scientific controls
Use point-in-time universe membership wherever recoverable; survivor-only limitations must be explicit. Splits/dividends adjusted. Earnings/fundamental data use publication availability.
Signal multiplicity is not independent evidence.
No strategy family is forced.
Mandatory down-market report for every major decline: MTS, SPY, Treasury, MDD, short-window loss, long/short/SAFE contribution, drawdown velocity and recovery.
No post-blind tuning.

## Bounded staged GA
Stage 1 core strategy discovery; Stage 2 refine robust winners; Stage 3 context/architecture interactions; Stage 4 frozen replay/validation.
Initial target ~250 population x up to ~200 generations per outer experiment, using evolutionary mutation/crossover, duplicate/content-addressed caching and early stopping when the Pareto frontier stops materially improving. This is not exhaustive Cartesian enumeration. Extend only if the frontier is still improving.

## Reproducibility
Before outcome search preserve executable source, exact git commit, input paths+SHA256, environment manifest, seeds, complete gene schema, checkpoints, serialized chromosomes+lineage, fitness records/shards, deterministic replay command and serialization/replay tests. Freeze finalists before external evidence. Archive study package to Backblaze with checksum.

## Prohibited
Ticker-specific rules; calendar-date trading rules; future data as live input; fixed holding horizons; elapsed-position-age exits; session-count cooldowns; hard sector quotas; hard position-count quotas; post-blind repair; using preserved50/TEST17 outcomes to tune this architecture.
