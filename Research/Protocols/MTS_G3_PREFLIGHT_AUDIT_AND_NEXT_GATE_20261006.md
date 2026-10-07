# MTS G3 — Preflight Audit and Next Gate
Date: 2026-10-06
Status: DESIGN/PREFLIGHT — NO PRODUCTION COMPUTE AUTHORIZED

## Findings
1. G3 is isolated from the live G2 tree in a separate worktree/branch.
2. G2 already exposes a broad causal-in-time primitive bank across stock, market, and sector context. G3 should audit/reuse primitives rather than create a gratuitous new indicator zoo.
3. Existing G2 stock primitives include returns across horizons, residual momentum, high/low distance, Donchian, MA geometry, realized/idiosyncratic volatility, beta, positive-day fraction, failed rebounds, skew, dollar volume, Amihud, overnight/intraday, relative volume, RSI, pullback, range expansion, market-relative returns, and PIT earnings-event fields.
4. Market primitives include SPY return/DD/vol, breadth levels/deltas, sector participation, leadership change, dispersion, pair correlation, rebound/trough geometry, VIX/VVIX, OFR FSI, funding/credit, T-bill, and yield-curve context.
5. Sector primitives include peer return/volatility/participation/relative-strength context.
6. A recovered PIT earnings registry now exists for DEV117:
   - 117 tickers;
   - 2006-01-06 through 2026-09-14;
   - 8,989 aligned event-session rows;
   - source: recovered EODHD raw acquisition cache;
   - unknown timing policy: conservative next observed session close;
   - audit passed;
   - SHA256 eb9c997df50af4ca1f17164ba50f9fb314ed6e8907fc0d7a4b98e51ad38f6194.
7. This earnings registry is DEV117-only. It does NOT establish PIT earnings coverage for the 503-stock universe or protected banks.
8. Historical research records show the original 67-stock Discovery laboratory and the 50-stock heldout cohort have been consumed/exposed. The 50 is preserved, not pristine, and remains unavailable for G3 design/tuning.
9. Historical protocols repeatedly identify 186 remaining Discovery tickers plus Verification A/B as protected. Exact current ticker-level contamination must be reconstructed before assigning G3 validation partitions.
10. Existing Oct 1-6 protocols are extensive enough that contamination cannot safely be inferred from labels alone. A machine-readable evidence ledger is required.

## Immediate recommendation
Proceed with G3 Stage 0 only:
A. build machine-readable primitive manifest;
B. build machine-readable contamination ledger from protocols/manifests/results;
C. build G3 genome-grammar candidate using causal primitives but without G2 family labels as evolutionary targets;
D. build null specification and synthetic planted-signal conformance harness;
E. build archive/search-ledger schemas;
F. write tests enforcing portfolio-metric blindness and protected-data barriers.

These are engineering/conformance tasks, not production evolutionary search.

## Do not do yet
- Do not open remaining 186 Discovery, Verification A, Verification B, DEV50, or BLIND17 outcomes.
- Do not allocate final G3 train/transport/blind banks until contamination ledger is complete.
- Do not launch G3 GA/QD.
- Do not launch Thunder or another Nebius instance.
- Do not use portfolio CAGR/MDD to select specialist organisms.
- Do not assume DEV117 fundamentals generalize to other banks.

## Decision gate for user
No additional machine is needed now.

Next user action is only required when:
1. the contamination ledger reveals which genuinely protected evidence can be assigned to G3;
2. Stage-1 synthetic/null smoke tests are ready to benchmark;
3. a measured compute estimate exists.

At that point, user chooses whether to run the pilot on Thunder, current Nebius after G2/H7 completes, or a fresh 64-core instance.
