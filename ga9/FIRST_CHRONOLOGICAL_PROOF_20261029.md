# First bounded chronological proof — 2026-10-29

Implemented `first_replay.py`: deterministic sorted ingestion of three recovery batches,
SHA-256 verification of response bytes against both request ledger and recovered row,
OHLCV comparison to the original vendor response, symbol/feed/adjustment/session checks,
conflict rejection, and immutable lineage digests. Raw evidence remains quarantined.
The derived evidence manifest retains every input response and batch digest.

Reconciliation: 5,506 original gaps = 4,498 raw recovered + five invalid XLNX
expectations + 1,003 unresolved GOOGL gaps. Corrected expected gap denominator is
5,501. No AMD substitution, fill-forward, invented action zeros or membership.
`nasdaq_archive.py` now excludes sessions after documented XLNX last trade from
retrospective coverage accounting only. The notice's unknown update knowledge time
still prohibits using it as historical trading authorization. Original artifacts
are preserved; corrected audit is in `artifacts/coverage_corrected_20261029`.

Actual smoke: `artifacts/first_chronological_proof_20261029/replay.json` records six
observed peer sessions, January 3–10, 2022. Existing daily_screen, fixed Gene scoring,
portfolio selection and replay accounting ran with an explicitly empty admitted
universe. Five close decisions are NO_TRADE; five subsequent open stages have zero
orders/fills; all six NAV marks are $100,000, MDD zero. The last session is mark-only,
consistent with existing execution semantics. There is no fitted chromosome or
trading result. Empty-universe screening does not validate nonempty market features.

QQQ is frozen as primary, but no local QQQ file was found under /tmp or /opt/mts.
No QQQ benchmark, excess return, or full real trading end-to-end replay is claimed.
The peer-session sequence is observed historical data, not an independently
certified exchange calendar. No download or long evolution was attempted.

Admission blockers: the supplied snapshots have no certified starting roster,
complete event chain, known_at and stable IDs. Selected annual addition notices
alone do not establish a continuously eligible, identity-resolved interval.
Recovered raw bars lack reconciled action/adjustment and availability evidence.
GOOGL and other unresolved identities and membership remain quarantined. The
archive admission gate remains closed.

Next milestone needs one source-backed stable-ID membership interval with a
verified knowledge timestamp, reconciled price/actions including warmup and next
open, an independent session calendar, and matching QQQ OHLC/actions. Estimated
engineering time after those inputs are locally available: 2–4 hours for a short
nonempty replay and targeted verification. Evidence acquisition has no defensible
ETA. Current bounded proof completes in seconds.

GA8 files and processes were not modified or controlled. Host GA8 liveness cannot
be verified from this sandbox's isolated process view; no restart was attempted.

Reproduce the proof in a fresh output directory:

```bash
/opt/mts/.venv/bin/python -m ga9.first_replay \
  --gaps ga9/artifacts/nasdaq_archive_audit_final_20261029/missing_projected_bars.csv \
  --batch ga9/artifacts/alpaca_stock_recovery_batch_20261029 \
  --batch ga9/artifacts/alpaca_stock_recovery_second_20261029 \
  --batch ga9/artifacts/identity_retrieval_host_20261029 \
  --output ga9/artifacts/NEW_CHRONOLOGICAL_PROOF
```

Validation: 58 targeted tests passed; after coverage correction, nine relevant
archive/ingestion/replay tests passed again. Actual corrected archive smoke
asserted 5,501 gaps and zero post-last-trade XLNX expectations.
