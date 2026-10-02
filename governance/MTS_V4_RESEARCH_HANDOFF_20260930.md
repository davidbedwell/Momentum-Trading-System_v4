# MTS v4 — September 30, 2026 Research Handoff

## Status
Branch: `mts-v4-evolutionary-search-governance-20260928`

This session ended after the final Discovery adverse-excursion / recovery / stop analysis. No Verification A remainder or Verification B data were accessed by these Discovery experiments. No Sol calls, adaptive Search, refit, or rule selection were performed in the final studies.

## Scientific boundary
The current evidence is Discovery evidence. It is useful for hypothesis formation and falsification, but it is not validated tradeable alpha. The 503-name calibration universe is current-S&P-500 based and therefore survivorship-biased. The authoritative historical PIT membership problem remains unresolved. Verification A1 used 20 frozen names earlier; the remaining 80 Verification A names and all 100 Verification B names remain sealed.

## Discovery population
The final trajectory and stop studies use all 67 open Discovery tickers: the original 50-name Discovery-2 cohort plus the 17-name sector-balancing supplement.

A coverage audit found that an earlier trajectory run contained only 107,934 trades because nine entire ticker checkpoints were empty: SO, T, XEL, WELL, SPG, SNPS, SBAC, TRGP, and STLD. The runner was patched to reject empty checkpoints and require complete ticker coverage. Those nine were rerun. The authoritative corrected trajectory population is 125,002 trades across all 67 tickers.

## Corrected trajectory finding
Original terminal winners:
- n = 80,406
- median MAE = -3.19%
- median sessions to MAE = 4
- median decline/session = -0.68%
- median rebound/decline speed ratio = 3.382

Original terminal losers:
- n = 43,585
- median MAE = -10.28%
- median sessions to MAE = 18
- median decline/session = -0.54%
- median rebound/decline speed ratio = 2.441

Interpretation: in this Discovery population, eventual winners tend to experience shallower adverse excursion, bottom much sooner, and rebound faster relative to their decline than eventual losers. This is descriptive Discovery evidence, not a selected rule.

## Partial-recovery finding
Across AE depths from 1% to 10%, waiting for a larger fraction of recovery did not improve win rate. Early 25% recovery generally preserved a better entry price and similar or higher win rate than waiting for full recovery. Full reclaim frequently surrendered entry price without improving discrimination.

Examples from the corrected run:
- 3% AE / 25% recovery: 81,111 confirmations, win rate 64.6%, mean return 4.54%, median entry 2.40% below original reference.
- 5% AE / 25% recovery: 59,972 confirmations, win rate 64.8%, mean return 4.92%, median entry 4.11% below reference.
- 10% AE / 25% recovery: 29,099 confirmations, win rate 65.2%, mean return 5.84%, median entry 8.22% below reference.
- 10% AE / full recovery: 12,945 confirmations, win rate 62.5%, mean return 4.55%, median entry 1.34% above reference.

The printed `filtW=0` field in the trajectory runner is not authoritative; the separate accounting audit showed nonzero filtered winners. Do not use that printed field for inference.

## Static discriminator finding
The preceding recovery-discriminator analysis found essentially no useful static snapshot discriminator between confirmed-reclaim winners and losers. Leading continuous features had AUC values around 0.49–0.50 and very small separations. This shifted attention from static indicator state to path/trajectory behavior.

## Final early-recovery stop neighborhood
Frozen neighborhood:
- AE: 3%, 3.5%, 4%, 5%
- timing: AE reached by session 3, 4, 5, or unrestricted
- causal recovery confirmation: 25% or 50%
- entry: next-session open after confirmation
- stops: 1%, 2%, 3%, plus no-stop comparator
- gap-through stop at open; otherwise intraday-low touch at stop price
- original frozen terminal exit if not stopped
- no target
- no post-hoc best-cell selection

