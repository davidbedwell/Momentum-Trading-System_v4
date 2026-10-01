# Frozen Discovery Protocol — Adverse Path, Entry Timing, and Failure Conditions

Date: 2026-10-01
Status: FROZEN BEFORE EXECUTION
Base commit: 35a264023acc26f80e032d37ef7836ab06d03218
Population: corrected 67-ticker Discovery population, 125,002 trades
Forbidden evidence: remaining 80 Verification A names and all 100 Verification B names

## Purpose

Determine whether adverse path, timing, volatility normalization, and causal pre-existing price structure distinguish normal recoverable adverse excursion from genuine failure, and quantify the economic tradeoff of candidate stops and entry timing. This is Discovery. It may generate candidate hypotheses; it cannot validate them.

The Analysis Engine performs calculations only. It does not select scientific conclusions, formulate hypotheses, or decide what is meaningful.

## Integrity rules

1. Use only the corrected 125,002-trade / 67-ticker Discovery population.
2. Do not access sealed Verification A remainder or Verification B.
3. Preserve original ticker, family, genome/setup, signal, entry, terminal exit, and outcome lineage.
4. All features used at a decision point must be causally observable at that point. Full-path quantities such as eventual MAE may be used only as retrospective labels/descriptors.
5. Report full prespecified grids. Do not suppress cells because they are unattractive.
6. Any "best" result is explicitly an in-sample optimization ceiling, not validation.
7. No Search/GA, AI selection, refit, or adaptive threshold changes during execution.
8. Movement after a simulated exit may be reported diagnostically but may never be credited to policy P/L.
9. Costs, where available from the governed executable-policy assumptions, must be applied consistently; if unavailable, report gross results and mark net results unavailable rather than invent costs.
10. Every conclusion must include trade count and breadth by ticker, family/genome, and calendar period where applicable.

## A. Winner and loser MAE distributions

Compute separately for original terminal winners and original terminal losers:
- N
- MAE percentiles: 50, 70, 80, 90, 95
- MAE in percent and ATR units
- sessions to MAE percentiles: 50, 70, 80, 90, 95

Produce cumulative survival tables over fixed percent-MAE thresholds:
0.5% through 15.0% in 0.5 percentage-point increments.

For each threshold report:
- winners with MAE no worse than threshold / all winners
- losers with MAE no worse than threshold / all losers
- winner survival minus loser survival
- N and unique tickers

Also produce the same survival tables in ATR units:
0.5 ATR through 5.0 ATR in 0.25-ATR increments.

"Survival" here is descriptive only: the trade's realized MAE did not cross the threshold before its original frozen terminal exit.

## B. Fixed-stop tradeoff curves

Percent-stop grid:
1.0% through 15.0% in 0.5 percentage-point increments.

ATR-stop grid:
0.5 ATR through 5.0 ATR in 0.25-ATR increments.

For each stop, simulate chronologically from the relevant executable entry:
- gap through stop -> fill at next available open
- otherwise intraday low touch -> stop-price fill
- no favorable movement after stop may count
- original frozen exit applies if never stopped

Report:
- N
- stop count/rate
- original winners killed: count and %
- original losers cut: count and %
- average and total foregone P/L among killed winners
- average and total loss avoided among stopped losers
- gross expectancy before/after
- net expectancy before/after when governed costs exist
- incremental expectancy
- profit factor before/after
- maximum drawdown before/after using a clearly declared deterministic trade-order convention
- median return
- 5th percentile trade return
- worst trade
- unique tickers
- family/genome breadth

Do not select a stop from this curve.

## C. Time-conditioned adverse path

Prespecified path windows:
- sessions 1-2
- sessions 3-4
- sessions 5-10
- sessions 11+ through original frozen exit

For every trade calculate:
- cumulative MAE through each window
- incremental adverse excursion added during each window
- whether a new adverse low occurs in each window
- recovery fraction at the end of each window relative to the deepest causal adverse excursion then known
- eventual original terminal outcome

Report winner/loser distributions and transition matrices between windows.

Time-stop grid:
1 through 20 completed sessions after executable entry.

At each time stop report the same economic metrics required in section B.

Also evaluate a prespecified two-dimensional descriptive matrix:
percent stop {2,3,4,5,6,8,10,12,15}% x maximum holding period {2,4,5,10,15,20} sessions.
This matrix is descriptive and cannot nominate a rule merely because one cell is best.

## D. Conditional-regime breakdown

Prespecified causal conditioning dimensions:
- initial AE depth: <3%, 3-<5%, 5-<8%, >=8%
- time to causal AE low: <=2, 3-4, 5-10, >10 sessions
- causal recovery fraction: <25%, 25-<50%, 50-<100%, >=100%
- ATR-normalized AE bins: <1, 1-<2, 2-<3, >=3 ATR
- eight frozen Search families
- exact frozen genome/setup identity
- calendar year
- broad market-regime labels only if already causally defined by repository artifacts before this protocol

