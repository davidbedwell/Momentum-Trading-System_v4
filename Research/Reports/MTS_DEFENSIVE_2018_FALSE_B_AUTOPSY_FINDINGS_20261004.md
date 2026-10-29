# MTS Defensive 2018 False-B Autopsy — Findings
Date: 2026-10-04
Status: COMPLETED UNDER FROZEN AUTOPSY PROTOCOL
Provenance: NEW_RESEARCH_POST_RECOVERY

## Question
Why did the frozen candidate-stock + market LOEO router classify four of five 2018 observations as B_EMERGING_LEADERSHIP when all five carried the frozen label OTHER?

## Exact 2018 false-B observations
- AJG 2018-12-24: stock ret20 -9.53%, market ret20 -10.80%, rel20 +1.27%, frozen D3_EXIT2 +5.14%.
- FIS 2018-12-24: stock ret20 -6.92%, market ret20 -10.80%, rel20 +3.88%, frozen D3_EXIT2 +7.56%.
- T 2018-12-21: stock ret20 -4.90%, market ret20 -8.81%, rel20 +3.90%, frozen D3_EXIT2 +10.89%.
- T 2018-10-10: stock ret20 +0.24%, market ret20 -3.73%, rel20 +3.97%, frozen D3_EXIT2 -0.89%.

The fifth 2018 observation, ITW 2018-12-24, was correctly classified OTHER and returned +9.79%.

## Main diagnostic result
The 2018 classification failure is not well described as a simple causal-morphology failure. Three of four 2018 OTHER->B classifications were profitable under the already-frozen D3_EXIT2 trade logic. As a group they were 75% winners, mean +5.67%, median +6.35%.

The same pattern is broader than 2018. Thirty non-2018 true-OTHER observations were routed B. They were 80% winners, mean +4.88%, median +4.86%. The 14 frozen true-B observations were stronger (92.86% winners, mean +11.31%, median +8.43%), but the nominal false positives were not generally economic failures.

## Morphology
2018 false-B median stock ret20 was -5.91% while median market ret20 was -9.80%, yielding median rel20 +3.89%. Genuine B median stock ret20 was -4.44% against median market ret20 -16.09%, yielding median rel20 +8.16%.

2018 false-B relative leadership was persistent: median fraction of the preceding ten causal observations with positive rel20 was 0.95 versus 1.00 for genuine B. Absolute repair did not distinguish the groups: both had median 0.15 of trailing observations with positive stock ret20; 2018 false-B had median 0.15 above SMA20 versus 0.05 for genuine B.

The clearest descriptive difference was market severity. Genuine B occurred in much more damaged/stressed market states: median market drawdown -44.03%, breadth above SMA200 3.33%, VIX 66.25. 2018 false-B medians were market drawdown -23.59%, breadth above SMA200 15.01%, VIX 33.09. These are descriptive findings only; no thresholds were fit or authorized.

## Methodological finding
The frozen B label is not an independent economic truth label. It was constructed from development-domain ranks of stock_drawdown252 and rel20. The router then used stock_drawdown252 and rel20 to reproduce those labels. Consequently, LOEO balanced classification accuracy against A/B/OTHER is partly a test of reproducing a morphology partition, not an independent test that B is a distinct profitable strategy state.

The 2018 fold exposes this weakness especially clearly: the router failed the label metric while three of four disputed B routes made money. Non-2018 false-B routes were also economically positive as a group.

## Determination
Primary determination: LABEL-CIRCULARITY / LABEL-SPECIFICATION PROBLEM, with a secondary market-severity distinction worth independent testing.

Not supported: a simple claim that 2018 false-B observations were merely transient relative strength or lacked absolute repair. The causal persistence and absolute-repair diagnostics do not cleanly separate them from genuine B.

## Governance consequence
Do not repair the current classifier to improve A/B/OTHER balanced accuracy. Doing so would optimize reproduction of a partly self-defined label and could remove profitable opportunities.

The strategy-bank architecture remains plausible, but EMERGING_LEADERSHIP should not be treated as validated merely because the router reproduces the frozen B morphology. The next experiment, if pursued, should define an economically independent routing target or directly test a pre-frozen causal market-severity hypothesis against frozen trade outcomes across the consumed development domain.

No preserved50, TEST17, remaining Discovery, Verification A, or Verification B evidence was accessed.