### Day <= 4, 25% recovery — aggregate
At 3% AE:
- no stop: n=47,812, win=65.2%, mean return=+5.29%
- 2% stop: win=20.2%, mean return=+0.85%, stop rate=79.0%
- among stopped trades: 78.3% subsequently fell another 2%, 94.0% later recovered to entry, and 56.9% would have been terminal winners without the stop

At 3.5% AE:
- no stop: n=40,522, win=65.3%, mean return=+5.56%
- 2% stop: win=19.6%, mean return=+0.88%, stop rate=79.8%
- stopped: 79.1% fell another 2%, 94.6% recovered to entry, 57.3% would have been terminal winners

At 4% AE:
- no stop: n=34,539, win=65.6%, mean return=+5.89%
- 2% stop: win=19.0%, mean return=+0.89%, stop rate=80.4%
- stopped: 79.5% fell another 2%, 95.2% recovered to entry, 57.9% would have been terminal winners

At 5% AE:
- no stop: n=25,248, win=65.7%, mean return=+6.50%
- 2% stop: win=18.1%, mean return=+0.99%, stop rate=81.4%
- stopped: 81.2% fell another 2%, 96.0% recovered to entry, 58.5% would have been terminal winners

### Interpretation of 2% stop hypothesis
The hypothesis was that after early recovery, a subsequent 2% stop might identify trades likely to continue lower rather than recover.

One part is true: stopped trades often do continue lower in the near term. Roughly 78–81% subsequently fell another 2%.

The important part is falsified in this Discovery sample: the stop does not reliably identify eventual failure. Roughly 94–96% of stopped trades later recovered to the entry price, and roughly 57–59% would ultimately have been terminal winners without the stop. The 1–3% stop neighborhood therefore appears too tight for this entry mechanism in aggregate.

This does not establish that no stop is optimal. It only rejects the tested tight-stop neighborhood as an effective failure discriminator in this Discovery population. A structural failure condition or materially wider stop would be a new hypothesis requiring a separately frozen experiment.

## Eight-family 2% stop breakdown
The same day<=4 / 25%-recovery / 2%-stop analysis was broken out across all eight Search families. The destructive stop behavior is broad rather than confined to one family.

At 5% AE:
- Breakout: stop 84.7%; recover-entry 98.1%; 64.6% of stopped trades would have been terminal winners.
- Market Regime/Structure: stop 86.5%; recover-entry 97.2%; terminal-winner 62.4%.
- Mean Reversion: stop 78.4%; recover-entry 95.1%; terminal-winner 55.6%.
- Momentum: stop 84.7%; recover-entry 98.1%; terminal-winner 66.1%.
- Relative/Cross-Sectional: stop 85.0%; recover-entry 97.7%; terminal-winner 70.8%.
- Trend: stop 85.6%; recover-entry 98.1%; terminal-winner 65.5%.
- Volatility: stop 86.4%; recover-entry 97.1%; terminal-winner 61.1%.
- Volume/Liquidity: stop 76.2%; recover-entry 93.4%; terminal-winner 49.3%.

No family provides evidence that the 2% stop becomes a clean failure classifier.

## Important incomplete item: frozen composites
The user requested both eight-family and previously frozen composite-specific analysis. The final runner produced the aggregate and exact eight-family breakdown, but it did NOT produce the requested composite-specific slice. Composite membership was deliberately not reconstructed from memory because doing so could alter the frozen definitions. Therefore the composite-specific stop analysis remains incomplete and must not be represented as completed.

Previously frozen composite structures remain available for a later exact executable-membership replay, including the recurring structures and negative control already used in prior Discovery and Verification work. If resumed, recover their exact frozen executable definitions from repository artifacts before computing the stop slice; do not infer membership from family labels.

## Earlier Discovery evidence retained
Cross-ticker frozen transport previously showed recurrence for 7 of 8 composite structures across D2 and D2B, with the Momentum-trigger / Momentum+Relative+Volume 2-of-3 structure acting as a weak negative comparator.

