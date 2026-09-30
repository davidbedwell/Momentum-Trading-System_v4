# MTS v4 — Final 2026-09-30 Discovery: Early-Recovery Failure / Stop Neighborhood
Date: 2026-09-30
Role: Discovery-only follow-up generated from today's trajectory observations. This experiment may characterize a hypothesis but may not validate, promote, or tune a trading rule.

## Mandatory audit gate
Before interpreting this experiment:
1. Reconcile why the trajectory/partial-recovery run produced 107,934 trade rows versus 125,002 in the preceding recovery-pattern run.
2. Audit the prior partial-recovery accounting in which every cell printed original_winners_filtered=0.
3. If either reflects a material implementation/accounting defect, correct it and rerun affected summaries before interpreting this experiment.

## Hypothesis neighborhood
Today's observed winner medians (approximately 3.3% MAE and 4 sessions to MAE) and user's casual hypothesis motivate a PREDECLARED neighborhood, not an optimized point:
- AE trigger depths: 3%, 3.5%, 4%, 5%.
- Timing states: AE first reached by session 3, 4, 5, or unrestricted.
- Causal recovery confirmation: 25% and 50% recovery from the contemporaneously observed running trough, using the same causal state-machine definition as the frozen trajectory protocol.
- Executable entry: next-session open after confirmation, before original terminal exit.
- Stops after executable entry: 1%, 2%, 3%, and no-stop comparator.
- Stop semantics: gap-through stop exits at session open; otherwise intraday low touching stop exits at stop price. No target. Original frozen terminal exit remains for unstopped trades.

## Primary question
After early partial-recovery entry, does failure through a modest stop identify trades that subsequently continue materially lower rather than trades that merely stop out and then recover?

For each AE × timing × recovery × stop cell report:
- eligible and executable entries;
- win rate;
- mean/median realized return using stop-or-original-terminal exit;
- stop rate;
- among stopped trades: fraction that subsequently fall another 1%, 2%, 3%, and 5% below stop before original terminal exit;
- among stopped trades: fraction that subsequently recover to entry, original reference, and would have been terminal winners without the stop;
- MAE/MFE after stop;
- original winners retained/stopped and original losers retained/stopped;
- ticker and family breadth.

## Guardrails
Do not select a best AE/timing/recovery/stop combination in this run. Report the complete neighborhood. No Search, mutation, refit, adaptive thresholding, Verification A/B access, costs, or Sol. Raw candidate-trade observations are dependent/repeated and descriptive.

Any chosen rule after viewing this output is a new frozen hypothesis requiring untouched-data testing.

SEARCH_RUN=False
REFIT=False
RULE_SELECTION=False
VERIFICATION_A_ACCESSED=False
VERIFICATION_B_ACCESSED=False
SOL_CALLS=0
