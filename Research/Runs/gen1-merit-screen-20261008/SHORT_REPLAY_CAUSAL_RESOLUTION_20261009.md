# Gen1 causal replay resolution — 2026-10-09

Root cause: replay mistakenly used VectorSignalCompiler, whose feature quantile is estimated from the full DEV80 panel. The original Gen1 results use CausalSignalCompiler, whose threshold is calculated from observations strictly preceding the decision date. This is a material point-in-time distinction, not a transaction-cost or data-file problem.

Validation: replayed candidate IDs 1 SHORT, 5 SHORT, 6 LONG, 2733 SHORT at horizons 1, 3, 7, 20, 63. All 20 comparisons reproduced archived n, effective_n and EV_net exactly (zero differences). Candidate 2733 includes positive SHORT EV at horizons 3 and 7.

Validated only this smoke sample, not all 4,360 candidates or all 23 horizons. Do not claim full archive certification or environment-effectiveness findings yet. Protected DEV37, DEV50, BLIND17 untouched.

Reproduction script: scripts/validate_gen1_causal_replay_20261009.py
