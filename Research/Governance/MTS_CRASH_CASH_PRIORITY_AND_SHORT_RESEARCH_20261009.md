# Crash defense: cash-first policy and SHORT research separation

Status: USER-APPROVED PREFERENCE, 2026-10-09. Applies to future implementation and study design; not evidence of a deployed controller.

- When the pre-existing point-in-time A/B/C crash-defense detector triggers, MTS's default risk response is to liquidate equity exposure according to executable risk controls and transition to cash or cash-equivalent holdings. Do not automatically open SHORT positions to express the crash signal.
- Crash defense is capital preservation, not an obligation to seek SHORT alpha. Prioritize exit feasibility, slippage, gap risk, and prevention of new equity exposure while the defensive gate is active.
- Keep independent SHORT opportunity discovery separate from A/B/C crash protection. SHORT signals may be researched across Normal and Defensive market episodes without making crash status a necessary condition for discovery.
- Do not allow the SHORT research engine to override the crash cash-first default. Any future permission for opportunistic SHORT execution during Defensive requires a separate explicit policy decision and tests; it is not granted here.
- Retain the approved 6% annualized SHORT borrow assumption and reject actual quotes above 6% or unavailable borrow. Keep scientific protections and Gen2 parent certification gates unchanged.
- Existing recovery R-1 rules remain in force for resuming Normal operation. Do not redefine A/B/C or R-1 thresholds without explicit approval.
- Research comparisons should report cash/T-bill baseline alongside hypothetical SHORT outcomes, with actual historical rates where available. Do not treat hypothetical SHORT profits as realized Defensive strategy returns.
