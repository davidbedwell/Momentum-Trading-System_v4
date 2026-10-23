# GA5 eligibility-first discovery design — 2026-10-19

## Objective
Discover diverse regime-conditional chromosomes whose causally estimated, cost-adjusted and uncertainty-penalized Calmar clears an eligibility gate. 3% INITIAL target allocation for each qualifying trade, 10% absolute per-name maximum subject to total portfolio limits. No trade based solely on an attractive full-history score.

## Frozen discovery architecture
1. Entry signal and horizon discovery independent of position-sizing genes; evaluate standardized horizons 2/5/10/20/40/63 sessions, next-open fills, 10 bps per side. Track all attempted signals, including losers, unavailable fills, censored exits and costs.
2. Conditional exit optimization for retained entry families: stop, trail, time, hold, replacement. Maintain per-family baselines and ablations. Never drop a potentially profitable entry solely because its initial exit/sizing genes are poor.
3. Development chronological walk-forward folds: train on completed past observations, embargo overlapping label horizons, score subsequent sessions without future leakage. Compute annualized portfolio-return estimates and MDD with conservative uncertainty adjustment; do not use single-trade Calmar or full-sample future returns at decision time.
4. Test adjusted-Calmar eligibility thresholds 1.00,1.25,1.50,1.75,2.00 on development folds. Minimum evidence threshold must be set before threshold selection; use conservative bootstrap/block uncertainty and minimum completed-trade and distinct-market-episode counts. Insufficient evidence => NO ENTRY.
5. Eligible chromosomes receive 3% initial target weight, subject to available cash, concentration, earnings embargo, membership and risk veto. Scale toward at most 10% only with independently higher validated adjusted-Calmar threshold (initial hypothesis 2.0) and position/portfolio risk caps. Never bypass eligibility due to a strong raw signal.
6. Rank discovery using multiple objectives: adjusted Calmar, net CAGR, worst drawdown, left-tail loss, robustness across folds/market environments, and independent signal coverage. Maintain top-by-CAGR, top-by-Calmar and Pareto banks; protect behavioral diversity without forcing capital to underperformers.
7. Same-engine GA4 vs GA5 replay on identical DEV data, same costs and policy. Any non-translatable GA4 semantics => mark incomparable, not silently substitute.
8. Freeze chosen eligibility policy BEFORE untouched final blind tests. Never tune on BLIND17 or frozen A/B partitions.

## Scientific safeguards
The GA5 current full-period fitness, shadow expectancy, and retrospective niche labels are DIAGNOSTIC, not causal prospective eligibility estimates. Do not use oracle future regime classification to choose trades. Preserve full lineage, checkpoint, code/data hashes and trial counts to account for selection bias. Report actual daily invested capital, realized portfolio drawdown, cash drag, fees, turnover and skipped opportunities. A 1.5 threshold is a testable hypothesis, NOT a certified parameter.

## Current state
Design frozen here; no claim that the gate is implemented or backtested. Keep existing 8-worker GA5 run as unchanged control. Build an isolated eligibility-first runner and verify equivalence and no-lookahead before launching a production-scale diagnostic experiment.

## User-approved capital tier amendment — 2026-10-19
- Adjusted Calmar < 1.5: no new entry.
- Adjusted Calmar >= 1.5: standard 3% initial target, subject to all risk constraints.
- Adjusted Calmar >= 2.0: scaling may be authorized up to 10% per position, conditional on fresh causal evidence, concentration and risk checks.
- Adjusted Calmar > 3.0 (STRICTLY GREATER): scaling may be authorized up to 20% per position, conditional on statistically reliable completed outcomes, independent regime/episode coverage, current risk checks and available cash.
- 20% is a ceiling, not a target or automatic purchase. An estimate of adjusted Calmar must be computed only from information known by the allocation decision time; otherwise fail closed.
- These thresholds are user-approved candidate policy parameters, not validated evidence of profitable performance. Stress-test concentration and simultaneous correlated positions before any deployment.
- Discovery preference: high win-rate, repeatable net 5–10% winning trades, positive net expectancy, bounded loss tails and adequate opportunity frequency. Do not maximize win-rate at expense of expected value; do not cap unusually strong winners mechanically.

## User-approved outcome target correction — 2026-10-19
- Supersedes the earlier preference for winning trades in a 5–10% band.
- Discovery target: winning trades with NET return >5%, with NO upper profit target or take-profit ceiling imposed by this objective.
- Preserve and reward gains above 10% where exit rules and risk-adjusted expectancy justify holding.
- Still require high win probability, positive net expectancy, loss-tail control, time efficiency, and robust validation. A >5% winner target is not a mandate to hold every trade until it wins or to suppress necessary loss exits.

## Joint success-and-payoff objective — user clarification 2026-10-19
- The discovery target is JOINT: high success probability AND winning trades >5% net, without an upper profit cap.
- Report separately: (a) fraction of ALL completed trades with net return >5%, (b) ordinary win rate net >0%, (c) mean and median positive-trade gain, (d) net expectancy, (e) mean loss, left-tail loss, holding time, and (f) uncertainty bounds across independent market episodes.
- Do not substitute a high ordinary win rate with tiny gains for the requested >5% successful-trade rate. Do not count overlapping opportunities as independent statistical evidence.
- Maintain net expectancy, loss-tail and adjusted-Calmar safeguards to reject high-win-rate strategies with rare catastrophic losses.
