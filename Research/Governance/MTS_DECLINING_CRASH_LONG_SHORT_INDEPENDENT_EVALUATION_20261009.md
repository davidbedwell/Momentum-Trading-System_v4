# Declining/crash markets: independent LONG and SHORT opportunity evaluation

Status: USER CLARIFICATION APPROVED, 2026-10-09. Clarifies MTS_CRASH_CASH_FIRST_INDEPENDENT_REENTRY_AMENDMENT_20261009.md.

- A/B/C crash detection first triggers a risk-managed transition toward cash. Cancel conflicting entries and initiate liquidation; do not assume immediate fills.
- Continue discovering both LONG and SHORT candidates during declining markets and crash episodes. Neither direction is excluded simply because the market is declining, nor is either direction automatically qualified because of it.
- Independently evaluate every candidate against point-in-time entry conditions, net EV, statistical robustness, liquidity/execution feasibility, downside/tail risk, correlation/portfolio exposure, and the relevant market state. SHORTs additionally require borrow availability and actual quoted annual borrow fee <= 6%, with 6% modeled for research.
- Only a separately validated, explicitly authorized Defensive strategy can initiate trades while the crash/Defensive gate is active. Independent evaluation is not an automatic trade authorization; cash remains the default when no candidate qualifies.
- R-1 governs restoration of ordinary Normal trading. Do not change A/B/C or R-1 triggers or protected research banks under this clarification.
- This is governance documentation only; no assertion of controller implementation or tests.
