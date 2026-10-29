# MTS POST-EXPERIMENT INDEPENDENT AUDIT — CLAUDE OPUS MAX

## Mandate
You previously performed the independent senior quantitative-research architecture review that materially informed the redesigned MTS GA experiment. The redesigned DEV117 experiment has now completed. Independently diagnose the evidence. Audit your own prior recommendations as aggressively as you would another researcher's design.

Do NOT assume the ChatGPT team's interpretation is correct. You are explicitly invited to conclude that the prior Claude design was wrong, the implementation was wrong, the GA/search is wrong, the feature/information set is limiting, the representation is limiting, portfolio construction is limiting, the simulator/objective is distorting evolution, the commercial comparison is invalid, the entire MTS concept is unrealistic, or that some other explanation fits better.

Do not constrain yourself to those hypotheses. Identify anything important we missed.

## Research goal / commercial context
MTS is intended to discover an unusually strong, robust systematic equity trading system, not merely statistically detectable alpha. A competing commercial product, OmniFunds, has represented performance on the order of 10–11% monthly and roughly 96% annually. Treat those numbers ONLY as an unverified claimed/commercial benchmark; do not assume comparability or truth. Nevertheless, the owner is disappointed by MTS blind performance around 15–18% annual CAGR with materially larger-than-desired drawdowns and wants a candid assessment of whether MTS has a credible path to exceptional performance.

## Governance boundary — limits action, NOT thought
Protected DV25/A25/A75/B100 remain sealed. You may freely recommend opening protected evidence if you believe it is scientifically justified, but explain exactly why, what it would answer, and why consumed evidence cannot answer it. Do not access it. You may recommend any architecture/design/GA/data/fitness/simulator change, including reversal of your own prior recommendations. Nothing you recommend will be executed automatically; the owner will review it first.

## Completed experiment summary
Frozen controlling architecture and validation rules are appended below, followed by the final report.

Additional verified observations from post-hoc structural analysis of the representative middle-risk genomes:
- Pairwise Jaccard overlap of strategy-family sets across folds: 0.222–0.500.
- Pairwise all-feature overlap: 0.413–0.510.
- Signal-feature overlap: 0.333–0.452.
- Gate-feature overlap: 0.098–0.286.
- Therefore the four folds did NOT simply converge to one nearly identical genome.
- Three of four representative middle-risk genomes chose downside allocation.
- Representative gamma values: Fold0 4.884; Fold1 1.795; Fold2 6.0; Fold3 6.0. Gamma=6 is the allowed upper bound.
- Representative kappa: Fold0 20; Fold1 20; Fold2 20; Fold3 7.10. Kappa=20 is the allowed upper bound.
- Across all frozen finalists, correlation(blind CAGR, blind average gross exposure)=+0.865.
- correlation(abs blind MDD, blind average gross)=+0.599.
- correlation(abs train MDD, abs blind MDD)=+0.670.
- Approximate same-average-gross SPY/SAFE mixture comparison for representative middle-risk genomes:
  Fold0 gross79.0%, blind CAGR17.60%, naive SPY/SAFE mix9.18%, difference +8.42pp.
  Fold1 gross66.6%, blind CAGR15.99%, naive mix8.00%, difference +7.99pp.
  Fold2 gross87.1%, blind CAGR15.76%, naive mix9.95%, difference +5.81pp.
  Fold3 gross83.0%, blind CAGR14.75%, naive mix9.56%, difference +5.18pp.
This is a crude attribution proxy, NOT a beta-matched alpha estimate. Challenge it if inappropriate.
- Successful genomes were dominated by stock/time-series and cross-sectional information; market-state information appeared substantially in gates but crash-defense transport remained poor.
- Realized blind short share was 0 for all finalists despite short capability.
- SAFE was active (roughly 11%–99% depending finalist), so the old near-zero SAFE defect was repaired.
- Attractive middle-risk finalists generally survived 10/20 bps cost sensitivity, though some cost sensitivity was non-monotonic and deserves scrutiny.
- Four independent folds share the same historical market path, so they are NOT four independent crash-timing experiments.

## Questions — deliberately open
1. What do these results actually establish, and what do they NOT establish?
2. Is ~15–18% blind CAGR evidence of meaningful transferable stock-selection/timing skill, equity exposure/drift, overfit, or a mixture? Quantify/diagnose where possible.
3. Why did materially different genomes converge to a similar economic return neighborhood?
4. What most likely limits performance? Do not restrict yourself to architecture/search/features/allocation/market-state; diagnose freely.
5. Why does risk/crash behavior transport substantially worse than return?
6. What should we infer from gamma and kappa repeatedly hitting upper bounds?
7. What should we infer from zero realized shorting?
8. Does the experiment as actually implemented faithfully test the architecture you intended? Identify any material departures or implementation defects that could explain the results.
9. Reassess your own original experimental recommendations in light of these results. Which were good, which were mistakes, and which are now questionable?
10. Is daily-bar, long/short-or-SAFE, gross<=1, no leverage/options MTS plausibly capable of performance remotely approaching the claimed OmniFunds magnitude? Give a mathematically/economically candid answer.
11. What analyses can be done NOW on already-consumed DEV117/frozen artifacts to discriminate among explanations without another evolutionary run?
12. Then recommend the highest-information next action(s), regardless of whether they involve no compute, another GA, architecture changes, new information/data, different validation, or eventually opening protected evidence.
13. Explicitly distinguish: (a) findings supported by current evidence, (b) hypotheses, (c) implementation audits required, (d) scientific changes requiring owner approval.
14. If the evidence says the project should stop or radically change direction, say so plainly. If it says the result is stronger than the owner thinks, say that plainly too.

Return a rigorous senior-researcher report. Prioritize diagnosis over encouragement. No need to defend your previous design.