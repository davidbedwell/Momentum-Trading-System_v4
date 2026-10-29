# Defensive Anti-Overfit Method Tournament — DEV50 Finding
Date: 2026-10-05

The frozen post-hoc tournament produced a negative but decisive result: date aggregation, cluster weighting, stock-fold slicing, and episode slicing of chromosomes already evolved on all DEV50 do not adequately diagnose overfit.

PF2 and PF3, which later failed 50+17 transport, remain positive in all five DEV50 stock folds and all six DEV50 bear episodes. PF2 worst stock-fold selected-event mean is +4.11% and worst episode mean +2.43%; PF3 worst fold +3.61% and worst episode +2.20%. A post-hoc validation architecture would therefore have falsely endorsed them.

This does not falsify cross-validation. It demonstrates that the folds must exist during model selection. Once a chromosome has been evolved on all DEV50, evaluating that same chromosome on subsets of DEV50 is not held-out validation.

Required redesign:
1. True stock nested discovery: for each deterministic DEV50 stock fold, evolve chromosomes using only the other four folds, then evaluate frozen fold-specific winners on the omitted fold.
2. True episode nested discovery: for each bear episode, evolve using the other five episodes, then evaluate on the omitted episode.
3. Same-date/market-cluster weighting must be applied inside training fitness so correlated ticker events cannot multiply selection credit.
4. Candidate selection and GA selection are both optimization layers and must be treated as such.
5. A production candidate must be supported by repeated independently-trained folds, not merely one pooled DEV50 GA.
6. preserved50 remains the verification stage and TEST17 the subsequent test stage after architecture and acceptance rules are frozen. Because both have already been observed in prior research, neither is statistically pristine for the redesigned methodology and must be labeled accordingly.
7. No remaining Discovery or Verification A/B is accessed during redesign.

Determination: select true nested hierarchical validation for the next methodology. Do not select a simple synthetic ticker or post-hoc fold method as sufficient.
