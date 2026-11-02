# Iteration6 — FAIL

Five-tier support: seed2098214662956861329 has0 AVERAGE assignments. Frozen interval straddles a band; this experiment cannot repair it after final evaluation. Next independent step must obtain more independent fit/calibration evidence under unchanged bands, then freeze and test fresh tapes. Rapid safety is promising but residual4–7-session exposure and false-alarm power need independent episode validation; no safe zero-delay detection from this DGP.

Completed 59 portfolio replays, six tests; runner elapsed 9.06s. Limit64 replays/720s. Three test portfolios, four fixed design probes, twelve paired regressions, forty frozen final portfolios. No candidate tuning, GA, production changes or final reruns. All new files stay here.

## Diagnosis

Iteration5 false GREAT count442 comprised49 in sessions606–608, before any post-change outcome was eligible, and393 after first outcome availability. Funded false GREAT trades lost $36,554 across four separate $100,000 accounts; these are a subset of portfolio PnL. Full reversal mean return was−10.31%. The frozen sensor/full models agree on the wrong sign, so disagreement cannot reveal remapping. The20-date drift window and hard-coded first scan628 impose delay. Replacing only the schedule would cross the original threshold at [623, 621, 623, 623]. See iteration5_diagnosis.json for exact per-seed counts and timestamps.

No zero-delay switch detector is identifiable here: iid symmetric sensor marginals, unconditional returns, and entire price paths are unchanged by sensor remapping. Under the required signal+3 availability rule,606 outcomes first enter at609. Later statistical accumulation is necessary to avoid excessive false alarms; not all393 later errors can simply be eliminated.

## Frozen gate

Iteration5 classifier, bands, train/cal split, disagreement filter and DGP remain unchanged. Before each entry, the gate evaluates2/4/8-date sensor-conditioned extreme-cell residual contrasts, which cancel common-date return shocks. At least2 names in each extreme cell are required per date; missing dates conservatively skip the look. An independent channel monitors date-grouped forecast errors of actual funded, matured fills. A drift alarm causes full abstention for the remaining horizon. There is no forecast-sign flip or automatic recovery. All outcomes obey signal+3<=decision.

Market/sector breadth was assessed and rejected as a switch detector: there are no sector effects or memberships, and prices are bit-identical across stable and reversal scenarios. No informative synthetic indicator was added. Residual trend conditioned on the sensor is informative. All first fresh alarms came from cross-sectional residual evidence; funded surprise did not lead detection, so this run does not establish incremental benefit from that second channel. Threshold envelopes and multiplicity bounds are prescribed synthetic engineering assumptions, not certified real-data error guarantees.

## Measured comparisons

Arithmetic per-seed means; return and MDD below use the adverse segment starting at the switch, including terminal liquidation. Costs are full-window dollars per initial$100,000 account. Random-switch total returns include earlier planted gains and therefore are not used as the adverse-loss metric.

| Phase / scenario / policy | False GREAT | Detection delay | Adverse return | Adverse MDD | Costs |
|---|---:|---|---:|---:|---:|
| paired_regression / reversal / iteration5 | 442 | [22, 22, 22, 22] | -10.31% | 10.31% | $3,104 |
| paired_regression / reversal / iteration6 | 116 | [7, 6, 5, 6] | -2.83% | 2.83% | $886 |
| final / reversal / iteration5 | 393 | [22, 22, 22, 22] | -10.30% | 10.30% | $3,136 |
| final / reversal / iteration6 | 86 | [5, 5, 5, 4] | -2.24% | 2.24% | $762 |
| final / random_reversal / iteration5 | 338 | [18, 18, 18, 16] | -8.26% | 8.71% | $11,154 |
| final / random_reversal / iteration6 | 84 | [4, 4, 4, 7] | -2.61% | 3.09% | $8,966 |

Stable final learnable coverage76.3%–100%; outer-noise38.9%–100%. Stable extreme errors0; no observed alarms across four seeds, paired stable scenarios. Stable classifications, funded trades, return and costs match iteration5 exactly: no observed stable economic cost. All four null tapes fully abstain with zero costs and returns. Three of four fresh learnable seeds support all five tiers; the failing seed has inferred support[590,518,0,614,585]. No forced tiers or widened bands.

All frozen hashes match. Artifact audit verifies no funded entries on/after the latch, nonnegative cash, net/PnL reconciliation, one-session matched horizons and both-leg costs (max recomputation error7.3e-11). Modeled per-trade risk remains<=2%; the50% gap probe exceeds modeled loss as expected. Aggregate portfolio and realized gap losses are not capped at2%. Cash is a zero-yield control; no SGOV data or alpha claim.

## Process and limitations

preregister.json predates all runs. Design seeds620101/620102 and already-viewed paired tapes are separate from final seeds. commitment.json records core, reference dependency, test, runner and preregistration hashes before OS-entropy seeds/switch dates were drawn. Random switches are drawn uniformly from626–686; neither policy sees the switch. Source-freeze is local, without a trusted public timestamp. The post-run analyze.py only reads evidence and writes documentation/audits; it executes no portfolios and is separately checksummed.

Zero alarms on four independent seeds gives a52.7% one-sided95% upper seed alarm probability; paired scenarios do not increase independent seed count. The observed false-alarm criterion passes, but a population<=5% claim is unsupported. Fresh tapes validate this synthetic engineering change, not real PIT predictors or production readiness. The inherited five-tier support failure remains. Available PIT information supports faster detection after outcomes accrue; it cannot support risk-free immediate recognition.

## Artifacts and commands

report.json contains explicit PASS/FAIL for every preregistered check. confusion.csv includes UNKNOWN and individual-latent truth; portfolio.csv contains all return/CAGR/MDD/cost/risk metrics. detection.csv, economic_paired.csv, audit.csv, opportunities.jsonl.gz and replays.jsonl.gz provide timestamps, all-opportunity outcomes and actual funded ledgers. checksums.json covers artifacts.

Run `python3 analyze.py` in this directory to re-audit archived results without portfolios. `python3 run.py` refuses reuse after commitment. Tests are in test_engine.py; rerunning them executes three additional portfolios outside the archived59 and must not be presented as part of this frozen experiment.

**Next blocker:** obtain enough independent fit/calibration evidence for the missing middle tier, and independently validate residual exposure and false-alarm rates before any promotion. Do not tune these evaluated final seeds.
