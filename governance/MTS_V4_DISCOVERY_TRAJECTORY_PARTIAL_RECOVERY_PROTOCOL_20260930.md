# MTS v4 — Discovery Trajectory and Partial-Recovery Protocol
Date: 2026-09-30
Role: Discovery-only path-shape analysis on the same 67 open Discovery tickers. No Verification access, Search, refit, or rule selection.

## Question
After an MTS signal enters adverse excursion, do decline/recovery trajectory and partial-recovery behavior distinguish subsequent recovery from continued failure earlier than full original-price reclaim?

## Scientific separation
Two analyses must remain distinct.

### A. Retrospective trajectory characterization
Eventual realized MAE may be used only after the fact to describe path shape:
- MAE depth;
- sessions from original next-open reference to MAE;
- average decline per session to MAE;
- maximum one-session close decline before MAE;
- fraction of total MAE occurring in first 1/2/3 sessions;
- sessions spent within 10% and 25% of realized MAE depth;
- sessions from MAE to original-level reclaim, when reclaim occurs;
- average rebound per session from MAE to reclaim;
- rebound/decline speed ratio;
- path efficiency: net movement divided by cumulative absolute close movement on decline and rebound legs.
These fields are descriptive and may NOT define an executable entry because the eventual MAE is unknowable contemporaneously.

### B. Causal partial-recovery state machine
Use only information observable at each session. Maintain a running trough since original next-open entry. Whenever a new trough is observed, update running adverse excursion. From that running trough, define recovery fraction:
(close - running_trough) / (reference - running_trough), when running_trough < reference.
Freeze recovery thresholds at 25%, 50%, 75%, and 100%.

For each threshold, the first session close meeting/exceeding that fraction after at least a 1%, 2%, 3%, 5%, 7.5%, or 10% running adverse excursion is a confirmation event. Executable entry is next-session open if before the original frozen terminal exit. If a new lower trough occurs before confirmation, the recovery target updates causally from that new trough. No future MAE information may be used.

For every AE-depth × recovery-fraction cell report:
- eligible events;
- confirmed entries and confirmation rate;
- sessions to confirmation;
- entry price versus original reference;
- terminal win rate and mean/median terminal return from confirmation entry;
- subsequent MAE/MFE from confirmation entry;
- original winners retained/filtered;
- original losers retained/filtered;
- gross delta versus the same trades at original next-open entry.
Do not choose a best cell in this run.

## Trajectory comparisons
Compare retrospective trajectory variables across:
1. eventual original-terminal winners vs losers;
2. causal partial-recovery confirmation winners vs losses;
3. trades that achieve partial recovery vs those that do not.
Report distributions overall, by ticker, and by family. Raw candidate-trade rows are dependent/repeated; no independent-trial p-values.

## Inputs and implementation
Use the same exact 67 Discovery-2/2B tickers and saved candidate genomes as prior Recovery-Pattern study. Existing recovery checkpoints do not contain full bar paths, so OHLCV may be reacquired once per ticker as required to reconstruct causal trajectories. Use 8-worker parallelism and per-ticker gzip checkpoints/resume. Do not access A1, remaining Verification A, or Verification B.

## Outputs
Detailed results/checkpoints to disk. Terminal output limited to trajectory summary plus the complete 24-cell AE-depth × partial-recovery table.

Any rule suggested after inspecting these results is a new Discovery hypothesis and must be frozen before subsequent testing.

SEARCH_RUN=False
REFIT=False
RULE_SELECTION=False
VERIFICATION_A_ACCESSED=False
VERIFICATION_B_ACCESSED=False
SOL_CALLS=0
