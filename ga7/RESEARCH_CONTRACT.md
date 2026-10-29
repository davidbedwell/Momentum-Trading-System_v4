# GA7 autonomous research pipeline

This branch is the source of truth. The GA6 production portfolio evaluator is the reference implementation; GA7 research must **not** silently substitute its simplified experimental evaluator for a parity-certified GA6 engine.

## Execution contract

1. Freeze and hash the DEV79 feature parquet, defense tape, policy JSON, and GA7 source revision.
2. Derive deterministic sector-balanced DEV24, DEV32, and DEV40 subsets from the 79 stock identities; record the exact symbols and selection algorithm. Selection must not use future return performance.
3. Benchmark **the same** 300 chromosomes over the same historical window on all three subsets. Verify portfolio/accounting parity with the GA6 reference before accepting speed results.
4. Select the smallest subset with adequate sector and opportunity coverage. DEV32 is the provisional default, not an unconditional choice.
5. Evolve 300 chromosomes for 1,000 generations with eight workers, checkpointing, and an append-only results ledger. No early stop or silent component removal.
6. Evaluate selected chromosomes on the excluded tickers and full DEV79, reporting results separately. These are transport checks, not pristine out-of-sample evidence.
7. Produce a final machine-readable JSON report and human-readable Markdown report with run metadata, hashes, wall time, throughput, trade counts, EV, MAE, CAGR, MDD, Calmar, per-family results, and policy coverage.
8. Fail closed if data, earnings embargo, PIT membership, corporate actions, or defense inputs are incomplete. Do not report a certified study after a failed prerequisite.

## Execution policy

The server must run the complete DAG unattended, including report generation and backups, and must resume from validated checkpoints after reboot. Chat messages are not part of the run control plane. Never modify frozen GA6-v3 research artifacts.

## Current blockers

The standalone `ga7/runner.py` is an **uncertified prototype**. It does not yet implement complete GA6-equivalent execution, optimized replay, rolling correlation limits, corporate action handling, or a complete autonomous benchmark-to-report DAG. Do not start the 1,000-generation experiment until these are implemented and tested.

Hetzner GitHub SSH authentication was unavailable when checked. Deployment must use an authorized read-only checkout method or an authenticated transport without placing tokens in logs.
