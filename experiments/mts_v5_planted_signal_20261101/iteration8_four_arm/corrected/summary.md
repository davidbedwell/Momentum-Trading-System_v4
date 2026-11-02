# Corrected fair synthetic experiment

Completed 640 portfolios in 115.9 seconds, one Python process. Five prespecified implementation tests passed. Audit checks: {'cash_nonnegative': True, 'pnl_reconciles': True, 'cost_reconciles': True, 'net_reconciles': True, 'horizon': True, 'no_funding_after_alarm': True, 'committed_hashes_match': True}.

8A-D and 8A-Full use Claude Part II §6 C_ablation exactly. **INVALID as an e-process. No mathematical validity or false-alarm guarantee is claimed for C.** CUSUM is empirically calibrated only.

| Arm | Stable alarm seeds /16 | Delay pass seeds /16 | All primary seed passes /16 | Strict | ≥12/16 | Stable return Δ |
|---|---:|---:|---:|---|---|---:|
| 6 | 0 | 15 | 9 | False | False | 0.00% |
| 7B | 0 | 13 | 8 | False | False | 0.00% |
| 8A-D | 10 | 15 | 2 | False | False | 0.00% |
| 8B-D | 11 | 16 | 4 | False | False | 0.00% |
| 6-600/300 | 0 | 14 | 13 | False | True | 0.00% |
| 7B-600/300 | 0 | 15 | 13 | False | True | 0.00% |
| 8A-Full | 6 | 16 | 10 | False | False | 0.00% |
| 8B-Full | 7 | 16 | 9 | False | False | 0.00% |

Strict and ≥12/16 are separate rules, both include the frozen mean stable-return criterion. The report separately provides descriptive paired t intervals and every endpoint. Stable alarms aggregate learnable, outer_noise and null within each seed. Zero of 16 gives a one-sided 95% upper bound of 17.07%, not ≤5%.

Stage1 uses original 400/200 history; Stage2 uses independent seeds with 600/300 history and diagnostic 6/7B clones. Full candidates share fit_v3. Compare within history; no cross-history detector attribution. No winner selection, production changes, automatic iteration, or real-market claims.

Artifacts: preregister.json; commitment.json; seeds.json; calibration.json; per_seed.jsonl; event_ledger.json; opportunities.jsonl.gz (all per-date/asset labels); replays.jsonl.gz (daily NAV, fills, detector traces); report.json (paired contrasts, exact intervals, criteria and limitations).

Reproduce in a NEW directory preserving relative engine paths: copy code and preregistration, run `python3 run.py` then `python3 analyze.py`. Original run refuses holdout reuse. Seeds and full sources are retained for deterministic audit; new run draws new seeds.

Per-scenario stable alarm counts (learnable / outer_noise / null):
- 6: 0 / 0 / 0
- 7B: 0 / 0 / 0
- 8A-D: 0 / 2 / 9
- 8B-D: 0 / 3 / 9
- 6-600/300: 0 / 0 / 0
- 7B-600/300: 0 / 0 / 0
- 8A-Full: 0 / 2 / 5
- 8B-Full: 0 / 4 / 4

CUSUM calibration used learnable stable tapes only. Its outer_noise/null false alarms show failure to transfer that calibration. Arm C also alarms on those scenarios. See PRIOR_STATUS.md for the preflight and historical holdout audit; verification.json checks all archived records.
