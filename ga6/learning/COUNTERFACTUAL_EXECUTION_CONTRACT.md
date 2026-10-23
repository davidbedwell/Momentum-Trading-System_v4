# GA6-v3 counterfactual execution contract

## Objective
For every decision date, evaluate the selected chromosome and all relevant eligible alternatives using the **same frozen GA6 execution semantics**. Preserve the original 400-chromosome bank and frozen defense. This is GA6-v3, not GA6-H.

## Non-negotiable parity
- Decision at time t; order fills no earlier than the next executable open.
- Preserve ENTER, HOLD, SCALE_IN, SCALE_OUT, EXIT, REPLACE_CANDIDATE and mandatory risk exits.
- Preserve 40-session maximum holding period, point-in-time membership, earnings embargo, frozen defense, settlement, fees, corporate actions, cash yield and cash availability.
- Shadow chromosomes have independent simulated capital; actual selector trades compete for one shared $100,000 portfolio.
- No retrospective niche fitting, future sector information, or same-day matured outcomes in selector features.
- Do not silently substitute a simplified single-symbol replay for the reference settled-ledger evaluator.

## Required immutable event records
Each event must carry: run ID, chromosome ID, symbol, decision date, execution date (if filled), order/decision ID, event type, position ID, intended action, executed action, quantity, price, fee, cash before/after, inventory before/after, equity reference, policy rejections, regime, niche, point-in-time feature snapshot and evidence cutoff. Record exit reason, realized net PnL, capital usage and holding sessions at completion.

## Post-trade audit
Compare only candidates eligible at the original decision date, using the same opportunity definition and comparable capital/risk constraints. A shadow trade must be fully completed before its outcome can enter the learning bank. Record selection, regime, niche, entry, scaling, exit and risk differences. Distinguish descriptive hindsight regret from proven causal attribution.

## Certification gates
1. Instrumentation produces identical aggregate NAV, fills, realized PnL, scaling counts and risk outcomes as the unmodified frozen evaluator.
2. Event-ledger reconciliation matches settled-ledger inventory, cash and fees.
3. Chronological cutoff tests exclude same-day and future labels.
4. Independent shadow portfolios reconcile to their own reference runs.
5. Adaptive selector beats or robustly matches a frozen selector out of sample; report failure honestly.

## Suspension
Defer until sufficient context-specific evidence. Suspended chromosomes remain preserved and eligible for periodic reevaluation/reactivation; rare niches must not be discarded based on overall rank.
