# Outcome interpretation

8B-Cal FAILS the frozen conjunctive rule. Outer_noise paired return improvement vs original8B: 7.6264% points; descriptive paired t95 [-1.6435%, 16.8964%] points. This is synthetic, with n24 and no multiplicity adjustment.

Fixed reversal mean post3 false GREAT rises from0.375 to1.0833 per seed; random reversal remains0.0833. Mean first3 false GREAT is14.1667 and13.9167 respectively for every arm, reflecting the outcome availability delay. Candidate maximum adverse MDD is2.95% fixed and2.38% random reversal.

3-session detection is22/24 fixed and23/24 random for both original8B and8B-Cal. Identical3-session rates do not imply identical later delays: see every seed in summary.md. Stable false alarms (learnable/outer_noise/null) are0/0/0 for6 and7B,0/3/9 for original8B,0/0/1 for8B-Cal. Reversal prechange alarms are separately explicit in the event ledger.

Even zero alarms among24 independent seeds permits a one-sided95% upper population rate of11.73%; one observed null alarm is not evidence of a<=5% population bound. Calibration/tapes and repeated scenarios within a seed do not increase the independent holdout sample count.

Seven unit tests and the independent artifact audit passed. Source and threshold hashes match commitments. No production files were edited by this experiment; no GA, deployment, or monitoring was started. No candidate revision follows this failure.
