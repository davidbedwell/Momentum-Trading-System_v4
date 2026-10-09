# SHORT borrow policy — USER APPROVED, FROZEN 2026-10-09

- Model **6.00% annualized stock-borrow fee** for every eligible SHORT position, accrued for actual calendar days outstanding using the broker's 360-day fee convention. Apply to the broker-defined borrow collateral value when available; do not silently equate it to proceeds if collateral differs.
- **6.00% is the maximum acceptable quoted borrow rate for execution.** Reject a SHORT entry when the actual broker borrow quote exceeds 6.00%, when shares are unavailable to borrow, or when availability/rate cannot be verified at order time. Do not open and assume a 6% rate without a quote.
- Rates below 6% (including 0% or 3%) are execution upside relative to the conservative 6% research model; do not tune search to lower rates.
- If the broker reprices an existing borrow above 6%, flag it immediately for exit/risk handling; do not pretend the position can always be closed before an overnight rate change. Model actual incurred charges and forced buy-ins. This freeze is not a guarantee of a capped realized borrow fee.
- Borrow cost is distinct from margin-debit interest, regulatory charges, execution spread/slippage, dividend substitutes, and margin/capital requirements. Continue to model those separately.
- Historical borrow availability and quotes are not present in the current DEV80 research arrays. Until verified, all backtests using 6% are *conditional executable proxies*, not certified historically executable returns. No Gen2 authorization or scientific certification is implied.
- Supersedes the 0/3/6/15/30 percent SHORT borrow sensitivity scenarios in the SHORT discovery preregistration draft for the **primary** study. Use 6% alone for SHORT borrow-fee modeling, with actual broker eligibility gate at execution.
