# GA5 staged research experiment — frozen plan (2026-10-19)

## Why
Historical GA4 oracle diagnostic: 250,110 chromosome-horizon evaluations, best 27.943% CAGR, median 0.986%. DEV80 long: 1,489 evaluations, best 24.953%, median 1.113%. GA5 current top-50 fitness-ranked median 5.653% CAGR and best CAGR 15.318%. DIFFERENT EVALUATORS, UNFAIR TO COMPARE AS WIN/LOSS.

## Phase A — isolated signal discovery
Use DEV79 only. Each entry chromosome's signals evaluated against standardized forward horizons (2, 5, 10, 20, 40, 63 sessions), with causal entry-time features and next-session open fill. Require at least 20 completed opportunities and 10 bps cost assumptions, report mean/median net returns, win rate, left-tail loss, frequency, signal concentration, and opportunity coverage. Store all candidates and outcomes, not just scalar top ranks. A horizon outcome may be used for retrospective discovery but never as a contemporaneous selection feature.

## Phase B — exits conditional on promising entries
Freeze entry candidate shortlist BEFORE optimizing exits. Compare identical entry sets with fixed-horizon exits, stop, trail, replacement, and time-exit policies. Preserve losers and trade lineage. Selection uses DEV79 only, with walk-forward splits within DEV79 to measure generalization, not as independent blind certification.

## Phase C — portfolio construction
Replay selected entry/exit combinations with realistic cash, fees, next-open execution, corporate actions, and sizing (3% typical, max 10% strong in requested policy scenario). Report daily invested-capital fraction, number of holdings, turnover, scale-in/out notional, fee drag, cash yield, annual CAGR/MDD, and gross/net return attribution. Compare against no-scale and fixed-sizing ablations to isolate effects.

## Phase D — Pareto and selection
Non-dominated selection across portfolio CAGR, MDD, net expectancy, and tail risk, with evidence thresholds and niche diversity. Do not conflate shadow expectancy with portfolio-realized expectancy. Preserve Pareto front and scalar top-CAGR top-Calmar leaderboards separately; do not promote low-return risk-minimized genomes solely on Pareto rank.

## Phase E — controlled GA4 comparison
Translate only GA4 strategies whose signals and exits can be represented with the same causal engine. Replay on identical DEV79 symbols, sessions, earnings exclusions, fees, risk gates, next-open execution, sizing and capital. If semantics cannot be matched, label non-comparable; never infer superiority from oracle GA4 ranking.

## Phase F — validation and governance
No access to or optimization on frozen blind A/B or BLIND17. Use development-only chronological folds for model selection, record exact data and code hashes, then request explicit authorization before final blind certification. All current results diagnostic-only.

## Execution constraints
Keep existing GA5 continuous run unchanged as a control. No mutation of its checkpoint, policy or fitness while live. Implement isolated staged experiments in a separate output directory and compare against frozen baseline results. Stop and report any data/semantic incompatibility instead of silently substituting results.
