# Competing independent tests

Execution COMPLETE: 120 portfolios, 6 tests, 25.10s, one CPU. Primary6 seeds and separate extended-history2 seeds; each has5 scenarios x3 policies. Arm outcomes: {'iteration6': 'FAIL', 'A': 'FAIL', 'B': 'FAIL'}. Accounting audit: True.

Primary comparator is exact frozen iteration6. Extended comparator uses its unchanged code with common600/300 split and is not the frozen configuration. No pooling. Arm A uses the explicit runnable detector and prioritized radius patch; the inconsistent full review is not uniquely testable. See preregister.json and VALIDITY.md for every ambiguity and impossibility. No mathematical repair to A.

| Stratum | Scenario | Arm | Return | Adverse return | MDD | Adverse MDD | Costs | Coverage | False GREAT (first3/post3) | Delays |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| primary | learnable | iteration6 | 85.29% | 85.29% | 0.17% | 0.17% | $25,233 | 93.1% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | reversal | iteration6 | -2.51% | -2.51% | 2.51% | 2.51% | $831 | 4.2% | 175 (86/89) | [4, 4, 5, 10, 5, 5] |
| primary | random_reversal | iteration6 | 20.58% | -2.07% | 2.55% | 2.55% | $8,323 | 37.6% | 145 (80/65) | [4, 7, 5, 5, 5, 4] |
| primary | outer_noise | iteration6 | 84.20% | 84.20% | 0.22% | 0.22% | $23,719 | 77.9% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | null | iteration6 | 0.00% | 0.00% | 0.00% | 0.00% | $0 | 0.0% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | learnable | A | 85.29% | 85.29% | 0.17% | 0.17% | $25,233 | 93.1% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | reversal | A | -47.48% | -47.48% | 47.48% | 47.48% | $13,628 | 93.4% | 3569 (86/3483) | [None, None, None, None, None, None] |
| primary | random_reversal | A | -18.43% | -34.15% | 34.47% | 34.47% | $19,057 | 93.4% | 2279 (80/2199) | [None, None, None, None, None, None] |
| primary | outer_noise | A | 78.59% | 78.59% | 0.22% | 0.22% | $22,199 | 73.9% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | null | A | 0.00% | 0.00% | 0.00% | 0.00% | $0 | 0.0% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | learnable | B | 85.29% | 85.29% | 0.17% | 0.17% | $25,233 | 93.1% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | reversal | B | -2.84% | -2.84% | 2.84% | 2.84% | $921 | 4.6% | 198 (86/112) | [5, 6, 6, 8, 6, 6] |
| primary | random_reversal | B | 18.60% | -3.68% | 4.15% | 4.15% | $8,805 | 39.7% | 239 (80/159) | [7, 9, 9, 6, 8, 8] |
| primary | outer_noise | B | 84.20% | 84.20% | 0.22% | 0.22% | $23,719 | 77.9% | 0 (0/0) | [None, None, None, None, None, None] |
| primary | null | B | 0.00% | 0.00% | 0.00% | 0.00% | $0 | 0.0% | 0 (0/0) | [None, None, None, None, None, None] |
| extended_secondary | learnable | iteration6 | 82.99% | 82.99% | 0.22% | 0.22% | $25,871 | 99.0% | 0 (0/0) | [None, None] |
| extended_secondary | reversal | iteration6 | -2.04% | -2.04% | 2.04% | 2.04% | $743 | 3.9% | 56 (29/27) | [6, 4] |
| extended_secondary | random_reversal | iteration6 | 21.80% | -1.95% | 2.55% | 2.55% | $9,168 | 42.4% | 48 (28/20) | [6, 4] |
| extended_secondary | outer_noise | iteration6 | 81.07% | 81.07% | 0.41% | 0.41% | $23,855 | 80.5% | 0 (0/0) | [None, None] |
| extended_secondary | null | iteration6 | 0.00% | 0.00% | 0.00% | 0.00% | $0 | 0.0% | 0 (0/0) | [None, None] |
| extended_secondary | learnable | A | 82.99% | 82.99% | 0.22% | 0.22% | $25,871 | 99.0% | 0 (0/0) | [None, None] |
| extended_secondary | reversal | A | -47.87% | -47.87% | 47.87% | 47.87% | $13,830 | 98.9% | 1168 (29/1139) | [None, None] |
| extended_secondary | random_reversal | A | -15.59% | -32.07% | 32.49% | 32.49% | $20,159 | 99.0% | 712 (28/684) | [None, None] |
| extended_secondary | outer_noise | A | 81.07% | 81.07% | 0.41% | 0.41% | $23,855 | 80.6% | 0 (0/0) | [None, None] |
| extended_secondary | null | A | 0.00% | 0.00% | 0.00% | 0.00% | $0 | 0.0% | 0 (0/0) | [None, None] |
| extended_secondary | learnable | B | 82.99% | 82.99% | 0.22% | 0.22% | $25,871 | 99.0% | 0 (0/0) | [None, None] |
| extended_secondary | reversal | B | -2.39% | -2.39% | 2.39% | 2.39% | $837 | 4.3% | 62 (29/33) | [6, 5] |
| extended_secondary | random_reversal | B | 19.80% | -3.56% | 4.15% | 4.15% | $9,826 | 45.2% | 78 (28/50) | [9, 8] |
| extended_secondary | outer_noise | B | 81.07% | 81.07% | 0.41% | 0.41% | $23,855 | 80.5% | 0 (0/0) | [None, None] |
| extended_secondary | null | B | 0.00% | 0.00% | 0.00% | 0.00% | $0 | 0.0% | 0 (0/0) | [None, None] |

