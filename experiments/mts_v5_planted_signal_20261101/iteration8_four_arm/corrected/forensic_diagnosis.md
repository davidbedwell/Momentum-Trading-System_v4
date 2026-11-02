# Forensic diagnosis of the completed corrected experiment

## Finding and scope

False alarms have two different consequences: null alarms occur while the classifier already abstains completely; outer-noise alarms stop a real synthetic trading opportunity. False-alarm reduction without additional observed delay is feasible on these already-seen tapes. It is not yet established on independent seeds. Arm C has a structural evidence-accumulation defect; 8B has empirical calibration-transfer failure, not the same defect.

This is a retrospective diagnostic of the 640 archived portfolios only. No experiment source, seed, holdout threshold, portfolio, GA, or monitoring process was changed or launched. Counts and economics come from per_seed.jsonl and saved replays. To recover contrasts after a detector latched (the saved trace then stops observing), the existing seed/scenario tapes were deterministically reconstructed using the frozen generator; no new seeds, fitting, or portfolio replay was performed. All 11,202 non-null recorded CUSUM contrasts matched reconstructed values within 1e-12. Counterfactual statistics continue on those existing outcomes after the original latch; they are exploratory, not new holdout results. opportunities.jsonl.gz supplies the saved label/funding audit; the reported support/coverage counts are its archived aggregates.

Stage 1 has 16 seeds with 400/200 training/calibration dates; stage 2 has 16 different seeds with 600/300 dates. Full candidates also change classifier uncertainty. All detector comparisons below respect history. There are six conceptual arms plus two history clones, hence eight reported rows. Existing unrelated workspace changes were left alone.

## What the null actually means

The frozen generator in ../../discrimination_iteration5/experiment.py sets

\[
y_{ij}=M_{z_{ij}}+u_i+\epsilon_{ij},\quad M=(-.012,-.004,0,.004,.012),\quad z\sim\operatorname{Uniform}\{0,\ldots,4\}.
\]

These are **net** one-session returns. Prices embed costs through
\(1+g=(1+y)(1+c/2)/(1-c/2)\), with \(c=.003\), and `observed` removes the same execution costs exactly. Thus \(E[y]=0\), while expected gross return is approximately +0.30045%; that apparent gross drift only offsets execution friction. In null, the sensor source is an independent uniform draw, so \(E[y\mid f=c]=0\) for every cell. Neither the sensor nor the independent lag-price feature has a planted forecasting edge. Latent winners exist, but their evaluator-only labels are unavailable to the policy. Favorable realized outcomes are not evidence of an ex ante opportunity.

**There is no learnable-to-null switch in a null tape.** Training, calibration and test all use independent sensors. The learned null cell means are near zero, rather than inherited ±1.2% learnable means. A claim that null alarms are caused by training on learnable and suddenly testing on null would be wrong. The mismatch is between detector calibration laws and deployment laws, plus finite-sample centering error. A transition from a trained positive signal into an uninformative regime is a different case and must remain detectable.

Across all 32 null seeds, every arm has zero coverage, funded trades, exposure, costs and return. Learned five-cell spread is 0.0270–0.1331% in stage 1 and 0.0366–0.1192% in stage 2, always below the existing 0.3% identifiability rule. Null abstention is appropriate; disabling a drift latch there changes alarm reporting, not current economics. In another DGP a common positive net premium could make an uninformative sensor tradable; that is absent here.

## Grounded alarm counts and timing

Offsets below are zero-based sessions from evaluation start (606 or 906); an offset 9 is the tenth evaluation decision. All cells have 16 seeds. Stable union is the number of seeds alarmed in any of learnable, outer_noise or null, not the sum of scenario counts.

| Arm | Learnable | Outer noise | Null | Stable union | Reversal delay range | Random reversal delay range |
|---|---:|---:|---:|---:|---|---|
| 6 | 0 | 0 | 0 | 0 | 4–6 | 4–11 |
| 7B | 0 | 0 | 0 | 0 | 5–7 | 6–10 |
| 8A-D | 0 | 2 | 9 | 10 | 4–7 | 4–9 |
| 8B-D | 0 | 3 | 9 | 11 | 3–3 | 3–4 |
| 6-600/300 | 0 | 0 | 0 | 0 | 4–8 | 4–9 |
| 7B-600/300 | 0 | 0 | 0 | 0 | 5–7 | 6–9 |
| 8A-Full | 0 | 2 | 5 | 6 | 5–7 | 4–8 |
| 8B-Full | 0 | 4 | 4 | 7 | 3–3 | 3–4 |

