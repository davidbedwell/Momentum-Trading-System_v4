# MTS Discovery Portfolio-Capital Mitigation — Final Audit

**Date:** 2026-10-01  
**Conclusion:** **DISCOVERY CANDIDATE**  
**Survivor:** `ev_over_risk_p10_loss_floor0.5_cap2.0`  
**Status:** Discovery only — **not promoted to paper/live trading**. Verification A remainder and all Verification B remain sealed.

## Executive result
The experiment found one surviving capital-allocation policy: causal genome/family **expected return ÷ p10 loss** sizing, bounded to **0.50×–2.00×** with the Development-frozen score scale `3.243424867981`.

Development non-levered portfolio: baseline **15.823×** wealth, **18.54%** CAGR-equivalent, **-45.73%** max drawdown. Growth nominee: **18.084×**, **19.52%**, **-41.19%**.

Frozen Discovery Holdout: baseline **2.818×** vs nominee **2.961×** (**5.08%** relative improvement); CAGR **23.03% → 24.25%**. Holdout max drawdown was slightly worse, **-16.15% → -16.43%**, and CVaR5 also worsened slightly. Therefore this survives only as a **growth-oriented Discovery candidate**, not a risk-reduction claim.

## Exposure-matched falsification
The Holdout nominee averaged slightly more gross exposure than baseline. An exposure-matched baseline reached **2.878×**, still below the nominee's **2.961×**. The remaining relative wealth advantage is **2.92%**, so the surviving effect is not explained solely by higher average exposure.

## Independent stages
- **Stage 1 — simple sizing:** 24 policies. Simple ATR/realized-vol sizing improved portfolio wealth/drawdown in Development, but failed the frozen breadth gate: negative mean trade contribution, too few positive tickers, and no positive signal families. It did not advance.
- **Stage 2 — genome/family sizing:** 60 policies. Exact genome was used when >=100 prior completed observations existed, otherwise family, then global. Source use: {'family': 40492, 'genome': 45617, 'global': 928, 'unavailable': 464}. The EV÷p10 family produced the robust frontier.
- **Stage 3 — graduated entry:** 51 policies. Best wealth policy `GRAD_ENTRY_init0.75_NO_NEW_LOW_2` reached **15.755×** vs its matched baseline **15.830×**. No candidate advanced.
- **Stage 4 — partial de-risking:** 27 policies. Best wealth policy `DERISK_reduce0.25_REC_LT25_S5` reached **15.637×** vs baseline **15.830×**. No candidate advanced.
- **Stage 5 — combinations:** **0 eligible combinations**. The protocol forbids combining failed components merely to search for a backtest winner.

## Breadth and uncertainty
Growth nominee trade contribution was positive across **47/56 Development tickers**, **13/17 years**, and **6/8 families**. Ticker-cluster bootstrap mean-delta 95% CI: **[0.002149, 0.006827]**, with P(delta>0) **1.000**.

The main stability caution is year concentration: **2020 contributes ~71.1% of net Development improvement** for the growth nominee. Removing 2020 still leaves positive net improvement, and 13/17 years are positive, but this remains a material caveat.

## Drawdown nominee
The Development drawdown nominee `ev_over_risk_p10_loss_floor0.25_cap2.0` looked strong in-sample: wealth **16.095×** and max drawdown **-36.21%**. On frozen Holdout it produced **2.949×**, but max drawdown worsened to **-16.52%** vs baseline **-16.15%**. It **fails its intended drawdown-control role** and is rejected.

## Catastrophic protection
Fixed 8/10/12-ATR and 25/30/40% disaster layers were tested with gap-through fills. For the surviving growth sizing policy, **every catastrophic layer reduced Development terminal wealth and none improved max drawdown versus no catastrophic layer**. No catastrophic layer is nominated.

## Important implementation notes
1. The primary decision uses the strict **non-levered 100% capital-budget** model. The second risk-budget convention is diagnostic only; because borrowing is permitted it reaches extreme gross exposure and is not a deployment recommendation.
2. Stages 3–4 use a more explicit open-aware transaction simulator. Its baseline differs from the Stage 1–2 baseline by ~0.05%; all Stage 3–4 comparisons are internal to the matched simulator, and no Stage 3–4 policy advanced.
3. Missing causal risk estimates are assigned neutral **1.0×** sizing. No future median proxy is used.
4. The prior dynamic-stop null has separate protocol-compliance caveats and is treated only as motivation, not as evidence required for this result.

## Scientific interpretation
The useful relationship is **not simply “lower volatility gets more capital.”** The strongest result allocates capital according to what a causally supported genome/family has historically earned **relative to its downside tail**. This directly supports continued research into whether the current genes/genomes can be improved as representations of conditional reward/risk.

## Governance status
- Discovery Holdout replayed once after nominee freeze.
- No Holdout retuning.
- Verification A remainder: **not accessed**.
- Verification B: **not accessed**.
- No paper/live promotion.
- Full candidate manifests and source artifact hashes are preserved in the companion JSON audit.
