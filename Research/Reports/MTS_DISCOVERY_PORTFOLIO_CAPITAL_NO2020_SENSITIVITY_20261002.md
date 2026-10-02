# MTS Portfolio-Capital 2020-Exclusion Sensitivity

**Date:** 2026-10-02  
**Status:** Frozen-policy Development sensitivity; no search or retuning. Verification A remainder and Verification B remained sealed.

## Test
Removed all **10,056** Development trades with 2020 signal dates, retaining **77,445** of 87,501 trades. Replayed the already-frozen growth policy `ev_over_risk_p10_loss_floor0.5_cap2.0` using unchanged score scale **3.243424867981**, floor **0.5x**, cap **2.0x**. 2020 was excluded from portfolio evaluation only; causal histories/scores for non-2020 trades were not refit.

## Result
- Equal-weight baseline terminal wealth: **12.429x**; frozen sizing: **13.661x** (**+9.91%** relative).
- CAGR-equivalent: **16.79% -> 17.48%** (**+0.68 pp**).
- Max drawdown: **-45.88% -> -42.13%** (improvement **+3.75 pp**).
- Daily CVaR5: **-2.98% -> -2.84%**.
- Return/drawdown: **24.91 -> 30.05**.
- Average gross exposure: **84.97% -> 87.77%**.

## Interpretation
The frozen genome/family EV-to-p10-loss sizing effect does **not** depend on including 2020 in the evaluated Development portfolio. With 2020 removed, it still improves terminal wealth, CAGR-equivalent, max drawdown, CVaR5, and return-to-drawdown versus equal sizing. This is a sensitivity result, not new validation and not authorization for paper/live promotion.
