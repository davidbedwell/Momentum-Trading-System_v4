# MTS v4 — Discovery Recovery-Pattern Measurement Protocol
Date: 2026-09-30
Role: broad Discovery-only measurement and hypothesis generation. No Verification A/B access.

## Cohort and source signals
Use exactly the same 67 open Discovery-2/2B tickers and exact saved candidate genomes used by the frozen adverse-excursion study. No new Search, mutation, refit, winner selection, or ticker selection.

## Central question
What conditions observable during/after an adverse excursion distinguish signals that subsequently recover from signals that continue failing?

No rule may use knowledge that a currently observed low is the eventual MAE. MAE may be used retrospectively only to characterize paths.

## Predeclared benchmark
Original-level reclaim benchmark:
1. reference level = original frozen next-session-open entry price;
2. require an adverse excursion below that reference after entry;
3. first reclaim event = first later session after the excursion whose close is >= reference level;
4. executable confirmation entry = next trading-session open after that reclaim close, if it occurs no later than the original frozen terminal-exit session;
5. preserve the original terminal-exit date; do not extend the horizon.
Measure eligibility, reclaim frequency, confirmation-entry frequency, win rate, terminal return, gross EV, subsequent MAE/MFE, winners retained/missed, losers filtered, and time to reclaim.

Also describe reclaim after predeclared AE depths of 1%, 2%, 3%, 5%, 7.5%, and 10%, without selecting a winning depth.

## Broad single-feature measurements
At each trade and around the developing excursion/reclaim, calculate only deterministic price/volume features from information available at that date:
- AE depth and elapsed sessions; decline velocity;
- SMA10/SMA20/SMA50 price distance and slope;
- EMA20 distance and slope;
- ATR14 and AE in ATR units;
- RSI14;
- volume versus 20-session mean;
- prior 5/10/20-session low distances and sweep/reclaim states;
- local 10-session swing-low sweep/reclaim;
- candle body/range and lower-wick fraction;
- realized 20-session volatility;
- original-reference reclaim state.
Indicators must be computed causally from bars available through each observation date.

First-pass analysis is single-feature/descriptive. Do not combine indicators into optimized rules in this run.

## Subsequent outcomes
From each observation/reclaim event, report whether price subsequently:
- recovers the original reference;
- reaches +2%, +5%, and +10% versus the original reference;
- ends positive at the original frozen terminal exit;
and report subsequent MFE, MAE, terminal return, and elapsed sessions.

## Outputs
Write detailed per-trade/per-event rows to compressed checkpoint/artifact files, not terminal. Terminal output is a concise benchmark and feature-coverage summary. Produce aggregate and per-family/per-ticker descriptive summaries suitable for later relationship analysis.

## Boundaries
This pass may discover candidate relationships but does not validate or promote them. Any composite/threshold rule developed after inspecting these results is a new Discovery hypothesis requiring a separately frozen validation path. Existing A1 is not validation for such a rule.

SEARCH_RUN=False
REFIT=False
WINNER_SELECTION=False
VERIFICATION_A_ACCESSED=False
VERIFICATION_B_ACCESSED=False
SOL_CALLS=0