False GREAT = individual latent TERRIBLE predicted GREAT, not conditional-mean classification error. Non-reversal first3/post3 fields are0 by definition; total includes all dates. Random reversal adverse return begins at switch; full return includes earlier planted gains. Missing delay is non-detection/prechange alarm and counts as rapid-detection failure. Costs include both legs; MDD includes liquidation. Confusions also use individual realized returns in per-seed results.

- primary/iteration6: stable_coverage=True, stable_false_great_zero=True, stable_no_alarm=True, five_tier_support=False, rapid_detection=False, adverse_loss_limit=True, null_abstention=True
- primary/A: stable_coverage=True, stable_false_great_zero=True, stable_no_alarm=False, five_tier_support=False, rapid_detection=False, adverse_loss_limit=False, null_abstention=True, stable_noninferiority_point=True, stable_noninferiority_t95=True
- primary/B: stable_coverage=True, stable_false_great_zero=True, stable_no_alarm=True, five_tier_support=False, rapid_detection=False, adverse_loss_limit=False, null_abstention=True, stable_noninferiority_point=True, stable_noninferiority_t95=True
- extended_secondary/iteration6: stable_coverage=True, stable_false_great_zero=True, stable_no_alarm=True, five_tier_support=True, rapid_detection=True, adverse_loss_limit=True, null_abstention=True
- extended_secondary/A: stable_coverage=True, stable_false_great_zero=True, stable_no_alarm=False, five_tier_support=True, rapid_detection=False, adverse_loss_limit=False, null_abstention=True, stable_noninferiority_point=True, stable_noninferiority_t95=True
- extended_secondary/B: stable_coverage=True, stable_false_great_zero=True, stable_no_alarm=True, five_tier_support=True, rapid_detection=False, adverse_loss_limit=True, null_abstention=True, stable_noninferiority_point=True, stable_noninferiority_t95=True

Paired learnable return differences vs comparator (95% descriptive seed t intervals):
- primary A: 0.00%, interval [0.00%, 0.00%].
- primary B: 0.00%, interval [0.00%, 0.00%].
- extended_secondary A: 0.00%, interval [0.00%, 0.00%].
- extended_secondary B: 0.00%, interval [0.00%, 0.00%].

