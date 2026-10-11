# 13-window GA — Crash-exclusion governance amendment

User-approved change: supersedes the 2026-10-10 Alpha Discovery Scope instruction to preserve crash-era observations in fitness evaluation. Retain raw DEV80 source records unchanged; apply an **evaluation-time** horizon-specific exclusion, not source deletion.

- Reuse GA4 Normal's frozen retrospective episode set from `Research/Protocols/MTS_REENTRY_THREE_HYPOTHESIS_TEST_FREEZE_20261004.json` and `Core/layered_ga/ga4_oracle_crash_mask.py`.
- For every horizon 2–65, exclude any entry-to-exit execution path intersecting an inclusive crash interval (peak+10 trading sessions through trough+10 trading sessions). Never stitch across excluded sessions.
- The 13-window GA must use its own fresh population, independent fitness, and restored GA4 selection mechanism. Crash-specific discovery is reserved for a separate GA Crash study.
- This is a **retrospective oracle research mask**, not a causal real-time crash detector. Report this limitation prominently and do not claim live-tradable performance from oracle-masked results.
- No access to DEV37, preserved DEV50, or BLIND17 during design; no automatic heldout evaluation.
- Fail closed if the episode file, calendar, or mask coverage cannot be validated. Scientific certification remains required before launch.
