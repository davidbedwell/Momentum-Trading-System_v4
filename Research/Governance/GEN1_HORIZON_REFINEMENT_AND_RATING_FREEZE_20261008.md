# Frozen Generation 1 Horizon Refinement and Rating Governance — 2026-10-08

Status: FROZEN BY USER DIRECTION. This document governs the current horizon-refinement research and subsequent rating-system design. Do not silently revise.

## Discovery and preservation
- Preserve all 4,360 original Generation 1 candidates, their nine original horizon measurements, and the original screening criterion unchanged.
- Original preliminary eligibility: net expected value (EV_net) > 0 on at least one evaluated horizon. This is NOT scientific certification or promotion.
- No fixed survivor count. Do not discard nine-horizon failures before estimating false-negative rates through refinement.
- DEV80 discovery only. DEV37, DEV50, BLIND17 remain protected under their existing governance. No reproduction or Generation 2 before refinement and certification gates.

## Horizon refinement
- Phase A: evaluate additional horizons 4,6,8,9,12,18,25,30,35,40,45,50,55,60 for every candidate, alongside original 1,2,3,5,7,10,15,20,63.
- Phase B: engineer and validate outcomes beyond 63 through 126 sessions before evaluation; preserve original results and comparable execution/cost conventions.
- Phase C: fine-grained neighboring horizons around positive regions and sign transitions; prespecified sampling of initial failures to quantify missed opportunities.
- Phase D: robustness and market-exposure audit before any promotion.

## Apples-to-apples diagnostics
- Report candidate absolute EV_net and matched passive EV_net using identical signal/decision dates, direction, holding horizon, and consistent transaction-cost assumptions. The matched reference is an equal-weight same-date same-sector eligible DEV80 basket; disclose differences in trade construction, cost model, or coverage.
- Report excess EV_net = candidate net EV minus matched passive net EV on exactly matched observations; record matched sample counts and missingness.
- Passive/excess EV is diagnostic only at this stage: not an eligibility threshold, tuning objective, or elimination rule. Separate predictive-edge certification comes later.
- Evaluate LONG and SHORT separately, including short borrowing and cash/collateral assumptions as appropriate. Do not silently treat short passive comparison as equivalent to long buy-and-hold.

## MAE and risk
- Measure and retain average MAE and worst-5% tail MAE for each candidate and horizon NOW, together with EV_net, observation counts, and where available MFE.
- Do NOT optimize for, rank by, gate, or eliminate on MAE during current refinement.
- Compare MAE across matched holding horizons, not raw 5-day versus 63-day excursions without adjustment.

## Subsequent rating and screening DESIGN (not yet calibrated)
1. Eligibility: economic viability, sufficient independent observations, valid execution/cost assumptions, and identifiable profitable holding interval. Thresholds beyond original EV_net criterion must be specified and frozen before application.
2. Quality: statistical robustness, EV magnitude, average and tail MAE relative to reward, horizon stability, market-regime behavior, sample size, and trade frequency. Matched passive excess EV remains a separately reported diagnostic until independently approved as a gate.
3. Diversity: retain distinct family combinations, side, horizon, and trading behavior; identify near duplicates. No arbitrary survivor quota.
- Initially use multiple dimensions and Pareto comparisons rather than an arbitrary single weighted score. Freeze exact definitions, thresholds, and tests BEFORE applying new selection rules; independent validation required for generalization claims.
- No changes to current running Phase A evaluation or promotion decisions based on these later design criteria.