Do not invent new regime labels after results are viewed.

For each condition report N, ticker breadth, original win rate, expectancy, MAE distribution, time-to-MAE distribution, and the percent/ATR stop tradeoff curves.

Interactions are permitted only for the following prespecified pairs:
- AE depth x time-to-low
- AE depth x recovery fraction
- AE depth x ATR-normalized AE
- time-to-low x recovery fraction
- family x AE depth
- genome x AE depth

All other interactions are exploratory observations requiring a new frozen protocol before rule selection.

## E. Causal structural reference analysis

Moving averages:
SMA {10,20,30,40,50,75,100,150,200}; EMA {20,50}.

Slope is normalized change in the average over the preceding 5 completed sessions:
slope_norm = (MA_t - MA_t-5) / ATR20_t.
Classify positive if > +0.10 ATR, approximately flat if [-0.10,+0.10] ATR inclusive, negative if < -0.10 ATR.

Touch: session low <= reference <= session high.
Penetration: low below reference, measured in percent and ATR20.
Reclaim: close returns above reference after having traded below it.
Prompt reclaim windows: 1,2,3,5 completed sessions.
Sustained break: closes below reference for 3 consecutive completed sessions.

Causal swing low: a low lower than the preceding two completed-session lows and subsequently confirmed only after two later completed sessions both have higher lows. The swing becomes usable only on completion of the second confirming session. Swing high is symmetric.

Prior-high/low windows: 5,10,20,50 completed sessions, excluding the current session.

Structural sweep of a prior/swing low: intraday low penetrates the causal reference by <=0.50 ATR20 and the same or next completed session closes back above it.
Structural failure: penetration >0.50 ATR20 OR 3 consecutive closes below the reference. These are descriptive definitions for measurement, not a trading rule.

Compression geometry uses only causally confirmed swing points. Require >=2 usable swing highs and >=2 usable swing lows in the preceding 50 completed sessions. Fit ordinary least-squares lines separately to swing highs and swing lows against session index. Normalize slopes by ATR20. Classify:
- converging/compression: lower-line slope exceeds upper-line slope by >=0.05 ATR per 10 sessions
- expanding: upper-line slope exceeds lower-line slope by >=0.05 ATR per 10 sessions
- approximately parallel/range: absolute slope difference <0.05 ATR per 10 sessions
For converging cases, separately label ascending/descending/mixed according to the signs of the two slopes. Report boundary fit residuals; do not discard poor fits post hoc.

Confluence: two causal structural references are "near" when separated by <=0.50 ATR20. Report prespecified combinations of prior/swing low with MA and compression lower boundary.

Measure winner/loser touch, hold, sweep/reclaim, sustained-break, penetration, reclaim-time, subsequent-low, and upper-boundary-break behavior. Report all reference classes; do not select a "best MA."

## F. Repeatable path-pattern analysis

Measure these prespecified sequences:
P1: AE -> early causal low (<=4 sessions) -> >=25% recovery -> controlled retest without structural failure -> continuation to original favorable terminal outcome.
P2: AE -> >=25% recovery -> structural sweep -> reclaim within 3 sessions -> continuation.
P3: AE -> weak/failed recovery (<25% by 4 sessions after causal low) -> new lower low -> original unfavorable terminal outcome.
P4: AE -> structural failure -> failed reclaim within 5 sessions -> new lower low -> original unfavorable terminal outcome.

For each: prevalence, conditional terminal outcome rate, expectancy under original frozen exit, ticker breadth, family/genome breadth, year stability, and uncertainty. These are descriptive patterns until a separately frozen executable policy is nominated.

## G. Best-genome / best-stop optimization ceiling

Using Discovery only:
1. For every exact genome/setup with adequate observations, calculate no-stop baseline economics.
2. Cross every genome with the complete percent-stop, ATR-stop, and time-stop grids above.
3. Report the combination with:
   a. highest success rate, and
   b. highest gross expectancy,
   c. highest net expectancy where costs exist,
   d. highest profit factor.
4. For each reported optimum include N, unique tickers, years, average winner, average loser, payoff ratio, total P/L in return units, expectancy, profit factor, maximum drawdown, stop rate, and original winners killed.
5. Label every optimum: IN-SAMPLE OPTIMIZATION CEILING — NOT VALIDATED.
6. Do not use the selected optimum on Verification data in this run.

A high-success-rate stop is not presumed economically superior. Report P/L and expectancy for it even if inferior.

## H. Internal Discovery stress test