All reversal tapes alarmed; none had a prechange alarm. Exact stable false-alarm offsets:
- 8A-D: outer_noise [119, 124]; null [117, 118, 122, 105, 86, 107, 46, 123, 98].
- 8B-D: outer_noise [16, 82, 68]; null [86, 93, 10, 19, 23, 100, 63, 16, 18].
- 8A-Full: outer_noise [120, 97]; null [72, 67, 74, 121, 91].
- 8B-Full: outer_noise [45, 99, 68, 43]; null [9, 18, 71, 67].

8B immediate reversals are 3 sessions in 32/32 cases. For random reversals, stage 1 is 15/16 at 3, one at 4; stage 2 is 14/16 at 3, two at 4. Combined random reversals are **29/32 at 3**, three at 4. Across both reversal scenarios 8B is 61/64 at 3. The 3-session result is therefore very frequent, not universal.

## Why Arm C accumulates false evidence

`engine.py:C_ablation` uses baseline \(\widehat\mu=m_4-m_0\), window \(w\in\{2,4,8\}\), \(\sigma_w=.018/\sqrt w\), and

\[
\delta_{n,w}=\overline D_{n-2-w:n-3}-\widehat\mu,\qquad
\lambda_{n,w}=\max(0,\min(-\delta_{n,w}/\sigma_w^2,1/\sigma_w)),
\]
\[
L_{n,w}=L_{n-1,w}+\lambda_{n,w}(-\delta_{n,w})-\tfrac12(\lambda_{n,w}\sigma_w)^2.
\]

