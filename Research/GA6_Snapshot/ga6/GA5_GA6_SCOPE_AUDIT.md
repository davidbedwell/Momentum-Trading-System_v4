# GA5 → GA6 scope audit (2026-10-21)

## Verified inherited infrastructure
- Data ingestion and prepared sessions: GA5 PreparedSessions.
- PIT membership, risk veto, earnings embargo: GA5 policies and existing decision modules.
- Next-session open fills, settlement, corporate actions, portfolio NAV: existing ledger modules reused in GA6 guarded evaluator.
- Parallel execution, evaluation cache, checkpoints with fingerprint, RNG resume, stagnation stop: GA5 runner inherited.
- DEV79 feature and niche-label data reused unchanged.

## Actual GA6-specific differences
- GA6 EV-led fitness; positive EV and positive geometric log EV remain original research criteria.
- 13-niche evidence reporting and independent niche ranks.
- Cross-niche breeding with niche quotas.
- Unrestricted entry mode (niche labels used for research evidence, not entry restriction).
- Optional extra exit/reentry and policy diagnostics, some of which are not required to run GA6 discovery.

## Verified tests
- 26 population, 2 generations, 52 evaluations, 13 niches, checkpoint validation and resume: PASS (`runs/automated_recovery_v1/automation_status.json`).

## Outstanding and distinctions
- GA6 production 500-pop runtime/throughput not benchmarked. No claim of production certification.
- GA6 guarded evaluator duplicates GA5 evaluator code; verify any deviations and prefer GA5 implementation where behavior matches.
- Extra policy-evolution diagnostics currently run during each evaluation, adding cost; benchmark impact before deciding whether to disable or move them to post-discovery (do not change scientific features silently).
- Production conveyor remains BLOCKED because it contains placeholder PENDING_* gates. This is a conveyor design error, not evidence that all those capabilities are absent from GA5.
- Current GA6 research reports explicitly label historical niche outcomes retrospective, not OOS certification.

## Recommended minimal path
1. Use existing GA5 preflight and portfolio accounting tests rather than rebuilding.
2. Run parity tests between GA5 and GA6 guarded evaluator on the same chromosome/input.
3. Run a small 500-pop benchmark and confirm checkpoint/restart at production size.
4. Replace placeholder conveyor gates with actual executable checks; only then launch production research automatically.