False-alarm uncertainty (event=any stable scenario alarm on a seed; paired stable scenarios not independent):
- primary iteration6: 0/6, exact two-sided95 interval [0, 0.4592581264399006], one-sided95 upper 39.3%.
- primary A: 3/6, exact two-sided95 interval [0.11811724875702517, 0.8818827512429748], one-sided95 upper 84.7%.
- primary B: 0/6, exact two-sided95 interval [0, 0.4592581264399006], one-sided95 upper 39.3%.
- extended_secondary iteration6: 0/2, exact two-sided95 interval [0, 0.841886116991581], one-sided95 upper 77.6%.
- extended_secondary A: 1/2, exact two-sided95 interval [0.012579117093425018, 0.9874208829065749], one-sided95 upper 97.5%.
- extended_secondary B: 0/2, exact two-sided95 interval [0, 0.841886116991581], one-sided95 upper 77.6%.

Five-tier support vectors by seed (TERRIBLE, POOR, AVERAGE, GOOD, GREAT):
- primary iteration6: [[613, 642, 599, 605, 562], [602, 0, 588, 555, 637], [616, 631, 569, 0, 600], [594, 621, 591, 586, 632], [620, 592, 595, 638, 579], [611, 617, 601, 573, 622]].
- primary A: [[613, 642, 599, 605, 562], [602, 0, 588, 555, 637], [616, 631, 569, 0, 600], [594, 621, 591, 586, 632], [620, 592, 595, 638, 579], [611, 617, 601, 573, 622]].
- primary B: [[613, 642, 599, 605, 562], [602, 0, 588, 555, 637], [616, 631, 569, 0, 600], [594, 621, 591, 586, 632], [620, 592, 595, 638, 579], [611, 617, 601, 573, 622]].
- extended_secondary iteration6: [[626, 578, 609, 580, 624], [575, 531, 670, 604, 591]].
- extended_secondary A: [[626, 578, 609, 580, 624], [575, 531, 670, 604, 591]].
- extended_secondary B: [[626, 578, 609, 580, 624], [575, 531, 670, 604, 591]].

Arm A has no valid anytime error guarantee: one Gaussian null factor has exact expectation1.39894228; overlapping length2 windows with a fixed lambda already give expected two-factor product1.64872127. Its nonnegative lambda cannot respond to negative contrast shifts. Empirical alarms do not repair those defects. Arm B has a conditional synthetic proof, including fitted baseline uncertainty and mixture multiplicity, but may spend more samples detecting shifts. All numerical power intervals, paired economic/coverage/error intervals and per-seed failures are in report.json. Neither arm is promoted based on point estimates.

Bounded comparison does not meet the review's request for20 independent reversal episodes: there are6 primary seeds, with two paired episodes each, and2 separate extended seeds. Claims about<=5% population false alarms or all-seed tier support are unsupported. Individual tier radii remain heuristic; Arm A's selection branch has no certified coverage. No real PIT features, public timestamp, real alpha, GA, production edits, automatic recovery or guaranteed2% realized loss. The modeled per-trade limit is unchanged.

Reproduce: `cd experiments/mts_v5_planted_signal_20261101/competing_independent_tests && python3 analyze.py` re-audits artifacts with zero portfolios. `python3 -m unittest discover -s . -v` runs six tests with zero portfolios. `run.py` refuses a second fresh-seed run. To replay archived seeds, copy this entire directory and parent reference dependencies to a separate workspace, replace entropy draws by seeds.json values in that copy, delete generated outputs there, and execute run.py; record it as a separate replay outside this120-portfolio experiment. Python standard library only. Frozen copies preserve source; original dependencies verified before and after. checksums.json covers all artifacts; commitment.json froze runner, analyzer, tests, review and prereg before seed draws.

Post-run artifact audit verified all frozen commitment hashes,120 unique archived portfolios, seed separation from iteration6, and per-seed ledger equality. No new portfolios. Exact stable alarms and B episode failures are in report.json post_run_audit.

Direct primary comparison B minus A (descriptive paired95% t intervals):
- reversal adverse return: 44.64%, interval [43.69%, 45.58%].
- random_reversal adverse return: 30.47%, interval [24.22%, 36.72%].

AVERAGE was supported on all6 primary seeds under every policy; the primary five-tier failures were missing POOR on one seed and GOOD on another. The literal radius patch did not change primary learnable support. Both extended seeds had five-tier support under every policy, so this small secondary sample does not establish a unique benefit from Claude's radius fix or guarantee support on future seeds.