Create a chronological Discovery-only development/holdout split before any optimum is chosen:
- development: earliest 70% of observations by prediction timestamp
- holdout: latest 30%
- ties at the split timestamp stay wholly on one side; choose the side that preserves chronology and report the resulting counts.

Selection of a genome/stop combination may occur on development only. Apply that exact frozen combination unchanged to the Discovery holdout.

Additionally report stability by:
- calendar year
- ticker
- eight Search families
- genome
- broad pre-existing causal market regime where available

Use dependence-aware uncertainty appropriate to repeated/overlapping observations; report the method. Do not treat raw trade count as independent sample size.

The remaining Verification cohorts remain sealed.

## I. Required falsification / misleading-analysis section

Every report must explicitly assess:
- current-S&P survivorship bias
- repeated/overlapping trades and cross-sectional dependence
- ticker concentration
- family/genome concentration
- year/regime concentration
- multiple-testing and winner's-curse effects
- sensitivity to original terminal winner/loser labeling
- cost/slippage sensitivity
- gap execution
- full-path MAE leakage risk
- instability of structural definitions
- Discovery holdout contamination risk
- effective sample size versus raw N
- whether an apparent stop benefit merely truncates both tails
- whether position sizing rather than stopping could explain the same economic improvement

State what evidence would falsify each nominated interpretation.

## Required outputs

Machine-readable JSON plus concise human-readable Markdown.

The report must contain:
1. population/coverage audit
2. winner/loser MAE survival tables
3. percent-stop tradeoff curve
4. ATR-stop tradeoff curve
5. time-conditioned MAE analysis
6. time-stop results
7. conditional-regime results
8. structural-reference results
9. repeatable path-pattern results
10. best-genome/best-stop in-sample ceiling
11. Discovery development-to-holdout replay
12. stability/breadth analysis
13. failure modes / what could mislead us
14. candidate observations, explicitly separated from any future nominated executable hypothesis

## J. Volatility-standardized excursion and regime analysis

In addition to raw-percent and ATR normalization, calculate rolling close-to-close realized volatility using trailing 10, 20, 50, and 100 completed sessions, annualization not required for z-style normalization. No current-session/future return may enter the estimate.

Express adverse excursion in sigma units using the corresponding causal rolling volatility. Report winner/loser cumulative survival at {0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,5.0} sigma for every prespecified window.

Report raw-percent, ATR20, and sigma-normalized results side by side. Also condition on causal volatility regime using the current 20-session realized volatility percentile within that ticker's trailing 252 completed sessions: low <=25th percentile, normal >25th-<75th, high >=75th. Missing-history cases remain explicit and are not imputed.

## K. Trajectory derivatives and path shape

For each causal post-entry path, in raw-percent, ATR20-normalized, and sigma-normalized coordinates, calculate:
- one-session velocity and 2-session/4-session rolling velocity
- acceleration as change in velocity
- maximum decline velocity and maximum recovery velocity
- decline/recovery speed ratio
- count of new lower lows
- count of failed rebounds
- successive-low depth changes
- sessions between successive lows
- rebound amplitude after each low
- path efficiency = absolute net displacement / cumulative absolute session-to-session displacement
- sign-change count and normalized choppiness

A failed rebound is prespecified as a recovery of >=25% of the then-observed adverse excursion followed, before reclaiming the original entry/reference, by a new lower low. Report full distributions by terminal outcome; no derivative threshold may be selected adaptively in this run.

## L. Causal state-transition analysis

At each completed session assign a descriptive state using only information then available:
DECLINING, NEW_LOW, RECOVERING_LT25, RECOVERING_25_50, RECOVERING_GE50, RECLAIMED, STRUCTURAL_SWEEP, STRUCTURAL_FAILURE, or STALLED.

When multiple labels apply, use this fixed precedence: STRUCTURAL_FAILURE > STRUCTURAL_SWEEP > RECLAIMED > NEW_LOW > RECOVERING_GE50 > RECOVERING_25_50 > RECOVERING_LT25 > DECLINING > STALLED.

STALLED means absolute one-session change <=0.10 ATR20 and no higher-precedence state applies. DECLINING means negative one-session return and no higher-precedence state applies.

Build one-step and two-step empirical transition matrices separately for eventual winners and losers, with N, ticker breadth, year breadth, and uncertainty. Also report prespecified sequences P1-P4 from section F in state form. This is descriptive; do not assume a Markov data-generating process.

## M. Change-point detection

Apply causal change-point diagnostics to the post-entry return path without using terminal outcome labels during detection. Use fixed methods:
- Page-Hinkley on normalized returns
- two-window mean shift comparing preceding 5 vs preceding 20 completed observations when history permits
- two-window realized-volatility ratio, 5-session / 20-session

