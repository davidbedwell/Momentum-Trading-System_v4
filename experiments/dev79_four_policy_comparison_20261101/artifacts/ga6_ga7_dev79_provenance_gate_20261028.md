# GA6/GA7 DEV79 historical input certification gate (2026-10-28)

**Result: BLOCKED — no historical PIT certification.** This is a read-only source audit, not a trading replay.

- 179,265 membership records over 2,516 sessions and 77 symbols in 2009–2018. **All 179,265 are True**; no false membership rows. The policy builder explicitly sets membership from observed price bars, not an independent historical index roster.
- 8,623 retrospective earnings-blocked symbol/session entries; the EODHD report-date archive does not certify when announcements became knowable.
- Niche model manifest status: `CHRONOLOGY_VERIFIED_FEATURE_PROVENANCE_PENDING`; chronological reconstruction passed but underlying feature provenance remains pending.
- Historical sector map is retrospective and static; dividend payment dates and true historical cash rates remain unverified.
- Policy checksum matches its existing assumptions manifest.

These issues are already disclosed in the original exploratory input manifest. The current audit verifies their continued presence. They are **not new evidence that the GA7 replay failed**. A common-execution replay can be research-comparable but cannot be called historically certified until independently timestamped membership, earnings, sector, corporate-action and feature evidence is supplied. DEV87 was not read.