Chronology analysis found recurring cross-stock structures across historical eras, strongest descriptively in Mean Reversion, Trend, Relative, Volume, Momentum, and Market Regime families. These results are still Discovery evidence and not independent investable-alpha proof.

The unconditional baseline audit showed selected Discovery candidates broadly exceeding same-horizon unconditional returns, but because the candidates were selected in-sample this is context, not validation.

## Verification A1 status
Verification A1 is the frozen 20-name cohort:
APP, BKR, C, CAT, CEG, CF, CL, CPT, DE, EIX, EQT, FRT, HUM, LLY, Q, RJF, SJM, SW, VZ, XYZ.

The prior structural and executable A1 replay showed mixed results. MarketRegime+Momentum+Volume and MarketRegime+Volatility+Volume were the more coherent positive structures descriptively; several other structures weakened or contradicted Discovery behavior.

The A1 stop diagnostic did not justify post-hoc stop selection. Wider stops sometimes preserved effects better descriptively, but no stop was selected.

Remaining Verification A (80 names) and Verification B (100 names) remain sealed.

## Negative findings worth preserving
Do not lose these:
1. Static reclaim-moment indicators did not discriminate winners from losers.
2. Fixed delayed-entry discounts alone did not solve adverse-excursion risk.
3. Waiting for full reference-price reclaim did not improve win rate and sacrificed entry price.
4. Tight 1–3% stops after early partial recovery are too frequently triggered and remove many eventual winners.
5. A 2% stop remains poor even after 5% AE and across all eight individual Search families.
6. No current result establishes tradeable alpha, an optimal stop, or a production entry rule.

## Current hypothesis worth preserving
The most interesting unresolved Discovery observation is path-based rather than snapshot-based:
- eventual winners tend to bottom near four sessions with approximately 3% median MAE;
- eventual losers tend to continue declining much longer and deeper;
- early partial recovery preserves entry advantage;
- a shallow retest after that recovery is common even among eventual winners.

The next useful research question is therefore not simply a tighter price stop. A future study could examine causal structural/path failure conditions or wider risk boundaries, but it must be frozen prospectively and tested without converting this Discovery exploration into post-hoc rule selection.

## Key output files
- `/home/ubuntu/mts-v4-search-results/MTS_DISCOVERY_TRAJECTORY_ACCOUNTING_AUDIT_20260930.json`
- `/home/ubuntu/mts-v4-search-results/MTS_DISCOVERY_TRAJECTORY_PARTIAL_RECOVERY_20260930.json`
- `/home/ubuntu/mts-v4-search-results/discovery_trajectory_partial_recovery_checkpoints_20260930/`
- `/home/ubuntu/mts-v4-search-results/MTS_DISCOVERY_EARLY_RECOVERY_STOP_NEIGHBORHOOD_20260930.json`
- `/home/ubuntu/mts-v4-search-results/discovery_early_recovery_stop_checkpoints_20260930/`
- `/home/ubuntu/mts-v4-search-results/MTS_DISCOVERY_RECOVERY_DISCRIMINATORS_20260930.json`
- `/home/ubuntu/mts-v4-search-results/MTS_DISCOVERY_RECOVERY_PATTERN_SUMMARY_20260930.json`
- `/home/ubuntu/mts-v4-search-results/MTS_DISCOVERY_ADVERSE_EXCURSION_DELAYED_ENTRY_20260930.json`