The increment is **always nonnegative**. For \(-\sigma_w\le\delta<0\) it is \(\delta^2/(2\sigma_w^2)>0\); for \(\delta<-\sigma_w\) it is \(-\delta/\sigma_w-1/2>0\); for \(\delta\ge0\) it is zero. Favorable evidence never erases unfavorable evidence. Even centered stationary noise produces positive expected log increments. For an ideal normal window deviation with SD \(\sigma_w\), the expected increment is about 0.2123 per update (illustrative, not this tape's measured rate); log(300)=5.704 can then be reached through noise alone.

Lambda is chosen from the very outcome it scores, so the exponential-MGF argument for a predictable bet does not apply. Consecutive windows share w−1 dates, and the same outcome is repeatedly counted in accumulated logs. Dependence would not alone invalidate every rolling-window test, but this accumulation treats reused, adaptively selected evidence as fresh. Three window channels also lack a demonstrated joint error budget. C scans pretest windows immediately at START, unlike B/CUSUM's test-only increments. Higher null cross-sectional variance and baseline estimation error make the positive accumulation more visible. The corrected sign fixes the direction of reversal detection, not mathematical validity. Raising its threshold may postpone alarms over 126 sessions but cannot repair this mechanism or establish an anytime guarantee.

## Why CUSUM transfers poorly

CUSUM consumes each eligible date contrast only once:

\[
D_d=\operatorname{mean}(y_{dj}\mid f_{dj}=4)-\operatorname{mean}(y_{dj}\mid f_{dj}=0),\quad
S_{n,j}=\max(0,S_{n-1,j}+\widehat\mu_D-D_{n-3}-k_j),
\]

with \(k=(.009,.0045)\). Its baseline is the mean of **paired valid contrasts** over FIT. C's baseline instead subtracts two separately estimated cell means; missing-cell dates mean these are not identical estimands in finite samples. Neither baseline is a known population mean. CUSUM plugs in its estimate with no baseline uncertainty allowance. Conditional on an overestimated training baseline, future increments are systematically more positive than calibration around the true baseline would suggest. Reflection at zero allows occasional adverse runs even when unconditional increments have negative mean. This is not C's always-positive increment flaw.

The thresholds are stage 1 (0.018, 0.0273563), stage 2 (0.018, 0.0260849), each max(0.018, 1.1 × maximum over 32 learnable calibration paths). They are not a specified error quantile, do not provide a finite-sample population guarantee, and do not cover outer_noise/null laws. The .018 scale in the drift constants is not a calibration of all deployment scenarios.

The empirical mean across each seed's full-test valid contrast SDs and training baselines is:

| Arm/scenario | Mean training D | Mean test D | Mean within-seed test SD |
|---|---:|---:|---:|
| 8B-D/learnable | 0.023426 | 0.023719 | 0.005634 |
| 8B-D/outer_noise | 0.023385 | 0.023753 | 0.007020 |
| 8B-D/null | 0.000147 | 0.000053 | 0.007872 |
| 8B-D/reversal | 0.023426 | -0.023719 | 0.005634 |
| 8B-Full/learnable | 0.023587 | 0.023492 | 0.005489 |
| 8B-Full/outer_noise | 0.023587 | 0.023465 | 0.006834 |
| 8B-Full/null | 0.000015 | -0.000029 | 0.007741 |
| 8B-Full/reversal | 0.023587 | -0.023492 | 0.005489 |

Null has larger contrast variance despite the same marginal outcome mixture: each arbitrary sensor group contains the whole latent-class return mixture. Under learnable, conditioning on a sensor narrows the latent-class distribution. Common date noise cancels from a paired contrast. Outer_noise raises idiosyncratic noise 25%, which directly raises contrast variance, without destroying the conditional signal. Null fitted contrast baselines range −0.001031 to +0.000642 (stage 1) and −0.000413 to +0.000623 (stage 2); test noise and such centering errors matter against these small empirical thresholds. The source has no population null mean shift to explain away. More history does not isolate the detector effect: stage 2 uses independent seeds and changed uncertainty estimates.

For example, stage-1 seed 634620836584636185 has null training contrast −0.00009396 yet 8B alarms at index 692 (offset 86); no trade was funded. This is a stochastic excursion relative to an estimated baseline, not evidence of lost profitability. By contrast, learnable baselines near +0.0235 become approximately −0.0235 under reversal, giving a roughly 0.047 downward change that overwhelms the thresholds after one eligible date.

## Is three sessions structural?

The trade from signal d enters at open d+1 and exits at open d+2. Every new detector explicitly consumes only d=n−3, so the first permitted changed outcome at change τ is available to it at n=τ+3. CUSUM starts test updates only then. If both sensor groups do not have at least two assets, that contrast is unavailable and the update is skipped; a sufficiently small first excursion can also require another outcome. For instance stage-1 random-reversal seed 8681148680100060182 changes at 653 and alarms at 657 (delay 4).

Thus τ+3 is the **earliest outcome permitted by this experiment's information contract**, not an unavoidable universal latency. The numerical return is determined by the exit at d+2; the extra availability session is imposed by code. Changing that contract would be a separate experiment. Sensor reversal preserves the marginal sensor law, so current sensor frequencies alone do not identify the change. A guard based solely on historical training identifiability needs no new postchange outcome and can preserve the current alarm time. Waiting for several changed outcomes would necessarily delay some first-date alarms. No detector can guarantee distinguishing overlapping stochastic laws after a single outcome with zero false alarms.

## Prealarm exposure and economics

The next table uses actual saved fills with signal in [change, alarm) for reversal scenarios, including their eventual exit P&L and costs. Means are over all 16 seeds; debit is cumulative dollars committed, potentially reusing capital, not peak capital. Exposure is the sum of saved daily exposure fractions over that interval (NAV-session equivalents), not an average allocation. Costs are already included in net P&L and must not be subtracted again. Initial NAV is $100,000.

| Arm/scenario | Funded fills | Cumulative debit | Net P&L | Execution costs | Exposure sessions |
|---|---:|---:|---:|---:|---:|
| 8A-D/reversal | 29.25 | $263,204 | $-2,118 | $786 | 2.652 |
| 8A-D/random_reversal | 29.88 | $327,672 | $-3,278 | $978 | 2.597 |
| 8B-D/reversal | 18.50 | $169,147 | $-1,390 | $505 | 1.696 |
| 8B-D/random_reversal | 17.06 | $188,620 | $-1,949 | $563 | 1.483 |
| 8A-Full/reversal | 30.94 | $275,551 | $-2,273 | $823 | 2.779 |
| 8A-Full/random_reversal | 28.81 | $318,828 | $-3,318 | $952 | 2.553 |
| 8B-Full/reversal | 19.50 | $177,429 | $-1,539 | $530 | 1.781 |
| 8B-Full/random_reversal | 17.94 | $200,150 | $-2,033 | $597 | 1.583 |

At delay 3 the policy still funds signals τ, τ+1, τ+2. The alarm prevents funding at τ+3, but cannot cancel their committed losses. Those losses explain the negative immediate-reversal economics despite fast detection. Random-reversal full-horizon return also includes profitable prechange trading; the adverse-window numbers above isolate new wrong-direction commitments.

On null every one of these economic measures is zero. Alarm-count cleanup there does not recover money. Outer-noise costs require a matched no-alarm comparison:

| Candidate vs within-history 6 | Candidate return | Control return | Return delta (pp) | Candidate/control costs |
|---|---:|---:|---:|---:|
| 8A-D | 86.99% | 87.43% | -0.437 | $24,772 / $24,929 |
| 8B-D | 76.86% | 87.43% | -10.561 | $21,875 / $24,929 |
| 8A-Full | 83.93% | 85.55% | -1.619 | $24,847 / $25,375 |
| 8B-Full | 73.09% | 85.55% | -12.460 | $21,982 / $25,375 |

These are paired descriptive mean differences on the same tapes. D variants share the classifier with their controls, so stopped funding explains their differences. Full-vs-control also includes fit_v3; 8A-Full vs 8B-Full holds that classifier fixed and the mean outer-noise return gap is 10.84 pp. Lower costs after an alarm reflect foregone trading as well as saved friction. The unchanged learnable returns (87.35% stage 1; 85.95% stage 2) do not reveal this outer-noise economic loss.

## Exploratory counterfactuals on seen data only

For a multiplier f, retain the exact CUSUM recursion, missing-date behavior and original h, but check S_j ≥ f h_j. Continue the statistic beyond the original latch on recovered existing outcomes. No new portfolio NAV is simulated. These calculations are selection on the old holdout and cannot be reported as validated performance.

| Arm | Threshold multiplier | Learnable/outer/null alarms | Immediate reversal delay-3 count | Random reversal delay-3 count | Max delay |
|---|---:|---|---:|---:|---:|
| 8B-D | 1 | 0 / 3 / 9 | 16/16 | 15/16 | 4 |
| 8B-D | 1.25 | 0 / 1 / 4 | 16/16 | 15/16 | 4 |
| 8B-D | 1.5 | 0 / 0 / 2 | 15/16 | 15/16 | 4 |
| 8B-D | 2 | 0 / 0 / 1 | 11/16 | 8/16 | 5 |
| 8B-Full | 1 | 0 / 4 / 4 | 16/16 | 14/16 | 4 |
| 8B-Full | 1.25 | 0 / 0 / 3 | 16/16 | 14/16 | 4 |
| 8B-Full | 1.5 | 0 / 0 / 1 | 16/16 | 14/16 | 4 |
| 8B-Full | 2 | 0 / 0 / 0 | 7/16 | 8/16 | 6 |

At 1.25×, every original 8B reversal alarm time is unchanged, while outer-noise alarms fall from 3 to 1 in stage 1 and 4 to 0 in stage 2; null alarms fall from 9 to 4 and 4 to 3. This directly answers “can any false-alarm reduction preserve speed?” affirmatively **on the observed data**. Threshold-only elimination of all stable alarms requires multipliers just above 2.0975934 and 1.9501768 on these tapes, with maximum reversal delays 5 and 6 respectively; it loses some first-outcome alarms. These retrospectively selected maxima are not recommended holdout thresholds.

A cleaner zero-latency guard uses existing training information: if max_c m_c − min_c m_c ≤ .003, remain UNKNOWN and record `NO_IDENTIFIABLE_SIGNAL`, while not interpreting raw detector crossings as actionable drift. Keep raw shadow crossings separately for audit; merely renaming alarms must not be claimed as statistical calibration. This removes every null actionable alarm (9/9 C-D, 9/9 B-D, 5/5 C-Full, 4/4 B-Full), with all reversal/learnable/outer-noise raw paths and funding unchanged. Stable seed unions would become 2/16, 3/16, 2/16, 4/16 respectively. It does not fix outer-noise alarms or C's invalid evidence.

Combining that historical guard with 1.25× thresholds yields exploratory stable actionable alarm counts 1/16 for 8B-D and 0/16 for 8B-Full, preserving all original reversal times. This is **two changes**, not the proposed single-change validation below. It demonstrates empirical headroom, not a population guarantee. A stronger guard requiring a confidently positive training contrast could avoid arming on uncertain signals, but needs a frozen date-level uncertainty rule and independent evaluation; the existing spread guard already perfectly separates these archived null tapes. Never use scenario names, latent truth, change times or future outcomes in a deployable guard. Do not disable monitoring merely because today's predictions became UNKNOWN: a historically identifiable signal can fail and should remain under surveillance.

## Targeted next experiment — proposal only, not launched

Make exactly one change to 8B-Full: require the **existing training identifiability flag** (spread > .003) to arm actionable CUSUM latching. Retain raw shadow statistics and crossings in all cases. Keep fit_v3, history, CUSUM baseline, drift constants, original threshold values, execution accounting and availability convention unchanged. Compare guarded and original 8B-Full on paired tapes with independent seeds, after freezing the guard and endpoints. This isolates whether nonactionable null alarms can be removed without affecting learnable/outer-noise detection or any reversal timing; it does not claim to solve outer-noise calibration.

Use fresh seeds disjoint from every prior calibration and test seed and all existing scenario laws, plus prespecified diagnostic transition tapes that lose identifiability only after training (to catch accidental disabling of legitimate drift protection). Primary endpoints: raw vs actionable alarm counts separately; all reversal delay distributions including missing contrasts; zero additional adverse-window funded exposure/loss; matched stable net-return differences; null UNKNOWN coverage and funding. Report paired seed outcomes and seed-level uncertainty. For an independently sampled seed-level union of stable scenarios, zero alarms in 59 independent seeds gives a one-sided 95% upper bound below 5%; 16 seeds cannot. This sample-size statement concerns the union per seed, not independent scenario rows, and does not guarantee the proposed change will achieve zero alarms.

If that guard works as designed, the subsequent separate single-change study should replace learnable-only threshold calibration with a frozen multi-law calibration protocol including outer_noise and null, with baseline uncertainty explicitly represented. The present exploratory 1.25× result motivates studying that tradeoff; do not adopt its number as validated. Repairing C requires predictable bets on fresh date increments with a justified scale/centering and error budget, or an explicitly empirical alternative; it is not a threshold patch.

## Evidence and limitations

Source anchors (relative to this report): engine.py (`states`, `contrast`, `C_ablation`, `CUSUM`); run.py (32 learnable-only calibration paths, per-arm construction, events and fills); ../../discrimination_iteration6/engine.py (`generate`, `replay`, maturity contract); ../../discrimination_iteration5/experiment.py (`MU`, `generate`, `observed`, `fit`, `predict`). Archive anchors: seeds.json, calibration.json, per_seed.jsonl, replays.jsonl.gz, opportunities.jsonl.gz, report.json, event_ledger.json and commitment.json. The two ../../ paths resolve from this report directory; no production sources were edited.

All original commitment hashes were checked after this diagnostic. A local hash commitment has no trusted external timestamp. No old and new seeds were pooled as independent confirmation. Scenarios and arms within a seed are paired. Full-test SDs above are descriptive (random reversal would mix regimes). Raw vs actionable alarm suppression changes the estimand and must remain explicit. A guard can preserve observed speed without providing universal false-alarm control; neither these small samples nor exploratory thresholds establish future, real-market or anytime-valid performance.


Verification: every source/calibration hash in commitment.json still matches. Only this Markdown report was added to the experiment directory by this diagnostic.
