# MTS v4 — Discovery Adverse-Excursion / Delayed-Entry Protocol
Date: 2026-09-30
Scientific role: Discovery-only hypothesis generation. This experiment does not validate a strategy and may not access Verification A or B.

## Frozen cohort
Use exactly the 67 already-open Discovery-2 tickers: the 50-ticker Discovery-2 cohort plus the 17-ticker Discovery-2B sector-balancing supplement. No ticker may be added or removed after results are inspected.

## Frozen source signals
Use exact saved Discovery-2 / Discovery-2B candidate genomes already produced for the eight frozen single-family Search families. Do not run Search, mutate genomes, refit thresholds, select winners, or inspect Verification data.

## Executable reference
For each signal stream, information cutoff is the completed signal-day bar. The original executable reference entry is next trading-session open. Overlapping positions are prohibited within each signal stream using the candidate's frozen forward horizon. The original terminal exit is the close on signal date plus the frozen forward horizon trading sessions.

## Adverse-excursion measurements
For every accepted original entry, record full-horizon MAE and MFE from the original next-open entry, the session offsets of MAE and MFE, whether MAE occurred before MFE, and terminal return. Report distributions overall, per ticker, per family, per horizon, and by original terminal outcome sign. Report mean, median, P25, P75, P90 and sample count where meaningful. Percentages are relative to original next-open entry.

This experiment measures price excursion. It does not infer that an observed low was a liquidity sweep.

## Frozen delayed-entry offsets
Evaluate limit-buy offsets below the original next-open reference price at exactly:
1%, 2%, 3%, 5%, 7.5%, and 10%.

For each offset, the limit price is fixed before subsequent bars are examined. Starting with the original entry session and ending at the original frozen terminal-exit session:
- if that session's open is at or below the limit, fill at the observed open;
- otherwise, if that session's low touches or crosses the limit, fill at the limit;
- otherwise the delayed order remains unfilled for that trade.
No later extension of the horizon is permitted.

For filled delayed entries, preserve the original terminal exit date and calculate terminal return, post-fill MAE, post-fill MFE, and sessions-to-fill. No stop or profit target is selected in this experiment.

## Opportunity-cost accounting
Every offset must report:
- eligible original trades;
- filled delayed trades and fill rate;
- unfilled trades;
- original winners missed because the delayed order never filled;
- original losers avoided because the delayed order never filled;
- return distributions for filled delayed entries;
- return difference versus the same trades' original next-open entries;
- post-fill MAE/MFE distributions.

Unfilled trades may not be silently discarded when interpreting an offset.

## ATR normalization
Where a pre-entry ATR-like predictor is already present in the frozen predictor store and can be resolved without creating a new fitted feature, report adverse excursion in ATR units. If no such frozen predictor can be resolved unambiguously, report ATR-normalized results as unavailable rather than inventing a new feature.

## Grouping
Report aggregate results and breakdowns by ticker, family, frozen horizon, and cohort. Sector/regime/volatility-bucket extensions are permitted only as separately declared descriptive analyses using information already available at signal time; they are not required for this first frozen run.

## Boundaries
This is Discovery-only. Verification A (including the already-open A1 results) is not used to construct, tune, select, or evaluate delayed-entry offsets. Verification B remains sealed. Results may motivate a new frozen hypothesis, but any such hypothesis requires a new validation path and cannot claim the prior A1 run as validation.

SEARCH_RUN=False
REFIT=False
WINNER_SELECTION=False
VERIFICATION_A_ACCESSED=False
VERIFICATION_B_ACCESSED=False
SOL_CALLS=0