## Relevant September 30 commits
- `7139f3461072e3f3adcb4760493f3a6c16bbd7ce` freeze adverse-excursion delayed-entry protocol
- `aa64eef7085e7bfb4f851418af7b1f155c7e46a9` adverse-excursion delayed-entry runner
- `a5f2c98830de945d9fbe0a8c661b5b9bd5705220` freeze recovery-pattern protocol
- `54bf7d91b55e0c90a5fd9e393a470915ac7bac3b` recovery-pattern measurement
- `8345dd80511c5d33a2665249f63d45abe8128d94` freeze recovery discriminator protocol
- `2841fc823731c70563b7c5885ec9fcf021d28fce` recovery discriminator analysis
- `89c3ee99b04d250bf774027db7518d421fb9dead` null-comparison fix
- `cafd30294b85545d2b5cc928d520bd2aa706f873` freeze trajectory/partial-recovery protocol
- `9e91eab91c62a9f5924b0e3d3717a61b5214027a` trajectory/partial-recovery runner
- `13b2838773f9cf71403b363736b973179ce9996d` freeze early-recovery stop-neighborhood protocol
- `1635be7d49da65151f4e0ba825dd06bc87369ca1` trajectory accounting audit
- `969f709bbcf1978d048daade7149c540f0977590` audit parent-row lookup fix
- `ee9622174b1951f114df3a1e5fa8865552acd431` reject empty trajectory checkpoints / complete coverage
- `08b8e5a2183f1db3abd7734523c49ad04b781050` early-recovery stop runner
- `c474846455910a2a59914165feda10e93595b627` worker initialization fix
- `df3721c8cde91a194df8e4ec490c716bb7155961` eight-family breakdown

## Recommended restart point
1. Do not run additional adaptive Discovery tonight.
2. Preserve the corrected 67-ticker trajectory and final stop JSONs.
3. If the composite question is resumed, first recover exact frozen composite executable membership and run only the already-frozen stop neighborhood against those structures.
4. Decide prospectively whether the next scientific step is an untouched-data test of a specifically frozen path/recovery hypothesis. Do not choose a rule from the 128-cell Discovery table and call it validated.
5. Keep Verification A remainder and Verification B sealed until the exact hypothesis and pass/fail criteria are frozen.


## Prospective next Discovery hypothesis — structural support, moving averages, and compression
**Status: hypothesis only. Added after completion of the September 30 experiments. This section does not alter, reinterpret, or select from the frozen results above.**

The final stop-neighborhood work suggests that a fixed percentage decline after early recovery is a poor failure discriminator. A more plausible next question is whether eventual winners and losers interact differently with **pre-existing price structure** during adverse excursion and recovery.

### A. Moving-average support/reclaim
Before observing results, freeze a small, explicit comparison set rather than searching arbitrary periods. Candidate set discussed:
- SMA 10, 20, 30, 40, 50, 75, 100, 150, 200
- EMA 20 and EMA 50 as limited prespecified comparisons

For each average, classify its causal slope at the relevant decision point as positive, approximately flat, or negative using a definition frozen before execution. Measure:
- whether the AE touches/crosses the average;
- penetration below it in percent and ATR units;
- whether price reclaims it within 1, 2, 3, or 5 sessions;
- subsequent MAE and MFE;
- terminal winner/loser outcome;
- winner-versus-loser differences in touch, hold, sweep/reclaim, and sustained-break behavior.

Do not search for an arbitrary “best SMA.” The purpose is to determine whether a stable structural relationship exists.

### B. Prior-high / prior-low structural hypothesis
Reconstruct only structure that was observable before the signal/decision point. Candidate measurements:
- prior 5-, 10-, 20-, and 50-session highs/lows;
- most recent causally confirmed swing high and swing low;
- distance to and penetration through the prior low, in percent and ATR;
- touch versus sweep-and-reclaim versus sustained break;
- sessions spent below the prior low;
- time to reclaim;
- higher/equal/lower subsequent low;
- corresponding behavior around prior highs during recovery.

Primary descriptive comparison:
- eventual winners: does AE tend to test or modestly sweep an existing low/structural boundary and reclaim it promptly?
- eventual losers: do they tend to penetrate farther, remain below the boundary longer, fail to reclaim, or establish another lower low?

This directly tests whether the tight-stop failure occurred because a fixed 1–3% threshold confuses a normal structural retest/liquidity sweep with genuine breakdown.

