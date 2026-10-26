# GA7 engineering status — not production certified

The research branch now includes a C-contiguous daily market-array builder, a Numba signal scanner, a Numba chronological portfolio research kernel, persistent evaluation caching in the legacy Python runner, persistent worker pool, generation checkpoints, and a reproducible compiled benchmark entrypoint.

**Do not equate existence with production completion.** The legacy runner does not call the compiled portfolio kernel. The compiled kernel does not implement all GA6 execution semantics (dynamic scale-ins, correlation cap, intraday hard-stop fills, full corporate-action conventions, GA6 defense transition parity, or exit-rule grammar). The GA6 policy's historical membership entries are all true and lack independent PIT provenance certification. The benchmark is research-only and may fail closed on splits.

## Release gates

- [ ] Confirm GitHub Actions passes all tests, including compiled portfolio tests.
- [ ] Verify corporate-action adjustment conventions against source data and GA6 accounting; implement validated split/dividend handling.
- [ ] Port complete GA6 execution semantics into compiled path; demonstrate identical fill ledger and daily NAV for deterministic cases.
- [ ] Make chronological evaluation consume the same frozen arrays without reloading parquet per worker.
- [ ] Integrate compiled evaluation with evolutionary runner and persistent cache, with input/code/policy hash keys.
- [ ] Implement atomic generation results and checkpoint transactions; restart after injected crashes and prove no duplicate evaluations.
- [ ] Add independent PIT provenance and earnings-policy coverage audit.
- [ ] Measure cold-JIT and warmed throughput on the actual target server, then compute ETA.
- [ ] Implement and validate the complete unattended benchmark/evolution/transport/final-report DAG.
- [ ] Only after passing all gates, deploy and start full research.

The user explicitly requested GitHub-first engineering. Do not deploy this branch to Hetzner as production until these gates pass.