Freeze Page-Hinkley parameters before implementation from standard deterministic defaults documented in code; they may not be tuned against outcomes. Report detection timing relative to AE low, recovery, structural failure, and terminal outcome. Any method whose implementation requires an outcome-tuned parameter is omitted and reported as unavailable rather than tuned.

## N. Matched-trajectory divergence analysis

Construct causal feature vectors at sessions 2, 4, 5, and 10 using only prespecified variables from this protocol. Standardize continuous variables using development-split statistics only. Match opposite-outcome trades within the same family, requiring different tickers, by nearest-neighbor distance. Genome identity may be included as a feature but is not required for a match.

Report the first subsequent observable dimension on which matched paths materially diverge, using only the already-prespecified bins/definitions in this protocol. Do not invent a new cutoff from matched outcomes. Report match distance, N pairs, unique tickers, years, and balance diagnostics.

## O. Label-blind trajectory clustering

Perform clustering without terminal winner/loser labels. Represent paths through sessions {2,4,5,10,20} using causally available normalized path summaries from sections J-K. Missing later horizons caused by earlier frozen terminal exit remain missing and must not be outcome-imputed.

Use development data only to fit preprocessing and clusters. Prespecified candidate cluster counts k={2,3,4,5,6,8,10}. Select k on development using silhouette score only, with deterministic seed/tie-break to smaller k. To bound computation without outcome-dependent sampling, compute silhouette on a deterministic evenly spaced sample of at most 3,000 development observations after chronological ordering; fit each candidate k on the complete eligible development matrix and evaluate the frozen sample against those centroids. After clusters are frozen, reveal outcome distributions and replay cluster assignment unchanged on Discovery holdout.

Clustering is an unsupervised descriptive check, not validation and not a trading rule.

## P. Information-value analysis

For every already-prespecified causal observation/state in this protocol, measure association with eventual frozen outcome using:
- mutual information with deterministic discretization defined by existing protocol bins
- conditional entropy reduction
- univariate AUC only where the variable is ordered/continuous

Estimate all preprocessing/discretization from prespecified rules or development data only. Rank variables for description, but do not convert the ranking into a candidate rule in this run. Report N, effective breadth, and Discovery-holdout stability.

## Q. Competing-risk / event-race analysis

From each executable entry, measure which prespecified event occurs first:
- favorable excursion +{1,2,3,5,8,10}%
- adverse excursion -{1,2,3,5,8,10}%
- favorable excursion +{0.5,1,1.5,2,3} ATR20
- adverse excursion -{0.5,1,1.5,2,3} ATR20
- >=25% recovery after causal AE
- entry/reference reclaim
- structural sweep
- structural failure
- original frozen terminal exit

Ties use conservative ordering: adverse/failure event before favorable event when intraday ordering is unknowable. Report cumulative incidence/event-race tables and time-to-event distributions. Do not infer intraday path ordering unavailable from the source bars.

## R. Entry timing / opportunity-cost frontier

Evaluate entry at prespecified causal milestones rather than selecting an optimized entry:
- original executable entry
- after 25%, 50%, 75%, and 100% recovery from causal AE
- first prompt structural reclaim
- first controlled retest after >=25% recovery, where controlled retest means no structural failure under section E
- sessions 1,2,3,4,5 after causal AE low when the trade remains eligible

For each entry policy report participation rate, missed favorable trades, entry-price improvement/deterioration, subsequent MAE/MFE, terminal P/L under the original frozen terminal exit, expectancy, profit factor, drawdown, and opportunity cost versus original entry. No entry policy is selected in this run.

## S. Three-action decision framing

All candidate observations in the report must be assessed, descriptively, against three possible future actions rather than stop-only framing:
- ENTER / MAINTAIN NORMAL EXPOSURE
- WAIT / REDUCE EXPOSURE
- ABANDON / EXIT

This section does not assign an action rule. It reports whether evidence appears more relevant to entry timing, position sizing/exposure, or thesis invalidation, and states what untouched evidence would be required before such an action could be promoted.

## Additional required outputs

Append to the required report:
15. sigma-normalized MAE and volatility-regime tables
16. trajectory derivative/path-shape analysis
17. state-transition matrices
18. change-point diagnostics
19. matched-trajectory divergence results
20. label-blind clustering plus unchanged Discovery-holdout replay
21. information-value analysis
22. competing-risk/event-race analysis
23. entry opportunity-cost frontier
24. ENTER/WAIT/ABANDON evidence framing

These additions are frozen before execution and inherit all integrity, causality, reporting, falsification, and stop-condition requirements above.

## Stop condition

This protocol ends after reporting the prespecified Discovery analyses and Discovery-only holdout replay. Do not open remaining Verification A or Verification B. Do not promote an optimized cell as validated. Any proposed executable trading hypothesis must be separately specified and frozen before untouched validation.