### C. Triangle / compression hypothesis
Test the previously discussed “triangle” concept objectively rather than visually. Using only causal swing points available before the decision:
- estimate a lower boundary from prior swing lows;
- estimate an upper boundary from prior swing highs;
- measure slopes and convergence/divergence;
- classify geometry prospectively as converging/compression, ascending, descending, approximately parallel/range, or expanding, with numerical tolerances frozen before execution.

Then measure whether eventual winners disproportionately follow:
`AE -> lower-boundary test/sweep -> reclaim -> later upper-boundary break`

and whether eventual losers disproportionately follow:
`AE -> lower-boundary violation -> failed reclaim -> continued lower-low sequence`.

### D. Confluence
Measure prespecified confluence rather than inventing it after inspection. Examples include a causal prior swing low lying near a rising SMA/EMA or compression boundary. Distance tolerances must be frozen in ATR and/or percent units before results are viewed.

A possible pattern to test descriptively is:
`prior structural low + rising moving average nearby -> limited sweep -> prompt reclaim`.

This is an example, not a selected rule.

### Governance for the next experiment
- Discovery only initially; do not access sealed Verification A remainder or Verification B.
- Use the corrected 125,002-trade / 67-ticker Discovery population.
- Freeze all swing definitions, MA periods, slope definitions, boundary-fitting rules, tolerances, reclaim windows, and comparison metrics before execution.
- Preserve winner and loser denominators and ticker/family breadth.
- Report the full prespecified grid; do not output only a “best” level.
- No Search/GA, refit, Sol selection, or post-hoc threshold optimization.
- Treat this as descriptive hypothesis measurement first.
- If a specific structural rule is later nominated, freeze it with pass/fail criteria before untouched-data testing.
- The unresolved exact frozen-composite stop slice remains separate and should not be conflated with this new structural experiment.

### Rationale
The current Discovery evidence suggests that **trajectory may matter more than absolute volatility**. Eventual winners had shallower and much earlier median bottoms than losers, yet many winners still experienced a substantial secondary decline after early recovery. A causal structural test may distinguish a normal retest from genuine thesis failure more effectively than a fixed percentage stop.

## Execution continuity / credit-efficiency rule — added 2026-10-01
**Status: mandatory operating rule for authorized MTS workflows. This governs execution behavior; it does not alter scientific thresholds or evidence partitions.**

When David authorizes an end-to-end MTS experiment or workflow, that authorization covers all ordinary downstream execution already implied by the approved protocol: implementation, deterministic tests, process launch, polling, result collection, ordinary debugging, governance-preserving fixes, reruns after implementation failures, downstream approved stages, and final audit/synthesis.

The assistant must keep the active tool-execution turn open while authorized work remains. Progress updates are intermediate updates, not stopping points. Do **not** send a final response that says work will continue afterward: once a final response ends the turn, autonomous tool execution cannot continue until David sends another message.

Do not require David to send `continue`, ask for status, or poll every 20–30 minutes merely to restart already-authorized work. Poll long-running processes within the same active turn. If a process fails for an ordinary engineering reason, diagnose and repair it within frozen governance and relaunch it without seeking redundant approval.

Stop and request David's decision only at a genuine decision boundary: a proposed change to a frozen protocol, scientific/governance ambiguity requiring human judgment, new spending/authorization beyond what was approved, inaccessible required evidence, or another action that materially changes the authorized scope.

For credit efficiency, use deterministic remote computation for numerical grinding and reserve model reasoning for hypothesis formation, interpretation, anomaly recognition, scientific decisions, and audit. Prefer one continuous execution session over repeated `run -> final response -> user restart -> reconstruct context -> run` cycles.

When giving an ETA, state whether the actual experiment is already launched. Never describe queued, merely designed, or not-yet-started work as running. If runtime materially changes, report the revised ETA in an intermediate update while continuing execution.
