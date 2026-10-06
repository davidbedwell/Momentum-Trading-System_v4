# MTS CLEAN ENGINE ADVERSARIAL AUDIT — 2026-10-06

Status: COMPLETE FOR AVAILABLE INPUTS

Adversarial attacks executed:
1. Blind37 values mutated to extreme values; Train80 rank/peer state unchanged.
2. Future prices randomized after T; prior features/decisions unchanged across 200 real dates.
3. Ticker order/renaming permutation; equivalent feature decisions preserved.
4. Weak absolute opportunities; capital remains predominantly SAFE.
5. Hand replacement where direct incumbent→challenger clears while separate SAFE legs do not; REPLACE succeeds.
6. Hand replacement below hurdle; REPLACE blocked.
7. 60%→30% partial resize; exact bounded movement.
8. Position historical age changed/omitted; decision invariant.
9. 1,000 randomized genomes; gross exposure never exceeds one.
10. Worker-count 1 vs 4; deterministic final populations.
11. Generation-10 checkpoint resume to generation 12; bit-identical with uninterrupted run.
12. Landlock Train80 worker; known Blind37 parquet read denied by kernel.
13. Real Fold0 dynamic-peer validity against randomized peers and window perturbation.
14. SPY comparator independently checked against Nasdaq for 20 returns; DEV117 equal-weight alias rejected.

Adversarial finding during rebuild:
- Initial fresh ledger ordering allowed SAFE-funded challenger entries to consume replacement deficit before a legitimate direct REPLACE. The test failed; implementation was fixed, test unchanged.
- Initial clean allocation implementation simplified Claude F.2 equal-mode semantics and friction representation. Re-reading the controlling architecture caught this before integration; literal F.2 and E.4 modules replaced it.

Remaining non-engineering blocker:
- mandatory historical PIT earnings stream absent from recovered data/environment.
