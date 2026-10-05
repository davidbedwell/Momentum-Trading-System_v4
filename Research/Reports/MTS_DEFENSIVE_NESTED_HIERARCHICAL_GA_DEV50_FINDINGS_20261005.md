# MTS Defensive Nested Hierarchical GA — DEV50 Findings
Date: 2026-10-05

## Governance
Completed true nested DEV50 discovery under the frozen redesign. Each of five stock folds was excluded during its GA evolution. Each of six bear episodes was separately excluded during its GA evolution. Feature quantile thresholds were recomputed from training events only and applied unchanged to the heldout group. Same-date selected events were aggregated in training fitness so ticker multiplicity did not directly multiply success credit.

preserved50 was not accessed. TEST17 was not accessed. Remaining Discovery and Verification A/B were not accessed.

## Result
The nested architecture successfully exposed severe non-portability before verification.

### Stock outer folds
All five heldout stock folds had positive selected-event means, but support was sparse:
- fold 0: 9 events; date-weighted mean +5.27%; exact-MTM CAGR +1.90%; MDD -2.01%
- fold 1: 2 events; +2.33%; CAGR +0.27%; MDD -0.94%
- fold 2: 9 events; +5.16%; CAGR +2.45%; MDD -6.78%
- fold 3: 13 events; +4.85%; CAGR +2.87%; MDD -1.84%
- fold 4: 10 events; +6.42%; CAGR +3.17%; MDD -7.45%

These are not adequate evidence of a portable strategy because independently trained winners rarely activate in omitted stocks.

### Bear-episode outer folds
Transport failure is decisive:
- GFC omitted during training: 35 heldout events; selected-date mean +3.02%, but exact-MTM CAGR -9.96% and max DD -41.01%.
- 2011 omitted: 0 heldout events.
- 2015–16 omitted: 0 heldout events.
- 2018 omitted: 0 heldout events.
- COVID omitted: 0 heldout events.
- 2022 omitted: 13 heldout events; selected-date mean +6.52%; exact-MTM CAGR +3.60%; MDD -3.23%.

Four of six omitted bears generated no qualifying trade at all. One transported destructively (GFC), and one transported positively (2022).

## Mechanism stability
The independently evolved fold winners do not converge on one stable mechanism. Family masks, horizons, and entry conditions vary materially across folds. Examples include breakout/volatility breadth rules, volume/liquidity drawdown rules, mean-reversion/volatility breadth rules, VIX/VVIX rules, OFR funding rules, and market-structure return rules.

This lack of recurrence is itself evidence that the search space is flexible enough to fit the available bear environments in multiple incompatible ways.

## Determination
FAIL TO ADVANCE TO preserved50.

The nested experiment demonstrates that:
1. pooled DEV50 fitness materially overstated generalization;
2. correlation adjustment alone was insufficient;
3. true holdout-during-evolution correctly reveals regime-specific overfit;
4. current search space / selection pressure is too flexible relative to six independent bear environments;
5. sparse heldout activation is a serious portability failure, not a success;
6. preserved50 and TEST17 must remain untouched for this redesign.

## Next scientific design implication
Do not simply increase GA population/generations or relax heldout requirements. The next design must reduce effective model flexibility and require mechanism recurrence across independently trained folds. Candidate families/conditions that recur across multiple outer folds can be studied as mechanism-level hypotheses, but the heldout outcomes must not be used to tune their numeric thresholds. A future pooled finalist should only be created after a predeclared recurrence/stability rule is frozen.
